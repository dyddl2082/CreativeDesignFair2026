"""Fast grasp-axis interception for MacRobot.

The controller uses a fresh RGB-D object point and the taught/current object
axis to move the differential-drive base directly to a pre-grasp corridor.
It deliberately separates the task into:

1. ``axis_intercept``: reach the taught grasp axis and orientation with one
   camera-atomic TURN -> MOVE -> TURN macro (or optional DRIVE_REL -> TURN),
   while optionally advancing to a configurable pre-grasp standoff;
2. ``axial_approach``: move a much larger step along that axis; and
3. ``precision_handoff``: let the existing camera-authoritative precision
   controller perform only the final small correction.

Coordinate convention inside this module:
- +x: forward
- +y: left
- +yaw: left / counter-clockwise

Pico ``TURN_DEG`` uses the opposite sign on this robot (+ is right/clockwise).
The existing camera-authoritative motion adapter owns that final sign
conversion.  This module never negates Pico commands directly.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

from .camera_pose_relocation import (
    MotionPrimitive,
    RelativeRobotPose,
    decompose_drive_then_turn,
    decompose_turn_move_turn,
    minimum_object_range_during_primitives,
    object_after_relative_robot_pose,
    relative_pose_from_primitives,
    robot_pose_for_object_target,
    signed_axial_error_deg,
    wrap_angle_deg,
)

PATCH_MARKER = "macrobot_fast_axis_intercept_v6"
Vector2 = tuple[float, float]


@dataclass(frozen=True)
class AxisFrameError:
    """Exact target displacement expressed in the desired final robot frame."""

    desired_robot_yaw_deg: float
    object_point_after_yaw_only: Vector2
    along_axis_error_m: float
    cross_track_error_m: float


@dataclass(frozen=True)
class FastAxisPlan:
    stage: str
    handoff_ready: bool
    reason: str
    current_point: Vector2
    reference_point: Vector2
    target_point: Vector2
    desired_point: Vector2
    current_orientation_deg: float
    reference_orientation_deg: float
    orientation_error_deg: float
    raw_forward_error_m: float
    raw_lateral_error_m: float
    along_axis_error_m: float
    cross_track_error_m: float
    progress: float
    robot_target: RelativeRobotPose
    primitives: tuple[MotionPrimitive, ...]
    predicted_point: Vector2
    predicted_orientation_deg: float
    predicted_minimum_object_range_m: float
    decomposition: str

    @property
    def total_move_m(self) -> float:
        return sum(
            abs(float(item.amount))
            for item in self.primitives
            if item.kind in {"move", "drive"}
        )

    @property
    def total_turn_deg(self) -> float:
        return sum(
            abs(float(item.amount if item.kind == "turn" else item.yaw_deg))
            for item in self.primitives
            if item.kind in {"turn", "drive"}
        )


def _finite_pair(value: Sequence[float], label: str) -> Vector2:
    if len(value) != 2:
        raise ValueError(f"{label} must contain exactly two values")
    result = (float(value[0]), float(value[1]))
    if not all(math.isfinite(item) for item in result):
        raise ValueError(f"{label} must be finite")
    return result


def _rotate(point: Vector2, yaw_deg: float) -> Vector2:
    theta = math.radians(float(yaw_deg))
    cosine = math.cos(theta)
    sine = math.sin(theta)
    return (
        cosine * point[0] - sine * point[1],
        sine * point[0] + cosine * point[1],
    )


def axis_frame_error(
    current_point: Sequence[float],
    reference_point: Sequence[float],
    current_orientation_deg: float,
    reference_orientation_deg: float,
    *,
    orientation_error_override_deg: float | None = None,
) -> AxisFrameError:
    """Return the exact pose error in the desired final robot frame.

    Let ``theta`` be the robot yaw that restores the taught object-axis angle.
    If the robot were rotated by ``theta`` without translating, the object
    would appear at ``q = R(-theta) p_current``.  Therefore

    ``q.x - p_reference.x`` is the remaining motion along the taught approach
    axis, and ``q.y - p_reference.y`` is the cross-track displacement needed
    to get onto that axis.
    """

    current = _finite_pair(current_point, "current_point")
    reference = _finite_pair(reference_point, "reference_point")
    if orientation_error_override_deg is None:
        yaw = signed_axial_error_deg(
            float(current_orientation_deg),
            float(reference_orientation_deg),
        )
    else:
        raw_yaw = float(orientation_error_override_deg)
        if not math.isfinite(raw_yaw):
            raise ValueError("orientation_error_override_deg must be finite")
        # The parent orientation assessment may use a measured 3-D base_link
        # axis rather than the scalar image angle.  Preserve its signed axial
        # result while normalising the 180-degree symmetry.
        yaw = ((raw_yaw + 90.0) % 180.0) - 90.0
    yaw_only_point = _rotate(current, -yaw)
    return AxisFrameError(
        desired_robot_yaw_deg=yaw,
        object_point_after_yaw_only=yaw_only_point,
        along_axis_error_m=yaw_only_point[0] - reference[0],
        cross_track_error_m=yaw_only_point[1] - reference[1],
    )


def _primitive_bounds_ok(
    primitives: Sequence[MotionPrimitive],
    *,
    maximum_translation_m: float,
    maximum_turn_primitive_deg: float,
    allow_reverse: bool,
) -> bool:
    for item in primitives:
        if item.kind in {"move", "drive"}:
            if abs(float(item.amount)) > abs(float(maximum_translation_m)) + 1e-9:
                return False
            if not allow_reverse and float(item.amount) < -1e-9:
                return False
        turn = item.amount if item.kind == "turn" else item.yaw_deg
        if item.kind in {"turn", "drive"} and abs(float(turn)) > abs(
            float(maximum_turn_primitive_deg)
        ) + 1e-9:
            return False
    return True


def _candidate_cost(primitives: Sequence[MotionPrimitive]) -> float:
    """A simple expected-time proxy used only to choose valid decompositions."""

    move = sum(
        abs(float(item.amount))
        for item in primitives
        if item.kind in {"move", "drive"}
    )
    turn = sum(
        abs(float(item.amount if item.kind == "turn" else item.yaw_deg))
        for item in primitives
        if item.kind in {"turn", "drive"}
    )
    # One metre of travel and about 180 degrees of in-place rotation receive
    # comparable cost.  A small primitive-count penalty prefers an arc when
    # both paths are otherwise similar.
    return move + turn / 180.0 + 0.01 * max(0, len(primitives) - 1)


def _plan_toward_object_target(
    *,
    current: Vector2,
    target: Vector2,
    orientation_error_deg: float,
    requested_progress: float,
    maximum_translation_m: float,
    maximum_turn_primitive_deg: float,
    minimum_object_range_m: float,
    allow_reverse: bool,
    reverse_turn_penalty_deg: float,
    minimum_turn_deg: float,
    minimum_move_m: float,
    prefer_drive_rel: bool,
    maximum_drive_yaw_deg: float,
    minimum_drive_radius_m: float,
) -> tuple[
    float,
    Vector2,
    RelativeRobotPose,
    tuple[MotionPrimitive, ...],
    float,
    str,
]:
    progress = max(0.05, min(1.0, float(requested_progress)))
    last_reason = "no_valid_compound_motion"
    for _ in range(24):
        desired = (
            current[0] + progress * (target[0] - current[0]),
            current[1] + progress * (target[1] - current[1]),
        )
        yaw = progress * float(orientation_error_deg)
        pose = robot_pose_for_object_target(current, desired, yaw)
        candidates: list[tuple[str, tuple[MotionPrimitive, ...]]] = []

        if bool(prefer_drive_rel):
            try:
                drive = decompose_drive_then_turn(
                    pose,
                    maximum_drive_yaw_deg=maximum_drive_yaw_deg,
                    minimum_drive_radius_m=minimum_drive_radius_m,
                    minimum_turn_deg=minimum_turn_deg,
                    minimum_move_m=minimum_move_m,
                )
                candidates.append(("drive_rel_then_turn", drive))
            except ValueError as error:
                last_reason = str(error)

        turn_move_turn = decompose_turn_move_turn(
            pose,
            allow_reverse=allow_reverse,
            reverse_turn_penalty_deg=reverse_turn_penalty_deg,
            minimum_turn_deg=minimum_turn_deg,
            minimum_move_m=minimum_move_m,
        )
        candidates.append(("turn_move_turn", turn_move_turn))

        valid: list[
            tuple[float, str, tuple[MotionPrimitive, ...], float, RelativeRobotPose]
        ] = []
        for decomposition, primitives in candidates:
            if not primitives:
                last_reason = "decomposition_was_empty"
                continue
            if not _primitive_bounds_ok(
                primitives,
                maximum_translation_m=maximum_translation_m,
                maximum_turn_primitive_deg=maximum_turn_primitive_deg,
                allow_reverse=allow_reverse,
            ):
                last_reason = "primitive_bound_exceeded"
                continue
            clearance = minimum_object_range_during_primitives(current, primitives)
            if clearance < max(0.0, float(minimum_object_range_m)):
                last_reason = "predicted_object_clearance_too_small"
                continue
            composed = relative_pose_from_primitives(primitives)
            pose_error = math.hypot(
                float(composed.x_m) - float(pose.x_m),
                float(composed.y_m) - float(pose.y_m),
            )
            yaw_error = abs(
                wrap_angle_deg(float(composed.yaw_deg) - float(pose.yaw_deg))
            )
            # camera_pose_relocation intentionally removes turns/moves below
            # the configured actuator thresholds.  Treat that bounded cleanup
            # as equivalent instead of rejecting an otherwise valid macro.
            pose_tolerance = max(1e-6, abs(float(minimum_move_m)) + 1e-6)
            yaw_tolerance = max(1e-6, abs(float(minimum_turn_deg)) + 1e-6)
            if pose_error > pose_tolerance or yaw_error > yaw_tolerance:
                last_reason = "primitive_decomposition_error_too_large"
                continue
            valid.append(
                (
                    _candidate_cost(primitives),
                    decomposition,
                    primitives,
                    clearance,
                    composed,
                )
            )
        if valid:
            _, decomposition, primitives, clearance, composed = min(
                valid,
                key=lambda item: item[0],
            )
            return (
                progress,
                desired,
                composed,
                primitives,
                clearance,
                decomposition,
            )
        progress *= 0.78
        if progress < 0.05:
            break
    raise ValueError(last_reason)


def choose_fast_axis_plan(
    current_point: Sequence[float],
    reference_point: Sequence[float],
    current_orientation_deg: float,
    reference_orientation_deg: float,
    *,
    handoff_forward_tolerance_m: float = 0.035,
    handoff_lateral_tolerance_m: float = 0.012,
    handoff_orientation_tolerance_deg: float = 5.0,
    axis_corridor_tolerance_m: float = 0.015,
    axis_orientation_tolerance_deg: float = 7.0,
    pregrasp_standoff_m: float = 0.080,
    intercept_progress: float = 0.92,
    intercept_maximum_translation_m: float = 0.180,
    intercept_maximum_turn_deg: float = 105.0,
    approach_progress: float = 0.90,
    approach_maximum_translation_m: float = 0.150,
    approach_maximum_turn_deg: float = 30.0,
    minimum_object_range_m: float = 0.120,
    allow_reverse: bool = False,
    reverse_turn_penalty_deg: float = 30.0,
    minimum_turn_deg: float = 0.75,
    minimum_move_m: float = 0.004,
    prefer_drive_rel: bool = False,
    maximum_drive_yaw_deg: float = 25.0,
    minimum_drive_radius_m: float = 0.10,
    orientation_error_override_deg: float | None = None,
) -> FastAxisPlan:
    """Choose one camera-atomic coarse motion before precision docking.

    ``axis_intercept`` aims at an object point
    ``(reference_forward + standoff, reference_lateral)`` in the desired final
    robot frame.  This is a pre-grasp point on the taught approach corridor.
    When the object is already closer than that standoff, the controller keeps
    the current along-axis distance instead of deliberately backing away.

    Once cross-track and orientation are small, ``axial_approach`` aims at the
    exact taught point with a much larger step than the legacy 12 mm precision
    chunk.  The existing controller takes over only inside the handoff box.
    """

    current = _finite_pair(current_point, "current_point")
    reference = _finite_pair(reference_point, "reference_point")
    current_orientation = float(current_orientation_deg)
    reference_orientation = float(reference_orientation_deg)
    if not math.isfinite(current_orientation) or not math.isfinite(
        reference_orientation
    ):
        raise ValueError("orientation values must be finite")

    axis = axis_frame_error(
        current,
        reference,
        current_orientation,
        reference_orientation,
        orientation_error_override_deg=orientation_error_override_deg,
    )
    raw_forward_error = current[0] - reference[0]
    raw_lateral_error = current[1] - reference[1]

    handoff_ready = (
        abs(axis.along_axis_error_m)
        <= abs(float(handoff_forward_tolerance_m))
        and abs(axis.cross_track_error_m)
        <= abs(float(handoff_lateral_tolerance_m))
        and abs(axis.desired_robot_yaw_deg)
        <= abs(float(handoff_orientation_tolerance_deg))
    )
    zero_pose = RelativeRobotPose(0.0, 0.0, 0.0)
    if handoff_ready:
        return FastAxisPlan(
            stage="precision_handoff",
            handoff_ready=True,
            reason="inside_fast_axis_handoff_box",
            current_point=current,
            reference_point=reference,
            target_point=reference,
            desired_point=current,
            current_orientation_deg=current_orientation,
            reference_orientation_deg=reference_orientation,
            orientation_error_deg=axis.desired_robot_yaw_deg,
            raw_forward_error_m=raw_forward_error,
            raw_lateral_error_m=raw_lateral_error,
            along_axis_error_m=axis.along_axis_error_m,
            cross_track_error_m=axis.cross_track_error_m,
            progress=0.0,
            robot_target=zero_pose,
            primitives=(),
            predicted_point=current,
            predicted_orientation_deg=current_orientation,
            predicted_minimum_object_range_m=math.hypot(*current),
            decomposition="none",
        )

    needs_axis_intercept = (
        abs(axis.cross_track_error_m) > abs(float(axis_corridor_tolerance_m))
        or abs(axis.desired_robot_yaw_deg)
        > abs(float(axis_orientation_tolerance_deg))
    )
    if needs_axis_intercept:
        stage = "axis_intercept"
        # Aim for a safe point on the taught grasp axis.  When rotation-only
        # would leave the object in front of the robot, preserve that current
        # axis-frame range if it is already closer than the nominal pre-grasp
        # standoff; this produces the shortest lateral dog-leg and avoids an
        # unnecessary move away from the object.  When that range is invalid
        # (object would be behind after the desired yaw), use the safe
        # pre-grasp point and let the primitive bounds decide whether the
        # manoeuvre is executable.
        safe_axis_forward = max(
            max(0.0, float(minimum_object_range_m)),
            reference[0] + max(0.0, float(pregrasp_standoff_m)),
        )
        yaw_only_forward = axis.object_point_after_yaw_only[0]
        if yaw_only_forward >= max(0.0, float(minimum_object_range_m)):
            target_forward = min(yaw_only_forward, safe_axis_forward)
        else:
            target_forward = safe_axis_forward
        target = (target_forward, reference[1])
        requested_progress = intercept_progress
        maximum_translation = intercept_maximum_translation_m
        maximum_turn = intercept_maximum_turn_deg
    else:
        stage = "axial_approach"
        target = reference
        requested_progress = approach_progress
        maximum_translation = approach_maximum_translation_m
        maximum_turn = approach_maximum_turn_deg

    if target[0] <= 0.0:
        return FastAxisPlan(
            stage=stage,
            handoff_ready=False,
            reason="target_object_point_not_in_front_half_plane",
            current_point=current,
            reference_point=reference,
            target_point=target,
            desired_point=current,
            current_orientation_deg=current_orientation,
            reference_orientation_deg=reference_orientation,
            orientation_error_deg=axis.desired_robot_yaw_deg,
            raw_forward_error_m=raw_forward_error,
            raw_lateral_error_m=raw_lateral_error,
            along_axis_error_m=axis.along_axis_error_m,
            cross_track_error_m=axis.cross_track_error_m,
            progress=0.0,
            robot_target=zero_pose,
            primitives=(),
            predicted_point=current,
            predicted_orientation_deg=current_orientation,
            predicted_minimum_object_range_m=math.hypot(*current),
            decomposition="none",
        )

    try:
        (
            progress,
            desired,
            robot_target,
            primitives,
            clearance,
            decomposition,
        ) = _plan_toward_object_target(
            current=current,
            target=target,
            orientation_error_deg=axis.desired_robot_yaw_deg,
            requested_progress=requested_progress,
            maximum_translation_m=maximum_translation,
            maximum_turn_primitive_deg=maximum_turn,
            minimum_object_range_m=minimum_object_range_m,
            allow_reverse=allow_reverse,
            reverse_turn_penalty_deg=reverse_turn_penalty_deg,
            minimum_turn_deg=minimum_turn_deg,
            minimum_move_m=minimum_move_m,
            prefer_drive_rel=prefer_drive_rel,
            maximum_drive_yaw_deg=maximum_drive_yaw_deg,
            minimum_drive_radius_m=minimum_drive_radius_m,
        )
    except ValueError as error:
        return FastAxisPlan(
            stage=stage,
            handoff_ready=False,
            reason=str(error),
            current_point=current,
            reference_point=reference,
            target_point=target,
            desired_point=current,
            current_orientation_deg=current_orientation,
            reference_orientation_deg=reference_orientation,
            orientation_error_deg=axis.desired_robot_yaw_deg,
            raw_forward_error_m=raw_forward_error,
            raw_lateral_error_m=raw_lateral_error,
            along_axis_error_m=axis.along_axis_error_m,
            cross_track_error_m=axis.cross_track_error_m,
            progress=0.0,
            robot_target=zero_pose,
            primitives=(),
            predicted_point=current,
            predicted_orientation_deg=current_orientation,
            predicted_minimum_object_range_m=math.hypot(*current),
            decomposition="none",
        )

    predicted_point = object_after_relative_robot_pose(current, robot_target)
    predicted_orientation = (
        current_orientation - float(robot_target.yaw_deg)
    ) % 180.0
    return FastAxisPlan(
        stage=stage,
        handoff_ready=False,
        reason="fast_axis_compound_motion_selected",
        current_point=current,
        reference_point=reference,
        target_point=target,
        desired_point=desired,
        current_orientation_deg=current_orientation,
        reference_orientation_deg=reference_orientation,
        orientation_error_deg=axis.desired_robot_yaw_deg,
        raw_forward_error_m=raw_forward_error,
        raw_lateral_error_m=raw_lateral_error,
        along_axis_error_m=axis.along_axis_error_m,
        cross_track_error_m=axis.cross_track_error_m,
        progress=progress,
        robot_target=robot_target,
        primitives=primitives,
        predicted_point=predicted_point,
        predicted_orientation_deg=predicted_orientation,
        predicted_minimum_object_range_m=clearance,
        decomposition=decomposition,
    )


def _arc_endpoint(distance_m: float, yaw_deg: float) -> Vector2:
    theta = math.radians(float(yaw_deg))
    distance = float(distance_m)
    if abs(theta) <= 1e-9:
        return distance, 0.0
    return (
        distance * math.sin(theta) / theta,
        distance * (1.0 - math.cos(theta)) / theta,
    )


def apply_primitives_to_object(
    point_xy: Sequence[float],
    orientation_deg: float,
    primitives: Sequence[MotionPrimitive],
    *,
    move_scale: float = 1.0,
    turn_scale: float = 1.0,
) -> tuple[Vector2, float]:
    """Deterministic helper for controller regression tests."""

    point = _finite_pair(point_xy, "point_xy")
    orientation = float(orientation_deg)
    for primitive in primitives:
        if primitive.kind == "turn":
            actual_yaw = float(primitive.amount) * float(turn_scale)
            point = _rotate(point, -actual_yaw)
            orientation = (orientation - actual_yaw) % 180.0
            continue
        if primitive.kind == "move":
            actual_distance = float(primitive.amount) * float(move_scale)
            point = (point[0] - actual_distance, point[1])
            continue
        actual_distance = float(primitive.amount) * float(move_scale)
        actual_yaw = float(primitive.yaw_deg) * float(turn_scale)
        translation = _arc_endpoint(actual_distance, actual_yaw)
        point = _rotate(
            (point[0] - translation[0], point[1] - translation[1]),
            -actual_yaw,
        )
        orientation = (orientation - actual_yaw) % 180.0
    return point, orientation


def simulate_until_handoff(
    current_point: Sequence[float],
    reference_point: Sequence[float],
    current_orientation_deg: float,
    reference_orientation_deg: float,
    *,
    maximum_steps: int = 10,
    move_scale: float = 1.0,
    turn_scale: float = 1.0,
    planner_kwargs: dict | None = None,
) -> tuple[bool, int, Vector2, float, tuple[str, ...]]:
    point = _finite_pair(current_point, "current_point")
    orientation = float(current_orientation_deg)
    stages: list[str] = []
    kwargs = dict(planner_kwargs or {})
    for index in range(max(1, int(maximum_steps))):
        plan = choose_fast_axis_plan(
            point,
            reference_point,
            orientation,
            reference_orientation_deg,
            **kwargs,
        )
        stages.append(plan.stage)
        if plan.handoff_ready:
            return True, index, point, orientation, tuple(stages)
        if not plan.primitives:
            return False, index, point, orientation, tuple(stages)
        point, orientation = apply_primitives_to_object(
            point,
            orientation,
            plan.primitives,
            move_scale=move_scale,
            turn_scale=turn_scale,
        )
    return False, int(maximum_steps), point, orientation, tuple(stages)
