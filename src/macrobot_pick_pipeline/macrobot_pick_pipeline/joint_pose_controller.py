"""Axis-coupled local pose controller for MacRobot.

The controller recreates the taught camera-relative object pose as one SE(2)
goal.  It deliberately does not treat a smaller image bearing after a straight
retreat as object-axis progress.  Outside the taught grasp-axis corridor it
selects only coupled manoeuvres:

* a true ``DRIVE_REL`` constant-curvature arc; or
* a bounded ``TURN -> MOVE -> TURN`` dog-leg evaluated as one atomic macro.

The dog-leg is not three independent corrections.  Its terminal rigid-body
transform is scored as a unit, and the camera is consulted only after the
whole short macro.  This lets an intermediate steering turn temporarily make
an image error worse without the next callback immediately undoing it.

This module has no ROS imports.  Geometry, candidate safety, orientation
fusion, cycle rejection, and closed-loop convergence can therefore be tested
on a development computer.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
import math
import time
from typing import Iterable, Mapping, Optional, Sequence

PATCH_MARKER = "macrobot_axis_coupled_macro_v3"


# ---------------------------------------------------------------------------
# Numeric helpers
# ---------------------------------------------------------------------------


def wrap_angle_deg(value: float) -> float:
    """Wrap a directional angle to ``[-180, 180)`` degrees."""

    result = (float(value) + 180.0) % 360.0 - 180.0
    return 0.0 if abs(result) < 1e-12 else result


def wrap_axial_deg(value: float) -> float:
    """Wrap a 180-degree axis error to ``[-90, 90)`` degrees."""

    result = (float(value) + 90.0) % 180.0 - 90.0
    return 0.0 if abs(result) < 1e-12 else result


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


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(float(lower), min(float(upper), float(value)))


def _rotate(point: tuple[float, float], yaw_deg: float) -> tuple[float, float]:
    angle = math.radians(float(yaw_deg))
    cosine = math.cos(angle)
    sine = math.sin(angle)
    return (
        cosine * point[0] - sine * point[1],
        sine * point[0] + cosine * point[1],
    )


def _arc_endpoint(distance_m: float, yaw_deg: float) -> tuple[float, float]:
    """Return a centre-arc endpoint in the starting robot frame."""

    theta = math.radians(float(yaw_deg))
    distance = float(distance_m)
    if abs(theta) <= 1e-10:
        return distance, 0.0
    return (
        distance * math.sin(theta) / theta,
        distance * (1.0 - math.cos(theta)) / theta,
    )


def _sign(value: float) -> int:
    return 1 if value > 1e-12 else -1 if value < -1e-12 else 0


# ---------------------------------------------------------------------------
# Public data types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ObjectPoseState:
    """Observed object pose in physical ``base_link`` planar axes.

    ``orientation_error_deg`` is the current-minus-taught object-axis error.
    A positive value requires a left-positive robot yaw to restore the taught
    relative orientation.  The value is axial and therefore modulo 180 degrees.
    """

    forward_m: float
    lateral_m: float
    orientation_error_deg: float
    orientation_quality: float = 1.0
    orientation_reliable: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "forward_m", _finite(self.forward_m, "forward_m"))
        object.__setattr__(self, "lateral_m", _finite(self.lateral_m, "lateral_m"))
        object.__setattr__(
            self,
            "orientation_error_deg",
            wrap_axial_deg(
                _finite(self.orientation_error_deg, "orientation_error_deg")
            ),
        )
        object.__setattr__(
            self,
            "orientation_quality",
            _clamp(
                _finite(self.orientation_quality, "orientation_quality"),
                0.0,
                1.0,
            ),
        )
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
    """Taught camera-relative object point; taught axis error is zero."""

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
    """Exact current-frame robot displacement recreating the taught view."""

    x_m: float
    y_m: float
    yaw_deg: float

    def to_mapping(self) -> dict[str, float]:
        return {"x_m": self.x_m, "y_m": self.y_m, "yaw_deg": self.yaw_deg}


@dataclass(frozen=True)
class AxisCorridorError:
    """Robot-goal error resolved in the desired final robot-axis frame."""

    along_m: float
    cross_track_m: float
    heading_error_deg: float
    position_error_m: float

    def to_mapping(self) -> dict[str, float]:
        return {
            "along_m": self.along_m,
            "cross_track_m": self.cross_track_m,
            "heading_error_deg": self.heading_error_deg,
            "position_error_m": self.position_error_m,
        }


@dataclass(frozen=True)
class OrientationFilterResult:
    raw_error_deg: float
    predicted_error_deg: float
    filtered_error_deg: float
    innovation_deg: float
    clipped_innovation_deg: float
    measurement_gain: float
    mode: str

    def to_mapping(self) -> dict[str, float | str]:
        return {
            "raw_error_deg": self.raw_error_deg,
            "predicted_error_deg": self.predicted_error_deg,
            "filtered_error_deg": self.filtered_error_deg,
            "innovation_deg": self.innovation_deg,
            "clipped_innovation_deg": self.clipped_innovation_deg,
            "measurement_gain": self.measurement_gain,
            "mode": self.mode,
        }


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
        if abs(amount) <= 1e-12:
            raise ValueError("primitive amount must be non-zero")
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
        value = self.effective_move_m
        if abs(value) <= 1e-12:
            value = self.effective_turn_deg
        return _sign(value)

    def signature(self) -> tuple[str, int, int]:
        return self.kind, _sign(self.effective_move_m), _sign(self.effective_turn_deg)

    def to_mapping(self) -> dict[str, float | str]:
        return {"kind": self.kind, "amount": self.amount, "yaw_deg": self.yaw_deg}


@dataclass(frozen=True)
class JointPoseConfig:
    """Local macro, sensing, and safety parameters."""

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
    drive_enabled: bool = True
    position_only_when_orientation_unreliable: bool = True

    # Desired final-axis corridor and coupled macro synthesis.
    axis_corridor_tolerance_m: float = 0.008
    axis_turn_position_gate_m: float = 0.014
    axis_straight_heading_gate_deg: float = 5.0
    axis_cross_track_weight: float = 2.8
    axis_heading_weight: float = 1.6
    axis_along_weight: float = 1.0
    maximum_steering_turn_deg: float = 16.0
    maximum_heading_step_deg: float = 8.0
    minimum_coupled_steering_deg: float = 1.0
    minimum_drive_radius_m: float = 0.09
    minimum_drive_yaw_deg: float = 0.45
    drive_yaw_levels: int = 3
    macro_action_cost: float = 0.03
    dogleg_cost_penalty: float = 0.03
    minimum_macro_improvement: float = 0.04
    maximum_cross_track_regression_m: float = 0.006
    maximum_heading_regression_deg: float = 8.0

    # Axial orientation prediction/fusion.  A translation-only terminal motion
    # cannot physically rotate a static object's axis in base_link.
    orientation_translation_measurement_gain: float = 0.03
    orientation_stationary_measurement_gain: float = 0.20
    orientation_turn_measurement_gain: float = 0.45
    orientation_translation_innovation_limit_deg: float = 1.0
    orientation_turn_innovation_limit_deg: float = 12.0
    orientation_motion_yaw_epsilon_deg: float = 0.25

    # Kept for v2 parameter compatibility.  v3 uses the time budget and the
    # primitive-count field, but no longer runs the large weighted-A* lattice.
    position_resolution_m: float = 0.004
    orientation_resolution_deg: float = 2.0
    search_maximum_expansions: int = 25000
    search_maximum_wall_time_sec: float = 0.12
    search_maximum_depth: int = 3
    search_maximum_translation_m: float = 0.06
    search_maximum_turn_deg: float = 60.0
    heuristic_weight: float = 1.0
    execution_prefix_length: int = 3

    action_cost: float = 0.0
    motion_cost_weight: float = 0.04
    reverse_cost_penalty: float = 0.20
    drive_cost_penalty: float = 0.0
    action_family_change_penalty: float = 0.03
    immediate_reversal_penalty: float = 0.50
    same_direction_bonus: float = 0.02
    recent_cycle_penalty: float = 4.0
    hard_reject_recent_cycle: bool = True
    cycle_position_radius_m: float = 0.010
    cycle_orientation_radius_deg: float = 5.0
    cycle_required_cost_improvement: float = 0.20
    minimum_frontier_improvement: float = 0.04
    top_candidate_count: int = 8

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
            "axis_corridor_tolerance_m",
            "axis_turn_position_gate_m",
            "axis_straight_heading_gate_deg",
            "axis_cross_track_weight",
            "axis_heading_weight",
            "axis_along_weight",
            "maximum_steering_turn_deg",
            "maximum_heading_step_deg",
            "minimum_coupled_steering_deg",
            "minimum_drive_radius_m",
            "minimum_drive_yaw_deg",
            "orientation_translation_innovation_limit_deg",
            "orientation_turn_innovation_limit_deg",
            "orientation_motion_yaw_epsilon_deg",
            "position_resolution_m",
            "orientation_resolution_deg",
            "search_maximum_wall_time_sec",
            "search_maximum_translation_m",
            "search_maximum_turn_deg",
            "cycle_position_radius_m",
            "cycle_orientation_radius_deg",
        ):
            _positive(getattr(self, name), name)
        for name in (
            "macro_action_cost",
            "dogleg_cost_penalty",
            "minimum_macro_improvement",
            "maximum_cross_track_regression_m",
            "maximum_heading_regression_deg",
            "orientation_translation_measurement_gain",
            "orientation_stationary_measurement_gain",
            "orientation_turn_measurement_gain",
            "action_cost",
            "motion_cost_weight",
            "reverse_cost_penalty",
            "drive_cost_penalty",
            "action_family_change_penalty",
            "immediate_reversal_penalty",
            "same_direction_bonus",
            "recent_cycle_penalty",
            "cycle_required_cost_improvement",
            "minimum_frontier_improvement",
        ):
            _nonnegative(getattr(self, name), name)
        if not 0.0 <= self.minimum_orientation_quality <= 1.0:
            raise ValueError("minimum_orientation_quality must be within [0, 1]")
        for name in (
            "orientation_translation_measurement_gain",
            "orientation_stationary_measurement_gain",
            "orientation_turn_measurement_gain",
        ):
            if getattr(self, name) > 1.0:
                raise ValueError(f"{name} must be within [0, 1]")
        if self.maximum_object_range_m <= self.minimum_object_range_m:
            raise ValueError("maximum_object_range_m must exceed minimum_object_range_m")
        if self.minimum_move_step_m > self.maximum_move_step_m:
            raise ValueError("minimum_move_step_m exceeds maximum_move_step_m")
        if self.minimum_turn_step_deg > self.maximum_turn_step_deg:
            raise ValueError("minimum_turn_step_deg exceeds maximum_turn_step_deg")
        if self.maximum_heading_step_deg > 2.0 * self.maximum_steering_turn_deg:
            raise ValueError("maximum_heading_step_deg is incompatible with dog-leg turns")
        if int(self.turn_action_levels) not in range(1, 6):
            raise ValueError("turn_action_levels must be within [1, 5]")
        if int(self.move_action_levels) not in range(1, 6):
            raise ValueError("move_action_levels must be within [1, 5]")
        if int(self.drive_yaw_levels) not in range(1, 8):
            raise ValueError("drive_yaw_levels must be within [1, 7]")
        if int(self.path_sample_count) < 2 or int(self.path_sample_count) > 101:
            raise ValueError("path_sample_count must be within [2, 101]")
        if int(self.search_maximum_expansions) < 1:
            raise ValueError("search_maximum_expansions must be positive")
        if int(self.search_maximum_depth) < 1 or int(self.search_maximum_depth) > 3:
            raise ValueError("search_maximum_depth must be within [1, 3]")
        if int(self.execution_prefix_length) < 1 or int(self.execution_prefix_length) > 3:
            raise ValueError("execution_prefix_length must be within [1, 3]")
        if int(self.top_candidate_count) < 0:
            raise ValueError("top_candidate_count must be non-negative")


@dataclass(frozen=True)
class CandidateScore:
    sequence: tuple[Primitive, ...]
    maneuver_type: str
    predicted_state: ObjectPoseState
    estimated_total_cost: float
    goal_error: float
    expected_improvement: float
    predicted_minimum_range_m: float
    predicted_maximum_bearing_deg: float
    admissible: bool
    rejection_reason: str = ""

    @property
    def primitive(self) -> Primitive:
        """Compatibility accessor for v2 log consumers."""

        return self.sequence[0]

    def to_mapping(self) -> dict[str, object]:
        return {
            "maneuver_type": self.maneuver_type,
            "sequence": [item.to_mapping() for item in self.sequence],
            "predicted_state": self.predicted_state.to_mapping(),
            "estimated_total_cost": self.estimated_total_cost,
            "goal_error": self.goal_error,
            "expected_improvement": self.expected_improvement,
            "predicted_minimum_range_m": self.predicted_minimum_range_m,
            "predicted_maximum_bearing_deg": self.predicted_maximum_bearing_deg,
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
    current_axis_error: AxisCorridorError
    terminal_axis_error: AxisCorridorError
    current_cost: float
    planned_terminal_cost: float
    expected_improvement: float
    predicted_minimum_range_m: float
    predicted_maximum_bearing_deg: float
    search_expansions: int
    search_reached_goal: bool
    orientation_effective: bool
    orientation_required: bool
    maneuver_type: str = "hold"
    top_candidates: tuple[CandidateScore, ...] = field(default_factory=tuple)

    def to_mapping(self) -> dict[str, object]:
        return {
            "aligned": self.aligned,
            "hold": self.hold,
            "reason": self.reason,
            "maneuver_type": self.maneuver_type,
            "sequence": [item.to_mapping() for item in self.sequence],
            "route_preview": [item.to_mapping() for item in self.route_preview],
            "current_state": self.current_state.to_mapping(),
            "predicted_state": self.predicted_state.to_mapping(),
            "planned_terminal_state": self.planned_terminal_state.to_mapping(),
            "robot_goal": self.robot_goal.to_mapping(),
            "current_axis_error": self.current_axis_error.to_mapping(),
            "terminal_axis_error": self.terminal_axis_error.to_mapping(),
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
# Exact target geometry and orientation fusion
# ---------------------------------------------------------------------------


def bearing_error_deg(state: ObjectPoseState, target: ObjectPoseTarget) -> float:
    return wrap_angle_deg(state.bearing_deg - target.bearing_deg)


def robot_goal_for_taught_object_pose(
    state: ObjectPoseState,
    target: ObjectPoseTarget,
    *,
    orientation_required: bool,
) -> RobotRelativeGoal:
    """Solve the current-frame robot pose that recreates the taught view.

    For robot translation ``t`` and left-positive yaw ``theta``::

        p_target = R(-theta) (p_current - t)

    therefore ``t = p_current - R(theta) p_target``.
    """

    yaw = state.orientation_error_deg if orientation_required else 0.0
    rotated_target = _rotate((target.forward_m, target.lateral_m), yaw)
    return RobotRelativeGoal(
        state.forward_m - rotated_target[0],
        state.lateral_m - rotated_target[1],
        wrap_angle_deg(yaw),
    )


def axis_corridor_error(goal: RobotRelativeGoal) -> AxisCorridorError:
    """Resolve translation into along/cross components of the final axis."""

    theta = math.radians(goal.yaw_deg)
    cosine = math.cos(theta)
    sine = math.sin(theta)
    along = cosine * goal.x_m + sine * goal.y_m
    cross = -sine * goal.x_m + cosine * goal.y_m
    return AxisCorridorError(
        along_m=along,
        cross_track_m=cross,
        heading_error_deg=wrap_angle_deg(goal.yaw_deg),
        position_error_m=math.hypot(goal.x_m, goal.y_m),
    )


def sequence_net_yaw_deg(sequence: Sequence[Primitive]) -> float:
    return wrap_angle_deg(sum(item.effective_turn_deg for item in sequence))


def sequence_total_translation_m(sequence: Sequence[Primitive]) -> float:
    return sum(abs(item.effective_move_m) for item in sequence)


def representative_primitive(sequence: Sequence[Primitive]) -> Optional[Primitive]:
    """Return the translating primitive used for cross-macro hysteresis."""

    for item in sequence:
        if item.kind in {"move", "drive"}:
            return item
    return sequence[-1] if sequence else None


def fuse_axial_orientation_error(
    *,
    previous_error_deg: Optional[float],
    measured_error_deg: float,
    measurement_quality: float,
    expected_robot_yaw_deg: float,
    motion_kind: Optional[str],
    config: JointPoseConfig,
) -> OrientationFilterResult:
    """Fuse an axial observation with the rigid-body yaw prediction.

    A terminal motion with zero net yaw cannot physically rotate the axis of a
    static object in ``base_link``.  A large apparent improvement after a
    straight retreat or zero-net-yaw dog-leg is therefore clipped and given a
    very small gain instead of becoming control authority.
    """

    measured = wrap_axial_deg(_finite(measured_error_deg, "measured_error_deg"))
    quality = _clamp(_finite(measurement_quality, "measurement_quality"), 0.0, 1.0)
    expected_yaw = _finite(expected_robot_yaw_deg, "expected_robot_yaw_deg")
    if previous_error_deg is None:
        return OrientationFilterResult(
            raw_error_deg=measured,
            predicted_error_deg=measured,
            filtered_error_deg=measured,
            innovation_deg=0.0,
            clipped_innovation_deg=0.0,
            measurement_gain=1.0,
            mode="initial_measurement",
        )

    predicted = wrap_axial_deg(float(previous_error_deg) - expected_yaw)
    innovation = wrap_axial_deg(measured - predicted)
    if abs(expected_yaw) <= config.orientation_motion_yaw_epsilon_deg and motion_kind in {
        "move",
        "zero_net_yaw_macro",
    }:
        mode = "translation_invariant"
        gain = config.orientation_translation_measurement_gain
        limit = config.orientation_translation_innovation_limit_deg
    elif abs(expected_yaw) > config.orientation_motion_yaw_epsilon_deg:
        mode = "yaw_prediction_fusion"
        gain = config.orientation_turn_measurement_gain
        limit = config.orientation_turn_innovation_limit_deg
    else:
        mode = "stationary_fusion"
        gain = config.orientation_stationary_measurement_gain
        limit = config.orientation_turn_innovation_limit_deg

    effective_gain = _clamp(gain * max(0.10, quality), 0.0, 1.0)
    clipped = _clamp(innovation, -limit, limit)
    filtered = wrap_axial_deg(predicted + effective_gain * clipped)
    return OrientationFilterResult(
        raw_error_deg=measured,
        predicted_error_deg=predicted,
        filtered_error_deg=filtered,
        innovation_deg=innovation,
        clipped_innovation_deg=clipped,
        measurement_gain=effective_gain,
        mode=mode,
    )


# ---------------------------------------------------------------------------
# Motion model and safety envelope
# ---------------------------------------------------------------------------


def _primitive_robot_pose(
    primitive: Primitive, fraction: float = 1.0
) -> RobotRelativeGoal:
    u = _clamp(float(fraction), 0.0, 1.0)
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
    samples = (
        sampled_states_during_primitive(state, primitive, config.path_sample_count)
        if primitive.kind == "drive"
        else (apply_primitive(state, primitive),)
    )
    predicted = state
    for predicted in samples:
        minimum_range = min(minimum_range, predicted.planar_range_m)
        maximum_bearing = max(maximum_bearing, abs(predicted.bearing_deg))
        valid, reason = _state_admissibility(predicted, config)
        if not valid:
            return False, reason, predicted, minimum_range, maximum_bearing
    return True, "", predicted, minimum_range, maximum_bearing


def route_envelope(
    state: ObjectPoseState,
    sequence: Sequence[Primitive],
    *,
    config: JointPoseConfig,
) -> tuple[bool, str, ObjectPoseState, float, float]:
    current = state
    minimum_range = state.planar_range_m
    maximum_bearing = abs(state.bearing_deg)
    for primitive in sequence:
        valid, reason, current, local_minimum, local_maximum = primitive_admissibility(
            current, primitive, config
        )
        minimum_range = min(minimum_range, local_minimum)
        maximum_bearing = max(maximum_bearing, local_maximum)
        if not valid:
            return False, reason, current, minimum_range, maximum_bearing
    return True, "", current, minimum_range, maximum_bearing


# ---------------------------------------------------------------------------
# Goal and cycle logic
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
        # Independent point/orientation tolerances can still describe a robot
        # pose that is centimetres away from the final grasp axis (for example,
        # 2 degrees at 0.25 m is about 8.7 mm).  Require the exact SE(2) robot
        # goal to be inside the final-axis corridor before declaring success.
        axis = axis_corridor_error(
            robot_goal_for_taught_object_pose(
                state, target, orientation_required=True
            )
        )
        if abs(axis.cross_track_m) > config.axis_corridor_tolerance_m:
            return False
        if axis.position_error_m > config.axis_turn_position_gate_m:
            return False
    return True


def goal_error(
    state: ObjectPoseState,
    target: ObjectPoseTarget,
    config: JointPoseConfig,
    *,
    orientation_required: bool,
) -> float:
    """Dimensionless final-axis SE(2) error.

    Bearing alone shrinks when the robot retreats.  Metric cross-track does not:
    with unchanged yaw, a straight retreat leaves lateral displacement from the
    taught axis visible in this cost.
    """

    goal = robot_goal_for_taught_object_pose(
        state, target, orientation_required=orientation_required
    )
    axis = axis_corridor_error(goal)
    along_scale = max(config.forward_tolerance_m, config.lateral_tolerance_m)
    along = axis.along_m / along_scale
    cross = axis.cross_track_m / config.axis_corridor_tolerance_m
    heading = (
        axis.heading_error_deg / config.orientation_tolerance_deg
        if orientation_required
        else 0.0
    )
    weighted = math.sqrt(
        config.axis_along_weight * along * along
        + config.axis_cross_track_weight * cross * cross
        + config.axis_heading_weight * heading * heading
    )
    bearing = abs(bearing_error_deg(state, target)) / config.bearing_tolerance_deg
    return weighted + 0.05 * bearing


pose_cost = goal_error


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


# ---------------------------------------------------------------------------
# Coupled macro generation
# ---------------------------------------------------------------------------


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
    if all(abs(value - floor) > max(1e-9, 0.10 * floor) for value in values):
        values.append(floor)
    return tuple(sorted({round(value, 12) for value in values}, reverse=True))


def _deduplicate_sequences(
    values: Iterable[tuple[str, tuple[Primitive, ...]]],
) -> tuple[tuple[str, tuple[Primitive, ...]], ...]:
    seen: set[tuple[tuple[str, int, int], ...]] = set()
    result: list[tuple[str, tuple[Primitive, ...]]] = []
    for maneuver_type, sequence in values:
        key = tuple(
            (
                item.kind,
                int(round(item.amount * 1_000_000.0)),
                int(round(item.yaw_deg * 1_000_000.0)),
            )
            for item in sequence
        )
        if not key or key in seen:
            continue
        seen.add(key)
        result.append((maneuver_type, sequence))
    return tuple(result)


def _optional_turn(value: float, config: JointPoseConfig) -> tuple[Primitive, ...]:
    if abs(value) < config.minimum_turn_step_deg:
        return ()
    return (Primitive("turn", value),)


def _bounded_distance(value: float, config: JointPoseConfig) -> Optional[float]:
    if abs(value) < config.minimum_move_step_m:
        return None
    if value > 0.0:
        return min(value, config.maximum_move_step_m)
    if not config.allow_reverse:
        return None
    return max(value, -config.maximum_reverse_step_m)


def _dogleg_candidates(
    state: ObjectPoseState,
    target: ObjectPoseTarget,
    config: JointPoseConfig,
    *,
    orientation_required: bool,
    step_scale: float,
) -> tuple[tuple[str, tuple[Primitive, ...]], ...]:
    goal = robot_goal_for_taught_object_pose(
        state, target, orientation_required=orientation_required
    )
    scale = _clamp(step_scale, 0.25, 1.0)
    max_steer = max(
        config.minimum_coupled_steering_deg,
        config.maximum_steering_turn_deg * scale,
    )
    max_heading = max(
        config.minimum_turn_step_deg,
        config.maximum_heading_step_deg * scale,
    )
    max_forward = max(config.minimum_move_step_m, config.maximum_move_step_m * scale)
    max_reverse = max(config.minimum_move_step_m, config.maximum_reverse_step_m * scale)

    position_bearing = (
        math.degrees(math.atan2(goal.y_m, goal.x_m))
        if math.hypot(goal.x_m, goal.y_m) > 1e-12
        else 0.0
    )
    alpha_values = {0.0, _clamp(position_bearing, -max_steer, max_steer)}
    for magnitude in _geometric_levels(
        max_steer,
        config.minimum_coupled_steering_deg,
        config.turn_action_levels,
    ):
        alpha_values.add(magnitude)
        alpha_values.add(-magnitude)

    heading_values = {
        0.0,
        _clamp(goal.yaw_deg, -max_heading, max_heading),
        _clamp(0.5 * goal.yaw_deg, -max_heading, max_heading),
    }
    if abs(goal.yaw_deg) >= config.minimum_turn_step_deg:
        heading_values.add(
            math.copysign(
                min(max_heading, config.minimum_turn_step_deg), goal.yaw_deg
            )
        )

    base_forward = _geometric_levels(
        max_forward, config.minimum_move_step_m, config.move_action_levels
    )
    base_reverse = (
        _geometric_levels(
            max_reverse, config.minimum_move_step_m, config.move_action_levels
        )
        if config.allow_reverse
        else ()
    )

    raw: list[tuple[str, tuple[Primitive, ...]]] = []
    for alpha in sorted(alpha_values):
        alpha_rad = math.radians(alpha)
        direction = (math.cos(alpha_rad), math.sin(alpha_rad))
        distance_values: set[float] = set(base_forward)
        if config.allow_reverse:
            distance_values.update(-item for item in base_reverse)

        projected = goal.x_m * direction[0] + goal.y_m * direction[1]
        bounded_projected = _bounded_distance(projected, config)
        if bounded_projected is not None:
            distance_values.add(bounded_projected)
        if abs(direction[1]) > 0.08:
            lateral_solution = _bounded_distance(goal.y_m / direction[1], config)
            if lateral_solution is not None:
                distance_values.add(lateral_solution)

        local_heading_values = set(heading_values)
        local_heading_values.add(_clamp(alpha, -max_heading, max_heading))
        local_heading_values.add(
            _clamp(alpha + max_steer, -max_heading, max_heading)
        )
        local_heading_values.add(
            _clamp(alpha - max_steer, -max_heading, max_heading)
        )
        for distance in sorted(distance_values):
            if distance < 0.0 and not config.allow_reverse:
                continue
            for net_yaw in sorted(local_heading_values):
                final_turn = net_yaw - alpha
                if abs(alpha) > max_steer + 1e-9:
                    continue
                if abs(final_turn) > max_steer + 1e-9:
                    continue
                sequence = (
                    _optional_turn(alpha, config)
                    + (Primitive("move", distance),)
                    + _optional_turn(final_turn, config)
                )
                if len(sequence) > int(config.execution_prefix_length):
                    continue
                # Outside the final corridor, a pure straight retreat is not an
                # axis controller.  The macro must steer before translating.
                goal_axis = axis_corridor_error(goal)
                off_axis = abs(goal_axis.cross_track_m) > config.axis_corridor_tolerance_m
                if off_axis and abs(alpha) < config.minimum_coupled_steering_deg:
                    continue
                kind = "dogleg_reverse" if distance < 0.0 else "dogleg_forward"
                raw.append((kind, sequence))
    return _deduplicate_sequences(raw)


def _bounded_drive_yaw(
    distance_m: float,
    requested_yaw_deg: float,
    config: JointPoseConfig,
    *,
    step_scale: float,
) -> Optional[float]:
    maximum = max(
        config.minimum_drive_yaw_deg,
        config.maximum_drive_yaw_deg * _clamp(step_scale, 0.25, 1.0),
    )
    yaw = _clamp(requested_yaw_deg, -maximum, maximum)
    if abs(yaw) < config.minimum_drive_yaw_deg:
        return None
    radius = abs(float(distance_m) / math.radians(yaw))
    if radius + 1e-12 < config.minimum_drive_radius_m:
        maximum_for_radius = math.degrees(
            abs(float(distance_m)) / config.minimum_drive_radius_m
        )
        yaw = math.copysign(min(abs(yaw), maximum_for_radius), yaw)
    if abs(yaw) < config.minimum_drive_yaw_deg:
        return None
    return yaw


def _drive_candidates(
    state: ObjectPoseState,
    target: ObjectPoseTarget,
    config: JointPoseConfig,
    *,
    orientation_required: bool,
    step_scale: float,
) -> tuple[tuple[str, tuple[Primitive, ...]], ...]:
    if not config.drive_enabled:
        return ()
    goal = robot_goal_for_taught_object_pose(
        state, target, orientation_required=orientation_required
    )
    scale = _clamp(step_scale, 0.25, 1.0)
    max_forward = max(config.minimum_move_step_m, config.maximum_move_step_m * scale)
    max_reverse = max(config.minimum_move_step_m, config.maximum_reverse_step_m * scale)
    distances: set[float] = set(
        _geometric_levels(
            max_forward, config.minimum_move_step_m, config.move_action_levels
        )
    )
    if config.allow_reverse:
        distances.update(
            -item
            for item in _geometric_levels(
                max_reverse, config.minimum_move_step_m, config.move_action_levels
            )
        )

    denominator = goal.x_m * goal.x_m + goal.y_m * goal.y_m
    raw: list[tuple[str, tuple[Primitive, ...]]] = []
    for distance in sorted(distances):
        maximum = max(
            config.minimum_drive_yaw_deg,
            config.maximum_drive_yaw_deg * scale,
        )
        requested: set[float] = set()
        for magnitude in _geometric_levels(
            maximum, config.minimum_drive_yaw_deg, config.drive_yaw_levels
        ):
            requested.add(magnitude)
            requested.add(-magnitude)
        requested.add(_clamp(goal.yaw_deg, -maximum, maximum))
        if denominator > 1e-10:
            curvature = 2.0 * goal.y_m / denominator
            requested.add(math.degrees(curvature * distance))
        for requested_yaw in requested:
            yaw = _bounded_drive_yaw(
                distance, requested_yaw, config, step_scale=scale
            )
            if yaw is None:
                continue
            kind = "drive_reverse" if distance < 0.0 else "drive_forward"
            raw.append((kind, (Primitive("drive", distance, yaw),)))
    return _deduplicate_sequences(raw)


def _corridor_candidates(
    state: ObjectPoseState,
    target: ObjectPoseTarget,
    config: JointPoseConfig,
    *,
    orientation_required: bool,
    step_scale: float,
) -> tuple[tuple[str, tuple[Primitive, ...]], ...]:
    goal = robot_goal_for_taught_object_pose(
        state, target, orientation_required=orientation_required
    )
    axis = axis_corridor_error(goal)
    scale = _clamp(step_scale, 0.25, 1.0)
    raw: list[tuple[str, tuple[Primitive, ...]]] = []

    corridor_locked = abs(axis.cross_track_m) <= config.axis_corridor_tolerance_m
    heading_locked = (
        not orientation_required
        or abs(axis.heading_error_deg) <= config.axis_straight_heading_gate_deg
    )
    if corridor_locked and heading_locked:
        requested = _bounded_distance(goal.x_m, config)
        if requested is not None:
            raw.append(
                (
                    "corridor_reverse" if requested < 0.0 else "corridor_forward",
                    (Primitive("move", requested * scale),),
                )
            )
        max_forward = max(config.minimum_move_step_m, config.maximum_move_step_m * scale)
        sign = _sign(goal.x_m)
        if sign > 0:
            raw.append(("corridor_forward", (Primitive("move", max_forward),)))
        elif sign < 0 and config.allow_reverse:
            raw.append(
                (
                    "corridor_reverse",
                    (
                        Primitive(
                            "move",
                            -max(
                                config.minimum_move_step_m,
                                config.maximum_reverse_step_m * scale,
                            ),
                        ),
                    ),
                )
            )

    if (
        corridor_locked
        and axis.position_error_m <= config.axis_turn_position_gate_m
        and orientation_required
        and abs(axis.heading_error_deg) >= config.minimum_turn_step_deg
    ):
        amount = _clamp(
            axis.heading_error_deg,
            -config.maximum_turn_step_deg * scale,
            config.maximum_turn_step_deg * scale,
        )
        if abs(amount) >= config.minimum_turn_step_deg:
            raw.append(("final_axis_turn", (Primitive("turn", amount),)))
    return _deduplicate_sequences(raw)


def candidate_maneuvers(
    state: ObjectPoseState,
    target: ObjectPoseTarget,
    config: JointPoseConfig,
    *,
    orientation_required: bool,
    step_scale: float = 1.0,
) -> tuple[tuple[str, tuple[Primitive, ...]], ...]:
    values: list[tuple[str, tuple[Primitive, ...]]] = []
    values.extend(
        _drive_candidates(
            state,
            target,
            config,
            orientation_required=orientation_required,
            step_scale=step_scale,
        )
    )
    values.extend(
        _dogleg_candidates(
            state,
            target,
            config,
            orientation_required=orientation_required,
            step_scale=step_scale,
        )
    )
    values.extend(
        _corridor_candidates(
            state,
            target,
            config,
            orientation_required=orientation_required,
            step_scale=step_scale,
        )
    )
    return _deduplicate_sequences(values)


def candidate_primitives(
    state: ObjectPoseState,
    target: ObjectPoseTarget,
    config: JointPoseConfig,
    *,
    orientation_required: bool,
    step_scale: float = 1.0,
) -> tuple[Primitive, ...]:
    """Compatibility view returning the first primitive of each macro."""

    result: list[Primitive] = []
    seen: set[tuple[str, int, int]] = set()
    for _, sequence in candidate_maneuvers(
        state,
        target,
        config,
        orientation_required=orientation_required,
        step_scale=step_scale,
    ):
        first = sequence[0]
        key = (
            first.kind,
            int(round(first.amount * 1_000_000.0)),
            int(round(first.yaw_deg * 1_000_000.0)),
        )
        if key not in seen:
            seen.add(key)
            result.append(first)
    return tuple(result)


# ---------------------------------------------------------------------------
# Candidate evaluation and local decision
# ---------------------------------------------------------------------------


def _is_translation_reversal(
    previous: Optional[Primitive], sequence: Sequence[Primitive]
) -> bool:
    current = representative_primitive(sequence)
    if previous is None or current is None:
        return False
    previous_move = previous.effective_move_m
    current_move = current.effective_move_m
    return abs(previous_move) > 1e-12 and previous_move * current_move < 0.0


def _maneuver_score(
    *,
    maneuver_type: str,
    sequence: Sequence[Primitive],
    terminal_error: float,
    previous_primitive: Optional[Primitive],
    config: JointPoseConfig,
) -> float:
    score = terminal_error + config.macro_action_cost * max(0, len(sequence) - 1)
    translation = sequence_total_translation_m(sequence)
    yaw = sum(abs(item.effective_turn_deg) for item in sequence)
    score += config.motion_cost_weight * (
        translation / max(config.maximum_move_step_m, 1e-9)
        + yaw / max(config.maximum_steering_turn_deg, 1e-9)
    )
    if any(item.effective_move_m < 0.0 for item in sequence):
        score += config.reverse_cost_penalty
    if maneuver_type.startswith("dogleg"):
        score += config.dogleg_cost_penalty
    if maneuver_type.startswith("drive"):
        score += config.drive_cost_penalty
    if _is_translation_reversal(previous_primitive, sequence):
        score += config.immediate_reversal_penalty
    current = representative_primitive(sequence)
    if previous_primitive is not None and current is not None:
        if previous_primitive.kind != current.kind:
            score += config.action_family_change_penalty
        elif previous_primitive.signature() == current.signature():
            score = max(0.0, score - config.same_direction_bonus)
    return score


def _evaluate_candidate(
    *,
    state: ObjectPoseState,
    target: ObjectPoseTarget,
    config: JointPoseConfig,
    orientation_required: bool,
    maneuver_type: str,
    sequence: tuple[Primitive, ...],
    previous_primitive: Optional[Primitive],
    recent_states: Sequence[ObjectPoseState],
    current_error: float,
    current_axis: AxisCorridorError,
) -> CandidateScore:
    valid, reason, predicted, minimum_range, maximum_bearing = route_envelope(
        state, sequence, config=config
    )
    if valid and sequence_total_translation_m(sequence) > (
        config.search_maximum_translation_m + 1e-12
    ):
        valid = False
        reason = "macro_translation_bound_exceeded"
    total_turn = sum(abs(item.effective_turn_deg) for item in sequence)
    if valid and total_turn > config.search_maximum_turn_deg + 1e-12:
        valid = False
        reason = "macro_turn_bound_exceeded"

    terminal_error = goal_error(
        predicted,
        target,
        config,
        orientation_required=orientation_required,
    )
    improvement = current_error - terminal_error
    terminal_goal = robot_goal_for_taught_object_pose(
        predicted, target, orientation_required=orientation_required
    )
    terminal_axis = axis_corridor_error(terminal_goal)

    off_axis = abs(current_axis.cross_track_m) > config.axis_corridor_tolerance_m
    contains_translation = any(abs(item.effective_move_m) > 1e-12 for item in sequence)
    contains_steering = any(abs(item.effective_turn_deg) >= config.minimum_coupled_steering_deg for item in sequence)
    if valid and off_axis and orientation_required:
        if not contains_translation or not contains_steering:
            valid = False
            reason = "off_axis_requires_coupled_translation_and_steering"
        cross_regression = (
            abs(terminal_axis.cross_track_m) - abs(current_axis.cross_track_m)
        )
        heading_regression = (
            abs(terminal_axis.heading_error_deg) - abs(current_axis.heading_error_deg)
        )
        if cross_regression > config.maximum_cross_track_regression_m:
            valid = False
            reason = "cross_track_regression_too_large"
        elif heading_regression > config.maximum_heading_regression_deg:
            valid = False
            reason = "heading_regression_too_large"

    reaches_goal = valid and is_aligned(
        predicted,
        target,
        config,
        orientation_required=orientation_required,
    )
    if valid and not reaches_goal and improvement < config.minimum_macro_improvement:
        valid = False
        reason = "insufficient_terminal_joint_improvement"

    if valid:
        for recent in recent_states:
            if not states_near(
                predicted,
                recent,
                config,
                orientation_required=orientation_required,
            ):
                continue
            # A geometric neighbourhood is deliberately wider than the final
            # actuator resolution.  Do not reject a candidate merely because it
            # enters that neighbourhood: reject only when it fails to improve
            # on the cost previously observed there.  This preserves the loop
            # guard without trapping the controller just outside a tolerance.
            recent_error = goal_error(
                recent,
                target,
                config,
                orientation_required=orientation_required,
            )
            improvement_over_revisit = recent_error - terminal_error
            if improvement_over_revisit < config.cycle_required_cost_improvement:
                if config.hard_reject_recent_cycle:
                    valid = False
                    reason = "recent_measured_cycle_hard_reject"
                break

    score = _maneuver_score(
        maneuver_type=maneuver_type,
        sequence=sequence,
        terminal_error=terminal_error,
        previous_primitive=previous_primitive,
        config=config,
    )
    if not valid:
        score += config.recent_cycle_penalty
    return CandidateScore(
        sequence=sequence,
        maneuver_type=maneuver_type,
        predicted_state=predicted,
        estimated_total_cost=score,
        goal_error=terminal_error,
        expected_improvement=improvement,
        predicted_minimum_range_m=minimum_range,
        predicted_maximum_bearing_deg=maximum_bearing,
        admissible=valid,
        rejection_reason=reason,
    )


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
    effective = orientation_effective
    current_cost = goal_error(
        state, target, config, orientation_required=effective
    )
    goal = robot_goal_for_taught_object_pose(
        state, target, orientation_required=effective
    )
    axis = axis_corridor_error(goal)
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
        current_axis_error=axis,
        terminal_axis_error=axis,
        current_cost=current_cost,
        planned_terminal_cost=current_cost,
        expected_improvement=0.0,
        predicted_minimum_range_m=state.planar_range_m,
        predicted_maximum_bearing_deg=abs(state.bearing_deg),
        search_expansions=expansions,
        search_reached_goal=False,
        orientation_effective=effective,
        orientation_required=orientation_required,
        maneuver_type="hold",
        top_candidates=tuple(top_candidates),
    )


def _has_reverse_solution(
    state: ObjectPoseState,
    target: ObjectPoseTarget,
    config: JointPoseConfig,
    *,
    orientation_required: bool,
    previous_primitive: Optional[Primitive],
    recent_states: Sequence[ObjectPoseState],
    step_scale: float,
    current_error: float,
    current_axis: AxisCorridorError,
) -> bool:
    reverse_config = replace(config, allow_reverse=True, top_candidate_count=0)
    for maneuver_type, sequence in candidate_maneuvers(
        state,
        target,
        reverse_config,
        orientation_required=orientation_required,
        step_scale=step_scale,
    ):
        if not any(item.effective_move_m < 0.0 for item in sequence):
            continue
        score = _evaluate_candidate(
            state=state,
            target=target,
            config=reverse_config,
            orientation_required=orientation_required,
            maneuver_type=maneuver_type,
            sequence=sequence,
            previous_primitive=previous_primitive,
            recent_states=recent_states,
            current_error=current_error,
            current_axis=current_axis,
        )
        if score.admissible:
            return True
    return False


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
    """Select one bounded axis-coupled macro from a fresh camera state."""

    if top_k is not None:
        config = replace(config, top_candidate_count=max(0, int(top_k)))
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
        if is_aligned(state, target, config, orientation_required=False):
            return _hold_decision(
                state=state,
                target=target,
                config=config,
                reason="position_reached_orientation_unreliable_hold",
                orientation_required=True,
                orientation_effective=False,
            )

    planning_orientation = effective_orientation
    if is_aligned(
        state,
        target,
        config,
        orientation_required=planning_orientation,
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
            state, target, config, orientation_required=planning_orientation
        )
        goal = robot_goal_for_taught_object_pose(
            state, target, orientation_required=planning_orientation
        )
        axis = axis_corridor_error(goal)
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
            current_axis_error=axis,
            terminal_axis_error=axis,
            current_cost=current_cost,
            planned_terminal_cost=current_cost,
            expected_improvement=0.0,
            predicted_minimum_range_m=state.planar_range_m,
            predicted_maximum_bearing_deg=abs(state.bearing_deg),
            search_expansions=0,
            search_reached_goal=True,
            orientation_effective=effective_orientation,
            orientation_required=orientation_required,
            maneuver_type="aligned",
            top_candidates=(),
        )

    current_cost = goal_error(
        state, target, config, orientation_required=planning_orientation
    )
    goal = robot_goal_for_taught_object_pose(
        state, target, orientation_required=planning_orientation
    )
    current_axis = axis_corridor_error(goal)
    evaluated: list[CandidateScore] = []
    started = time.perf_counter()
    deadline = started + config.search_maximum_wall_time_sec
    for index, (maneuver_type, sequence) in enumerate(
        candidate_maneuvers(
            state,
            target,
            config,
            orientation_required=planning_orientation,
            step_scale=step_scale,
        )
    ):
        if index and index % 32 == 0 and time.perf_counter() >= deadline:
            break
        evaluated.append(
            _evaluate_candidate(
                state=state,
                target=target,
                config=config,
                orientation_required=planning_orientation,
                maneuver_type=maneuver_type,
                sequence=sequence,
                previous_primitive=previous_primitive,
                recent_states=recent_states,
                current_error=current_cost,
                current_axis=current_axis,
            )
        )
        if len(evaluated) >= config.search_maximum_expansions:
            break

    evaluated.sort(
        key=lambda item: (
            not item.admissible,
            item.estimated_total_cost,
            item.goal_error,
            len(item.sequence),
            item.maneuver_type,
        )
    )
    top_candidates = tuple(evaluated[: config.top_candidate_count])
    selected = next((item for item in evaluated if item.admissible), None)
    if selected is None:
        reason = "joint_pose_no_safe_improving_coupled_macro"
        if not config.allow_reverse and _has_reverse_solution(
            state,
            target,
            config,
            orientation_required=planning_orientation,
            previous_primitive=previous_primitive,
            recent_states=recent_states,
            step_scale=step_scale,
            current_error=current_cost,
            current_axis=current_axis,
        ):
            reason = "joint_pose_local_axis_shift_requires_reverse_clearance"
        return _hold_decision(
            state=state,
            target=target,
            config=config,
            reason=reason,
            orientation_required=orientation_required,
            orientation_effective=effective_orientation,
            expansions=len(evaluated),
            top_candidates=top_candidates,
        )

    terminal_goal = robot_goal_for_taught_object_pose(
        selected.predicted_state,
        target,
        orientation_required=planning_orientation,
    )
    terminal_axis = axis_corridor_error(terminal_goal)
    reached = is_aligned(
        selected.predicted_state,
        target,
        config,
        orientation_required=planning_orientation,
    )
    return JointPoseDecision(
        aligned=False,
        hold=False,
        reason="axis_coupled_macro_selected",
        sequence=selected.sequence,
        route_preview=selected.sequence,
        current_state=state,
        predicted_state=selected.predicted_state,
        planned_terminal_state=selected.predicted_state,
        robot_goal=goal,
        current_axis_error=current_axis,
        terminal_axis_error=terminal_axis,
        current_cost=current_cost,
        planned_terminal_cost=selected.goal_error,
        expected_improvement=selected.expected_improvement,
        predicted_minimum_range_m=selected.predicted_minimum_range_m,
        predicted_maximum_bearing_deg=selected.predicted_maximum_bearing_deg,
        search_expansions=len(evaluated),
        search_reached_goal=reached,
        orientation_effective=effective_orientation,
        orientation_required=orientation_required,
        maneuver_type=selected.maneuver_type,
        top_candidates=top_candidates,
    )


def decision_from_mapping(value: Mapping[str, object]) -> Mapping[str, object]:
    """Marker helper retained for downstream log tooling."""

    return dict(value)
