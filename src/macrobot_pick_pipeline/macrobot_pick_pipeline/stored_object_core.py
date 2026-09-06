from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
import math
from pathlib import Path
import tempfile
from typing import Any, Dict, Iterable, Mapping, Optional, Tuple

import yaml

from .alignment_core import AlignmentProfile, planar_observation


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


def optional_vector3(value: Any, field: str) -> Optional[Vector3]:
    if value is None:
        return None
    return vector3(value, field)


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
    drive_direction: str = "forward"

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

    @property
    def uses_reverse(self) -> bool:
        return self.drive_direction == "reverse" and self.move_distance_m < 0.0


def plan_return_to_pose(
    current: OdomPose,
    target: OdomPose,
    *,
    position_tolerance_m: float = 0.01,
    angle_tolerance_deg: float = 2.0,
    allow_reverse: bool = False,
    reverse_heading_tolerance_deg: float = 90.0,
) -> BaseReturnPlan:
    """Plan a turn/move/turn return in the Pico odom frame.

    When ``allow_reverse`` is enabled, the planner compares the normal
    forward-driving plan with a reverse-driving alternative.  Reverse is used
    only when:

    * the chassis can point its rear toward the target with less than
      ``reverse_heading_tolerance_deg`` of initial rotation;
    * the target pose yaw differs from the current chassis yaw by less than the
      same threshold; and
    * the reverse option reduces total commanded rotation.

    The strict ``< 90 deg`` default intentionally keeps targets in the forward
    half-plane on the normal forward path while allowing a pose directly behind
    the robot, with a similar final heading, to be reached by a negative move.
    """
    dx = target.x_m - current.x_m
    dy = target.y_m - current.y_m
    distance = math.hypot(dx, dy)
    drive_direction = "none"

    if distance <= max(0.0, float(position_tolerance_m)):
        initial_turn = 0.0
        move = 0.0
        final_turn = wrap_angle_deg(target.yaw_deg - current.yaw_deg)
    else:
        bearing = math.degrees(math.atan2(dy, dx))

        forward_initial = wrap_angle_deg(bearing - current.yaw_deg)
        forward_final = wrap_angle_deg(target.yaw_deg - bearing)
        initial_turn = forward_initial
        move = distance
        final_turn = forward_final
        drive_direction = "forward"

        threshold = max(0.0, min(abs(float(reverse_heading_tolerance_deg)), 180.0))
        if bool(allow_reverse) and threshold > 0.0:
            reverse_bearing = wrap_angle_deg(bearing + 180.0)
            reverse_initial = wrap_angle_deg(reverse_bearing - current.yaw_deg)
            reverse_final = wrap_angle_deg(target.yaw_deg - reverse_bearing)
            target_heading_error = abs(
                wrap_angle_deg(target.yaw_deg - current.yaw_deg)
            )
            forward_turn_cost = abs(forward_initial) + abs(forward_final)
            reverse_turn_cost = abs(reverse_initial) + abs(reverse_final)

            if (
                abs(reverse_initial) < threshold
                and target_heading_error < threshold
                and reverse_turn_cost + 1e-9 < forward_turn_cost
            ):
                initial_turn = reverse_initial
                move = -distance
                final_turn = reverse_final
                drive_direction = "reverse"

    if abs(initial_turn) <= angle_tolerance_deg:
        initial_turn = 0.0
    if abs(final_turn) <= angle_tolerance_deg:
        final_turn = 0.0
    if abs(move) <= position_tolerance_m:
        move = 0.0
        drive_direction = "none"

    return BaseReturnPlan(
        initial_turn,
        move,
        final_turn,
        drive_direction=drive_direction,
    )


def pico_session_is_compatible(
    recorded_time_ms: Optional[int],
    current_time_ms: Optional[int],
    *,
    tolerance_ms: int = 2000,
) -> bool:
    """Best-effort detection of a Pico reset within a stored odom session."""
    if recorded_time_ms is None or current_time_ms is None:
        return True
    return int(current_time_ms) + max(0, int(tolerance_ms)) >= int(recorded_time_ms)


def _axis_sign(value: float, field: str) -> float:
    if float(value) == 0.0:
        raise ValueError(f"{field} must be non-zero")
    return math.copysign(1.0, float(value))


