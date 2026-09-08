"""Joint camera-relative lattice controller for MacRobot.

The taught object point and taught axial orientation form one camera-relative
SE(2) target.  A candidate robot motion is evaluated with the rigid-body model

    p_next = R(-yaw) (p_now - translation)
    axis_error_next = wrap_axial(axis_error_now - yaw)

so position and direction are never corrected by independent, competing loops.
The planner runs a bounded weighted-A* search on short TURN_DEG, MOVE_CM and
optional DRIVE_REL primitives.  The ROS node executes only the first primitive,
discards pre-motion frames, and replans from a fresh RGB-D observation.

This module intentionally has no ROS imports so geometry, safety bounds, cycle
rejection and closed-loop convergence can be unit-tested on a development PC.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import heapq
import itertools
import math
import time
from typing import Iterable, Mapping, Optional, Sequence

PATCH_MARKER = "macrobot_joint_pose_lattice_v2"


# ---------------------------------------------------------------------------
# Angle and planar geometry helpers
# ---------------------------------------------------------------------------


def wrap_angle_deg(value: float) -> float:
    """Wrap a directional angle to ``[-180, 180)`` degrees."""

    result = (float(value) + 180.0) % 360.0 - 180.0
    return 0.0 if abs(result) < 1e-12 else result


def wrap_axial_deg(value: float) -> float:
    """Wrap a 180-degree axis error to ``[-90, 90)`` degrees."""

    result = (float(value) + 90.0) % 180.0 - 90.0
    return 0.0 if abs(result) < 1e-12 else result


def _rotate(point: tuple[float, float], yaw_deg: float) -> tuple[float, float]:
    angle = math.radians(float(yaw_deg))
    cosine = math.cos(angle)
    sine = math.sin(angle)
    return (
        cosine * point[0] - sine * point[1],
        sine * point[0] + cosine * point[1],
    )


def _arc_endpoint(distance_m: float, yaw_deg: float) -> tuple[float, float]:
    """Return a centre-arc endpoint expressed in the starting robot frame."""

    theta = math.radians(float(yaw_deg))
    distance = float(distance_m)
    if abs(theta) <= 1e-10:
        return distance, 0.0
    return (
        distance * math.sin(theta) / theta,
        distance * (1.0 - math.cos(theta)) / theta,
    )


def _finite(value: float, label: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{label} must be finite")
    return result


def _positive(value: float, label: str) -> float:
    result = _finite(value, label)
    if result <= 0.0:
        raise ValueError(f"{label} must be positive")
    return result


def _nonnegative(value: float, label: str) -> float:
    result = _finite(value, label)
    if result < 0.0:
        raise ValueError(f"{label} must be non-negative")
    return result


# ---------------------------------------------------------------------------
# Public data types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ObjectPoseState:
    """Observed object pose in physical ``base_link`` planar axes.

    ``orientation_error_deg`` is current minus taught axial orientation.  A
    positive value means a left-positive robot yaw is required to restore the
    taught axis.  It is always represented modulo 180 degrees.
    """

    forward_m: float
    lateral_m: float
    orientation_error_deg: float
    orientation_quality: float = 1.0
    orientation_reliable: bool = True

    def __post_init__(self) -> None:
        forward = _finite(self.forward_m, "forward_m")
        lateral = _finite(self.lateral_m, "lateral_m")
        orientation = wrap_axial_deg(
            _finite(self.orientation_error_deg, "orientation_error_deg")
        )
        quality = max(
            0.0,
            min(1.0, _finite(self.orientation_quality, "orientation_quality")),
        )
        object.__setattr__(self, "forward_m", forward)
        object.__setattr__(self, "lateral_m", lateral)
        object.__setattr__(self, "orientation_error_deg", orientation)
        object.__setattr__(self, "orientation_quality", quality)
        object.__setattr__(self, "orientation_reliable", bool(self.orientation_reliable))

    @property
    def planar_range_m(self) -> float:
        return math.hypot(self.forward_m, self.lateral_m)

    @property
    def bearing_deg(self) -> float:
        return math.degrees(math.atan2(self.lateral_m, self.forward_m))

    def to_mapping(self) -> dict[str, object]:
        return {
            "forward_m": self.forward_m,
            "lateral_m": self.lateral_m,
            "orientation_error_deg": self.orientation_error_deg,
            "orientation_quality": self.orientation_quality,
            "orientation_reliable": self.orientation_reliable,
            "range_m": self.planar_range_m,
            "bearing_deg": self.bearing_deg,
        }


@dataclass(frozen=True)
class ObjectPoseTarget:
    """Taught camera-relative object point; taught orientation error is zero."""

    forward_m: float
    lateral_m: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "forward_m", _finite(self.forward_m, "forward_m"))
        object.__setattr__(self, "lateral_m", _finite(self.lateral_m, "lateral_m"))

    @property
    def planar_range_m(self) -> float:
        return math.hypot(self.forward_m, self.lateral_m)

    @property
    def bearing_deg(self) -> float:
        return math.degrees(math.atan2(self.lateral_m, self.forward_m))

    def to_mapping(self) -> dict[str, float]:
        return {
            "forward_m": self.forward_m,
            "lateral_m": self.lateral_m,
            "range_m": self.planar_range_m,
            "bearing_deg": self.bearing_deg,
        }


@dataclass(frozen=True)
class RobotRelativeGoal:
    """Exact current-frame robot displacement that recreates the taught view."""

    x_m: float
    y_m: float
    yaw_deg: float

    def to_mapping(self) -> dict[str, float]:
        return {"x_m": self.x_m, "y_m": self.y_m, "yaw_deg": self.yaw_deg}


@dataclass(frozen=True)
class Primitive:
    """One low-level local motion.

    * ``turn``: ``amount`` is left-positive degrees.
    * ``move``: ``amount`` is forward-positive metres.
    * ``drive``: ``amount`` is signed centre-arc metres and ``yaw_deg`` is the
      simultaneous left-positive heading change.
    """

    kind: str
    amount: float
    yaw_deg: float = 0.0

    def __post_init__(self) -> None:
        if self.kind not in {"turn", "move", "drive"}:
            raise ValueError(f"unsupported primitive kind: {self.kind}")
        amount = _finite(self.amount, "primitive amount")
        yaw = _finite(self.yaw_deg, "primitive yaw")
        if self.kind != "drive" and abs(yaw) > 1e-12:
            raise ValueError("only drive primitives may specify yaw_deg")
        if self.kind == "drive" and abs(yaw) <= 1e-12:
            raise ValueError("drive primitive must specify non-zero yaw_deg")
        object.__setattr__(self, "amount", amount)
        object.__setattr__(self, "yaw_deg", yaw)

    @property
    def effective_turn_deg(self) -> float:
        if self.kind == "turn":
            return self.amount
        if self.kind == "drive":
            return self.yaw_deg
        return 0.0

    @property
    def effective_move_m(self) -> float:
        return self.amount if self.kind in {"move", "drive"} else 0.0

    @property
    def sign(self) -> int:
        value = self.effective_turn_deg
        if abs(value) <= 1e-12:
            value = self.effective_move_m
        return 1 if value > 0.0 else -1 if value < 0.0 else 0

    def signature(self) -> tuple[str, int]:
        return self.kind, self.sign

    def to_mapping(self) -> dict[str, float | str]:
        return {
            "kind": self.kind,
            "amount": self.amount,
            "yaw_deg": self.yaw_deg,
        }


@dataclass(frozen=True)
class JointPoseConfig:
    """Bounded lattice and safety settings.

    Defaults are intentionally conservative for a Raspberry Pi 4.  Reverse is
    represented by the planner but is disabled here; the ROS node enables it
    only when both the user option and explicit rear-clearance acknowledgement
    are true.
    """

    forward_tolerance_m: float = 0.005
    lateral_tolerance_m: float = 0.005
    bearing_tolerance_deg: float = 1.0
    orientation_tolerance_deg: float = 4.0
    minimum_orientation_quality: float = 0.45

    maximum_move_step_m: float = 0.018
    maximum_reverse_step_m: float = 0.012
    maximum_turn_step_deg: float = 8.0
    maximum_drive_yaw_deg: float = 6.0
    minimum_move_step_m: float = 0.003
    minimum_turn_step_deg: float = 0.5
    turn_action_levels: int = 3
    move_action_levels: int = 3

    minimum_object_range_m: float = 0.10
    maximum_object_range_m: float = 0.80
    minimum_object_forward_m: float = 0.04
    maximum_predicted_bearing_deg: float = 48.0
    path_sample_count: int = 9

    allow_reverse: bool = False
    drive_enabled: bool = False
    position_only_when_orientation_unreliable: bool = True

    position_resolution_m: float = 0.004
    orientation_resolution_deg: float = 2.0
    search_maximum_expansions: int = 25000
    # Hard callback-time cap. Typical solvable routes finish in tens of
    # expansions; infeasible states must not monopolize the ROS executor.
    search_maximum_wall_time_sec: float = 0.15
    search_maximum_depth: int = 72
    search_maximum_translation_m: float = 0.40
    search_maximum_turn_deg: float = 220.0
    heuristic_weight: float = 3.5
    execution_prefix_length: int = 1

    action_cost: float = 1.0
    motion_cost_weight: float = 0.08
    reverse_cost_penalty: float = 0.20
    drive_cost_penalty: float = 0.08
    action_family_change_penalty: float = 0.04
    immediate_reversal_penalty: float = 1.80
    same_direction_bonus: float = 0.08
    recent_cycle_penalty: float = 4.0
    hard_reject_recent_cycle: bool = True
    cycle_position_radius_m: float = 0.010
    cycle_orientation_radius_deg: float = 5.0
    cycle_required_cost_improvement: float = 0.20

    minimum_frontier_improvement: float = 0.08
    top_candidate_count: int = 6

    def validate(self) -> None:
        for name in (
            "forward_tolerance_m",
            "lateral_tolerance_m",
            "bearing_tolerance_deg",
            "orientation_tolerance_deg",
            "maximum_move_step_m",
            "maximum_reverse_step_m",
            "maximum_turn_step_deg",
            "maximum_drive_yaw_deg",
            "minimum_move_step_m",
            "minimum_turn_step_deg",
            "minimum_object_range_m",
            "maximum_object_range_m",
            "minimum_object_forward_m",
            "maximum_predicted_bearing_deg",
            "position_resolution_m",
            "orientation_resolution_deg",
            "search_maximum_wall_time_sec",
            "search_maximum_translation_m",
            "search_maximum_turn_deg",
            "heuristic_weight",
            "action_cost",
            "minimum_frontier_improvement",
            "cycle_position_radius_m",
            "cycle_orientation_radius_deg",
        ):
            _positive(getattr(self, name), name)
        for name in (
            "motion_cost_weight",
            "reverse_cost_penalty",
            "drive_cost_penalty",
            "action_family_change_penalty",
            "immediate_reversal_penalty",
            "same_direction_bonus",
            "recent_cycle_penalty",
            "cycle_required_cost_improvement",
        ):
            _nonnegative(getattr(self, name), name)
        if not 0.0 <= float(self.minimum_orientation_quality) <= 1.0:
            raise ValueError("minimum_orientation_quality must be within [0, 1]")
        if self.maximum_object_range_m <= self.minimum_object_range_m:
            raise ValueError("maximum_object_range_m must exceed minimum_object_range_m")
        if self.minimum_move_step_m > self.maximum_move_step_m:
            raise ValueError("minimum_move_step_m exceeds maximum_move_step_m")
        if self.minimum_turn_step_deg > self.maximum_turn_step_deg:
            raise ValueError("minimum_turn_step_deg exceeds maximum_turn_step_deg")
        if int(self.turn_action_levels) < 1 or int(self.turn_action_levels) > 5:
            raise ValueError("turn_action_levels must be within [1, 5]")
        if int(self.move_action_levels) < 1 or int(self.move_action_levels) > 5:
            raise ValueError("move_action_levels must be within [1, 5]")
        if int(self.path_sample_count) < 2 or int(self.path_sample_count) > 101:
            raise ValueError("path_sample_count must be within [2, 101]")
        if int(self.search_maximum_expansions) < 1:
            raise ValueError("search_maximum_expansions must be positive")
        if int(self.search_maximum_depth) < 1:
            raise ValueError("search_maximum_depth must be positive")
        # Camera-authoritative control is safe only when every physical
        # primitive is followed by a fresh RGB-D reset.  Keep this field in the
        # dataclass for log/config compatibility, but reject values that would
        # execute an open-loop prefix.
        if int(self.execution_prefix_length) != 1:
            raise ValueError(
                "execution_prefix_length must be exactly 1 for camera-reset control"
            )
        if int(self.top_candidate_count) < 0:
            raise ValueError("top_candidate_count must be non-negative")


@dataclass(frozen=True)
class CandidateScore:
    primitive: Primitive
    predicted_state: ObjectPoseState
    estimated_total_cost: float
    goal_error: float
    admissible: bool
    rejection_reason: str = ""

    def to_mapping(self) -> dict[str, object]:
        return {
            "primitive": self.primitive.to_mapping(),
            "predicted_state": self.predicted_state.to_mapping(),
            "estimated_total_cost": self.estimated_total_cost,
            "goal_error": self.goal_error,
            "admissible": self.admissible,
            "rejection_reason": self.rejection_reason,
        }


@dataclass(frozen=True)
class JointPoseDecision:
    aligned: bool
    hold: bool
    reason: str
    sequence: tuple[Primitive, ...]
    route_preview: tuple[Primitive, ...]
    current_state: ObjectPoseState
    predicted_state: ObjectPoseState
    planned_terminal_state: ObjectPoseState
    robot_goal: RobotRelativeGoal
    current_cost: float
    planned_terminal_cost: float
    expected_improvement: float
    predicted_minimum_range_m: float
    predicted_maximum_bearing_deg: float
    search_expansions: int
    search_reached_goal: bool
    orientation_effective: bool
    orientation_required: bool
    top_candidates: tuple[CandidateScore, ...] = field(default_factory=tuple)

    def to_mapping(self) -> dict[str, object]:
        return {
            "aligned": self.aligned,
            "hold": self.hold,
            "reason": self.reason,
            "sequence": [item.to_mapping() for item in self.sequence],
            "route_preview": [item.to_mapping() for item in self.route_preview],
            "current_state": self.current_state.to_mapping(),
            "predicted_state": self.predicted_state.to_mapping(),
            "planned_terminal_state": self.planned_terminal_state.to_mapping(),
            "robot_goal": self.robot_goal.to_mapping(),
            "current_cost": self.current_cost,
            "planned_terminal_cost": self.planned_terminal_cost,
            "expected_improvement": self.expected_improvement,
            "predicted_minimum_range_m": self.predicted_minimum_range_m,
            "predicted_maximum_bearing_deg": self.predicted_maximum_bearing_deg,
            "search_expansions": self.search_expansions,
            "search_reached_goal": self.search_reached_goal,
            "orientation_effective": self.orientation_effective,
            "orientation_required": self.orientation_required,
            "top_candidates": [item.to_mapping() for item in self.top_candidates],
        }


# ---------------------------------------------------------------------------
# Exact target geometry and state propagation
# ---------------------------------------------------------------------------


def bearing_error_deg(state: ObjectPoseState, target: ObjectPoseTarget) -> float:
    return wrap_angle_deg(state.bearing_deg - target.bearing_deg)


def robot_goal_for_taught_object_pose(
    state: ObjectPoseState,
    target: ObjectPoseTarget,
    *,
    orientation_required: bool,
) -> RobotRelativeGoal:
    """Solve the robot displacement that maps ``state`` to ``target`` exactly.

    For a robot translation ``t`` and left-positive yaw ``theta``::

        p_target = R(-theta) (p_current - t)

    therefore ``t = p_current - R(theta) p_target``.  When an orientation is
    required, ``theta`` is the measured current-minus-taught axial error.
    Without a reliable orientation, yaw is set to zero and only the taught
    object point is used.
    """

    yaw = state.orientation_error_deg if orientation_required else 0.0
    rotated_target = _rotate((target.forward_m, target.lateral_m), yaw)
    return RobotRelativeGoal(
        state.forward_m - rotated_target[0],
        state.lateral_m - rotated_target[1],
        wrap_angle_deg(yaw),
    )


def _primitive_robot_pose(primitive: Primitive, fraction: float = 1.0) -> RobotRelativeGoal:
    u = max(0.0, min(1.0, float(fraction)))
    if primitive.kind == "turn":
        return RobotRelativeGoal(0.0, 0.0, primitive.amount * u)
    if primitive.kind == "move":
        return RobotRelativeGoal(primitive.amount * u, 0.0, 0.0)
    distance = primitive.amount * u
    yaw = primitive.yaw_deg * u
    endpoint = _arc_endpoint(distance, yaw)
    return RobotRelativeGoal(endpoint[0], endpoint[1], yaw)


def apply_primitive(
    state: ObjectPoseState,
    primitive: Primitive,
    *,
    fraction: float = 1.0,
) -> ObjectPoseState:
    """Predict a fixed object's next base-frame pose under one robot motion."""

    robot_pose = _primitive_robot_pose(primitive, fraction)
    translated = (
        state.forward_m - robot_pose.x_m,
        state.lateral_m - robot_pose.y_m,
    )
    next_xy = _rotate(translated, -robot_pose.yaw_deg)
    return ObjectPoseState(
        next_xy[0],
        next_xy[1],
        wrap_axial_deg(state.orientation_error_deg - robot_pose.yaw_deg),
        state.orientation_quality,
        state.orientation_reliable,
    )


