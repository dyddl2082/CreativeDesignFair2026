from __future__ import annotations

import json
import math
from pathlib import Path
import time
from typing import Any, Dict, Optional, Tuple

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point
from sensor_msgs.msg import JointState
from std_msgs.msg import Empty, String
from visualization_msgs.msg import Marker, MarkerArray

from .alignment_core import (
    AlignmentErrors,
    AlignmentProfile,
    AlignmentProfileStore,
    alignment_errors,
    choose_alignment_action,
    pico_move_command_cm,
    pico_turn_command_deg,
)
from .planner import DetectionSample, StablePointFilter
from .profiles import Q, Vector3


TERMINAL_STATES = {"IDLE", "DONE", "FAILED", "CANCELLED"}
ACTIVE_DETECTION_STATES = {"RECORDING", "SEARCHING"}


def _as_bool(value: object, default: bool) -> bool:
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


def _q_close(a: Q, b: Q, tolerance: float = 1e-4) -> bool:
    return max(abs(a[index] - b[index]) for index in range(3)) <= tolerance


def _point_from_payload(value: Any) -> Optional[Vector3]:
    if not isinstance(value, dict):
        return None
    try:
        point = (float(value["x"]), float(value["y"]), float(value["z"]))
    except (KeyError, TypeError, ValueError):
        return None
    if not all(math.isfinite(item) for item in point):
        return None
    return point