def point_base_to_odom(
    point_base: Vector3,
    base_pose: OdomPose,
    *,
    forward_axis_sign: float = 1.0,
    lateral_axis_sign: float = 1.0,
) -> Vector3:
    forward_sign = _axis_sign(forward_axis_sign, "forward_axis_sign")
    lateral_sign = _axis_sign(lateral_axis_sign, "lateral_axis_sign")
    forward = forward_sign * float(point_base[0])
    lateral = lateral_sign * float(point_base[1])
    yaw = math.radians(base_pose.yaw_deg)
    x = base_pose.x_m + forward * math.cos(yaw) - lateral * math.sin(yaw)
    y = base_pose.y_m + forward * math.sin(yaw) + lateral * math.cos(yaw)
    return (x, y, float(point_base[2]))


def point_odom_to_base(
    point_odom: Vector3,
    base_pose: OdomPose,
    *,
    forward_axis_sign: float = 1.0,
    lateral_axis_sign: float = 1.0,
) -> Vector3:
    """Transform a static object point in the Pico odom frame into base_link.

    This is the inverse of :func:`point_base_to_odom`.  It allows a target that
    was positively identified at a recognition-friendly distance to remain
    usable after the finder is stopped and the chassis moves into arm reach.
    """
    forward_sign = _axis_sign(forward_axis_sign, "forward_axis_sign")
    lateral_sign = _axis_sign(lateral_axis_sign, "lateral_axis_sign")
    dx = float(point_odom[0]) - base_pose.x_m
    dy = float(point_odom[1]) - base_pose.y_m
    yaw = math.radians(base_pose.yaw_deg)
    forward = math.cos(yaw) * dx + math.sin(yaw) * dy
    lateral = -math.sin(yaw) * dx + math.cos(yaw) * dy
    return (
        forward_sign * forward,
        lateral_sign * lateral,
        float(point_odom[2]),
    )


def translated_pose_for_object_shift(
    recorded_pose: OdomPose,
    recorded_object_point_odom: Vector3,
    current_object_point_odom: Vector3,
) -> OdomPose:
    """Translate a recorded grasp pose with a relocated, orientation-stable object."""
    return OdomPose(
        x_m=recorded_pose.x_m
        + float(current_object_point_odom[0])
        - float(recorded_object_point_odom[0]),
        y_m=recorded_pose.y_m
        + float(current_object_point_odom[1])
        - float(recorded_object_point_odom[1]),
        yaw_deg=recorded_pose.yaw_deg,
        reliable=recorded_pose.reliable,
        pico_time_ms=recorded_pose.pico_time_ms,
    )


def planar_range_m(
    point_base: Vector3,
    *,
    forward_axis_sign: float = 1.0,
    lateral_axis_sign: float = 1.0,
) -> float:
    return planar_observation(
        point_base,
        forward_axis_sign=forward_axis_sign,
        lateral_axis_sign=lateral_axis_sign,
    ).range_m