def apply_sequence(
    state: ObjectPoseState,
    sequence: Iterable[Primitive],
) -> ObjectPoseState:
    result = state
    for primitive in sequence:
        result = apply_primitive(result, primitive)
    return result


def sampled_states_during_primitive(
    state: ObjectPoseState,
    primitive: Primitive,
    sample_count: int,
) -> tuple[ObjectPoseState, ...]:
    count = max(2, int(sample_count))
    return tuple(
        apply_primitive(state, primitive, fraction=index / float(count))
        for index in range(1, count + 1)
    )


def route_envelope(
    state: ObjectPoseState,
    sequence: Sequence[Primitive],
    *,
    sample_count: int = 9,
) -> tuple[float, float]:
    """Return minimum object range and maximum absolute bearing along a route."""

    minimum_range = state.planar_range_m
    maximum_bearing = abs(state.bearing_deg)
    current = state
    for primitive in sequence:
        samples = (
            sampled_states_during_primitive(current, primitive, sample_count)
            if primitive.kind == "drive"
            else (apply_primitive(current, primitive),)
        )
        for sample in samples:
            minimum_range = min(minimum_range, sample.planar_range_m)
            maximum_bearing = max(maximum_bearing, abs(sample.bearing_deg))
        current = samples[-1]
    return minimum_range, maximum_bearing


