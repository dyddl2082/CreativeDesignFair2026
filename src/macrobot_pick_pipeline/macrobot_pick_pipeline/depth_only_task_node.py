"""Camera-authoritative depth-only grasp approach node.

The node deliberately gives up object-orientation matching and never emits a
turn or DRIVE_REL command during the final approach.  It compares only the
base_link forward depth with the taught forward depth, executes one bounded
straight MOVE primitive, and then requires a fresh RGB-D observation.

Lateral displacement and bearing are used only as configurable safety guards.
They cannot cause corrective motion.
"""

from __future__ import annotations

from dataclasses import replace
import math
import time
from typing import Any, Dict, Mapping

import rclpy

from .alignment_core import alignment_errors, observation_constraint_decision
from .camera_authoritative_task_node import CameraAuthoritativeTaskNode
from .camera_pose_relocation import (
    MotionPrimitive,
    RelocationPlan,
    relative_pose_from_primitives,
)
from .depth_only_controller import DepthOnlyPlan, choose_depth_only_plan

PATCH_MARKER = "macrobot_depth_only_grasp_v7_1"


class DepthOnlyTaskNode(CameraAuthoritativeTaskNode):
    """Align only the taught forward depth before semantic grasp preflight."""

    def __init__(self) -> None:
        self.depth_only_confirmations = 0
        self.depth_only_move_count = 0
        self.depth_only_last_plan: dict[str, object] = {}
        super().__init__()
        self._publish_status(
            "depth_only_controller_ready",
            control_policy=(
                "base_link_forward_depth_only_straight_move_then_fresh_rgbd"
            ),
            orientation_policy="ignored_for_base_alignment",
            turn_commands_enabled=False,
            drive_rel_enabled=False,
            reverse_enabled=bool(
                self.get_parameter("depth_only_allow_reverse").value
            ),
        )
        self.get_logger().warning(
            "Depth-only grasp controller active: orientation is ignored and "
            "final approach uses straight MOVE commands only"
        )

    def _declare_parameters(self) -> None:
        super()._declare_parameters()
        defaults: Dict[str, Any] = {
            "depth_only_enabled": True,
            "depth_only_forward_tolerance_m": 0.008,
            "depth_only_confirmation_count": 2,
            "depth_only_target_offset_m": 0.0,
            "depth_only_coarse_progress": 0.90,
            "depth_only_near_progress": 0.65,
            "depth_only_near_error_m": 0.040,
            "depth_only_max_forward_step_m": 0.080,
            "depth_only_max_reverse_step_m": 0.040,
            "depth_only_min_move_m": 0.004,
            "depth_only_minimum_object_forward_m": 0.120,
            "depth_only_allow_reverse": True,
            "depth_only_lateral_guard_enabled": True,
            "depth_only_max_lateral_delta_m": 0.080,
            "depth_only_max_abs_bearing_deg": 28.0,
            "depth_only_max_moves": 10,
            "depth_only_fallback_to_legacy": False,
        }
        for name, value in defaults.items():
            self.declare_parameter(name, value)

    def _orientation_required(self) -> bool:
        """Disable orientation as an alignment acceptance requirement."""

        return False

    def _status_payload(
        self,
        event: str,
        ok: bool,
        details: Mapping[str, Any],
    ) -> Dict[str, Any]:
        payload = super()._status_payload(event, ok, details)
        payload.update(
            {
                "depth_only_enabled": bool(
                    self.get_parameter("depth_only_enabled").value
                ),
                "depth_only_confirmations": self.depth_only_confirmations,
                "depth_only_move_count": self.depth_only_move_count,
                "depth_only_last_plan": dict(self.depth_only_last_plan),
                "depth_only_orientation_ignored": True,
            }
        )
        return payload

    def _reset_action_state(self) -> None:
        super()._reset_action_state()
        self.depth_only_confirmations = 0
        self.depth_only_move_count = 0
        self.depth_only_last_plan = {}

    def _begin_visual_approach(self, stable) -> None:
        super()._begin_visual_approach(stable)
        self.depth_only_confirmations = 0
        self.depth_only_move_count = 0
        self.depth_only_last_plan = {}
        reference = self.profile.alignment.reference_point_base
        self._publish_status(
            "depth_only_alignment_started",
            reference_point_base=list(reference),
            target_forward_depth_m=(
                float(reference[0])
                + float(self.get_parameter("depth_only_target_offset_m").value)
            ),
            orientation_policy="ignored",
            motion_policy="straight_move_only",
            controller="depth_only_grasp_v7",
        )

    @staticmethod
    def _plan_payload(plan: DepthOnlyPlan) -> dict[str, object]:
        return {
            "reached": plan.reached,
            "blocked": plan.blocked,
            "reason": plan.reason,
            "current_depth_m": plan.current_depth_m,
            "target_depth_m": plan.target_depth_m,
            "depth_error_m": plan.depth_error_m,
            "current_lateral_m": plan.current_lateral_m,
            "reference_lateral_m": plan.reference_lateral_m,
            "lateral_delta_m": plan.lateral_delta_m,
            "bearing_deg": plan.bearing_deg,
            "progress": plan.progress,
            "command_m": plan.command_m,
            "predicted_depth_m": plan.predicted_depth_m,
            "predicted_range_m": plan.predicted_range_m,
            "orientation_used": False,
        }

    def _stable_or_cached_detection(self):
        stable = self._stable_detection()
        if stable is None and self.cached_stable_detection is not None:
            stable = self.cached_stable_detection
            self.cached_stable_detection = None
        return stable

    def _handle_missing_detection(self) -> None:
        now = time.monotonic()
        if now < self.reobserve_not_before:
            return
        if self.last_visual_wall_sec <= 0.0 or (
            time.time() - self.last_visual_wall_sec
            > float(self.get_parameter("visual_lost_timeout_sec").value)
        ):
            self._publish_status(
                "depth_only_visual_target_lost",
                next="restart_full_search",
            )
            self._restart_full_search(
                "visual target lost during depth-only approach"
            )

    def _complete_depth_alignment(self, stable, plan: DepthOnlyPlan) -> None:
        self.depth_only_confirmations += 1
        required = max(
            1,
            int(self.get_parameter("depth_only_confirmation_count").value),
        )
        if self.depth_only_confirmations < required:
            self.filter.clear()
            self._publish_status(
                "depth_only_alignment_confirmation",
                confirmation=self.depth_only_confirmations,
                required=required,
                current_depth_m=plan.current_depth_m,
                target_depth_m=plan.target_depth_m,
                depth_error_m=plan.depth_error_m,
                orientation_policy="ignored",
            )
            return

        self.latest_stable_detection = stable
        self.last_object_point = stable.point_base
        self._publish_status(
            "depth_only_alignment_completed",
            confirmations=self.depth_only_confirmations,
            final_depth_error_m=plan.depth_error_m,
            ignored_orientation_deg=stable.orientation_deg,
            next="semantic_preflight_and_grasp",
        )
        self._alignment_complete()

    def _try_alignment_step(self) -> None:
        if not bool(self.get_parameter("depth_only_enabled").value):
            super()._try_alignment_step()
            return
        if self.profile is None or self.base_active or self.pose_relocation_active:
            return

        stable = self._stable_or_cached_detection()
        if stable is None:
            self._handle_missing_detection()
            return

        # Keep localization/depth quality checks, but explicitly remove the
        # orientation-match requirement from the observation contract.
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
            self.depth_only_confirmations = 0
            self.filter.clear()
            self._publish_status(
                "depth_only_observation_rejected",
                reason=constraint.reason,
                policy="hold_stationary_and_wait_for_better_depth",
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
        self.latest_stable_detection = stable
        self.last_object_point = stable.point_base

        if errors.current.forward_m <= 0.0:
            self._restart_full_search("object_not_in_front_half_plane")
            return
        if abs(errors.height_error_m) > self.profile.alignment.height_tolerance_m:
            self._enter_recovery_hold(
                "TARGET_POSE_NOT_CORRECTABLE",
                "height_error_not_correctable_by_straight_depth_motion",
                resume_mode="manual",
                height_error_m=errors.height_error_m,
            )
            return

        target_depth = (
            errors.reference.forward_m
            + float(self.get_parameter("depth_only_target_offset_m").value)
        )
        plan = choose_depth_only_plan(
            errors.current.forward_m,
            target_depth,
            current_lateral_m=errors.current.lateral_m,
            reference_lateral_m=errors.reference.lateral_m,
            forward_tolerance_m=float(
                self.get_parameter("depth_only_forward_tolerance_m").value
            ),
            coarse_progress=float(
                self.get_parameter("depth_only_coarse_progress").value
            ),
            near_progress=float(
                self.get_parameter("depth_only_near_progress").value
            ),
            near_error_m=float(
                self.get_parameter("depth_only_near_error_m").value
            ),
            maximum_forward_step_m=float(
                self.get_parameter("depth_only_max_forward_step_m").value
            ),
            maximum_reverse_step_m=float(
                self.get_parameter("depth_only_max_reverse_step_m").value
            ),
            minimum_move_m=float(
                self.get_parameter("depth_only_min_move_m").value
            ),
            minimum_object_forward_m=float(
                self.get_parameter(
                    "depth_only_minimum_object_forward_m"
                ).value
            ),
            allow_reverse=bool(
                self.get_parameter("depth_only_allow_reverse").value
            ),
            lateral_guard_enabled=bool(
                self.get_parameter(
                    "depth_only_lateral_guard_enabled"
                ).value
            ),
            maximum_lateral_delta_m=float(
                self.get_parameter(
                    "depth_only_max_lateral_delta_m"
                ).value
            ),
            maximum_abs_bearing_deg=float(
                self.get_parameter(
                    "depth_only_max_abs_bearing_deg"
                ).value
            ),
        )
        self.depth_only_last_plan = self._plan_payload(plan)
        self._publish_status(
            "depth_only_camera_comparison",
            plan=dict(self.depth_only_last_plan),
            measured_point_base=list(stable.point_base),
            reference_point_base=list(
                self.profile.alignment.reference_point_base
            ),
            ignored_orientation={
                "orientation_deg": stable.orientation_deg,
                "orientation_class": stable.orientation_class,
                "orientation_quality": stable.orientation_quality,
            },
            control_policy=(
                "compare_forward_depth_only; lateral_and_bearing_are_guards; "
                "never_turn_during_final_approach"
            ),
        )

        if plan.reached:
            self._complete_depth_alignment(stable, plan)
            return

        self.depth_only_confirmations = 0
        if plan.blocked or abs(plan.command_m) <= 1e-12:
            if bool(
                self.get_parameter("depth_only_fallback_to_legacy").value
            ):
                self.cached_stable_detection = stable
                self._publish_status(
                    "depth_only_fallback_to_legacy",
                    reason=plan.reason,
                    warning="legacy_controller_may_turn_and_use_orientation",
                )
                super()._try_alignment_step()
                return
            self._enter_recovery_hold(
                "TARGET_POSE_NOT_CORRECTABLE",
                f"depth-only controller stopped: {plan.reason}",
                resume_mode="align",
                depth_only_plan=dict(self.depth_only_last_plan),
            )
            return

        maximum_moves = max(
            1,
            int(self.get_parameter("depth_only_max_moves").value),
        )
        if self.depth_only_move_count >= maximum_moves:
            self._enter_recovery_hold(
                "ALIGNMENT_BUDGET_EXHAUSTED",
                "depth-only move budget exhausted before target depth",
                resume_mode="align",
                maximum_moves=maximum_moves,
                depth_only_plan=dict(self.depth_only_last_plan),
            )
            return

        primitive = MotionPrimitive("move", plan.command_m, 0.0)
        primitives = (primitive,)
        robot_target = relative_pose_from_primitives(primitives)
        current_point = (
            errors.current.forward_m,
            errors.current.lateral_m,
        )
        desired_point = (
            target_depth,
            errors.current.lateral_m,
        )
        current_range = math.hypot(*current_point)
        current_bearing = math.degrees(
            math.atan2(current_point[1], current_point[0])
        )
        relocation = RelocationPlan(
            stage="depth_only",
            reached=False,
            reason=plan.reason,
            current_point=current_point,
            desired_point=desired_point,
            anchor_range_m=current_range,
            orientation_error_deg=0.0,
            bearing_error_deg=current_bearing,
            range_error_m=plan.depth_error_m,
            forward_error_m=plan.depth_error_m,
            lateral_error_m=0.0,
            progress=plan.progress,
            robot_target=robot_target,
            primitives=primitives,
            predicted_minimum_object_range_m=min(
                current_range,
                plan.predicted_range_m,
            ),
            decomposition="depth_only_single_straight_move",
        )
        self.depth_only_move_count += 1
        self.pose_relocation_stage = "depth_only"
        self._start_pose_relocation(relocation)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = DepthOnlyTaskNode()
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
