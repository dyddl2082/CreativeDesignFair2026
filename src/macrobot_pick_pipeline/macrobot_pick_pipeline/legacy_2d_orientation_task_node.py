"""Camera-authoritative task node with pre-full-3D style orientation policy.

Policy origin:
- 9b2970d introduced early ``orientation_3d`` metadata/work.
- 441df9b is the first known commit that adds explicit ``orientation-mode`` and
  ``min-3d-orientation-samples`` switches, i.e. the behavioral full-3D cutoff.
- This node intentionally recreates the pre-441df9b policy on top of the current
  search, fresh-observation, localization, IK, safe-region and grasp stack.

Only ``stable.orientation_deg`` (the legacy 2D/image-axis value) is consulted.
No face normal or 3D orientation field is read by this node.
"""

from __future__ import annotations

from dataclasses import replace
import math
import time
from typing import Any, Dict, Mapping

import rclpy

from .alignment_core import alignment_errors, observation_constraint_decision
from .camera_authoritative_task_node import CameraAuthoritativeTaskNode
from .camera_pose_relocation import MotionPrimitive, RelocationPlan, relative_pose_from_primitives
from .legacy_2d_controller import Legacy2DPlan, choose_legacy_2d_plan

PATCH_MARKER = "macrobot_legacy_2d_orientation_v8_2"