# ---------------------------------------------------------------------------
# Goal, admissibility and search costs
# ---------------------------------------------------------------------------


def orientation_is_effective(
    state: ObjectPoseState,
    config: JointPoseConfig,
    *,
    orientation_required: bool,
) -> bool:
    return bool(
        orientation_required
        and state.orientation_reliable
        and state.orientation_quality >= config.minimum_orientation_quality
    )


def is_aligned(
    state: ObjectPoseState,
    target: ObjectPoseTarget,
    config: JointPoseConfig,
    *,
    orientation_required: bool,
) -> bool:
    if abs(state.forward_m - target.forward_m) > config.forward_tolerance_m:
        return False
    if abs(state.lateral_m - target.lateral_m) > config.lateral_tolerance_m:
        return False
    if abs(bearing_error_deg(state, target)) > config.bearing_tolerance_deg:
        return False
    if orientation_required:
        if not orientation_is_effective(
            state, config, orientation_required=orientation_required
        ):
            return False
        if abs(state.orientation_error_deg) > config.orientation_tolerance_deg:
            return False
    return True


def goal_error(
    state: ObjectPoseState,
    target: ObjectPoseTarget,
    config: JointPoseConfig,
    *,
    orientation_required: bool,
) -> float:
    """Dimensionless diagnostic error; it is not required to decrease per step."""

    forward = abs(state.forward_m - target.forward_m) / config.forward_tolerance_m
    lateral = abs(state.lateral_m - target.lateral_m) / config.lateral_tolerance_m
    bearing = abs(bearing_error_deg(state, target)) / config.bearing_tolerance_deg
    orientation = (
        abs(state.orientation_error_deg) / config.orientation_tolerance_deg
        if orientation_required
        else 0.0
    )
    # Cartesian position is primary; bearing is retained as the final visual gate
    # rather than becoming another independent high-gain controller.
    return math.hypot(forward, lateral) + 0.20 * bearing + orientation


