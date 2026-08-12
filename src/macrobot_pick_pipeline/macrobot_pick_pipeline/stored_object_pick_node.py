from __future__ import annotations

import json
import math
from pathlib import Path
import time
from typing import Any, Dict, List, Mapping, Optional, Tuple

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Empty, String

from .alignment_core import (
    AlignmentErrors,
    AlignmentProfile,
    alignment_errors,
    choose_alignment_action,
    observation_constraint_decision,
    pico_move_command_cm,
    pico_turn_command_deg,
)
from .planner import DetectionSample, StableDetection, StablePointFilter
from .profiles import Q, Vector3
from .grasp_keyframe_store import GraspKeyframeStore
from .stored_object_core import (
    OdomPose,
    StoredObjectProfileStore,
    StoredObjectRuntimeProfile,
    absolute_offsets_to_relative_turns,
    plan_return_to_pose,
    point_base_to_odom,
    pico_session_is_compatible,
    search_offsets,
)


TERMINAL_STATES = {"IDLE", "SUCCEEDED", "FAILED", "CANCELED", "TIMED_OUT"}
ACTIVE_DETECTION_STATES = {"RECORD_WAIT_DETECTION", "SEARCHING", "ALIGNING"}
BASE_MOTION_EVENTS = {"move_cm_result", "turn_deg_result", "move_ticks_result", "drive_relative_result"}
ARM_ERROR_EVENTS = {
    "runtime_interpolation_rejected",
    "defense_in_depth_rejection",
    "pico_error",
    "invalid_validated_goal",
}


def _json_object(text: str) -> Dict[str, Any]:
    text = text.strip()
    if not text:
        raise ValueError("empty JSON command")
    if not text.startswith("{"):
        return {"object_name": text}
    value = json.loads(text)
    if not isinstance(value, dict):
        raise ValueError("command must be a JSON object")
    return value


