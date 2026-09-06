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
)
from .orientation_control import OrientationAssessment
from .precision_docking import choose_precision_docking_action, precision_errors
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
        # The parent constructor dynamically calls status/reset helpers.
        self.final_visual_confirmations = 0
        self.final_visual_started_at = 0.0
        self.camera_motion_sequence = 0
        self.camera_motion_completed_at = 0.0
        super().__init__()
        self._publish_status(
            "camera_authoritative_tasks_ready",
            execution_authority="fresh_rgbd_localization",
            persistent_odometry_used=False,
            encoder_role="bounded_motion_completion_only",
            teaching_workflow="camera_reference_plus_semantic_keyframes",
        )
        self.get_logger().info(
            "Camera-authoritative task policy ready: fresh RGB-D after every base motion"
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
                "execution_authority": "fresh_rgbd_localization",
                "persistent_odometry_used": False,
                "encoder_role": "bounded_motion_completion_and_fault_detection",
                "camera_motion_sequence": self.camera_motion_sequence,
                "final_visual_confirmations": self.final_visual_confirmations,
                "distance_handoff_active": False,
            }
        )
        return payload

    def _reset_action_state(self) -> None:
        super()._reset_action_state()
        self.final_visual_confirmations = 0
        self.final_visual_started_at = 0.0
        self.camera_motion_sequence = 0
        self.camera_motion_completed_at = 0.0
        # Explicitly invalidate all pose-like state.  Individual Pico motion
        # results may still contain odometry fields, but this policy never uses
        # them to predict an object point or reproduce a stored pose.
        self.last_odom = None
        self.last_visual_object_odom = None

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

    def _send_move(self, physical_forward_positive_m: float, purpose: str) -> None:
        requested = float(physical_forward_positive_m)
        if purpose == "resilient_search_backoff":
            limit = float(
                self.get_parameter("camera_search_backoff_chunk_m").value
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

    def _send_turn(self, physical_left_positive_deg: float, purpose: str) -> None:
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
            event in BASE_MOTION_EVENTS
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
            self._after_camera_motion(purpose, physical_amount)
            return

        # Non-motion responses are still useful for Pico health, E-stop and
        # legacy administration.  No odometry result is retained as object pose.
        super()._pico_response_callback(msg)
        if event == "odometry":
            self.last_odom = None
            self.last_visual_object_odom = None

    def _after_camera_motion(self, purpose: str, physical_amount: float) -> None:
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
        self.settle_until = time.monotonic() + self.profile.alignment.settle_sec
        self.reobserve_not_before = self.settle_until + float(
            self.get_parameter("visual_reobserve_sec").value
        )
        self._publish_status(
            "visual_servo_motion_completed",
            purpose=purpose,
            completed_amount=physical_amount,
            next="fresh_post_motion_camera_observation",
            correction_policy="measure_move_measure_reverse_if_overshot",
        )

    def _begin_visual_approach(self, stable) -> None:
        super()._begin_visual_approach(stable)
        self._publish_status(
            "camera_authoritative_docking_started",
            reference_point_base=list(self.profile.alignment.reference_point_base),
            current_point_base=list(stable.point_base),
            distance_handoff_used=False,
            translation_chunk_cap_m=min(
                float(self.get_parameter("camera_max_translation_chunk_m").value),
                float(self.get_parameter("precision_move_chunk_m").value),
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