# Compatibility alias retained for early patch tests and downstream notebooks.
pose_cost = goal_error


def _state_admissibility(
    state: ObjectPoseState,
    config: JointPoseConfig,
) -> tuple[bool, str]:
    if state.forward_m < config.minimum_object_forward_m:
        return False, "object_left_front_half_plane"
    if state.planar_range_m < config.minimum_object_range_m:
        return False, "predicted_object_range_too_small"
    if state.planar_range_m > config.maximum_object_range_m:
        return False, "predicted_object_range_too_large"
    if abs(state.bearing_deg) > config.maximum_predicted_bearing_deg:
        return False, "predicted_object_outside_bearing_envelope"
    return True, ""


def primitive_admissibility(
    state: ObjectPoseState,
    primitive: Primitive,
    config: JointPoseConfig,
) -> tuple[bool, str, ObjectPoseState, float, float]:
    minimum_range = state.planar_range_m
    maximum_bearing = abs(state.bearing_deg)
    predicted = state
    # For an in-place turn, range is constant and bearing changes monotonically.
    # For a straight move while the front-half-plane constraint is enforced,
    # range and absolute bearing attain their safety extrema at an endpoint.
    # Only a curved DRIVE_REL therefore needs interior samples.  This keeps the
    # default TURN/MOVE lattice fast enough for camera-rate replanning on Pi 4.
    samples = (
        sampled_states_during_primitive(
            state, primitive, config.path_sample_count
        )
        if primitive.kind == "drive"
        else (apply_primitive(state, primitive),)
    )
    for predicted in samples:
        minimum_range = min(minimum_range, predicted.planar_range_m)
        maximum_bearing = max(maximum_bearing, abs(predicted.bearing_deg))
        valid, reason = _state_admissibility(predicted, config)
        if not valid:
            return False, reason, predicted, minimum_range, maximum_bearing
    return True, "", predicted, minimum_range, maximum_bearing


def states_near(
    left: ObjectPoseState,
    right: ObjectPoseState,
    config: JointPoseConfig,
    *,
    orientation_required: bool,
) -> bool:
    if math.hypot(
        left.forward_m - right.forward_m,
        left.lateral_m - right.lateral_m,
    ) > config.cycle_position_radius_m:
        return False
    if orientation_required and abs(
        wrap_axial_deg(left.orientation_error_deg - right.orientation_error_deg)
    ) > config.cycle_orientation_radius_deg:
        return False
    return True


