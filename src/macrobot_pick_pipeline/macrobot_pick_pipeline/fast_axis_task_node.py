"""Camera-authoritative fast grasp-axis interception node.

This executable is additive.  It leaves the existing search, perception,
camera-authoritative controller, and Pico firmware untouched.  Only the
alignment policy is changed: a coarse compound manoeuvre first reaches the
taught grasp-axis corridor, a larger axial approach follows, and the existing
precision controller receives only the final small residual.
"""

from __future__ import annotations

from dataclasses import replace
import math
import time
from typing import Any, Dict, Mapping, Optional

import rclpy

from .alignment_core import alignment_errors, observation_constraint_decision
from .camera_authoritative_task_node import CameraAuthoritativeTaskNode
from .camera_pose_relocation import RelocationPlan, relative_pose_from_primitives
from .fast_axis_controller import FastAxisPlan, choose_fast_axis_plan
from .orientation_control import OrientationAssessment
from .precision_docking import precision_errors
from .resilient_object_task_node import ResilientObjectTaskNode

PATCH_MARKER = "macrobot_fast_axis_intercept_v6"


class FastAxisTaskNode(CameraAuthoritativeTaskNode):
    """Reach the taught grasp axis quickly before legacy precision docking."""

    def __init__(self) -> None:
        self.fast_axis_stage = "axis_intercept"
        self.fast_axis_macro_count = 0
        self.fast_axis_last_plan: dict[str, object] = {}
        super().__init__()
        self._publish_status(
            "fast_axis_controller_ready",
            control_policy=(
                "fresh_rgbd_to_pregrasp_axis_compound_motion_then_"
                "existing_precision_handoff"
            ),
            pico_turn_positive_is_right=bool(self.pico_turn_positive_is_right),
            reverse_enabled=bool(
                self.get_parameter("fast_axis_allow_reverse").value
            ),
            drive_rel_enabled=bool(
                self.get_parameter("fast_axis_prefer_drive_rel").value
            ),
        )
        self.get_logger().info(
            "Fast-axis controller ready: axis intercept -> axial approach -> precision handoff"
        )

    def _declare_parameters(self) -> None:
        super()._declare_parameters()
        defaults: Dict[str, Any] = {
            "fast_axis_enabled": True,
            "fast_axis_pregrasp_standoff_m": 0.080,
            "fast_axis_corridor_tolerance_m": 0.015,
            "fast_axis_orientation_tolerance_deg": 7.0,
            "fast_axis_handoff_forward_tolerance_m": 0.035,
            "fast_axis_handoff_lateral_tolerance_m": 0.012,
            "fast_axis_handoff_orientation_tolerance_deg": 5.0,
            "fast_axis_precision_reentry_forward_m": 0.070,
            "fast_axis_precision_reentry_lateral_m": 0.030,
            "fast_axis_precision_reentry_orientation_deg": 12.0,
            "fast_axis_intercept_progress": 0.92,
            "fast_axis_intercept_max_translation_m": 0.180,
            "fast_axis_intercept_max_turn_deg": 105.0,
            "fast_axis_approach_progress": 0.90,
            "fast_axis_approach_max_translation_m": 0.150,
            "fast_axis_approach_max_turn_deg": 30.0,
            "fast_axis_minimum_object_range_m": 0.120,
            "fast_axis_allow_reverse": False,
            "fast_axis_reverse_turn_penalty_deg": 30.0,
            "fast_axis_min_turn_deg": 0.75,
            "fast_axis_min_move_m": 0.004,
            "fast_axis_prefer_drive_rel": False,
            "fast_axis_max_drive_yaw_deg": 25.0,
            "fast_axis_min_drive_radius_m": 0.10,
            "fast_axis_max_macros_before_handoff": 8,
            "fast_axis_fallback_to_legacy": True,
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
                "fast_axis_enabled": bool(
                    self.get_parameter("fast_axis_enabled").value
                ),
                "fast_axis_stage": self.fast_axis_stage,
                "fast_axis_macro_count": self.fast_axis_macro_count,
                "fast_axis_last_plan": dict(self.fast_axis_last_plan),
            }
        )
        return payload

    def _reset_action_state(self) -> None:
        super()._reset_action_state()
        self.fast_axis_stage = "axis_intercept"
        self.fast_axis_macro_count = 0
        self.fast_axis_last_plan = {}

    def _begin_visual_approach(self, stable) -> None:
        super()._begin_visual_approach(stable)
        self.fast_axis_stage = "axis_intercept"
        self.fast_axis_macro_count = 0
        self.fast_axis_last_plan = {}
        self._publish_status(
            "fast_axis_alignment_started",
            reference_point_base=list(
                self.profile.alignment.reference_point_base
            ),
            reference_orientation_deg=self.orientation_reference_deg,
            pregrasp_standoff_m=float(
                self.get_parameter("fast_axis_pregrasp_standoff_m").value
            ),
            controller="fast_axis_intercept_v6",
        )

    @staticmethod
    def _plan_payload(plan: FastAxisPlan) -> dict[str, object]:
        return {
            "stage": plan.stage,
            "handoff_ready": plan.handoff_ready,
            "reason": plan.reason,
            "current_point": list(plan.current_point),
            "reference_point": list(plan.reference_point),
            "target_point": list(plan.target_point),
            "desired_point": list(plan.desired_point),
            "predicted_point": list(plan.predicted_point),
            "current_orientation_deg": plan.current_orientation_deg,
            "reference_orientation_deg": plan.reference_orientation_deg,
            "predicted_orientation_deg": plan.predicted_orientation_deg,
            "orientation_error_deg": plan.orientation_error_deg,
            "raw_forward_error_m": plan.raw_forward_error_m,
            "raw_lateral_error_m": plan.raw_lateral_error_m,
            "along_axis_error_m": plan.along_axis_error_m,
            "cross_track_error_m": plan.cross_track_error_m,
            "progress": plan.progress,
            "robot_target": {
                "x_m": plan.robot_target.x_m,
                "y_m": plan.robot_target.y_m,
                "yaw_deg": plan.robot_target.yaw_deg,
            },
            "decomposition": plan.decomposition,
            "predicted_minimum_object_range_m": (
                plan.predicted_minimum_object_range_m
            ),
            "primitives": [
                {
                    "kind": item.kind,
                    "amount": item.amount,
                    "yaw_deg": item.yaw_deg,
                }
                for item in plan.primitives
            ],
        }

    def _delegate_stable_to_existing_precision(self, stable, *, reason: str) -> None:
        self.fast_axis_stage = "precision_handoff"
        self.cached_stable_detection = stable
        self.latest_stable_detection = stable
        self.last_object_point = stable.point_base
        self._publish_status(
            "fast_axis_precision_handoff",
            reason=reason,
            next="existing_camera_authoritative_precision_controller",
            coarse_macro_count=self.fast_axis_macro_count,
        )
        super()._try_alignment_step()

    def _try_alignment_step(self) -> None:
        if not bool(self.get_parameter("fast_axis_enabled").value):
            super()._try_alignment_step()
            return
        if self.profile is None or self.base_active or self.pose_relocation_active:
            return
        # A taught, reliable object axis is required to define the grasp
        # corridor.  Profiles without one retain the existing controller.
        if not ResilientObjectTaskNode._orientation_required(self):
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
                    "fast_axis_visual_target_lost",
                    next="restart_full_search",
                )
                self._restart_full_search(
                    "visual target lost during fast-axis interception"
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
            self.filter.clear()
            self._publish_status(
                "fast_axis_observation_rejected",
                reason=constraint.reason,
                policy="hold_stationary_and_wait_for_better_rgbd",
            )
            return

        self._update_visual_anchor(stable)
        try:
            errors = alignment_errors(
                stable.point_base,
                self.profile.alignment.reference_point_base,
                forward_axis_sign=self.forward_axis_sign,
                lateral_axis_sign=self.lateral_axis_sign,
            )
        except Exception as error:
            self.filter.clear()
            self._enter_recovery_hold(
                "TARGET_POSE_INVALID",
                str(error),
                resume_mode="search",
            )
            return
        self.last_errors = errors
        if errors.current.forward_m <= 0.0:
            self.filter.clear()
            self._restart_full_search("object_not_in_front_half_plane")
            return
        if abs(errors.height_error_m) > self.profile.alignment.height_tolerance_m:
            self.filter.clear()
            self._enter_recovery_hold(
                "TARGET_POSE_NOT_CORRECTABLE",
                "height_error_not_correctable_by_planar_base",
                resume_mode="manual",
                height_error_m=errors.height_error_m,
            )
            return

        assessment: Optional[OrientationAssessment] = self._orientation_assessment(
            stable
        )
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
            self.filter.clear()
            self._publish_status(
                "fast_axis_orientation_quality_low",
                assessment=dict(self.orientation_last_assessment),
                next="existing_orientation_recovery",
            )
            self._run_orientation_recovery(stable, assessment)
            return

        current_xy = (errors.current.forward_m, errors.current.lateral_m)
        reference_xy = (
            errors.reference.forward_m,
            errors.reference.lateral_m,
        )
        plan = choose_fast_axis_plan(
            current_xy,
            reference_xy,
            stable.orientation_deg,
            self.orientation_reference_deg,
            handoff_forward_tolerance_m=float(
                self.get_parameter(
                    "fast_axis_handoff_forward_tolerance_m"
                ).value
            ),
            handoff_lateral_tolerance_m=float(
                self.get_parameter(
                    "fast_axis_handoff_lateral_tolerance_m"
                ).value
            ),
            handoff_orientation_tolerance_deg=float(
                self.get_parameter(
                    "fast_axis_handoff_orientation_tolerance_deg"
                ).value
            ),
            axis_corridor_tolerance_m=float(
                self.get_parameter("fast_axis_corridor_tolerance_m").value
            ),
            axis_orientation_tolerance_deg=float(
                self.get_parameter(
                    "fast_axis_orientation_tolerance_deg"
                ).value
            ),
            pregrasp_standoff_m=float(
                self.get_parameter("fast_axis_pregrasp_standoff_m").value
            ),
            intercept_progress=float(
                self.get_parameter("fast_axis_intercept_progress").value
            ),
            intercept_maximum_translation_m=float(
                self.get_parameter(
                    "fast_axis_intercept_max_translation_m"
                ).value
            ),
            intercept_maximum_turn_deg=float(
                self.get_parameter("fast_axis_intercept_max_turn_deg").value
            ),
            approach_progress=float(
                self.get_parameter("fast_axis_approach_progress").value
            ),
            approach_maximum_translation_m=float(
                self.get_parameter(
                    "fast_axis_approach_max_translation_m"
                ).value
            ),
            approach_maximum_turn_deg=float(
                self.get_parameter("fast_axis_approach_max_turn_deg").value
            ),
            minimum_object_range_m=float(
                self.get_parameter("fast_axis_minimum_object_range_m").value
            ),
            allow_reverse=bool(
                self.get_parameter("fast_axis_allow_reverse").value
            ),
            reverse_turn_penalty_deg=float(
                self.get_parameter(
                    "fast_axis_reverse_turn_penalty_deg"
                ).value
            ),
            minimum_turn_deg=float(
                self.get_parameter("fast_axis_min_turn_deg").value
            ),
            minimum_move_m=float(
                self.get_parameter("fast_axis_min_move_m").value
            ),
            prefer_drive_rel=bool(
                self.get_parameter("fast_axis_prefer_drive_rel").value
            ),
            maximum_drive_yaw_deg=float(
                self.get_parameter("fast_axis_max_drive_yaw_deg").value
            ),
            minimum_drive_radius_m=float(
                self.get_parameter("fast_axis_min_drive_radius_m").value
            ),
            # Use the parent assessment's signed error because it may come
            # from a compatible measured 3-D base_link axis rather than the
            # scalar image-plane angle.
            orientation_error_override_deg=assessment.signed_error_deg,
        )
        self.fast_axis_last_plan = self._plan_payload(plan)
        precise = precision_errors(errors)
        self._publish_status(
            "fast_axis_camera_comparison",
            plan=dict(self.fast_axis_last_plan),
            precision_errors={
                "bearing_error_deg": precise.bearing_error_deg,
                "forward_error_m": precise.forward_error_m,
                "lateral_error_m": precise.lateral_error_m,
                "range_error_m": precise.range_error_m,
                "planar_position_error_m": precise.planar_position_error_m,
            },
            orientation_assessment=dict(self.orientation_last_assessment),
            policy=(
                "intercept_taught_grasp_axis_at_pregrasp_standoff_then_"
                "large_axial_approach_then_precision"
            ),
        )

        # Hysteresis after handoff: the existing precision controller remains
        # authoritative unless the target has moved far outside a wider box.
        if self.fast_axis_stage == "precision_handoff":
            inside_reentry_box = (
                abs(plan.along_axis_error_m)
                <= abs(
                    float(
                        self.get_parameter(
                            "fast_axis_precision_reentry_forward_m"
                        ).value
                    )
                )
                and abs(plan.cross_track_error_m)
                <= abs(
                    float(
                        self.get_parameter(
                            "fast_axis_precision_reentry_lateral_m"
                        ).value
                    )
                )
                and abs(plan.orientation_error_deg)
                <= abs(
                    float(
                        self.get_parameter(
                            "fast_axis_precision_reentry_orientation_deg"
                        ).value
                    )
                )
            )
            if inside_reentry_box:
                self.filter.clear()
                self._delegate_stable_to_existing_precision(
                    stable,
                    reason="inside_precision_reentry_hysteresis_box",
                )
                return
            self.fast_axis_stage = "axis_intercept"
            self.fast_axis_macro_count = 0
            self._publish_status(
                "fast_axis_coarse_reentry",
                reason="precision_residual_left_reentry_box",
            )

        if plan.handoff_ready:
            self.filter.clear()
            self._delegate_stable_to_existing_precision(
                stable,
                reason=plan.reason,
            )
            return

        if not plan.primitives:
            self.filter.clear()
            if bool(
                self.get_parameter("fast_axis_fallback_to_legacy").value
            ):
                self.cached_stable_detection = stable
                self.latest_stable_detection = stable
                self.last_object_point = stable.point_base
                self._publish_status(
                    "fast_axis_fallback_to_legacy",
                    reason=plan.reason,
                )
                super()._try_alignment_step()
                return
            self._enter_recovery_hold(
                "TARGET_POSE_NOT_CORRECTABLE",
                f"fast-axis planner produced no safe macro: {plan.reason}",
                resume_mode="align",
                fast_axis_plan=dict(self.fast_axis_last_plan),
            )
            return

        maximum_macros = max(
            1,
            int(
                self.get_parameter(
                    "fast_axis_max_macros_before_handoff"
                ).value
            ),
        )
        if self.fast_axis_macro_count >= maximum_macros:
            self.filter.clear()
            if bool(
                self.get_parameter("fast_axis_fallback_to_legacy").value
            ):
                self.cached_stable_detection = stable
                self.latest_stable_detection = stable
                self.last_object_point = stable.point_base
                self._publish_status(
                    "fast_axis_macro_budget_exhausted",
                    maximum_macros=maximum_macros,
                    next="existing_camera_controller",
                )
                super()._try_alignment_step()
                return
            self._enter_recovery_hold(
                "ALIGNMENT_BUDGET_EXHAUSTED",
                "fast-axis macro budget exhausted before precision handoff",
                resume_mode="align",
            )
            return

        self.filter.clear()
        self.fast_axis_stage = plan.stage
        self.fast_axis_macro_count += 1
        robot_target = relative_pose_from_primitives(plan.primitives)
        current_range = math.hypot(*plan.current_point)
        reference_range = math.hypot(*plan.reference_point)
        current_bearing = math.degrees(
            math.atan2(plan.current_point[1], plan.current_point[0])
        )
        reference_bearing = math.degrees(
            math.atan2(plan.reference_point[1], plan.reference_point[0])
        )
        relocation = RelocationPlan(
            stage=f"fast_axis_{plan.stage}",
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
            forward_error_m=plan.raw_forward_error_m,
            lateral_error_m=plan.raw_lateral_error_m,
            progress=plan.progress,
            robot_target=robot_target,
            primitives=plan.primitives,
            predicted_minimum_object_range_m=(
                plan.predicted_minimum_object_range_m
            ),
            decomposition=f"fast_axis_{plan.decomposition}",
        )
        self.pose_relocation_stage = plan.stage
        self._start_pose_relocation(relocation)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = FastAxisTaskNode()
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
