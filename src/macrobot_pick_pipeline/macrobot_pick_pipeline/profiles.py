from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional, Tuple

import yaml


Vector3 = Tuple[float, float, float]
Q = Tuple[float, float, float]


def _vector3(value: Any, fallback: Vector3) -> Vector3:
    if isinstance(value, (list, tuple)) and len(value) == 3:
        return tuple(float(item) for item in value)  # type: ignore[return-value]
    return fallback


def _q(value: Any, fallback: Q) -> Q:
    return _vector3(value, fallback)


def _mapping(value: Any) -> Dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


@dataclass(frozen=True)
class PickProfile:
    name: str
    open_q3: float = 0.0
    close_q3: float = 1.0
    grasp_offset_base: Vector3 = (0.0, 0.0, 0.0)
    pregrasp_offset_base: Vector3 = (0.0, 0.0, 0.035)
    lift_offset_base: Vector3 = (0.0, 0.0, 0.050)
    lateral_tolerance_m: float = 0.035
    min_score: float = 0.0
    stability_count: int = 5
    stability_window_sec: float = 1.5
    stability_radius_m: float = 0.012
    search_timeout_sec: float = 30.0
    motion_timeout_sec: float = 20.0
    pre_grasp_seed_q: Q = (0.0, 0.0, 0.0)
    grasp_seed_q: Q = (0.0, 0.0, 0.0)
    lift_seed_q: Q = (0.0, 0.0, 1.0)
    speed_scale: float = 0.5
    relocalize_before_grasp: bool = False
    notes: str = ""

    @staticmethod
    def from_mapping(name: str, data: Mapping[str, Any], base: Optional["PickProfile"] = None) -> "PickProfile":
        seed = base or PickProfile(name=name)
        return PickProfile(
            name=name,
            open_q3=float(data.get("open_q3", seed.open_q3)),
            close_q3=float(data.get("close_q3", seed.close_q3)),
            grasp_offset_base=_vector3(data.get("grasp_offset_base"), seed.grasp_offset_base),
            pregrasp_offset_base=_vector3(
                data.get("pregrasp_offset_base"), seed.pregrasp_offset_base
            ),
            lift_offset_base=_vector3(data.get("lift_offset_base"), seed.lift_offset_base),
            lateral_tolerance_m=float(
                data.get("lateral_tolerance_m", seed.lateral_tolerance_m)
            ),
            min_score=float(data.get("min_score", seed.min_score)),
            stability_count=max(1, int(data.get("stability_count", seed.stability_count))),
            stability_window_sec=max(
                0.1, float(data.get("stability_window_sec", seed.stability_window_sec))
            ),
            stability_radius_m=max(
                0.0, float(data.get("stability_radius_m", seed.stability_radius_m))
            ),
            search_timeout_sec=max(
                0.1, float(data.get("search_timeout_sec", seed.search_timeout_sec))
            ),
            motion_timeout_sec=max(
                0.1, float(data.get("motion_timeout_sec", seed.motion_timeout_sec))
            ),
            pre_grasp_seed_q=_q(data.get("pre_grasp_seed_q"), seed.pre_grasp_seed_q),
            grasp_seed_q=_q(data.get("grasp_seed_q"), seed.grasp_seed_q),
            lift_seed_q=_q(data.get("lift_seed_q"), seed.lift_seed_q),
            speed_scale=max(0.05, min(1.0, float(data.get("speed_scale", seed.speed_scale)))),
            relocalize_before_grasp=bool(
                data.get("relocalize_before_grasp", seed.relocalize_before_grasp)
            ),
            notes=str(data.get("notes", seed.notes)),
        )