def _geometric_levels(maximum: float, minimum: float, levels: int) -> tuple[float, ...]:
    values: list[float] = []
    current = abs(float(maximum))
    floor = abs(float(minimum))
    for _ in range(max(1, int(levels))):
        if current + 1e-12 >= floor:
            values.append(max(floor, current))
        current *= 0.5
    if not values:
        values.append(floor)
    # A final exact minimum is useful near the gate, but avoid nearly duplicate
    # branches when geometric halving already produced it.
    if all(abs(value - floor) > max(1e-9, 0.10 * floor) for value in values):
        values.append(floor)
    return tuple(sorted({round(value, 12) for value in values}, reverse=True))


def _deduplicate_primitives(primitives: Iterable[Primitive]) -> tuple[Primitive, ...]:
    result: list[Primitive] = []
    seen: set[tuple[str, int, int]] = set()
    for primitive in primitives:
        key = (
            primitive.kind,
            int(round(primitive.amount * 1_000_000.0)),
            int(round(primitive.yaw_deg * 1_000_000.0)),
        )
        if key in seen:
            continue
        seen.add(key)
        result.append(primitive)
    return tuple(result)


def candidate_primitives(
    state: ObjectPoseState,
    target: ObjectPoseTarget,
    config: JointPoseConfig,
    *,
    orientation_required: bool,
    step_scale: float = 1.0,
) -> tuple[Primitive, ...]:
    """Build a small multi-resolution action lattice around one state."""

    scale = max(0.25, min(1.0, float(step_scale)))
    max_turn = max(
        config.minimum_turn_step_deg,
        config.maximum_turn_step_deg * scale,
    )
    max_move = max(
        config.minimum_move_step_m,
        config.maximum_move_step_m * scale,
    )
    max_reverse = max(
        config.minimum_move_step_m,
        config.maximum_reverse_step_m * scale,
    )

    turns: list[float] = list(
        _geometric_levels(max_turn, config.minimum_turn_step_deg, config.turn_action_levels)
    )
    dynamic_turns = [bearing_error_deg(state, target)]
    if orientation_required:
        dynamic_turns.append(state.orientation_error_deg)
    for requested in dynamic_turns:
        magnitude = min(max_turn, abs(requested))
        if magnitude >= config.minimum_turn_step_deg:
            turns.append(magnitude)

    moves: list[float] = list(
        _geometric_levels(max_move, config.minimum_move_step_m, config.move_action_levels)
    )
    direct_forward = abs(state.forward_m - target.forward_m)
    if direct_forward >= config.minimum_move_step_m:
        moves.append(min(max_move, direct_forward))

    primitives: list[Primitive] = []
    for magnitude in turns:
        bounded = min(max_turn, abs(magnitude))
        if bounded >= config.minimum_turn_step_deg:
            primitives.append(Primitive("turn", bounded))
            primitives.append(Primitive("turn", -bounded))
    for magnitude in moves:
        bounded = min(max_move, abs(magnitude))
        if bounded >= config.minimum_move_step_m:
            primitives.append(Primitive("move", bounded))
    if config.allow_reverse:
        reverse_levels = list(
            _geometric_levels(
                max_reverse,
                config.minimum_move_step_m,
                config.move_action_levels,
            )
        )
        if direct_forward >= config.minimum_move_step_m:
            reverse_levels.append(min(max_reverse, direct_forward))
        for magnitude in reverse_levels:
            bounded = min(max_reverse, abs(magnitude))
            if bounded >= config.minimum_move_step_m:
                primitives.append(Primitive("move", -bounded))

    if config.drive_enabled:
        drive_turn = min(config.maximum_drive_yaw_deg * scale, max_turn)
        if drive_turn >= config.minimum_turn_step_deg:
            drive_distances = (max_move, max(config.minimum_move_step_m, 0.5 * max_move))
            for distance in drive_distances:
                primitives.append(Primitive("drive", distance, drive_turn))
                primitives.append(Primitive("drive", distance, -drive_turn))
            if config.allow_reverse:
                reverse_distance = -max_reverse
                primitives.append(Primitive("drive", reverse_distance, drive_turn))
                primitives.append(Primitive("drive", reverse_distance, -drive_turn))

    return _deduplicate_primitives(primitives)


def _is_immediate_reversal(previous: Optional[Primitive], current: Primitive) -> bool:
    if previous is None:
        return False
    if previous.kind != current.kind:
        return False
    if current.kind == "turn":
        return previous.amount * current.amount < 0.0
    if current.kind == "move":
        return previous.amount * current.amount < 0.0
    return (
        previous.amount * current.amount < 0.0
        or previous.yaw_deg * current.yaw_deg < 0.0
    )


def _edge_cost(
    primitive: Primitive,
    previous: Optional[Primitive],
    config: JointPoseConfig,
) -> float:
    cost = config.action_cost
    turn_fraction = abs(primitive.effective_turn_deg) / max(
        config.maximum_turn_step_deg, 1e-9
    )
    move_limit = (
        config.maximum_reverse_step_m
        if primitive.effective_move_m < 0.0
        else config.maximum_move_step_m
    )
    move_fraction = abs(primitive.effective_move_m) / max(move_limit, 1e-9)
    cost += config.motion_cost_weight * (turn_fraction + move_fraction)
    if primitive.effective_move_m < 0.0:
        cost += config.reverse_cost_penalty
    if primitive.kind == "drive":
        cost += config.drive_cost_penalty
    if previous is not None:
        if previous.kind != primitive.kind:
            cost += config.action_family_change_penalty
        if _is_immediate_reversal(previous, primitive):
            cost += config.immediate_reversal_penalty
        elif previous.signature() == primitive.signature():
            cost = max(0.0, cost - config.same_direction_bonus)
    return cost