def estimate_handoff_uncertainty_m(
    *,
    acquisition_radius_m: float,
    acquisition_depth_std_m: float,
    traveled_distance_m: float,
    accumulated_turn_deg: float,
    target_range_m: float,
    linear_error_fraction: float,
    turn_error_fraction: float,
    turn_translation_drift_m_per_360: float = 0.0,
) -> float:
    """Conservative scalar uncertainty for the far-acquire/near-grasp handoff.

    The chassis calibration is good but not absolute.  This estimate explicitly
    prevents a long dead-reckoning approach from being treated as a fresh camera
    measurement.  ``turn_error_fraction`` is a fractional angular error, e.g.
    0.02 means a 10 degree command may carry roughly 0.2 degree uncertainty.
    """
    base = max(0.0, float(acquisition_radius_m), float(acquisition_depth_std_m))
    linear = abs(float(traveled_distance_m)) * max(0.0, float(linear_error_fraction))
    angular_error_rad = math.radians(
        abs(float(accumulated_turn_deg)) * max(0.0, float(turn_error_fraction))
    )
    angular = abs(float(target_range_m)) * angular_error_rad
    turn_drift = (
        abs(float(accumulated_turn_deg))
        / 360.0
        * max(0.0, float(turn_translation_drift_m_per_360))
    )
    return math.sqrt(
        base * base
        + linear * linear
        + angular * angular
        + turn_drift * turn_drift
    )


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
    """Internal runtime adapter for object recognition and grasping.

    Legacy ``pico_odom_session`` profiles retain the two-distance handoff fields.
    New ``camera_relative`` profiles keep those fields only as schema-compatible
    placeholders; fresh RGB-D localization is the sole high-level pose authority.
    """

    name: str
    object_name: str
    recorded_at: str
    search_pose_odom: OdomPose
    object_point_odom: Vector3
    alignment: AlignmentProfile
    grasp_pose_odom: Optional[OdomPose] = None
    recognition_point_base: Optional[Vector3] = None
    recognition_score: float = 0.0
    recording_state: str = "complete"  # search_only | complete
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
    distance_handoff_enabled: bool = True
    recognition_min_range_m: float = 0.32
    recognition_max_range_m: float = 1.20
    graspable_min_range_m: float = 0.08
    graspable_max_range_m: float = 0.30
    approach_position_tolerance_m: float = 0.012
    approach_angle_tolerance_deg: float = 2.0
    approach_max_move_step_m: float = 0.10
    approach_max_turn_step_deg: float = 4.0
    approach_max_iterations: int = 16
    approach_max_total_move_m: float = 0.80
    approach_max_total_turn_deg: float = 180.0
    base_linear_error_fraction: float = 0.015
    base_turn_error_fraction: float = 0.020
    turn_translation_drift_m_per_360: float = 0.010
    maximum_handoff_uncertainty_m: float = 0.025
    maximum_object_relocation_m: float = 1.0

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
        search_pose = OdomPose.from_mapping(search_pose_raw)
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
        recognition = value.get("recognition", {})
        if not isinstance(recognition, Mapping):
            recognition = {}
        handoff = value.get("distance_handoff", value.get("approach", {}))
        if not isinstance(handoff, Mapping):
            handoff = {}

        grasp_pose_raw = value.get("grasp_pose_odom")
        grasp_pose = (
            OdomPose.from_mapping(grasp_pose_raw)
            if isinstance(grasp_pose_raw, Mapping)
            else None
        )
        grasp_executor = str(
            grasp.get("executor", value.get("grasp_executor", "keyframes"))
        ).strip()
        grasp_trajectory = str(
            grasp.get("trajectory", value.get("grasp_trajectory", ""))
        ).strip()
        grasp_keyframe_profile = str(
            grasp.get("keyframe_profile", value.get("grasp_keyframe_profile", ""))
        ).strip()
        recording_state = str(value.get("recording_state", "")).strip().casefold()
        if not recording_state:
            # Legacy v0 profiles recorded search and grasp at the same pose.
            complete_grasp = bool(
                (grasp_executor == "keyframes" and grasp_keyframe_profile)
                or (grasp_executor == "arm_demo" and grasp_trajectory)
                or grasp_executor == "pick_coordinator"
            )
            recording_state = "complete" if complete_grasp else "search_only"
        if grasp_pose is None and recording_state == "complete":
            grasp_pose = search_pose

        profile = cls(
            name=str(name),
            object_name=object_name,
            recorded_at=str(value.get("recorded_at", utc_now_iso())),
            search_pose_odom=search_pose,
            object_point_odom=object_point,
            alignment=alignment,
            grasp_pose_odom=grasp_pose,
            recognition_point_base=optional_vector3(
                recognition.get("point_base", value.get("recognition_point_base")),
                "recognition.point_base",
            ),
            recognition_score=finite_float(
                recognition.get("score", value.get("recognition_score", 0.0)),
                "recognition.score",
            ),
            recording_state=recording_state,
            grasp_executor=grasp_executor,
            grasp_trajectory=grasp_trajectory,
            grasp_keyframe_profile=grasp_keyframe_profile,
            pick_profile=str(
                grasp.get("pick_profile", value.get("pick_profile", object_name))
            ).strip(),
            position_scope=str(value.get("position_scope", "pico_odom_session")),
            search_max_yaw_deg=finite_float(
                search.get("max_yaw_deg", 35.0), "search.max_yaw_deg"
            ),
            search_step_deg=finite_float(search.get("step_deg", 10.0), "search.step_deg"),
            search_dwell_sec=finite_float(
                search.get("dwell_sec", 1.2), "search.dwell_sec"
            ),
            coarse_position_tolerance_m=finite_float(
                coarse.get("position_tolerance_m", 0.02),
                "coarse.position_tolerance_m",
            ),
            coarse_angle_tolerance_deg=finite_float(
                coarse.get("angle_tolerance_deg", 3.0),
                "coarse.angle_tolerance_deg",
            ),
            coarse_max_move_m=finite_float(
                coarse.get("max_move_m", 1.5), "coarse.max_move_m"
            ),
            coarse_max_turn_deg=finite_float(
                coarse.get("max_turn_deg", 180.0), "coarse.max_turn_deg"
            ),
            distance_handoff_enabled=bool(handoff.get("enabled", True)),
            recognition_min_range_m=finite_float(
                recognition.get("minimum_range_m", 0.32),
                "recognition.minimum_range_m",
            ),
            recognition_max_range_m=finite_float(
                recognition.get("maximum_range_m", 1.20),
                "recognition.maximum_range_m",
            ),
            graspable_min_range_m=finite_float(
                handoff.get("graspable_min_range_m", 0.08),
                "distance_handoff.graspable_min_range_m",
            ),
            graspable_max_range_m=finite_float(
                handoff.get("graspable_max_range_m", 0.30),
                "distance_handoff.graspable_max_range_m",
            ),
            approach_position_tolerance_m=finite_float(
                handoff.get("position_tolerance_m", 0.012),
                "distance_handoff.position_tolerance_m",
            ),
            approach_angle_tolerance_deg=finite_float(
                handoff.get("angle_tolerance_deg", 2.0),
                "distance_handoff.angle_tolerance_deg",
            ),
            approach_max_move_step_m=finite_float(
                handoff.get("max_move_step_m", 0.10),
                "distance_handoff.max_move_step_m",
            ),
            approach_max_turn_step_deg=finite_float(
                handoff.get("max_turn_step_deg", 4.0),
                "distance_handoff.max_turn_step_deg",
            ),
            approach_max_iterations=int(handoff.get("max_iterations", 16)),
            approach_max_total_move_m=finite_float(
                handoff.get("max_total_move_m", 0.80),
                "distance_handoff.max_total_move_m",
            ),
            approach_max_total_turn_deg=finite_float(
                handoff.get("max_total_turn_deg", 180.0),
                "distance_handoff.max_total_turn_deg",
            ),
            base_linear_error_fraction=finite_float(
                handoff.get("base_linear_error_fraction", 0.015),
                "distance_handoff.base_linear_error_fraction",
            ),
            base_turn_error_fraction=finite_float(
                handoff.get("base_turn_error_fraction", 0.020),
                "distance_handoff.base_turn_error_fraction",
            ),
            turn_translation_drift_m_per_360=finite_float(
                handoff.get("turn_translation_drift_m_per_360", 0.010),
                "distance_handoff.turn_translation_drift_m_per_360",
            ),
            maximum_handoff_uncertainty_m=finite_float(
                handoff.get("maximum_uncertainty_m", 0.025),
                "distance_handoff.maximum_uncertainty_m",
            ),
            maximum_object_relocation_m=finite_float(
                handoff.get("maximum_object_relocation_m", 1.0),
                "distance_handoff.maximum_object_relocation_m",
            ),
        )
        profile.validate()
        return profile

    @property
    def complete(self) -> bool:
        return self.recording_state == "complete"

    def validate(self) -> None:
        if not self.name.strip() or not self.object_name.strip():
            raise ValueError("profile and object names must be non-empty")
        if self.position_scope not in {"pico_odom_session", "camera_relative"}:
            raise ValueError(
                "position_scope must be pico_odom_session or camera_relative"
            )
        if (
            self.position_scope == "pico_odom_session"
            and not self.search_pose_odom.reliable
        ):
            raise ValueError("recorded search pose must be reliable")
        if self.recording_state not in {"search_only", "complete"}:
            raise ValueError("recording_state must be search_only or complete")
        if self.grasp_executor not in {"keyframes", "arm_demo", "pick_coordinator"}:
            raise ValueError("grasp_executor must be keyframes, arm_demo or pick_coordinator")
        if self.complete:
            if self.position_scope == "pico_odom_session":
                effective_grasp_pose = self.grasp_pose_odom or self.search_pose_odom
                if not effective_grasp_pose.reliable:
                    raise ValueError("complete profile requires a reliable grasp pose")
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
            self.recognition_min_range_m,
            self.recognition_max_range_m,
            self.graspable_min_range_m,
            self.graspable_max_range_m,
            self.approach_position_tolerance_m,
            self.approach_angle_tolerance_deg,
            self.approach_max_move_step_m,
            self.approach_max_turn_step_deg,
            self.approach_max_total_move_m,
            self.approach_max_total_turn_deg,
            self.maximum_handoff_uncertainty_m,
            self.maximum_object_relocation_m,
        )
        if any(value <= 0.0 for value in positive_values):
            raise ValueError("search, reach and handoff limits must be positive")
        if self.search_max_yaw_deg < 0.0:
            raise ValueError("search_max_yaw_deg must be non-negative")
        if self.recognition_min_range_m >= self.recognition_max_range_m:
            raise ValueError("recognition range is invalid")
        if self.graspable_min_range_m >= self.graspable_max_range_m:
            raise ValueError("graspable range is invalid")
        if self.approach_max_iterations < 1:
            raise ValueError("approach_max_iterations must be >= 1")
        if not 0.0 <= self.recognition_score <= 1.0:
            raise ValueError("recognition_score must be within [0, 1]")
        if (
            self.base_linear_error_fraction < 0.0
            or self.base_turn_error_fraction < 0.0
            or self.turn_translation_drift_m_per_360 < 0.0
        ):
            raise ValueError("base error and drift parameters must be non-negative")
        self.alignment.validate()

    def validate_for_execution(
        self,
        *,
        forward_axis_sign: float = 1.0,
        lateral_axis_sign: float = 1.0,
    ) -> None:
        self.validate()
        if not self.complete:
            raise ValueError("stored object profile is incomplete; record grasp pose")
        # camera_relative_no_fixed_distance_gate_v1
        # Camera-relative profiles reproduce the camera-observed teaching point
        # and rely on semantic-keyframe IK plus safe-region preflight for actual
        # reachability.  The legacy 0.32 m / 0.30 m split remains enforced only
        # for pico_odom_session profiles that still use distance handoff.
        if self.position_scope != "camera_relative":
            reference_range = planar_range_m(
                self.alignment.reference_point_base,
                forward_axis_sign=forward_axis_sign,
                lateral_axis_sign=lateral_axis_sign,
            )
            if reference_range < self.graspable_min_range_m - 1e-9:
                raise ValueError("recorded grasp reference is too close")
            if reference_range > self.graspable_max_range_m + 1e-9:
                raise ValueError("recorded grasp reference exceeds arm reach")

    def with_search_recording(
        self,
        *,
        point_base: Vector3,
        search_pose: OdomPose,
        object_point_odom: Vector3,
        object_name: str,
        recognition_score: float,
    ) -> "StoredObjectRuntimeProfile":
        result = replace(
            self,
            object_name=object_name,
            recorded_at=utc_now_iso(),
            search_pose_odom=search_pose,
            object_point_odom=object_point_odom,
            recognition_point_base=point_base,
            recognition_score=float(recognition_score),
            recording_state="search_only",
            grasp_pose_odom=None,
            grasp_trajectory="",
            grasp_keyframe_profile="",
        )
        result.validate()
        return result

    def with_grasp_recording(
        self,
        *,
        point_base: Vector3,
        grasp_pose: OdomPose,
        object_name: str,
        grasp_executor: str,
        grasp_trajectory: str,
        grasp_keyframe_profile: str,
        pick_profile: str,
        orientation_deg: float = 0.0,
        orientation_class: str = "unknown",
        orientation_quality: float = 0.0,
        require_orientation_match: Optional[bool] = None,
        graspable_max_range_m: Optional[float] = None,
    ) -> "StoredObjectRuntimeProfile":
        result = replace(
            self,
            object_name=object_name,
            recorded_at=utc_now_iso(),
            grasp_pose_odom=grasp_pose,
            alignment=self.alignment.with_reference(
                point_base,
                object_name=object_name,
                pick_profile=pick_profile,
                orientation_deg=orientation_deg,
                orientation_class=orientation_class,
                orientation_quality=orientation_quality,
                require_orientation_match=require_orientation_match,
            ),
            recording_state="complete",
            grasp_executor=grasp_executor,
            grasp_trajectory=grasp_trajectory,
            grasp_keyframe_profile=grasp_keyframe_profile,
            pick_profile=pick_profile,
            graspable_max_range_m=(
                self.graspable_max_range_m
                if graspable_max_range_m is None
                else float(graspable_max_range_m)
            ),
        )
        result.validate_for_execution()
        return result

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
        """Legacy one-pose registration retained for compatibility."""
        search = self.with_search_recording(
            point_base=point_base,
            search_pose=search_pose,
            object_point_odom=object_point_odom,
            object_name=object_name,
            recognition_score=0.0,
        )
        return search.with_grasp_recording(
            point_base=point_base,
            grasp_pose=search_pose,
            object_name=object_name,
            grasp_executor=grasp_executor,
            grasp_trajectory=grasp_trajectory,
            grasp_keyframe_profile=grasp_keyframe_profile,
            pick_profile=pick_profile,
            orientation_deg=orientation_deg,
            orientation_class=orientation_class,
            orientation_quality=orientation_quality,
            require_orientation_match=require_orientation_match,
            graspable_max_range_m=max(
                self.graspable_max_range_m,
                planar_range_m(point_base),
            ),
        )

    def target_grasp_pose(self, current_object_point_odom: Vector3) -> OdomPose:
        if self.position_scope != "pico_odom_session":
            raise ValueError(
                "camera-relative profiles do not define an odometry grasp pose"
            )
        grasp_pose = self.grasp_pose_odom or self.search_pose_odom
        relocation = math.hypot(
            float(current_object_point_odom[0]) - float(self.object_point_odom[0]),
            float(current_object_point_odom[1]) - float(self.object_point_odom[1]),
        )
        if relocation > self.maximum_object_relocation_m:
            raise ValueError("object relocation exceeds profile limit")
        return translated_pose_for_object_shift(
            grasp_pose,
            self.object_point_odom,
            current_object_point_odom,
        )

    def to_mapping(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "object_name": self.object_name,
            "recorded_at": self.recorded_at,
            "recording_state": self.recording_state,
            "position_scope": self.position_scope,
            "execution_authority": (
                "fresh_rgbd_localization"
                if self.position_scope == "camera_relative"
                else "pico_odom_session"
            ),
            # Compatibility mirror.  The canonical schema remains
            # grasp.keyframe_profile, but older diagnostics looked at this
            # top-level name directly.
            "grasp_keyframe_profile": self.grasp_keyframe_profile,
            "fixed_distance_gate_enabled": (
                self.position_scope != "camera_relative"
            ),
            "search_pose_odom": self.search_pose_odom.to_mapping(),
            "object_point_odom": {
                "x": self.object_point_odom[0],
                "y": self.object_point_odom[1],
                "z": self.object_point_odom[2],
            },
            "alignment": self.alignment.to_mapping(),
            "recognition": {
                "point_base": (
                    None
                    if self.recognition_point_base is None
                    else {
                        "x": self.recognition_point_base[0],
                        "y": self.recognition_point_base[1],
                        "z": self.recognition_point_base[2],
                    }
                ),
                "score": self.recognition_score,
                "minimum_range_m": self.recognition_min_range_m,
                "maximum_range_m": self.recognition_max_range_m,
            },
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
            "distance_handoff": {
                "enabled": self.distance_handoff_enabled,
                "graspable_min_range_m": self.graspable_min_range_m,
                "graspable_max_range_m": self.graspable_max_range_m,
                "position_tolerance_m": self.approach_position_tolerance_m,
                "angle_tolerance_deg": self.approach_angle_tolerance_deg,
                "max_move_step_m": self.approach_max_move_step_m,
                "max_turn_step_deg": self.approach_max_turn_step_deg,
                "max_iterations": self.approach_max_iterations,
                "max_total_move_m": self.approach_max_total_move_m,
                "max_total_turn_deg": self.approach_max_total_turn_deg,
                "base_linear_error_fraction": self.base_linear_error_fraction,
                "base_turn_error_fraction": self.base_turn_error_fraction,
                "turn_translation_drift_m_per_360": self.turn_translation_drift_m_per_360,
                "maximum_uncertainty_m": self.maximum_handoff_uncertainty_m,
                "maximum_object_relocation_m": self.maximum_object_relocation_m,
            },
        }
        if self.position_scope == "camera_relative":
            # Keep the legacy dataclass fields internally for schema loading,
            # but do not serialize the obsolete two-distance thresholds into a
            # camera-authoritative profile.
            recognition = result.get("recognition", {})
            if isinstance(recognition, dict):
                recognition.pop("minimum_range_m", None)
                recognition.pop("maximum_range_m", None)
                recognition["fixed_range_gate_enabled"] = False
            handoff = result.get("distance_handoff", {})
            if isinstance(handoff, dict):
                handoff.pop("graspable_min_range_m", None)
                handoff.pop("graspable_max_range_m", None)
                handoff["fixed_range_gate_enabled"] = False

        if self.grasp_pose_odom is not None:
            result["grasp_pose_odom"] = self.grasp_pose_odom.to_mapping()
        return result


class StoredObjectProfileStore:
    SCHEMA = "macrobot.stored_object_runtime/v1"
    SUPPORTED_SCHEMAS = {"macrobot.stored_object_runtime/v0", SCHEMA}

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
        if schema not in self.SUPPORTED_SCHEMAS:
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
