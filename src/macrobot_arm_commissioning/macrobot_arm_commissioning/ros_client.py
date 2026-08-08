from __future__ import annotations

from collections import deque
import json
import math
from pathlib import Path
import threading
import time
from typing import Deque, Dict, List, Optional, Sequence, Tuple

from ament_index_python.packages import get_package_share_directory
from geometry_msgs.msg import PoseStamped
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Empty, Float64, String

from macrobot_arm_control.servo_mapping import JOINT_NAMES, load_servo_mapping


Q = Tuple[float, float, float]


class ArmCommissioningNode(Node):
    """ROS I/O client used by the interactive commissioning wizard."""

    def __init__(self) -> None:
        super().__init__("macrobot_arm_commissioning")

        safe_pkg = Path(get_package_share_directory("macrobot_safe_region"))
        default_actuator = safe_pkg / "config" / "actuator_limits.yaml"

        self.declare_parameter(
            "report_path",
            str(
                Path.home()
                / "MacRobot"
                / "data"
                / "commissioning"
                / "arm_commissioning_report.yaml"
            ),
        )
        self.declare_parameter("actuator_limits_file", str(default_actuator))
        self.declare_parameter("safe_region_csv", "")
        self.declare_parameter("all_samples_csv", "")
        self.declare_parameter("allow_motion_commands", False)
        self.declare_parameter("allow_raw_pulse_commands", False)
        self.declare_parameter("motion_timeout_sec", 30.0)
        self.declare_parameter("settle_time_sec", 0.25)
        self.declare_parameter("raw_pulse_absolute_min_us", 900.0)
        self.declare_parameter("raw_pulse_absolute_max_us", 2100.0)
        self.declare_parameter("raw_pulse_max_step_us", 25.0)
        self.declare_parameter("raw_pulse_step_delay_sec", 0.12)

        self.declare_parameter("joint_goal_topic", "/macrobot/arm/joint_goal")
        self.declare_parameter("validation_status_topic", "/macrobot/arm/validation_status")
        self.declare_parameter("bridge_status_topic", "/macrobot/arm/servo_bridge/status")
        self.declare_parameter("logical_state_topic", "/macrobot/arm/logical_joint_states")
        self.declare_parameter("tool_pose_topic", "/macrobot/arm/tool_pose")
        self.declare_parameter("gripper_gap_topic", "/macrobot/gripper/gap")
        self.declare_parameter(
            "command_preview_topic", "/macrobot/arm/servo_bridge/command_preview"
        )
        self.declare_parameter("stop_topic", "/macrobot/arm/stop")
        self.declare_parameter("disable_topic", "/macrobot/arm/disable_servos")
        self.declare_parameter("pico_command_topic", "/pico_debug/cmd")
        self.declare_parameter("pico_response_topic", "/pico_debug/response")

        self.report_path = Path(
            str(self.get_parameter("report_path").value)
        ).expanduser().resolve()
        self.actuator_limits_file = Path(
            str(self.get_parameter("actuator_limits_file").value)
        ).expanduser().resolve()
        self.safe_region_csv = str(self.get_parameter("safe_region_csv").value).strip()
        self.all_samples_csv = str(self.get_parameter("all_samples_csv").value).strip()
        self.allow_motion_commands = bool(
            self.get_parameter("allow_motion_commands").value
        )
        self.allow_raw_pulse_commands = bool(
            self.get_parameter("allow_raw_pulse_commands").value
        )
        self.motion_timeout = float(self.get_parameter("motion_timeout_sec").value)
        self.settle_time = float(self.get_parameter("settle_time_sec").value)
        self.raw_min = float(self.get_parameter("raw_pulse_absolute_min_us").value)
        self.raw_max = float(self.get_parameter("raw_pulse_absolute_max_us").value)
        self.raw_max_step = float(self.get_parameter("raw_pulse_max_step_us").value)
        self.raw_step_delay = float(
            self.get_parameter("raw_pulse_step_delay_sec").value
        )

        self.mapping = load_servo_mapping(self.actuator_limits_file)
        self.current_q: Q = self.mapping.logical_limits.home
        self.tool_pose: Optional[Dict[str, float]] = None
        self.gripper_gap: Optional[float] = None
        self.last_preview_commands: Deque[str] = deque(maxlen=100)
        self.last_pico_responses: Deque[Dict[str, object]] = deque(maxlen=100)

        self._condition = threading.Condition()
        self._seq = 0
        self.validation_events: Deque[Tuple[int, Dict[str, object]]] = deque(maxlen=200)
        self.bridge_events: Deque[Tuple[int, Dict[str, object]]] = deque(maxlen=200)

        self.joint_goal_pub = self.create_publisher(
            JointState, str(self.get_parameter("joint_goal_topic").value), 10
        )
        self.stop_pub = self.create_publisher(
            Empty, str(self.get_parameter("stop_topic").value), 10
        )
        self.disable_pub = self.create_publisher(
            Empty, str(self.get_parameter("disable_topic").value), 10
        )
        self.pico_cmd_pub = self.create_publisher(
            String, str(self.get_parameter("pico_command_topic").value), 20
        )

        self.create_subscription(
            String,
            str(self.get_parameter("validation_status_topic").value),
            self._validation_callback,
            20,
        )
        self.create_subscription(
            String,
            str(self.get_parameter("bridge_status_topic").value),
            self._bridge_callback,
            20,
        )
        self.create_subscription(
            JointState,
            str(self.get_parameter("logical_state_topic").value),
            self._logical_state_callback,
            20,
        )
        self.create_subscription(
            PoseStamped,
            str(self.get_parameter("tool_pose_topic").value),
            self._tool_pose_callback,
            20,
        )
        self.create_subscription(
            Float64,
            str(self.get_parameter("gripper_gap_topic").value),
            self._gap_callback,
            20,
        )
        self.create_subscription(
            String,
            str(self.get_parameter("command_preview_topic").value),
            self._preview_callback,
            50,
        )
        self.create_subscription(
            String,
            str(self.get_parameter("pico_response_topic").value),
            self._pico_callback,
            50,
        )

    def _next_seq(self) -> int:
        self._seq += 1
        return self._seq

    @staticmethod
    def _decode_json(text: str) -> Dict[str, object]:
        try:
            value = json.loads(text)
            return value if isinstance(value, dict) else {"raw": text}
        except Exception:
            return {"raw": text}

    def _validation_callback(self, msg: String) -> None:
        payload = self._decode_json(msg.data)
        with self._condition:
            seq = self._next_seq()
            self.validation_events.append((seq, payload))
            self._condition.notify_all()

    def _bridge_callback(self, msg: String) -> None:
        payload = self._decode_json(msg.data)
        with self._condition:
            seq = self._next_seq()
            self.bridge_events.append((seq, payload))
            self._condition.notify_all()

    def _logical_state_callback(self, msg: JointState) -> None:
        values = dict(zip(msg.name, msg.position))
        q = tuple(
            float(values.get(name, self.current_q[index]))
            for index, name in enumerate(JOINT_NAMES)
        )
        if all(math.isfinite(value) for value in q):
            self.current_q = q  # type: ignore[assignment]

    def _tool_pose_callback(self, msg: PoseStamped) -> None:
        self.tool_pose = {
            "frame_id": msg.header.frame_id,
            "x": float(msg.pose.position.x),
            "y": float(msg.pose.position.y),
            "z": float(msg.pose.position.z),
            "qx": float(msg.pose.orientation.x),
            "qy": float(msg.pose.orientation.y),
            "qz": float(msg.pose.orientation.z),
            "qw": float(msg.pose.orientation.w),
        }

    def _gap_callback(self, msg: Float64) -> None:
        self.gripper_gap = float(msg.data)

    def _preview_callback(self, msg: String) -> None:
        self.last_preview_commands.append(msg.data)

    def _pico_callback(self, msg: String) -> None:
        self.last_pico_responses.append(self._decode_json(msg.data))

    @staticmethod
    def _goal_close(payload: Dict[str, object], q: Q, tolerance: float = 1e-5) -> bool:
        candidate = payload.get("goal")
        if not isinstance(candidate, list) or len(candidate) < 3:
            return True
        try:
            return all(abs(float(candidate[i]) - q[i]) <= tolerance for i in range(3))
        except Exception:
            return False

    def _wait_event(
        self,
        source: str,
        after_seq: int,
        accepted_events: Sequence[str],
        timeout: float,
        q: Optional[Q] = None,
    ) -> Optional[Dict[str, object]]:
        deadline = time.monotonic() + timeout
        history = self.validation_events if source == "validation" else self.bridge_events
        with self._condition:
            while True:
                for seq, payload in list(history):
                    if seq <= after_seq:
                        continue
                    if str(payload.get("event", "")) not in accepted_events:
                        continue
                    if q is not None and not self._goal_close(payload, q):
                        continue
                    return dict(payload)
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return None
                self._condition.wait(min(remaining, 0.2))

    def system_snapshot(self) -> Dict[str, object]:
        return {
            "current_q": list(self.current_q),
            "tool_pose": dict(self.tool_pose) if self.tool_pose else None,
            "gripper_gap_m": self.gripper_gap,
            "allow_motion_commands": self.allow_motion_commands,
            "allow_raw_pulse_commands": self.allow_raw_pulse_commands,
            "actuator_limits_file": str(self.actuator_limits_file),
            "safe_region_csv": self.safe_region_csv or None,
            "all_samples_csv": self.all_samples_csv or None,
            "joint_goal_subscribers": self.joint_goal_pub.get_subscription_count(),
            "pico_command_subscribers": self.pico_cmd_pub.get_subscription_count(),
        }

    def execute_joint_goal(self, q: Q, timeout: Optional[float] = None) -> Dict[str, object]:
        if not self.allow_motion_commands:
            return {
                "ok": False,
                "event": "motion_commands_disabled",
                "goal": list(q),
            }
        timeout = self.motion_timeout if timeout is None else float(timeout)
        start_seq = self._seq
        preview_start = len(self.last_preview_commands)
        started_at = time.monotonic()

        message = JointState()
        message.header.stamp = self.get_clock().now().to_msg()
        message.name = list(JOINT_NAMES)
        message.position = list(q)
        self.joint_goal_pub.publish(message)

        validation = self._wait_event(
            "validation",
            start_seq,
            ("goal_validated", "goal_rejected"),
            min(timeout, 10.0),
            q,
        )
        if validation is None:
            return {
                "ok": False,
                "event": "validation_timeout",
                "goal": list(q),
            }
        if validation.get("event") != "goal_validated":
            return {
                "ok": False,
                "event": "goal_rejected",
                "goal": list(q),
                "validation": validation,
            }

        bridge = self._wait_event(
            "bridge",
            start_seq,
            (
                "trajectory_completed",
                "defense_in_depth_rejection",
                "runtime_interpolation_rejected",
                "pico_error",
            ),
            timeout,
            q,
        )
        if bridge is None:
            self.stop()
            return {
                "ok": False,
                "event": "bridge_timeout",
                "goal": list(q),
                "validation": validation,
            }

        if bridge.get("event") != "trajectory_completed":
            return {
                "ok": False,
                "event": str(bridge.get("event")),
                "goal": list(q),
                "validation": validation,
                "bridge": bridge,
            }

        if self.settle_time > 0:
            time.sleep(self.settle_time)
        preview = list(self.last_preview_commands)[preview_start:]
        return {
            "ok": True,
            "event": "trajectory_completed",
            "goal": list(q),
            "duration_sec": time.monotonic() - started_at,
            "validation": validation,
            "bridge": bridge,
            "commanded_state": list(self.current_q),
            "tool_pose": dict(self.tool_pose) if self.tool_pose else None,
            "gripper_gap_m": self.gripper_gap,
            "servo_command_preview": preview,
        }

    def stop(self) -> None:
        self.stop_pub.publish(Empty())

    def disable(self) -> None:
        self.disable_pub.publish(Empty())

    def raw_servo_off(self, axis_name: str) -> None:
        axis = getattr(self.mapping, axis_name)
        message = String()
        message.data = f"SERVO_OFF {axis.channel}"
        self.pico_cmd_pub.publish(message)

    def raw_pulse(self, axis_name: str, pulse_us: float, previous_us: Optional[float] = None) -> Dict[str, object]:
        if not self.allow_raw_pulse_commands:
            return {"ok": False, "event": "raw_pulse_commands_disabled"}
        axis = getattr(self.mapping, axis_name)
        target = min(self.raw_max, max(self.raw_min, float(pulse_us)))
        start = (
            float(previous_us)
            if previous_us is not None
            else float(axis.pulse_center_us)
        )
        count = max(1, int(math.ceil(abs(target - start) / max(self.raw_max_step, 1e-6))))
        sent: List[float] = []
        for index in range(1, count + 1):
            value = start + (target - start) * index / count
            message = String()
            message.data = f"SERVO_US {axis.channel} {value:.1f}"
            self.pico_cmd_pub.publish(message)
            sent.append(value)
            time.sleep(self.raw_step_delay)
        return {
            "ok": True,
            "event": "raw_pulse_sent",
            "axis": axis_name,
            "channel": axis.channel,
            "target_us": target,
            "steps": sent,
        }