def _turn_move_turn_estimate(
    goal: RobotRelativeGoal,
    config: JointPoseConfig,
) -> float:
    distance = math.hypot(goal.x_m, goal.y_m)
    max_turn = max(config.maximum_turn_step_deg, config.minimum_turn_step_deg)
    max_move = max(config.maximum_move_step_m, config.minimum_move_step_m)
    if distance <= config.forward_tolerance_m:
        return abs(wrap_angle_deg(goal.yaw_deg)) / max_turn

    forward_heading = math.degrees(math.atan2(goal.y_m, goal.x_m))
    forward = (
        abs(wrap_angle_deg(forward_heading)) / max_turn
        + distance / max_move
        + abs(wrap_angle_deg(goal.yaw_deg - forward_heading)) / max_turn
    )
    if not config.allow_reverse:
        return forward

    reverse_heading = wrap_angle_deg(forward_heading + 180.0)
    max_reverse = max(config.maximum_reverse_step_m, config.minimum_move_step_m)
    reverse = (
        abs(reverse_heading) / max_turn
        + distance / max_reverse
        + abs(wrap_angle_deg(goal.yaw_deg - reverse_heading)) / max_turn
        + config.reverse_cost_penalty
    )
    return min(forward, reverse)


def _heuristic(
    state: ObjectPoseState,
    target: ObjectPoseTarget,
    config: JointPoseConfig,
    *,
    orientation_required: bool,
) -> float:
    goal = robot_goal_for_taught_object_pose(
        state, target, orientation_required=orientation_required
    )
    estimate = _turn_move_turn_estimate(goal, config)
    # A small residual term resolves ties without turning the search back into
    # the old myopic bearing/orientation priority loop.
    return estimate + 0.03 * goal_error(
        state, target, config, orientation_required=orientation_required
    )


def _quantized_key(
    state: ObjectPoseState,
    previous: Optional[Primitive],
    config: JointPoseConfig,
    *,
    orientation_required: bool,
) -> tuple[int, int, int, str, int]:
    orientation_bin = (
        int(round(state.orientation_error_deg / config.orientation_resolution_deg))
        if orientation_required
        else 0
    )
    kind = "none" if previous is None else previous.kind
    sign = 0 if previous is None else previous.sign
    return (
        int(round(state.forward_m / config.position_resolution_m)),
        int(round(state.lateral_m / config.position_resolution_m)),
        orientation_bin,
        kind,
        sign,
    )


def _recent_cycle_cost(
    predicted: ObjectPoseState,
    target: ObjectPoseTarget,
    recent_states: Sequence[ObjectPoseState],
    config: JointPoseConfig,
    *,
    orientation_required: bool,
    current_cost: float,
) -> tuple[float, bool]:
    for recent in recent_states:
        if not states_near(
            predicted,
            recent,
            config,
            orientation_required=orientation_required,
        ):
            continue
        predicted_cost = goal_error(
            predicted,
            target,
            config,
            orientation_required=orientation_required,
        )
        improvement = current_cost - predicted_cost
        if improvement < config.cycle_required_cost_improvement:
            return config.recent_cycle_penalty, bool(config.hard_reject_recent_cycle)
    return 0.0, False


@dataclass
class _SearchNode:
    state: ObjectPoseState
    g_cost: float
    depth: int
    parent_index: Optional[int]
    primitive: Optional[Primitive]
    previous_primitive: Optional[Primitive]
    translation_total_m: float
    turn_total_deg: float
    minimum_range_m: float
    maximum_bearing_deg: float


def _reconstruct(nodes: Sequence[_SearchNode], index: int) -> tuple[Primitive, ...]:
    reversed_route: list[Primitive] = []
    current: Optional[int] = index
    while current is not None:
        node = nodes[current]
        if node.primitive is not None:
            reversed_route.append(node.primitive)
        current = node.parent_index
    reversed_route.reverse()
    return tuple(reversed_route)


def _first_action_candidates(
    state: ObjectPoseState,
    target: ObjectPoseTarget,
    config: JointPoseConfig,
    *,
    orientation_required: bool,
    previous_primitive: Optional[Primitive],
    recent_states: Sequence[ObjectPoseState],
    step_scale: float,
) -> tuple[CandidateScore, ...]:
    current_cost = goal_error(
        state, target, config, orientation_required=orientation_required
    )
    candidates: list[CandidateScore] = []
    for primitive in candidate_primitives(
        state,
        target,
        config,
        orientation_required=orientation_required,
        step_scale=step_scale,
    ):
        valid, reason, predicted, _, _ = primitive_admissibility(
            state, primitive, config
        )
        cycle_penalty = 0.0
        hard_cycle = False
        if valid:
            cycle_penalty, hard_cycle = _recent_cycle_cost(
                predicted,
                target,
                recent_states,
                config,
                orientation_required=orientation_required,
                current_cost=current_cost,
            )
            if hard_cycle:
                valid = False
                reason = "recent_measured_cycle_hard_reject"
        estimated = (
            _edge_cost(primitive, previous_primitive, config)
            + cycle_penalty
            + config.heuristic_weight
            * _heuristic(
                predicted,
                target,
                config,
                orientation_required=orientation_required,
            )
        )
        candidates.append(
            CandidateScore(
                primitive=primitive,
                predicted_state=predicted,
                estimated_total_cost=estimated,
                goal_error=goal_error(
                    predicted,
                    target,
                    config,
                    orientation_required=orientation_required,
                ),
                admissible=valid,
                rejection_reason=reason,
            )
        )
    candidates.sort(
        key=lambda item: (
            not item.admissible,
            item.estimated_total_cost,
            item.goal_error,
            item.primitive.kind,
            item.primitive.amount,
            item.primitive.yaw_deg,
        )
    )
    return tuple(candidates[: config.top_candidate_count])


