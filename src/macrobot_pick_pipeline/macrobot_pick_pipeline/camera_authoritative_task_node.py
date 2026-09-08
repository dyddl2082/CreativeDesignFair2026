"""Camera-authoritative stored-object task orchestration for MacRobot.

This execution policy intentionally removes persistent Pico odometry from all
high-level decisions.  The camera owns target acquisition, docking, orientation
alignment and the final pre-grasp pose.  Encoder-backed ``MOVE_CM`` and
``TURN_DEG`` remain short, bounded actuators only:

1. measure the current object error with RGB-D,
2. execute one short motion,
3. discard every image captured before motion completion,
4. measure again,
5. reverse/correct until the camera error is within tolerance.

The node keeps the public stored-object topics and profile adapter so existing
Gateway/UI code can continue to use ``run`` and ``visible-test``.  The legacy
``resilient_object_task_node`` remains available as a rollback executable.
"""

from __future__ import annotations

from dataclasses import replace
import json
import math
import time
from typing import Any, Dict, Mapping, Optional

import rclpy
from std_msgs.msg import String

from .alignment_core import (
    AlignmentProfile,
    alignment_errors,
    observation_constraint_decision,
    pico_move_command_cm,
    pico_turn_command_deg,
)
from .orientation_control import OrientationAssessment
from .orientation_domain import (
    axis_from_mapping,
    is_measured_base_axis_orientation,
)
from .precision_docking import choose_precision_docking_action, precision_errors
from .camera_pose_relocation import (
    MotionPrimitive,
    RelocationPlan,
    plan_range_relocation,
    plan_viewpoint_relocation,
)
from .fast_visual_docking import (
    choose_fast_camera_docking_action,
    direct_axis_turn_deg,
    orientation_engagement_ready,
)
from .resilient_object_task_node import ResilientObjectTaskNode
from .stored_object_core import (
    OdomPose,
    StoredObjectRuntimeProfile,
    planar_range_m,
    utc_now_iso,
)
from .stored_object_pick_node import (
    BASE_MOTION_EVENTS,
    TERMINAL_STATES,
    _json_object,
    _point_from_payload,
)


def _camera_grasp_point_from_payload(value: object):
    # camera_grasp_point_payload_compatibility_v1
    # The legacy stored-object parser accepts {"x", "y", "z"} mappings.
    # Integrated teaching originally sent [x, y, z].  Accept both so mixed
    # client/server versions cannot silently discard a valid camera point.
    point = _point_from_payload(value)
    if point is not None:
        return point
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        return None
    try:
        candidate = tuple(float(item) for item in value)
    except (TypeError, ValueError):
        return None
    if not all(math.isfinite(item) for item in candidate):
        return None
    return candidate


