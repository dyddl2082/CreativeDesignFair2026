from __future__ import annotations

import time
from typing import Any, Callable

from PySide6.QtCore import QObject, QThread, Signal
from rclpy.executors import SingleThreadedExecutor
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import String

from .ros_protocol import compact_json, parse_json_object


class RosSignals(QObject):
    backend_status = Signal(object)
    task_status = Signal(object)
    task_result = Signal(object)
    telemetry = Signal(str, object)
    ros_error = Signal(str)


class RosUiBridge:
    """ROS publishers/subscribers whose callbacks emit queued Qt signals."""

    def __init__(self, node) -> None:
        self.node = node
        self.signals = RosSignals()
        defaults = {
            "task_request_topic": "/macrobot/ui/task/request",
            "task_status_topic": "/macrobot/ui/task/status",
            "task_result_topic": "/macrobot/ui/task/result",
            "stop_topic": "/macrobot/ui/stop",
            "held_reset_topic": "/macrobot/ui/held/reset",
            "backend_status_topic": "/macrobot/ui/backend/status",
            "stored_pick_status_topic": "/macrobot/stored_pick/status",
            "stored_pick_result_topic": "/macrobot/stored_pick/result",
            "finder_status_topic": "/object_finder/status",
            "localized_detection_topic": "/macrobot/perception/localized_detection",
            "arm_status_topic": "/macrobot/arm/servo_bridge/status",
            "pico_response_topic": "/pico_debug/response",
        }
        for name, value in defaults.items():
            node.declare_parameter(name, value)

        control_qos = QoSProfile(
            depth=20,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE,
        )
        result_qos = QoSProfile(
            depth=20,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )
        heartbeat_qos = QoSProfile(
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )
        self._request_pub = node.create_publisher(
            String, str(node.get_parameter("task_request_topic").value), control_qos
        )
        self._stop_pub = node.create_publisher(
            String, str(node.get_parameter("stop_topic").value), control_qos
        )
        self._held_reset_pub = node.create_publisher(
            String, str(node.get_parameter("held_reset_topic").value), control_qos
        )
        node.create_subscription(
            String,
            str(node.get_parameter("task_status_topic").value),
            self._callback(self.signals.task_status.emit, "task_status"),
            control_qos,
        )
        node.create_subscription(
            String,
            str(node.get_parameter("task_result_topic").value),
            self._callback(self.signals.task_result.emit, "task_result"),
            result_qos,
        )
        node.create_subscription(
            String,
            str(node.get_parameter("backend_status_topic").value),
            self._callback(self.signals.backend_status.emit, "backend_status"),
            heartbeat_qos,
        )
        telemetry = {
            "stored_pick": "stored_pick_status_topic",
            "stored_result": "stored_pick_result_topic",
            "finder": "finder_status_topic",
            "localized": "localized_detection_topic",
            "arm": "arm_status_topic",
            "pico": "pico_response_topic",
        }
        for label, parameter in telemetry.items():
            node.create_subscription(
                String,
                str(node.get_parameter(parameter).value),
                self._telemetry_callback(label),
                20,
            )

    def publish_task(self, payload: dict[str, Any]) -> None:
        self._request_pub.publish(String(data=compact_json(payload)))

    def publish_stop(self, payload: dict[str, Any]) -> None:
        self._stop_pub.publish(String(data=compact_json(payload)))

    def publish_held_reset(self, payload: dict[str, Any]) -> None:
        self._held_reset_pub.publish(String(data=compact_json(payload)))

    def _callback(
        self,
        emit: Callable[[object], None],
        label: str,
    ) -> Callable[[String], None]:
        def callback(message: String) -> None:
            payload = parse_json_object(message.data)
            if payload is None:
                self.signals.ros_error.emit(f"{label}: invalid JSON")
                return
            emit(payload)

        return callback

    def _telemetry_callback(self, label: str) -> Callable[[String], None]:
        def callback(message: String) -> None:
            payload = parse_json_object(message.data)
            if payload is None:
                payload = {"raw": message.data}
            payload.setdefault("received_at_unix_ms", int(time.time() * 1000))
            self.signals.telemetry.emit(label, payload)

        return callback


class RosExecutorThread(QThread):
    failed = Signal(str)

    def __init__(self, node, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._node = node
        self._executor = SingleThreadedExecutor(context=node.context)
        self._executor.add_node(node)

    def run(self) -> None:
        try:
            while not self.isInterruptionRequested():
                self._executor.spin_once(timeout_sec=0.1)
        except Exception as exc:
            self.failed.emit(f"{type(exc).__name__}: {exc}")

    def stop(self) -> None:
        self.requestInterruption()
        try:
            self._executor.wake()
        except Exception:
            pass
        self.wait(3000)
        try:
            self._executor.remove_node(self._node)
        except Exception:
            pass
        try:
            self._executor.shutdown(timeout_sec=1.0)
        except Exception:
            pass
