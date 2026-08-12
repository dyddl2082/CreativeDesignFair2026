"""Persistent semantic grasp keyframe profile store."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import tempfile
from typing import Any, Dict, Mapping, Optional

import yaml

from .grasp_keyframe_core import GraspKeyframeProfile, GraspKeyframeStage


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _q(value: Any) -> tuple[float, float, float]:
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        raise ValueError("q must be a three-vector")
    return tuple(float(item) for item in value)  # type: ignore[return-value]


def _vector3(value: Any) -> Optional[tuple[float, float, float]]:
    if value is None:
        return None
    if isinstance(value, Mapping):
        return (float(value["x"]), float(value["y"]), float(value["z"]))
    if isinstance(value, (list, tuple)) and len(value) == 3:
        return tuple(float(item) for item in value)  # type: ignore[return-value]
    raise ValueError("object_offset must be a three-vector")


class GraspKeyframeStore:
    SCHEMA = "macrobot.grasp_keyframes/v2"

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path).expanduser().resolve()
        self.profiles: Dict[str, GraspKeyframeProfile] = {}
        self.reload()

    @staticmethod
    def _key(value: str) -> str:
        return value.strip().casefold()

    def reload(self) -> None:
        self.profiles = {}
        if not self.path.exists():
            return
        root = yaml.safe_load(self.path.read_text(encoding="utf-8")) or {}
        if not isinstance(root, Mapping):
            raise ValueError("grasp keyframe root must be a mapping")
        if str(root.get("schema", self.SCHEMA)) != self.SCHEMA:
            raise ValueError("unsupported grasp keyframe schema")
        profiles = root.get("profiles", {})
        if not isinstance(profiles, Mapping):
            raise ValueError("profiles must be a mapping")
        for name, raw in profiles.items():
            if not isinstance(raw, Mapping):
                continue
            stages_raw = raw.get("stages", {})
            if not isinstance(stages_raw, Mapping):
                continue
            stages: Dict[str, GraspKeyframeStage] = {}
            for stage_name, stage_raw in stages_raw.items():
                if not isinstance(stage_raw, Mapping):
                    continue
                stage = GraspKeyframeStage(
                    name=str(stage_name).upper(),
                    representation=str(stage_raw.get("representation", "joint_fallback")),
                    q=_q(stage_raw.get("q")),
                    object_offset=_vector3(stage_raw.get("object_offset")),
                    seed_q=(None if stage_raw.get("seed_q") is None else _q(stage_raw.get("seed_q"))),
                    gripper_q=(None if stage_raw.get("gripper_q") is None else float(stage_raw.get("gripper_q"))),
                    settle_sec=float(stage_raw.get("settle_sec", 0.10)),
                )
                stage.validate()
                stages[stage.name] = stage
            profile = GraspKeyframeProfile(
                name=str(name),
                object_name=str(raw.get("object_name", name)),
                stages=stages,
                reference_orientation_deg=float(raw.get("reference_orientation_deg", 0.0)),
                reference_orientation_class=str(raw.get("reference_orientation_class", "unknown")),
                reference_orientation_quality=float(raw.get("reference_orientation_quality", 0.0)),
                recorded_at=str(raw.get("recorded_at", "")),
            )
            # Draft profiles can be incomplete while the operator captures stages.
            self.profiles[self._key(str(name))] = profile

    def get(self, name: str) -> GraspKeyframeProfile:
        key = self._key(name)
        if key not in self.profiles:
            raise KeyError(name)
        return self.profiles[key]

    def upsert_stage(
        self,
        *,
        profile_name: str,
        object_name: str,
        stage: GraspKeyframeStage,
        orientation_deg: float = 0.0,
        orientation_class: str = "unknown",
        orientation_quality: float = 0.0,
    ) -> GraspKeyframeProfile:
        key = self._key(profile_name)
        existing = self.profiles.get(key)
        stages = dict(existing.stages) if existing else {}
        stages[stage.name] = stage
        profile = GraspKeyframeProfile(
            name=profile_name,
            object_name=object_name,
            stages=stages,
            reference_orientation_deg=(
                existing.reference_orientation_deg
                if existing and existing.reference_orientation_quality > 0.0
                else float(orientation_deg)
            ),
            reference_orientation_class=(
                existing.reference_orientation_class
                if existing and existing.reference_orientation_quality > 0.0
                else str(orientation_class)
            ),
            reference_orientation_quality=(
                existing.reference_orientation_quality
                if existing and existing.reference_orientation_quality > 0.0
                else float(orientation_quality)
            ),
            recorded_at=utc_now_iso(),
        )
        self.profiles[key] = profile
        self.save()
        return profile

    def delete(self, name: str) -> bool:
        key = self._key(name)
        if key not in self.profiles:
            return False
        del self.profiles[key]
        self.save()
        return True

    def mappings(self) -> Dict[str, Any]:
        output: Dict[str, Any] = {}
        for profile in sorted(self.profiles.values(), key=lambda item: item.name):
            stages: Dict[str, Any] = {}
            for name, stage in profile.stages.items():
                stages[name] = {
                    "representation": stage.representation,
                    "q": list(stage.q),
                    "object_offset": (None if stage.object_offset is None else list(stage.object_offset)),
                    "seed_q": (None if stage.seed_q is None else list(stage.seed_q)),
                    "gripper_q": stage.gripper_q,
                    "settle_sec": stage.settle_sec,
                }
            output[profile.name] = {
                "object_name": profile.object_name,
                "recorded_at": profile.recorded_at,
                "reference_orientation_deg": profile.reference_orientation_deg,
                "reference_orientation_class": profile.reference_orientation_class,
                "reference_orientation_quality": profile.reference_orientation_quality,
                "stages": stages,
            }
        return output

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        root = {
            "schema": self.SCHEMA,
            "updated_at": utc_now_iso(),
            "profiles": self.mappings(),
        }
        text = yaml.safe_dump(root, allow_unicode=True, sort_keys=False)
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=str(self.path.parent),
            prefix=self.path.name + ".", suffix=".tmp", delete=False,
        ) as stream:
            stream.write(text)
            temporary = Path(stream.name)
        temporary.replace(self.path)
