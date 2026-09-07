"""Camera-reset, encoder-proportional relative-pose control for MacRobot.

The camera remains the state authority.  Encoder calibration is used only to
execute one bounded relative manoeuvre.  After the whole manoeuvre finishes,
all pre-motion visual samples are discarded and the next cycle starts from a
fresh RGB-D observation.

The controller has two stages:

``viewpoint``
    Keep approximately the range measured when visual approach began, while
    moving to the taught object bearing and taught object orientation.  The
    range condition is intentionally soft in this stage.

``range``
    Move from that viewpoint to the exact camera-relative object point stored
    at teaching time.  Final acceptance is delegated to the existing 4-degree
    orientation and 5-millimetre Cartesian gates in the ROS node.

For speed, a desired local SE(2) displacement is normally decomposed into one
``DRIVE_REL`` constant-curvature motion followed by one final in-place turn.
When the required arc is too tight, too large, or unsafe, the planner falls
back to an exact TURN -> MOVE -> TURN decomposition.  Systematic encoder scale
error is corrected by replanning from the next camera observation.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable, Sequence, Tuple


PATCH_MARKER = "macrobot_camera_reset_pose_relocation_v1"


Vector2 = Tuple[float, float]


def wrap_angle_rad(value: float) -> float:
    return math.atan2(math.sin(float(value)), math.cos(float(value)))


def wrap_angle_deg(value: float) -> float:
    return math.degrees(wrap_angle_rad(math.radians(float(value))))


def signed_axial_error_deg(current_deg: float, reference_deg: float) -> float:
    """Return the shortest signed error for a 180-degree axial direction.

    A positive result means that the robot should rotate counter-clockwise by
    that amount: a left-positive robot rotation subtracts the same amount from
    the object orientation expressed in ``base_link``.
    """

    current = float(current_deg)
    reference = float(reference_deg)
    if not math.isfinite(current) or not math.isfinite(reference):
        raise ValueError("orientation angles must be finite")
    return ((current - reference + 90.0) % 180.0) - 90.0


def _finite_pair(value: Sequence[float], label: str) -> Vector2:
    if len(value) != 2:
        raise ValueError(f"{label} must contain two values")
    result = (float(value[0]), float(value[1]))
    if not all(math.isfinite(item) for item in result):
        raise ValueError(f"{label} must be finite")
    return result


def _rotate(point: Vector2, yaw_deg: float) -> Vector2:
    angle = math.radians(float(yaw_deg))
    cosine = math.cos(angle)
    sine = math.sin(angle)
    return (
        cosine * point[0] - sine * point[1],
        sine * point[0] + cosine * point[1],
    )


def _polar(point: Vector2) -> tuple[float, float]:
    radius = math.hypot(point[0], point[1])
    if radius <= 1e-9:
        raise ValueError("object point is too close to the base origin")
    return radius, math.atan2(point[1], point[0])


@dataclass(frozen=True)
class MotionPrimitive:
    """One encoder-bounded Pico motion.

    ``turn``
        ``amount`` is the left-positive angle in degrees.

    ``move``
        ``amount`` is the signed straight distance in metres.

    ``drive``
        ``amount`` is the signed centre-arc distance in metres and ``yaw_deg``
        is the simultaneous left-positive heading change used by ``DRIVE_REL``.
    """

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
class RelativeRobotPose:
    x_m: float
    y_m: float
    yaw_deg: float


@dataclass(frozen=True)
class RelocationPlan:
    stage: str
    reached: bool
    reason: str
    current_point: Vector2
    desired_point: Vector2
    anchor_range_m: float
    orientation_error_deg: float
    bearing_error_deg: float
    range_error_m: float
    forward_error_m: float
    lateral_error_m: float
    progress: float
    robot_target: RelativeRobotPose
    primitives: tuple[MotionPrimitive, ...]
    predicted_minimum_object_range_m: float
    decomposition: str = "none"

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


def robot_pose_for_object_target(
    current_object_xy: Sequence[float],
    desired_object_xy: Sequence[float],
    robot_yaw_change_deg: float,
) -> RelativeRobotPose:
    """Solve the robot motion that maps one object-relative point to another.

    With robot translation ``t`` and left-positive yaw ``theta``, a fixed
    object's new base-frame coordinate is::

        p_new = R(-theta) (p_current - t)

    Therefore ``t = p_current - R(theta) p_desired``.
    """

    current = _finite_pair(current_object_xy, "current_object_xy")
    desired = _finite_pair(desired_object_xy, "desired_object_xy")
    yaw = float(robot_yaw_change_deg)
    if not math.isfinite(yaw):
        raise ValueError("robot_yaw_change_deg must be finite")
    rotated_desired = _rotate(desired, yaw)
    return RelativeRobotPose(
        current[0] - rotated_desired[0],
        current[1] - rotated_desired[1],
        wrap_angle_deg(yaw),
    )


def object_after_relative_robot_pose(
    current_object_xy: Sequence[float],
    pose: RelativeRobotPose,
) -> Vector2:
    current = _finite_pair(current_object_xy, "current_object_xy")
    translated = (current[0] - pose.x_m, current[1] - pose.y_m)
    return _rotate(translated, -pose.yaw_deg)


def _clean_primitives(
    primitives: Iterable[MotionPrimitive],
    *,
    minimum_turn_deg: float,
    minimum_move_m: float,
) -> tuple[MotionPrimitive, ...]:
    result: list[MotionPrimitive] = []
    for primitive in primitives:
        if primitive.kind == "turn":
            if abs(float(primitive.amount)) < abs(float(minimum_turn_deg)):
                continue
            if result and result[-1].kind == "turn":
                combined = wrap_angle_deg(
                    result[-1].amount + primitive.amount
                )
                if abs(combined) < abs(float(minimum_turn_deg)):
                    result.pop()
                else:
                    result[-1] = MotionPrimitive("turn", combined)
                continue
        else:
            if abs(float(primitive.amount)) < abs(float(minimum_move_m)):
                # A zero-distance drive is just a turn.
                if primitive.kind == "drive" and abs(primitive.yaw_deg) >= abs(
                    float(minimum_turn_deg)
                ):
                    primitive = MotionPrimitive("turn", primitive.yaw_deg)
                else:
                    continue
        result.append(primitive)
    return tuple(result)


def decompose_turn_move_turn(
    pose: RelativeRobotPose,
    *,
    allow_reverse: bool,
    reverse_turn_penalty_deg: float,
    minimum_turn_deg: float,
    minimum_move_m: float,
) -> tuple[MotionPrimitive, ...]:
    """Exact ideal-kinematic decomposition for a differential-drive base."""

    distance = math.hypot(float(pose.x_m), float(pose.y_m))
    if distance < abs(float(minimum_move_m)):
        return _clean_primitives(
            (MotionPrimitive("turn", wrap_angle_deg(pose.yaw_deg)),),
            minimum_turn_deg=minimum_turn_deg,
            minimum_move_m=minimum_move_m,
        )

    heading = math.degrees(math.atan2(pose.y_m, pose.x_m))
    forward = (
        MotionPrimitive("turn", wrap_angle_deg(heading)),
        MotionPrimitive("move", distance),
        MotionPrimitive("turn", wrap_angle_deg(pose.yaw_deg - heading)),
    )
    candidates: list[tuple[float, tuple[MotionPrimitive, ...]]] = [
        (abs(forward[0].amount) + abs(forward[2].amount), forward)
    ]
    if bool(allow_reverse):
        reverse_heading = wrap_angle_deg(heading + 180.0)
        reverse = (
            MotionPrimitive("turn", reverse_heading),
            MotionPrimitive("move", -distance),
            MotionPrimitive(
                "turn",
                wrap_angle_deg(pose.yaw_deg - reverse_heading),
            ),
        )
        candidates.append(
            (
                abs(reverse[0].amount)
                + abs(reverse[2].amount)
                + max(0.0, float(reverse_turn_penalty_deg)),
                reverse,
            )
        )
    _, selected = min(candidates, key=lambda item: item[0])
    return _clean_primitives(
        selected,
        minimum_turn_deg=minimum_turn_deg,
        minimum_move_m=minimum_move_m,
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


def decompose_drive_then_turn(
    pose: RelativeRobotPose,
    *,
    maximum_drive_yaw_deg: float,
    minimum_drive_radius_m: float,
    minimum_turn_deg: float,
    minimum_move_m: float,
) -> tuple[MotionPrimitive, ...]:
    """Decompose an arbitrary local pose into DRIVE_REL plus a final turn.

    The translation chord fixes the arc yaw.  When the target is behind the
    robot, a reverse arc is used.  Purely lateral targets require an almost
    180-degree arc and are rejected here so that the safer TURN-MOVE-TURN
    fallback can handle them.
    """

    x = float(pose.x_m)
    y = float(pose.y_m)
    chord = math.hypot(x, y)
    if chord < abs(float(minimum_move_m)):
        return _clean_primitives(
            (MotionPrimitive("turn", wrap_angle_deg(pose.yaw_deg)),),
            minimum_turn_deg=minimum_turn_deg,
            minimum_move_m=minimum_move_m,
        )

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
    final_turn = wrap_angle_deg(float(pose.yaw_deg) - arc_yaw_deg)
    return _clean_primitives(
        (
            MotionPrimitive("drive", drive_distance, arc_yaw_deg),
            MotionPrimitive("turn", final_turn),
        ),
        minimum_turn_deg=minimum_turn_deg,
        minimum_move_m=minimum_move_m,
    )


def relative_pose_from_primitives(
    primitives: Sequence[MotionPrimitive],
) -> RelativeRobotPose:
    """Compose low-level primitives into one ideal relative robot pose."""

    x = 0.0
    y = 0.0
    yaw = 0.0
    for primitive in primitives:
        if primitive.kind == "turn":
            yaw = wrap_angle_deg(yaw + primitive.amount)
            continue
        if primitive.kind == "move":
            local = (primitive.amount, 0.0)
            delta = _rotate(local, yaw)
            x += delta[0]
            y += delta[1]
            continue
        local = _arc_endpoint(primitive.amount, primitive.yaw_deg)
        delta = _rotate(local, yaw)
        x += delta[0]
        y += delta[1]
        yaw = wrap_angle_deg(yaw + primitive.yaw_deg)
    return RelativeRobotPose(x, y, yaw)


def minimum_object_range_during_primitives(
    current_object_xy: Sequence[float],
    primitives: Sequence[MotionPrimitive],
    *,
    samples_per_motion: int = 31,
) -> float:
    """Approximate minimum robot-to-object distance over a compound path."""

    point = _finite_pair(current_object_xy, "current_object_xy")
    robot_x = 0.0
    robot_y = 0.0
    robot_yaw = 0.0
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
                    local = (
                        radius * math.sin(partial),
                        radius * (1.0 - math.cos(partial)),
                    )
            delta = _rotate(local, robot_yaw)
            sample_x = robot_x + delta[0]
            sample_y = robot_y + delta[1]
            minimum = min(
                minimum,
                math.hypot(point[0] - sample_x, point[1] - sample_y),
            )
        if primitive.kind == "move":
            endpoint_local = (primitive.amount, 0.0)
        else:
            endpoint_local = _arc_endpoint(
                primitive.amount,
                primitive.yaw_deg,
            )
        endpoint_delta = _rotate(endpoint_local, robot_yaw)
        robot_x += endpoint_delta[0]
        robot_y += endpoint_delta[1]
        if primitive.kind == "drive":
            robot_yaw = wrap_angle_deg(robot_yaw + primitive.yaw_deg)
    return minimum


def _interpolated_target(
    current: Vector2,
    target_radius: float,
    target_bearing_rad: float,
    progress: float,
) -> Vector2:
    current_radius, current_bearing = _polar(current)
    bearing_delta = wrap_angle_rad(target_bearing_rad - current_bearing)
    radius = current_radius + progress * (float(target_radius) - current_radius)
    bearing = current_bearing + progress * bearing_delta
    return (radius * math.cos(bearing), radius * math.sin(bearing))


def _primitive_bounds_ok(
    primitives: Sequence[MotionPrimitive],
    *,
    maximum_translation_m: float,
    maximum_turn_primitive_deg: float,
) -> bool:
    for item in primitives:
        if item.kind in {"move", "drive"} and abs(item.amount) > abs(
            float(maximum_translation_m)
        ) + 1e-9:
            return False
        turn = item.amount if item.kind == "turn" else item.yaw_deg
        if item.kind in {"turn", "drive"} and abs(turn) > abs(
            float(maximum_turn_primitive_deg)
        ) + 1e-9:
            return False
    return True


def _plan_bounded_step(
    *,
    current: Vector2,
    target_radius_m: float,
    target_bearing_rad: float,
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
    progress = max(0.02, min(1.0, float(requested_progress)))
    minimum_progress = 0.02
    last_reason = "no_candidate"

    for _ in range(28):
        desired = _interpolated_target(
            current,
            target_radius_m,
            target_bearing_rad,
            progress,
        )
        yaw = progress * float(orientation_error_deg)
        pose = robot_pose_for_object_target(current, desired, yaw)

        candidates: list[tuple[str, tuple[MotionPrimitive, ...]]] = []
        if bool(prefer_drive_rel):
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
                "turn_move_turn_fallback",
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
                maximum_translation_m=maximum_translation_m,
                maximum_turn_primitive_deg=maximum_turn_primitive_deg,
            ):
                last_reason = "primitive_bound_exceeded"
                continue
            clearance = minimum_object_range_during_primitives(
                current,
                primitives,
            )
            if clearance < max(0.0, float(minimum_object_range_m)):
                last_reason = "predicted_object_clearance_too_small"
                continue
            composed = relative_pose_from_primitives(primitives)
            pose_error = math.hypot(
                composed.x_m - pose.x_m,
                composed.y_m - pose.y_m,
            )
            yaw_error = abs(wrap_angle_deg(composed.yaw_deg - pose.yaw_deg))
            if pose_error > 1e-6 or yaw_error > 1e-6:
                last_reason = "primitive_decomposition_not_exact"
                continue
            return (
                progress,
                desired,
                pose,
                primitives,
                clearance,
                decomposition,
            )

        progress *= 0.75
        if progress < minimum_progress:
            break

    raise ValueError(f"could not create bounded relocation step: {last_reason}")


def _plan(
    *,
    stage: str,
    current_object_xy: Sequence[float],
    reference_object_xy: Sequence[float],
    current_orientation_deg: float,
    reference_orientation_deg: float,
    anchor_range_m: float,
    orientation_tolerance_deg: float,
    orbit_bearing_tolerance_deg: float,
    orbit_range_tolerance_m: float,
    forward_tolerance_m: float,
    lateral_tolerance_m: float,
    requested_progress: float,
    maximum_translation_m: float,
    maximum_turn_primitive_deg: float,
    minimum_object_range_m: float,
    allow_reverse: bool,
    reverse_turn_penalty_deg: float,
    minimum_turn_deg: float,
    minimum_move_m: float,
    prefer_drive_rel: bool = True,
    maximum_drive_yaw_deg: float = 80.0,
    minimum_drive_radius_m: float = 0.08,
) -> RelocationPlan:
    current = _finite_pair(current_object_xy, "current_object_xy")
    reference = _finite_pair(reference_object_xy, "reference_object_xy")
    current_range, current_bearing = _polar(current)
    reference_range, reference_bearing = _polar(reference)
    anchor_range = float(anchor_range_m)
    if not math.isfinite(anchor_range) or anchor_range <= 1e-6:
        anchor_range = current_range

    orientation_error = signed_axial_error_deg(
        current_orientation_deg,
        reference_orientation_deg,
    )
    bearing_error = math.degrees(
        wrap_angle_rad(current_bearing - reference_bearing)
    )
    forward_error = current[0] - reference[0]
    lateral_error = current[1] - reference[1]
    range_error = current_range - (
        anchor_range if stage == "viewpoint" else reference_range
    )

    if stage == "viewpoint":
        reached = (
            abs(orientation_error) <= float(orientation_tolerance_deg)
            and abs(bearing_error) <= float(orbit_bearing_tolerance_deg)
            and abs(range_error) <= float(orbit_range_tolerance_m)
        )
        target_radius = anchor_range
        reason = (
            "viewpoint_orientation_and_same_range_reached"
            if reached
            else "relocate_on_same_range_to_taught_view"
        )
    elif stage == "range":
        reached = (
            abs(orientation_error) <= float(orientation_tolerance_deg)
            and abs(forward_error) <= float(forward_tolerance_m)
            and abs(lateral_error) <= float(lateral_tolerance_m)
        )
        target_radius = reference_range
        reason = (
            "camera_relative_grasp_point_reached"
            if reached
            else "relocate_to_exact_taught_camera_point"
        )
    else:
        raise ValueError(f"unsupported relocation stage: {stage}")

    if reached:
        pose = RelativeRobotPose(0.0, 0.0, 0.0)
        return RelocationPlan(
            stage=stage,
            reached=True,
            reason=reason,
            current_point=current,
            desired_point=current,
            anchor_range_m=anchor_range,
            orientation_error_deg=orientation_error,
            bearing_error_deg=bearing_error,
            range_error_m=range_error,
            forward_error_m=forward_error,
            lateral_error_m=lateral_error,
            progress=0.0,
            robot_target=pose,
            primitives=(),
            predicted_minimum_object_range_m=current_range,
            decomposition="none",
        )

    (
        progress,
        desired,
        pose,
        primitives,
        clearance,
        decomposition,
    ) = _plan_bounded_step(
        current=current,
        target_radius_m=target_radius,
        target_bearing_rad=reference_bearing,
        orientation_error_deg=orientation_error,
        requested_progress=requested_progress,
        maximum_translation_m=maximum_translation_m,
        maximum_turn_primitive_deg=maximum_turn_primitive_deg,
        minimum_object_range_m=minimum_object_range_m,
        allow_reverse=allow_reverse,
        reverse_turn_penalty_deg=reverse_turn_penalty_deg,
        minimum_turn_deg=minimum_turn_deg,
        minimum_move_m=minimum_move_m,
        prefer_drive_rel=prefer_drive_rel,
        maximum_drive_yaw_deg=maximum_drive_yaw_deg,
        minimum_drive_radius_m=minimum_drive_radius_m,
    )
    return RelocationPlan(
        stage=stage,
        reached=False,
        reason=reason,
        current_point=current,
        desired_point=desired,
        anchor_range_m=anchor_range,
        orientation_error_deg=orientation_error,
        bearing_error_deg=bearing_error,
        range_error_m=range_error,
        forward_error_m=forward_error,
        lateral_error_m=lateral_error,
        progress=progress,
        robot_target=pose,
        primitives=primitives,
        predicted_minimum_object_range_m=clearance,
        decomposition=decomposition,
    )


def plan_viewpoint_relocation(**kwargs) -> RelocationPlan:
    return _plan(stage="viewpoint", **kwargs)


def plan_range_relocation(**kwargs) -> RelocationPlan:
    return _plan(stage="range", **kwargs)


def apply_ideal_primitive_to_object(
    point_xy: Sequence[float],
    orientation_deg: float,
    primitive: MotionPrimitive,
    *,
    turn_scale: float = 1.0,
    move_scale: float = 1.0,
) -> tuple[Vector2, float]:
    """Pure test/simulation helper for one low-level primitive."""

    point = _finite_pair(point_xy, "point_xy")
    orientation = float(orientation_deg)
    if primitive.kind == "turn":
        actual = float(primitive.amount) * float(turn_scale)
        return _rotate(point, -actual), (orientation - actual) % 180.0
    if primitive.kind == "move":
        actual = float(primitive.amount) * float(move_scale)
        return (point[0] - actual, point[1]), orientation % 180.0

    actual_distance = float(primitive.amount) * float(move_scale)
    actual_yaw = float(primitive.yaw_deg) * float(turn_scale)
    translation = _arc_endpoint(actual_distance, actual_yaw)
    pose = RelativeRobotPose(translation[0], translation[1], actual_yaw)
    return (
        object_after_relative_robot_pose(point, pose),
        (orientation - actual_yaw) % 180.0,
    )