class BaseAlignmentNode(Node):
    """Record a graspable camera-relative pose, align the base, then pick.

    The node deliberately uses encoder-bounded Pico commands (``TURN_DEG`` and
    ``MOVE_CM``), not open-loop ``MOTOR`` commands.  Alignment is visual-servoed:
    after every small chassis motion it waits for a fresh stable object point,
    recomputes the error, and only then sends the next motion.

    Project-specific base convention defaults:
      * robot forward is ``-base_link.x``
      * robot left is ``+base_link.y``
      * Pico ``TURN_DEG`` positive is right turn
      * Pico ``MOVE_CM`` positive is forward
    All four conventions are parameters so a calibrated robot can override them.
    """

    def __init__(self) -> None:
        super().__init__("macrobot_base_alignment")

        default_profile_file = (
            Path.home()
            / "MacRobot"
            / "data"
            / "alignment"
            / "base_alignment_profiles.yaml"
        )

        # Public API.
        self.declare_parameter("goal_topic", "/macrobot/align_pick/goal")
        self.declare_parameter("record_topic", "/macrobot/base_alignment/record")
        self.declare_parameter("admin_topic", "/macrobot/base_alignment/admin")
        self.declare_parameter("cancel_topic", "/macrobot/base_alignment/cancel")
        self.declare_parameter("status_topic", "/macrobot/base_alignment/status")
        self.declare_parameter("result_topic", "/macrobot/base_alignment/result")
        self.declare_parameter(
            "command_preview_topic", "/macrobot/base_alignment/command_preview"
        )
        self.declare_parameter("marker_topic", "/macrobot/base_alignment/markers")

        # Perception / finder hand-off.
        self.declare_parameter(
            "localized_detection_topic", "/macrobot/perception/localized_detection"
        )
        self.declare_parameter("finder_goal_topic", "/object_finder/goal")
        self.declare_parameter("finder_cancel_topic", "/object_finder/cancel")
        self.declare_parameter("active_target_topic", "/macrobot/pick/active_target")

        # Base and Pico.
        self.declare_parameter("pico_command_topic", "/pico_debug/cmd")
        self.declare_parameter("pico_response_topic", "/pico_debug/response")
        self.declare_parameter("dry_run_base", False)
        self.declare_parameter("dry_run_motion_sec", 0.60)
        self.declare_parameter("forward_axis_sign", -1.0)
        self.declare_parameter("lateral_axis_sign", 1.0)
        self.declare_parameter("pico_turn_positive_is_right", True)
        self.declare_parameter("pico_move_positive_is_forward", True)

        # Arm stow and validated pick hand-off.
        self.declare_parameter("stow_before_alignment", True)
        self.declare_parameter("stow_q", [0.0, 0.0, 0.0])
        self.declare_parameter("stow_timeout_sec", 20.0)
        self.declare_parameter("joint_goal_topic", "/macrobot/arm/joint_goal")
        self.declare_parameter(
            "logical_state_topic", "/macrobot/arm/logical_joint_states"
        )
        self.declare_parameter(
            "validation_status_topic", "/macrobot/arm/validation_status"
        )
        self.declare_parameter(
            "bridge_status_topic", "/macrobot/arm/servo_bridge/status"
        )
        self.declare_parameter("arm_stop_topic", "/macrobot/arm/stop")
        self.declare_parameter("pick_goal_topic", "/macrobot/pick/goal")
        self.declare_parameter("pick_cancel_topic", "/macrobot/pick/cancel")
        self.declare_parameter("pick_result_topic", "/macrobot/pick/result")
        self.declare_parameter("pick_timeout_sec", 120.0)

        # Storage and default profile values used when a new pose is recorded.
        self.declare_parameter("profile_file", str(default_profile_file))
        self.declare_parameter("base_frame", "base_link")
        self.declare_parameter("default_minimum_score", 0.55)
        self.declare_parameter("default_stability_count", 5)
        self.declare_parameter("default_stability_window_sec", 1.5)
        self.declare_parameter("default_stability_radius_m", 0.012)
        self.declare_parameter("default_bearing_tolerance_deg", 2.0)
        self.declare_parameter("default_range_tolerance_m", 0.015)
        self.declare_parameter("default_height_tolerance_m", 0.030)
        self.declare_parameter("default_max_turn_step_deg", 8.0)
        self.declare_parameter("default_max_move_step_m", 0.040)
        self.declare_parameter("default_turn_speed", 70)
        self.declare_parameter("default_move_speed", 80)
        self.declare_parameter("default_motion_timeout_sec", 8.0)
        self.declare_parameter("default_settle_sec", 0.45)
        self.declare_parameter("default_max_iterations", 20)
        self.declare_parameter("default_max_total_turn_deg", 90.0)
        self.declare_parameter("default_max_total_move_m", 0.50)
        self.declare_parameter("default_search_timeout_sec", 60.0)
        self.declare_parameter("record_timeout_sec", 20.0)
        self.declare_parameter("alignment_confirmation_count", 2)
        self.declare_parameter("timer_rate_hz", 20.0)

        self.base_frame = str(self.get_parameter("base_frame").value)
        self.profile_store = AlignmentProfileStore(
            str(self.get_parameter("profile_file").value)
        )
        self.forward_axis_sign = float(
            self.get_parameter("forward_axis_sign").value
        )
        self.lateral_axis_sign = float(
            self.get_parameter("lateral_axis_sign").value
        )
        self.pico_turn_positive_is_right = bool(
            self.get_parameter("pico_turn_positive_is_right").value
        )
        self.pico_move_positive_is_forward = bool(
            self.get_parameter("pico_move_positive_is_forward").value
        )
        self.dry_run_base = bool(self.get_parameter("dry_run_base").value)
        self.dry_run_motion_sec = max(
            0.0, float(self.get_parameter("dry_run_motion_sec").value)
        )
        self.stow_before_alignment = bool(
            self.get_parameter("stow_before_alignment").value
        )
        stow_values = list(self.get_parameter("stow_q").value)
        if len(stow_values) != 3:
            raise ValueError("stow_q must have three values")
        self.stow_q: Q = tuple(float(item) for item in stow_values)  # type: ignore[assignment]
        self.stow_timeout = float(self.get_parameter("stow_timeout_sec").value)
        self.pick_timeout = float(self.get_parameter("pick_timeout_sec").value)
        self.default_search_timeout = float(
            self.get_parameter("default_search_timeout_sec").value
        )
        self.record_timeout = float(self.get_parameter("record_timeout_sec").value)
        self.alignment_confirmation_count = max(
            1, int(self.get_parameter("alignment_confirmation_count").value)
        )

        # Publishers.
        self.status_pub = self.create_publisher(
            String, str(self.get_parameter("status_topic").value), 20
        )
        self.result_pub = self.create_publisher(
            String, str(self.get_parameter("result_topic").value), 10
        )
        self.preview_pub = self.create_publisher(
            String, str(self.get_parameter("command_preview_topic").value), 20
        )
        self.marker_pub = self.create_publisher(
            MarkerArray, str(self.get_parameter("marker_topic").value), 10
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
        self.pick_goal_pub = self.create_publisher(
            String, str(self.get_parameter("pick_goal_topic").value), 10
        )
        self.pick_cancel_pub = self.create_publisher(
            String, str(self.get_parameter("pick_cancel_topic").value), 10
        )

        # Subscriptions.
        self.create_subscription(
            String,
            str(self.get_parameter("goal_topic").value),
            self._goal_callback,
            10,
        )
        self.create_subscription(
            String,
            str(self.get_parameter("record_topic").value),
            self._record_callback,
            10,
        )
        self.create_subscription(
            String,
            str(self.get_parameter("admin_topic").value),
            self._admin_callback,
            10,
        )
        self.create_subscription(
            String,
            str(self.get_parameter("cancel_topic").value),
            self._cancel_callback,
            10,
        )
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
            str(self.get_parameter("pick_result_topic").value),
            self._pick_result_callback,
            20,
        )

        # Runtime state.
        self.state = "IDLE"
        self.request_id = ""
        self.object_name = ""
        self.alignment_profile_name = ""
        self.pick_profile_name = ""
        self.execute_pick = True
        self.profile: Optional[AlignmentProfile] = None
        self.filter = StablePointFilter()
        self.current_q: Q = (0.0, 0.0, 0.0)
        self.pending_arm_q: Optional[Q] = None
        self.pending_started = 0.0
        self.search_deadline = 0.0
        self.record_deadline = 0.0
        self.pick_deadline = 0.0
        self.motion_command = ""
        self.motion_event = ""
        self.motion_started = 0.0
        self.settle_until = 0.0
        self.iteration_count = 0
        self.total_turn_deg = 0.0
        self.total_move_m = 0.0
        self.aligned_confirmations = 0
        self.last_errors: Optional[AlignmentErrors] = None
        self.last_stable_point: Optional[Vector3] = None
        self.record_pick_profile = ""
        self.finder_active = False
        self.requested_search_timeout = self.default_search_timeout

        rate = max(2.0, float(self.get_parameter("timer_rate_hz").value))
        self.create_timer(1.0 / rate, self._timer_callback)
        self.get_logger().info(
            "Base alignment ready: recorded camera pose -> TURN_DEG/MOVE_CM -> validated pick"
        )

    # ------------------------------------------------------------------
    # Utility and public status
    # ------------------------------------------------------------------
    def _publish_json(self, publisher, payload: Dict[str, object]) -> None:
        message = String()
        message.data = json.dumps(payload, ensure_ascii=False)
        publisher.publish(message)

    def _status(self, event: str, ok: bool = True, **details: object) -> None:
        payload: Dict[str, object] = {
            "ok": ok,
            "event": event,
            "state": self.state,
            "request_id": self.request_id,
            "object_name": self.object_name,
            "alignment_profile": self.alignment_profile_name,
            **details,
        }
        self._publish_json(self.status_pub, payload)
        if ok:
            self.get_logger().info(json.dumps(payload, ensure_ascii=False))
        else:
            self.get_logger().warning(json.dumps(payload, ensure_ascii=False))

    def _publish_result(self, event: str, ok: bool, **details: object) -> None:
        self._publish_json(
            self.result_pub,
            {
                "ok": ok,
                "event": event,
                "request_id": self.request_id,
                "object_name": self.object_name,
                "alignment_profile": self.alignment_profile_name,
                **details,
            },
        )

    def _publish_alignment_markers(
        self,
        current: Optional[Vector3],
        reference: Optional[Vector3],
        *,
        clear_only: bool = False,
    ) -> None:
        array = MarkerArray()
        clear = Marker()
        clear.action = Marker.DELETEALL
        array.markers.append(clear)
        if clear_only or current is None or reference is None:
            self.marker_pub.publish(array)
            return

        now = self.get_clock().now().to_msg()
        for marker_id, label, point, color in (
            (0, "current object", current, (1.0, 0.15, 0.15, 0.95)),
            (1, "recorded target", reference, (0.1, 1.0, 0.2, 0.95)),
        ):
            sphere = Marker()
            sphere.header.frame_id = self.base_frame
            sphere.header.stamp = now
            sphere.ns = "macrobot_base_alignment_points"
            sphere.id = marker_id
            sphere.type = Marker.SPHERE
            sphere.action = Marker.ADD
            sphere.pose.orientation.w = 1.0
            sphere.pose.position.x, sphere.pose.position.y, sphere.pose.position.z = point
            sphere.scale.x = sphere.scale.y = sphere.scale.z = 0.022
            sphere.color.r, sphere.color.g, sphere.color.b, sphere.color.a = color
            array.markers.append(sphere)

            text = Marker()
            text.header.frame_id = self.base_frame
            text.header.stamp = now
            text.ns = "macrobot_base_alignment_labels"
            text.id = marker_id + 100
            text.type = Marker.TEXT_VIEW_FACING
            text.action = Marker.ADD
            text.pose.orientation.w = 1.0
            text.pose.position.x = point[0]
            text.pose.position.y = point[1]
            text.pose.position.z = point[2] + 0.03
            text.scale.z = 0.018
            text.color.r = text.color.g = text.color.b = text.color.a = 1.0
            text.text = label
            array.markers.append(text)

        line = Marker()
        line.header.frame_id = self.base_frame
        line.header.stamp = now
        line.ns = "macrobot_base_alignment_error"
        line.id = 200
        line.type = Marker.ARROW
        line.action = Marker.ADD
        line.scale.x = 0.005
        line.scale.y = 0.010
        line.scale.z = 0.010
        line.color.r = 1.0
        line.color.g = 0.85
        line.color.b = 0.1
        line.color.a = 0.95
        start = Point()
        start.x, start.y, start.z = current
        end = Point()
        end.x, end.y, end.z = reference
        line.points = [start, end]
        array.markers.append(line)
        self.marker_pub.publish(array)

    def _default_profile(
        self,
        name: str,
        object_name: str,
        pick_profile: str,
        point: Vector3 = (-0.20, 0.06, 0.10),
    ) -> AlignmentProfile:
        profile = AlignmentProfile(
            name=name,
            object_name=object_name,
            pick_profile=pick_profile,
            reference_point_base=point,
            recorded_at="",
            frame_id=self.base_frame,
            minimum_score=float(self.get_parameter("default_minimum_score").value),
            stability_count=int(self.get_parameter("default_stability_count").value),
            stability_window_sec=float(
                self.get_parameter("default_stability_window_sec").value
            ),
            stability_radius_m=float(
                self.get_parameter("default_stability_radius_m").value
            ),
            bearing_tolerance_deg=float(
                self.get_parameter("default_bearing_tolerance_deg").value
            ),
            range_tolerance_m=float(
                self.get_parameter("default_range_tolerance_m").value
            ),
            height_tolerance_m=float(
                self.get_parameter("default_height_tolerance_m").value
            ),
            max_turn_step_deg=float(
                self.get_parameter("default_max_turn_step_deg").value
            ),
            max_move_step_m=float(
                self.get_parameter("default_max_move_step_m").value
            ),
            turn_speed=int(self.get_parameter("default_turn_speed").value),
            move_speed=int(self.get_parameter("default_move_speed").value),
            motion_timeout_sec=float(
                self.get_parameter("default_motion_timeout_sec").value
            ),
            settle_sec=float(self.get_parameter("default_settle_sec").value),
            max_iterations=int(
                self.get_parameter("default_max_iterations").value
            ),
            max_total_turn_deg=float(
                self.get_parameter("default_max_total_turn_deg").value
            ),
            max_total_move_m=float(
                self.get_parameter("default_max_total_move_m").value
            ),
        )
        profile.validate()
        return profile

    @staticmethod
    def _parse_text_or_json(text: str) -> Dict[str, object]:
        text = text.strip()
        if not text:
            raise ValueError("empty command")
        if text.startswith("{"):
            data = json.loads(text)
            if not isinstance(data, dict):
                raise ValueError("command JSON must be an object")
            return data
        return {"object_name": text}

    def _set_active_target(self, object_name: str) -> None:
        message = String()
        message.data = object_name
        self.active_target_pub.publish(message)

    def _clear_active_target(self) -> None:
        self._set_active_target("")

    def _start_finder(self, object_name: str, timeout_sec: float) -> None:
        self._set_active_target(object_name)
        self.finder_active = True
        self._publish_json(
            self.finder_goal_pub,
            {
                "object_name": object_name,
                "timeout_sec": timeout_sec,
                "continuous": True,
                "request_id": self.request_id,
            },
        )

    def _cancel_finder(self, reason: str) -> None:
        self.finder_active = False
        message = String()
        message.data = reason
        self.finder_cancel_pub.publish(message)

    # ------------------------------------------------------------------
    # Record / admin API
    # ------------------------------------------------------------------
    def _record_callback(self, msg: String) -> None:
        if self.state not in TERMINAL_STATES:
            self._status("alignment_busy", False)
            return
        try:
            request = self._parse_text_or_json(msg.data)
            object_name = str(request.get("object_name", "")).strip()
            if not object_name:
                raise ValueError("object_name is required")
            name = str(
                request.get("alignment_profile", request.get("profile", object_name))
            ).strip()
            pick_profile = str(request.get("pick_profile", object_name)).strip()
        except Exception as exc:
            self._status("invalid_record_request", False, error=str(exc))
            return

        self._publish_alignment_markers(None, None, clear_only=True)
        self.request_id = f"align-record-{int(time.time() * 1000)}"
        self.finder_active = False
        self.object_name = object_name
        self.alignment_profile_name = name
        self.record_pick_profile = pick_profile
        try:
            self.profile = self.profile_store.get(name, object_name)
        except KeyError:
            self.profile = self._default_profile(name, object_name, pick_profile)
        self.filter.clear()
        self.last_stable_point = None
        self.record_deadline = time.monotonic() + self.record_timeout
        self.state = "RECORDING"
        self._start_finder(object_name, self.record_timeout)
        self._status(
            "alignment_record_started",
            pick_profile=pick_profile,
            profile_file=str(self.profile_store.path),
        )

    def _admin_callback(self, msg: String) -> None:
        try:
            data = self._parse_text_or_json(msg.data)
            action = str(data.get("action", msg.data)).strip().casefold()
        except Exception as exc:
            self._status("invalid_admin_request", False, error=str(exc))
            return
        if action in {"list", "profiles", "status"}:
            self._status(
                "alignment_profiles",
                profiles=self.profile_store.mappings(),
                profile_file=str(self.profile_store.path),
            )
            return
        if action == "reload":
            try:
                self.profile_store.reload()
                self._status("alignment_profiles_reloaded", names=list(self.profile_store.names()))
            except Exception as exc:
                self._status("alignment_profiles_reload_failed", False, error=str(exc))
            return
        if action == "delete":
            name = str(data.get("profile", data.get("name", ""))).strip()
            if not name:
                self._status("alignment_profile_delete_failed", False, error="profile is required")
                return
            deleted = self.profile_store.delete(name)
            self._status(
                "alignment_profile_deleted" if deleted else "alignment_profile_not_found",
                deleted,
                profile=name,
            )
            return
        self._status("unsupported_admin_action", False, action=action)

    # ------------------------------------------------------------------
    # Align-and-pick goal
    # ------------------------------------------------------------------
    def _goal_callback(self, msg: String) -> None:
        if self.state not in TERMINAL_STATES:
            self._cancel("replaced_by_new_alignment_goal")
        try:
            request = self._parse_text_or_json(msg.data)
            object_name = str(request.get("object_name", "")).strip()
            if not object_name:
                raise ValueError("object_name is required")
            shared_profile = str(request.get("profile", "")).strip()
            alignment_profile = str(
                request.get("alignment_profile", shared_profile or object_name)
            ).strip()
            pick_profile = str(
                request.get("pick_profile", shared_profile or object_name)
            ).strip()
            execute_pick = _as_bool(request.get("execute_pick"), True)
            search_timeout = float(
                request.get("search_timeout_sec", self.default_search_timeout)
            )
            profile = self.profile_store.get(alignment_profile, object_name)
        except Exception as exc:
            self._status("invalid_alignment_goal", False, error=str(exc))
            return

        self._publish_alignment_markers(None, None, clear_only=True)
        self.request_id = f"align-pick-{int(time.time() * 1000)}"
        self.finder_active = False
        self.object_name = object_name
        self.alignment_profile_name = alignment_profile
        self.pick_profile_name = pick_profile or profile.pick_profile or object_name
        self.execute_pick = execute_pick
        self.profile = profile
        self.filter.clear()
        self.last_stable_point = None
        self.last_errors = None
        self.iteration_count = 0
        self.total_turn_deg = 0.0
        self.total_move_m = 0.0
        self.aligned_confirmations = 0
        self.requested_search_timeout = search_timeout
        self.search_deadline = 0.0
        self.pending_arm_q = None

        if self.stow_before_alignment and not _q_close(self.current_q, self.stow_q, 0.01):
            self._command_stow()
        else:
            self._begin_alignment_search()

        self._status(
            "alignment_started",
            execute_pick=self.execute_pick,
            pick_profile=self.pick_profile_name,
            reference_point_base=list(profile.reference_point_base),
            dry_run_base=self.dry_run_base,
        )

    def _command_stow(self) -> None:
        self.pending_arm_q = self.stow_q
        self.pending_started = time.monotonic()
        self.state = "WAITING_STOW"
        goal = JointState()
        goal.header.stamp = self.get_clock().now().to_msg()
        goal.name = ["arm_lift_joint", "wrist_pitch_joint", "gripper_joint"]
        goal.position = list(self.stow_q)
        self.joint_goal_pub.publish(goal)
        self._status("alignment_stow_commanded", q=list(self.stow_q))

    def _begin_alignment_search(self) -> None:
        self.state = "SEARCHING"
        self.filter.clear()
        if self.search_deadline <= 0.0:
            self.search_deadline = time.monotonic() + self.requested_search_timeout
        if not self.finder_active:
            self._start_finder(
                self.object_name,
                max(1.0, self.search_deadline - time.monotonic()),
            )
        self._status("alignment_waiting_for_stable_object")

    # ------------------------------------------------------------------
    # Input callbacks
    # ------------------------------------------------------------------
    def _detection_callback(self, msg: String) -> None:
        if self.state not in ACTIVE_DETECTION_STATES:
            return
        try:
            payload = json.loads(msg.data)
        except Exception:
            return
        if not isinstance(payload, dict) or payload.get("event") != "localized_object":
            return
        object_name = str(payload.get("object_name", "")).strip()
        if object_name.casefold() != self.object_name.casefold():
            return
        point = _point_from_payload(payload.get("point_base"))
        if point is None:
            return
        score = float(payload.get("score", 0.0))
        stamp = float(payload.get("stamp_sec", time.time()))
        if not all(math.isfinite(value) for value in (*point, score, stamp)):
            return
        self.filter.add(
            DetectionSample(
                stamp_sec=stamp,
                object_name=object_name,
                score=score,
                point_base=point,
                source=str(payload.get("source", "")),
            )
        )

    def _logical_state_callback(self, msg: JointState) -> None:
        values = dict(zip(msg.name, msg.position))
        names = ("arm_lift_joint", "wrist_pitch_joint", "gripper_joint")
        if all(name in values for name in names):
            q = tuple(float(values[name]) for name in names)
            if all(math.isfinite(value) for value in q):
                self.current_q = q  # type: ignore[assignment]

    def _validation_callback(self, msg: String) -> None:
        if self.state != "WAITING_STOW" or self.pending_arm_q is None:
            return
        try:
            payload = json.loads(msg.data)
        except Exception:
            return
        if not isinstance(payload, dict):
            return
        event = str(payload.get("event", ""))
        if event == "goal_rejected":
            self._fail("alignment_stow_rejected", validator=payload)

    def _bridge_callback(self, msg: String) -> None:
        if self.state != "WAITING_STOW" or self.pending_arm_q is None:
            return
        try:
            payload = json.loads(msg.data)
        except Exception:
            return
        if not isinstance(payload, dict):
            return
        event = str(payload.get("event", ""))
        if event in {
            "runtime_interpolation_rejected",
            "defense_in_depth_rejection",
            "pico_error",
            "invalid_validated_goal",
        }:
            self._fail("alignment_stow_failed", bridge=payload)
            return
        if event != "trajectory_completed":
            return
        goal = payload.get("goal")
        if isinstance(goal, list) and len(goal) == 3:
            q = tuple(float(value) for value in goal)
            if not _q_close(q, self.pending_arm_q):
                return
        self.current_q = self.pending_arm_q
        self.pending_arm_q = None
        self._begin_alignment_search()

    def _pico_response_callback(self, msg: String) -> None:
        if self.state != "WAITING_BASE_MOTION" or self.dry_run_base:
            return
        try:
            payload = json.loads(msg.data)
        except Exception:
            return
        if not isinstance(payload, dict):
            return
        event = str(payload.get("event", ""))
        if event != self.motion_event:
            if payload.get("ok") is False and event in {
                "command_error",
                "main_loop_error",
                "estop_latched",
                "busy",
            }:
                self._fail("base_motion_error", pico_response=payload)
            return
        status = str(payload.get("status", ""))
        if payload.get("ok") is True and status == "done":
            self._complete_base_motion(payload)
            return
        self._fail("base_motion_failed", pico_response=payload)

    def _pick_result_callback(self, msg: String) -> None:
        if self.state != "WAITING_PICK":
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
        if payload.get("ok") is True and event in {"pick_completed", "localized_only"}:
            self.state = "DONE"
            self._publish_result(
                "align_pick_completed",
                True,
                alignment_errors=self._error_mapping(self.last_errors),
                pick_result=payload,
                iterations=self.iteration_count,
                total_turn_deg=self.total_turn_deg,
                total_move_m=self.total_move_m,
            )
            self._status("align_pick_completed", pick_result=payload)
            self._clear_active_target()
        elif payload.get("ok") is False or event == "pick_failed":
            self._fail("pick_after_alignment_failed", pick_result=payload)

    def _cancel_callback(self, msg: String) -> None:
        self._cancel(msg.data.strip() or "user_cancel")

    # ------------------------------------------------------------------
    # Timer and alignment control
    # ------------------------------------------------------------------
    def _timer_callback(self) -> None:
        now = time.monotonic()
        if self.state == "RECORDING":
            if now > self.record_deadline:
                self._fail("alignment_record_timeout")
                return
            self._try_record_stable_point()
            return
        if self.state == "WAITING_STOW":
            if now - self.pending_started > self.stow_timeout:
                self._fail("alignment_stow_timeout")
            return
        if self.state == "SEARCHING":
            if now > self.search_deadline:
                self._fail("alignment_search_timeout")
                return
            self._try_alignment_step()
            return
        if self.state == "WAITING_BASE_MOTION":
            if self.dry_run_base and now - self.motion_started >= self.dry_run_motion_sec:
                self._complete_base_motion({"dry_run": True})
                return
            assert self.profile is not None
            if now - self.motion_started > self.profile.motion_timeout_sec + 1.0:
                self._fail("base_motion_response_timeout", command=self.motion_command)
            return
        if self.state == "SETTLING" and now >= self.settle_until:
            self._begin_alignment_search()
            return
        if self.state == "WAITING_PICK" and now > self.pick_deadline:
            self._fail("pick_after_alignment_timeout")

    def _stable_detection(self):
        assert self.profile is not None
        return self.filter.stable(
            now_sec=time.time(),
            object_name=self.object_name,
            minimum_score=self.profile.minimum_score,
            minimum_count=self.profile.stability_count,
            window_sec=self.profile.stability_window_sec,
            radius_m=self.profile.stability_radius_m,
        )

    def _try_record_stable_point(self) -> None:
        stable = self._stable_detection()
        if stable is None or self.profile is None:
            return
        try:
            record_errors = alignment_errors(
                stable.point_base,
                stable.point_base,
                forward_axis_sign=self.forward_axis_sign,
                lateral_axis_sign=self.lateral_axis_sign,
            )
            record_decision = choose_alignment_action(record_errors, self.profile)
        except Exception as exc:
            self._fail("alignment_record_geometry_error", error=str(exc))
            return
        if record_decision.action == "reject":
            self._fail(record_decision.reason)
            return
        recorded = self.profile.with_reference(
            stable.point_base,
            object_name=self.object_name,
            pick_profile=self.record_pick_profile,
        )
        self.profile_store.upsert(recorded)
        self.profile = recorded
        self.last_stable_point = stable.point_base
        self._cancel_finder("alignment_profile_recorded")
        self._clear_active_target()
        self.state = "DONE"
        self._publish_result(
            "alignment_profile_recorded",
            True,
            profile=recorded.to_mapping(),
            profile_file=str(self.profile_store.path),
            sample_count=stable.sample_count,
            stability_radius_m=stable.radius_m,
        )
        self._status(
            "alignment_profile_recorded",
            profile=recorded.to_mapping(),
            profile_file=str(self.profile_store.path),
        )

    def _try_alignment_step(self) -> None:
        stable = self._stable_detection()
        if stable is None or self.profile is None:
            return
        self.last_stable_point = stable.point_base
        try:
            errors = alignment_errors(
                stable.point_base,
                self.profile.reference_point_base,
                forward_axis_sign=self.forward_axis_sign,
                lateral_axis_sign=self.lateral_axis_sign,
            )
            decision = choose_alignment_action(errors, self.profile)
        except Exception as exc:
            self._fail("alignment_geometry_error", error=str(exc))
            return
        self.last_errors = errors
        self._publish_alignment_markers(
            stable.point_base, self.profile.reference_point_base
        )
        self._status(
            "alignment_observation",
            current_point_base=list(stable.point_base),
            reference_point_base=list(self.profile.reference_point_base),
            errors=self._error_mapping(errors),
            decision={"action": decision.action, "amount": decision.amount, "reason": decision.reason},
            sample_count=stable.sample_count,
            stability_radius_m=stable.radius_m,
        )

        if decision.action == "reject":
            self._fail(decision.reason, errors=self._error_mapping(errors))
            return
        if decision.action == "aligned":
            self.aligned_confirmations += 1
            if self.aligned_confirmations < self.alignment_confirmation_count:
                self.filter.clear()
                self._status(
                    "alignment_confirmation_pending",
                    confirmations=self.aligned_confirmations,
                    required=self.alignment_confirmation_count,
                )
                return
            self._alignment_complete()
            return

        self.aligned_confirmations = 0
        self.iteration_count += 1
        if self.iteration_count > self.profile.max_iterations:
            self._fail("alignment_iteration_limit")
            return
        if decision.action == "turn":
            self._command_turn(decision.amount)
        elif decision.action == "move":
            self._command_move(decision.amount)

    def _command_turn(self, physical_left_positive_deg: float) -> None:
        assert self.profile is not None
        if self.total_turn_deg + abs(physical_left_positive_deg) > self.profile.max_total_turn_deg:
            self._fail("alignment_total_turn_limit")
            return
        pico_deg = pico_turn_command_deg(
            physical_left_positive_deg,
            pico_positive_is_right=self.pico_turn_positive_is_right,
        )
        command = (
            f"TURN_DEG {pico_deg:.3f} {self.profile.turn_speed} "
            f"{self.profile.motion_timeout_sec:.2f}"
        )
        self.total_turn_deg += abs(physical_left_positive_deg)
        self._send_base_command(command, "turn_deg_result", "turn", physical_left_positive_deg)

    def _command_move(self, physical_forward_positive_m: float) -> None:
        assert self.profile is not None
        if self.total_move_m + abs(physical_forward_positive_m) > self.profile.max_total_move_m:
            self._fail("alignment_total_move_limit")
            return
        pico_cm = pico_move_command_cm(
            physical_forward_positive_m,
            pico_positive_is_forward=self.pico_move_positive_is_forward,
        )
        command = (
            f"MOVE_CM {pico_cm:.3f} {self.profile.move_speed} "
            f"{self.profile.motion_timeout_sec:.2f}"
        )
        self.total_move_m += abs(physical_forward_positive_m)
        self._send_base_command(command, "move_cm_result", "move", physical_forward_positive_m)

    def _send_base_command(
        self,
        command: str,
        expected_event: str,
        action: str,
        physical_amount: float,
    ) -> None:
        self.motion_command = command
        self.motion_event = expected_event
        self.motion_started = time.monotonic()
        self.state = "WAITING_BASE_MOTION"
        self.filter.clear()

        preview = String()
        preview.data = command
        self.preview_pub.publish(preview)
        if not self.dry_run_base:
            outgoing = String()
            outgoing.data = command
            self.pico_command_pub.publish(outgoing)
        self._status(
            "base_motion_commanded",
            action=action,
            physical_amount=physical_amount,
            pico_command=command,
            dry_run=self.dry_run_base,
            iteration=self.iteration_count,
        )

    def _complete_base_motion(self, response: Dict[str, object]) -> None:
        assert self.profile is not None
        command = self.motion_command
        self.motion_command = ""
        self.motion_event = ""
        self.state = "SETTLING"
        self.settle_until = time.monotonic() + self.profile.settle_sec
        self.filter.clear()
        self._status(
            "base_motion_completed",
            command=command,
            response=response,
            settle_sec=self.profile.settle_sec,
        )

    def _alignment_complete(self) -> None:
        assert self.profile is not None
        self._cancel_finder("alignment_complete")
        self._clear_active_target()
        details = {
            "reference_point_base": list(self.profile.reference_point_base),
            "current_point_base": list(self.last_stable_point) if self.last_stable_point else None,
            "errors": self._error_mapping(self.last_errors),
            "iterations": self.iteration_count,
            "total_turn_deg": self.total_turn_deg,
            "total_move_m": self.total_move_m,
        }
        self._publish_result("alignment_completed", True, **details)
        self._status("alignment_completed", **details)
        if not self.execute_pick:
            self.state = "DONE"
            return

        self.state = "WAITING_PICK"
        self.pick_deadline = time.monotonic() + self.pick_timeout
        goal = String()
        goal.data = json.dumps(
            {
                "object_name": self.object_name,
                "profile": self.pick_profile_name,
                "execute": True,
            },
            ensure_ascii=False,
        )
        self.pick_goal_pub.publish(goal)
        self._status(
            "pick_handoff_started",
            pick_profile=self.pick_profile_name,
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

    # ------------------------------------------------------------------
    # Cancel / failure
    # ------------------------------------------------------------------
    def _cancel(self, reason: str) -> None:
        if self.state in TERMINAL_STATES and self.state != "DONE":
            return
        stop = String()
        stop.data = "STOP"
        self.pico_command_pub.publish(stop)
        self.arm_stop_pub.publish(Empty())
        finder_cancel = String()
        finder_cancel.data = reason
        self.finder_cancel_pub.publish(finder_cancel)
        pick_cancel = String()
        pick_cancel.data = reason
        self.pick_cancel_pub.publish(pick_cancel)
        self._clear_active_target()
        self._publish_alignment_markers(None, None, clear_only=True)
        self.state = "CANCELLED"
        self._publish_result("alignment_cancelled", False, reason=reason)
        self._status("alignment_cancelled", False, reason=reason)

    def _fail(self, reason: str, **details: object) -> None:
        stop = String()
        stop.data = "STOP"
        self.pico_command_pub.publish(stop)
        self.arm_stop_pub.publish(Empty())
        self._cancel_finder(reason)
        if self.state == "WAITING_PICK":
            pick_cancel = String()
            pick_cancel.data = reason
            self.pick_cancel_pub.publish(pick_cancel)
        self._clear_active_target()
        self._publish_alignment_markers(None, None, clear_only=True)
        self.state = "FAILED"
        self._publish_result("alignment_failed", False, reason=reason, **details)
        self._status("alignment_failed", False, reason=reason, **details)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = BaseAlignmentNode()
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
