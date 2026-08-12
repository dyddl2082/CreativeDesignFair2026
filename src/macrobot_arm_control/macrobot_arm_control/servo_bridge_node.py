from __future__ import annotations

import json
import math
from pathlib import Path
import time
from typing import Dict, Optional, Tuple

from ament_index_python.packages import get_package_share_directory
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Empty, String

from .safety import SafeRegionGrid, SafetyValidator
from .servo_mapping import JOINT_NAMES, ServoMapping, load_servo_mapping


Q = Tuple[float, float, float]


def smoothstep(value: float) -> float:
    value = min(1.0, max(0.0, value))
    return value * value * (3.0 - 2.0 * value)


class ArmServoBridgeNode(Node):
    """Execute validated logical goals as interpolated PCA9685 commands.

    This node has no physical feedback. ``/macrobot/arm/logical_joint_states``
    therefore represents the commanded state, not a measured state.
    """

    def __init__(self) -> None:
        super().__init__("macrobot_arm_servo_bridge")

        safe_pkg = Path(get_package_share_directory("macrobot_safe_region"))
        default_actuator_file = safe_pkg / "config" / "actuator_limits.yaml"

        self.declare_parameter("input_topic", "/macrobot/arm/validated_joint_goal")
        self.declare_parameter("logical_state_topic", "/macrobot/arm/logical_joint_states")
        self.declare_parameter("pico_command_topic", "/pico_debug/cmd")
        self.declare_parameter("pico_response_topic", "/pico_debug/response")
        self.declare_parameter("status_topic", "/macrobot/arm/servo_bridge/status")
        self.declare_parameter("command_preview_topic", "/macrobot/arm/servo_bridge/command_preview")
        self.declare_parameter("stop_topic", "/macrobot/arm/stop")
        self.declare_parameter("disable_topic", "/macrobot/arm/disable_servos")

        self.declare_parameter("actuator_limits_file", str(default_actuator_file))
        self.declare_parameter("safe_region_csv", "")
        self.declare_parameter("require_safe_region", False)
        self.declare_parameter("safe_region_mode", "cell")
        self.declare_parameter("required_safe_region_revision", "macrobot-collision-dae-v2-20260808")

        self.declare_parameter("dry_run", True)
        self.declare_parameter("command_mode", "pulse_us")  # pulse_us or angle
        self.declare_parameter("update_rate_hz", 10.0)
        self.declare_parameter("q1_max_velocity", 0.35)
        self.declare_parameter("q2_max_velocity", 0.35)
        self.declare_parameter("q3_max_velocity", 0.50)
        self.declare_parameter("minimum_duration_sec", 0.20)
        self.declare_parameter("preempt_active_goal", True)
        self.declare_parameter("command_home_on_start", False)
        self.declare_parameter("minimum_command_delta", 1.0)

        self.mapping: ServoMapping = load_servo_mapping(
            str(self.get_parameter("actuator_limits_file").value)
        )
        self.require_safe_region = bool(self.get_parameter("require_safe_region").value)
        safe_csv = str(self.get_parameter("safe_region_csv").value).strip()
        grid: Optional[SafeRegionGrid] = None
        if safe_csv:
            try:
                grid = SafeRegionGrid(safe_csv)
                self.get_logger().info(f"Servo bridge loaded safe region: {grid.path}")
                required_revision = str(
                    self.get_parameter("required_safe_region_revision").value
                ).strip()
                if required_revision and grid.model_revision != required_revision:
                    raise RuntimeError(
                        "Safe-region model revision mismatch: "
                        f"required={required_revision!r}, found={grid.model_revision!r}, "
                        f"summary={grid.summary_path}"
                    )
            except Exception as exc:
                if self.require_safe_region:
                    raise RuntimeError(f"Safe-region loading failed: {exc}") from exc
                self.get_logger().warning(f"Safe region unavailable: {exc}")
        elif self.require_safe_region:
            raise RuntimeError("require_safe_region=true but safe_region_csv is empty")

        self.validator = SafetyValidator(
            self.mapping,
            grid,
            str(self.get_parameter("safe_region_mode").value),
        )
        self.dry_run = bool(self.get_parameter("dry_run").value)
        self.command_mode = str(self.get_parameter("command_mode").value).lower()
        if self.command_mode not in ("pulse_us", "angle"):
            raise ValueError("command_mode must be 'pulse_us' or 'angle'")

        self.rate_hz = max(1.0, float(self.get_parameter("update_rate_hz").value))
        self.max_vel = (
            max(1e-4, float(self.get_parameter("q1_max_velocity").value)),
            max(1e-4, float(self.get_parameter("q2_max_velocity").value)),
            max(1e-4, float(self.get_parameter("q3_max_velocity").value)),
        )
        self.minimum_duration = max(
            0.0, float(self.get_parameter("minimum_duration_sec").value)
        )
        self.preempt = bool(self.get_parameter("preempt_active_goal").value)
        self.minimum_command_delta = max(
            0.0, float(self.get_parameter("minimum_command_delta").value)
        )

        self.command_pub = self.create_publisher(
            String, str(self.get_parameter("pico_command_topic").value), 100
        )
        self.state_pub = self.create_publisher(
            JointState, str(self.get_parameter("logical_state_topic").value), 10
        )
        self.status_pub = self.create_publisher(
            String, str(self.get_parameter("status_topic").value), 10
        )
        self.preview_pub = self.create_publisher(
            String, str(self.get_parameter("command_preview_topic").value), 100
        )

        self.create_subscription(
            JointState,
            str(self.get_parameter("input_topic").value),
            self._goal_callback,
            10,
        )
        self.create_subscription(
            String,
            str(self.get_parameter("pico_response_topic").value),
            self._pico_response_callback,
            100,
        )
        self.create_subscription(
            Empty,
            str(self.get_parameter("stop_topic").value),
            self._stop_callback,
            10,
        )
        self.create_subscription(
            Empty,
            str(self.get_parameter("disable_topic").value),
            self._disable_callback,
            10,
        )

        self.current_q: Q = self.mapping.logical_limits.home
        self.start_q: Q = self.current_q
        self.goal_q: Q = self.current_q
        self.trajectory_start = time.monotonic()
        self.trajectory_duration = 0.0
        self.active = False
        self.last_commands: Dict[str, float] = {}

        self.create_timer(1.0 / self.rate_hz, self._timer_callback)
        self._publish_commanded_state()

        if bool(self.get_parameter("command_home_on_start").value):
            home_result = self.validator.validate_point(self.current_q)
            if not home_result.ok:
                raise RuntimeError(f"Configured home is unsafe: {home_result.reason}")
            self._send_servo_set(self.current_q, force=True)

        self.get_logger().info(
            f"Servo bridge ready: dry_run={self.dry_run}, mode={self.command_mode}, "
            f"rate={self.rate_hz:.1f} Hz"
        )

    @staticmethod
    def _extract_goal(msg: JointState) -> Optional[Q]:
        values = dict(zip(msg.name, msg.position))
        if not all(name in values for name in JOINT_NAMES):
            return None
        q = tuple(float(values[name]) for name in JOINT_NAMES)
        if not all(math.isfinite(value) for value in q):
            return None
        return q  # type: ignore[return-value]

    def _goal_callback(self, msg: JointState) -> None:
        goal = self._extract_goal(msg)
        if goal is None:
            self._publish_status(False, "invalid_validated_goal")
            return
        if self.active and not self.preempt:
            self._publish_status(False, "bridge_busy", {"goal": list(goal)})
            return

        endpoint = self.validator.validate_point(goal)
        if not endpoint.ok:
            self._publish_status(
                False,
                "defense_in_depth_rejection",
                {"reason": endpoint.reason, **endpoint.details},
            )
            return

        duration = max(
            self.minimum_duration,
            max(abs(goal[i] - self.current_q[i]) / self.max_vel[i] for i in range(3)),
        )
        self.start_q = self.current_q
        self.goal_q = goal
        self.trajectory_start = time.monotonic()
        self.trajectory_duration = duration
        self.active = True
        self._publish_status(
            True,
            "trajectory_started",
            {
                "start": list(self.start_q),
                "goal": list(self.goal_q),
                "duration_sec": duration,
                "dry_run": self.dry_run,
            },
        )

    def _timer_callback(self) -> None:
        if self.active:
            elapsed = time.monotonic() - self.trajectory_start
            raw_t = 1.0 if self.trajectory_duration <= 0 else elapsed / self.trajectory_duration
            t = min(1.0, max(0.0, raw_t))
            blend = smoothstep(t)
            candidate: Q = tuple(
                self.start_q[i] + blend * (self.goal_q[i] - self.start_q[i])
                for i in range(3)
            )  # type: ignore[assignment]
            check = self.validator.validate_point(candidate)
            if not check.ok:
                self.active = False
                self._publish_status(
                    False,
                    "runtime_interpolation_rejected",
                    {"reason": check.reason, "q": list(candidate), **check.details},
                )
                return
            self.current_q = candidate
            if t >= 1.0:
                self.current_q = self.goal_q
                self.active = False
                self._send_servo_set(self.current_q, force=True)
                self._publish_status(
                    True,
                    "trajectory_completed",
                    {
                        "goal": list(self.goal_q),
                        "servo_deg": self.mapping.servo_commands_deg(*self.goal_q),
                        "servo_pulse_us": self.mapping.servo_pulses_us(*self.goal_q),
                    },
                )
            else:
                self._send_servo_set(candidate, force=False)
        self._publish_commanded_state()

    def _publish_pico_command(self, command: str) -> None:
        """Publish one complete Pico command and mirror it to the preview topic."""
        preview = String()
        preview.data = command
        self.preview_pub.publish(preview)

        if not self.dry_run:
            message = String()
            message.data = command
            self.command_pub.publish(message)

    def _send_servo_set(self, q: Q, force: bool = False) -> None:
        commands_deg = self.mapping.servo_commands_deg(*q)
        pulses = self.mapping.servo_pulses_us(*q)
        keys = ("lift", "tilt", "gripper")

        if self.command_mode == "pulse_us":
            # Send all three channels in a single serial command.  Pico still
            # writes the PCA9685 channels sequentially, but no other command can
            # be interleaved and all three values belong to the same trajectory
            # sample.
            values = tuple(float(pulses[key]) for key in keys)

            if not force and all(key in self.last_commands for key in keys):
                largest_delta = max(
                    abs(values[index] - self.last_commands[key])
                    for index, key in enumerate(keys)
                )
                if largest_delta < self.minimum_command_delta:
                    return

            command = (
                f"ARM_US {values[0]:.1f} "
                f"{values[1]:.1f} "
                f"{values[2]:.1f}"
            )
            self._publish_pico_command(command)

            for key, value in zip(keys, values):
                self.last_commands[key] = value
            return

        # Legacy angle mode is retained for bench debugging only.  Normal arm
        # operation should use pulse_us/ARM_US so that calibrated pulse limits
        # are preserved.
        axes = (
            ("lift", self.mapping.lift),
            ("tilt", self.mapping.tilt),
            ("gripper", self.mapping.gripper),
        )
        for key, axis in axes:
            value = float(commands_deg[key])
            previous = self.last_commands.get(key)
            if (
                not force
                and previous is not None
                and abs(value - previous) < self.minimum_command_delta
            ):
                continue
            self._publish_pico_command(
                f"SERVO {axis.channel} {value:.3f}"
            )
            self.last_commands[key] = value

    def _publish_commanded_state(self) -> None:
        state = JointState()
        state.header.stamp = self.get_clock().now().to_msg()
        state.name = list(JOINT_NAMES)
        state.position = list(self.current_q)
        self.state_pub.publish(state)

    def _stop_callback(self, _: Empty) -> None:
        self.active = False
        self.goal_q = self.current_q
        self._publish_status(True, "trajectory_stopped", {"hold_q": list(self.current_q)})

    def _disable_callback(self, _: Empty) -> None:
        self.active = False
        self._publish_pico_command("ARM_OFF")
        # After FULL OFF, the next trajectory sample must be transmitted even
        # if it numerically matches the last command before disabling.
        self.last_commands.clear()
        self._publish_status(True, "servos_disabled")

    def _pico_response_callback(self, msg: String) -> None:
        try:
            payload = json.loads(msg.data)
        except Exception:
            return

        if not isinstance(payload, dict):
            return

        event = str(payload.get("event", ""))

        base_events = {
            "move_cm_result",
            "turn_deg_result",
            "drive_relative_result",
            "move_ticks_result",
            "odometry",
            "odometry_reset",
            "status",
            "track_calibration",
            "encoders",
            "encoders_reset",
            "stopped",
            "stop_requested",
        }

        if event in base_events:
            return

        if payload.get("ok") is False or event in {
            "command_error",
            "main_loop_error",
            "servo_error",
        }:
            self.active = False
            self._publish_status(
                False,
                "pico_error",
                {"pico_response": payload},
            )

    def _publish_status(
        self, ok: bool, event: str, details: Optional[Dict[str, object]] = None
    ) -> None:
        payload: Dict[str, object] = {
            "ok": ok,
            "event": event,
            "commanded_state": list(self.current_q),
            "dry_run": self.dry_run,
        }
        if details:
            payload.update(details)
        message = String()
        message.data = json.dumps(payload, ensure_ascii=False)
        self.status_pub.publish(message)
        if ok:
            self.get_logger().info(message.data)
        else:
            self.get_logger().error(message.data)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = ArmServoBridgeNode()
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
