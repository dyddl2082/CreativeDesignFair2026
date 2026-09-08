"""Camera-authoritative direct-pose task node.

This node is intentionally an additive executable.  It does not overwrite the
existing camera_authoritative_task_node, so the previous controller remains an
immediate rollback option.
"""

from __future__ import annotations

from dataclasses import replace
import math
import time
from typing import Any, Dict, Mapping, Optional

import rclpy

from .alignment_core import alignment_errors, observation_constraint_decision
from .camera_authoritative_task_node import CameraAuthoritativeTaskNode
from .camera_pose_relocation import (
    MotionPrimitive,
    RelocationPlan,
    relative_pose_from_primitives,
)
from .direct_pose_controller import choose_direct_pose_macro
from .orientation_control import OrientationAssessment
from .precision_docking import precision_errors

PATCH_MARKER = "macrobot_direct_pose_pursuit_v5"


class DirectPoseTaskNode(CameraAuthoritativeTaskNode):
    """Use one joint SE(2) camera-pose objective during alignment."""

    def __init__(self) -> None:
        self.direct_pose_confirmations = 0
        self.direct_pose_last_plan: dict[str, object] = {}
        super().__init__()
        self._publish_status(
            "direct_pose_controller_ready",
            control_policy="joint_taught_camera_pose_receding_horizon",
            reverse_enabled=bool(self.get_parameter("direct_pose_allow_reverse").value),
            pico_turn_positive_is_right=bool(self.pico_turn_positive_is_right),
        )
        self.get_logger().info(
            "Direct-pose pursuit ready: RGB-D position + object axis -> bounded SE(2) macro -> fresh RGB-D"
        )

    def _declare_parameters(self) -> None:
        super()._declare_parameters()
        defaults: Dict[str, Any] = {
            "direct_pose_enabled": True,
            "direct_pose_coarse_progress": 0.72,
            "direct_pose_near_progress": 0.45,
            "direct_pose_near_position_error_m": 0.025,
            "direct_pose_near_orientation_error_deg": 8.0,
            "direct_pose_max_translation_m": 0.065,
            "direct_pose_near_max_translation_m": 0.030,
            "direct_pose_max_turn_primitive_deg": 100.0,
            "direct_pose_min_turn_deg": 0.75,
            "direct_pose_min_move_m": 0.002,
            "direct_pose_minimum_object_range_m": 0.12,
            "direct_pose_allow_reverse": False,
            "direct_pose_reverse_turn_penalty_deg": 25.0,
            "direct_pose_prefer_drive_rel": True,
            "direct_pose_max_drive_yaw_deg": 20.0,
            "direct_pose_min_drive_radius_m": 0.08,
            "direct_pose_confirmation_count": 2,
            "direct_pose_fallback_to_legacy": True,
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
                "direct_pose_enabled": bool(
                    self.get_parameter("direct_pose_enabled").value
                ),
                "direct_pose_confirmations": self.direct_pose_confirmations,
                "direct_pose_last_plan": dict(self.direct_pose_last_plan),
            }
        )
        return payload

    def _reset_action_state(self) -> None:
        super()._reset_action_state()
        self.direct_pose_confirmations = 0
        self.direct_pose_last_plan = {}

    def _begin_visual_approach(self, stable) -> None:
        super()._begin_visual_approach(stable)
        self.direct_pose_confirmations = 0
        self.direct_pose_last_plan = {}
        self._publish_status(
            "direct_pose_alignment_started",
            reference_point_base=list(self.profile.alignment.reference_point_base),
            reference_orientation_deg=self.orientation_reference_deg,
            controller="direct_pose_pursuit_v5",
        )

    @staticmethod
    def _plan_payload(plan) -> dict[str, object]:
        return {
            "reached": plan.reached,
            "reason": plan.reason,
            "current_point": list(plan.current_point),
            "reference_point": list(plan.reference_point),
            "desired_point": list(plan.desired_point),
            "predicted_point": list(plan.predicted_point),
            "current_orientation_deg": plan.current_orientation_deg,
            "reference_orientation_deg": plan.reference_orientation_deg,
            "predicted_orientation_deg": plan.predicted_orientation_deg,
            "orientation_error_deg": plan.orientation_error_deg,
            "forward_error_m": plan.forward_error_m,
            "lateral_error_m": plan.lateral_error_m,
            "position_error_m": plan.position_error_m,
            "progress": plan.progress,
            "exact_goal_robot_pose": list(plan.exact_goal_robot_pose),
            "intermediate_robot_pose": list(plan.intermediate_robot_pose),
            "decomposition": plan.decomposition,
            "predicted_minimum_object_range_m": plan.predicted_minimum_object_range_m,
            "primitives": [
                {
                    "kind": item.kind,
                    "amount": item.amount,
                    "yaw_deg": item.yaw_deg,
                }
                for item in plan.primitives
            ],
        }

    def _try_alignment_step(self) -> None:
        if not bool(self.get_parameter("direct_pose_enabled").value):
            super()._try_alignment_step()
            return
        if self.profile is None or self.base_active or self.pose_relocation_active:
            return
        # Without a taught reliable orientation there is no unique grasp-side
        # target.  Keep the existing camera controller for such legacy profiles.
        if not CameraAuthoritativeTaskNode._orientation_required(self):
            super()._try_alignment_step()
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
                self._publish_status(
                    "direct_pose_visual_target_lost",
                    next="restart_full_search",
                )
                self._restart_full_search(
                    "visual target lost during direct-pose pursuit"
                )
            return

        basic_profile = replace(
            self.profile.alignment,
            require_orientation_match=False,
        )
        constraint = observation_constraint_decision(
            basic_profile,
            localization_quality=stable.localization_quality,
            depth_std_m=stable.depth_std_m,
            center_std_px=stable.center_std_px,
            orientation_deg=stable.orientation_deg,
            orientation_class=stable.orientation_class,
            orientation_quality=stable.orientation_quality,
        )
        if constraint.action == "reject":
            self.direct_pose_confirmations = 0
            self.filter.clear()
            self._publish_status(
                "direct_pose_observation_rejected",
                reason=constraint.reason,
                policy="hold_stationary_and_wait_for_better_rgbd",
            )
            return

        self._update_visual_anchor(stable)
        self.filter.clear()
        try:
            errors = alignment_errors(
                stable.point_base,
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

        assessment: Optional[OrientationAssessment] = self._orientation_assessment(stable)
        self.orientation_last_assessment = {
            "state": assessment.state,
            "signed_error_deg": assessment.signed_error_deg,
            "absolute_error_deg": assessment.absolute_error_deg,
            "quality": assessment.quality,
            "cost": assessment.cost,
            "comparison_mode": assessment.comparison_mode,
            "reason": assessment.reason,
        }
        if assessment.state == "quality_low":
            self.direct_pose_confirmations = 0
            self._publish_status(
                "direct_pose_orientation_quality_low",
                assessment=dict(self.orientation_last_assessment),
                next="existing_orientation_recovery",
            )
            self._run_orientation_recovery(stable, assessment)
            return

        current_xy = (
            errors.current.forward_m,
            errors.current.lateral_m,
        )
        reference_xy = (
            errors.reference.forward_m,
            errors.reference.lateral_m,
        )
        plan = choose_direct_pose_macro(
            current_xy,
            reference_xy,
            stable.orientation_deg,
            self.orientation_reference_deg,
            forward_tolerance_m=float(
                self.get_parameter("precision_forward_tolerance_m").value
            ),
            lateral_tolerance_m=float(
                self.get_parameter("precision_lateral_tolerance_m").value
            ),
            orientation_tolerance_deg=float(
                self.get_parameter("precision_orientation_tolerance_deg").value
            ),
            coarse_progress=float(
                self.get_parameter("direct_pose_coarse_progress").value
            ),
            near_progress=float(
                self.get_parameter("direct_pose_near_progress").value
            ),
            near_position_error_m=float(
                self.get_parameter("direct_pose_near_position_error_m").value
            ),
            near_orientation_error_deg=float(
                self.get_parameter("direct_pose_near_orientation_error_deg").value
            ),
            maximum_translation_m=float(
                self.get_parameter("direct_pose_max_translation_m").value
            ),
            near_maximum_translation_m=float(
                self.get_parameter("direct_pose_near_max_translation_m").value
            ),
            maximum_turn_primitive_deg=float(
                self.get_parameter("direct_pose_max_turn_primitive_deg").value
            ),
            minimum_turn_deg=float(
                self.get_parameter("direct_pose_min_turn_deg").value
            ),
            minimum_move_m=float(
                self.get_parameter("direct_pose_min_move_m").value
            ),
            minimum_object_range_m=float(
                self.get_parameter("direct_pose_minimum_object_range_m").value
            ),
            allow_reverse=bool(
                self.get_parameter("direct_pose_allow_reverse").value
            ),
            reverse_turn_penalty_deg=float(
                self.get_parameter("direct_pose_reverse_turn_penalty_deg").value
            ),
            prefer_drive_rel=bool(
                self.get_parameter("direct_pose_prefer_drive_rel").value
            ),
            maximum_drive_yaw_deg=float(
                self.get_parameter("direct_pose_max_drive_yaw_deg").value
            ),
            minimum_drive_radius_m=float(
                self.get_parameter("direct_pose_min_drive_radius_m").value
            ),
        )
        self.direct_pose_last_plan = self._plan_payload(plan)
        precise = precision_errors(errors)
        self._publish_status(
            "direct_pose_camera_comparison",
            plan=dict(self.direct_pose_last_plan),
            precision_errors={
                "bearing_error_deg": precise.bearing_error_deg,
                "forward_error_m": precise.forward_error_m,
                "lateral_error_m": precise.lateral_error_m,
                "range_error_m": precise.range_error_m,
                "planar_position_error_m": precise.planar_position_error_m,
            },
            orientation_assessment=dict(self.orientation_last_assessment),
            control_policy=(
                "solve_taught_camera_relative_SE2_then_execute_bounded_macro_"
                "without_intermediate_camera_decision"
            ),
            reverse_enabled=bool(
                self.get_parameter("direct_pose_allow_reverse").value
            ),
        )

        if plan.reached:
            self.direct_pose_confirmations += 1
            required = max(
                1,
                int(self.get_parameter("direct_pose_confirmation_count").value),
            )
            if self.direct_pose_confirmations >= required:
                self._publish_status(
                    "direct_pose_alignment_completed",
                    confirmations=self.direct_pose_confirmations,
                    next="semantic_preflight",
                )
                self._alignment_complete()
            else:
                self.filter.clear()
                self._publish_status(
                    "direct_pose_alignment_confirmation",
                    confirmation=self.direct_pose_confirmations,
                    required=required,
                )
            return

        self.direct_pose_confirmations = 0
        if not plan.primitives:
            if bool(self.get_parameter("direct_pose_fallback_to_legacy").value):
                self.cached_stable_detection = stable
                self.latest_stable_detection = stable
                self.last_object_point = stable.point_base
                self._publish_status(
                    "direct_pose_fallback_to_legacy",
                    reason=plan.reason,
                )
                super()._try_alignment_step()
                return
            self._enter_recovery_hold(
                "TARGET_POSE_NOT_CORRECTABLE",
                f"direct-pose planner produced no bounded macro: {plan.reason}",
                resume_mode="align",
                direct_pose_plan=dict(self.direct_pose_last_plan),
            )
            return

        primitives = tuple(
            MotionPrimitive(item.kind, item.amount, item.yaw_deg)
            for item in plan.primitives
        )
        robot_target = relative_pose_from_primitives(primitives)
        current_range = math.hypot(*plan.current_point)
        reference_range = math.hypot(*plan.reference_point)
        current_bearing = math.degrees(
            math.atan2(plan.current_point[1], plan.current_point[0])
        )
        reference_bearing = math.degrees(
            math.atan2(plan.reference_point[1], plan.reference_point[0])
        )
        relocation = RelocationPlan(
            stage="direct",
            reached=False,
            reason=plan.reason,
            current_point=plan.current_point,
            desired_point=plan.desired_point,
            anchor_range_m=current_range,
            orientation_error_deg=plan.orientation_error_deg,
            bearing_error_deg=(
                (current_bearing - reference_bearing + 180.0) % 360.0 - 180.0
            ),
            range_error_m=current_range - reference_range,
            forward_error_m=plan.forward_error_m,
            lateral_error_m=plan.lateral_error_m,
            progress=plan.progress,
            robot_target=robot_target,
            primitives=primitives,
            predicted_minimum_object_range_m=(
                plan.predicted_minimum_object_range_m
            ),
            decomposition=f"direct_pose_{plan.decomposition}",
        )
        self.pose_relocation_stage = "direct"
        self._start_pose_relocation(relocation)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = DirectPoseTaskNode()
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