class PickProfileRepository:
    """Load camera-to-grasp execution settings and optional commissioning seeds."""

    def __init__(
        self,
        profile_file: str | Path,
        commissioning_report: str | Path | None = None,
    ) -> None:
        self.profile_file = Path(profile_file).expanduser().resolve()
        self.commissioning_report = (
            Path(commissioning_report).expanduser().resolve()
            if commissioning_report
            else None
        )
        self.default_profile = PickProfile(name="default")
        self.object_profiles: Dict[str, PickProfile] = {}
        self._load()

    @staticmethod
    def _key(name: str) -> str:
        return name.strip().casefold()

    def reload(self) -> None:
        self.default_profile = PickProfile(name="default")
        self.object_profiles = {}
        self._load()

    def _load(self) -> None:
        root: Dict[str, Any] = {}
        if self.profile_file.exists():
            with self.profile_file.open("r", encoding="utf-8") as stream:
                loaded = yaml.safe_load(stream) or {}
            root = _mapping(loaded)

        default_data = _mapping(root.get("defaults"))
        self.default_profile = PickProfile.from_mapping("default", default_data)

        objects = _mapping(root.get("objects"))
        for name, value in objects.items():
            if isinstance(value, Mapping):
                profile = PickProfile.from_mapping(
                    str(name), value, base=replace(self.default_profile, name=str(name))
                )
                self.object_profiles[self._key(str(name))] = profile

        self._merge_commissioning_report()

    def _merge_commissioning_report(self) -> None:
        if self.commissioning_report is None or not self.commissioning_report.exists():
            return
        with self.commissioning_report.open("r", encoding="utf-8") as stream:
            report = yaml.safe_load(stream) or {}
        profiles = (
            _mapping(report)
            .get("sections", {})
        )
        if not isinstance(profiles, Mapping):
            return
        profiles = profiles.get("grasp_profiles", {})
        if not isinstance(profiles, Mapping):
            return
        profiles = profiles.get("profiles", {})
        if not isinstance(profiles, Mapping):
            return

        for object_name, raw in profiles.items():
            if not isinstance(raw, Mapping):
                continue
            key = self._key(str(object_name))
            base = self.object_profiles.get(
                key,
                replace(self.default_profile, name=str(object_name)),
            )
            override: Dict[str, Any] = {}
            # Joint-space seeds remain useful for selecting the same IK branch.
            if "pre_grasp_q" in raw:
                override["pre_grasp_seed_q"] = raw["pre_grasp_q"]
            if "grasp_q" in raw:
                override["grasp_seed_q"] = raw["grasp_q"]
            if "lift_q" in raw:
                override["lift_seed_q"] = raw["lift_q"]
            for source_key, destination_key in (
                ("pre_grasp_seed_q", "pre_grasp_seed_q"),
                ("grasp_seed_q", "grasp_seed_q"),
                ("lift_seed_q", "lift_seed_q"),
                ("grasp_offset_base", "grasp_offset_base"),
                ("pregrasp_offset_base", "pregrasp_offset_base"),
                ("lift_offset_base", "lift_offset_base"),
            ):
                if source_key in raw:
                    override[destination_key] = raw[source_key]
            if "open_q3" in raw:
                open_q3 = float(raw["open_q3"])
                if open_q3 >= 0.0:
                    override["open_q3"] = open_q3
            if "close_q3" in raw:
                close_q3 = float(raw["close_q3"])
                # Current physical convention is q3>=0 while closing. Ignore a
                # stale report produced with the former negative-q3 convention.
                if close_q3 >= 0.0:
                    override["close_q3"] = close_q3
            if "speed_scale" in raw:
                override["speed_scale"] = raw["speed_scale"]
            if "notes" in raw:
                override["notes"] = str(raw["notes"])
            self.object_profiles[key] = PickProfile.from_mapping(
                str(object_name), override, base=base
            )

    def get(self, object_name: str, profile_name: str = "") -> PickProfile:
        lookup = profile_name.strip() or object_name.strip()
        key = self._key(lookup)
        if key in self.object_profiles:
            return self.object_profiles[key]
        return replace(self.default_profile, name=lookup or "default")

    def names(self) -> Iterable[str]:
        return sorted(profile.name for profile in self.object_profiles.values())