def _hold_decision(
    *,
    state: ObjectPoseState,
    target: ObjectPoseTarget,
    config: JointPoseConfig,
    reason: str,
    orientation_required: bool,
    orientation_effective: bool,
    expansions: int = 0,
    top_candidates: Sequence[CandidateScore] = (),
) -> JointPoseDecision:
    cost = goal_error(
        state,
        target,
        config,
        orientation_required=orientation_effective,
    )
    goal = robot_goal_for_taught_object_pose(
        state,
        target,
        orientation_required=orientation_effective,
    )
    return JointPoseDecision(
        aligned=False,
        hold=True,
        reason=reason,
        sequence=(),
        route_preview=(),
        current_state=state,
        predicted_state=state,
        planned_terminal_state=state,
        robot_goal=goal,
        current_cost=cost,
        planned_terminal_cost=cost,
        expected_improvement=0.0,
        predicted_minimum_range_m=state.planar_range_m,
        predicted_maximum_bearing_deg=abs(state.bearing_deg),
        search_expansions=expansions,
        search_reached_goal=False,
        orientation_effective=orientation_effective,
        orientation_required=orientation_required,
        top_candidates=tuple(top_candidates),
    )


# ---------------------------------------------------------------------------
# Bounded weighted-A* local planner
# ---------------------------------------------------------------------------