class CameraAuthoritativeTaskNode(ResilientObjectTaskNode):
    """Vision-first task node with no persistent-odometry navigation authority."""

    def __init__(self) -> None:
        self.place_side_turn_target_deg = 0.0
        self.place_side_turn_completed_deg = 0.0
        self.place_side_turn_remaining_deg = 0.0
        # The parent constructor dynamically calls status/reset helpers.
        self.final_visual_confirmations = 0
        self.final_visual_started_at = 0.0
        self.camera_motion_sequence = 0
        self.camera_motion_completed_at = 0.0
        # fast_camera_docking_v1
        self.fast_docking_phase = "coarse"
        self.fast_translation_streak = 0
        # camera_reset_pose_relocation_v1
        self.pose_relocation_stage = "viewpoint"
        self.pose_relocation_anchor_range_m = 0.0
        self.pose_relocation_stage_confirmations = 0
        self.pose_relocation_iteration = 0
        self.pose_relocation_active = False
        self.pose_relocation_queue: list[MotionPrimitive] = []
        self.pose_relocation_completed: list[dict[str, object]] = []
        self.pose_relocation_plan: Optional[RelocationPlan] = None
        self.pose_relocation_purpose = ""
        self.pose_relocation_primitive_index = 0
        super().__init__()
        self._publish_status(
            "camera_authoritative_tasks_ready",
            execution_authority="fresh_rgbd_localization",
            persistent_odometry_used=False,
            encoder_role="proportional_relative_pose_actuation_only",
            teaching_workflow="camera_reference_plus_semantic_keyframes",
        )
        self.get_logger().info(
            "Camera-authoritative task policy ready: one fresh RGB-D reset after each compound relative-pose manoeuvre"
        )

    def _declare_parameters(self) -> None:
        super()._declare_parameters()
        defaults: Dict[str, Any] = {
            "camera_authoritative_mode": True,
            "camera_record_min_orientation_quality": 0.45,
            "camera_record_max_point_radius_m": 0.008,
            "camera_record_max_orientation_spread_deg": 8.0,
            "camera_final_visual_confirmation_count": 2,
            "camera_final_visual_lost_restart_sec": 8.0,
            "camera_motion_frame_guard_sec": 0.25,
            "camera_max_translation_chunk_m": 0.012,
            "camera_search_backoff_chunk_m": 0.020,
            "camera_max_turn_chunk_deg": 4.0,
            "camera_search_turn_chunk_deg": 10.0,
            "camera_disable_location_memory": True,
            "camera_disable_distance_handoff": True,
            "camera_allow_legacy_record_commands": False,
            "camera_profile_position_scope": "camera_relative",
            # fast_camera_docking_v1
            # Keep the depth-assisted orientation path, but leave the unrelated
            # coarse-to-fine speed controller disabled by default.
            "fast_docking_enabled": False,
            "fast_coarse_move_chunk_m": 0.030,
            "fast_coarse_bearing_tolerance_deg": 4.0,
            "fast_emergency_bearing_tolerance_deg": 7.0,
            "fast_coarse_lateral_tolerance_m": 0.025,
            "fast_coarse_turn_chunk_deg": 6.0,
            "fast_final_forward_band_m": 0.035,
            "fast_max_translation_streak": 3,
            "fast_orientation_engage_forward_m": 0.025,
            "fast_orientation_engage_lateral_m": 0.015,
            "fast_orientation_engage_bearing_deg": 3.0,
            "fast_direct_3d_orientation_enabled": False,
            "fast_direct_3d_turn_gain": 1.0,
            "fast_direct_3d_turn_max_deg": 6.0,
            "fast_direct_3d_turn_min_deg": 0.75,
            "fast_coarse_settle_sec": 0.20,
            "fast_final_settle_sec": 0.35,
            "fast_reobserve_sec": 0.30,
        }
        for name, value in defaults.items():
            self.declare_parameter(name, value)
        # camera_reset_pose_relocation_v1
        relocation_defaults: Dict[str, Any] = {
# pose_relocation_emergency_disable_2026_09_08
            "pose_relocation_enabled": False,
            "pose_relocation_viewpoint_gain": 0.25,
            "pose_relocation_range_gain": 0.35,
            "pose_relocation_orbit_bearing_tolerance_deg": 5.0,
            "pose_relocation_orbit_range_tolerance_m": 0.025,
            "pose_relocation_orientation_reentry_deg": 6.0,
            "pose_relocation_viewpoint_confirmation_count": 1,
            "pose_relocation_max_viewpoint_translation_m": 0.03,
            "pose_relocation_max_range_translation_m": 0.02,
            "pose_relocation_max_turn_primitive_deg": 8.0,
            "pose_relocation_minimum_object_range_m": 0.1,
            "pose_relocation_allow_reverse": False,
            "pose_relocation_reverse_turn_penalty_deg": 10.0,
            "pose_relocation_min_turn_deg": 0.5,
            "pose_relocation_min_move_m": 0.003,
            "pose_relocation_settle_sec": 0.2,
            "pose_relocation_reobserve_sec": 0.25,
            "pose_relocation_clearance_heading_limit_deg": 20.0,
            "pose_relocation_prefer_drive_rel": False,
            "pose_relocation_max_drive_yaw_deg": 6.0,
            "pose_relocation_min_drive_radius_m": 0.08,
            "pose_relocation_drive_speed": 0,
        }
        for name, value in relocation_defaults.items():
            self.declare_parameter(name, value)

        # PLACE_SIDE_TURN_CAMERA_POLICY_V1_1
        place_side_turn_defaults: Dict[str, Any] = {
            "place_side_turn_enabled": True,
            "place_side_turn_deg": 15.0,
            "place_side_turn_chunk_deg": 4.0,
            "place_side_turn_max_abs_deg": 30.0,
            "place_side_turn_finish_tolerance_deg": 0.05,
        }
        for name, value in place_side_turn_defaults.items():
            self.declare_parameter(name, value)
        # PLACE_REFERENCE_UNIFIED_SEARCH_V1
        if not self.has_parameter("place_reference_keep_finder_on_lost"):
            self.declare_parameter("place_reference_keep_finder_on_lost", True)
    def _status_payload(
        self,
        event: str,
        ok: bool,
        details: Mapping[str, Any],
    ) -> Dict[str, Any]:
        payload = super()._status_payload(event, ok, details)
        payload.update(
            {
                "execution_authority": "fresh_rgbd_localization",
                "persistent_odometry_used": False,
                "encoder_role": "proportional_relative_pose_actuation_and_fault_detection",
                "camera_motion_sequence": self.camera_motion_sequence,
                "final_visual_confirmations": self.final_visual_confirmations,
                "distance_handoff_active": False,
                "fast_docking_phase": self.fast_docking_phase,
                "fast_translation_streak": self.fast_translation_streak,
            }
        )
        # camera_reset_pose_relocation_v1
        payload.update(
            {
                "pose_relocation_enabled": bool(
                    self.get_parameter("pose_relocation_enabled").value
                ),
                "pose_relocation_stage": self.pose_relocation_stage,
                "pose_relocation_anchor_range_m": (
                    self.pose_relocation_anchor_range_m
                ),
                "pose_relocation_iteration": self.pose_relocation_iteration,
                "pose_relocation_compound_active": self.pose_relocation_active,
            }
        )
        return payload

    def _reset_action_state(self) -> None:
        self.place_side_turn_target_deg = 0.0
        self.place_side_turn_completed_deg = 0.0
        self.place_side_turn_remaining_deg = 0.0
        super()._reset_action_state()
        self.final_visual_confirmations = 0
        self.final_visual_started_at = 0.0
        self.camera_motion_sequence = 0
        self.camera_motion_completed_at = 0.0
        self.fast_docking_phase = "coarse"
        self.fast_translation_streak = 0
        # Explicitly invalidate all pose-like state.  Individual Pico motion
        # results may still contain odometry fields, but this policy never uses
        # them to predict an object point or reproduce a stored pose.
        self.last_odom = None
        self.last_visual_object_odom = None
        # camera_reset_pose_relocation_v1
        self.pose_relocation_stage = "viewpoint"
        self.pose_relocation_anchor_range_m = 0.0
        self.pose_relocation_stage_confirmations = 0
        self.pose_relocation_iteration = 0
        self.pose_relocation_active = False
        self.pose_relocation_queue = []
        self.pose_relocation_completed = []
        self.pose_relocation_plan = None
        self.pose_relocation_purpose = ""
        self.pose_relocation_primitive_index = 0

    # ------------------------------------------------------------------
    # Camera-only profile teaching commit
    # ------------------------------------------------------------------
    def _record_callback(self, msg: String) -> None:
        try:
            request = _json_object(msg.data)
        except Exception:
            super()._record_callback(msg)
            return
        stage = str(request.get("record_stage", "")).strip().casefold()
        if stage in {"camera_grasp", "camera_grasp_commit"}:
            self._commit_camera_grasp_profile(request)
            return
        if bool(
            self.get_parameter("camera_allow_legacy_record_commands").value
        ):
            super()._record_callback(msg)
            return

        request_id = str(
            request.get("request_id", f"camera-record-reject-{int(time.time() * 1000)}")
        )
        object_name = str(request.get("object_name", "")).strip()
        profile_name = str(request.get("profile", object_name)).strip()
        self._publish_command_rejection(
            event="camera_authoritative_teaching_required",
            legacy_event="alignment_profile_record_failed",
            request_id=request_id,
            object_name=object_name,
            profile=profile_name,
            mode=f"record_{stage or 'legacy'}",
            execute_pick=False,
            error_code="INVALID_ARGUMENT",
            reason=(
                "odometry-based record-search/record-grasp is disabled; "
                "use camera_grasp_teach_cli so grasp position and all semantic "
                "keyframes share one RGB-D reference"
            ),
        )

    def _camera_profile_template(
        self,
        *,
        profile_name: str,
        object_name: str,
        pick_profile: str,
        keyframe_profile: str,
    ) -> StoredObjectRuntimeProfile:
        alignment = AlignmentProfile(
            **{
                **self.default_alignment.__dict__,
                "name": profile_name,
                "object_name": object_name,
                "pick_profile": pick_profile,
            }
        )
        placeholder = OdomPose(0.0, 0.0, 0.0, False, None)
        return StoredObjectRuntimeProfile(
            name=profile_name,
            object_name=object_name,
            recorded_at=utc_now_iso(),
            search_pose_odom=placeholder,
            object_point_odom=(0.0, 0.0, 0.0),
            alignment=alignment,
            grasp_pose_odom=placeholder,
            recognition_point_base=None,
            recognition_score=0.0,
            recording_state="complete",
            grasp_executor="keyframes",
            grasp_keyframe_profile=keyframe_profile,
            pick_profile=pick_profile,
            position_scope="camera_relative",
            distance_handoff_enabled=False,
            recognition_min_range_m=float(
                self.get_parameter("recognition_min_range_m").value
            ),
            recognition_max_range_m=float(
                self.get_parameter("recognition_max_range_m").value
            ),
            graspable_min_range_m=float(
                self.get_parameter("graspable_min_range_m").value
            ),
            graspable_max_range_m=float(
                self.get_parameter("graspable_max_range_m").value
            ),
            approach_position_tolerance_m=float(
                self.get_parameter("approach_position_tolerance_m").value
            ),
            approach_angle_tolerance_deg=float(
                self.get_parameter("approach_angle_tolerance_deg").value
            ),
            approach_max_move_step_m=float(
                self.get_parameter("approach_max_move_step_m").value
            ),
            approach_max_turn_step_deg=float(
                self.get_parameter("approach_max_turn_step_deg").value
            ),
            approach_max_iterations=int(
                self.get_parameter("approach_max_iterations").value
            ),
            approach_max_total_move_m=float(
                self.get_parameter("approach_max_total_move_m").value
            ),
            approach_max_total_turn_deg=float(
                self.get_parameter("approach_max_total_turn_deg").value
            ),
            base_linear_error_fraction=0.0,
            base_turn_error_fraction=0.0,
            turn_translation_drift_m_per_360=0.0,
            maximum_handoff_uncertainty_m=0.001,
            maximum_object_relocation_m=float(
                self.get_parameter("maximum_object_relocation_m").value
            ),
        )

    def _commit_camera_grasp_profile(self, request: Mapping[str, Any]) -> None:
        request_id = str(
            request.get("request_id", f"camera-grasp-{int(time.time() * 1000)}")
        )
        object_name = str(request.get("object_name", "")).strip()
        profile_name = str(request.get("profile", object_name)).strip()
        keyframe_profile = str(
            request.get("grasp_keyframe_profile", request.get("keyframes", ""))
        ).strip()
        pick_profile = str(request.get("pick_profile", object_name)).strip()
        try:
            if self._is_busy():
                if request_id == self.request_id and self.mode == "record_camera_grasp":
                    self._publish_status(
                        "stored_object_command_acknowledged",
                        command="camera_grasp_commit",
                        duplicate=True,
                    )
                    return
                raise RuntimeError("another stored-object action is active")
            if not object_name or not profile_name or not keyframe_profile:
                raise ValueError(
                    "object_name, profile and grasp_keyframe_profile are required"
                )
            point = _camera_grasp_point_from_payload(request.get("object_point_base"))
            if point is None:
                raise ValueError("object_point_base is required")
            orientation_raw = request.get("object_orientation", {})
            orientation = orientation_raw if isinstance(orientation_raw, Mapping) else {}
            angle = float(orientation.get("angle_deg", 0.0) or 0.0) % 180.0
            quality = max(
                0.0,
                min(1.0, float(orientation.get("quality", 0.0) or 0.0)),
            )
            orientation_class = str(
                orientation.get("class", "unknown")
            ).strip() or "unknown"
            orientation_source = str(
                orientation.get("source", "")
            ).strip()
            orientation_frame = str(
                orientation.get("coordinate_frame", "")
            ).strip()
            orientation_semantics = str(
                orientation.get("semantics", "")
            ).strip()
            orientation_axis_base = axis_from_mapping(
                orientation.get("axis_base")
            )
            if not math.isfinite(angle) or not math.isfinite(quality):
                raise ValueError("object orientation contains a non-finite value")
            minimum_quality = float(
                self.get_parameter("camera_record_min_orientation_quality").value
            )
            if orientation_class == "unknown" or quality < minimum_quality:
                raise ValueError(
                    "camera teaching orientation is unreliable: "
                    f"quality={quality:.3f}, required={minimum_quality:.3f}"
                )

            # camera_teaching_no_fixed_distance_gate_v1
            # A camera-authoritative teaching point is accepted at the actual
            # observed pose.  Fixed 0.32 m recognition / 0.30 m grasp gates are
            # legacy distance-handoff assumptions.  Reachability is decided by
            # the semantic keyframe IK and sampled safe-region preflight.
            current_range = planar_range_m(
                point,
                forward_axis_sign=self.forward_axis_sign,
                lateral_axis_sign=self.lateral_axis_sign,
            )
            if not math.isfinite(current_range) or current_range <= 0.0:
                raise ValueError("camera teaching point has an invalid range")

            self.keyframe_store.reload()
            keyframes = self.keyframe_store.get(keyframe_profile)
            keyframes.validate()
            if keyframes.object_name.casefold() != object_name.casefold():
                raise ValueError("keyframe object_name does not match stored profile object")

            try:
                base = self.profile_store.get(profile_name, object_name)
            except KeyError:
                base = self._camera_profile_template(
                    profile_name=profile_name,
                    object_name=object_name,
                    pick_profile=pick_profile,
                    keyframe_profile=keyframe_profile,
                )

            placeholder = OdomPose(0.0, 0.0, 0.0, False, None)
            alignment = base.alignment.with_reference(
                point,
                object_name=object_name,
                pick_profile=pick_profile,
                orientation_deg=angle,
                orientation_class=orientation_class,
                orientation_quality=quality,
                orientation_source=orientation_source,
                orientation_frame=orientation_frame,
                orientation_semantics=orientation_semantics,
                orientation_axis_base=orientation_axis_base,
                require_orientation_match=True,
            )
            stored = replace(
                base,
                name=profile_name,
                object_name=object_name,
                recorded_at=utc_now_iso(),
                search_pose_odom=placeholder,
                object_point_odom=(0.0, 0.0, float(point[2])),
                alignment=alignment,
                grasp_pose_odom=placeholder,
                recognition_point_base=point,
                recognition_score=max(
                    0.0,
                    min(1.0, float(request.get("score", 0.0) or 0.0)),
                ),
                recording_state="complete",
                grasp_executor="keyframes",
                grasp_trajectory="",
                grasp_keyframe_profile=keyframe_profile,
                pick_profile=pick_profile,
                position_scope="camera_relative",
                distance_handoff_enabled=False,
                base_linear_error_fraction=0.0,
                base_turn_error_fraction=0.0,
                turn_translation_drift_m_per_360=0.0,
                maximum_handoff_uncertainty_m=0.001,
            )
            stored.validate_for_execution(
                forward_axis_sign=self.forward_axis_sign,
                lateral_axis_sign=self.lateral_axis_sign,
            )
        except Exception as error:
            self._publish_command_rejection(
                event="camera_grasp_teaching_rejected",
                legacy_event="alignment_profile_record_failed",
                request_id=request_id,
                object_name=object_name,
                profile=profile_name,
                mode="record_camera_grasp",
                execute_pick=False,
                error_code=(
                    "RESOURCE_BUSY" if isinstance(error, RuntimeError) else "INVALID_ARGUMENT"
                ),
                reason=str(error),
            )
            return

        self._reset_action_state()
        self.request_id = request_id
        self.object_name = object_name
        self.profile_name = profile_name
        self.profile = stored
        self.mode = "record_camera_grasp"
        self.execute_pick = False
        self.state = "SUCCEEDED"
        self.phase = "record_camera_grasp_completed"
        self.profile_store.upsert(stored)
        self._publish_status(
            "stored_object_command_acknowledged",
            command="camera_grasp_commit",
            duplicate=False,
        )
        self._publish_result(
            "camera_grasp_teaching_committed",
            True,
            "alignment_profile_recorded",
            profile_mapping=stored.to_mapping(),
            profile_file=str(self.profile_store.path),
            reference_source="locked_camera_teaching_reference",
            persistent_odometry_used=False,
            fixed_distance_gate_used=False,
            measured_reference_range_m=current_range,
            reachability_authority="semantic_keyframe_ik_and_safe_region",
        )
        self._publish_status(
            "camera_grasp_teaching_committed",
            profile_mapping=stored.to_mapping(),
            fixed_distance_gate_used=False,
            measured_reference_range_m=current_range,
            reachability_authority="semantic_keyframe_ik_and_safe_region",
        )

    # ------------------------------------------------------------------
    # No persistent odometry in search or visual docking
    # ------------------------------------------------------------------
    def _after_stow(self) -> None:
        self._start_resilient_search()

    def _request_odom(self, purpose: str) -> None:
        # Camera-authoritative mode never asks for a persistent global pose.
        # Encoder counts remain inside each bounded MOVE_CM/TURN_DEG command.
        if purpose == "resilient_search_start":
            self._publish_status(
                "persistent_odometry_request_suppressed",
                purpose=purpose,
                next="current_camera_view_then_rotation_search",
            )
            self._start_resilient_search()
            return
        self._fail(
            "INTERNAL_ERROR",
            reason=(
                "camera-authoritative mode attempted an unsupported persistent "
                f"odometry request: {purpose}"
            ),
        )

    def _start_resilient_search(self) -> None:
        # Suppress location-memory use in the inherited bounded-rotation search.
        self.last_odom = None
        self.last_visual_object_odom = None
        super()._start_resilient_search()
        self.location_hint_state = "disabled"
        self.location_hint_reason = "camera_authoritative_mode"
        self._publish_status(
            "camera_authoritative_search_started",
            stored_pose_return=False,
            location_memory_used=False,
            distance_handoff_used=False,
            scan_rotation_accounting="successful_encoder_bounded_turn_commands",
        )

    def _robot_moved_since(self, wall_sec: float) -> bool:
        # We never use odometry to transform an old camera point across motion.
        # Frames predating the motion boundary are rejected instead.
        del wall_sec
        return False

    def _process_pending_detections(self) -> None:
        queued = len(self.pending_detections)
        self.pending_detections.clear()
        if queued:
            self._publish_status(
                "motion_boundary_perception_discarded",
                queued=queued,
                accepted=0,
                policy="discard_pre_motion_frames_wait_for_fresh_rgbd",
            )

    def _update_visual_anchor(self, stable) -> None:
        self.last_object_point = stable.point_base
        self.latest_stable_detection = stable
        self.last_visual_wall_sec = time.time()
        self.deadreckon_since_visual_m = 0.0
        self.require_fresh_after_turn = False
        self.last_visual_object_odom = None

    def _remember_observation_point(self, *args, **kwargs) -> None:
        # Persistent odometry locations are intentionally not updated.
        del args, kwargs

    def _predicted_point(self):
        return None

    def _relocation_common_kwargs(self, stable, errors, *, stage: str):
        assert self.profile is not None
        if stage == "viewpoint":
            progress = float(
                self.get_parameter("pose_relocation_viewpoint_gain").value
            )
            maximum_translation = float(
                self.get_parameter(
                    "pose_relocation_max_viewpoint_translation_m"
                ).value
            )
        else:
            progress = float(
                self.get_parameter("pose_relocation_range_gain").value
            )
            maximum_translation = float(
                self.get_parameter(
                    "pose_relocation_max_range_translation_m"
                ).value
            )
        return {
            "current_object_xy": (
                errors.current.forward_m,
                errors.current.lateral_m,
            ),
            "reference_object_xy": (
                errors.reference.forward_m,
                errors.reference.lateral_m,
            ),
            "current_orientation_deg": stable.orientation_deg,
            "reference_orientation_deg": self.orientation_reference_deg,
            "anchor_range_m": self.pose_relocation_anchor_range_m,
            "orientation_tolerance_deg": float(
                self.get_parameter(
                    "precision_orientation_tolerance_deg"
                ).value
            ),
            "orbit_bearing_tolerance_deg": float(
                self.get_parameter(
                    "pose_relocation_orbit_bearing_tolerance_deg"
                ).value
            ),
            "orbit_range_tolerance_m": float(
                self.get_parameter(
                    "pose_relocation_orbit_range_tolerance_m"
                ).value
            ),
            "forward_tolerance_m": float(
                self.get_parameter("precision_forward_tolerance_m").value
            ),
            "lateral_tolerance_m": float(
                self.get_parameter("precision_lateral_tolerance_m").value
            ),
            "requested_progress": progress,
            "maximum_translation_m": maximum_translation,
            "maximum_turn_primitive_deg": float(
                self.get_parameter(
                    "pose_relocation_max_turn_primitive_deg"
                ).value
            ),
            "minimum_object_range_m": float(
                self.get_parameter(
                    "pose_relocation_minimum_object_range_m"
                ).value
            ),
            "allow_reverse": bool(
                self.get_parameter("pose_relocation_allow_reverse").value
            ),
            "reverse_turn_penalty_deg": float(
                self.get_parameter(
                    "pose_relocation_reverse_turn_penalty_deg"
                ).value
            ),
            "minimum_turn_deg": float(
                self.get_parameter("pose_relocation_min_turn_deg").value
            ),
            "minimum_move_m": float(
                self.get_parameter("pose_relocation_min_move_m").value
            ),
            "prefer_drive_rel": bool(
                self.get_parameter("pose_relocation_prefer_drive_rel").value
            ),
            "maximum_drive_yaw_deg": float(
                self.get_parameter(
                    "pose_relocation_max_drive_yaw_deg"
                ).value
            ),
            "minimum_drive_radius_m": float(
                self.get_parameter(
                    "pose_relocation_min_drive_radius_m"
                ).value
            ),
        }
    @staticmethod  # pose_relocation_plan_payload_binding_fix_v1
    def _pose_relocation_plan_payload(plan: RelocationPlan) -> Dict[str, Any]:
        return {
            "stage": plan.stage,
            "reached": plan.reached,
            "reason": plan.reason,
            "decomposition": plan.decomposition,
            "current_point": list(plan.current_point),
            "desired_point": list(plan.desired_point),
            "anchor_range_m": plan.anchor_range_m,
            "orientation_error_deg": plan.orientation_error_deg,
            "bearing_error_deg": plan.bearing_error_deg,
            "range_error_m": plan.range_error_m,
            "forward_error_m": plan.forward_error_m,
            "lateral_error_m": plan.lateral_error_m,
            "progress": plan.progress,
            "robot_target": {
                "x_m": plan.robot_target.x_m,
                "y_m": plan.robot_target.y_m,
                "yaw_deg": plan.robot_target.yaw_deg,
            },
            "primitives": [
                {
                    "kind": item.kind,
                    "amount": item.amount,
                    "yaw_deg": item.yaw_deg,
                }
                for item in plan.primitives
            ],
            "total_move_m": plan.total_move_m,
            "total_turn_deg": plan.total_turn_deg,
            "predicted_minimum_object_range_m": (
                plan.predicted_minimum_object_range_m
            ),
        }
    def _clear_pose_relocation_compound(self) -> None:
        self.pose_relocation_active = False
        self.pose_relocation_queue = []
        self.pose_relocation_completed = []
        self.pose_relocation_plan = None
        self.pose_relocation_purpose = ""
        self.pose_relocation_primitive_index = 0
    def _send_pose_relocation_primitive(
        self,
        primitive: MotionPrimitive,
        *,
        purpose: str,
    ) -> None:
        assert self.profile is not None
        timeout = self.profile.alignment.motion_timeout_sec
        if primitive.kind == "turn":
            pico_deg = pico_turn_command_deg(
                primitive.amount,
                pico_positive_is_right=self.pico_turn_positive_is_right,
            )
            command = (
                f"TURN_DEG {pico_deg:.3f} "
                f"{self.profile.alignment.turn_speed} {timeout:.2f}"
            )
            self._start_base_command(
                command,
                "turn_deg_result",
                purpose,
                float(primitive.amount),
            )
            return
        pico_cm = pico_move_command_cm(
            primitive.amount,
            pico_positive_is_forward=self.pico_move_positive_is_forward,
        )
        if primitive.kind == "drive":
            # Pico DRIVE_REL uses yaw positive = left / counter-clockwise,
            # unlike legacy TURN_DEG whose positive sign is normally right.
            configured_speed = int(
                self.get_parameter("pose_relocation_drive_speed").value
            )
            drive_speed = (
                configured_speed
                if configured_speed > 0
                else max(
                    self.profile.alignment.move_speed,
                    self.profile.alignment.turn_speed,
                )
            )
            command = (
                f"DRIVE_REL {pico_cm:.3f} {primitive.yaw_deg:.3f} "
                f"{drive_speed} {timeout:.2f}"
            )
            self._start_base_command(
                command,
                "drive_relative_result",
                purpose,
                float(primitive.amount),
            )
            return
        command = (
            f"MOVE_CM {pico_cm:.3f} "
            f"{self.profile.alignment.move_speed} {timeout:.2f}"
        )
        self._start_base_command(
            command,
            "move_cm_result",
            purpose,
            float(primitive.amount),
        )
    def _dispatch_pose_relocation_primitive(self) -> None:
        if not self.pose_relocation_active or not self.pose_relocation_queue:
            return
        primitive = self.pose_relocation_queue.pop(0)
        self.pose_relocation_primitive_index += 1
        purpose = (
            f"{self.pose_relocation_purpose}_step_"
            f"{self.pose_relocation_primitive_index}_{primitive.kind}"
        )
        self._publish_status(
            "pose_relocation_primitive_started",
            relocation_stage=self.pose_relocation_stage,
            primitive_index=self.pose_relocation_primitive_index,
            primitive_count=(
                self.pose_relocation_primitive_index
                + len(self.pose_relocation_queue)
            ),
            primitive={
                "kind": primitive.kind,
                "amount": primitive.amount,
                "yaw_deg": primitive.yaw_deg,
            },
            camera_observation_between_primitives=False,
        )
        self._send_pose_relocation_primitive(primitive, purpose=purpose)
    def _start_pose_relocation(self, plan: RelocationPlan) -> None:
        if self.base_active or self.pose_relocation_active:
            return
        if not plan.primitives:
            self._enter_recovery_hold(
                "TARGET_POSE_NOT_CORRECTABLE",
                "pose relocation produced no executable primitive",
                resume_mode="align",
            )
            return
        positive_moves = [
            item.amount
            for item in plan.primitives
            if item.kind in {"move", "drive"} and item.amount > 0.0
        ]
        first_heading_change = next(
            (
                abs(
                    item.amount
                    if item.kind == "turn"
                    else item.yaw_deg
                )
                for item in plan.primitives
                if item.kind in {"turn", "drive"}
            ),
            0.0,
        )
        clearance_scope = "target_geometry_only"
        if positive_moves and first_heading_change <= float(
            self.get_parameter(
                "pose_relocation_clearance_heading_limit_deg"
            ).value
        ):
            requested_forward = max(positive_moves)
            if not self._clearance_allows(requested_forward):
                self._enter_recovery_hold(
                    "FORWARD_CLEARANCE_BLOCKED",
                    "compound relocation forward segment is blocked",
                    resume_mode="align",
                    clearance=self.last_clearance,
                    requested_forward_m=requested_forward,
                )
                return
            clearance_scope = "fresh_forward_depth_clearance"

        self.pose_relocation_iteration += 1
        self.pose_relocation_plan = plan
        self.pose_relocation_purpose = (
            f"resilient_pose_relocation_{plan.stage}"
        )
        self.pose_relocation_primitive_index = 0
        self.pose_relocation_completed = []
        self.total_move_m += plan.total_move_m
        self.total_turn_deg += plan.total_turn_deg
        self.alignment_iterations += 1
        self._publish_status(
            "pose_relocation_maneuver_started",
            relocation_iteration=self.pose_relocation_iteration,
            plan=self._pose_relocation_plan_payload(plan),
            command_authority=(
                "encoder_proportional_relative_motion_then_camera_reset"
            ),
            camera_comparison_count_per_maneuver=1,
            clearance_scope=clearance_scope,
            rear_clearance_sensor_available=False,
        )

        if self.dry_run_base:
            self.steps[self.pose_relocation_purpose] = {
                "ok": True,
                "event": "compound_relative_pose_dry_run",
                "status": "done",
                "plan": self._pose_relocation_plan_payload(plan),
            }
            purpose = self.pose_relocation_purpose
            self._clear_pose_relocation_compound()
            self._after_camera_motion(purpose, plan.total_move_m)
            return

        self.pose_relocation_active = True
        self.pose_relocation_queue = list(plan.primitives)
        self._dispatch_pose_relocation_primitive()
    def _try_alignment_step_before_place_stop_spin_v3(self) -> None:
        # camera_reset_pose_relocation_v1
        if not bool(self.get_parameter("pose_relocation_enabled").value):
            super()._try_alignment_step()
            return
        if self.profile is None or self.pose_relocation_active:
            return
        if not ResilientObjectTaskNode._orientation_required(self):
            # A profile without a reliable taught orientation keeps the
            # existing camera controller.  Bypass the old fast-docking
            # distance gate, which may temporarily suppress orientation.
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
                    "visual_target_lost_restarting_full_search",
                    last_visual_age_sec=(
                        None
                        if self.last_visual_wall_sec <= 0.0
                        else time.time() - self.last_visual_wall_sec
                    ),
                )
                self._restart_full_search(
                    "visual target lost during pose relocation"
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
                "recoverable_observation_rejected",
                reason=constraint.reason,
                policy="hold_stationary_and_wait_for_better_visual_sample",
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

        assessment = self._orientation_assessment(stable)
        self.orientation_last_assessment = {
            "state": assessment.state,
            "signed_error_deg": assessment.signed_error_deg,
            "absolute_error_deg": assessment.absolute_error_deg,
            "quality": assessment.quality,
            "cost": assessment.cost,
            "comparison_mode": assessment.comparison_mode,
            "reason": assessment.reason,
        }
        self._publish_status(
            "object_orientation_observation",
            current_angle_deg=stable.orientation_deg,
            current_class=stable.orientation_class,
            current_quality=stable.orientation_quality,
            current_source=stable.orientation_source,
            current_semantics=stable.orientation_semantics,
            reference_angle_deg=self.orientation_reference_deg,
            reference_class=self.orientation_reference_class,
            reference_quality=self.orientation_reference_quality,
            reference_source=self.orientation_reference_source,
            reference_semantics=self.orientation_reference_semantics,
            assessment=dict(self.orientation_last_assessment),
        )
        if assessment.state == "quality_low":
            self.aligned_confirmations = 0
            self.pose_relocation_stage_confirmations = 0
            self._run_orientation_recovery(stable, assessment)
            return

        if self.pose_relocation_anchor_range_m <= 1e-6:
            self.pose_relocation_anchor_range_m = errors.current.range_m
        if self.pose_relocation_stage not in {"viewpoint", "range"}:
            self.pose_relocation_stage = "viewpoint"

        if (
            self.pose_relocation_stage == "range"
            and assessment.absolute_error_deg
            > float(
                self.get_parameter(
                    "pose_relocation_orientation_reentry_deg"
                ).value
            )
        ):
            self.pose_relocation_stage = "viewpoint"
            self.pose_relocation_anchor_range_m = errors.current.range_m
            self.pose_relocation_stage_confirmations = 0
            self.aligned_confirmations = 0
            self._publish_status(
                "pose_relocation_viewpoint_reentered",
                reason="orientation_drifted_outside_range_stage_hysteresis",
                orientation_error_deg=assessment.absolute_error_deg,
            )

        common = self._relocation_common_kwargs(
            stable,
            errors,
            stage=self.pose_relocation_stage,
        )
        try:
            if self.pose_relocation_stage == "viewpoint":
                plan = plan_viewpoint_relocation(**common)
                if plan.reached:
                    self.pose_relocation_stage_confirmations += 1
                    required = max(
                        1,
                        int(
                            self.get_parameter(
                                "pose_relocation_viewpoint_confirmation_count"
                            ).value
                        ),
                    )
                    if self.pose_relocation_stage_confirmations < required:
                        self._publish_status(
                            "pose_relocation_viewpoint_confirmation",
                            confirmation=self.pose_relocation_stage_confirmations,
                            required=required,
                            plan=self._pose_relocation_plan_payload(plan),
                        )
                        return
                    self.pose_relocation_stage = "range"
                    self.pose_relocation_stage_confirmations = 0
                    self._publish_status(
                        "pose_relocation_viewpoint_completed",
                        next_stage="range",
                        plan=self._pose_relocation_plan_payload(plan),
                    )
                    common = self._relocation_common_kwargs(
                        stable,
                        errors,
                        stage="range",
                    )
                    plan = plan_range_relocation(**common)
            else:
                plan = plan_range_relocation(**common)
        except Exception as error:
            self._enter_recovery_hold(
                "TARGET_POSE_NOT_CORRECTABLE",
                f"pose relocation planner failed: {error}",
                resume_mode="align",
            )
            return

        self._publish_status(
            "pose_relocation_camera_comparison",
            relocation_stage=self.pose_relocation_stage,
            plan=self._pose_relocation_plan_payload(plan),
            precise_errors={
                "bearing_error_deg": precise.bearing_error_deg,
                "forward_error_m": precise.forward_error_m,
                "lateral_error_m": precise.lateral_error_m,
                "range_error_m": precise.range_error_m,
                "planar_position_error_m": precise.planar_position_error_m,
            },
            control_policy=(
                "camera_measure_then_encoder_proportional_relative_pose_then_"
                "single_camera_reset"
            ),
        )

        if plan.reached:
            self.aligned_confirmations += 1
            required = max(
                2,
                int(
                    self.get_parameter(
                        "precision_confirmation_count"
                    ).value
                ),
            )
            if self.aligned_confirmations >= required:
                self._alignment_complete()
            return

        self.aligned_confirmations = 0
        if self.alignment_iterations > self.profile.alignment.max_iterations:
            self._publish_status(
                "alignment_soft_limit_recycled",
                previous_iterations=self.alignment_iterations,
                policy="continue_with_fresh_camera_relative_replanning",
            )
            self.alignment_iterations = 0
        self._start_pose_relocation(plan)

    def _select_alignment_decision(self, errors):
        if not bool(self.get_parameter("fast_docking_enabled").value):
            return super()._select_alignment_decision(errors)
        result = choose_fast_camera_docking_action(
            errors,
            translation_streak=self.fast_translation_streak,
            final_bearing_tolerance_deg=float(
                self.get_parameter("precision_bearing_tolerance_deg").value
            ),
            final_forward_tolerance_m=float(
                self.get_parameter("precision_forward_tolerance_m").value
            ),
            final_lateral_tolerance_m=float(
                self.get_parameter("precision_lateral_tolerance_m").value
            ),
            final_turn_step_deg=float(
                self.get_parameter("precision_turn_chunk_deg").value
            ),
            final_move_step_m=float(
                self.get_parameter("precision_move_chunk_m").value
            ),
            coarse_bearing_tolerance_deg=float(
                self.get_parameter(
                    "fast_coarse_bearing_tolerance_deg"
                ).value
            ),
            emergency_bearing_tolerance_deg=float(
                self.get_parameter(
                    "fast_emergency_bearing_tolerance_deg"
                ).value
            ),
            coarse_lateral_tolerance_m=float(
                self.get_parameter("fast_coarse_lateral_tolerance_m").value
            ),
            coarse_turn_step_deg=float(
                self.get_parameter("fast_coarse_turn_chunk_deg").value
            ),
            coarse_move_step_m=float(
                self.get_parameter("fast_coarse_move_chunk_m").value
            ),
            final_forward_band_m=float(
                self.get_parameter("fast_final_forward_band_m").value
            ),
            max_translation_streak=int(
                self.get_parameter("fast_max_translation_streak").value
            ),
        )
        self.fast_docking_phase = result.phase
        if result.decision.action == "turn":
            self.fast_translation_streak = 0
        elif result.decision.action == "move":
            self.fast_translation_streak += 1
        return result.decision

    def _alignment_turn_limit_deg(self) -> float:
        base = abs(super()._alignment_turn_limit_deg())
        if (
            bool(self.get_parameter("fast_docking_enabled").value)
            and self.fast_docking_phase == "coarse"
        ):
            return max(
                base,
                abs(
                    float(
                        self.get_parameter(
                            "fast_coarse_turn_chunk_deg"
                        ).value
                    )
                ),
            )
        return base

    def _alignment_move_limit_m(self) -> float:
        base = abs(super()._alignment_move_limit_m())
        if (
            bool(self.get_parameter("fast_docking_enabled").value)
            and self.fast_docking_phase == "coarse"
        ):
            return max(
                base,
                abs(
                    float(
                        self.get_parameter(
                            "fast_coarse_move_chunk_m"
                        ).value
                    )
                ),
            )
        return base

    def _orientation_required(self) -> bool:
        required = super()._orientation_required()
        if not required or not bool(
            self.get_parameter("fast_docking_enabled").value
        ):
            return required
        if self.phase == "final_visual_verify":
            return True
        if self.profile is None or self.last_object_point is None:
            return False
        try:
            errors = alignment_errors(
                self.last_object_point,
                self.profile.alignment.reference_point_base,
                forward_axis_sign=self.forward_axis_sign,
                lateral_axis_sign=self.lateral_axis_sign,
            )
        except Exception:
            return False
        return orientation_engagement_ready(
            errors,
            maximum_forward_error_m=float(
                self.get_parameter(
                    "fast_orientation_engage_forward_m"
                ).value
            ),
            maximum_lateral_error_m=float(
                self.get_parameter(
                    "fast_orientation_engage_lateral_m"
                ).value
            ),
            maximum_bearing_error_deg=float(
                self.get_parameter(
                    "fast_orientation_engage_bearing_deg"
                ).value
            ),
        )

    def _current_orientation_source(self) -> str:
        payload = self.latest_detection_metadata.get("payload", {})
        if not isinstance(payload, Mapping):
            return ""
        orientation = payload.get("orientation", {})
        if not isinstance(orientation, Mapping):
            return ""
        return str(orientation.get("source", "")).strip()

    def _run_orientation_recovery(self, stable, assessment) -> None:
        # upright_orientation_pingpong_guard_v1
        source = str(getattr(stable, "orientation_source", "")).strip()
        current_semantics = str(
            getattr(stable, "orientation_semantics", "")
        ).strip()
        reference_semantics = str(
            self.orientation_reference_semantics
        ).strip()

        # A face normal is a pose constraint, not an independent in-place yaw
        # target.  Turning in place changes object bearing; the following
        # bearing controller then commands the opposite turn.  Always use the
        # inherited measured-improvement viewpoint sequence for upright faces:
        # turn -> short translation -> re-centre -> fresh observation.
        if current_semantics == "face_normal_yaw_mod_180":
            self._publish_status(
                "upright_orientation_viewpoint_recovery_selected",
                orientation_state=assessment.state,
                signed_axis_error_deg=assessment.signed_error_deg,
                orientation_source=source,
                orientation_probe_stage=getattr(
                    self, "orientation_probe_stage", "idle"
                ),
                direct_in_place_turn_suppressed=True,
                controller="turn_translate_recenter_with_direction_latch",
                reason=(
                    "in_place_face_normal_turn_would_be_undone_by_"
                    "bearing_correction"
                ),
            )
            super()._run_orientation_recovery(stable, assessment)
            return

        # Preserve the optional legacy direct correction only for compatible
        # non-upright measured 3-D axes.  It remains disabled by default.
        compatible_3d = (
            is_measured_base_axis_orientation(
                source=source,
                coordinate_frame=str(
                    getattr(stable, "orientation_coordinate_frame", "")
                ),
                semantics=current_semantics,
                axis=getattr(stable, "orientation_axis_base", None),
            )
            and self.orientation_reference_coordinate_frame == "base_link"
            and self.orientation_reference_axis_base is not None
            and current_semantics == reference_semantics
            and assessment.comparison_mode == "base_link_axis_3d"
        )
        if (
            bool(
                self.get_parameter(
                    "fast_direct_3d_orientation_enabled"
                ).value
            )
            and compatible_3d
            and current_semantics != "face_normal_yaw_mod_180"
            and assessment.state == "angle_mismatch"
        ):
            amount = direct_axis_turn_deg(
                assessment.signed_error_deg,
                gain=float(
                    self.get_parameter("fast_direct_3d_turn_gain").value
                ),
                maximum_step_deg=float(
                    self.get_parameter(
                        "fast_direct_3d_turn_max_deg"
                    ).value
                ),
                minimum_step_deg=float(
                    self.get_parameter(
                        "fast_direct_3d_turn_min_deg"
                    ).value
                ),
            )
            self._reset_orientation_recovery(keep_direction=False)
            self.orientation_probe_count += 1
            self.orientation_total_turn_deg += abs(amount)
            self._publish_status(
                "orientation_3d_direct_turn_started",
                requested_turn_deg=amount,
                signed_axis_error_deg=assessment.signed_error_deg,
                orientation_source=source,
                controller="base_frame_long_axis_direct_correction",
            )
            self._send_turn(amount, "resilient_orientation_probe_turn")
            return

        super()._run_orientation_recovery(stable, assessment)

    # PLACE_SIDE_TURN_CAMERA_POLICY_V1_1
    # Reference-based PLACE only: after normal camera-authoritative alignment,
    # intentionally yaw the chassis a small amount and place at the held
    # object's taught reachable arm point.  Do not visually re-center the
    # reference after this deliberate side turn.
    def _alignment_complete_before_simple_place_v2(self) -> None:
        if self.task_kind != "place":
            super()._alignment_complete()
            return
        if not bool(self.get_parameter("place_side_turn_enabled").value):
            super()._alignment_complete()
            return
        target_deg = float(self.get_parameter("place_side_turn_deg").value)
        max_abs_deg = max(
            0.0,
            float(self.get_parameter("place_side_turn_max_abs_deg").value),
        )
        finish_tolerance_deg = max(
            0.01,
            abs(float(self.get_parameter("place_side_turn_finish_tolerance_deg").value)),
        )
        if not math.isfinite(target_deg):
            self._fail("INVALID_ARGUMENT", reason="place_side_turn_deg must be finite")
            return
        if abs(target_deg) > max_abs_deg + 1e-9:
            self._fail(
                "INVALID_ARGUMENT",
                reason=(
                    "place_side_turn_deg exceeds configured safety bound: "
                    f"requested={target_deg:.3f}, max={max_abs_deg:.3f} deg"
                ),
            )
            return
        if abs(target_deg) <= finish_tolerance_deg:
            super()._alignment_complete()
            return
        if self.last_object_point is None:
            self._fail(
                "OBJECT_LOST",
                reason="reference object point unavailable before PLACE side turn",
            )
            return
        try:
            held_runtime = self.profile_store.get(
                self.held_runtime_profile,
                self.held_object_name,
            )
            held_runtime.validate_for_execution(
                forward_axis_sign=self.forward_axis_sign,
                lateral_axis_sign=self.lateral_axis_sign,
            )
            reachable_point = tuple(
                float(value)
                for value in held_runtime.alignment.reference_point_base
            )
            if len(reachable_point) != 3 or not all(
                math.isfinite(value) for value in reachable_point
            ):
                raise ValueError("held taught reachable point is invalid")
        except Exception as error:
            self._fail(
                "INVALID_ARGUMENT",
                reason=f"held-object taught reachable point unavailable: {error}",
            )
            return

        reference_point = tuple(float(value) for value in self.last_object_point)
        self._cancel_finder("place_reference_aligned_side_turn")
        self._clear_active_target()
        self.steps["alignment"] = {
            "iterations": self.alignment_iterations,
            "errors": self._error_mapping(self.last_errors),
            "reference_point_base": list(reference_point),
        }
        self.placement_point_base = reachable_point
        self.place_side_turn_target_deg = target_deg
        self.place_side_turn_completed_deg = 0.0
        self.place_side_turn_remaining_deg = target_deg
        self._publish_status(
            "place_target_resolved",
            reference_object=self.place_reference_object,
            reference_point_base=list(reference_point),
            placement_policy="camera_side_turn_then_held_taught_reachable_point",
            requested_side_turn_deg=target_deg,
            legacy_placement_offset_base=list(self.place_offset_base),
            legacy_offset_used=False,
            placement_point_base=list(self.placement_point_base),
            visual_recenter_after_side_turn=False,
        )
        self._publish_status(
            "place_side_turn_started",
            target_deg=target_deg,
            direction=("left_ccw" if target_deg > 0.0 else "right_cw"),
            high_level_sign_contract="positive_is_left_ccw",
            visual_recenter_after_side_turn=False,
        )
        self._continue_place_side_turn()

    def _continue_place_side_turn(self) -> None:
        if self.state in TERMINAL_STATES or self.state == "CANCEL_REQUESTED":
            return
        if self.base_active:
            return
        tolerance = max(
            0.01,
            abs(float(self.get_parameter("place_side_turn_finish_tolerance_deg").value)),
        )
        remaining = self.place_side_turn_target_deg - self.place_side_turn_completed_deg
        self.place_side_turn_remaining_deg = remaining
        if abs(remaining) <= tolerance:
            self.place_side_turn_remaining_deg = 0.0
            self.phase = "place_side_turn_completed"
            self._publish_status(
                "place_side_turn_completed",
                target_deg=self.place_side_turn_target_deg,
                completed_deg=self.place_side_turn_completed_deg,
                placement_point_base=(
                    None
                    if self.placement_point_base is None
                    else list(self.placement_point_base)
                ),
                visual_recenter_after_side_turn=False,
                next="semantic_place_preflight",
            )
            self._start_place_preflight()
            return
        configured_chunk = max(
            0.1,
            abs(float(self.get_parameter("place_side_turn_chunk_deg").value)),
        )
        camera_chunk = max(
            0.1,
            abs(float(self.get_parameter("camera_max_turn_chunk_deg").value)),
        )
        chunk_limit = min(configured_chunk, camera_chunk)
        amount = max(-chunk_limit, min(chunk_limit, remaining))
        self.phase = "place_side_turn"
        self._publish_status(
            "place_side_turn_chunk_started",
            chunk_deg=amount,
            target_deg=self.place_side_turn_target_deg,
            completed_deg=self.place_side_turn_completed_deg,
            remaining_before_deg=remaining,
            chunk_limit_deg=chunk_limit,
        )
        # Keep sign conversion centralized in StoredObjectPickNode._send_turn:
        # + here means physical left/CCW; pico_turn_positive_is_right=true then
        # converts it to negative TURN_DEG at the Pico boundary.
        self._send_turn(amount, "resilient_place_side_turn")

    def _after_place_side_turn_chunk(self, physical_amount: float) -> None:
        self.place_side_turn_completed_deg += float(physical_amount)
        self.place_side_turn_remaining_deg = (
            self.place_side_turn_target_deg - self.place_side_turn_completed_deg
        )
        self._publish_status(
            "place_side_turn_chunk_completed",
            completed_chunk_deg=float(physical_amount),
            completed_total_deg=self.place_side_turn_completed_deg,
            remaining_deg=self.place_side_turn_remaining_deg,
            visual_recenter_after_side_turn=False,
        )
        self._continue_place_side_turn()

    def _send_move(self, physical_forward_positive_m: float, purpose: str) -> None:
        requested = float(physical_forward_positive_m)
        if purpose == "resilient_search_backoff":
            limit = float(
                self.get_parameter("camera_search_backoff_chunk_m").value
            )
        elif (
            purpose == "resilient_approach_move"
            and self.fast_docking_phase == "coarse"
            and bool(self.get_parameter("fast_docking_enabled").value)
        ):
            limit = float(
                self.get_parameter("fast_coarse_move_chunk_m").value
            )
        else:
            limit = float(
                self.get_parameter("camera_max_translation_chunk_m").value
            )
        bounded = max(-abs(limit), min(abs(limit), requested))
        if abs(bounded - requested) > 1e-9:
            self._publish_status(
                "camera_motion_command_clamped",
                purpose=purpose,
                motion="translation",
                requested=requested,
                bounded=bounded,
            )
        super()._send_move(bounded, purpose)

    def _send_turn_before_place_stop_spin_v3(self, physical_left_positive_deg: float, purpose: str) -> None:
        requested = float(physical_left_positive_deg)
        parameter = (
            "camera_search_turn_chunk_deg"
            if purpose == "resilient_search_turn"
            else "camera_max_turn_chunk_deg"
        )
        limit = float(self.get_parameter(parameter).value)
        bounded = max(-abs(limit), min(abs(limit), requested))
        if abs(bounded - requested) > 1e-9:
            self._publish_status(
                "camera_motion_command_clamped",
                purpose=purpose,
                motion="rotation",
                requested=requested,
                bounded=bounded,
            )
        super()._send_turn(bounded, purpose)

    def _start_base_command(
        self,
        command: str,
        expected_event: str,
        purpose: str,
        physical_amount: float,
    ) -> None:
        if not purpose.startswith("resilient_"):
            super()._start_base_command(
                command, expected_event, purpose, physical_amount
            )
            return
        self.base_active = True
        self.base_expected_event = expected_event
        self.base_command = command
        self.base_purpose = purpose
        self.base_physical_amount = float(physical_amount)
        self.phase = purpose
        self.phase_deadline = time.monotonic() + float(
            self.get_parameter("base_motion_timeout_sec").value
        ) + 1.0
        self.motion_started_wall_sec = time.time()
        self.base_motion_start_odom = None
        self.camera_motion_sequence += 1
        # No camera result observed during this motion can authorize a next
        # command.  The finite threshold is set at completion below.
        self.fresh_detection_not_before_wall_sec = math.inf
        self.pending_detections.clear()
        self.filter.clear()
        self.cached_stable_detection = None
        self.latest_stable_detection = None
        self.last_object_point = None

        if self.dry_run_base:
            self.base_active = False
            if purpose == "resilient_search_turn":
                self.search_measured_turn_deg += abs(float(physical_amount))
            self.steps[purpose] = {
                "ok": True,
                "event": expected_event,
                "status": "done",
                "dry_run": True,
                "physical_amount": physical_amount,
            }
            self.base_purpose = ""
            self._after_camera_motion(purpose, float(physical_amount))
            return

        self._send_pico(command)
        self._publish_status(
            "base_motion_commanded",
            purpose=purpose,
            physical_amount=physical_amount,
            pico_command=command,
            camera_samples_during_motion="discarded",
            persistent_odometry_used=False,
        )

    def _pico_response_callback(self, msg: String) -> None:
        try:
            payload = json.loads(msg.data)
        except Exception:
            super()._pico_response_callback(msg)
            return
        if not isinstance(payload, dict):
            return
        event = str(payload.get("event", ""))
        if (
            (event in BASE_MOTION_EVENTS or event == "drive_relative_result")
            and self.base_active
            and self.base_purpose.startswith("resilient_")
        ):
            if event != self.base_expected_event:
                return
            self.last_pico_payload = dict(payload)
            purpose = self.base_purpose
            physical_amount = float(self.base_physical_amount)
            self.base_active = False
            self.last_base_response = dict(payload)
            status = str(payload.get("status", ""))
            if self.state == "CANCEL_REQUESTED":
                self._clear_pose_relocation_compound()
                if status in {
                    "stopped",
                    "done",
                    "timeout",
                    "stall",
                    "encoder_direction_error",
                }:
                    self.cancel_wait_base = False
                    self._try_finish_cancel()
                return
            if payload.get("ok") is not True or status != "done":
                self._clear_pose_relocation_compound()
                error_code = {
                    "stall": "WHEEL_SLIP",
                    "encoder_direction_error": "ENCODER_DIRECTION_ERROR",
                    "timeout": "MOTION_EXECUTION_FAILED",
                    "stopped": "MOTION_EXECUTION_FAILED",
                }.get(status, "MOTION_EXECUTION_FAILED")
                self._fail(
                    error_code,
                    reason=f"base motion ended with status={status or 'unknown'}",
                    pico_response=payload,
                )
                return
            if purpose == "resilient_search_turn":
                # A successful TURN_DEG is encoder-bounded internally.  We count
                # successful atomic turns, not a persistent global odometry pose.
                self.search_measured_turn_deg += abs(physical_amount)
                self._publish_status(
                    "search_rotation_accounting_updated",
                    completed_step_deg=abs(physical_amount),
                    accumulated_deg=self.search_measured_turn_deg,
                    source="successful_encoder_bounded_turn_command",
                )
            self.steps[purpose] = dict(payload)
            self.base_purpose = ""
            if (
                self.pose_relocation_active
                and purpose.startswith("resilient_pose_relocation_")
            ):
                self.pose_relocation_completed.append(
                    {
                        "purpose": purpose,
                        "physical_amount": physical_amount,
                        "response": dict(payload),
                    }
                )
                if self.pose_relocation_queue:
                    self._dispatch_pose_relocation_primitive()
                    return
                plan = self.pose_relocation_plan
                overall_purpose = self.pose_relocation_purpose
                completed = list(self.pose_relocation_completed)
                self._clear_pose_relocation_compound()
                self._publish_status(
                    "pose_relocation_maneuver_completed",
                    purpose=overall_purpose,
                    completed_primitives=completed,
                    plan=(
                        None
                        if plan is None
                        else self._pose_relocation_plan_payload(plan)
                    ),
                    next="single_fresh_camera_comparison",
                )
                self._after_camera_motion(
                    overall_purpose,
                    0.0 if plan is None else plan.total_move_m,
                )
                return
            self._after_camera_motion(purpose, physical_amount)
            return

        # Non-motion responses are still useful for Pico health, E-stop and
        # legacy administration.  No odometry result is retained as object pose.
        super()._pico_response_callback(msg)
        if event == "odometry":
            self.last_odom = None
            self.last_visual_object_odom = None

    def _after_camera_motion_before_simple_place_v2(self, purpose: str, physical_amount: float) -> None:
        if purpose == "resilient_place_side_turn":
            self.camera_motion_completed_at = time.time()
            guard = max(
                0.0,
                float(self.get_parameter("camera_motion_frame_guard_sec").value),
                float(self.get_parameter("post_motion_frame_guard_sec").value),
            )
            self.fresh_detection_not_before_wall_sec = (
                self.camera_motion_completed_at + guard
            )
            self.pending_detections.clear()
            self.filter.clear()
            self.cached_stable_detection = None
            self.latest_stable_detection = None
            self.last_object_point = None
            self._after_place_side_turn_chunk(physical_amount)
            return
        self.camera_motion_completed_at = time.time()
        guard = max(
            0.0,
            float(self.get_parameter("camera_motion_frame_guard_sec").value),
            float(self.get_parameter("post_motion_frame_guard_sec").value),
        )
        self.fresh_detection_not_before_wall_sec = (
            self.camera_motion_completed_at + guard
        )
        self.pending_detections.clear()
        self.filter.clear()
        self.cached_stable_detection = None
        self.latest_stable_detection = None
        self.last_object_point = None
        self.require_fresh_after_turn = True
        if purpose.startswith("resilient_search"):
            self.phase = "search"
            self.search_observe_until = 0.0
            self._publish_status(
                "search_motion_completed",
                purpose=purpose,
                completed_amount=physical_amount,
                next="fresh_post_motion_camera_observation",
                persistent_odometry_used=False,
            )
            return
        self.phase = "align_settle"
        assert self.profile is not None
        if purpose.startswith("resilient_pose_relocation_"):
            settle_sec = max(
                0.0,
                float(
                    self.get_parameter("pose_relocation_settle_sec").value
                ),
            )
            reobserve_sec = max(
                0.0,
                float(
                    self.get_parameter("pose_relocation_reobserve_sec").value
                ),
            )
        elif bool(self.get_parameter("fast_docking_enabled").value):
            settle_parameter = (
                "fast_coarse_settle_sec"
                if self.fast_docking_phase == "coarse"
                else "fast_final_settle_sec"
            )
            settle_sec = max(
                0.0,
                float(self.get_parameter(settle_parameter).value),
            )
            reobserve_sec = max(
                0.0,
                float(self.get_parameter("fast_reobserve_sec").value),
            )
        else:
            settle_sec = self.profile.alignment.settle_sec
            reobserve_sec = float(
                self.get_parameter("visual_reobserve_sec").value
            )
        self.settle_until = time.monotonic() + settle_sec
        self.reobserve_not_before = self.settle_until + reobserve_sec
        self._publish_status(
            "visual_servo_motion_completed",
            purpose=purpose,
            completed_amount=physical_amount,
            next="fresh_post_motion_camera_observation",
            correction_policy="measure_move_measure_reverse_if_overshot",
        )

    # PLACE_REFERENCE_UNIFIED_SEARCH_V1
    # Reference-based PLACE uses the same camera-authoritative search/alignment
    # path as ordinary object alignment.  The held-object state is only a PLACE
    # safety contract; it does not change target acquisition or visual servoing.
    #
    # The object finder already runs in continuous mode and transitions back to
    # SEARCHING after a temporal track is deconfirmed/expired.  Therefore a
    # PLACE reference loss should restart only the base search plan while
    # preserving a healthy finder session.  Repeatedly cancelling/restarting
    # the finder unnecessarily resets temporal confirmation and target readiness.
    def _start_place_goal(self, request) -> None:
        super()._start_place_goal(request)
        if (
            self.task_kind == "place"
            and self.state == "RUNNING"
            and self.direct_placement_point is None
        ):
            self._publish_status(
                "place_reference_search_unified",
                reference_object=self.place_reference_object,
                held_object=self.held_object_name,
                acquisition_pipeline="same_camera_authoritative_search_and_alignment",
                held_object_changes_search_policy=False,
                place_specific_behavior_starts_after_alignment=True,
                lost_reacquisition="preserve_continuous_finder_restart_base_search",
            )

    def _restart_full_search(self, reason: str) -> None:
        if (
            self.task_kind != "place"
            or self.direct_placement_point is not None
            or not bool(
                self.get_parameter(
                    "place_reference_keep_finder_on_lost"
                ).value
            )
        ):
            super()._restart_full_search(reason)
            return
        if self.base_active or self.arm_active:
            return

        self.filter.clear()
        self.pending_detections.clear()
        self.cached_stable_detection = None
        self.latest_stable_detection = None
        self.last_visual_wall_sec = 0.0
        self.reobserve_not_before = 0.0
        self._reset_orientation_recovery()

        finder_state = str(
            self.last_finder_status.get("state", "")
        ).strip().upper()
        finder_terminal = finder_state in {
            "IDLE",
            "TIMED_OUT",
            "CANCELLED",
            "CANCELED",
            "ERROR",
        }

        # A healthy continuous finder is deliberately preserved.  If the finder
        # really reached a terminal state, mark the Pi-side state inactive so
        # _start_resilient_search() creates a fresh finder goal.
        if self.start_finder_for_goal and self.finder_active and finder_terminal:
            self.finder_active = False
            self.finder_goal_payload = {}
            self.finder_goal_acknowledged = False
            self.finder_target_ready = False
            self.finder_target_ready_at = 0.0

        self._publish_status(
            "place_reference_reacquire_started",
            reason=reason,
            reference_object=self.place_reference_object,
            finder_preserved=bool(
                self.start_finder_for_goal
                and self.finder_active
                and not finder_terminal
            ),
            finder_state=finder_state or "unknown",
            policy="same_camera_authoritative_search_keep_continuous_finder",
            place_specific_behavior_starts_after_alignment=True,
        )

        # Rebuild the exact same rotation-first camera-authoritative base search
        # used by the normal alignment path.  This method will keep an active
        # finder and merely reassert the target, or start a new one if needed.
        self._start_resilient_search()

    def _begin_visual_approach(self, stable) -> None:
        super()._begin_visual_approach(stable)
        self.pose_relocation_stage = "viewpoint"
        self.pose_relocation_stage_confirmations = 0
        self.pose_relocation_iteration = 0
        self._clear_pose_relocation_compound()
        try:
            initial_errors = alignment_errors(
                stable.point_base,
                self.profile.alignment.reference_point_base,
                forward_axis_sign=self.forward_axis_sign,
                lateral_axis_sign=self.lateral_axis_sign,
            )
            self.pose_relocation_anchor_range_m = (
                initial_errors.current.range_m
            )
        except Exception:
            self.pose_relocation_anchor_range_m = planar_range_m(
                stable.point_base
            )
        self._publish_status(
            "camera_authoritative_docking_started",
            reference_point_base=list(self.profile.alignment.reference_point_base),
            current_point_base=list(stable.point_base),
            distance_handoff_used=False,
            coarse_translation_chunk_cap_m=float(
                self.get_parameter("fast_coarse_move_chunk_m").value
            ),
            final_translation_chunk_cap_m=min(
                float(self.get_parameter("camera_max_translation_chunk_m").value),
                float(self.get_parameter("precision_move_chunk_m").value),
            ),
            coarse_turn_chunk_cap_deg=float(
                self.get_parameter("fast_coarse_turn_chunk_deg").value
            ),
            after_every_move="discard_old_frames_and_remeasure",
        )

    # ------------------------------------------------------------------
    # Final camera check after semantic preflight and before physical grasp
    # ------------------------------------------------------------------
    def _detection_callback(self, msg: String) -> None:
        if self.phase != "final_visual_verify":
            super()._detection_callback(msg)
            return
        if not self._is_busy() or self.base_active:
            return
        detection = self._parse_detection(msg)
        if detection is not None:
            self._ingest_detection(detection)

    def _keyframe_result_callback(self, msg: String) -> None:
        if self.task_kind == "place":
            super()._keyframe_result_callback(msg)
            return
        if not self.keyframe_command_id or self.state in TERMINAL_STATES:
            return
        try:
            payload = json.loads(msg.data)
        except Exception:
            return
        if not isinstance(payload, dict):
            return
        if str(payload.get("command_id", "")) != self.keyframe_command_id:
            return
        event = str(payload.get("event", ""))
        if (
            event == "grasp_keyframe_preflight_succeeded"
            and payload.get("ok") is True
        ):
            preflight_only = self.keyframe_preflight_only
            self.keyframe_preflight_only = False
            self.arm_active = False
            self.keyframe_command_id = ""
            self.steps["grasp_preflight"] = dict(payload)
            if preflight_only and self.execute_pick:
                self.phase = "final_visual_verify"
                self.final_visual_started_at = time.monotonic()
                self.final_visual_confirmations = 0
                self.filter.clear()
                self.latest_stable_detection = None
                self.last_object_point = None
                self.fresh_detection_not_before_wall_sec = time.time()
                self._set_active_target(self.object_name)
                if not self.finder_active:
                    self._start_finder(
                        max(
                            60.0,
                            float(
                                self.get_parameter("finder_search_timeout_sec").value
                            ),
                        )
                    )
                self._publish_status(
                    "final_camera_verification_started",
                    required_confirmations=max(
                        1,
                        int(
                            self.get_parameter(
                                "camera_final_visual_confirmation_count"
                            ).value
                        ),
                    ),
                    reason="semantic_preflight_does_not_authorize_motion_without_fresh_rgbd",
                )
            else:
                self._succeed()
            return
        super()._keyframe_result_callback(msg)

    def _precision_stable_detection(self):
        original_phase = self.phase
        try:
            self.phase = "align"
            return super()._stable_detection()
        finally:
            self.phase = original_phase

    def _try_final_visual_verification(self) -> None:
        stable = self._precision_stable_detection()
        if stable is None:
            if (
                self.final_visual_started_at > 0.0
                and time.monotonic() - self.final_visual_started_at
                > float(
                    self.get_parameter(
                        "camera_final_visual_lost_restart_sec"
                    ).value
                )
            ):
                self._restart_full_search(
                    "fresh camera verification unavailable after arm preflight"
                )
            return

        assert self.profile is not None
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
                "final_camera_verification_waiting",
                reason=constraint.reason,
            )
            return

        errors = alignment_errors(
            stable.point_base,
            self.profile.alignment.reference_point_base,
            forward_axis_sign=self.forward_axis_sign,
            lateral_axis_sign=self.lateral_axis_sign,
        )
        decision = choose_precision_docking_action(
            errors,
            bearing_tolerance_deg=float(
                self.get_parameter("precision_bearing_tolerance_deg").value
            ),
            forward_tolerance_m=float(
                self.get_parameter("precision_forward_tolerance_m").value
            ),
            lateral_tolerance_m=float(
                self.get_parameter("precision_lateral_tolerance_m").value
            ),
            max_turn_step_deg=float(
                self.get_parameter("precision_turn_chunk_deg").value
            ),
            max_move_step_m=float(
                self.get_parameter("precision_move_chunk_m").value
            ),
        )
        assessment: Optional[OrientationAssessment] = None
        if self._orientation_required():
            assessment = self._orientation_assessment(stable)

        aligned = decision.action == "aligned" and (
            assessment is None or assessment.aligned
        )
        precise = precision_errors(errors)
        self._publish_status(
            "final_camera_verification_observation",
            point_base=list(stable.point_base),
            precision_errors={
                "bearing_error_deg": precise.bearing_error_deg,
                "forward_error_m": precise.forward_error_m,
                "lateral_error_m": precise.lateral_error_m,
            },
            orientation=(
                None
                if assessment is None
                else {
                    "state": assessment.state,
                    "absolute_error_deg": assessment.absolute_error_deg,
                    "quality": assessment.quality,
                }
            ),
            aligned=aligned,
        )
        if not aligned:
            self.final_visual_confirmations = 0
            self.phase = "align"
            self.cached_stable_detection = stable
            self.latest_stable_detection = stable
            self.last_object_point = stable.point_base
            self.filter.clear()
            self._publish_status(
                "final_camera_verification_returned_to_docking",
                reason=(
                    decision.reason
                    if decision.action != "aligned"
                    else assessment.state if assessment is not None else "not_aligned"
                ),
            )
            return

        self.final_visual_confirmations += 1
        self.latest_stable_detection = stable
        self.last_object_point = stable.point_base
        required = max(
            1,
            int(
                self.get_parameter(
                    "camera_final_visual_confirmation_count"
                ).value
            ),
        )
        if self.final_visual_confirmations < required:
            self.filter.clear()
            self._publish_status(
                "final_camera_verification_confirmation",
                count=self.final_visual_confirmations,
                required=required,
            )
            return
        self._publish_status(
            "final_camera_verification_completed",
            confirmations=self.final_visual_confirmations,
            final_point_base=list(stable.point_base),
            persistent_odometry_used=False,
        )
        self._start_grasp()

    def _timer_callback(self) -> None:
        if (
            self.phase == "final_visual_verify"
            and self.state == "RUNNING"
        ):
            self._try_final_visual_verification()
            return
        super()._timer_callback()


    # SIMPLE_PLACE_SINGLE_TURN_V2
    # PLACE is intentionally simple:
    # normal camera-authoritative search/alignment
    # -> one +15 deg (default) physical-left-positive base turn
    # -> no re-observation / no re-centering
    # -> semantic PLACE preflight immediately.
    def _alignment_complete(self) -> None:
        if self.task_kind != "place":
            self._alignment_complete_before_simple_place_v2()
            return

        self._simple_place_side_turn_pending = False
        self._cancel_finder("place_reference_aligned_simple")
        self._clear_active_target()

        if self.last_object_point is None:
            self._fail(
                "OBJECT_LOST",
                reason="reference object point unavailable after final PLACE alignment",
            )
            return

        try:
            held_runtime = self.profile_store.get(
                self.held_runtime_profile,
                self.held_object_name,
            )
            placement_point = tuple(
                float(value)
                for value in held_runtime.alignment.reference_point_base
            )
            if len(placement_point) != 3 or not all(
                math.isfinite(value) for value in placement_point
            ):
                raise ValueError("held taught reference point is invalid")
        except Exception as exc:
            self._fail(
                "POSITION_STORE_ERROR",
                reason=f"held taught reachable point unavailable for PLACE: {exc}",
            )
            return

        reference_point = tuple(float(v) for v in self.last_object_point)
        self.steps["alignment"] = {
            "iterations": self.alignment_iterations,
            "errors": self._error_mapping(self.last_errors),
            "reference_point_base": list(reference_point),
        }

        self.placement_point_base = placement_point

        side_turn_deg = 15.0
        if self.has_parameter("place_side_turn_deg"):
            try:
                side_turn_deg = float(
                    self.get_parameter("place_side_turn_deg").value
                )
            except (TypeError, ValueError):
                side_turn_deg = 15.0
        if not math.isfinite(side_turn_deg):
            side_turn_deg = 15.0
        side_turn_deg = max(-30.0, min(30.0, side_turn_deg))

        self._publish_status(
            "place_target_resolved",
            reference_object=self.place_reference_object,
            reference_point_base=list(reference_point),
            placement_point_base=list(self.placement_point_base),
            placement_policy="single_side_turn_then_held_taught_reachable_point",
            legacy_offset_used=False,
            side_turn_deg=side_turn_deg,
        )

        if abs(side_turn_deg) < 1e-6:
            self._publish_status(
                "place_side_turn_skipped",
                side_turn_deg=side_turn_deg,
                next="semantic_place_preflight",
            )
            self._start_place_preflight()
            return

        self._simple_place_side_turn_pending = True
        self._publish_status(
            "place_side_turn_started",
            requested_deg=side_turn_deg,
            chunks=1,
            recenter_after_turn=False,
            next="semantic_place_preflight",
        )

        # Bypass the camera servo 4-degree clamp for this intentional final
        # offset while preserving the inherited Pico TURN sign conversion.
        super(CameraAuthoritativeTaskNode, self)._send_turn(
            side_turn_deg,
            "resilient_place_side_turn_simple",
        )

    def _after_camera_motion(
        self,
        purpose: str,
        physical_amount: float,
    ) -> None:
        if purpose != "resilient_place_side_turn_simple":
            self._after_camera_motion_before_simple_place_v2(
                purpose,
                physical_amount,
            )
            return

        if not getattr(self, "_simple_place_side_turn_pending", False):
            self._fail(
                "INTERNAL_ERROR",
                reason="unexpected PLACE side-turn completion without pending state",
            )
            return

        self._simple_place_side_turn_pending = False
        self.camera_motion_completed_at = time.time()

        self.pending_detections.clear()
        self.filter.clear()
        self.cached_stable_detection = None
        self.latest_stable_detection = None
        self.last_object_point = None
        self.require_fresh_after_turn = False
        self.reobserve_not_before = 0.0

        self._publish_status(
            "place_side_turn_completed",
            completed_deg=float(physical_amount),
            chunks=1,
            recenter_after_turn=False,
            perception_after_turn="disabled_for_intentional_place_offset",
            next="semantic_place_preflight",
        )
        self._start_place_preflight()

    # PLACE_STOP_SPIN_V3
    # Deterministic PLACE safety policy:
    #   1. normal camera-authoritative acquisition/alignment,
    #   2. commit after the first genuinely aligned 3-D observation,
    #   3. NO post-alignment base turn,
    #   4. NO automatic full-search rotation after identity confirmation,
    #   5. if 3-D localization disappears before alignment, hold stationary.
    def _start_place_goal(self, request) -> None:
        self._place_identity_latched_v3 = False
        self._place_commit_started_v3 = False
        self._place_identity_source_v3 = ""
        super()._start_place_goal(request)
        if self.task_kind == "place" and self.state == "RUNNING":
            self._publish_status(
                "place_stop_spin_policy_active",
                post_alignment_base_turn_deg=0.0,
                first_aligned_observation_commits=True,
                automatic_search_after_identity=False,
                loss_policy="stationary_manual_hold",
            )

    def _mark_identity_confirmed(self, source: str) -> None:
        super()._mark_identity_confirmed(source)
        if self.task_kind != "place" or self.state != "RUNNING":
            return
        first = not getattr(self, "_place_identity_latched_v3", False)
        self._place_identity_latched_v3 = True
        self._place_identity_source_v3 = str(source)
        if first:
            self._publish_status(
                "place_reference_identity_latched",
                confirmation_source=str(source),
                automatic_full_search_disabled=True,
                physical_motion="stationary_until_3d_alignment",
            )

    def _try_alignment_step(self) -> None:
        if self.task_kind != "place" or getattr(
            self, "_place_commit_started_v3", False
        ):
            self._try_alignment_step_before_place_stop_spin_v3()
            return

        self._try_alignment_step_before_place_stop_spin_v3()

        # The reference center is not a precision placement target in this
        # project.  One complete aligned 3-D assessment is enough.  Do not wait
        # for a second confirmation that can disappear and trigger recovery.
        if (
            self.state == "RUNNING"
            and not getattr(self, "_place_commit_started_v3", False)
            and not self.base_active
            and not self.arm_active
            and self.phase in {"align", "align_settle"}
            and self.aligned_confirmations >= 1
            and self.last_object_point is not None
        ):
            self._publish_status(
                "place_first_alignment_accepted",
                aligned_confirmations=self.aligned_confirmations,
                policy="single_aligned_3d_observation",
                next="semantic_place_preflight",
            )
            self._alignment_complete()

    def _alignment_complete(self) -> None:
        if self.task_kind != "place":
            super()._alignment_complete()
            return
        if getattr(self, "_place_commit_started_v3", False):
            return
        if self.base_active or self.arm_active:
            return

        reference_point = self.last_object_point
        if reference_point is None and self.latest_stable_detection is not None:
            reference_point = self.latest_stable_detection.point_base
        if reference_point is None:
            self._enter_recovery_hold(
                "PLACE_REFERENCE_3D_UNAVAILABLE",
                "reference identity was confirmed but no usable 3-D point remains",
                resume_mode="manual",
                automatic_full_search_disabled=True,
            )
            return

        try:
            held_runtime = self.profile_store.get(
                self.held_runtime_profile,
                self.held_object_name,
            )
            held_runtime.validate_for_execution(
                forward_axis_sign=self.forward_axis_sign,
                lateral_axis_sign=self.lateral_axis_sign,
            )
            placement_point = tuple(
                float(value)
                for value in held_runtime.alignment.reference_point_base
            )
            if len(placement_point) != 3 or not all(
                math.isfinite(value) for value in placement_point
            ):
                raise ValueError("held taught reachable point is invalid")
        except Exception as exc:
            self._fail(
                "POSITION_STORE_ERROR",
                reason=f"held taught reachable point unavailable for PLACE: {exc}",
            )
            return

        self._place_commit_started_v3 = True
        self._cancel_finder("place_alignment_committed_no_turn_v3")
        self._clear_active_target()
        self.search_actions.clear()
        self.search_observe_until = 0.0
        self.require_fresh_after_turn = False
        self.reobserve_not_before = 0.0
        self.placement_point_base = placement_point

        error_payload = (
            None
            if self.last_errors is None
            else self._error_mapping(self.last_errors)
        )
        self.steps["alignment"] = {
            "iterations": self.alignment_iterations,
            "errors": error_payload,
            "reference_point_base": list(reference_point),
            "confirmation_policy": "single_aligned_3d_observation",
        }
        self._publish_status(
            "place_alignment_committed_no_base_turn",
            reference_object=self.place_reference_object,
            reference_point_base=list(reference_point),
            placement_point_base=list(self.placement_point_base),
            placement_policy="held_taught_reachable_point_no_base_turn",
            post_alignment_base_turn_deg=0.0,
            legacy_offset_used=False,
            finder_cancelled=True,
            next="semantic_place_preflight",
        )
        self._start_place_preflight()

    def _fail(self, error_code: str, *, reason: str, **details) -> None:
        perception_codes = {
            "OBJECT_LOST",
            "OBJECT_NOT_FOUND",
            "PERCEPTION_UNAVAILABLE",
            "ALIGNMENT_TIMEOUT",
        }
        if (
            self.task_kind == "place"
            and getattr(self, "_place_identity_latched_v3", False)
            and not getattr(self, "_place_commit_started_v3", False)
            and error_code in perception_codes
        ):
            if self.aligned_confirmations >= 1 and self.last_object_point is not None:
                self._publish_status(
                    "place_perception_loss_after_alignment_committing",
                    original_error_code=error_code,
                    original_reason=reason,
                    automatic_full_search_disabled=True,
                )
                self._alignment_complete()
                return
            if self.phase != "recovery_hold":
                self._enter_recovery_hold(
                    "PLACE_REFERENCE_LOST_AFTER_IDENTITY",
                    reason,
                    resume_mode="manual",
                    original_error_code=error_code,
                    identity_source=getattr(
                        self, "_place_identity_source_v3", ""
                    ),
                    automatic_full_search_disabled=True,
                        **details,
                )
            return
        super()._fail(error_code, reason=reason, **details)

    def _restart_full_search(self, reason: str) -> None:
        if (
            self.task_kind == "place"
            and (
                getattr(self, "_place_identity_latched_v3", False)
                or getattr(self, "_place_commit_started_v3", False)
            )
        ):
            if getattr(self, "_place_commit_started_v3", False):
                self._publish_status(
                    "place_search_restart_ignored_after_commit",
                    reason=reason,
                    phase=self.phase,
                )
                return
            if self.aligned_confirmations >= 1 and self.last_object_point is not None:
                self._publish_status(
                    "place_search_restart_replaced_by_commit",
                    reason=reason,
                    automatic_full_search_disabled=True,
                )
                self._alignment_complete()
                return
            if self.phase != "recovery_hold":
                self._enter_recovery_hold(
                    "PLACE_REFERENCE_LOST_AFTER_IDENTITY",
                    reason,
                    resume_mode="manual",
                    automatic_full_search_disabled=True,
                    )
            return
        super()._restart_full_search(reason)

    def _send_turn(
        self,
        physical_left_positive_deg: float,
        purpose: str,
    ) -> None:
        block_side_turn = (
            self.task_kind == "place"
            and purpose.startswith("resilient_place_side_turn")
        )
        block_search_after_identity = (
            self.task_kind == "place"
            and getattr(self, "_place_identity_latched_v3", False)
            and (
                purpose == "search_turn"
                or purpose.startswith("resilient_search")
            )
        )
        if block_side_turn or block_search_after_identity:
            self._publish_status(
                "place_base_turn_blocked",
                requested_deg=float(physical_left_positive_deg),
                purpose=purpose,
                reason=(
                    "post_alignment_side_turn_disabled"
                    if block_side_turn
                    else "automatic_search_after_identity_disabled"
                ),
                physical_motion="not_commanded",
            )
            if (
                not getattr(self, "_place_commit_started_v3", False)
                and self.aligned_confirmations >= 1
                and self.last_object_point is not None
            ):
                self._alignment_complete()
            elif (
                not getattr(self, "_place_commit_started_v3", False)
                and self.phase != "recovery_hold"
            ):
                self._enter_recovery_hold(
                    "PLACE_BASE_TURN_BLOCKED",
                    "unsafe PLACE search/side-turn request was suppressed",
                    resume_mode="manual",
                    blocked_purpose=purpose,
                    requested_deg=float(physical_left_positive_deg),
                    )
            return

        self._send_turn_before_place_stop_spin_v3(
            physical_left_positive_deg,
            purpose,
        )


def main(args=None) -> None:
    rclpy.init(args=args)
    node = CameraAuthoritativeTaskNode()
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
