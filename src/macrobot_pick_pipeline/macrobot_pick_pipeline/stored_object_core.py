from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
import math
from pathlib import Path
import tempfile
from typing import Any, Dict, Iterable, Mapping, Optional, Tuple

import yaml

from .alignment_core import AlignmentProfile


Vector3 = Tuple[float, float, float]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def finite_float(value: Any, field: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{field} must be finite")
    return result


def vector3(value: Any, field: str) -> Vector3:
    if isinstance(value, Mapping):
        raw = (value.get("x"), value.get("y"), value.get("z"))
    elif isinstance(value, (list, tuple)) and len(value) == 3:
        raw = value
    else:
        raise ValueError(f"{field} must be x/y/z or a 3-vector")
    return tuple(finite_float(item, field) for item in raw)  # type: ignore[return-value]


def wrap_angle_deg(value: float) -> float:
    wrapped = (float(value) + 180.0) % 360.0 - 180.0
    return -180.0 if wrapped == 180.0 else wrapped


@dataclass(frozen=True)
class OdomPose:
    x_m: float
    y_m: float
    yaw_deg: float
    reliable: bool = True
    pico_time_ms: Optional[int] = None

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "OdomPose":
        time_value = value.get("pico_time_ms")
        return cls(
            x_m=finite_float(value.get("x_m"), "odom.x_m"),
            y_m=finite_float(value.get("y_m"), "odom.y_m"),
            yaw_deg=wrap_angle_deg(finite_float(value.get("yaw_deg"), "odom.yaw_deg")),
            reliable=bool(value.get("reliable", True)),
            pico_time_ms=(None if time_value is None else int(time_value)),
        )

    def to_mapping(self) -> Dict[str, Any]:
        return {
            "x_m": self.x_m,
            "y_m": self.y_m,
            "yaw_deg": self.yaw_deg,
            "reliable": self.reliable,
            "pico_time_ms": self.pico_time_ms,
        }


@dataclass(frozen=True)
class BaseReturnPlan:
    initial_turn_deg: float
    move_distance_m: float
    final_turn_deg: float

    @property
    def motion_count(self) -> int:
        return sum(
            1
            for value in (
                self.initial_turn_deg,
                self.move_distance_m,
                self.final_turn_deg,
            )
            if abs(value) > 1e-9
        )


def plan_return_to_pose(
    current: OdomPose,
    target: OdomPose,
    *,
    position_tolerance_m: float = 0.01,
    angle_tolerance_deg: float = 2.0,
) -> BaseReturnPlan:
    dx = target.x_m - current.x_m
    dy = target.y_m - current.y_m
    distance = math.hypot(dx, dy)

    if distance <= max(0.0, float(position_tolerance_m)):
        initial_turn = 0.0
        move = 0.0
        final_turn = wrap_angle_deg(target.yaw_deg - current.yaw_deg)
    else:
        bearing = math.degrees(math.atan2(dy, dx))
        initial_turn = wrap_angle_deg(bearing - current.yaw_deg)
        move = distance
        final_turn = wrap_angle_deg(target.yaw_deg - bearing)

    if abs(initial_turn) <= angle_tolerance_deg:
        initial_turn = 0.0
    if abs(final_turn) <= angle_tolerance_deg:
        final_turn = 0.0
    if move <= position_tolerance_m:
        move = 0.0

    return BaseReturnPlan(initial_turn, move, final_turn)



def pico_session_is_compatible(
    recorded_time_ms: Optional[int],
    current_time_ms: Optional[int],
    *,
    tolerance_ms: int = 2000,
) -> bool:
    """Best-effort detection of a Pico reset within a stored odom session.

    MicroPython ``ticks_ms`` eventually wraps, so this is intentionally only a
    guard for the normal record-then-teleop-then-run workflow.  Long-lived or
    reboot-persistent object positions require an external map/localization
    source.
    """
    if recorded_time_ms is None or current_time_ms is None:
        return True
    return int(current_time_ms) + max(0, int(tolerance_ms)) >= int(recorded_time_ms)

def point_base_to_odom(
    point_base: Vector3,
    base_pose: OdomPose,
    *,
    forward_axis_sign: float = -1.0,
    lateral_axis_sign: float = 1.0,
) -> Vector3:
    if forward_axis_sign == 0.0 or lateral_axis_sign == 0.0:
        raise ValueError("axis signs must be non-zero")
    forward = math.copysign(1.0, forward_axis_sign) * float(point_base[0])
    lateral = math.copysign(1.0, lateral_axis_sign) * float(point_base[1])
    yaw = math.radians(base_pose.yaw_deg)
    x = base_pose.x_m + forward * math.cos(yaw) - lateral * math.sin(yaw)
    y = base_pose.y_m + forward * math.sin(yaw) + lateral * math.cos(yaw)
    return (x, y, float(point_base[2]))


def search_offsets(max_abs_deg: float, step_deg: float) -> Tuple[float, ...]:
    maximum = abs(float(max_abs_deg))
    step = abs(float(step_deg))
    if maximum <= 0.0 or step <= 0.0:
        return (0.0,)
    values = [0.0]
    level = step
    while level <= maximum + 1e-9:
        values.extend((level, -level))
        level += step
    return tuple(values)


def absolute_offsets_to_relative_turns(offsets: Iterable[float]) -> Tuple[float, ...]:
    result = []
    previous = 0.0
    for raw in offsets:
        current = float(raw)
        result.append(wrap_angle_deg(current - previous))
        previous = current
    return tuple(result)


@dataclass(frozen=True)
class StoredObjectRuntimeProfile:
    """Internal runtime adapter profile.

    The project team owns the final persistent object schema.  This class is a
    deliberately small adapter that stores only the values required by the
    current ROS runtime: an odometry-session search pose, a camera-relative
    alignment reference, and the name of a validated arm demonstration.
    """

    name: str
    object_name: str
    recorded_at: str
    search_pose_odom: OdomPose
    object_point_odom: Vector3
    alignment: AlignmentProfile
    grasp_executor: str = "keyframes"
    grasp_trajectory: str = ""
    grasp_keyframe_profile: str = ""
    pick_profile: str = ""
    position_scope: str = "pico_odom_session"
    search_max_yaw_deg: float = 35.0
    search_step_deg: float = 10.0
    search_dwell_sec: float = 1.2
    coarse_position_tolerance_m: float = 0.02
    coarse_angle_tolerance_deg: float = 3.0
    coarse_max_move_m: float = 1.5
    coarse_max_turn_deg: float = 180.0

    @classmethod
    def from_mapping(
        cls,
        name: str,
        value: Mapping[str, Any],
        *,
        default_alignment: Optional[AlignmentProfile] = None,
    ) -> "StoredObjectRuntimeProfile":
        object_name = str(value.get("object_name", name)).strip()
        if not object_name:
            raise ValueError("object_name is empty")
        search_pose_raw = value.get("search_pose_odom")
        if not isinstance(search_pose_raw, Mapping):
            raise ValueError("search_pose_odom must be a mapping")
        object_point = vector3(value.get("object_point_odom"), "object_point_odom")

        alignment_raw = value.get("alignment")
        if not isinstance(alignment_raw, Mapping):
            alignment_raw = {
                "object_name": object_name,
                "pick_profile": str(value.get("pick_profile", object_name)),
                "reference_point_base": value.get("reference_point_base"),
            }
        alignment = AlignmentProfile.from_mapping(
            name,
            alignment_raw,
            defaults=default_alignment,
        )

        grasp = value.get("grasp", {})
        if not isinstance(grasp, Mapping):
            grasp = {}
        search = value.get("search", {})
        if not isinstance(search, Mapping):
            search = {}
        coarse = value.get("coarse_return", {})
        if not isinstance(coarse, Mapping):
            coarse = {}

        profile = cls(
            name=str(name),
            object_name=object_name,
            recorded_at=str(value.get("recorded_at", utc_now_iso())),
            search_pose_odom=OdomPose.from_mapping(search_pose_raw),
            object_point_odom=object_point,
            alignment=alignment,
            grasp_executor=str(grasp.get("executor", value.get("grasp_executor", "keyframes"))).strip(),
            grasp_trajectory=str(grasp.get("trajectory", value.get("grasp_trajectory", ""))).strip(),
            grasp_keyframe_profile=str(
                grasp.get("keyframe_profile", value.get("grasp_keyframe_profile", ""))
            ).strip(),
            pick_profile=str(grasp.get("pick_profile", value.get("pick_profile", object_name))).strip(),
            position_scope=str(value.get("position_scope", "pico_odom_session")),
            search_max_yaw_deg=finite_float(search.get("max_yaw_deg", 35.0), "search.max_yaw_deg"),
            search_step_deg=finite_float(search.get("step_deg", 10.0), "search.step_deg"),
            search_dwell_sec=finite_float(search.get("dwell_sec", 1.2), "search.dwell_sec"),
            coarse_position_tolerance_m=finite_float(coarse.get("position_tolerance_m", 0.02), "coarse.position_tolerance_m"),
            coarse_angle_tolerance_deg=finite_float(coarse.get("angle_tolerance_deg", 3.0), "coarse.angle_tolerance_deg"),
            coarse_max_move_m=finite_float(coarse.get("max_move_m", 1.5), "coarse.max_move_m"),
            coarse_max_turn_deg=finite_float(coarse.get("max_turn_deg", 180.0), "coarse.max_turn_deg"),
        )
        profile.validate()
        return profile

    def validate(self) -> None:
        if not self.name.strip() or not self.object_name.strip():
            raise ValueError("profile and object names must be non-empty")
        if self.position_scope != "pico_odom_session":
            raise ValueError("only pico_odom_session is currently supported")
        if not self.search_pose_odom.reliable:
            raise ValueError("recorded search pose must be reliable")
        if self.grasp_executor not in {"keyframes", "arm_demo", "pick_coordinator"}:
            raise ValueError("grasp_executor must be keyframes, arm_demo or pick_coordinator")
        if self.grasp_executor == "keyframes" and not self.grasp_keyframe_profile:
            raise ValueError("keyframe grasp requires grasp_keyframe_profile")
        if self.grasp_executor == "arm_demo" and not self.grasp_trajectory:
            raise ValueError("arm_demo grasp requires grasp_trajectory")
        positive_values = (
            self.search_step_deg,
            self.search_dwell_sec,
            self.coarse_position_tolerance_m,
            self.coarse_angle_tolerance_deg,
            self.coarse_max_move_m,
            self.coarse_max_turn_deg,
        )
        if any(value <= 0.0 for value in positive_values):
            raise ValueError("search and coarse-return limits must be positive")
        if self.search_max_yaw_deg < 0.0:
            raise ValueError("search_max_yaw_deg must be non-negative")
        self.alignment.validate()

    def with_recording(
        self,
        *,
        point_base: Vector3,
        search_pose: OdomPose,
        object_point_odom: Vector3,
        object_name: str,
        grasp_executor: str,
        grasp_trajectory: str,
        grasp_keyframe_profile: str,
        pick_profile: str,
        orientation_deg: float = 0.0,
        orientation_class: str = "unknown",
        orientation_quality: float = 0.0,
        require_orientation_match: Optional[bool] = None,
    ) -> "StoredObjectRuntimeProfile":
        result = replace(
            self,
            object_name=object_name,
            recorded_at=utc_now_iso(),
            search_pose_odom=search_pose,
            object_point_odom=object_point_odom,
            alignment=self.alignment.with_reference(
                point_base,
                object_name=object_name,
                pick_profile=pick_profile,
                orientation_deg=orientation_deg,
                orientation_class=orientation_class,
                orientation_quality=orientation_quality,
                require_orientation_match=require_orientation_match,
            ),
            grasp_executor=grasp_executor,
            grasp_trajectory=grasp_trajectory,
            grasp_keyframe_profile=grasp_keyframe_profile,
            pick_profile=pick_profile,
        )
        result.validate()
        return result

    def to_mapping(self) -> Dict[str, Any]:
        return {
            "object_name": self.object_name,
            "recorded_at": self.recorded_at,
            "position_scope": self.position_scope,
            "search_pose_odom": self.search_pose_odom.to_mapping(),
            "object_point_odom": {
                "x": self.object_point_odom[0],
                "y": self.object_point_odom[1],
                "z": self.object_point_odom[2],
            },
            "alignment": self.alignment.to_mapping(),
            "grasp": {
                "executor": self.grasp_executor,
                "trajectory": self.grasp_trajectory,
                "keyframe_profile": self.grasp_keyframe_profile,
                "pick_profile": self.pick_profile,
            },
            "search": {
                "max_yaw_deg": self.search_max_yaw_deg,
                "step_deg": self.search_step_deg,
                "dwell_sec": self.search_dwell_sec,
            },
            "coarse_return": {
                "position_tolerance_m": self.coarse_position_tolerance_m,
                "angle_tolerance_deg": self.coarse_angle_tolerance_deg,
                "max_move_m": self.coarse_max_move_m,
                "max_turn_deg": self.coarse_max_turn_deg,
            },
        }


class StoredObjectProfileStore:
    SCHEMA = "macrobot.stored_object_runtime/v0"

    def __init__(self, path: str | Path, default_alignment: AlignmentProfile) -> None:
        self.path = Path(path).expanduser().resolve()
        self.default_alignment = default_alignment
        self._profiles: Dict[str, StoredObjectRuntimeProfile] = {}
        self.reload()

    @staticmethod
    def _key(value: str) -> str:
        return value.strip().casefold()

    def reload(self) -> None:
        self._profiles = {}
        if not self.path.exists():
            return
        root = yaml.safe_load(self.path.read_text(encoding="utf-8")) or {}
        if not isinstance(root, Mapping):
            raise ValueError("stored object profile root must be a mapping")
        schema = str(root.get("schema", self.SCHEMA))
        if schema != self.SCHEMA:
            raise ValueError(f"unsupported stored object schema: {schema}")
        profiles = root.get("profiles", {})
        if not isinstance(profiles, Mapping):
            raise ValueError("profiles must be a mapping")
        for name, value in profiles.items():
            if not isinstance(value, Mapping):
                continue
            profile = StoredObjectRuntimeProfile.from_mapping(
                str(name),
                value,
                default_alignment=replace(self.default_alignment, name=str(name)),
            )
            self._profiles[self._key(str(name))] = profile

    def get(self, name: str = "", object_name: str = "") -> StoredObjectRuntimeProfile:
        key = self._key(name)
        if key and key in self._profiles:
            return self._profiles[key]
        object_key = self._key(object_name)
        matches = [
            profile
            for profile in self._profiles.values()
            if self._key(profile.object_name) == object_key
        ]
        if len(matches) == 1:
            return matches[0]
        if not matches:
            raise KeyError(name or object_name)
        raise KeyError(f"multiple stored profiles match {object_name!r}")

    def upsert(self, profile: StoredObjectRuntimeProfile) -> None:
        profile.validate()
        self._profiles[self._key(profile.name)] = profile
        self.save()

    def delete(self, name: str) -> bool:
        key = self._key(name)
        if key not in self._profiles:
            return False
        del self._profiles[key]
        self.save()
        return True

    def names(self) -> Tuple[str, ...]:
        return tuple(sorted(profile.name for profile in self._profiles.values()))

    def mappings(self) -> Dict[str, Dict[str, Any]]:
        return {
            profile.name: profile.to_mapping()
            for profile in sorted(self._profiles.values(), key=lambda item: item.name)
        }

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        root = {
            "schema": self.SCHEMA,
            "updated_at": utc_now_iso(),
            "profiles": self.mappings(),
        }
        text = yaml.safe_dump(root, allow_unicode=True, sort_keys=False)
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