class Legacy2DOrientationTaskNode(CameraAuthoritativeTaskNode):
    """Keep modern perception/search, but use bounded advisory 2D orientation."""

    def __init__(self) -> None:
        self.legacy2d_orientation_corrections = 0
        self.legacy2d_alignment_confirmations = 0
        self.legacy2d_last_plan: dict[str, object] = {}
        self.legacy2d_parent_handoff_pending = False
        self.legacy2d_parent_handoff_count = 0
        super().__init__()
        self._publish_status(
            "legacy2d_orientation_controller_ready",
            policy="pre_full_3d_soft_2d_orientation",
            historical_cutoff="before_441df9bc65aec487ab5ce83156f6a403926b441b",
            reference_commit="441df9b^1 (resolved by installer)",
            uses_face_normal=False,
            uses_3d_orientation=False,
            uses_2d_orientation_deg=True,
        )
        self.get_logger().warning(
            "Legacy 2D orientation policy active: 3D face-normal alignment is bypassed; "
            "2D orientation is advisory and correction-budgeted"
        )

    def _declare_parameters(self) -> None:
        super()._declare_parameters()
        defaults: Dict[str, Any] = {
            "legacy2d_enabled": True,
            "legacy2d_bearing_tolerance_deg": 6.0,
            "legacy2d_forward_tolerance_m": 0.010,
            "legacy2d_lateral_tolerance_m": 0.060,
            "legacy2d_position_turn_max_deg": 10.0,
            "legacy2d_position_move_max_m": 0.050,
            "legacy2d_position_progress": 0.85,
            "legacy2d_allow_reverse": True,
            "legacy2d_reverse_max_m": 0.020,
            "legacy2d_orientation_enabled": True,
            "legacy2d_orientation_trigger_deg": 18.0,
            "legacy2d_orientation_turn_max_deg": 7.0,
            "legacy2d_orientation_min_quality": 0.35,
            "legacy2d_orientation_max_corrections": 2,
            "legacy2d_confirmation_count": 1,
            "legacy2d_fallback_to_current_controller": False,
        }
        for name, value in defaults.items():
            self.declare_parameter(name, value)

    def _orientation_required(self) -> bool:
        # Prevent inherited full-3D orientation from becoming a hard acceptance
        # requirement.  This node handles the legacy 2D hint in _try_alignment_step.
        return False

    def _status_payload(self, event: str, ok: bool, details: Mapping[str, Any]):
        payload = super()._status_payload(event, ok, details)
        payload.update(
            {
                "legacy2d_enabled": bool(self.get_parameter("legacy2d_enabled").value),
                "legacy2d_orientation_corrections": self.legacy2d_orientation_corrections,
                "legacy2d_alignment_confirmations": self.legacy2d_alignment_confirmations,
                "legacy2d_last_plan": dict(self.legacy2d_last_plan),
                "legacy2d_uses_3d_orientation": False,
                "legacy2d_parent_handoff_pending": bool(self.legacy2d_parent_handoff_pending),
                "legacy2d_parent_handoff_count": int(self.legacy2d_parent_handoff_count),
            }
        )
        return payload

    def _reset_action_state(self) -> None:
        super()._reset_action_state()
        self.legacy2d_orientation_corrections = 0
        self.legacy2d_alignment_confirmations = 0
        self.legacy2d_last_plan = {}
        self.legacy2d_parent_handoff_pending = False
        self.legacy2d_parent_handoff_count = 0

    def _begin_visual_approach(self, stable) -> None:
        super()._begin_visual_approach(stable)
        self.legacy2d_orientation_corrections = 0
        self.legacy2d_alignment_confirmations = 0
        self.legacy2d_last_plan = {}
        self.legacy2d_parent_handoff_pending = False
        self.legacy2d_parent_handoff_count = 0
        self._publish_status(
            "legacy2d_alignment_started",
            reference_point_base=list(self.profile.alignment.reference_point_base),
            reference_orientation_deg=float(self.orientation_reference_deg),
            policy="position_first_then_at_most_two_small_2d_orientation_turns",
        )

    @staticmethod
    def _plan_payload(plan: Legacy2DPlan) -> dict[str, object]:
        return {
            "stage": plan.stage,
            "reached": plan.reached,
            "blocked": plan.blocked,
            "reason": plan.reason,
            "command_kind": plan.command_kind,
            "command_amount": plan.command_amount,
            "command_yaw_deg": plan.command_yaw_deg,
            "current_forward_m": plan.current_forward_m,
            "current_lateral_m": plan.current_lateral_m,
            "reference_forward_m": plan.reference_forward_m,
            "reference_lateral_m": plan.reference_lateral_m,
            "forward_error_m": plan.forward_error_m,
            "lateral_error_m": plan.lateral_error_m,
            "bearing_error_deg": plan.bearing_error_deg,
            "orientation_error_deg": plan.orientation_error_deg,
            "orientation_quality": plan.orientation_quality,
            "orientation_corrections_used": plan.orientation_corrections_used,
            "orientation_source": "stable.orientation_deg_2d_only",
            "face_normal_used": False,
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
                "legacy2d_visual_target_lost",
                next="restart_full_search",
            )
            self._restart_full_search("visual target lost during legacy 2D alignment")

    def _complete_alignment(self, stable, plan: Legacy2DPlan) -> None:
        """Finish legacy geometry, then hand alignment ownership back to parent.

        v8.1 called ``_alignment_complete()`` directly after consuming the stable
        observation.  The current camera-authoritative parent owns an additional
        fresh-visual/finalization state machine.  Directly calling the terminal
        hook therefore starved that state machine: every new stable frame was
        consumed by this subclass, ``legacy2d_alignment_confirmations`` kept
        increasing, while the parent's ``final_visual_confirmations`` remained
        zero.

        v8.2 performs an explicit state handoff instead.  From the next timer
        iteration onward ``super()._try_alignment_step()`` owns fresh detections
        and can execute its normal final-visual -> semantic-preflight -> grasp
        transition.  ``_orientation_required()`` remains overridden to False, so
        this handoff does not restore the full-3D orientation hard requirement.
        """
        self.legacy2d_alignment_confirmations += 1
        required = max(1, int(self.get_parameter("legacy2d_confirmation_count").value))
        if self.legacy2d_alignment_confirmations < required:
            self.filter.clear()
            self._publish_status(
                "legacy2d_alignment_confirmation",
                confirmation=self.legacy2d_alignment_confirmations,
                required=required,
                plan=self._plan_payload(plan),
            )
            return

        self.latest_stable_detection = stable
        self.last_object_point = stable.point_base
        self.legacy2d_parent_handoff_pending = True
        self.legacy2d_parent_handoff_count += 1

        # Do not feed the just-consumed frame back as a supposedly fresh final
        # confirmation.  The parent receives the next actual stable observation.
        self.cached_stable_detection = None
        self.filter.clear()
        self._publish_status(
            "legacy2d_alignment_handoff_to_parent",
            final_plan=self._plan_payload(plan),
            orientation_policy="soft_2d_advisory",
            next="parent_fresh_visual_confirmation_then_semantic_preflight_and_grasp",
            direct_alignment_complete_call=False,
        )

    def _try_alignment_step(self) -> None:
        if self.legacy2d_parent_handoff_pending:
            # Critical v8.2 fix: once legacy geometry has been accepted, stop
            # consuming stable frames in this subclass.  Let the current
            # camera-authoritative implementation own its final fresh-visual
            # confirmation and the semantic-preflight/grasp transition.
            super()._try_alignment_step()
            return
        if not bool(self.get_parameter("legacy2d_enabled").value):
            super()._try_alignment_step()
            return
        if self.profile is None or self.base_active or self.pose_relocation_active:
            return

        stable = self._stable_or_cached_detection()
        if stable is None:
            self._handle_missing_detection()
            return

        # Keep current depth/localization quality gates, but explicitly remove
        # all hard orientation matching so 3D face-normal fields cannot reject.
        basic_profile = replace(self.profile.alignment, require_orientation_match=False)
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
            self.legacy2d_alignment_confirmations = 0
            self.filter.clear()
            self._publish_status(
                "legacy2d_observation_rejected",
                reason=constraint.reason,
                orientation_is_not_a_rejection_reason=True,
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
                "TARGET_POSE_INVALID", str(error), resume_mode="search"
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

        current_orientation = getattr(stable, "orientation_deg", None)
        reference_orientation = getattr(self, "orientation_reference_deg", None)
        try:
            current_orientation = float(current_orientation)
            if not math.isfinite(current_orientation):
                current_orientation = None
        except (TypeError, ValueError):
            current_orientation = None
        try:
            reference_orientation = float(reference_orientation)
            if not math.isfinite(reference_orientation):
                reference_orientation = None
        except (TypeError, ValueError):
            reference_orientation = None

        plan = choose_legacy_2d_plan(
            (errors.current.forward_m, errors.current.lateral_m),
            (errors.reference.forward_m, errors.reference.lateral_m),
            current_orientation_deg=current_orientation,
            reference_orientation_deg=reference_orientation,
            orientation_quality=float(getattr(stable, "orientation_quality", 0.0) or 0.0),
            orientation_corrections_used=self.legacy2d_orientation_corrections,
            bearing_tolerance_deg=float(self.get_parameter("legacy2d_bearing_tolerance_deg").value),
            forward_tolerance_m=float(self.get_parameter("legacy2d_forward_tolerance_m").value),
            lateral_tolerance_m=float(self.get_parameter("legacy2d_lateral_tolerance_m").value),
            position_turn_max_deg=float(self.get_parameter("legacy2d_position_turn_max_deg").value),
            position_move_max_m=float(self.get_parameter("legacy2d_position_move_max_m").value),
            position_progress=float(self.get_parameter("legacy2d_position_progress").value),
            allow_reverse=bool(self.get_parameter("legacy2d_allow_reverse").value),
            reverse_max_m=float(self.get_parameter("legacy2d_reverse_max_m").value),
            orientation_enabled=bool(self.get_parameter("legacy2d_orientation_enabled").value),
            orientation_trigger_deg=float(self.get_parameter("legacy2d_orientation_trigger_deg").value),
            orientation_turn_max_deg=float(self.get_parameter("legacy2d_orientation_turn_max_deg").value),
            orientation_min_quality=float(self.get_parameter("legacy2d_orientation_min_quality").value),
            orientation_max_corrections=int(self.get_parameter("legacy2d_orientation_max_corrections").value),
        )
        self.legacy2d_last_plan = self._plan_payload(plan)
        self.latest_stable_detection = stable
        self.last_object_point = stable.point_base
        self._publish_status(
            "legacy2d_camera_comparison",
            plan=dict(self.legacy2d_last_plan),
            three_d_orientation_ignored=True,
            face_normal_ignored=True,
        )

        if plan.reached:
            self._complete_alignment(stable, plan)
            return
        self.legacy2d_alignment_confirmations = 0
        if plan.blocked:
            if bool(self.get_parameter("legacy2d_fallback_to_current_controller").value):
                self._publish_status(
                    "legacy2d_fallback_to_current_controller",
                    reason=plan.reason,
                )
                super()._try_alignment_step()
                return
            self._enter_recovery_hold(
                "TARGET_POSE_NOT_CORRECTABLE",
                f"legacy 2D controller stopped: {plan.reason}",
                resume_mode="align",
                legacy2d_plan=dict(self.legacy2d_last_plan),
            )
            return

        if plan.command_kind == "turn":
            primitive = MotionPrimitive("turn", 0.0, plan.command_yaw_deg)
            if plan.stage == "orientation_soft":
                self.legacy2d_orientation_corrections += 1
        elif plan.command_kind == "move":
            primitive = MotionPrimitive("move", plan.command_amount, 0.0)
        else:
            self._enter_recovery_hold(
                "TARGET_POSE_INVALID",
                "legacy 2D planner produced no executable primitive",
                resume_mode="align",
            )
            return

        primitives = (primitive,)
        robot_target = relative_pose_from_primitives(primitives)
        current_point = (errors.current.forward_m, errors.current.lateral_m)
        reference_point = (errors.reference.forward_m, errors.reference.lateral_m)
        current_range = math.hypot(*current_point)
        reference_range = math.hypot(*reference_point)
        relocation = RelocationPlan(
            stage=f"legacy2d_{plan.stage}",
            reached=False,
            reason=plan.reason,
            current_point=current_point,
            desired_point=reference_point,
            anchor_range_m=current_range,
            orientation_error_deg=(
                plan.orientation_error_deg if math.isfinite(plan.orientation_error_deg) else 0.0
            ),
            bearing_error_deg=plan.bearing_error_deg,
            range_error_m=current_range - reference_range,
            forward_error_m=plan.forward_error_m,
            lateral_error_m=plan.lateral_error_m,
            progress=1.0,
            robot_target=robot_target,
            primitives=primitives,
            predicted_minimum_object_range_m=max(0.0, min(current_range, reference_range)),
            decomposition=f"legacy2d_single_{plan.command_kind}",
        )
        self.pose_relocation_stage = f"legacy2d_{plan.stage}"
        self._start_pose_relocation(relocation)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = Legacy2DOrientationTaskNode()
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