def select_joint_pose_plan(
    state: ObjectPoseState,
    target: ObjectPoseTarget,
    config: JointPoseConfig,
    *,
    orientation_required: bool,
    previous_primitive: Optional[Primitive] = None,
    recent_states: Sequence[ObjectPoseState] = (),
    step_scale: float = 1.0,
    top_k: Optional[int] = None,
) -> JointPoseDecision:
    """Plan one camera-reset micro action toward the taught joint pose.

    The search may accept a first action whose immediate Cartesian or bearing
    error is temporarily worse, provided a bounded route reaches a lower joint
    pose error.  This is the core behavioural difference from the old
    left/right-then-forward/back priority loop.
    """

    if top_k is not None:
        config = JointPoseConfig(**{
            **config.__dict__,
            "top_candidate_count": max(0, int(top_k)),
        })
    config.validate()
    valid_start, start_reason = _state_admissibility(state, config)
    effective_orientation = orientation_is_effective(
        state, config, orientation_required=orientation_required
    )

    if not valid_start:
        return _hold_decision(
            state=state,
            target=target,
            config=config,
            reason=f"initial_state_not_admissible:{start_reason}",
            orientation_required=orientation_required,
            orientation_effective=effective_orientation,
        )

    if orientation_required and not effective_orientation:
        if not config.position_only_when_orientation_unreliable:
            return _hold_decision(
                state=state,
                target=target,
                config=config,
                reason="orientation_unreliable_hold_for_fresh_observation",
                orientation_required=True,
                orientation_effective=False,
            )
        if is_aligned(
            state,
            target,
            config,
            orientation_required=False,
        ):
            return _hold_decision(
                state=state,
                target=target,
                config=config,
                reason="position_reached_orientation_unreliable_hold",
                orientation_required=True,
                orientation_effective=False,
            )

    if is_aligned(
        state,
        target,
        config,
        orientation_required=effective_orientation,
    ):
        if orientation_required and not effective_orientation:
            return _hold_decision(
                state=state,
                target=target,
                config=config,
                reason="position_reached_orientation_unreliable_hold",
                orientation_required=True,
                orientation_effective=False,
            )
        current_cost = goal_error(
            state,
            target,
            config,
            orientation_required=effective_orientation,
        )
        goal = robot_goal_for_taught_object_pose(
            state,
            target,
            orientation_required=effective_orientation,
        )
        return JointPoseDecision(
            aligned=True,
            hold=False,
            reason="joint_pose_within_all_tolerances",
            sequence=(),
            route_preview=(),
            current_state=state,
            predicted_state=state,
            planned_terminal_state=state,
            robot_goal=goal,
            current_cost=current_cost,
            planned_terminal_cost=current_cost,
            expected_improvement=0.0,
            predicted_minimum_range_m=state.planar_range_m,
            predicted_maximum_bearing_deg=abs(state.bearing_deg),
            search_expansions=0,
            search_reached_goal=True,
            orientation_effective=effective_orientation,
            orientation_required=orientation_required,
            top_candidates=(),
        )

    top_candidates = _first_action_candidates(
        state,
        target,
        config,
        orientation_required=effective_orientation,
        previous_primitive=previous_primitive,
        recent_states=recent_states,
        step_scale=step_scale,
    )
    start_cost = goal_error(
        state,
        target,
        config,
        orientation_required=effective_orientation,
    )
    start_h = _heuristic(
        state,
        target,
        config,
        orientation_required=effective_orientation,
    )

    root = _SearchNode(
        state=state,
        g_cost=0.0,
        depth=0,
        parent_index=None,
        primitive=None,
        previous_primitive=previous_primitive,
        translation_total_m=0.0,
        turn_total_deg=0.0,
        minimum_range_m=state.planar_range_m,
        maximum_bearing_deg=abs(state.bearing_deg),
    )
    nodes: list[_SearchNode] = [root]
    counter = itertools.count()
    open_heap: list[tuple[float, float, int, int]] = []
    heapq.heappush(
        open_heap,
        (config.heuristic_weight * start_h, start_h, next(counter), 0),
    )
    root_key = _quantized_key(
        state,
        previous_primitive,
        config,
        orientation_required=effective_orientation,
    )
    best_g: dict[tuple[int, int, int, str, int], float] = {root_key: 0.0}
    best_index = 0
    best_h = start_h
    best_cost = start_cost
    goal_index: Optional[int] = None
    expansions = 0

    search_started = time.perf_counter()
    deadline = search_started + config.search_maximum_wall_time_sec
    while open_heap and expansions < config.search_maximum_expansions:
        # Check periodically rather than on every edge to keep the common path
        # cheap. The root/early-goal cases still complete before this branch.
        if expansions and expansions % 16 == 0 and time.perf_counter() >= deadline:
            break
        _, _, _, index = heapq.heappop(open_heap)
        node = nodes[index]
        key = _quantized_key(
            node.state,
            node.previous_primitive,
            config,
            orientation_required=effective_orientation,
        )
        if node.g_cost > best_g.get(key, math.inf) + 1e-10:
            continue
        if is_aligned(
            node.state,
            target,
            config,
            orientation_required=effective_orientation,
        ):
            goal_index = index
            break
        if node.depth >= config.search_maximum_depth:
            continue

        expansions += 1
        actions = candidate_primitives(
            node.state,
            target,
            config,
            orientation_required=effective_orientation,
            step_scale=step_scale,
        )
        for primitive in actions:
            translation_total = node.translation_total_m + abs(
                primitive.effective_move_m
            )
            turn_total = node.turn_total_deg + abs(primitive.effective_turn_deg)
            if translation_total > config.search_maximum_translation_m + 1e-12:
                continue
            if turn_total > config.search_maximum_turn_deg + 1e-12:
                continue

            valid, _, predicted, minimum_range, maximum_bearing = (
                primitive_admissibility(node.state, primitive, config)
            )
            if not valid:
                continue

            edge = _edge_cost(primitive, node.previous_primitive, config)
            if node.depth == 0 and recent_states:
                cycle_penalty, hard_cycle = _recent_cycle_cost(
                    predicted,
                    target,
                    recent_states,
                    config,
                    orientation_required=effective_orientation,
                    current_cost=start_cost,
                )
                if hard_cycle:
                    continue
                edge += cycle_penalty

            new_g = node.g_cost + edge
            child_key = _quantized_key(
                predicted,
                primitive,
                config,
                orientation_required=effective_orientation,
            )
            if new_g >= best_g.get(child_key, math.inf) - 1e-10:
                continue
            best_g[child_key] = new_g
            child = _SearchNode(
                state=predicted,
                g_cost=new_g,
                depth=node.depth + 1,
                parent_index=index,
                primitive=primitive,
                previous_primitive=primitive,
                translation_total_m=translation_total,
                turn_total_deg=turn_total,
                minimum_range_m=min(node.minimum_range_m, minimum_range),
                maximum_bearing_deg=max(node.maximum_bearing_deg, maximum_bearing),
            )
            child_index = len(nodes)
            nodes.append(child)
            child_h = _heuristic(
                predicted,
                target,
                config,
                orientation_required=effective_orientation,
            )
            child_cost = goal_error(
                predicted,
                target,
                config,
                orientation_required=effective_orientation,
            )
            if (
                child_h < best_h - 1e-10
                or (
                    abs(child_h - best_h) <= 1e-10
                    and child_cost < best_cost
                )
            ):
                best_h = child_h
                best_cost = child_cost
                best_index = child_index
            weighted_f = new_g + config.heuristic_weight * child_h
            heapq.heappush(
                open_heap,
                (weighted_f, child_h, next(counter), child_index),
            )

    selected_index = goal_index
    reached_goal = selected_index is not None
    if selected_index is None:
        h_improvement = start_h - best_h
        cost_improvement = start_cost - best_cost
        # A frontier route may begin with a temporarily worse observation, but
        # its planned terminal state must still improve the joint pose error.
        # This prevents an exhausted search from selecting an attractive-looking
        # kinematic decomposition that actually walks away from the taught pose.
        if best_index == 0 or cost_improvement < config.minimum_frontier_improvement:
            return _hold_decision(
                state=state,
                target=target,
                config=config,
                reason="joint_lattice_no_safe_improving_route",
                orientation_required=orientation_required,
                orientation_effective=effective_orientation,
                expansions=expansions,
                top_candidates=top_candidates,
            )
        selected_index = best_index

    route = _reconstruct(nodes, selected_index)
    if not route:
        return _hold_decision(
            state=state,
            target=target,
            config=config,
            reason="joint_lattice_selected_empty_route",
            orientation_required=orientation_required,
            orientation_effective=effective_orientation,
            expansions=expansions,
            top_candidates=top_candidates,
        )

    # ``validate`` enforces the one-primitive camera-reset contract.
    sequence = route[:1]
    predicted = apply_sequence(state, sequence)
    terminal_node = nodes[selected_index]
    terminal_cost = goal_error(
        terminal_node.state,
        target,
        config,
        orientation_required=effective_orientation,
    )
    expected_improvement = start_cost - terminal_cost
    minimum_range, maximum_bearing = route_envelope(
        state,
        sequence,
        sample_count=config.path_sample_count,
    )
    reason = (
        "joint_lattice_goal_route"
        if reached_goal
        else "joint_lattice_best_frontier_route"
    )
    return JointPoseDecision(
        aligned=False,
        hold=False,
        reason=reason,
        sequence=sequence,
        route_preview=route,
        current_state=state,
        predicted_state=predicted,
        planned_terminal_state=terminal_node.state,
        robot_goal=robot_goal_for_taught_object_pose(
            state,
            target,
            orientation_required=effective_orientation,
        ),
        current_cost=start_cost,
        planned_terminal_cost=terminal_cost,
        expected_improvement=expected_improvement,
        predicted_minimum_range_m=minimum_range,
        predicted_maximum_bearing_deg=maximum_bearing,
        search_expansions=expansions,
        search_reached_goal=reached_goal,
        orientation_effective=effective_orientation,
        orientation_required=orientation_required,
        top_candidates=top_candidates,
    )


def decision_from_mapping(value: Mapping[str, object]) -> Mapping[str, object]:
    """Marker helper for log tooling; intentionally returns an immutable view."""

    return dict(value)
