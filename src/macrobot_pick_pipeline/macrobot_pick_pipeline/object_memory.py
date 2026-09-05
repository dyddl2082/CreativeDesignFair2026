"""Persistent object observation memory separated from grasp skills.

The grasp keyframe/profile files describe *how* to manipulate an object and are
portable across reboots.  This store contains only volatile location hints and
held-object state.  Every odometry-scoped record carries a runtime epoch so a
restart invalidates the coordinate without deleting the reusable skill.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import math
import tempfile
from typing import Any, Dict, Mapping, Optional, Tuple

import yaml

from .runtime_epoch import RuntimeEpoch, epoch_compatibility
from .stored_object_core import OdomPose


Vector3 = Tuple[float, float, float]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _finite(value: Any, field: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{field} must be finite")
    return result


def _vector3(value: Any, field: str) -> Vector3:
    if isinstance(value, Mapping):
        raw = (value.get("x"), value.get("y"), value.get("z"))
    elif isinstance(value, (list, tuple)) and len(value) == 3:
        raw = value
    else:
        raise ValueError(f"{field} must be a three-vector")
    return tuple(_finite(item, field) for item in raw)  # type: ignore[return-value]


@dataclass(frozen=True)
class ObjectObservationMemory:
    object_name: str
    object_point_odom: Vector3
    observer_pose_odom: OdomPose
    source_stamp_sec: float
    recorded_at: str
    epoch: RuntimeEpoch
    score: float = 0.0
    localization_quality: float = 0.0
    depth_std_m: float = 0.0
    confidence: float = 0.5
    source: str = "localized_detection"

    @classmethod
    def from_mapping(
        cls,
        name: str,
        value: Mapping[str, Any],
    ) -> "ObjectObservationMemory":
        pose_raw = value.get("observer_pose_odom")
        epoch_raw = value.get("epoch")
        if not isinstance(pose_raw, Mapping):
            raise ValueError("observer_pose_odom must be a mapping")
        if not isinstance(epoch_raw, Mapping):
            epoch_raw = {}
        result = cls(
            object_name=str(value.get("object_name", name)).strip() or str(name),
            object_point_odom=_vector3(
                value.get("object_point_odom"), "object_point_odom"
            ),
            observer_pose_odom=OdomPose.from_mapping(pose_raw),
            source_stamp_sec=_finite(
                value.get("source_stamp_sec", 0.0), "source_stamp_sec"
            ),
            recorded_at=str(value.get("recorded_at", utc_now_iso())),
            epoch=RuntimeEpoch.from_mapping(epoch_raw),
            score=_finite(value.get("score", 0.0), "score"),
            localization_quality=_finite(
                value.get("localization_quality", 0.0), "localization_quality"
            ),
            depth_std_m=max(0.0, _finite(value.get("depth_std_m", 0.0), "depth_std_m")),
            confidence=_finite(value.get("confidence", 0.5), "confidence"),
            source=str(value.get("source", "localized_detection")),
        )
        result.validate()
        return result

    def validate(self) -> None:
        if not self.object_name:
            raise ValueError("object_name is empty")
        if not (0.0 <= self.score <= 1.0):
            raise ValueError("score must be within [0, 1]")
        if not (0.0 <= self.localization_quality <= 1.0):
            raise ValueError("localization_quality must be within [0, 1]")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("confidence must be within [0, 1]")

    def to_mapping(self) -> Dict[str, Any]:
        return {
            "object_name": self.object_name,
            "object_point_odom": {
                "x": self.object_point_odom[0],
                "y": self.object_point_odom[1],
                "z": self.object_point_odom[2],
            },
            "observer_pose_odom": self.observer_pose_odom.to_mapping(),
            "source_stamp_sec": self.source_stamp_sec,
            "recorded_at": self.recorded_at,
            "epoch": self.epoch.to_mapping(),
            "score": self.score,
            "localization_quality": self.localization_quality,
            "depth_std_m": self.depth_std_m,
            "confidence": self.confidence,
            "source": self.source,
        }


@dataclass(frozen=True)
class HeldObjectState:
    state: str = "empty"  # empty | holding | unknown
    object_name: str = ""
    grasp_profile: str = ""
    updated_at: str = ""
    epoch: Optional[RuntimeEpoch] = None
    source: str = "runtime"

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "HeldObjectState":
        epoch_raw = value.get("epoch")
        epoch = RuntimeEpoch.from_mapping(epoch_raw) if isinstance(epoch_raw, Mapping) else None
        result = cls(
            state=str(value.get("state", "unknown")).strip().casefold(),
            object_name=str(value.get("object_name", "")).strip(),
            grasp_profile=str(value.get("grasp_profile", "")).strip(),
            updated_at=str(value.get("updated_at", "")),
            epoch=epoch,
            source=str(value.get("source", "runtime")),
        )
        result.validate()
        return result

    def validate(self) -> None:
        if self.state not in {"empty", "holding", "unknown"}:
            raise ValueError("held-object state must be empty, holding, or unknown")
        if self.state == "holding" and not self.object_name:
            raise ValueError("holding state requires object_name")

    def to_mapping(self) -> Dict[str, Any]:
        return {
            "state": self.state,
            "object_name": self.object_name or None,
            "grasp_profile": self.grasp_profile or None,
            "updated_at": self.updated_at or utc_now_iso(),
            "epoch": None if self.epoch is None else self.epoch.to_mapping(),
            "source": self.source,
        }


class ObjectMemoryStore:
    SCHEMA = "macrobot.object_memory/v2"

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path).expanduser().resolve()
        self.observations: Dict[str, ObjectObservationMemory] = {}
        self.held = HeldObjectState(state="empty", updated_at=utc_now_iso())
        self.reload()

    @staticmethod
    def _key(value: str) -> str:
        return value.strip().casefold()

    def reload(self) -> None:
        self.observations = {}
        self.held = HeldObjectState(state="empty", updated_at=utc_now_iso())
        if not self.path.exists():
            return
        root = yaml.safe_load(self.path.read_text(encoding="utf-8")) or {}
        if not isinstance(root, Mapping):
            raise ValueError("object memory root must be a mapping")
        schema = str(root.get("schema", self.SCHEMA))
        if schema != self.SCHEMA:
            raise ValueError(f"unsupported object memory schema: {schema}")
        raw_observations = root.get("observations", {})
        if isinstance(raw_observations, Mapping):
            for name, raw in raw_observations.items():
                if not isinstance(raw, Mapping):
                    continue
                record = ObjectObservationMemory.from_mapping(str(name), raw)
                self.observations[self._key(record.object_name)] = record
        raw_held = root.get("held_object")
        if isinstance(raw_held, Mapping):
            self.held = HeldObjectState.from_mapping(raw_held)

    def get(self, object_name: str) -> Optional[ObjectObservationMemory]:
        return self.observations.get(self._key(object_name))

    def remember(self, record: ObjectObservationMemory) -> None:
        record.validate()
        self.observations[self._key(record.object_name)] = record
        self.save()

    def forget(self, object_name: str) -> bool:
        key = self._key(object_name)
        if key not in self.observations:
            return False
        del self.observations[key]
        self.save()
        return True

    def classify(
        self,
        object_name: str,
        current_epoch: RuntimeEpoch,
        *,
        current_wall_sec: Optional[float] = None,
        maximum_age_sec: float = 3600.0,
        pico_time_tolerance_ms: int = 2000,
    ) -> tuple[str, str, Optional[ObjectObservationMemory]]:
        record = self.get(object_name)
        if record is None:
            return "missing", "no_location_memory", None
        compatible, reason = epoch_compatibility(
            record.epoch,
            current_epoch,
            pico_time_tolerance_ms=pico_time_tolerance_ms,
        )
        if not compatible:
            return "stale", reason, record
        if current_wall_sec is not None and record.source_stamp_sec > 0.0:
            age = max(0.0, float(current_wall_sec) - record.source_stamp_sec)
            if age > max(0.0, float(maximum_age_sec)):
                return "stale", "location_hint_too_old", record
        return "fresh", reason, record

    def set_holding(
        self,
        object_name: str,
        grasp_profile: str,
        epoch: RuntimeEpoch,
        *,
        source: str = "pick_result",
    ) -> None:
        self.held = HeldObjectState(
            state="holding",
            object_name=object_name,
            grasp_profile=grasp_profile,
            updated_at=utc_now_iso(),
            epoch=epoch,
            source=source,
        )
        self.save()

    def set_empty(self, *, source: str = "place_result") -> None:
        self.held = HeldObjectState(
            state="empty",
            updated_at=utc_now_iso(),
            source=source,
        )
        self.save()

    def set_unknown(self, *, source: str) -> None:
        self.held = HeldObjectState(
            state="unknown",
            object_name=self.held.object_name,
            grasp_profile=self.held.grasp_profile,
            updated_at=utc_now_iso(),
            epoch=self.held.epoch,
            source=source,
        )
        self.save()

    def held_for_epoch(
        self,
        current_epoch: RuntimeEpoch,
        *,
        pico_time_tolerance_ms: int = 2000,
    ) -> HeldObjectState:
        if self.held.state != "holding" or self.held.epoch is None:
            return self.held
        compatible, _ = epoch_compatibility(
            self.held.epoch,
            current_epoch,
            pico_time_tolerance_ms=pico_time_tolerance_ms,
        )
        if compatible:
            return self.held
        return HeldObjectState(
            state="unknown",
            object_name=self.held.object_name,
            grasp_profile=self.held.grasp_profile,
            updated_at=self.held.updated_at,
            epoch=self.held.epoch,
            source="epoch_mismatch",
        )

    def to_mapping(self) -> Dict[str, Any]:
        return {
            "schema": self.SCHEMA,
            "updated_at": utc_now_iso(),
            "observations": {
                record.object_name: record.to_mapping()
                for record in sorted(
                    self.observations.values(), key=lambda item: item.object_name.casefold()
                )
            },
            "held_object": self.held.to_mapping(),
        }

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        text = yaml.safe_dump(self.to_mapping(), allow_unicode=True, sort_keys=False)
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=str(self.path.parent),
            prefix=self.path.name + ".",
            suffix=".tmp",
            delete=False,
        ) as stream:
            stream.write(text)
            temporary = Path(stream.name)
        temporary.replace(self.path)
