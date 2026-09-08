"""ROS 2 integration for the MacRobot axis-coupled local pose controller.

The executable subclasses the repository's camera-authoritative task node.  It
keeps finder, profile, keyframe, IK, safe-region, Pico, cancellation and camera
reset contracts, but replaces the final base-alignment policy with one short
SE(2) macro per fresh observation.
"""

from __future__ import annotations

from dataclasses import replace
import math
import time
from typing import Any, Dict, Mapping, Optional

import rclpy

from .alignment_core import alignment_errors, observation_constraint_decision
from .camera_authoritative_task_node import CameraAuthoritativeTaskNode
from .camera_pose_relocation import MotionPrimitive, RelocationPlan, RelativeRobotPose
from .joint_pose_controller import (
    JointPoseConfig,
    JointPoseDecision,
    ObjectPoseState,
    ObjectPoseTarget,
    Primitive,
    bearing_error_deg,
    fuse_axial_orientation_error,
    goal_error,
    representative_primitive,
    select_joint_pose_plan,
    sequence_net_yaw_deg,
    sequence_total_translation_m,
    states_near,
    wrap_axial_deg,
)
from .precision_docking import precision_errors
from .resilient_object_task_node import ResilientObjectTaskNode


class JointPoseTaskNode(CameraAuthoritativeTaskNode):
    """Camera-reset controller using atomic axis-coupled local macros."""

    def __init__(self) -> None:
        # Parent constructors dynamically dispatch status/reset methods.  Define
        # every field used by an override before calling ``super``.
        self.joint_pose_previous_primitive: Optional[Primitive] = None
        self.joint_pose_recent_states: list[ObjectPoseState] = []
        self.joint_pose_pending_prediction: Optional[ObjectPoseState] = None
        self.joint_pose_pending_start: Optional[ObjectPoseState] = None
        self.joint_pose_pending_sequence: tuple[Primitive, ...] = ()
        self.joint_pose_pending_raw_orientation_start: Optional[float] = None
        self.joint_pose_pending_orientation_effective = False
        self.joint_pose_orientation_estimate_deg: Optional[float] = None
        self.joint_pose_stall_count = 0
        self.joint_pose_hold_count = 0
        self.joint_pose_last_model_check: Dict[str, object] = {}
        self.joint_pose_last_orientation_filter: Dict[str, object] = {}
        self.joint_pose_last_decision: Dict[str, object] = {}
        self.joint_pose_reverse_requested = False
        self.joint_pose_reverse_authorized = False
        super().__init__()
        self.pose_relocation_stage = "joint_pose"
        self._publish_status(
            "joint_pose_controller_ready",
            controller="axis_coupled_atomic_macro_v3",
            target_semantics=(
                "recreate_taught_object_point_and_taught_axial_orientation"
            ),
            final_axis_corridor_used=True,
            independent_bearing_orientation_loops=False,
            straight_retreat_orientation_credit=False,
            camera_observation_between_macro_primitives=False,
            camera_reset_after_each_selected_macro=True,
            reverse_requires_explicit_rear_clearance_ack=True,
        )
        self.get_logger().info(
            "Axis-coupled joint pose controller ready: each fresh RGB-D state "
            "selects one bounded DRIVE_REL or TURN-MOVE-TURN macro"
        )

    # ------------------------------------------------------------------
    # Parameters and status
    # ------------------------------------------------------------------

    def _declare_parameters(self) -> None:
        super()._declare_parameters()
        defaults: Dict[str, Any] = {
            "joint_pose_controller_enabled": True,
            # Reverse may be kinematically necessary for a small local lateral
            # shift.  It remains physically disabled without operator ACK because
            # the current platform has no rear depth-clearance sensor.
            "joint_pose_allow_reverse": True,
            "joint_pose_rear_clearance_ack": False,
            "joint_pose_drive_enabled": True,
            "joint_pose_position_only_when_orientation_unreliable": True,
            "joint_pose_maximum_move_step_m": 0.018,
            "joint_pose_maximum_reverse_step_m": 0.012,
            "joint_pose_maximum_turn_step_deg": 8.0,
            "joint_pose_maximum_drive_yaw_deg": 6.0,
            "joint_pose_minimum_move_step_m": 0.003,
            "joint_pose_minimum_turn_step_deg": 0.5,
            "joint_pose_turn_action_levels": 3,
            "joint_pose_move_action_levels": 3,
            "joint_pose_minimum_object_range_m": 0.10,
            "joint_pose_maximum_object_range_m": 0.80,
            "joint_pose_minimum_object_forward_m": 0.04,
            "joint_pose_maximum_predicted_bearing_deg": 48.0,
            "joint_pose_path_sample_count": 9,
            # Axis-corridor and coupled macro synthesis.
            "joint_pose_axis_corridor_tolerance_m": 0.008,
            "joint_pose_axis_turn_position_gate_m": 0.014,
            "joint_pose_axis_straight_heading_gate_deg": 5.0,
            "joint_pose_axis_cross_track_weight": 2.8,
            "joint_pose_axis_heading_weight": 1.6,
            "joint_pose_axis_along_weight": 1.0,
            "joint_pose_maximum_steering_turn_deg": 16.0,
            "joint_pose_maximum_heading_step_deg": 8.0,
            "joint_pose_minimum_coupled_steering_deg": 1.0,
            "joint_pose_minimum_drive_radius_m": 0.09,
            "joint_pose_minimum_drive_yaw_deg": 0.45,
            "joint_pose_drive_yaw_levels": 3,
            "joint_pose_macro_action_cost": 0.03,
            "joint_pose_dogleg_cost_penalty": 0.03,
            "joint_pose_minimum_macro_improvement": 0.04,
            "joint_pose_maximum_cross_track_regression_m": 0.006,
            "joint_pose_maximum_heading_regression_deg": 8.0,
            # Translation-invariant object-axis fusion.
            "joint_pose_orientation_translation_measurement_gain": 0.03,
            "joint_pose_orientation_stationary_measurement_gain": 0.20,
            "joint_pose_orientation_turn_measurement_gain": 0.45,
            "joint_pose_orientation_translation_innovation_limit_deg": 1.0,
            "joint_pose_orientation_turn_innovation_limit_deg": 12.0,
            "joint_pose_orientation_motion_yaw_epsilon_deg": 0.25,
            # v2-compatible names retained for launch/YAML continuity.
            "joint_pose_position_resolution_m": 0.004,
            "joint_pose_orientation_resolution_deg": 2.0,
            "joint_pose_search_maximum_expansions": 25000,
            "joint_pose_search_maximum_wall_time_sec": 0.12,
            "joint_pose_search_maximum_depth": 3,
            "joint_pose_search_maximum_translation_m": 0.06,
            "joint_pose_search_maximum_turn_deg": 60.0,
            "joint_pose_heuristic_weight": 1.0,
            # Maximum primitive count inside one camera-atomic macro.
            "joint_pose_execution_prefix_length": 3,
            "joint_pose_action_cost": 0.0,
            "joint_pose_motion_cost_weight": 0.04,
            "joint_pose_reverse_cost_penalty": 0.20,
            "joint_pose_drive_cost_penalty": 0.0,
            "joint_pose_action_family_change_penalty": 0.03,
            "joint_pose_immediate_reversal_penalty": 0.50,
            "joint_pose_same_direction_bonus": 0.02,
            "joint_pose_recent_cycle_penalty": 4.0,
            "joint_pose_hard_reject_recent_cycle": True,
            "joint_pose_cycle_position_radius_m": 0.010,
            "joint_pose_cycle_orientation_radius_deg": 5.0,
            "joint_pose_cycle_required_cost_improvement": 0.20,
            "joint_pose_minimum_frontier_improvement": 0.04,
            "joint_pose_top_candidate_count": 8,
            "joint_pose_route_preview_count": 8,
            "joint_pose_history_size": 8,
            "joint_pose_hold_reobserve_sec": 0.30,
            "joint_pose_hold_limit": 8,
            "joint_pose_stall_limit": 5,
            "joint_pose_stall_step_shrink": 0.80,
            "joint_pose_minimum_step_scale": 0.35,
            "joint_pose_model_position_residual_tolerance_m": 0.018,
            "joint_pose_model_orientation_residual_tolerance_deg": 8.0,
            "joint_pose_minimum_observed_position_change_m": 0.0015,
            "joint_pose_minimum_observed_orientation_change_deg": 0.5,
        }
        for name, value in defaults.items():
            self.declare_parameter(name, value)

    def _status_payload(
        self,
        event: str,
        ok: bool,
        details: Mapping[str, Any],
    ) -> Dict[str, Any]:
        payload = super()._status_payload(event, ok, details)
        payload.update(
            {
                "joint_pose_controller": True,
                "joint_pose_controller_version": "axis_coupled_atomic_macro_v3",
                "joint_pose_stall_count": self.joint_pose_stall_count,
                "joint_pose_hold_count": self.joint_pose_hold_count,
                "joint_pose_reverse_requested": self.joint_pose_reverse_requested,
                "joint_pose_reverse_authorized": self.joint_pose_reverse_authorized,
                "joint_pose_last_model_check": dict(
                    self.joint_pose_last_model_check
                ),
                "joint_pose_last_orientation_filter": dict(
                    self.joint_pose_last_orientation_filter
                ),
                "joint_pose_last_decision": dict(self.joint_pose_last_decision),
            }
        )
        return payload

    def _reset_joint_pose_state(self) -> None:
        self.joint_pose_previous_primitive = None
        self.joint_pose_recent_states = []
        self.joint_pose_pending_prediction = None
        self.joint_pose_pending_start = None
        self.joint_pose_pending_sequence = ()
        self.joint_pose_pending_raw_orientation_start = None
        self.joint_pose_pending_orientation_effective = False
        self.joint_pose_orientation_estimate_deg = None
        self.joint_pose_stall_count = 0
        self.joint_pose_hold_count = 0
        self.joint_pose_last_model_check = {}
        self.joint_pose_last_orientation_filter = {}
        self.joint_pose_last_decision = {}
        self.joint_pose_reverse_requested = False
        self.joint_pose_reverse_authorized = False

    def _reset_action_state(self) -> None:
        super()._reset_action_state()
        self._reset_joint_pose_state()
        self.pose_relocation_stage = "joint_pose"

    def _begin_visual_approach(self, stable) -> None:
        super()._begin_visual_approach(stable)
        self._reset_joint_pose_state()
        self.pose_relocation_stage = "joint_pose"
        assert self.profile is not None
        self._publish_status(
            "joint_pose_docking_started",
            reference_point_base=list(
                self.profile.alignment.reference_point_base
            ),
            controller="axis_coupled_atomic_macro_v3",
        )

    def _joint_pose_config(self) -> JointPoseConfig:
        parameter = self.get_parameter
        reverse_requested = bool(parameter("joint_pose_allow_reverse").value)
        rear_ack = bool(parameter("joint_pose_rear_clearance_ack").value)
        self.joint_pose_reverse_requested = reverse_requested
        self.joint_pose_reverse_authorized = reverse_requested and rear_ack
        return JointPoseConfig(
            forward_tolerance_m=float(
                parameter("precision_forward_tolerance_m").value
            ),
            lateral_tolerance_m=float(
                parameter("precision_lateral_tolerance_m").value
            ),
            bearing_tolerance_deg=float(
                parameter("precision_bearing_tolerance_deg").value
            ),
            orientation_tolerance_deg=float(
                parameter("precision_orientation_tolerance_deg").value
            ),
            minimum_orientation_quality=float(
                parameter("precision_orientation_min_quality").value
            ),
            maximum_move_step_m=float(
                parameter("joint_pose_maximum_move_step_m").value
            ),
            maximum_reverse_step_m=float(
                parameter("joint_pose_maximum_reverse_step_m").value
            ),
            maximum_turn_step_deg=float(
                parameter("joint_pose_maximum_turn_step_deg").value
            ),
            maximum_drive_yaw_deg=float(
                parameter("joint_pose_maximum_drive_yaw_deg").value
            ),
            minimum_move_step_m=float(
                parameter("joint_pose_minimum_move_step_m").value
            ),
            minimum_turn_step_deg=float(
                parameter("joint_pose_minimum_turn_step_deg").value
            ),
            turn_action_levels=int(
                parameter("joint_pose_turn_action_levels").value
            ),
            move_action_levels=int(
                parameter("joint_pose_move_action_levels").value
            ),
            minimum_object_range_m=float(
                parameter("joint_pose_minimum_object_range_m").value
            ),
            maximum_object_range_m=float(
                parameter("joint_pose_maximum_object_range_m").value
            ),
            minimum_object_forward_m=float(
                parameter("joint_pose_minimum_object_forward_m").value
            ),
            maximum_predicted_bearing_deg=float(
                parameter("joint_pose_maximum_predicted_bearing_deg").value
            ),
            path_sample_count=int(
                parameter("joint_pose_path_sample_count").value
            ),
            allow_reverse=self.joint_pose_reverse_authorized,
            drive_enabled=bool(parameter("joint_pose_drive_enabled").value),
            position_only_when_orientation_unreliable=bool(
                parameter(
                    "joint_pose_position_only_when_orientation_unreliable"
                ).value
            ),
            axis_corridor_tolerance_m=float(
                parameter("joint_pose_axis_corridor_tolerance_m").value
            ),
            axis_turn_position_gate_m=float(
                parameter("joint_pose_axis_turn_position_gate_m").value
            ),
            axis_straight_heading_gate_deg=float(
                parameter("joint_pose_axis_straight_heading_gate_deg").value
            ),
            axis_cross_track_weight=float(
                parameter("joint_pose_axis_cross_track_weight").value
            ),
            axis_heading_weight=float(
                parameter("joint_pose_axis_heading_weight").value
            ),
            axis_along_weight=float(
                parameter("joint_pose_axis_along_weight").value
            ),
            maximum_steering_turn_deg=float(
                parameter("joint_pose_maximum_steering_turn_deg").value
            ),
            maximum_heading_step_deg=float(
                parameter("joint_pose_maximum_heading_step_deg").value
            ),
            minimum_coupled_steering_deg=float(
                parameter("joint_pose_minimum_coupled_steering_deg").value
            ),
            minimum_drive_radius_m=float(
                parameter("joint_pose_minimum_drive_radius_m").value
            ),
            minimum_drive_yaw_deg=float(
                parameter("joint_pose_minimum_drive_yaw_deg").value
            ),
            drive_yaw_levels=int(
                parameter("joint_pose_drive_yaw_levels").value
            ),
            macro_action_cost=float(
                parameter("joint_pose_macro_action_cost").value
            ),
            dogleg_cost_penalty=float(
                parameter("joint_pose_dogleg_cost_penalty").value
            ),
            minimum_macro_improvement=float(
                parameter("joint_pose_minimum_macro_improvement").value
            ),
            maximum_cross_track_regression_m=float(
                parameter("joint_pose_maximum_cross_track_regression_m").value
            ),
            maximum_heading_regression_deg=float(
                parameter("joint_pose_maximum_heading_regression_deg").value
            ),
            orientation_translation_measurement_gain=float(
                parameter(
                    "joint_pose_orientation_translation_measurement_gain"
                ).value
            ),
            orientation_stationary_measurement_gain=float(
                parameter(
                    "joint_pose_orientation_stationary_measurement_gain"
                ).value
            ),
            orientation_turn_measurement_gain=float(
                parameter("joint_pose_orientation_turn_measurement_gain").value
            ),
            orientation_translation_innovation_limit_deg=float(
                parameter(
                    "joint_pose_orientation_translation_innovation_limit_deg"
                ).value
            ),
            orientation_turn_innovation_limit_deg=float(
                parameter(
                    "joint_pose_orientation_turn_innovation_limit_deg"
                ).value
            ),
            orientation_motion_yaw_epsilon_deg=float(
                parameter(
                    "joint_pose_orientation_motion_yaw_epsilon_deg"
                ).value
            ),
            position_resolution_m=float(
                parameter("joint_pose_position_resolution_m").value
            ),
            orientation_resolution_deg=float(
                parameter("joint_pose_orientation_resolution_deg").value
            ),
            search_maximum_expansions=int(
                parameter("joint_pose_search_maximum_expansions").value
            ),
            search_maximum_wall_time_sec=float(
                parameter("joint_pose_search_maximum_wall_time_sec").value
            ),
            search_maximum_depth=int(
                parameter("joint_pose_search_maximum_depth").value
            ),
            search_maximum_translation_m=float(
                parameter("joint_pose_search_maximum_translation_m").value
            ),
            search_maximum_turn_deg=float(
                parameter("joint_pose_search_maximum_turn_deg").value
            ),
            heuristic_weight=float(
                parameter("joint_pose_heuristic_weight").value
            ),
            execution_prefix_length=int(
                parameter("joint_pose_execution_prefix_length").value
            ),
            action_cost=float(parameter("joint_pose_action_cost").value),
            motion_cost_weight=float(
                parameter("joint_pose_motion_cost_weight").value
            ),
            reverse_cost_penalty=float(
                parameter("joint_pose_reverse_cost_penalty").value
            ),
            drive_cost_penalty=float(
                parameter("joint_pose_drive_cost_penalty").value
            ),
            action_family_change_penalty=float(
                parameter("joint_pose_action_family_change_penalty").value
            ),
            immediate_reversal_penalty=float(
                parameter("joint_pose_immediate_reversal_penalty").value
            ),
            same_direction_bonus=float(
                parameter("joint_pose_same_direction_bonus").value
            ),
            recent_cycle_penalty=float(
                parameter("joint_pose_recent_cycle_penalty").value
            ),
            hard_reject_recent_cycle=bool(
                parameter("joint_pose_hard_reject_recent_cycle").value
            ),
            cycle_position_radius_m=float(
                parameter("joint_pose_cycle_position_radius_m").value
            ),
            cycle_orientation_radius_deg=float(
                parameter("joint_pose_cycle_orientation_radius_deg").value
            ),
            cycle_required_cost_improvement=float(
                parameter(
                    "joint_pose_cycle_required_cost_improvement"
                ).value
            ),
            minimum_frontier_improvement=float(
                parameter("joint_pose_minimum_frontier_improvement").value
            ),
            top_candidate_count=int(
                parameter("joint_pose_top_candidate_count").value
            ),
        )

    # ------------------------------------------------------------------
    # Camera-reset model monitoring and cycle history
    # ------------------------------------------------------------------

    def _append_recent_state(self, state: ObjectPoseState) -> None:
        self.joint_pose_recent_states.append(state)
        maximum = max(2, int(self.get_parameter("joint_pose_history_size").value))
        if len(self.joint_pose_recent_states) > maximum:
            del self.joint_pose_recent_states[:-maximum]

    def _record_model_residual(
        self,
        state: ObjectPoseState,
        target: ObjectPoseTarget,
        config: JointPoseConfig,
        *,
        raw_orientation_error_deg: float,
    ) -> None:
        predicted = self.joint_pose_pending_prediction
        start = self.joint_pose_pending_start
        sequence = self.joint_pose_pending_sequence
        if predicted is None or start is None or not sequence:
            return

        net_yaw = sequence_net_yaw_deg(sequence)
        position_residual = math.hypot(
            state.forward_m - predicted.forward_m,
            state.lateral_m - predicted.lateral_m,
        )
        filtered_orientation_residual = abs(
            wrap_axial_deg(
                state.orientation_error_deg - predicted.orientation_error_deg
            )
        )
        predicted_position_change = math.hypot(
            predicted.forward_m - start.forward_m,
            predicted.lateral_m - start.lateral_m,
        )
        observed_position_change = math.hypot(
            state.forward_m - start.forward_m,
            state.lateral_m - start.lateral_m,
        )

        raw_start = self.joint_pose_pending_raw_orientation_start
        raw_expected = (
            predicted.orientation_error_deg
            if raw_start is None
            else wrap_axial_deg(raw_start - net_yaw)
        )
        raw_orientation_residual = abs(
            wrap_axial_deg(raw_orientation_error_deg - raw_expected)
        )
        observed_raw_orientation_change = (
            0.0
            if raw_start is None
            else abs(wrap_axial_deg(raw_orientation_error_deg - raw_start))
        )
        predicted_orientation_change = abs(net_yaw)

        position_tolerance = float(
            self.get_parameter(
                "joint_pose_model_position_residual_tolerance_m"
            ).value
        )
        orientation_tolerance = float(
            self.get_parameter(
                "joint_pose_model_orientation_residual_tolerance_deg"
            ).value
        )
        minimum_position_change = float(
            self.get_parameter(
                "joint_pose_minimum_observed_position_change_m"
            ).value
        )
        minimum_orientation_change = float(
            self.get_parameter(
                "joint_pose_minimum_observed_orientation_change_deg"
            ).value
        )
        missing_position_motion = (
            predicted_position_change >= 2.0 * minimum_position_change
            and observed_position_change < minimum_position_change
        )
        current_orientation_effective = bool(
            self.joint_pose_pending_orientation_effective
            and state.orientation_reliable
            and state.orientation_quality >= config.minimum_orientation_quality
        )
        orientation_residual_used = bool(
            current_orientation_effective
            and abs(net_yaw) > config.orientation_motion_yaw_epsilon_deg
        )
        missing_orientation_motion = bool(
            orientation_residual_used
            and predicted_orientation_change >= 2.0 * minimum_orientation_change
            and observed_raw_orientation_change < minimum_orientation_change
        )
        cycle_return = any(
            states_near(
                state,
                recent,
                config,
                orientation_required=current_orientation_effective,
            )
            for recent in self.joint_pose_recent_states[:-1]
        )
        residual_bad = bool(
            position_residual > position_tolerance
            or (
                orientation_residual_used
                and raw_orientation_residual > orientation_tolerance
            )
            or missing_position_motion
            or missing_orientation_motion
            or cycle_return
        )
        if residual_bad:
            self.joint_pose_stall_count += 1
        else:
            self.joint_pose_stall_count = max(0, self.joint_pose_stall_count - 1)

        self.joint_pose_last_model_check = {
            "sequence": [item.to_mapping() for item in sequence],
            "net_yaw_deg": net_yaw,
            "predicted_state": predicted.to_mapping(),
            "observed_state": state.to_mapping(),
            "raw_orientation_error_deg": raw_orientation_error_deg,
            "raw_expected_orientation_error_deg": raw_expected,
            "position_residual_m": position_residual,
            "filtered_orientation_residual_deg": filtered_orientation_residual,
            "raw_orientation_residual_deg": raw_orientation_residual,
            "predicted_position_change_m": predicted_position_change,
            "observed_position_change_m": observed_position_change,
            "predicted_orientation_change_deg": predicted_orientation_change,
            "observed_raw_orientation_change_deg": observed_raw_orientation_change,
            "orientation_residual_used": orientation_residual_used,
            "translation_only_orientation_innovation_ignored": bool(
                current_orientation_effective and not orientation_residual_used
            ),
            "missing_position_motion": missing_position_motion,
            "missing_orientation_motion": missing_orientation_motion,
            "measured_cycle_return": cycle_return,
            "residual_bad": residual_bad,
            "stall_count": self.joint_pose_stall_count,
            "current_joint_error": goal_error(
                state,
                target,
                config,
                orientation_required=(
                    self.joint_pose_pending_orientation_effective
                ),
            ),
        }
        self._publish_status(
            "joint_pose_motion_model_checked",
            **self.joint_pose_last_model_check,
        )
        self.joint_pose_pending_prediction = None
        self.joint_pose_pending_start = None
        self.joint_pose_pending_sequence = ()
        self.joint_pose_pending_raw_orientation_start = None
        self.joint_pose_pending_orientation_effective = False

    # ------------------------------------------------------------------
    # Motion integration
    # ------------------------------------------------------------------

    @staticmethod
    def _to_motion_primitive(primitive: Primitive) -> MotionPrimitive:
        return MotionPrimitive(
            primitive.kind,
            float(primitive.amount),
            float(primitive.yaw_deg),
        )

    def _start_joint_pose_plan(
        self,
        *,
        decision: JointPoseDecision,
        state: ObjectPoseState,
        target: ObjectPoseTarget,
        raw_orientation_error_deg: float,
    ) -> bool:
        if not decision.sequence:
            return False
        maximum_primitives = int(
            self.get_parameter("joint_pose_execution_prefix_length").value
        )
        if len(decision.sequence) > maximum_primitives:
            self._enter_recovery_hold(
                "JOINT_POSE_MACRO_TOO_LONG",
                "selected macro exceeds configured primitive-count bound",
                resume_mode="manual",
                primitive_count=len(decision.sequence),
                maximum_primitives=maximum_primitives,
            )
            return False

        motion = tuple(
            self._to_motion_primitive(item) for item in decision.sequence
        )
        current_range = state.planar_range_m
        reference_range = target.planar_range_m
        progress = 0.0
        if decision.current_cost > 1e-9:
            progress = max(
                0.0,
                min(1.0, decision.expected_improvement / decision.current_cost),
            )
        plan = RelocationPlan(
            stage="joint_pose",
            reached=False,
            reason=decision.reason,
            current_point=(state.forward_m, state.lateral_m),
            desired_point=(
                decision.predicted_state.forward_m,
                decision.predicted_state.lateral_m,
            ),
            anchor_range_m=current_range,
            orientation_error_deg=state.orientation_error_deg,
            bearing_error_deg=bearing_error_deg(state, target),
            range_error_m=current_range - reference_range,
            forward_error_m=state.forward_m - target.forward_m,
            lateral_error_m=state.lateral_m - target.lateral_m,
            progress=progress,
            robot_target=RelativeRobotPose(
                decision.robot_goal.x_m,
                decision.robot_goal.y_m,
                decision.robot_goal.yaw_deg,
            ),
            primitives=motion,
            predicted_minimum_object_range_m=(
                decision.predicted_minimum_range_m
            ),
            decomposition=(
                "axis_coupled_atomic_macro:" + decision.maneuver_type
            ),
        )
        self.pose_relocation_stage = "joint_pose"
        iteration_before = self.pose_relocation_iteration
        self._start_pose_relocation(plan)
        started = self.pose_relocation_iteration > iteration_before
        if not started:
            return False

        # In inherited dry-run mode no physical transform occurs. Do not let
        # an unexecuted macro affect either the motion model or reversal
        # hysteresis on the next unchanged camera frame.
        if not self.dry_run_base:
            self.joint_pose_previous_primitive = representative_primitive(
                decision.sequence
            )
            self.joint_pose_pending_prediction = decision.predicted_state
            self.joint_pose_pending_start = state
            self.joint_pose_pending_sequence = tuple(decision.sequence)
            self.joint_pose_pending_raw_orientation_start = (
                raw_orientation_error_deg
            )
            self.joint_pose_pending_orientation_effective = (
                decision.orientation_effective
            )
        else:
            self.joint_pose_previous_primitive = None
            self.joint_pose_pending_prediction = None
            self.joint_pose_pending_start = None
            self.joint_pose_pending_sequence = ()
            self.joint_pose_pending_raw_orientation_start = None
            self.joint_pose_pending_orientation_effective = False
        self.joint_pose_hold_count = 0
        return True

    # ------------------------------------------------------------------
    # Joint position-orientation alignment policy
    # ------------------------------------------------------------------

    def _try_alignment_step(self) -> None:
        if not bool(self.get_parameter("joint_pose_controller_enabled").value):
            super()._try_alignment_step()
            return
        if self.profile is None or self.pose_relocation_active or self.base_active:
            return

        now = time.monotonic()
        stable = self._stable_detection()
        if stable is None and self.cached_stable_detection is not None:
            stable = self.cached_stable_detection
            self.cached_stable_detection = None
        if stable is None:
            if now < self.reobserve_not_before:
                return
            if self.last_visual_wall_sec <= 0.0 or (
                time.time() - self.last_visual_wall_sec
                > float(self.get_parameter("visual_lost_timeout_sec").value)
            ):
                self._restart_full_search(
                    "visual target lost during joint pose control"
                )
            return

        # Validate point/depth quality without rejecting a temporarily weak
        # orientation.  Position-only approach remains available, followed by a
        # stationary hold until the axis estimate is trustworthy.
        point_only_profile = replace(
            self.profile.alignment,
            require_orientation_match=False,
        )
        constraint = observation_constraint_decision(
            point_only_profile,
            localization_quality=stable.localization_quality,
            depth_std_m=stable.depth_std_m,
            center_std_px=stable.center_std_px,
            orientation_deg=stable.orientation_deg,
            orientation_class=stable.orientation_class,
            orientation_quality=stable.orientation_quality,
        )
        if constraint.action == "reject":
            self.filter.clear()
            self._publish_status(
                "joint_pose_observation_rejected",
                reason=constraint.reason,
                policy="hold_stationary_and_wait_for_fresh_visual_sample",
            )
            return

        self._update_visual_anchor(stable)
        self.filter.clear()
        point = stable.point_base
        self.last_object_point = point
        try:
            errors = alignment_errors(
                point,
                self.profile.alignment.reference_point_base,
                forward_axis_sign=self.forward_axis_sign,
                lateral_axis_sign=self.lateral_axis_sign,
            )
        except Exception as error:
            self._enter_recovery_hold(
                "TARGET_POSE_INVALID",
                str(error),
                resume_mode="search",
            )
            return
        self.last_errors = errors
        precise = precision_errors(errors)
        if errors.current.forward_m <= 0.0:
            self._restart_full_search("object_not_in_front_half_plane")
            return
        if abs(errors.height_error_m) > self.profile.alignment.height_tolerance_m:
            self._enter_recovery_hold(
                "TARGET_POSE_NOT_CORRECTABLE",
                "height_error_not_correctable_by_planar_base",
                resume_mode="manual",
                height_error_m=errors.height_error_m,
            )
            return

        try:
            config = self._joint_pose_config()
            config.validate()
        except Exception as error:
            self._enter_recovery_hold(
                "JOINT_POSE_CONFIGURATION_INVALID",
                str(error),
                resume_mode="manual",
            )
            return

        # Ask the profile-owning resilient base whether teaching actually stored
        # an orientation constraint.  Do not let the old coarse distance gate
        # temporarily turn that constraint off.
        orientation_required = ResilientObjectTaskNode._orientation_required(self)
        assessment = (
            self._orientation_assessment(stable)
            if orientation_required
            else None
        )
        raw_orientation_error = (
            0.0 if assessment is None else assessment.signed_error_deg
        )
        orientation_quality = (
            1.0 if assessment is None else assessment.quality
        )
        orientation_reliable = (
            assessment is None or assessment.state != "quality_low"
        )

        pending = self.joint_pose_pending_sequence
        expected_yaw = sequence_net_yaw_deg(pending) if pending else 0.0
        translated = sequence_total_translation_m(pending) if pending else 0.0
        motion_kind: Optional[str]
        if pending and abs(expected_yaw) > config.orientation_motion_yaw_epsilon_deg:
            motion_kind = "yaw_macro"
        elif pending and translated > 0.0:
            motion_kind = "zero_net_yaw_macro"
        elif pending:
            motion_kind = "stationary"
        else:
            motion_kind = None

        if orientation_required:
            filtered = fuse_axial_orientation_error(
                previous_error_deg=self.joint_pose_orientation_estimate_deg,
                measured_error_deg=raw_orientation_error,
                measurement_quality=orientation_quality,
                expected_robot_yaw_deg=expected_yaw,
                motion_kind=motion_kind,
                config=config,
            )
            orientation_error = filtered.filtered_error_deg
            self.joint_pose_orientation_estimate_deg = orientation_error
            self.joint_pose_last_orientation_filter = filtered.to_mapping()
        else:
            orientation_error = 0.0
            self.joint_pose_orientation_estimate_deg = None
            self.joint_pose_last_orientation_filter = {
                "mode": "orientation_not_required",
                "raw_error_deg": 0.0,
                "filtered_error_deg": 0.0,
            }

        if assessment is not None:
            self.orientation_last_assessment = {
                "state": assessment.state,
                "raw_signed_error_deg": assessment.signed_error_deg,
                "filtered_signed_error_deg": orientation_error,
                "absolute_error_deg": abs(orientation_error),
                "quality": assessment.quality,
                "cost": assessment.cost,
                "comparison_mode": assessment.comparison_mode,
                "reason": assessment.reason,
                "axis_filter": dict(self.joint_pose_last_orientation_filter),
            }

        state = ObjectPoseState(
            errors.current.forward_m,
            errors.current.lateral_m,
            orientation_error,
            orientation_quality,
            orientation_reliable,
        )
        target = ObjectPoseTarget(
            errors.reference.forward_m,
            errors.reference.lateral_m,
        )

        # Residual checking happens after orientation fusion.  Raw orientation is
        # nevertheless used for actual-yaw fault detection; zero-net translation
        # macros receive no false orientation credit or penalty.
        self._record_model_residual(
            state,
            target,
            config,
            raw_orientation_error_deg=raw_orientation_error,
        )
        stall_limit = max(
            1,
            int(self.get_parameter("joint_pose_stall_limit").value),
        )
        if self.joint_pose_stall_count >= stall_limit:
            self._enter_recovery_hold(
                "JOINT_POSE_MOTION_MODEL_MISMATCH",
                "fresh camera state repeatedly disagreed with commanded local macro",
                resume_mode="align",
                stall_count=self.joint_pose_stall_count,
                model_check=dict(self.joint_pose_last_model_check),
            )
            return

        shrink = max(
            0.10,
            min(
                1.0,
                float(
                    self.get_parameter("joint_pose_stall_step_shrink").value
                ),
            ),
        )
        minimum_scale = max(
            0.10,
            min(
                1.0,
                float(
                    self.get_parameter("joint_pose_minimum_step_scale").value
                ),
            ),
        )
        step_scale = max(
            minimum_scale,
            shrink ** self.joint_pose_stall_count,
        )
        history = tuple(self.joint_pose_recent_states)
        try:
            decision = select_joint_pose_plan(
                state,
                target,
                config,
                orientation_required=orientation_required,
                previous_primitive=self.joint_pose_previous_primitive,
                recent_states=history,
                step_scale=step_scale,
            )
        except Exception as error:
            self._enter_recovery_hold(
                "JOINT_POSE_PLANNER_FAILED",
                str(error),
                resume_mode="align",
            )
            return
        self._append_recent_state(state)

        preview_count = max(
            1,
            int(self.get_parameter("joint_pose_route_preview_count").value),
        )
        route_preview = decision.route_preview[:preview_count]
        self.joint_pose_last_decision = {
            "reason": decision.reason,
            "maneuver_type": decision.maneuver_type,
            "current_cost": decision.current_cost,
            "planned_terminal_cost": decision.planned_terminal_cost,
            "expected_improvement": decision.expected_improvement,
            "candidate_count": decision.search_expansions,
            "terminal_reaches_goal": decision.search_reached_goal,
            "orientation_required": decision.orientation_required,
            "orientation_effective": decision.orientation_effective,
            "robot_goal": decision.robot_goal.to_mapping(),
            "current_axis_error": decision.current_axis_error.to_mapping(),
            "terminal_axis_error": decision.terminal_axis_error.to_mapping(),
            "sequence": [item.to_mapping() for item in decision.sequence],
            "route_preview": [item.to_mapping() for item in route_preview],
            "macro_primitive_count": len(decision.sequence),
        }
        self._publish_status(
            "joint_pose_camera_comparison",
            current_object_pose=state.to_mapping(),
            taught_object_pose=target.to_mapping(),
            raw_orientation_error_deg=raw_orientation_error,
            filtered_orientation_error_deg=orientation_error,
            orientation_filter=dict(self.joint_pose_last_orientation_filter),
            precision_errors={
                "bearing_error_deg": precise.bearing_error_deg,
                "forward_error_m": precise.forward_error_m,
                "lateral_error_m": precise.lateral_error_m,
                "range_error_m": precise.range_error_m,
                "planar_position_error_m": precise.planar_position_error_m,
            },
            robot_relative_goal=decision.robot_goal.to_mapping(),
            current_axis_error=decision.current_axis_error.to_mapping(),
            terminal_axis_error=decision.terminal_axis_error.to_mapping(),
            current_cost=decision.current_cost,
            planned_terminal_cost=decision.planned_terminal_cost,
            expected_improvement=decision.expected_improvement,
            maneuver_type=decision.maneuver_type,
            selected_sequence=[
                item.to_mapping() for item in decision.sequence
            ],
            macro_primitive_count=len(decision.sequence),
            camera_observation_between_macro_primitives=False,
            camera_reset_after_macro=True,
            route_preview=[item.to_mapping() for item in route_preview],
            candidate_count=decision.search_expansions,
            terminal_reaches_goal=decision.search_reached_goal,
            top_candidates=[
                item.to_mapping() for item in decision.top_candidates
            ],
            step_scale=step_scale,
            reverse_requested=self.joint_pose_reverse_requested,
            reverse_authorized=self.joint_pose_reverse_authorized,
            rear_clearance_sensor_available=False,
            legacy_sequential_controller_used=False,
        )

        if decision.aligned:
            self.joint_pose_hold_count = 0
            self.aligned_confirmations += 1
            required = max(
                2,
                int(self.get_parameter("precision_confirmation_count").value),
            )
            if self.aligned_confirmations >= required:
                self._alignment_complete()
            return

        self.aligned_confirmations = 0
        if decision.hold:
            self.joint_pose_hold_count += 1
            self.reobserve_not_before = time.monotonic() + max(
                0.0,
                float(
                    self.get_parameter("joint_pose_hold_reobserve_sec").value
                ),
            )
            hold_limit = max(
                1,
                int(self.get_parameter("joint_pose_hold_limit").value),
            )
            reverse_clearance_required = (
                decision.reason
                == "joint_pose_local_axis_shift_requires_reverse_clearance"
            )
            self._publish_status(
                "joint_pose_holding_for_reobservation",
                hold_count=self.joint_pose_hold_count,
                hold_limit=hold_limit,
                reason=decision.reason,
                orientation_reliable=orientation_reliable,
                reverse_requested=self.joint_pose_reverse_requested,
                reverse_authorized=self.joint_pose_reverse_authorized,
                operator_hint=(
                    "physically verify the rear corridor, then set "
                    "joint_pose_rear_clearance_ack=true"
                    if reverse_clearance_required
                    else "none"
                ),
            )
            if self.joint_pose_hold_count >= hold_limit:
                self._enter_recovery_hold(
                    "JOINT_POSE_STALLED",
                    "no safe bounded axis-coupled local macro was found",
                    resume_mode="align",
                    planner_reason=decision.reason,
                    reverse_requested=self.joint_pose_reverse_requested,
                    reverse_authorized=self.joint_pose_reverse_authorized,
                    rear_clearance_sensor_available=False,
                    orientation_reliable=orientation_reliable,
                )
            return

        if self.alignment_iterations > self.profile.alignment.max_iterations:
            self._publish_status(
                "joint_pose_soft_iteration_limit_recycled",
                previous_iterations=self.alignment_iterations,
                policy="continue_with_fresh_camera_macro_replanning",
            )
            self.alignment_iterations = 0
        started = self._start_joint_pose_plan(
            decision=decision,
            state=state,
            target=target,
            raw_orientation_error_deg=raw_orientation_error,
        )
        if not started:
            self._publish_status(
                "joint_pose_selected_motion_not_started",
                reason="inherited motion or depth-clearance gate rejected macro",
                selected_sequence=[
                    item.to_mapping() for item in decision.sequence
                ],
            )


def main(args=None) -> None:
    rclpy.init(args=args)
    node = JointPoseTaskNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
