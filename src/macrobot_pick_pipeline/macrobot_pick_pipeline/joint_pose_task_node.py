"""ROS 2 integration for the MacRobot joint camera-relative pose planner.

This executable subclasses the current camera-authoritative task node.  It keeps
all existing finder, profile, keyframe, IK, safe-region, Pico and cancellation
contracts, but replaces only the final base-alignment decision policy.
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
    goal_error,
    select_joint_pose_plan,
    states_near,
    wrap_axial_deg,
)
from .precision_docking import precision_errors
from .resilient_object_task_node import ResilientObjectTaskNode


class JointPoseTaskNode(CameraAuthoritativeTaskNode):
    """Camera-reset weighted-A* local controller for the taught object pose."""

    def __init__(self) -> None:
        # Parent constructors dynamically dispatch status/reset methods, so all
        # fields used by our overrides must exist before ``super().__init__``.
        self.joint_pose_previous_primitive: Optional[Primitive] = None
        self.joint_pose_recent_states: list[ObjectPoseState] = []
        self.joint_pose_pending_prediction: Optional[ObjectPoseState] = None
        self.joint_pose_pending_start: Optional[ObjectPoseState] = None
        self.joint_pose_pending_primitive: Optional[Primitive] = None
        self.joint_pose_pending_orientation_effective = False
        self.joint_pose_stall_count = 0
        self.joint_pose_hold_count = 0
        self.joint_pose_last_model_check: Dict[str, object] = {}
        self.joint_pose_last_decision: Dict[str, object] = {}
        self.joint_pose_reverse_requested = False
        self.joint_pose_reverse_authorized = False
        super().__init__()
        self.pose_relocation_stage = "joint_pose"
        self._publish_status(
            "joint_pose_controller_ready",
            controller="camera_reset_weighted_a_star_lattice",
            target_semantics=(
                "recreate_taught_object_point_and_taught_axial_orientation"
            ),
            independent_bearing_orientation_loops=False,
            camera_reset_after_each_selected_primitive=True,
            reverse_requires_explicit_rear_clearance_ack=True,
        )
        self.get_logger().info(
            "Joint pose lattice controller ready: position and taught object "
            "orientation are planned as one camera-relative SE(2) target"
        )

    # ------------------------------------------------------------------
    # Parameters and status
    # ------------------------------------------------------------------

    def _declare_parameters(self) -> None:
        super()._declare_parameters()
        defaults: Dict[str, Any] = {
            "joint_pose_controller_enabled": True,
            # Reverse manoeuvres are often required to change viewpoint without
            # crowding the object.  They remain physically disabled until the
            # operator explicitly acknowledges a clear rear corridor.
            "joint_pose_allow_reverse": True,
            "joint_pose_rear_clearance_ack": False,
            "joint_pose_drive_enabled": False,
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
            "joint_pose_position_resolution_m": 0.004,
            "joint_pose_orientation_resolution_deg": 2.0,
            "joint_pose_search_maximum_expansions": 25000,
            "joint_pose_search_maximum_wall_time_sec": 0.15,
            "joint_pose_search_maximum_depth": 72,
            "joint_pose_search_maximum_translation_m": 0.40,
            "joint_pose_search_maximum_turn_deg": 220.0,
            "joint_pose_heuristic_weight": 3.5,
            "joint_pose_execution_prefix_length": 1,
            "joint_pose_action_cost": 1.0,
            "joint_pose_motion_cost_weight": 0.08,
            "joint_pose_reverse_cost_penalty": 0.20,
            "joint_pose_drive_cost_penalty": 0.08,
            "joint_pose_action_family_change_penalty": 0.04,
            "joint_pose_immediate_reversal_penalty": 1.80,
            "joint_pose_same_direction_bonus": 0.08,
            "joint_pose_recent_cycle_penalty": 4.0,
            "joint_pose_hard_reject_recent_cycle": True,
            "joint_pose_cycle_position_radius_m": 0.010,
            "joint_pose_cycle_orientation_radius_deg": 5.0,
            "joint_pose_cycle_required_cost_improvement": 0.20,
            "joint_pose_minimum_frontier_improvement": 0.08,
            "joint_pose_top_candidate_count": 6,
            "joint_pose_route_preview_count": 12,
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
                "joint_pose_stall_count": self.joint_pose_stall_count,
                "joint_pose_hold_count": self.joint_pose_hold_count,
                "joint_pose_reverse_requested": self.joint_pose_reverse_requested,
                "joint_pose_reverse_authorized": self.joint_pose_reverse_authorized,
                "joint_pose_last_model_check": dict(
                    self.joint_pose_last_model_check
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
        self.joint_pose_pending_primitive = None
        self.joint_pose_pending_orientation_effective = False
        self.joint_pose_stall_count = 0
        self.joint_pose_hold_count = 0
        self.joint_pose_last_model_check = {}
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
            controller="single_joint_camera_relative_pose_lattice",
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
    ) -> None:
        predicted = self.joint_pose_pending_prediction
        start = self.joint_pose_pending_start
        primitive = self.joint_pose_pending_primitive
        if predicted is None or start is None or primitive is None:
            return

        position_residual = math.hypot(
            state.forward_m - predicted.forward_m,
            state.lateral_m - predicted.lateral_m,
        )
        orientation_residual = abs(
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
        predicted_orientation_change = abs(
            wrap_axial_deg(
                predicted.orientation_error_deg - start.orientation_error_deg
            )
        )
        observed_orientation_change = abs(
            wrap_axial_deg(
                state.orientation_error_deg - start.orientation_error_deg
            )
        )
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
        missing_orientation_motion = (
            current_orientation_effective
            and predicted_orientation_change >= 2.0 * minimum_orientation_change
            and observed_orientation_change < minimum_orientation_change
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
        residual_bad = (
            position_residual > position_tolerance
            or (
                current_orientation_effective
                and orientation_residual > orientation_tolerance
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
            "primitive": primitive.to_mapping(),
            "predicted_state": predicted.to_mapping(),
            "observed_state": state.to_mapping(),
            "position_residual_m": position_residual,
            "orientation_residual_deg": orientation_residual,
            "predicted_position_change_m": predicted_position_change,
            "observed_position_change_m": observed_position_change,
            "predicted_orientation_change_deg": predicted_orientation_change,
            "observed_orientation_change_deg": observed_orientation_change,
            "orientation_residual_used": current_orientation_effective,
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
        self.joint_pose_pending_primitive = None
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
    ) -> bool:
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
            decomposition="weighted_a_star_lattice_first_action",
        )
        self.pose_relocation_stage = "joint_pose"
        iteration_before = self.pose_relocation_iteration
        self._start_pose_relocation(plan)
        started = self.pose_relocation_iteration > iteration_before
        if not started:
            return False

        self.joint_pose_previous_primitive = decision.sequence[-1]
        self.joint_pose_pending_prediction = decision.predicted_state
        self.joint_pose_pending_start = state
        self.joint_pose_pending_primitive = decision.sequence[-1]
        self.joint_pose_pending_orientation_effective = (
            decision.orientation_effective
        )
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
        # orientation; the pure planner can approach position-only and then hold.
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

        # Bypass CameraAuthoritativeTaskNode's optional coarse phase gate and
        # ask the profile-owning resilient base class whether teaching requires
        # an orientation match at all.
        orientation_required = ResilientObjectTaskNode._orientation_required(self)
        assessment = (
            self._orientation_assessment(stable)
            if orientation_required
            else None
        )
        orientation_error = (
            0.0 if assessment is None else assessment.signed_error_deg
        )
        orientation_quality = (
            1.0 if assessment is None else assessment.quality
        )
        orientation_reliable = (
            assessment is None or assessment.state != "quality_low"
        )
        if assessment is not None:
            self.orientation_last_assessment = {
                "state": assessment.state,
                "signed_error_deg": assessment.signed_error_deg,
                "absolute_error_deg": assessment.absolute_error_deg,
                "quality": assessment.quality,
                "cost": assessment.cost,
                "comparison_mode": assessment.comparison_mode,
                "reason": assessment.reason,
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

        self._record_model_residual(state, target, config)
        stall_limit = max(
            1,
            int(self.get_parameter("joint_pose_stall_limit").value),
        )
        if self.joint_pose_stall_count >= stall_limit:
            self._enter_recovery_hold(
                "JOINT_POSE_MOTION_MODEL_MISMATCH",
                "measured camera reset repeatedly disagreed with commanded local motion",
                resume_mode="align",
                stall_count=self.joint_pose_stall_count,
                model_check=dict(self.joint_pose_last_model_check),
            )
            return

        shrink = max(
            0.10,
            min(1.0, float(self.get_parameter("joint_pose_stall_step_shrink").value)),
        )
        minimum_scale = max(
            0.10,
            min(1.0, float(self.get_parameter("joint_pose_minimum_step_scale").value)),
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
            "current_cost": decision.current_cost,
            "planned_terminal_cost": decision.planned_terminal_cost,
            "expected_improvement": decision.expected_improvement,
            "search_expansions": decision.search_expansions,
            "search_reached_goal": decision.search_reached_goal,
            "orientation_required": decision.orientation_required,
            "orientation_effective": decision.orientation_effective,
            "robot_goal": decision.robot_goal.to_mapping(),
            "sequence": [item.to_mapping() for item in decision.sequence],
            "route_preview": [item.to_mapping() for item in route_preview],
            "route_length": len(decision.route_preview),
        }
        self._publish_status(
            "joint_pose_camera_comparison",
            current_object_pose=state.to_mapping(),
            taught_object_pose=target.to_mapping(),
            precision_errors={
                "bearing_error_deg": precise.bearing_error_deg,
                "forward_error_m": precise.forward_error_m,
                "lateral_error_m": precise.lateral_error_m,
                "range_error_m": precise.range_error_m,
                "planar_position_error_m": precise.planar_position_error_m,
            },
            robot_relative_goal=decision.robot_goal.to_mapping(),
            current_cost=decision.current_cost,
            planned_terminal_cost=decision.planned_terminal_cost,
            expected_improvement=decision.expected_improvement,
            selected_sequence=[
                item.to_mapping() for item in decision.sequence
            ],
            route_preview=[item.to_mapping() for item in route_preview],
            route_length=len(decision.route_preview),
            search_expansions=decision.search_expansions,
            search_reached_goal=decision.search_reached_goal,
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
            self._publish_status(
                "joint_pose_holding_for_reobservation",
                hold_count=self.joint_pose_hold_count,
                hold_limit=hold_limit,
                reason=decision.reason,
                orientation_reliable=orientation_reliable,
                reverse_requested=self.joint_pose_reverse_requested,
                reverse_authorized=self.joint_pose_reverse_authorized,
                operator_hint=(
                    "verify rear corridor then set joint_pose_rear_clearance_ack=true"
                    if self.joint_pose_reverse_requested
                    and not self.joint_pose_reverse_authorized
                    else "none"
                ),
            )
            if self.joint_pose_hold_count >= hold_limit:
                self._enter_recovery_hold(
                    "JOINT_POSE_STALLED",
                    "no safe bounded joint-pose route was found",
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
                policy="continue_with_fresh_camera_lattice_replanning",
            )
            self.alignment_iterations = 0
        started = self._start_joint_pose_plan(
            decision=decision,
            state=state,
            target=target,
        )
        if not started:
            self._publish_status(
                "joint_pose_selected_motion_not_started",
                reason="inherited motion or depth-clearance gate rejected plan",
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