def _as_bool(value: object, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        lowered = value.strip().casefold()
        if lowered in {"true", "1", "yes", "on"}:
            return True
        if lowered in {"false", "0", "no", "off"}:
            return False
    return default


def _point_from_payload(value: object) -> Optional[Vector3]:
    if not isinstance(value, Mapping):
        return None
    try:
        point = (float(value["x"]), float(value["y"]), float(value["z"]))
    except (KeyError, TypeError, ValueError):
        return None
    return point if all(math.isfinite(item) for item in point) else None


def _q_close(a: Q, b: Q, tolerance: float = 1e-4) -> bool:
    return max(abs(a[index] - b[index]) for index in range(3)) <= tolerance


class StoredObjectPickNode(Node):
    """Stored-position search, visual alignment, and recorded grasp execution.

    Public behavior:
      * record a runtime object profile while the object is visible and graspable;
      * visible-test mode: assume finding already succeeded, align from the live
        localized point, then execute the recorded semantic grasp keyframes;
      * full mode: use Pico encoder odometry to return near the recording pose,
        run a bounded finder scan, visually align to the recorded camera-relative
        point, then execute the recorded semantic grasp keyframes.

    The persistent profile is an internal runtime adapter.  The LLM team owns the
    final public object structure; only the goal/cancel/result contract is meant
    to be consumed by Robot Action Gateway.
    """

    def __init__(self) -> None:
        super().__init__("macrobot_stored_object_pick")
        self._declare_parameters()

        default_alignment = AlignmentProfile(
            name="default",
            object_name="default",
            pick_profile="default",
            reference_point_base=(-0.20, 0.06, 0.10),
            recorded_at="",
            frame_id=str(self.get_parameter("base_frame").value),
            minimum_score=float(self.get_parameter("minimum_score").value),
            stability_count=int(self.get_parameter("stability_count").value),
            stability_window_sec=float(self.get_parameter("stability_window_sec").value),
            stability_radius_m=float(self.get_parameter("stability_radius_m").value),
            bearing_tolerance_deg=float(self.get_parameter("bearing_tolerance_deg").value),
            range_tolerance_m=float(self.get_parameter("range_tolerance_m").value),
            height_tolerance_m=float(self.get_parameter("height_tolerance_m").value),
            max_turn_step_deg=float(self.get_parameter("max_turn_step_deg").value),
            max_move_step_m=float(self.get_parameter("max_move_step_m").value),
            turn_speed=int(self.get_parameter("alignment_turn_speed").value),
            move_speed=int(self.get_parameter("alignment_move_speed").value),
            motion_timeout_sec=float(self.get_parameter("base_motion_timeout_sec").value),
            settle_sec=float(self.get_parameter("settle_sec").value),
            max_iterations=int(self.get_parameter("max_alignment_iterations").value),
            max_total_turn_deg=float(self.get_parameter("max_alignment_total_turn_deg").value),
            max_total_move_m=float(self.get_parameter("max_alignment_total_move_m").value),
            minimum_localization_quality=float(
                self.get_parameter("minimum_localization_quality").value
            ),
            maximum_depth_std_m=float(self.get_parameter("maximum_depth_std_m").value),
            maximum_center_std_px=float(
                self.get_parameter("maximum_center_std_px").value
            ),
            require_orientation_match=bool(
                self.get_parameter("require_orientation_match").value
            ),
            minimum_orientation_quality=float(
                self.get_parameter("minimum_orientation_quality").value
            ),
            orientation_tolerance_deg=float(
                self.get_parameter("orientation_tolerance_deg").value
            ),
        )
        default_alignment.validate()
        self.profile_store = StoredObjectProfileStore(
            str(self.get_parameter("profile_file").value),
            default_alignment,
        )
        self.default_alignment = default_alignment

        self.base_frame = str(self.get_parameter("base_frame").value)
        self.forward_axis_sign = float(self.get_parameter("forward_axis_sign").value)
        self.lateral_axis_sign = float(self.get_parameter("lateral_axis_sign").value)
        self.pico_turn_positive_is_right = bool(
            self.get_parameter("pico_turn_positive_is_right").value
        )
        self.pico_move_positive_is_forward = bool(
            self.get_parameter("pico_move_positive_is_forward").value
        )
        self.dry_run_base = bool(self.get_parameter("dry_run_base").value)
        self.stow_q: Q = self._parameter_q("stow_q")
        self.recordings_dir = Path(
            str(self.get_parameter("recordings_dir").value)
        ).expanduser().resolve()
        self.keyframe_store = GraspKeyframeStore(
            str(self.get_parameter("grasp_keyframe_profile_file").value)
        )

        # Publishers: new API and legacy compatibility for existing Gateway.
        self.status_pub = self.create_publisher(
            String, str(self.get_parameter("status_topic").value), 20
        )
        self.result_pub = self.create_publisher(
            String, str(self.get_parameter("result_topic").value), 20
        )
        self.legacy_status_pub = self.create_publisher(
            String, str(self.get_parameter("legacy_status_topic").value), 20
        )
        self.legacy_result_pub = self.create_publisher(
            String, str(self.get_parameter("legacy_result_topic").value), 20
        )
        self.pico_command_pub = self.create_publisher(
            String, str(self.get_parameter("pico_command_topic").value), 20
        )
        self.finder_goal_pub = self.create_publisher(
            String, str(self.get_parameter("finder_goal_topic").value), 10
        )
        self.finder_cancel_pub = self.create_publisher(
            String, str(self.get_parameter("finder_cancel_topic").value), 10
        )
        self.active_target_pub = self.create_publisher(
            String, str(self.get_parameter("active_target_topic").value), 10
        )
        self.joint_goal_pub = self.create_publisher(
            JointState, str(self.get_parameter("joint_goal_topic").value), 10
        )
        self.arm_stop_pub = self.create_publisher(
            Empty, str(self.get_parameter("arm_stop_topic").value), 10
        )
        self.arm_demo_command_pub = self.create_publisher(
            String, str(self.get_parameter("arm_demo_command_topic").value), 20
        )
        self.keyframe_command_pub = self.create_publisher(
            String, str(self.get_parameter("grasp_keyframe_command_topic").value), 20
        )
        self.keyframe_cancel_pub = self.create_publisher(
            String, str(self.get_parameter("grasp_keyframe_cancel_topic").value), 20
        )
        self.pick_goal_pub = self.create_publisher(
            String, str(self.get_parameter("pick_goal_topic").value), 10
        )
        self.pick_cancel_pub = self.create_publisher(
            String, str(self.get_parameter("pick_cancel_topic").value), 10
        )

        # Goal aliases keep the old Robot Action Gateway mapping functional.
        goal_topics = {
            str(self.get_parameter("goal_topic").value),
            str(self.get_parameter("legacy_goal_topic").value),
        }
        for topic in goal_topics:
            self.create_subscription(String, topic, self._goal_callback, 20)
        cancel_topics = {
            str(self.get_parameter("cancel_topic").value),
            str(self.get_parameter("legacy_cancel_topic").value),
        }
        for topic in cancel_topics:
            self.create_subscription(String, topic, self._cancel_callback, 20)

        record_topics = {
            str(self.get_parameter("record_topic").value),
            str(self.get_parameter("legacy_record_topic").value),
        }
        for topic in record_topics:
            self.create_subscription(String, topic, self._record_callback, 20)
        admin_topics = {
            str(self.get_parameter("admin_topic").value),
            str(self.get_parameter("legacy_admin_topic").value),
        }
        for topic in admin_topics:
            self.create_subscription(String, topic, self._admin_callback, 20)
        self.create_subscription(
            String,
            str(self.get_parameter("localized_detection_topic").value),
            self._detection_callback,
            50,
        )
        self.create_subscription(
            String,
            str(self.get_parameter("pico_response_topic").value),
            self._pico_response_callback,
            100,
        )
        self.create_subscription(
            JointState,
            str(self.get_parameter("logical_state_topic").value),
            self._logical_state_callback,
            50,
        )
        self.create_subscription(
            String,
            str(self.get_parameter("validation_status_topic").value),
            self._validation_callback,
            50,
        )
        self.create_subscription(
            String,
            str(self.get_parameter("bridge_status_topic").value),
            self._bridge_callback,
            50,
        )
        self.create_subscription(
            String,
            str(self.get_parameter("arm_demo_result_topic").value),
            self._arm_demo_result_callback,
            50,
        )
        self.create_subscription(
            String,
            str(self.get_parameter("grasp_keyframe_result_topic").value),
            self._keyframe_result_callback,
            50,
        )
        self.create_subscription(
            String,
            str(self.get_parameter("pick_result_topic").value),
            self._pick_result_callback,
            20,
        )

        # Runtime state.
        self.state = "IDLE"
        self.phase = "idle"
        self.request_id = ""
        self.object_name = ""
        self.profile_name = ""
        self.mode = "full"
        self.execute_pick = True
        self.profile: Optional[StoredObjectRuntimeProfile] = None
        self.filter = StablePointFilter()
        self.current_q: Q = (0.0, 0.0, 0.0)
        self.have_q = False
        self.last_object_point: Optional[Vector3] = None
        self.last_odom: Optional[OdomPose] = None
        self.last_pico_payload: Dict[str, Any] = {}
        self.last_base_response: Dict[str, Any] = {}

        self.goal_started = 0.0
        self.goal_deadline = 0.0
        self.phase_deadline = 0.0
        self.settle_until = 0.0
        self.finder_active = False
        self.start_finder_for_goal = True

        self.pending_odom_purpose = ""
        self.pending_odom_sent = 0.0
        self.record_point: Optional[Vector3] = None
        self.record_grasp_executor = "keyframes"
        self.record_grasp_trajectory = ""
        self.record_grasp_keyframe_profile = ""
        self.record_require_orientation_match: Optional[bool] = None
        self.record_stable_detection: Optional[StableDetection] = None
        self.record_pick_profile = ""

        self.coarse_steps: List[Tuple[str, float]] = []
        self.search_relative_turns: List[float] = []
        self.search_index = 0
        self.search_next_time = 0.0

        self.base_active = False
        self.base_expected_event = ""
        self.base_command = ""
        self.base_purpose = ""
        self.base_physical_amount = 0.0

        self.arm_active = False
        self.pending_arm_q: Optional[Q] = None
        self.arm_demo_command_id = ""
        self.keyframe_command_id = ""
        self.keyframe_preflight_only = False
        self.pick_waiting = False

        self.alignment_iterations = 0
        self.total_turn_deg = 0.0
        self.total_move_m = 0.0
        self.aligned_confirmations = 0
        self.last_errors: Optional[AlignmentErrors] = None
        self.steps: Dict[str, Any] = {}

        self.cancel_reason = ""
        self.cancel_deadline = 0.0
        self.cancel_terminal = "CANCELED"
        self.cancel_error_code = "RUN_CANCELED"
        self.cancel_details: Dict[str, Any] = {}
        self.cancel_wait_base = False
        self.cancel_wait_arm = False

        timer_hz = max(5.0, float(self.get_parameter("timer_rate_hz").value))
        self.create_timer(1.0 / timer_hz, self._timer_callback)
        self._publish_status("stored_object_pick_ready")
        self.get_logger().info(
            "Stored object pick ready: saved odom pose -> finder scan -> visual alignment -> recorded grasp"
        )

    # ------------------------------------------------------------------
    # Configuration and publication helpers
    # ------------------------------------------------------------------
    def _declare_parameters(self) -> None:
        defaults: Dict[str, Any] = {
            "goal_topic": "/macrobot/stored_pick/goal",
            "cancel_topic": "/macrobot/stored_pick/cancel",
            "record_topic": "/macrobot/stored_pick/record",
            "admin_topic": "/macrobot/stored_pick/admin",
            "status_topic": "/macrobot/stored_pick/status",
            "result_topic": "/macrobot/stored_pick/result",
            "legacy_goal_topic": "/macrobot/align_pick/goal",
            "legacy_cancel_topic": "/macrobot/base_alignment/cancel",
            "legacy_status_topic": "/macrobot/base_alignment/status",
            "legacy_result_topic": "/macrobot/base_alignment/result",
            "legacy_record_topic": "/macrobot/base_alignment/record",
            "legacy_admin_topic": "/macrobot/base_alignment/admin",
            "localized_detection_topic": "/macrobot/perception/localized_detection",
            "finder_goal_topic": "/object_finder/goal",
            "finder_cancel_topic": "/object_finder/cancel",
            "active_target_topic": "/macrobot/pick/active_target",
            "pico_command_topic": "/pico_debug/cmd",
            "pico_response_topic": "/pico_debug/response",
            "joint_goal_topic": "/macrobot/arm/joint_goal",
            "logical_state_topic": "/macrobot/arm/logical_joint_states",
            "validation_status_topic": "/macrobot/arm/validation_status",
            "bridge_status_topic": "/macrobot/arm/servo_bridge/status",
            "arm_stop_topic": "/macrobot/arm/stop",
            "arm_demo_command_topic": "/macrobot/arm/demo/command",
            "arm_demo_result_topic": "/macrobot/arm/demo/result",
            "grasp_keyframe_command_topic": "/macrobot/grasp_keyframes/command",
            "grasp_keyframe_cancel_topic": "/macrobot/grasp_keyframes/cancel",
            "grasp_keyframe_result_topic": "/macrobot/grasp_keyframes/result",
            "grasp_keyframe_profile_file": str(
                Path.home() / "MacRobot" / "data" / "grasp_keyframes" / "profiles.yaml"
            ),
            "pick_goal_topic": "/macrobot/pick/goal",
            "pick_cancel_topic": "/macrobot/pick/cancel",
            "pick_result_topic": "/macrobot/pick/result",
            "profile_file": str(
                Path.home() / "MacRobot" / "data" / "stored_objects" / "runtime_profiles.yaml"
            ),
            "recordings_dir": str(Path.home() / "MacRobot" / "data" / "arm_primitives"),
            "base_frame": "base_link",
            "forward_axis_sign": -1.0,
            "lateral_axis_sign": 1.0,
            "pico_turn_positive_is_right": True,
            "pico_move_positive_is_forward": True,
            "dry_run_base": False,
            "stow_before_base_motion": True,
            "stow_q": [0.0, 0.0, 0.0],
            "stow_timeout_sec": 20.0,
            "minimum_score": 0.0,
            "stability_count": 5,
            "stability_window_sec": 1.5,
            "stability_radius_m": 0.012,
            "minimum_localization_quality": 0.15,
            "maximum_depth_std_m": 0.035,
            "maximum_center_std_px": 20.0,
            "require_orientation_match": False,
            "minimum_orientation_quality": 0.25,
            "auto_require_orientation_quality": 0.65,
            "orientation_tolerance_deg": 25.0,
            "bearing_tolerance_deg": 2.0,
            "range_tolerance_m": 0.015,
            "height_tolerance_m": 0.030,
            "max_turn_step_deg": 8.0,
            "max_move_step_m": 0.040,
            "alignment_turn_speed": 150,
            "alignment_move_speed": 80,
            "coarse_turn_speed": 150,
            "coarse_move_speed": 80,
            "base_motion_timeout_sec": 10.0,
            "settle_sec": 0.45,
            "max_alignment_iterations": 20,
            "max_alignment_total_turn_deg": 120.0,
            "max_alignment_total_move_m": 0.60,
            "alignment_confirmation_count": 2,
            "record_timeout_sec": 30.0,
            "visible_test_timeout_sec": 20.0,
            "full_search_timeout_sec": 90.0,
            "overall_timeout_sec": 180.0,
            "odom_request_timeout_sec": 2.0,
            "cancel_confirm_timeout_sec": 4.0,
            "pico_reboot_tolerance_ms": 2000,
            "allow_missing_grasp_trajectory": False,
            "timer_rate_hz": 20.0,
        }
        for name, value in defaults.items():
            self.declare_parameter(name, value)

    def _parameter_q(self, name: str) -> Q:
        values = list(self.get_parameter(name).value)
        if len(values) != 3:
            raise ValueError(f"{name} must have exactly three values")
        q = tuple(float(item) for item in values)
        if not all(math.isfinite(item) for item in q):
            raise ValueError(f"{name} contains a non-finite value")
        return q  # type: ignore[return-value]

    def _publish_json(self, publisher, payload: Mapping[str, Any]) -> None:
        msg = String()
        msg.data = json.dumps(dict(payload), ensure_ascii=False)
        publisher.publish(msg)

    def _status_payload(self, event: str, ok: bool, details: Mapping[str, Any]) -> Dict[str, Any]:
        return {
            "ok": ok,
            "event": event,
            "action_state": self._public_action_state(),
            "state": self.state,
            "phase": self.phase,
            "request_id": self.request_id,
            "object_name": self.object_name,
            "profile": self.profile_name,
            "mode": self.mode,
            "execute_pick": self.execute_pick,
            **dict(details),
        }

    def _publish_status(self, event: str, ok: bool = True, **details: Any) -> None:
        payload = self._status_payload(event, ok, details)
        self._publish_json(self.status_pub, payload)
        self._publish_json(self.legacy_status_pub, payload)
        if ok:
            self.get_logger().info(json.dumps(payload, ensure_ascii=False))
        else:
            self.get_logger().warning(json.dumps(payload, ensure_ascii=False))

    def _publish_result(self, event: str, ok: bool, legacy_event: str, **details: Any) -> None:
        base = {
            "ok": ok,
            "event": event,
            "action_state": self._public_action_state(),
            "request_id": self.request_id,
            "object_name": self.object_name,
            "profile": self.profile_name,
            "mode": self.mode,
            "execute_pick": self.execute_pick,
            "phase": self.phase,
            "iterations": self.alignment_iterations,
            "total_turn_deg": self.total_turn_deg,
            "total_move_m": self.total_move_m,
            "steps": self.steps,
            "partial_state": self._partial_state(),
            **details,
        }
        self._publish_json(self.result_pub, base)
        legacy = dict(base)
        legacy["event"] = legacy_event
        legacy["alignment_profile"] = self.profile_name
        self._publish_json(self.legacy_result_pub, legacy)

    def _public_action_state(self) -> str:
        if self.state == "SUCCEEDED":
            return "SUCCEEDED"
        if self.state == "FAILED":
            return "FAILED"
        if self.state == "CANCELED":
            return "CANCELED"
        if self.state == "TIMED_OUT":
            return "TIMED_OUT"
        if self.state == "CANCEL_REQUESTED":
            return "CANCEL_REQUESTED"
        if self.state == "IDLE":
            return "IDLE"
        return "RUNNING"

    def _partial_state(self) -> Dict[str, Any]:
        return {
            "current_q": list(self.current_q),
            "last_object_point_base": (
                list(self.last_object_point) if self.last_object_point is not None else None
            ),
            "last_odom": (
                self.last_odom.to_mapping() if self.last_odom is not None else None
            ),
            "last_base_response": self.last_base_response or None,
            "base_estimate_reliable": (
                self.last_odom.reliable if self.last_odom is not None else None
            ),
        }

    def _is_busy(self) -> bool:
        return self.state not in TERMINAL_STATES

    def _publish_command_rejection(
        self,
        *,
        event: str,
        legacy_event: str,
        request_id: str,
        object_name: str,
        profile: str,
        mode: str,
        execute_pick: bool,
        error_code: str,
        reason: str,
    ) -> None:
        """Publish a terminal rejection without disturbing an active action."""
        payload = {
            "ok": False,
            "event": event,
            "action_state": "FAILED",
            "state": "FAILED",
            "phase": "rejected",
            "request_id": request_id,
            "object_name": object_name,
            "profile": profile,
            "mode": mode,
            "execute_pick": execute_pick,
            "error_code": error_code,
            "reason": reason,
        }
        self._publish_json(self.status_pub, payload)
        self._publish_json(self.result_pub, payload)
        self._publish_json(self.legacy_status_pub, payload)
        legacy = dict(payload)
        legacy["event"] = legacy_event
        legacy["alignment_profile"] = profile
        self._publish_json(self.legacy_result_pub, legacy)
        self.get_logger().warning(json.dumps(payload, ensure_ascii=False))

    # ------------------------------------------------------------------
    # Public commands
    # ------------------------------------------------------------------
    def _record_callback(self, msg: String) -> None:
        request: Dict[str, Any] = {}
        request_id = f"record-{int(time.time() * 1000)}"
        object_name = ""
        profile_name = ""
        try:
            request = _json_object(msg.data)
            request_id = str(request.get("request_id", request_id))
            object_name = str(request.get("object_name", "")).strip()
            profile_name = str(
                request.get("profile", request.get("alignment_profile", object_name))
            ).strip()
            if self._is_busy():
                raise RuntimeError("another stored-object action is active")
            if not object_name:
                raise ValueError("object_name is required")
            grasp_keyframe_profile = str(
                request.get("grasp_keyframe_profile", "")
            ).strip()
            grasp_trajectory = str(request.get("grasp_trajectory", "")).strip()
            pick_profile = str(request.get("pick_profile", object_name)).strip()
            start_finder = _as_bool(request.get("start_finder"), True)
            raw_require_orientation = request.get("require_orientation_match")
            require_orientation_match = (
                None
                if raw_require_orientation is None
                else _as_bool(raw_require_orientation, False)
            )
            if grasp_keyframe_profile:
                grasp_executor = "keyframes"
                self.keyframe_store.reload()
                self.keyframe_store.get(grasp_keyframe_profile).validate()
            elif grasp_trajectory:
                grasp_executor = "arm_demo"
                self._validate_grasp_trajectory(grasp_trajectory)
            else:
                raise ValueError(
                    "grasp_keyframe_profile or grasp_trajectory is required"
                )
        except Exception as exc:
            self._publish_command_rejection(
                event="stored_object_record_rejected",
                legacy_event="alignment_profile_record_failed",
                request_id=request_id,
                object_name=object_name,
                profile=profile_name,
                mode="record",
                execute_pick=False,
                error_code=(
                    "RESOURCE_BUSY" if isinstance(exc, RuntimeError) else "INVALID_ARGUMENT"
                ),
                reason=str(exc),
            )
            return

        self._reset_action_state()
        self.request_id = request_id
        self.object_name = object_name
        self.profile_name = profile_name
        self.record_grasp_executor = grasp_executor
        self.record_grasp_trajectory = grasp_trajectory
        self.record_grasp_keyframe_profile = grasp_keyframe_profile
        self.record_require_orientation_match = require_orientation_match
        self.record_pick_profile = pick_profile
        self.mode = "record"
        self.execute_pick = False
        self.start_finder_for_goal = start_finder
        self.state = "RUNNING"
        self.phase = "record_wait_detection"
        self.goal_started = time.monotonic()
        self.goal_deadline = self.goal_started + float(
            self.get_parameter("record_timeout_sec").value
        )
        self.filter.clear()
        if start_finder:
            self._start_finder(self.goal_deadline - self.goal_started)
        else:
            self._set_active_target(object_name)
        self._publish_status(
            "stored_object_record_started",
            grasp_executor=grasp_executor,
            grasp_trajectory=grasp_trajectory,
            grasp_keyframe_profile=grasp_keyframe_profile,
            pick_profile=pick_profile,
            position_scope="pico_odom_session",
        )

    def _goal_callback(self, msg: String) -> None:
        request: Dict[str, Any] = {}
        request_id = f"stored-pick-{int(time.time() * 1000)}"
        object_name = ""
        profile_name = ""
        mode = "full"
        execute_pick = True
        try:
            request = _json_object(msg.data)
            request_id = str(request.get("request_id", request_id))
            object_name = str(request.get("object_name", "")).strip()
            shared_profile = str(request.get("profile", "")).strip()
            profile_name = str(
                request.get("alignment_profile", shared_profile or object_name)
            ).strip()
            mode = str(request.get("mode", "full")).strip().casefold()
            execute_pick = _as_bool(request.get("execute_pick"), True)
            if self._is_busy():
                raise RuntimeError("another stored-object action is active")
            if not object_name:
                raise ValueError("object_name is required")
            if mode not in {"full", "visible_test"}:
                raise ValueError("mode must be full or visible_test")
            profile = self.profile_store.get(profile_name, object_name)
            start_finder = _as_bool(request.get("start_finder"), mode == "full")
        except Exception as exc:
            error_code = "RESOURCE_BUSY" if isinstance(exc, RuntimeError) else (
                "GRASP_PROFILE_NOT_FOUND" if isinstance(exc, KeyError) else "INVALID_ARGUMENT"
            )
            self._publish_command_rejection(
                event="stored_pick_rejected",
                legacy_event="alignment_failed",
                request_id=request_id,
                object_name=object_name,
                profile=profile_name,
                mode=mode,
                execute_pick=execute_pick,
                error_code=error_code,
                reason=str(exc),
            )
            return

        self._reset_action_state()
        self.request_id = request_id
        self.object_name = object_name
        self.profile_name = profile.name
        self.profile = profile
        self.mode = mode
        self.execute_pick = execute_pick
        self.start_finder_for_goal = start_finder
        self.state = "RUNNING"
        self.phase = "starting"
        self.goal_started = time.monotonic()
        overall = float(
            request.get("timeout_sec", self.get_parameter("overall_timeout_sec").value)
        )
        self.goal_deadline = self.goal_started + max(1.0, overall)

        if bool(self.get_parameter("stow_before_base_motion").value) and (
            not self.have_q or not _q_close(self.current_q, self.stow_q, 0.01)
        ):
            self._command_arm_q(self.stow_q, "stow")
        else:
            self._after_stow()
        self._publish_status(
            "stored_pick_started",
            profile_mapping=profile.to_mapping(),
        )

    def _admin_callback(self, msg: String) -> None:
        try:
            request = _json_object(msg.data)
            action = str(request.get("action", msg.data)).strip().casefold()
            if action in {"list", "status", "profiles"}:
                self._publish_status(
                    "stored_object_profiles",
                    profiles=self.profile_store.mappings(),
                    profile_file=str(self.profile_store.path),
                )
                return
            if action == "reload":
                self.profile_store.reload()
                self._publish_status("stored_object_profiles_reloaded", names=list(self.profile_store.names()))
                return
            if action == "delete":
                name = str(request.get("profile", request.get("name", ""))).strip()
                if not name:
                    raise ValueError("profile is required")
                deleted = self.profile_store.delete(name)
                self._publish_status(
                    "stored_object_profile_deleted" if deleted else "stored_object_profile_not_found",
                    deleted,
                    profile=name,
                )
                return
            raise ValueError(f"unsupported admin action: {action}")
        except Exception as exc:
            self._publish_status("stored_object_admin_failed", False, error=str(exc))

    def _cancel_callback(self, msg: String) -> None:
        reason = msg.data.strip() or "user_cancel"
        self._request_cancel(reason, terminal="CANCELED")

    # ------------------------------------------------------------------
    # Perception, Pico, and arm callbacks
    # ------------------------------------------------------------------
    def _detection_callback(self, msg: String) -> None:
        if self.phase not in {"record_wait_detection", "search", "align"}:
            return
        try:
            payload = json.loads(msg.data)
        except Exception:
            return
        if not isinstance(payload, dict) or payload.get("event") != "localized_object":
            return
        if str(payload.get("object_name", "")).strip().casefold() != self.object_name.casefold():
            return
        point = _point_from_payload(payload.get("point_base"))
        if point is None:
            return
        try:
            score = float(payload.get("score", 0.0))
            stamp = float(payload.get("stamp_sec", time.time()))
        except (TypeError, ValueError):
            return
        if not all(math.isfinite(value) for value in (*point, score, stamp)):
            return
        self.last_object_point = point
        localization = payload.get("localization", {})
        orientation = payload.get("orientation", {})
        if not isinstance(localization, Mapping):
            localization = {}
        if not isinstance(orientation, Mapping):
            orientation = {}
        self.filter.add(
            DetectionSample(
                stamp_sec=stamp,
                object_name=self.object_name,
                score=score,
                point_base=point,
                source=str(payload.get("source", "")),
                localization_method=str(localization.get("method", "")),
                localization_quality=float(localization.get("quality", 0.0) or 0.0),
                center_std_px=float(payload.get("center_std_px", 0.0) or 0.0),
                depth_std_m=float(payload.get("depth_std_m", 0.0) or 0.0),
                orientation_deg=float(orientation.get("angle_deg", 0.0) or 0.0),
                orientation_class=str(orientation.get("class", "unknown")),
                orientation_quality=float(orientation.get("quality", 0.0) or 0.0),
            )
        )

    def _pico_response_callback(self, msg: String) -> None:
        try:
            payload = json.loads(msg.data)
        except Exception:
            return
        if not isinstance(payload, dict):
            return
        self.last_pico_payload = dict(payload)
        event = str(payload.get("event", ""))

        if event == "odometry":
            odom = self._odom_from_payload(payload)
            if odom is not None:
                self.last_odom = odom
                purpose = self.pending_odom_purpose
                self.pending_odom_purpose = ""
                if purpose == "record":
                    self._complete_recording_with_odom(odom)
                elif purpose == "coarse":
                    self._start_coarse_return(odom)
            return

        if event not in BASE_MOTION_EVENTS:
            return
        if not self.base_active:
            return
        if event != self.base_expected_event:
            return

        self.base_active = False
        self.last_base_response = dict(payload)
        odom = self._odom_from_payload(payload)
        if odom is not None:
            self.last_odom = odom
        status = str(payload.get("status", ""))

        if self.state == "CANCEL_REQUESTED":
            if status in {"stopped", "done", "timeout", "stall", "encoder_direction_error"}:
                self.cancel_wait_base = False
                self._try_finish_cancel()
            return

        if payload.get("ok") is not True or status != "done":
            self._fail(
                "MOTION_EXECUTION_FAILED",
                reason=f"base motion ended with status={status or 'unknown'}",
                pico_response=payload,
            )
            return

        self.steps[self.base_purpose] = dict(payload)
        purpose = self.base_purpose
        self.base_purpose = ""
        if purpose.startswith("coarse"):
            self._run_next_coarse_step()
        elif purpose == "search_turn":
            self.phase = "search"
            assert self.profile is not None
            self.search_next_time = time.monotonic() + self.profile.search_dwell_sec
            self.filter.clear()
        elif purpose.startswith("align"):
            assert self.profile is not None
            self.phase = "align_settle"
            self.settle_until = time.monotonic() + self.profile.alignment.settle_sec
            self.filter.clear()

    def _logical_state_callback(self, msg: JointState) -> None:
        values = dict(zip(msg.name, msg.position))
        names = ("arm_lift_joint", "wrist_pitch_joint", "gripper_joint")
        if all(name in values for name in names):
            q = tuple(float(values[name]) for name in names)
            if all(math.isfinite(value) for value in q):
                self.current_q = q  # type: ignore[assignment]
                self.have_q = True

    def _validation_callback(self, msg: String) -> None:
        if not self.arm_active or self.pending_arm_q is None:
            return
        try:
            payload = json.loads(msg.data)
        except Exception:
            return
        if not isinstance(payload, dict):
            return
        if str(payload.get("event", "")) == "goal_rejected":
            self.arm_active = False
            self._fail("ARM_PATH_UNSAFE", reason="stow goal rejected", validator=payload)

    def _bridge_callback(self, msg: String) -> None:
        try:
            payload = json.loads(msg.data)
        except Exception:
            return
        if not isinstance(payload, dict):
            return
        event = str(payload.get("event", ""))
        if self.state == "CANCEL_REQUESTED" and event == "trajectory_stopped":
            self.cancel_wait_arm = False
            self.arm_active = False
            self._try_finish_cancel()
            return
        if not self.arm_active or self.pending_arm_q is None:
            return
        if event in ARM_ERROR_EVENTS:
            self.arm_active = False
            self._fail("ARM_EXECUTION_FAILED", reason=event, bridge=payload)
            return
        if event != "trajectory_completed":
            return
        goal = payload.get("goal")
        if isinstance(goal, list) and len(goal) == 3:
            candidate = tuple(float(item) for item in goal)
            if not _q_close(candidate, self.pending_arm_q):
                return
        label = self.phase
        self.current_q = self.pending_arm_q
        self.pending_arm_q = None
        self.arm_active = False
        self.steps[label] = dict(payload)
        if label == "stow":
            self._after_stow()

    def _arm_demo_result_callback(self, msg: String) -> None:
        if not self.arm_demo_command_id:
            return
        try:
            payload = json.loads(msg.data)
        except Exception:
            return
        if not isinstance(payload, dict):
            return
        if str(payload.get("command_id", "")) != self.arm_demo_command_id:
            return
        event = str(payload.get("event", ""))
        if self.state == "CANCEL_REQUESTED" and event == "arm_demo_motion_stopped":
            self.cancel_wait_arm = False
            self.arm_active = False
            self.arm_demo_command_id = ""
            self._try_finish_cancel()
            return
        if event == "arm_demo_playback_completed" and payload.get("ok", True) is True:
            self.arm_active = False
            self.arm_demo_command_id = ""
            self.steps["grasp"] = dict(payload)
            self._succeed()
            return
        if event in {
            "arm_demo_playback_failed",
            "arm_demo_playback_rejected",
            "arm_demo_playback_timeout",
            "arm_demo_command_failed",
        } or payload.get("ok") is False:
            self.arm_active = False
            self.arm_demo_command_id = ""
            self._fail("GRIPPER_EXECUTION_FAILED", reason=event or "arm demo failed", arm_demo=payload)

    def _keyframe_result_callback(self, msg: String) -> None:
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
        if self.state == "CANCEL_REQUESTED":
            if event in {
                "grasp_keyframe_cancel_failed",
                "grasp_keyframe_execution_failed",
            }:
                self.cancel_terminal = "FAILED"
                self.cancel_error_code = "SAFE_STOP_UNCONFIRMED"
                self.cancel_details["keyframe_cancel_result"] = dict(payload)
            if event in {
                "grasp_keyframe_execution_cancelled",
                "grasp_keyframe_cancel_failed",
                "grasp_keyframe_execution_failed",
                "grasp_keyframe_preflight_succeeded",
                "grasp_keyframe_preflight_failed",
                "grasp_keyframe_command_rejected",
            }:
                self.cancel_wait_arm = False
                self.arm_active = False
                self.keyframe_command_id = ""
                self.keyframe_preflight_only = False
                self._try_finish_cancel()
            return
        if event == "grasp_keyframe_preflight_succeeded" and payload.get("ok") is True:
            preflight_only = self.keyframe_preflight_only
            self.keyframe_preflight_only = False
            self.arm_active = False
            self.keyframe_command_id = ""
            self.steps["grasp_preflight"] = dict(payload)
            if preflight_only and self.execute_pick:
                self._start_grasp()
            else:
                self._succeed()
            return
        if event == "grasp_keyframe_execution_completed" and payload.get("ok") is True:
            self.arm_active = False
            self.keyframe_command_id = ""
            self.keyframe_preflight_only = False
            self.steps["grasp"] = dict(payload)
            self._succeed()
            return
        if event in {
            "grasp_keyframe_execution_failed",
            "grasp_keyframe_preflight_failed",
            "grasp_keyframe_command_rejected",
        } or payload.get("ok") is False:
            self.arm_active = False
            self.keyframe_command_id = ""
            self.keyframe_preflight_only = False
            self._fail(
                "ARM_PATH_UNSAFE" if "preflight" in event else "GRASP_FAILED",
                reason=event or "semantic grasp failed",
                keyframe_result=payload,
            )

    def _pick_result_callback(self, msg: String) -> None:
        if not self.pick_waiting:
            return
        try:
            payload = json.loads(msg.data)
        except Exception:
            return
        if not isinstance(payload, dict):
            return
        if str(payload.get("object_name", "")).casefold() != self.object_name.casefold():
            return
        event = str(payload.get("event", ""))
        if self.state == "CANCEL_REQUESTED":
            if event in {"pick_cancelled", "pick_failed"} or payload.get("ok") is False:
                self.pick_waiting = False
                self.cancel_wait_arm = False
                self._try_finish_cancel()
            return
        if payload.get("ok") is True and event in {"pick_completed", "localized_only"}:
            self.pick_waiting = False
            self.steps["grasp"] = dict(payload)
            self._succeed()
        elif payload.get("ok") is False or event == "pick_failed":
            self.pick_waiting = False
            self._fail("GRASP_FAILED", reason=event or "pick failed", pick_result=payload)

    # ------------------------------------------------------------------
    # State-machine transitions
    # ------------------------------------------------------------------
    def _after_stow(self) -> None:
        if self.mode == "visible_test":
            self._start_search(visible_test=True)
        else:
            self._request_odom("coarse")

    def _command_arm_q(self, q: Q, label: str) -> None:
        goal = JointState()
        goal.header.stamp = self.get_clock().now().to_msg()
        goal.name = ["arm_lift_joint", "wrist_pitch_joint", "gripper_joint"]
        goal.position = list(q)
        self.pending_arm_q = q
        self.arm_active = True
        self.phase = label
        self.phase_deadline = time.monotonic() + float(
            self.get_parameter("stow_timeout_sec").value
        )
        self.joint_goal_pub.publish(goal)
        self._publish_status("arm_goal_commanded", label=label, q=list(q))

    def _request_odom(self, purpose: str) -> None:
        self.pending_odom_purpose = purpose
        self.pending_odom_sent = time.monotonic()
        self.phase = f"wait_odom_{purpose}"
        self._send_pico("ODOM?")
        self._publish_status("odometry_requested", purpose=purpose)

    def _start_coarse_return(self, current: OdomPose) -> None:
        assert self.profile is not None
        if not current.reliable:
            self._fail("POSE_ESTIMATE_UNRELIABLE", reason="current Pico odometry is unreliable")
            return
        recorded_time = self.profile.search_pose_odom.pico_time_ms
        if not pico_session_is_compatible(
            recorded_time,
            current.pico_time_ms,
            tolerance_ms=int(self.get_parameter("pico_reboot_tolerance_ms").value),
        ):
            self._fail(
                "POSE_ESTIMATE_UNRELIABLE",
                reason="Pico odometry session appears to have restarted after recording",
            )
            return
        plan = plan_return_to_pose(
            current,
            self.profile.search_pose_odom,
            position_tolerance_m=self.profile.coarse_position_tolerance_m,
            angle_tolerance_deg=self.profile.coarse_angle_tolerance_deg,
        )
        if abs(plan.move_distance_m) > self.profile.coarse_max_move_m:
            self._fail("SAFETY_BLOCKED", reason="coarse return distance exceeds profile limit")
            return
        if max(abs(plan.initial_turn_deg), abs(plan.final_turn_deg)) > self.profile.coarse_max_turn_deg:
            self._fail("SAFETY_BLOCKED", reason="coarse return turn exceeds profile limit")
            return
        self.coarse_steps = []
        if abs(plan.initial_turn_deg) > 1e-9:
            self.coarse_steps.append(("turn", plan.initial_turn_deg))
        if abs(plan.move_distance_m) > 1e-9:
            self.coarse_steps.append(("move", plan.move_distance_m))
        if abs(plan.final_turn_deg) > 1e-9:
            self.coarse_steps.append(("turn", plan.final_turn_deg))
        self.steps["coarse_plan"] = {
            "initial_turn_deg": plan.initial_turn_deg,
            "move_distance_m": plan.move_distance_m,
            "final_turn_deg": plan.final_turn_deg,
        }
        self._run_next_coarse_step()

    def _run_next_coarse_step(self) -> None:
        if not self.coarse_steps:
            self._start_search(visible_test=False)
            return
        action, amount = self.coarse_steps.pop(0)
        if action == "turn":
            self._send_turn(amount, "coarse_turn")
        else:
            self._send_move(amount, "coarse_move")

    def _start_search(self, *, visible_test: bool) -> None:
        assert self.profile is not None
        self.filter.clear()
        self.phase = "search"
        timeout = (
            float(self.get_parameter("visible_test_timeout_sec").value)
            if visible_test
            else float(self.get_parameter("full_search_timeout_sec").value)
        )
        self.phase_deadline = min(self.goal_deadline, time.monotonic() + timeout)
        if self.start_finder_for_goal:
            self._start_finder(timeout)
        else:
            self._set_active_target(self.object_name)
        if visible_test:
            offsets = (0.0,)
        else:
            generated = search_offsets(
                self.profile.search_max_yaw_deg,
                self.profile.search_step_deg,
            )
            # Return to the recorded heading before declaring search failure.
            offsets = generated if generated[-1] == 0.0 else (*generated, 0.0)
        self.search_relative_turns = list(absolute_offsets_to_relative_turns(offsets))[1:]
        self.search_index = 0
        self.search_next_time = time.monotonic() + self.profile.search_dwell_sec
        self._publish_status(
            "object_search_started",
            visible_test=visible_test,
            finder_started=self.start_finder_for_goal,
            search_offsets_deg=list(offsets),
        )

    def _try_search_or_align(self) -> None:
        stable = self._stable_detection()
        if stable is not None:
            self.last_object_point = stable.point_base
            self.phase = "align"
            self.filter.clear()
            self._publish_status(
                "object_acquired",
                point_base=list(stable.point_base),
                sample_count=stable.sample_count,
                stability_radius_m=stable.radius_m,
            )
            return
        if self.mode == "visible_test":
            return
        now = time.monotonic()
        if now < self.search_next_time or self.base_active:
            return
        if self.search_index >= len(self.search_relative_turns):
            self._fail("OBJECT_NOT_FOUND", reason="bounded stored-pose search exhausted")
            return
        turn = self.search_relative_turns[self.search_index]
        self.search_index += 1
        self._send_turn(turn, "search_turn")

    def _try_alignment_step(self) -> None:
        assert self.profile is not None
        stable = self._stable_detection()
        if stable is None:
            return
        self.last_object_point = stable.point_base
        constraint = observation_constraint_decision(
            self.profile.alignment,
            localization_quality=stable.localization_quality,
            depth_std_m=stable.depth_std_m,
            center_std_px=stable.center_std_px,
            orientation_deg=stable.orientation_deg,
            orientation_class=stable.orientation_class,
            orientation_quality=stable.orientation_quality,
        )
        if constraint.action == "reject":
            self._fail("TARGET_NOT_GRASPABLE", reason=constraint.reason)
            return
        try:
            errors = alignment_errors(
                stable.point_base,
                self.profile.alignment.reference_point_base,
                forward_axis_sign=self.forward_axis_sign,
                lateral_axis_sign=self.lateral_axis_sign,
            )
            decision = choose_alignment_action(errors, self.profile.alignment)
        except Exception as exc:
            self._fail("TARGET_NOT_GRASPABLE", reason=str(exc))
            return
        self.last_errors = errors
        self._publish_status(
            "alignment_observation",
            current_point_base=list(stable.point_base),
            reference_point_base=list(self.profile.alignment.reference_point_base),
            errors=self._error_mapping(errors),
            decision={
                "action": decision.action,
                "amount": decision.amount,
                "reason": decision.reason,
            },
        )
        if decision.action == "reject":
            self._fail("TARGET_NOT_GRASPABLE", reason=decision.reason)
            return
        if decision.action == "aligned":
            self.aligned_confirmations += 1
            required = max(1, int(self.get_parameter("alignment_confirmation_count").value))
            if self.aligned_confirmations < required:
                self.filter.clear()
                return
            self._alignment_complete()
            return
        self.aligned_confirmations = 0
        self.alignment_iterations += 1
        if self.alignment_iterations > self.profile.alignment.max_iterations:
            self._fail("ALIGNMENT_TIMEOUT", reason="alignment iteration limit")
            return
        if decision.action == "turn":
            if self.total_turn_deg + abs(decision.amount) > self.profile.alignment.max_total_turn_deg:
                self._fail("SAFETY_BLOCKED", reason="alignment turn budget exceeded")
                return
            self.total_turn_deg += abs(decision.amount)
            self._send_turn(decision.amount, "align_turn")
        elif decision.action == "move":
            if self.total_move_m + abs(decision.amount) > self.profile.alignment.max_total_move_m:
                self._fail("SAFETY_BLOCKED", reason="alignment move budget exceeded")
                return
            self.total_move_m += abs(decision.amount)
            self._send_move(decision.amount, "align_move")

    def _alignment_complete(self) -> None:
        self._cancel_finder("alignment_complete")
        self._clear_active_target()
        self.steps["alignment"] = {
            "iterations": self.alignment_iterations,
            "errors": self._error_mapping(self.last_errors),
            "point_base": list(self.last_object_point) if self.last_object_point else None,
        }
        # ALIGN_WITH_OBJECT must mean more than geometric tolerance. For the
        # default semantic-keyframe executor, prove that the current object
        # point has an IK solution and every segment is inside the sampled
        # safe region before reporting ALIGN success or starting physical grasp.
        if self.profile is not None and self.profile.grasp_executor == "keyframes":
            self._start_grasp_preflight()
            return
        if not self.execute_pick:
            self._succeed()
            return
        self._start_grasp()

    def _start_grasp_preflight(self) -> None:
        assert self.profile is not None
        if self.last_object_point is None:
            self._fail("OBJECT_LOST", reason="object point unavailable before grasp preflight")
            return
        self.phase = "grasp_preflight"
        self.keyframe_command_id = f"stored-pick-preflight-{self.request_id}"
        self.keyframe_preflight_only = True
        self.arm_active = True
        self.phase_deadline = self.goal_deadline
        self._publish_json(
            self.keyframe_command_pub,
            {
                "action": "preflight",
                "command_id": self.keyframe_command_id,
                "profile": self.profile.grasp_keyframe_profile,
                "object_name": self.object_name,
                "object_point_base": list(self.last_object_point),
            },
        )
        self._publish_status(
            "semantic_grasp_preflight_started",
            grasp_keyframe_profile=self.profile.grasp_keyframe_profile,
            align_only=not self.execute_pick,
        )

    def _start_grasp(self) -> None:
        assert self.profile is not None
        self.phase = "grasp"
        if self.profile.grasp_executor == "keyframes":
            if self.last_object_point is None:
                self._fail("OBJECT_LOST", reason="object point unavailable before grasp")
                return
            self.keyframe_command_id = f"stored-pick-keyframes-{self.request_id}"
            self.keyframe_preflight_only = False
            self.arm_active = True
            self.phase_deadline = self.goal_deadline
            self._publish_json(
                self.keyframe_command_pub,
                {
                    "action": "play",
                    "command_id": self.keyframe_command_id,
                    "profile": self.profile.grasp_keyframe_profile,
                    "object_name": self.object_name,
                    "object_point_base": list(self.last_object_point),
                },
            )
            self._publish_status(
                "semantic_grasp_started",
                grasp_keyframe_profile=self.profile.grasp_keyframe_profile,
            )
            return
        if self.profile.grasp_executor == "arm_demo":
            self.arm_demo_command_id = f"stored-pick-grasp-{self.request_id}"
            self.arm_active = True
            self.phase_deadline = self.goal_deadline
            self._publish_json(
                self.arm_demo_command_pub,
                {
                    "action": "play",
                    "command_id": self.arm_demo_command_id,
                    "name": self.profile.grasp_trajectory,
                    "speed_scale": 1.0,
                },
            )
            self._publish_status(
                "recorded_grasp_started",
                grasp_trajectory=self.profile.grasp_trajectory,
            )
            return
        self.pick_waiting = True
        self.phase_deadline = self.goal_deadline
        self._publish_json(
            self.pick_goal_pub,
            {
                "object_name": self.object_name,
                "profile": self.profile.pick_profile or self.object_name,
                "execute": True,
            },
        )
        self._publish_status("pick_coordinator_handoff_started")

    # ------------------------------------------------------------------
    # Record completion and profile defaults
    # ------------------------------------------------------------------
    def _complete_recording_with_odom(self, odom: OdomPose) -> None:
        if self.record_point is None:
            self._fail("INTERNAL_ERROR", reason="record point disappeared")
            return
        if not odom.reliable:
            self._fail("POSE_ESTIMATE_UNRELIABLE", reason="Pico odometry is unreliable")
            return
        try:
            object_odom = point_base_to_odom(
                self.record_point,
                odom,
                forward_axis_sign=self.forward_axis_sign,
                lateral_axis_sign=self.lateral_axis_sign,
            )
            try:
                existing = self.profile_store.get(self.profile_name, self.object_name)
            except KeyError:
                existing = self._new_profile_template()
            recorded_orientation_quality = (
                self.record_stable_detection.orientation_quality
                if self.record_stable_detection is not None else 0.0
            )
            require_orientation_match = self.record_require_orientation_match
            if require_orientation_match is None:
                require_orientation_match = (
                    recorded_orientation_quality
                    >= float(self.get_parameter("auto_require_orientation_quality").value)
                )
            stored = existing.with_recording(
                point_base=self.record_point,
                search_pose=odom,
                object_point_odom=object_odom,
                object_name=self.object_name,
                grasp_executor=self.record_grasp_executor,
                grasp_trajectory=self.record_grasp_trajectory,
                grasp_keyframe_profile=self.record_grasp_keyframe_profile,
                pick_profile=self.record_pick_profile,
                orientation_deg=(
                    self.record_stable_detection.orientation_deg
                    if self.record_stable_detection is not None else 0.0
                ),
                orientation_class=(
                    self.record_stable_detection.orientation_class
                    if self.record_stable_detection is not None else "unknown"
                ),
                orientation_quality=(
                    self.record_stable_detection.orientation_quality
                    if self.record_stable_detection is not None else 0.0
                ),
            )
            self.profile_store.upsert(stored)
        except Exception as exc:
            self._fail("POSITION_STORE_ERROR", reason=str(exc))
            return
        self.profile = stored
        self._cancel_finder("stored_object_recorded")
        self._clear_active_target()
        self.state = "SUCCEEDED"
        self.phase = "record_completed"
        self._publish_result(
            "stored_object_recorded",
            True,
            "alignment_profile_recorded",
            profile_mapping=stored.to_mapping(),
            profile_file=str(self.profile_store.path),
        )
        self._publish_status("stored_object_recorded", profile_mapping=stored.to_mapping())

    def _new_profile_template(self) -> StoredObjectRuntimeProfile:
        alignment = AlignmentProfile(
            **{
                **self.default_alignment.__dict__,
                "name": self.profile_name,
                "object_name": self.object_name,
                "pick_profile": self.record_pick_profile,
            }
        )
        return StoredObjectRuntimeProfile(
            name=self.profile_name,
            object_name=self.object_name,
            recorded_at="",
            search_pose_odom=OdomPose(0.0, 0.0, 0.0, True, None),
            object_point_odom=(0.0, 0.0, 0.0),
            alignment=alignment,
            grasp_executor=self.record_grasp_executor,
            grasp_trajectory=self.record_grasp_trajectory,
            grasp_keyframe_profile=self.record_grasp_keyframe_profile,
            pick_profile=self.record_pick_profile,
        )

    def _validate_grasp_trajectory(self, name: str) -> None:
        if bool(self.get_parameter("allow_missing_grasp_trajectory").value):
            return
        path = self.recordings_dir / f"{name}.yaml"
        if not path.is_file():
            raise ValueError(f"recorded arm trajectory not found: {path}")

    # ------------------------------------------------------------------
    # Low-level commands
    # ------------------------------------------------------------------
    def _send_pico(self, command: str) -> None:
        message = String()
        message.data = command
        self.pico_command_pub.publish(message)

    def _send_turn(self, physical_left_positive_deg: float, purpose: str) -> None:
        assert self.profile is not None
        speed = (
            int(self.get_parameter("coarse_turn_speed").value)
            if purpose.startswith("coarse") or purpose == "search_turn"
            else self.profile.alignment.turn_speed
        )
        pico_deg = pico_turn_command_deg(
            physical_left_positive_deg,
            pico_positive_is_right=self.pico_turn_positive_is_right,
        )
        timeout = self.profile.alignment.motion_timeout_sec
        command = f"TURN_DEG {pico_deg:.3f} {speed} {timeout:.2f}"
        self._start_base_command(command, "turn_deg_result", purpose, physical_left_positive_deg)

    def _send_move(self, physical_forward_positive_m: float, purpose: str) -> None:
        assert self.profile is not None
        speed = (
            int(self.get_parameter("coarse_move_speed").value)
            if purpose.startswith("coarse")
            else self.profile.alignment.move_speed
        )
        pico_cm = pico_move_command_cm(
            physical_forward_positive_m,
            pico_positive_is_forward=self.pico_move_positive_is_forward,
        )
        timeout = self.profile.alignment.motion_timeout_sec
        command = f"MOVE_CM {pico_cm:.3f} {speed} {timeout:.2f}"
        self._start_base_command(command, "move_cm_result", purpose, physical_forward_positive_m)

    def _start_base_command(
        self,
        command: str,
        expected_event: str,
        purpose: str,
        physical_amount: float,
    ) -> None:
        self.base_active = True
        self.base_expected_event = expected_event
        self.base_command = command
        self.base_purpose = purpose
        self.base_physical_amount = physical_amount
        self.phase = purpose
        self.phase_deadline = time.monotonic() + float(
            self.get_parameter("base_motion_timeout_sec").value
        ) + 1.0
        if self.dry_run_base:
            self.last_base_response = {
                "ok": True,
                "event": expected_event,
                "status": "done",
                "dry_run": True,
            }
            self.base_active = False
            self.steps[purpose] = dict(self.last_base_response)
            if purpose.startswith("coarse"):
                self._run_next_coarse_step()
            elif purpose == "search_turn":
                self.phase = "search"
                assert self.profile is not None
                self.search_next_time = time.monotonic() + self.profile.search_dwell_sec
            else:
                self.phase = "align_settle"
                assert self.profile is not None
                self.settle_until = time.monotonic() + self.profile.alignment.settle_sec
            return
        self._send_pico(command)
        self._publish_status(
            "base_motion_commanded",
            purpose=purpose,
            physical_amount=physical_amount,
            pico_command=command,
        )

    def _start_finder(self, timeout_sec: float) -> None:
        self.finder_active = True
        self._set_active_target(self.object_name)
        self._publish_json(
            self.finder_goal_pub,
            {
                "object_name": self.object_name,
                "timeout_sec": max(1.0, timeout_sec),
                "continuous": True,
                "request_id": self.request_id,
            },
        )

    def _cancel_finder(self, reason: str) -> None:
        if self.finder_active:
            message = String()
            message.data = reason
            self.finder_cancel_pub.publish(message)
        self.finder_active = False

    def _set_active_target(self, object_name: str) -> None:
        message = String()
        message.data = object_name
        self.active_target_pub.publish(message)

    def _clear_active_target(self) -> None:
        self._set_active_target("")

    def _odom_from_payload(self, payload: Mapping[str, Any]) -> Optional[OdomPose]:
        raw = payload.get("odometry")
        if not isinstance(raw, Mapping):
            raw = payload.get("odom")
        if not isinstance(raw, Mapping):
            return None
        try:
            return OdomPose(
                x_m=float(raw["x_m"]),
                y_m=float(raw["y_m"]),
                yaw_deg=float(raw["yaw_deg"]),
                reliable=bool(raw.get("reliable", False)),
                pico_time_ms=(
                    int(payload["time_ms"]) if payload.get("time_ms") is not None else None
                ),
            )
        except (KeyError, TypeError, ValueError):
            return None

    # ------------------------------------------------------------------
    # Cancellation and terminal states
    # ------------------------------------------------------------------
    def _request_cancel(
        self,
        reason: str,
        *,
        terminal: str,
        error_code: Optional[str] = None,
        details: Optional[Mapping[str, Any]] = None,
    ) -> None:
        if self.state in TERMINAL_STATES:
            return
        if self.state == "CANCEL_REQUESTED":
            return
        self.cancel_reason = reason
        self.cancel_terminal = terminal
        self.cancel_error_code = error_code or (
            "ACTION_HARD_TIMEOUT" if terminal == "TIMED_OUT" else
            "RUN_CANCELED" if terminal == "CANCELED" else
            "INTERNAL_ERROR"
        )
        self.cancel_details = dict(details or {})
        self.state = "CANCEL_REQUESTED"
        self.phase = "cancel_requested"
        self.cancel_deadline = time.monotonic() + float(
            self.get_parameter("cancel_confirm_timeout_sec").value
        )
        self._cancel_finder(reason)
        self._clear_active_target()
        pick_cancel = String()
        pick_cancel.data = reason
        self.pick_cancel_pub.publish(pick_cancel)

        self.cancel_wait_base = self.base_active
        self.cancel_wait_arm = self.arm_active or self.pick_waiting
        if self.cancel_wait_base:
            self._send_pico("STOP")
        elif self.pick_waiting:
            # The current recorded-grasp path does not move the base, but an
            # optional pick coordinator may. Issue a best-effort base STOP
            # without waiting for a motion result when no direct base command
            # is tracked by this node.
            self._send_pico("STOP")
        if self.cancel_wait_arm:
            self.arm_stop_pub.publish(Empty())
            if self.arm_demo_command_id:
                self._publish_json(
                    self.arm_demo_command_pub,
                    {
                        "action": "stop",
                        "command_id": self.arm_demo_command_id,
                    },
                )
            if self.keyframe_command_id:
                cancel = String()
                cancel.data = self.keyframe_command_id
                self.keyframe_cancel_pub.publish(cancel)
        self._publish_status(
            "cancel_requested",
            False,
            reason=reason,
            waiting_for_base_stop=self.cancel_wait_base,
            waiting_for_arm_stop=self.cancel_wait_arm,
        )
        self._try_finish_cancel()

    def _try_finish_cancel(self) -> None:
        if self.state != "CANCEL_REQUESTED":
            return
        if self.cancel_wait_base or self.cancel_wait_arm:
            return
        if self.cancel_terminal == "TIMED_OUT":
            self.state = "TIMED_OUT"
            event = "stored_pick_timed_out"
            legacy = "alignment_failed"
        elif self.cancel_terminal == "FAILED":
            self.state = "FAILED"
            event = "stored_pick_failed"
            legacy = "alignment_failed"
        else:
            self.state = "CANCELED"
            event = "stored_pick_cancelled"
            legacy = "alignment_cancelled"
        self.phase = "terminal"
        self._publish_result(
            event,
            False,
            legacy,
            reason=self.cancel_reason,
            error_code=self.cancel_error_code,
            **self.cancel_details,
        )
        self._publish_status(
            event,
            False,
            reason=self.cancel_reason,
            error_code=self.cancel_error_code,
        )

    def _fail(self, error_code: str, *, reason: str, **details: Any) -> None:
        if self.state in TERMINAL_STATES or self.state == "CANCEL_REQUESTED":
            return
        self._request_cancel(
            reason,
            terminal="FAILED",
            error_code=error_code,
            details=details,
        )

    def _succeed(self) -> None:
        self._cancel_finder("stored_pick_complete")
        self._clear_active_target()
        self.state = "SUCCEEDED"
        self.phase = "terminal"
        if self.execute_pick:
            event = "stored_pick_completed"
            legacy = "align_pick_completed"
        else:
            event = "stored_alignment_completed"
            legacy = "alignment_completed"
        self._publish_result(event, True, legacy)
        self._publish_status(event)

    # ------------------------------------------------------------------
    # Timer
    # ------------------------------------------------------------------
    def _timer_callback(self) -> None:
        now = time.monotonic()
        if self.state in TERMINAL_STATES:
            return
        if self.state == "CANCEL_REQUESTED":
            if now >= self.cancel_deadline:
                self.state = "FAILED"
                self.phase = "terminal"
                self._publish_result(
                    "stored_pick_failed",
                    False,
                    "alignment_failed",
                    reason="cancel stop confirmation timeout",
                    error_code="SAFE_STOP_UNCONFIRMED",
                )
                self._publish_status(
                    "safe_stop_unconfirmed",
                    False,
                    waiting_for_base_stop=self.cancel_wait_base,
                    waiting_for_arm_stop=self.cancel_wait_arm,
                )
            return
        if self.goal_deadline > 0.0 and now >= self.goal_deadline:
            self._request_cancel("overall action timeout", terminal="TIMED_OUT")
            return
        if self.pending_odom_purpose:
            if now - self.pending_odom_sent > float(
                self.get_parameter("odom_request_timeout_sec").value
            ):
                self._fail("PICO_COMMUNICATION_ERROR", reason="ODOM? response timeout")
            return
        if self.phase == "record_wait_detection":
            stable = self._stable_detection()
            if stable is not None:
                self.record_point = stable.point_base
                self.record_stable_detection = stable
                self.filter.clear()
                self._request_odom("record")
            return
        if self.arm_active and self.pending_arm_q is not None:
            if now >= self.phase_deadline:
                self._request_cancel("arm stow timeout", terminal="TIMED_OUT")
            return
        if self.base_active:
            if now >= self.phase_deadline:
                self._request_cancel("base motion timeout", terminal="TIMED_OUT")
            return
        if self.phase == "search":
            if now >= self.phase_deadline:
                self._fail("OBJECT_NOT_FOUND", reason="search timeout")
                return
            self._try_search_or_align()
            return
        if self.phase == "align_settle":
            if now >= self.settle_until:
                self.phase = "align"
                self.filter.clear()
            return
        if self.phase == "align":
            self._try_alignment_step()
            return
        if self.phase == "grasp" and now >= self.phase_deadline:
            self._request_cancel("grasp timeout", terminal="TIMED_OUT")

    # ------------------------------------------------------------------
    # Misc helpers
    # ------------------------------------------------------------------
    def _stable_detection(self):
        assert self.profile is not None or self.mode == "record"
        alignment = self.profile.alignment if self.profile is not None else self.default_alignment
        return self.filter.stable(
            now_sec=time.time(),
            object_name=self.object_name,
            minimum_score=alignment.minimum_score,
            minimum_count=alignment.stability_count,
            window_sec=alignment.stability_window_sec,
            radius_m=alignment.stability_radius_m,
            minimum_localization_quality=alignment.minimum_localization_quality,
            maximum_depth_std_m=alignment.maximum_depth_std_m,
            maximum_center_std_px=alignment.maximum_center_std_px,
            required_orientation_class=(
                alignment.reference_orientation_class
                if alignment.require_orientation_match else ""
            ),
            minimum_orientation_quality=alignment.minimum_orientation_quality,
        )

    @staticmethod
    def _error_mapping(errors: Optional[AlignmentErrors]) -> Optional[Dict[str, float]]:
        if errors is None:
            return None
        return {
            "bearing_error_deg": errors.bearing_error_deg,
            "range_error_m": errors.range_error_m,
            "height_error_m": errors.height_error_m,
            "current_forward_m": errors.current.forward_m,
            "current_lateral_m": errors.current.lateral_m,
            "current_range_m": errors.current.range_m,
            "reference_forward_m": errors.reference.forward_m,
            "reference_lateral_m": errors.reference.lateral_m,
            "reference_range_m": errors.reference.range_m,
        }

    def _reset_action_state(self) -> None:
        self.state = "IDLE"
        self.phase = "idle"
        self.request_id = ""
        self.object_name = ""
        self.profile_name = ""
        self.mode = "full"
        self.execute_pick = True
        self.profile = None
        self.filter.clear()
        self.last_object_point = None
        self.last_base_response = {}
        self.goal_started = 0.0
        self.goal_deadline = 0.0
        self.phase_deadline = 0.0
        self.settle_until = 0.0
        self.finder_active = False
        self.pending_odom_purpose = ""
        self.record_point = None
        self.record_stable_detection = None
        self.record_grasp_executor = "keyframes"
        self.record_grasp_trajectory = ""
        self.record_grasp_keyframe_profile = ""
        self.record_require_orientation_match = None
        self.coarse_steps = []
        self.search_relative_turns = []
        self.search_index = 0
        self.base_active = False
        self.base_expected_event = ""
        self.base_command = ""
        self.base_purpose = ""
        self.arm_active = False
        self.pending_arm_q = None
        self.arm_demo_command_id = ""
        self.keyframe_command_id = ""
        self.keyframe_preflight_only = False
        self.pick_waiting = False
        self.alignment_iterations = 0
        self.total_turn_deg = 0.0
        self.total_move_m = 0.0
        self.aligned_confirmations = 0
        self.last_errors = None
        self.steps = {}
        self.cancel_reason = ""
        self.cancel_terminal = "CANCELED"
        self.cancel_error_code = "RUN_CANCELED"
        self.cancel_details = {}
        self.cancel_wait_base = False
        self.cancel_wait_arm = False


def main(args=None) -> None:
    rclpy.init(args=args)
    node = StoredObjectPickNode()
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
