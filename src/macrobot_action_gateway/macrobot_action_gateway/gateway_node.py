from __future__ import annotations

import json
import math
from pathlib import Path
import threading
import time
import uuid
from typing import Any, Callable

import rclpy
from ament_index_python.packages import get_package_share_directory
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Empty, String
import yaml

from .api_types import ObjectId
from .bridge import BridgeOutcome
from .event_stream import EventStream
from .gateway_protocol import GatewayServerThread, GatewayUnixServer
from .gateway_runtime import GatewayRuntime


JOINT_NAMES = ("arm_lift_joint", "wrist_pitch_joint", "gripper_joint")


def _json_object(text: str) -> dict[str, Any] | None:
    try:
        value = json.loads(text)
    except Exception:
        return None
    return value if isinstance(value, dict) else None


def _q_close(values: Any, target: tuple[float, float, float], tolerance: float = 1e-4) -> bool:
    if not isinstance(values, list) or len(values) != 3:
        return False
    try:
        converted = tuple(float(item) for item in values)
    except (TypeError, ValueError):
        return False
    return max(abs(converted[index] - target[index]) for index in range(3)) <= tolerance


class MacRobotActionGatewayNode(Node):
    def __init__(self) -> None:
        super().__init__("macrobot_action_gateway")
        share = Path(get_package_share_directory("macrobot_action_gateway"))
        self.declare_parameter("settings_file", str(share / "config" / "gateway.yaml"))
        self.declare_parameter("object_catalog_file", str(share / "config" / "object_catalog.yaml"))
        self.declare_parameter("socket_path", "/tmp/macrobot_action_gateway.sock")
        self.declare_parameter("real_motion_enabled", False)
        self.declare_parameter("pico_turn_positive_is_right", True)
        self.declare_parameter("pico_move_positive_is_forward", True)

        self.declare_parameter("pico_command_topic", "/pico_debug/cmd")
        self.declare_parameter("pico_response_topic", "/pico_debug/response")
        self.declare_parameter("joint_goal_topic", "/macrobot/arm/joint_goal")
        self.declare_parameter("logical_state_topic", "/macrobot/arm/logical_joint_states")
        self.declare_parameter("validation_status_topic", "/macrobot/arm/validation_status")
        self.declare_parameter("bridge_status_topic", "/macrobot/arm/servo_bridge/status")
        self.declare_parameter("arm_stop_topic", "/macrobot/arm/stop")
        self.declare_parameter("align_pick_goal_topic", "/macrobot/align_pick/goal")
        self.declare_parameter("alignment_cancel_topic", "/macrobot/base_alignment/cancel")
        self.declare_parameter("alignment_status_topic", "/macrobot/base_alignment/status")
        self.declare_parameter("alignment_result_topic", "/macrobot/base_alignment/result")
        self.declare_parameter("finder_result_topic", "/object_finder/result")
        self.declare_parameter("finder_status_topic", "/object_finder/status")
        self.declare_parameter("stored_task_goal_topic", "/macrobot/stored_pick/goal")
        self.declare_parameter("stored_task_cancel_topic", "/macrobot/stored_pick/cancel")
        self.declare_parameter("stored_task_result_topic", "/macrobot/stored_pick/result")
        self.declare_parameter("stored_task_status_topic", "/macrobot/stored_pick/status")

        settings_path = Path(str(self.get_parameter("settings_file").value)).expanduser()
        catalog_path = Path(str(self.get_parameter("object_catalog_file").value)).expanduser()
        settings = yaml.safe_load(settings_path.read_text(encoding="utf-8")) or {}
        catalog_data = yaml.safe_load(catalog_path.read_text(encoding="utf-8")) or {}
        if not isinstance(settings, dict):
            raise ValueError("gateway settings must be a mapping")
        object_catalog = catalog_data.get("objects", catalog_data)
        if not isinstance(object_catalog, dict):
            raise ValueError("object catalog must be a mapping")
        settings["real_motion_enabled"] = bool(
            self.get_parameter("real_motion_enabled").value
        )
        self.settings = settings
        self.object_catalog = object_catalog
        self.real_motion_enabled = bool(settings["real_motion_enabled"])
        self.pico_turn_positive_is_right = bool(
            self.get_parameter("pico_turn_positive_is_right").value
        )
        self.pico_move_positive_is_forward = bool(
            self.get_parameter("pico_move_positive_is_forward").value
        )

        self.pico_stream = EventStream()
        self.validation_stream = EventStream()
        self.arm_bridge_stream = EventStream()
        self.alignment_status_stream = EventStream()
        self.alignment_result_stream = EventStream()
        self.finder_result_stream = EventStream()
        self.finder_status_stream = EventStream()
        self.stored_task_result_stream = EventStream()
        self.stored_task_status_stream = EventStream()
        self._active_place_request_id = ""

        self.pico_command_pub = self.create_publisher(
            String, str(self.get_parameter("pico_command_topic").value), 20
        )
        self.joint_goal_pub = self.create_publisher(
            JointState, str(self.get_parameter("joint_goal_topic").value), 10
        )
        self.arm_stop_pub = self.create_publisher(
            Empty, str(self.get_parameter("arm_stop_topic").value), 10
        )
        self.align_pick_goal_pub = self.create_publisher(
            String, str(self.get_parameter("align_pick_goal_topic").value), 10
        )
        self.alignment_cancel_pub = self.create_publisher(
            String, str(self.get_parameter("alignment_cancel_topic").value), 10
        )
        self.stored_task_goal_pub = self.create_publisher(
            String, str(self.get_parameter("stored_task_goal_topic").value), 10
        )
        self.stored_task_cancel_pub = self.create_publisher(
            String, str(self.get_parameter("stored_task_cancel_topic").value), 10
        )

        self.create_subscription(
            String,
            str(self.get_parameter("pico_response_topic").value),
            self._pico_callback,
            100,
        )
        self.create_subscription(
            String,
            str(self.get_parameter("validation_status_topic").value),
            self._validation_callback,
            100,
        )
        self.create_subscription(
            String,
            str(self.get_parameter("bridge_status_topic").value),
            self._arm_bridge_callback,
            100,
        )
        self.create_subscription(
            JointState,
            str(self.get_parameter("logical_state_topic").value),
            self._logical_state_callback,
            100,
        )
        self.create_subscription(
            String,
            str(self.get_parameter("alignment_status_topic").value),
            self._alignment_status_callback,
            100,
        )
        self.create_subscription(
            String,
            str(self.get_parameter("alignment_result_topic").value),
            self._alignment_result_callback,
            50,
        )
        self.create_subscription(
            String,
            str(self.get_parameter("finder_result_topic").value),
            self._finder_result_callback,
            50,
        )
        self.create_subscription(
            String,
            str(self.get_parameter("finder_status_topic").value),
            self._finder_status_callback,
            50,
        )
        self.create_subscription(
            String,
            str(self.get_parameter("stored_task_result_topic").value),
            self._stored_task_result_callback,
            50,
        )
        self.create_subscription(
            String,
            str(self.get_parameter("stored_task_status_topic").value),
            self._stored_task_status_callback,
            50,
        )

        self.runtime = GatewayRuntime(self, settings, object_catalog)
        socket_path = str(self.get_parameter("socket_path").value)
        self.rpc_server = GatewayUnixServer(socket_path, self.runtime)
        self.rpc_thread = GatewayServerThread(self.rpc_server)
        self.rpc_thread.start()
        self._last_topic_times: dict[str, float] = {}
        self.get_logger().info(
            f"Robot Action Gateway ready: socket={socket_path}, real_motion_enabled={self.real_motion_enabled}"
        )

    # ------------------------------------------------------------------
    # ROS callbacks
    # ------------------------------------------------------------------
    def _pico_callback(self, msg: String) -> None:
        payload = _json_object(msg.data)
        if payload is not None:
            self._last_topic_times["pico_response"] = time.monotonic()
            self.pico_stream.append(payload)

    def _validation_callback(self, msg: String) -> None:
        payload = _json_object(msg.data)
        if payload is not None:
            self._last_topic_times["validation"] = time.monotonic()
            self.validation_stream.append(payload)

    def _arm_bridge_callback(self, msg: String) -> None:
        payload = _json_object(msg.data)
        if payload is None:
            return
        self._last_topic_times["arm_bridge"] = time.monotonic()
        self.arm_bridge_stream.append(payload)
        event = str(payload.get("event", ""))
        if event == "trajectory_started":
            self.runtime.state.mark_arm_transient()
        elif event in {
            "runtime_interpolation_rejected",
            "defense_in_depth_rejection",
            "pico_error",
            "invalid_validated_goal",
        }:
            self.runtime.state.mark_arm_unreliable()

    def _logical_state_callback(self, msg: JointState) -> None:
        values = {name: position for name, position in zip(msg.name, msg.position)}
        if not all(name in values for name in JOINT_NAMES):
            return
        try:
            q = tuple(float(values[name]) for name in JOINT_NAMES)
        except (TypeError, ValueError):
            return
        if not all(math.isfinite(item) for item in q):
            return
        transient = (
            self.runtime.resources.owner(self._resource("ARM_MOTION")) is not None
            or self.runtime.resources.owner(self._resource("GRIPPER_MOTION")) is not None
        )
        self.runtime.state.update_logical_joint_state(
            math.degrees(q[0]),
            math.degrees(q[1]),
            math.degrees(q[2]),
            transient=transient,
        )
        self._last_topic_times["logical_state"] = time.monotonic()

    def _alignment_status_callback(self, msg: String) -> None:
        payload = _json_object(msg.data)
        if payload is not None:
            self._last_topic_times["alignment_status"] = time.monotonic()
            self.alignment_status_stream.append(payload)

    def _alignment_result_callback(self, msg: String) -> None:
        payload = _json_object(msg.data)
        if payload is not None:
            self._last_topic_times["alignment_result"] = time.monotonic()
            self.alignment_result_stream.append(payload)

    def _finder_status_callback(self, msg: String) -> None:
        payload = _json_object(msg.data)
        if payload is not None:
            self._last_topic_times["finder_status"] = time.monotonic()
            self.finder_status_stream.append(payload)
            self.runtime.state.update_perception_status()

    def _stored_task_result_callback(self, msg: String) -> None:
        payload = _json_object(msg.data)
        if payload is not None:
            self._last_topic_times["stored_task_result"] = time.monotonic()
            self.stored_task_result_stream.append(payload)

    def _stored_task_status_callback(self, msg: String) -> None:
        payload = _json_object(msg.data)
        if payload is None:
            return
        self._last_topic_times["stored_task_status"] = time.monotonic()
        self.stored_task_status_stream.append(payload)
        held = payload.get("held_object")
        if not isinstance(held, dict):
            return
        state = str(held.get("state", "unknown")).strip().casefold()
        if state == "empty":
            self.runtime.state.set_held_object(None, known=True)
            return
        if state == "holding":
            object_id = self._catalog_object_id(str(held.get("object_name", "")))
            if object_id is not None:
                self.runtime.state.set_held_object(object_id, known=True)
                return
        self.runtime.state.set_held_object(None, known=False)

    def _finder_result_callback(self, msg: String) -> None:
        payload = _json_object(msg.data)
        if payload is None:
            return
        self._last_topic_times["finder_result"] = time.monotonic()
        self.finder_result_stream.append(payload)
        name = str(payload.get("object_name", "")).strip()
        object_id = self._catalog_object_id(name)
        if object_id is None:
            return
        confidence = payload.get("score", payload.get("confidence"))
        try:
            confidence_value = None if confidence is None else float(confidence)
        except (TypeError, ValueError):
            confidence_value = None
        stamp_sec = payload.get("stamp_sec")
        try:
            observed_ms = None if stamp_sec is None else int(float(stamp_sec) * 1000)
        except (TypeError, ValueError):
            observed_ms = None
        self.runtime.state.update_object_result(
            object_id,
            event=str(payload.get("event", "")),
            confidence=confidence_value,
            observed_at_unix_ms=observed_ms,
        )

    # ------------------------------------------------------------------
    # HardwareBridge implementation
    # ------------------------------------------------------------------
    def execute_base_move(
        self,
        distance_m: float,
        *,
        speed: int,
        timeout_s: float,
        cancel_event: threading.Event,
    ) -> BridgeOutcome:
        if not self.real_motion_enabled:
            return self._dry_run_motion(cancel_event, "MOVE_BASE")
        centimeters = distance_m * 100.0
        if not self.pico_move_positive_is_forward:
            centimeters = -centimeters
        command = f"MOVE_CM {centimeters:.3f} {int(speed)} {float(timeout_s):.2f}"
        return self._execute_pico_command(
            command,
            expected_event="move_cm_result",
            timeout_s=timeout_s,
            cancel_event=cancel_event,
        )

    def execute_base_turn(
        self,
        angle_deg: float,
        *,
        speed: int,
        timeout_s: float,
        cancel_event: threading.Event,
    ) -> BridgeOutcome:
        if not self.real_motion_enabled:
            return self._dry_run_motion(cancel_event, "TURN_BASE")
        pico_angle = -angle_deg if self.pico_turn_positive_is_right else angle_deg
        command = f"TURN_DEG {pico_angle:.3f} {int(speed)} {float(timeout_s):.2f}"
        return self._execute_pico_command(
            command,
            expected_event="turn_deg_result",
            timeout_s=timeout_s,
            cancel_event=cancel_event,
        )

    def _execute_pico_command(
        self,
        command: str,
        *,
        expected_event: str,
        timeout_s: float,
        cancel_event: threading.Event,
    ) -> BridgeOutcome:
        before = self.pico_stream.last_sequence()
        outgoing = String()
        outgoing.data = command
        self.pico_command_pub.publish(outgoing)
        deadline = time.monotonic() + timeout_s + 1.0
        errors = {"command_error", "main_loop_error", "estop_latched", "busy"}
        while time.monotonic() < deadline:
            if cancel_event.is_set():
                stopped = self.stop_base(float(self._setting("control_timeouts.cancel_action_s", 3.0)))
                return BridgeOutcome(
                    False,
                    "RUN_CANCELED" if stopped.success else "SAFE_STOP_UNCONFIRMED",
                    "차체 액션이 취소되었습니다." if stopped.success else stopped.error_message,
                    canceled=stopped.success,
                    started=True,
                )
            payload = self.pico_stream.wait_for(
                lambda item: str(item.get("event", "")) == expected_event
                or str(item.get("event", "")) in errors,
                after_sequence=before,
                timeout_s=min(0.15, max(0.01, deadline - time.monotonic())),
            )
            if payload is None:
                continue
            event = str(payload.get("event", ""))
            if event == expected_event:
                if payload.get("ok") is True and str(payload.get("status", "")) == "done":
                    return BridgeOutcome(True, details=payload)
                status = str(payload.get("status", "failed"))
                return BridgeOutcome(
                    False,
                    "MOTION_EXECUTION_FAILED",
                    f"Pico motion failed: {status}",
                    details=payload,
                    started=True,
                )
            code = "PICO_COMMUNICATION_ERROR" if event in {"command_error", "main_loop_error"} else "MOTION_EXECUTION_FAILED"
            return BridgeOutcome(False, code, f"Pico error event: {event}", details=payload, started=True)
        stopped = self.stop_base(float(self._setting("control_timeouts.cancel_action_s", 3.0)))
        return BridgeOutcome(
            False,
            "ACTION_HARD_TIMEOUT" if stopped.success else "SAFE_STOP_UNCONFIRMED",
            "차체 액션 hard timeout" if stopped.success else "timeout 후 차체 정지를 확인하지 못했습니다.",
            timed_out=stopped.success,
            started=True,
        )

    def stop_base(self, timeout_s: float) -> BridgeOutcome:
        if not self.real_motion_enabled:
            return BridgeOutcome(True, details={"dry_run": True})
        before = self.pico_stream.last_sequence()
        message = String()
        message.data = "STOP"
        self.pico_command_pub.publish(message)
        payload = self.pico_stream.wait_for(
            lambda item: str(item.get("event", "")) == "stopped" and item.get("ok") is True,
            after_sequence=before,
            timeout_s=max(0.1, timeout_s),
        )
        if payload is None:
            return BridgeOutcome(False, "BASE_STOP_FAILED", "Pico STOP 응답을 확인하지 못했습니다.", started=True)
        return BridgeOutcome(True, details=payload)

    def execute_arm_goal(
        self,
        q_rad: tuple[float, float, float],
        *,
        timeout_s: float,
        cancel_event: threading.Event,
    ) -> BridgeOutcome:
        if not self.real_motion_enabled:
            return self._dry_run_motion(cancel_event, "ARM")
        validation_before = self.validation_stream.last_sequence()
        bridge_before = self.arm_bridge_stream.last_sequence()
        goal = JointState()
        goal.header.stamp = self.get_clock().now().to_msg()
        goal.name = list(JOINT_NAMES)
        goal.position = list(q_rad)
        self.joint_goal_pub.publish(goal)
        deadline = time.monotonic() + timeout_s

        validation: dict[str, Any] | None = None
        while time.monotonic() < deadline and validation is None:
            if cancel_event.is_set():
                return self._cancel_arm_outcome()
            validation = self.validation_stream.wait_for(
                lambda item: str(item.get("event", "")) in {"goal_validated", "goal_rejected"}
                and (
                    str(item.get("event", "")) == "goal_rejected"
                    or _q_close(item.get("goal"), q_rad)
                ),
                after_sequence=validation_before,
                timeout_s=min(0.15, max(0.01, deadline - time.monotonic())),
            )
        if validation is None:
            stopped = self.stop_arm(float(self._setting("control_timeouts.cancel_action_s", 3.0)))
            return BridgeOutcome(False, "ACTION_HARD_TIMEOUT", "팔 validation timeout", timed_out=stopped.success, started=True)
        if str(validation.get("event")) == "goal_rejected":
            reason = str(validation.get("reason", "arm_path_unsafe"))
            code = "ARM_LIMIT_VIOLATION" if "limit" in reason else "ARM_PATH_UNSAFE"
            return BridgeOutcome(False, code, f"팔 목표가 validator에서 거부되었습니다: {reason}", details=validation, started=False)

        errors = {
            "runtime_interpolation_rejected",
            "defense_in_depth_rejection",
            "pico_error",
            "invalid_validated_goal",
            "bridge_busy",
        }
        while time.monotonic() < deadline:
            if cancel_event.is_set():
                return self._cancel_arm_outcome()
            payload = self.arm_bridge_stream.wait_for(
                lambda item: (
                    str(item.get("event", "")) == "trajectory_completed"
                    and _q_close(item.get("goal"), q_rad)
                )
                or str(item.get("event", "")) in errors,
                after_sequence=bridge_before,
                timeout_s=min(0.15, max(0.01, deadline - time.monotonic())),
            )
            if payload is None:
                continue
            event = str(payload.get("event", ""))
            if event == "trajectory_completed":
                return BridgeOutcome(True, details=payload)
            code = "PICO_COMMUNICATION_ERROR" if event == "pico_error" else "ARM_EXECUTION_FAILED"
            return BridgeOutcome(False, code, f"servo bridge error: {event}", details=payload, started=True)
        stopped = self.stop_arm(float(self._setting("control_timeouts.cancel_action_s", 3.0)))
        return BridgeOutcome(
            False,
            "ACTION_HARD_TIMEOUT" if stopped.success else "SAFE_STOP_UNCONFIRMED",
            "팔 액션 hard timeout" if stopped.success else "timeout 후 팔 정지를 확인하지 못했습니다.",
            timed_out=stopped.success,
            started=True,
        )

    def _cancel_arm_outcome(self) -> BridgeOutcome:
        stopped = self.stop_arm(float(self._setting("control_timeouts.cancel_action_s", 3.0)))
        return BridgeOutcome(
            False,
            "RUN_CANCELED" if stopped.success else "SAFE_STOP_UNCONFIRMED",
            "팔 액션이 취소되었습니다." if stopped.success else stopped.error_message,
            canceled=stopped.success,
            started=True,
        )

    def stop_arm(self, timeout_s: float) -> BridgeOutcome:
        if not self.real_motion_enabled:
            return BridgeOutcome(True, details={"dry_run": True})
        before = self.arm_bridge_stream.last_sequence()
        self.arm_stop_pub.publish(Empty())
        payload = self.arm_bridge_stream.wait_for(
            lambda item: str(item.get("event", "")) == "trajectory_stopped" and item.get("ok") is True,
            after_sequence=before,
            timeout_s=max(0.1, timeout_s),
        )
        if payload is None:
            return BridgeOutcome(False, "ARM_STOP_FAILED", "servo bridge의 trajectory_stopped를 확인하지 못했습니다.", started=True)
        return BridgeOutcome(True, details=payload)

    def execute_align_pick(
        self,
        object_id: ObjectId,
        *,
        alignment_profile: str,
        pick_profile: str,
        execute_pick: bool,
        timeout_s: float,
        cancel_event: threading.Event,
    ) -> BridgeOutcome:
        if not self.real_motion_enabled:
            return self._dry_run_motion(cancel_event, "PICK" if execute_pick else "ALIGN", details={"internal_motion_steps": 0})
        before = self.alignment_result_stream.last_sequence()
        goal = String()
        goal.data = json.dumps(
            {
                "object_name": object_id.value,
                "alignment_profile": alignment_profile,
                "pick_profile": pick_profile,
                "execute_pick": execute_pick,
                "search_timeout_sec": min(timeout_s, 60.0),
            },
            ensure_ascii=False,
        )
        self.align_pick_goal_pub.publish(goal)
        deadline = time.monotonic() + timeout_s
        expected = "align_pick_completed" if execute_pick else "alignment_completed"
        while time.monotonic() < deadline:
            if cancel_event.is_set():
                self.cancel_align_pick()
                return BridgeOutcome(False, "RUN_CANCELED", "정렬/파지 액션이 취소되었습니다.", canceled=True, started=True)
            payload = self.alignment_result_stream.wait_for(
                lambda item: str(item.get("object_name", "")).casefold() == object_id.value.casefold()
                and (
                    str(item.get("event", "")) == expected
                    or item.get("ok") is False
                ),
                after_sequence=before,
                timeout_s=min(0.2, max(0.01, deadline - time.monotonic())),
            )
            if payload is None:
                continue
            if payload.get("ok") is True and str(payload.get("event")) == expected:
                iterations = int(payload.get("iterations", 0) or 0)
                pick_result = payload.get("pick_result")
                pick_steps = 0
                if isinstance(pick_result, dict):
                    steps = pick_result.get("steps")
                    if isinstance(steps, dict):
                        pick_steps = len(steps)
                details = dict(payload)
                details["internal_motion_steps"] = max(0, iterations) + max(0, pick_steps)
                return BridgeOutcome(True, details=details)
            reason = str(payload.get("reason", payload.get("event", "alignment_failed")))
            code = self._align_error_code(reason)
            return BridgeOutcome(False, code, f"정렬/파지 실패: {reason}", details=payload, started=True)
        self.cancel_align_pick()
        return BridgeOutcome(False, "ACTION_HARD_TIMEOUT", "정렬/파지 hard timeout", timed_out=True, started=True)

    def execute_place_nextto(
        self,
        reference_object_id: ObjectId,
        *,
        reference_profile: str,
        held_object_id: ObjectId,
        placement_offset_base: tuple[float, float, float],
        timeout_s: float,
        cancel_event: threading.Event,
    ) -> BridgeOutcome:
        if not self.real_motion_enabled:
            return self._dry_run_motion(
                cancel_event,
                "PLACE",
                details={"internal_motion_steps": 4},
            )
        request_id = f"gateway-place-{uuid.uuid4().hex}"
        self._active_place_request_id = request_id
        before = self.stored_task_result_stream.last_sequence()
        goal = String()
        goal.data = json.dumps(
            {
                "task": "place",
                "request_id": request_id,
                "reference_object": reference_object_id.value,
                "reference_profile": reference_profile,
                "held_object": held_object_id.value,
                "placement_offset_base": list(placement_offset_base),
                "timeout_sec": timeout_s,
                "start_finder": True,
            },
            ensure_ascii=False,
        )
        self.stored_task_goal_pub.publish(goal)
        deadline = time.monotonic() + timeout_s
        terminal_events = {
            "stored_place_completed",
            "stored_place_failed",
            "stored_place_rejected",
            "stored_place_timed_out",
            "stored_place_cancelled",
        }
        try:
            while time.monotonic() < deadline:
                if cancel_event.is_set():
                    self.cancel_place_nextto()
                    return BridgeOutcome(
                        False,
                        "RUN_CANCELED",
                        "배치 액션이 취소되었습니다.",
                        canceled=True,
                        started=True,
                    )
                payload = self.stored_task_result_stream.wait_for(
                    lambda item: str(item.get("request_id", "")) == request_id
                    and (
                        str(item.get("event", "")) in terminal_events
                        or item.get("ok") is False
                    ),
                    after_sequence=before,
                    timeout_s=min(0.2, max(0.01, deadline - time.monotonic())),
                )
                if payload is None:
                    continue
                event = str(payload.get("event", ""))
                if payload.get("ok") is True and event == "stored_place_completed":
                    iterations = int(payload.get("iterations", 0) or 0)
                    steps = payload.get("steps")
                    place_steps = 4
                    if isinstance(steps, dict):
                        place_result = steps.get("place")
                        if isinstance(place_result, dict):
                            listed = place_result.get("steps")
                            if isinstance(listed, (dict, list)):
                                place_steps = len(listed)
                    details = dict(payload)
                    details["internal_motion_steps"] = max(0, iterations) + max(1, place_steps)
                    return BridgeOutcome(True, details=details)
                reason = str(payload.get("reason", payload.get("error_code", event or "place_failed")))
                code = self._place_error_code(reason, event)
                return BridgeOutcome(
                    False,
                    code,
                    f"배치 실패: {reason}",
                    details=payload,
                    timed_out=event == "stored_place_timed_out",
                    canceled=event == "stored_place_cancelled",
                    started=True,
                )
            self.cancel_place_nextto()
            return BridgeOutcome(
                False,
                "ACTION_HARD_TIMEOUT",
                "배치 hard timeout",
                timed_out=True,
                started=True,
            )
        finally:
            if self._active_place_request_id == request_id:
                self._active_place_request_id = ""

    def cancel_place_nextto(self) -> None:
        if not self.real_motion_enabled:
            return
        message = String()
        message.data = (
            "gateway_cancel"
            if not self._active_place_request_id
            else f"gateway_cancel:{self._active_place_request_id}"
        )
        self.stored_task_cancel_pub.publish(message)

    def cancel_align_pick(self) -> None:
        if not self.real_motion_enabled:
            return
        message = String()
        message.data = "gateway_cancel"
        self.alignment_cancel_pub.publish(message)

    def system_health(self) -> dict[str, Any]:
        now = time.monotonic()
        ages = {
            name: None if timestamp is None else now - timestamp
            for name, timestamp in {
                "pico_response": self._last_topic_times.get("pico_response"),
                "logical_state": self._last_topic_times.get("logical_state"),
                "arm_bridge": self._last_topic_times.get("arm_bridge"),
                "finder_status": self._last_topic_times.get("finder_status"),
                "finder_result": self._last_topic_times.get("finder_result"),
                "stored_task_result": self._last_topic_times.get("stored_task_result"),
                "stored_task_status": self._last_topic_times.get("stored_task_status"),
            }.items()
        }
        return {
            "real_motion_enabled": self.real_motion_enabled,
            "topic_age_sec": ages,
            "publisher_counts": {
                "pico_command": self.count_subscribers(str(self.get_parameter("pico_command_topic").value)),
                "joint_goal": self.count_subscribers(str(self.get_parameter("joint_goal_topic").value)),
                "align_pick_goal": self.count_subscribers(str(self.get_parameter("align_pick_goal_topic").value)),
                "stored_task_goal": self.count_subscribers(str(self.get_parameter("stored_task_goal_topic").value)),
            },
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _dry_run_motion(
        self,
        cancel_event: threading.Event,
        label: str,
        *,
        details: dict[str, Any] | None = None,
    ) -> BridgeOutcome:
        duration = float(self._setting("dry_run.simulated_motion_sec", 0.05))
        deadline = time.monotonic() + duration
        while time.monotonic() < deadline:
            if cancel_event.is_set():
                return BridgeOutcome(False, "RUN_CANCELED", f"{label} dry-run cancelled", canceled=True)
            time.sleep(0.01)
        return BridgeOutcome(True, details={"dry_run": True, **(details or {})})

    def _setting(self, dotted: str, default: Any) -> Any:
        current: Any = self.settings
        for part in dotted.split("."):
            if not isinstance(current, dict) or part not in current:
                return default
            current = current[part]
        return current

    def _catalog_object_id(self, runtime_name: str) -> ObjectId | None:
        for object_id in ObjectId:
            config = self.object_catalog.get(object_id.name, {})
            names = {
                object_id.name.casefold(),
                object_id.value.casefold(),
                str(config.get("runtime_name", "")).casefold(),
            }
            if runtime_name.casefold() in names:
                return object_id
        return None

    @staticmethod
    def _resource(name: str):
        from .api_types import ResourceId
        return ResourceId[name]

    @staticmethod
    def _align_error_code(reason: str) -> str:
        lowered = reason.casefold()
        if "not_found" in lowered or "search_timeout" in lowered:
            return "OBJECT_NOT_FOUND"
        if "ambiguous" in lowered:
            return "OBJECT_AMBIGUOUS"
        if "lost" in lowered:
            return "OBJECT_LOST"
        if "grasp" in lowered or "unreachable" in lowered:
            return "TARGET_NOT_GRASPABLE"
        if "timeout" in lowered or "iteration" in lowered:
            return "ALIGNMENT_TIMEOUT"
        if "profile" in lowered:
            return "GRASP_PROFILE_NOT_FOUND"
        return "MOTION_EXECUTION_FAILED"

    @staticmethod
    def _place_error_code(reason: str, event: str = "") -> str:
        lowered = f"{event} {reason}".casefold()
        if "held" in lowered and "unknown" in lowered:
            return "HELD_OBJECT_STATE_UNKNOWN"
        if "not holding" in lowered or "no_held" in lowered:
            return "NO_HELD_OBJECT"
        if "not_found" in lowered or "search_timeout" in lowered:
            return "REFERENCE_OBJECT_NOT_FOUND"
        if "ambiguous" in lowered:
            return "REFERENCE_OBJECT_AMBIGUOUS"
        if "unsafe" in lowered or "preflight" in lowered:
            return "PLACEMENT_PATH_UNSAFE"
        if "unreachable" in lowered or "ik" in lowered:
            return "PLACEMENT_TARGET_UNREACHABLE"
        if "profile" in lowered:
            return "PLACEMENT_PROFILE_NOT_FOUND"
        if "timeout" in lowered:
            return "ACTION_HARD_TIMEOUT"
        if "cancel" in lowered:
            return "RUN_CANCELED"
        return "PLACEMENT_FAILED"

    def destroy_node(self):
        try:
            self.rpc_thread.close()
        finally:
            return super().destroy_node()


def main(args=None) -> None:
    rclpy.init(args=args)
    node = MacRobotActionGatewayNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
