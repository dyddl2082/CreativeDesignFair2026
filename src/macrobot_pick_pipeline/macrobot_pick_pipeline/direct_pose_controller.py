"""Direct camera-pose pursuit for MacRobot.

The old controller treats bearing, range, and object orientation as separate
corrections.  This module instead solves the robot SE(2) displacement that
would recreate the *taught camera-relative object pose* from the current RGB-D
observation, then executes only a bounded fraction of that displacement before
re-observing.

Coordinate convention inside this module:
- +x: forward
- +y: left
- +yaw: left / counter-clockwise

Legacy Pico TURN_DEG has the opposite sign (+ is right / clockwise).  The
existing camera-authoritative motion adapter already performs that conversion;
this module must never negate TURN_DEG itself.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

PATCH_MARKER = "macrobot_direct_pose_pursuit_v5"


@dataclass(frozen=True)
class DirectPrimitive:
    kind: str
    amount: float
    yaw_deg: float = 0.0

    def __post_init__(self) -> None:
        if self.kind not in {"turn", "move", "drive"}:
            raise ValueError(f"unsupported primitive kind: {self.kind}")
        if not math.isfinite(float(self.amount)):
            raise ValueError("primitive amount must be finite")
        if not math.isfinite(float(self.yaw_deg)):
            raise ValueError("primitive yaw must be finite")
        if self.kind != "drive" and abs(float(self.yaw_deg)) > 1e-12:
            raise ValueError("only drive primitives may contain yaw_deg")


@dataclass(frozen=True)
class DirectPosePlan:
    reached: bool
    reason: str
    current_point: tuple[float, float]
    reference_point: tuple[float, float]
    desired_point: tuple[float, float]
    current_orientation_deg: float
    reference_orientation_deg: float
    orientation_error_deg: float
    forward_error_m: float
    lateral_error_m: float
    position_error_m: float
    progress: float
    exact_goal_robot_pose: tuple[float, float, float]
    intermediate_robot_pose: tuple[float, float, float]
    primitives: tuple[DirectPrimitive, ...]
    predicted_point: tuple[float, float]
    predicted_orientation_deg: float
    predicted_minimum_object_range_m: float
    decomposition: str


def _finite_pair(value: Sequence[float], name: str) -> tuple[float, float]:
    if len(value) != 2:
        raise ValueError(f"{name} must contain exactly two values")
    result = (float(value[0]), float(value[1]))
    if not all(math.isfinite(item) for item in result):
        raise ValueError(f"{name} must be finite")
    return result


def wrap_angle_deg(value: float) -> float:
    angle = math.radians(float(value))
    return math.degrees(math.atan2(math.sin(angle), math.cos(angle)))


def signed_axial_error_deg(current_deg: float, reference_deg: float) -> float:
    current = float(current_deg)
    reference = float(reference_deg)
    if not math.isfinite(current) or not math.isfinite(reference):
        raise ValueError("orientation angles must be finite")
    return ((current - reference + 90.0) % 180.0) - 90.0


def _rotate(point: tuple[float, float], yaw_deg: float) -> tuple[float, float]:
    theta = math.radians(float(yaw_deg))
    c = math.cos(theta)
    s = math.sin(theta)
    return c * point[0] - s * point[1], s * point[0] + c * point[1]


def robot_pose_for_object_target(
    current_point: Sequence[float],
    desired_point: Sequence[float],
    yaw_deg: float,
) -> tuple[float, float, float]:
    """Solve t from p_new = R(-yaw) (p_current - t)."""
    current = _finite_pair(current_point, "current_point")
    desired = _finite_pair(desired_point, "desired_point")
    yaw = wrap_angle_deg(yaw_deg)
    rotated_desired = _rotate(desired, yaw)
    return current[0] - rotated_desired[0], current[1] - rotated_desired[1], yaw


def exact_robot_pose_for_taught_view(
    current_point: Sequence[float],
    reference_point: Sequence[float],
    current_orientation_deg: float,
    reference_orientation_deg: float,
) -> tuple[float, float, float]:
    yaw = signed_axial_error_deg(current_orientation_deg, reference_orientation_deg)
    return robot_pose_for_object_target(current_point, reference_point, yaw)


def _clean(primitives: list[DirectPrimitive], minimum_turn_deg: float, minimum_move_m: float) -> tuple[DirectPrimitive, ...]:
    out: list[DirectPrimitive] = []
    for item in primitives:
        if item.kind == "turn" and abs(item.amount) < abs(minimum_turn_deg):
            continue
        if item.kind in {"move", "drive"} and abs(item.amount) < abs(minimum_move_m):
            if item.kind == "drive" and abs(item.yaw_deg) >= abs(minimum_turn_deg):
                out.append(DirectPrimitive("turn", item.yaw_deg))
            continue
        out.append(item)
    return tuple(out)


def decompose_turn_move_turn(
    pose: Sequence[float],
    *,
    allow_reverse: bool,
    reverse_turn_penalty_deg: float,
    minimum_turn_deg: float,
    minimum_move_m: float,
) -> tuple[DirectPrimitive, ...]:
    x, y, yaw = (float(pose[0]), float(pose[1]), float(pose[2]))
    distance = math.hypot(x, y)
    if distance < abs(float(minimum_move_m)):
        return _clean([DirectPrimitive("turn", wrap_angle_deg(yaw))], minimum_turn_deg, minimum_move_m)

    forward_heading = math.degrees(math.atan2(y, x))
    forward_final = wrap_angle_deg(yaw - forward_heading)
    options: list[tuple[float, list[DirectPrimitive]]] = [
        (
            abs(forward_heading) + abs(forward_final),
            [
                DirectPrimitive("turn", wrap_angle_deg(forward_heading)),
                DirectPrimitive("move", distance),
                DirectPrimitive("turn", forward_final),
            ],
        )
    ]
    if allow_reverse:
        reverse_heading = wrap_angle_deg(forward_heading + 180.0)
        reverse_final = wrap_angle_deg(yaw - reverse_heading)
        reverse_cost = abs(reverse_heading) + abs(reverse_final) + max(0.0, float(reverse_turn_penalty_deg))
        options.append(
            (
                reverse_cost,
                [
                    DirectPrimitive("turn", reverse_heading),
                    DirectPrimitive("move", -distance),
                    DirectPrimitive("turn", reverse_final),
                ],
            )
        )
    _, selected = min(options, key=lambda item: item[0])
    return _clean(selected, minimum_turn_deg, minimum_move_m)


def _arc_endpoint(distance_m: float, yaw_deg: float) -> tuple[float, float]:
    theta = math.radians(float(yaw_deg))
    distance = float(distance_m)
    if abs(theta) <= 1e-9:
        return distance, 0.0
    return (
        distance * math.sin(theta) / theta,
        distance * (1.0 - math.cos(theta)) / theta,
    )


def decompose_drive_then_turn(
    pose: Sequence[float],
    *,
    maximum_drive_yaw_deg: float,
    minimum_drive_radius_m: float,
    minimum_turn_deg: float,
    minimum_move_m: float,
) -> tuple[DirectPrimitive, ...]:
    x, y, yaw = (float(pose[0]), float(pose[1]), float(pose[2]))
    chord = math.hypot(x, y)
    if chord < abs(float(minimum_move_m)):
        return _clean([DirectPrimitive("turn", wrap_angle_deg(yaw))], minimum_turn_deg, minimum_move_m)
    direction = 1.0 if x >= 0.0 else -1.0
    equivalent_x = direction * x
    equivalent_y = direction * y
    alpha = math.atan2(equivalent_y, equivalent_x)
    arc_yaw_rad = 2.0 * alpha
    arc_yaw_deg = math.degrees(arc_yaw_rad)
    if abs(arc_yaw_deg) > abs(float(maximum_drive_yaw_deg)) + 1e-9:
        raise ValueError("required_drive_yaw_too_large")
    if abs(arc_yaw_rad) <= 1e-9:
        unsigned_distance = chord
        radius = math.inf
    else:
        denominator = 2.0 * math.sin(0.5 * arc_yaw_rad)
        if abs(denominator) <= 1e-9:
            raise ValueError("drive_arc_is_singular")
        unsigned_distance = chord * arc_yaw_rad / denominator
        radius = abs(unsigned_distance / arc_yaw_rad)
    if radius < max(0.0, float(minimum_drive_radius_m)):
        raise ValueError("required_drive_radius_too_small")
    drive_distance = direction * abs(unsigned_distance)
    final_turn = wrap_angle_deg(yaw - arc_yaw_deg)
    return _clean(
        [DirectPrimitive("drive", drive_distance, arc_yaw_deg), DirectPrimitive("turn", final_turn)],
        minimum_turn_deg,
        minimum_move_m,
    )


def apply_primitive_to_object(
    point_xy: Sequence[float],
    orientation_deg: float,
    primitive: DirectPrimitive,
    *,
    move_scale: float = 1.0,
    turn_scale: float = 1.0,
) -> tuple[tuple[float, float], float]:
    point = _finite_pair(point_xy, "point_xy")
    orientation = float(orientation_deg)
    if primitive.kind == "turn":
        actual = primitive.amount * float(turn_scale)
        return _rotate(point, -actual), (orientation - actual) % 180.0
    if primitive.kind == "move":
        actual = primitive.amount * float(move_scale)
        return (point[0] - actual, point[1]), orientation % 180.0
    actual_distance = primitive.amount * float(move_scale)
    actual_yaw = primitive.yaw_deg * float(turn_scale)
    translation = _arc_endpoint(actual_distance, actual_yaw)
    translated = (point[0] - translation[0], point[1] - translation[1])
    return _rotate(translated, -actual_yaw), (orientation - actual_yaw) % 180.0


def apply_macro_to_object(
    point_xy: Sequence[float],
    orientation_deg: float,
    primitives: Sequence[DirectPrimitive],
    *,
    move_scale: float = 1.0,
    turn_scale: float = 1.0,
) -> tuple[tuple[float, float], float]:
    point = _finite_pair(point_xy, "point_xy")
    orientation = float(orientation_deg)
    for primitive in primitives:
        point, orientation = apply_primitive_to_object(
            point,
            orientation,
            primitive,
            move_scale=move_scale,
            turn_scale=turn_scale,
        )
    return point, orientation


def minimum_object_range_during_macro(
    point_xy: Sequence[float],
    primitives: Sequence[DirectPrimitive],
    *,
    samples_per_motion: int = 31,
) -> float:
    point = _finite_pair(point_xy, "point_xy")
    robot_x = robot_y = robot_yaw = 0.0
    minimum = math.hypot(point[0], point[1])
    count = max(3, int(samples_per_motion))
    for primitive in primitives:
        if primitive.kind == "turn":
            robot_yaw = wrap_angle_deg(robot_yaw + primitive.amount)
            continue
        for index in range(1, count + 1):
            fraction = index / float(count)
            if primitive.kind == "move":
                local = (primitive.amount * fraction, 0.0)
            else:
                theta = math.radians(primitive.yaw_deg)
                if abs(theta) <= 1e-9:
                    local = (primitive.amount * fraction, 0.0)
                else:
                    radius = primitive.amount / theta
                    partial = theta * fraction
                    local = (radius * math.sin(partial), radius * (1.0 - math.cos(partial)))
            delta = _rotate(local, robot_yaw)
            sample_x = robot_x + delta[0]
            sample_y = robot_y + delta[1]
            minimum = min(minimum, math.hypot(point[0] - sample_x, point[1] - sample_y))
        if primitive.kind == "move":
            endpoint = (primitive.amount, 0.0)
        else:
            endpoint = _arc_endpoint(primitive.amount, primitive.yaw_deg)
        delta = _rotate(endpoint, robot_yaw)
        robot_x += delta[0]
        robot_y += delta[1]
        if primitive.kind == "drive":
            robot_yaw = wrap_angle_deg(robot_yaw + primitive.yaw_deg)
    return minimum


def _primitive_bounds_ok(
    primitives: Sequence[DirectPrimitive],
    *,
    maximum_translation_m: float,
    maximum_turn_primitive_deg: float,
) -> bool:
    for item in primitives:
        if item.kind in {"move", "drive"} and abs(item.amount) > abs(maximum_translation_m) + 1e-9:
            return False
        turn = item.amount if item.kind == "turn" else item.yaw_deg
        if item.kind in {"turn", "drive"} and abs(turn) > abs(maximum_turn_primitive_deg) + 1e-9:
            return False
    return True


def choose_direct_pose_macro(
    current_point: Sequence[float],
    reference_point: Sequence[float],
    current_orientation_deg: float,
    reference_orientation_deg: float,
    *,
    forward_tolerance_m: float = 0.005,
    lateral_tolerance_m: float = 0.005,
    orientation_tolerance_deg: float = 4.0,
    coarse_progress: float = 0.72,
    near_progress: float = 0.45,
    near_position_error_m: float = 0.025,
    near_orientation_error_deg: float = 8.0,
    maximum_translation_m: float = 0.065,
    near_maximum_translation_m: float = 0.030,
    maximum_turn_primitive_deg: float = 100.0,
    minimum_turn_deg: float = 0.75,
    minimum_move_m: float = 0.005,
    minimum_object_range_m: float = 0.12,
    allow_reverse: bool = False,
    reverse_turn_penalty_deg: float = 25.0,
    prefer_drive_rel: bool = True,
    maximum_drive_yaw_deg: float = 20.0,
    minimum_drive_radius_m: float = 0.08,
) -> DirectPosePlan:
    """Plan one bounded compound move toward the taught camera-relative pose.

    The interpolation is in object-pose space, not in the old sequence of
    bearing -> forward -> lateral -> orientation corrections.  The macro is
    executed without a camera decision between its low-level primitives.  The
    next decision always starts from a fresh RGB-D observation.
    """
    current = _finite_pair(current_point, "current_point")
    reference = _finite_pair(reference_point, "reference_point")
    current_orientation = float(current_orientation_deg)
    reference_orientation = float(reference_orientation_deg)
    if not math.isfinite(current_orientation) or not math.isfinite(reference_orientation):
        raise ValueError("orientation values must be finite")

    forward_error = current[0] - reference[0]
    lateral_error = current[1] - reference[1]
    position_error = math.hypot(forward_error, lateral_error)
    orientation_error = signed_axial_error_deg(current_orientation, reference_orientation)
    exact_goal = exact_robot_pose_for_taught_view(
        current,
        reference,
        current_orientation,
        reference_orientation,
    )
    reached = (
        abs(forward_error) <= abs(float(forward_tolerance_m))
        and abs(lateral_error) <= abs(float(lateral_tolerance_m))
        and abs(orientation_error) <= abs(float(orientation_tolerance_deg))
    )
    if reached:
        return DirectPosePlan(
            True,
            "joint_camera_pose_within_tolerance",
            current,
            reference,
            current,
            current_orientation,
            reference_orientation,
            orientation_error,
            forward_error,
            lateral_error,
            position_error,
            0.0,
            exact_goal,
            (0.0, 0.0, 0.0),
            (),
            current,
            current_orientation,
            math.hypot(*current),
            "none",
        )

    near = (
        position_error <= abs(float(near_position_error_m))
        and abs(orientation_error) <= abs(float(near_orientation_error_deg))
    )
    requested_progress = near_progress if near else coarse_progress
    requested_progress = max(0.08, min(0.95, float(requested_progress)))
    max_translation = abs(float(near_maximum_translation_m if near else maximum_translation_m))
    max_turn = abs(float(maximum_turn_primitive_deg))

    progress_values: list[float] = []
    progress = requested_progress
    while progress >= 0.06:
        progress_values.append(progress)
        progress *= 0.78
    if 0.06 not in progress_values:
        progress_values.append(0.06)

    last_reason = "no_bounded_direct_pose_macro"
    for progress in progress_values:
        desired = (
            current[0] + progress * (reference[0] - current[0]),
            current[1] + progress * (reference[1] - current[1]),
        )
        yaw = progress * orientation_error
        pose = robot_pose_for_object_target(current, desired, yaw)
        candidates: list[tuple[str, tuple[DirectPrimitive, ...]]] = []
        if prefer_drive_rel:
            try:
                candidates.append(
                    (
                        "drive_rel_then_turn",
                        decompose_drive_then_turn(
                            pose,
                            maximum_drive_yaw_deg=maximum_drive_yaw_deg,
                            minimum_drive_radius_m=minimum_drive_radius_m,
                            minimum_turn_deg=minimum_turn_deg,
                            minimum_move_m=minimum_move_m,
                        ),
                    )
                )
            except ValueError as error:
                last_reason = str(error)
        candidates.append(
            (
                "turn_move_turn",
                decompose_turn_move_turn(
                    pose,
                    allow_reverse=allow_reverse,
                    reverse_turn_penalty_deg=reverse_turn_penalty_deg,
                    minimum_turn_deg=minimum_turn_deg,
                    minimum_move_m=minimum_move_m,
                ),
            )
        )

        for decomposition, primitives in candidates:
            if not primitives:
                continue
            if not _primitive_bounds_ok(
                primitives,
                maximum_translation_m=max_translation,
                maximum_turn_primitive_deg=max_turn,
            ):
                last_reason = "primitive_bound_exceeded"
                continue
            clearance = minimum_object_range_during_macro(current, primitives)
            if clearance < max(0.0, float(minimum_object_range_m)):
                last_reason = "predicted_object_clearance_too_small"
                continue
            predicted_point, predicted_orientation = apply_macro_to_object(
                current,
                current_orientation,
                primitives,
            )
            return DirectPosePlan(
                False,
                "joint_pose_macro_selected",
                current,
                reference,
                desired,
                current_orientation,
                reference_orientation,
                orientation_error,
                forward_error,
                lateral_error,
                position_error,
                progress,
                exact_goal,
                pose,
                primitives,
                predicted_point,
                predicted_orientation,
                clearance,
                decomposition,
            )

    return DirectPosePlan(
        False,
        last_reason,
        current,
        reference,
        current,
        current_orientation,
        reference_orientation,
        orientation_error,
        forward_error,
        lateral_error,
        position_error,
        0.0,
        exact_goal,
        (0.0, 0.0, 0.0),
        (),
        current,
        current_orientation,
        math.hypot(*current),
        "none",
    )


def simulate_closed_loop(
    current_point: Sequence[float],
    reference_point: Sequence[float],
    current_orientation_deg: float,
    reference_orientation_deg: float,
    *,
    maximum_steps: int = 20,
    move_scale: float = 1.0,
    turn_scale: float = 1.0,
    planner_kwargs: dict | None = None,
) -> tuple[bool, int, tuple[float, float], float]:
    point = _finite_pair(current_point, "current_point")
    orientation = float(current_orientation_deg)
    kwargs = dict(planner_kwargs or {})
    for index in range(max(1, int(maximum_steps))):
        plan = choose_direct_pose_macro(
            point,
            reference_point,
            orientation,
            reference_orientation_deg,
            **kwargs,
        )
        if plan.reached:
            return True, index, point, orientation
        if not plan.primitives:
            return False, index, point, orientation
        point, orientation = apply_macro_to_object(
            point,
            orientation,
            plan.primitives,
            move_scale=move_scale,
            turn_scale=turn_scale,
        )
    final = choose_direct_pose_macro(
        point,
        reference_point,
        orientation,
        reference_orientation_deg,
        **kwargs,
    )
    return final.reached, int(maximum_steps), point, orientation
