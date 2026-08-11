import json
import time
from typing import Optional

import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from geometry_msgs.msg import Twist


def clamp(value, lo, hi):
    return max(lo, min(hi, value))


def sign(value):
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


class TeleopToPicoNode(Node):
    """
    Convert teleop Twist commands into Pico text commands.

    Input:
    - /cmd_vel, geometry_msgs/Twist

    Output:
    - /pico_debug/cmd, std_msgs/String

    Optional input:
    - /pico_debug/response, std_msgs/String
      Used in step mode to know when Pico finished MOVE_CM / TURN_DEG.

    Modes:
    - step:
        forward  -> MOVE_CM +step_cm
        backward -> MOVE_CM -step_cm
        left     -> TURN_DEG -turn_deg
        right    -> TURN_DEG +turn_deg
      This uses Pico encoder-based motion.

    - velocity:
        forward/back/turn -> MOTOR left_pwm right_pwm
      This is open-loop velocity-style teleop.
    """

    def __init__(self):
        super().__init__("teleop_to_pico_node")

        # ------------------------------------------------------------
        # Topics
        # ------------------------------------------------------------
        self.declare_parameter("cmd_vel_topic", "/cmd_vel")
        self.declare_parameter("pico_cmd_topic", "/pico_debug/cmd")
        self.declare_parameter("pico_response_topic", "/pico_debug/response")
        self.declare_parameter("events_topic", "/macrobot_teleop/events")

        # ------------------------------------------------------------
        # Mode
        # ------------------------------------------------------------
        self.declare_parameter("control_mode", "step")  # "step" or "velocity"

        # ------------------------------------------------------------
        # Shared command parameters
        # ------------------------------------------------------------
        self.declare_parameter("deadband", 0.05)
        self.declare_parameter("stop_on_start", True)
        self.declare_parameter("stop_on_shutdown", True)
        self.declare_parameter("dry_run", False)

        # ------------------------------------------------------------
        # Step mode parameters
        # ------------------------------------------------------------
        self.declare_parameter("step_cm", 5.0)
        self.declare_parameter("turn_deg", 15.0)
        self.declare_parameter("step_speed", 110)
        self.declare_parameter("turn_speed", 90)
        self.declare_parameter("step_timeout_sec", 5.0)
        self.declare_parameter("turn_timeout_sec", 5.0)

        # ROS convention:
        # angular.z > 0 means turn left.
        #
        # Pico firmware currently defines:
        # TURN_DEG positive = right turn, based on earlier motor convention.
        #
        # Therefore default ros_left_to_pico_deg_sign = -1.0.
        self.declare_parameter("ros_left_to_pico_deg_sign", -1.0)

        self.declare_parameter("busy_timeout_sec", 8.0)
        self.declare_parameter("min_step_command_interval_sec", 0.05)

        # ------------------------------------------------------------
        # Velocity mode parameters
        # ------------------------------------------------------------
        self.declare_parameter("publish_rate_hz", 10.0)
        self.declare_parameter("velocity_watchdog_timeout_sec", 0.45)

        self.declare_parameter("max_pwm", 110)
        self.declare_parameter("min_pwm", 45)

        self.declare_parameter("max_linear_x", 0.30)
        self.declare_parameter("max_angular_z", 1.20)

        self.declare_parameter("linear_gain", 1.0)
        self.declare_parameter("angular_gain", 1.0)

        self.declare_parameter("linear_sign", 1.0)
        self.declare_parameter("angular_sign", 1.0)

        self.declare_parameter("left_trim", 1.0)
        self.declare_parameter("right_trim", 1.0)

        # ------------------------------------------------------------
        # Read parameters
        # ------------------------------------------------------------
        self.cmd_vel_topic = str(self.get_parameter("cmd_vel_topic").value)
        self.pico_cmd_topic = str(self.get_parameter("pico_cmd_topic").value)
        self.pico_response_topic = str(self.get_parameter("pico_response_topic").value)
        self.events_topic = str(self.get_parameter("events_topic").value)

        self.control_mode = str(self.get_parameter("control_mode").value).lower()

        self.deadband = float(self.get_parameter("deadband").value)
        self.stop_on_start = bool(self.get_parameter("stop_on_start").value)
        self.stop_on_shutdown = bool(self.get_parameter("stop_on_shutdown").value)
        self.dry_run = bool(self.get_parameter("dry_run").value)

        self.step_cm = float(self.get_parameter("step_cm").value)
        self.turn_deg = float(self.get_parameter("turn_deg").value)
        self.step_speed = int(self.get_parameter("step_speed").value)
        self.turn_speed = int(self.get_parameter("turn_speed").value)
        self.step_timeout_sec = float(self.get_parameter("step_timeout_sec").value)
        self.turn_timeout_sec = float(self.get_parameter("turn_timeout_sec").value)
        self.ros_left_to_pico_deg_sign = float(
            self.get_parameter("ros_left_to_pico_deg_sign").value
        )

        self.busy_timeout_sec = float(self.get_parameter("busy_timeout_sec").value)
        self.min_step_command_interval_sec = float(
            self.get_parameter("min_step_command_interval_sec").value
        )

        self.publish_rate_hz = float(self.get_parameter("publish_rate_hz").value)
        self.velocity_watchdog_timeout_sec = float(
            self.get_parameter("velocity_watchdog_timeout_sec").value
        )

        self.max_pwm = int(self.get_parameter("max_pwm").value)
        self.min_pwm = int(self.get_parameter("min_pwm").value)

        self.max_linear_x = float(self.get_parameter("max_linear_x").value)
        self.max_angular_z = float(self.get_parameter("max_angular_z").value)

        self.linear_gain = float(self.get_parameter("linear_gain").value)
        self.angular_gain = float(self.get_parameter("angular_gain").value)

        self.linear_sign = float(self.get_parameter("linear_sign").value)
        self.angular_sign = float(self.get_parameter("angular_sign").value)

        self.left_trim = float(self.get_parameter("left_trim").value)
        self.right_trim = float(self.get_parameter("right_trim").value)

        if self.control_mode not in ["step", "velocity"]:
            raise ValueError("control_mode must be 'step' or 'velocity'.")

        # ------------------------------------------------------------
        # ROS interfaces
        # ------------------------------------------------------------
        self.pico_cmd_pub = self.create_publisher(
            String,
            self.pico_cmd_topic,
            10,
        )

        self.events_pub = self.create_publisher(
            String,
            self.events_topic,
            10,
        )

        self.cmd_vel_sub = self.create_subscription(
            Twist,
            self.cmd_vel_topic,
            self.twist_callback,
            10,
        )

        self.pico_response_sub = self.create_subscription(
            String,
            self.pico_response_topic,
            self.pico_response_callback,
            10,
        )

        # ------------------------------------------------------------
        # State
        # ------------------------------------------------------------
        self.last_twist = Twist()
        self.last_twist_time: Optional[float] = None

        self.last_sent_command = ""
        self.last_step_command_time = 0.0

        self.busy = False
        self.pending_command = ""
        self.pending_command_started_at = 0.0

        if self.control_mode == "velocity":
            timer_period = 1.0 / max(1.0, self.publish_rate_hz)
        else:
            timer_period = 0.05

        self.timer = self.create_timer(timer_period, self.timer_callback)

        self.get_logger().info("MacRobot teleop bridge started.")
        self.get_logger().info(f"Mode: {self.control_mode}")
        self.get_logger().info(f"Subscribing Twist: {self.cmd_vel_topic}")
        self.get_logger().info(f"Publishing Pico commands: {self.pico_cmd_topic}")
        self.get_logger().info(f"Listening Pico responses: {self.pico_response_topic}")

        if self.stop_on_start:
            self.send_pico_command("STOP", reason="startup_stop")

    # ------------------------------------------------------------
    # Twist input
    # ------------------------------------------------------------

    def twist_callback(self, msg: Twist):
        self.last_twist = msg
        self.last_twist_time = time.time()

        if self.control_mode == "step":
            self.handle_step_twist(msg)

    # ------------------------------------------------------------
    # Step mode
    # ------------------------------------------------------------

    def handle_step_twist(self, msg: Twist):
        now = time.time()
        direction = self.classify_twist_direction(msg)

        if direction == "STOP":
            if self.busy:
                self.send_pico_command("STOP", reason="step_stop_while_busy")
                self.busy = False
                self.pending_command = ""
            else:
                self.send_pico_command_once("STOP", reason="step_stop")
            return

        if self.busy:
            # Pico is still executing MOVE_CM or TURN_DEG.
            return

        if now - self.last_step_command_time < self.min_step_command_interval_sec:
            return

        command = self.direction_to_step_command(direction)

        if not command:
            return

        self.send_pico_command(command, reason=f"step_{direction.lower()}")

        self.busy = True
        self.pending_command = command
        self.pending_command_started_at = now
        self.last_step_command_time = now

        self.publish_event(
            {
                "event": "step_command_started",
                "direction": direction,
                "command": command,
            }
        )

    def classify_twist_direction(self, msg: Twist) -> str:
        linear = float(msg.linear.x)
        angular = float(msg.angular.z)

        if abs(linear) < self.deadband and abs(angular) < self.deadband:
            return "STOP"

        # If both are non-zero, choose the dominant axis.
        if abs(linear) >= abs(angular):
            if linear > 0:
                return "FORWARD"
            return "BACKWARD"

        # ROS convention:
        # angular.z > 0 = left
        if angular > 0:
            return "LEFT"
        return "RIGHT"

    def direction_to_step_command(self, direction: str) -> str:
        if direction == "FORWARD":
            return f"MOVE_CM {self.step_cm:.3f} {self.step_speed} {self.step_timeout_sec:.3f}"

        if direction == "BACKWARD":
            return f"MOVE_CM {-self.step_cm:.3f} {self.step_speed} {self.step_timeout_sec:.3f}"

        if direction == "LEFT":
            pico_deg = self.ros_left_to_pico_deg_sign * self.turn_deg
            return f"TURN_DEG {pico_deg:.3f} {self.turn_speed} {self.turn_timeout_sec:.3f}"

        if direction == "RIGHT":
            pico_deg = -self.ros_left_to_pico_deg_sign * self.turn_deg
            return f"TURN_DEG {pico_deg:.3f} {self.turn_speed} {self.turn_timeout_sec:.3f}"

        return ""

    # ------------------------------------------------------------
    # Velocity mode
    # ------------------------------------------------------------

    def run_velocity_mode_once(self):
        now = time.time()

        if self.last_twist_time is None:
            self.send_pico_command_once("STOP", reason="no_twist_yet")
            return

        if now - self.last_twist_time > self.velocity_watchdog_timeout_sec:
            self.send_pico_command_once("STOP", reason="cmd_vel_timeout")
            return

        left_pwm, right_pwm = self.twist_to_motor_pwm(self.last_twist)

        if left_pwm == 0 and right_pwm == 0:
            self.send_pico_command_once("STOP", reason="zero_twist")
            return

        command = f"MOTOR {left_pwm} {right_pwm}"
        self.send_pico_command(command, reason="velocity_motor")

    def twist_to_motor_pwm(self, msg: Twist):
        linear = float(msg.linear.x)
        angular = float(msg.angular.z)

        linear = self.linear_sign * linear
        angular = self.angular_sign * angular

        linear_norm = 0.0
        angular_norm = 0.0

        if self.max_linear_x > 0:
            linear_norm = clamp(linear / self.max_linear_x, -1.0, 1.0)

        if self.max_angular_z > 0:
            angular_norm = clamp(angular / self.max_angular_z, -1.0, 1.0)

        linear_norm *= self.linear_gain
        angular_norm *= self.angular_gain

        linear_norm = clamp(linear_norm, -1.0, 1.0)
        angular_norm = clamp(angular_norm, -1.0, 1.0)

        if abs(linear_norm) < self.deadband:
            linear_norm = 0.0

        if abs(angular_norm) < self.deadband:
            angular_norm = 0.0

        # Differential drive mixing:
        # ROS angular.z > 0 means left turn.
        # left = v - w, right = v + w
        left = linear_norm - angular_norm
        right = linear_norm + angular_norm

        max_abs = max(1.0, abs(left), abs(right))
        left /= max_abs
        right /= max_abs

        left_pwm = self.normalized_to_pwm(left, self.left_trim)
        right_pwm = self.normalized_to_pwm(right, self.right_trim)

        return left_pwm, right_pwm

    def normalized_to_pwm(self, value: float, trim: float):
        value = clamp(value, -1.0, 1.0)

        if abs(value) < self.deadband:
            return 0

        pwm = int(round(value * self.max_pwm * trim))
        pwm = int(clamp(pwm, -self.max_pwm, self.max_pwm))

        if pwm != 0 and abs(pwm) < self.min_pwm:
            pwm = sign(pwm) * self.min_pwm

        return pwm

    # ------------------------------------------------------------
    # Pico responses
    # ------------------------------------------------------------

    def pico_response_callback(self, msg: String):
        text = msg.data.strip()

        if not text:
            return

        parsed = None

        try:
            parsed = json.loads(text)
        except Exception:
            return

        event = parsed.get("event", "")

        done_events = {
            "move_cm_result",
            "turn_deg_result",
            "move_ticks_result",
            "stopped",
            "stop_requested",
            "estop_latched",
            "command_error",
            "main_loop_error",
        }

        if event in done_events:
            if self.busy:
                self.publish_event(
                    {
                        "event": "step_command_finished",
                        "pico_event": event,
                        "pending_command": self.pending_command,
                        "pico_response": parsed,
                    }
                )

            self.busy = False
            self.pending_command = ""

    # ------------------------------------------------------------
    # Timer
    # ------------------------------------------------------------

    def timer_callback(self):
        if self.control_mode == "velocity":
            self.run_velocity_mode_once()
            return

        # Step mode busy watchdog.
        if self.busy:
            elapsed = time.time() - self.pending_command_started_at

            if elapsed > self.busy_timeout_sec:
                self.send_pico_command("STOP", reason="step_busy_timeout")

                self.publish_event(
                    {
                        "event": "step_busy_timeout",
                        "pending_command": self.pending_command,
                        "elapsed_sec": round(elapsed, 3),
                    }
                )

                self.busy = False
                self.pending_command = ""

    # ------------------------------------------------------------
    # Command publishing
    # ------------------------------------------------------------

    def send_pico_command_once(self, command: str, reason: str = ""):
        if self.last_sent_command == command:
            return
        self.send_pico_command(command, reason=reason)

    def send_pico_command(self, command: str, reason: str = ""):
        command = command.strip()

        if not command:
            return

        self.last_sent_command = command

        if self.dry_run:
            self.get_logger().info(f"DRY RUN Pico command: {command}")
        else:
            msg = String()
            msg.data = command
            self.pico_cmd_pub.publish(msg)

        self.publish_event(
            {
                "event": "pico_command_published",
                "command": command,
                "reason": reason,
                "mode": self.control_mode,
                "dry_run": self.dry_run,
            }
        )

    def publish_event(self, payload: dict):
        msg = String()
        msg.data = json.dumps(payload, ensure_ascii=False)
        self.events_pub.publish(msg)

    # ------------------------------------------------------------
    # Shutdown
    # ------------------------------------------------------------

    def destroy_node(self):
        if self.stop_on_shutdown:
            try:
                self.send_pico_command("STOP", reason="shutdown_stop")
            except Exception:
                pass

        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = TeleopToPicoNode()

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
