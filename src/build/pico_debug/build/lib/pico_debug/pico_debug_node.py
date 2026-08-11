import json
import queue
import sys
import threading
import time
from typing import Optional

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

try:
    import serial
except ImportError as exc:
    raise ImportError(
        "pyserial is required. Install it with: sudo apt install -y python3-serial"
    ) from exc


class PicoDebugNode(Node):
    """
    ROS 2 debug bridge for Raspberry Pi Pico.

    Features:
    - Opens Pico USB serial port, usually /dev/ttyACM0.
    - Sends text commands to Pico.
    - Reads Pico JSON/text responses.
    - Supports both interactive terminal input and ROS topic commands.

    Topics:
    - Subscribe: /pico_debug/cmd      std_msgs/String
    - Publish:   /pico_debug/response std_msgs/String
    - Publish:   /pico_debug/events   std_msgs/String
    """

    def __init__(self):
        super().__init__("pico_debug_node")

        self.declare_parameter("serial_port", "/dev/ttyACM0")
        self.declare_parameter("baudrate", 115200)
        self.declare_parameter("interactive", True)
        self.declare_parameter("auto_reconnect", True)
        self.declare_parameter("reconnect_interval_sec", 2.0)
        self.declare_parameter("read_timeout_sec", 0.02)
        self.declare_parameter("write_timeout_sec", 0.5)
        self.declare_parameter("open_delay_sec", 1.2)
        self.declare_parameter("send_stop_on_shutdown", True)
        self.declare_parameter("log_tx", True)
        self.declare_parameter("log_rx", True)

        self.serial_port = str(self.get_parameter("serial_port").value)
        self.baudrate = int(self.get_parameter("baudrate").value)
        self.interactive = bool(self.get_parameter("interactive").value)
        self.auto_reconnect = bool(self.get_parameter("auto_reconnect").value)
        self.reconnect_interval_sec = float(
            self.get_parameter("reconnect_interval_sec").value
        )
        self.read_timeout_sec = float(self.get_parameter("read_timeout_sec").value)
        self.write_timeout_sec = float(self.get_parameter("write_timeout_sec").value)
        self.open_delay_sec = float(self.get_parameter("open_delay_sec").value)
        self.send_stop_on_shutdown = bool(
            self.get_parameter("send_stop_on_shutdown").value
        )
        self.log_tx = bool(self.get_parameter("log_tx").value)
        self.log_rx = bool(self.get_parameter("log_rx").value)

        self.ser: Optional[serial.Serial] = None
        self.last_reconnect_attempt = 0.0
        self.command_queue: "queue.Queue[str]" = queue.Queue()

        self.response_pub = self.create_publisher(
            String,
            "pico_debug/response",
            10,
        )

        self.events_pub = self.create_publisher(
            String,
            "pico_debug/events",
            10,
        )

        self.command_sub = self.create_subscription(
            String,
            "pico_debug/cmd",
            self.command_callback,
            10,
        )

        self.timer = self.create_timer(0.02, self.loop_once)

        self.open_serial()

        if self.interactive:
            self.stdin_thread = threading.Thread(
                target=self.stdin_loop,
                daemon=True,
            )
            self.stdin_thread.start()

        self.get_logger().info("Pico debug node started.")
        self.get_logger().info(f"Serial port: {self.serial_port}")
        self.get_logger().info(f"Baudrate: {self.baudrate}")
        self.get_logger().info("Command topic: /pico_debug/cmd")
        self.get_logger().info("Response topic: /pico_debug/response")

        if self.interactive:
            self.get_logger().info("Interactive mode enabled. Type Pico commands below.")
            print("")
            print("Interactive Pico command mode")
            print("Examples:")
            print("  PING")
            print("  STATUS?")
            print("  ENC?")
            print("  MOTOR 60 60")
            print("  STOP")
            print("  MOVE_CM 10 120 5")
            print("  TURN_DEG 90 100 8")
            print("  SERVO 0 90")
            print("Type 'exit' or 'quit' to close.")
            print("")
            print("pico> ", end="", flush=True)

    # ------------------------------------------------------------
    # Serial handling
    # ------------------------------------------------------------

    def open_serial(self) -> bool:
        if self.ser is not None and self.ser.is_open:
            return True

        now = time.time()

        if now - self.last_reconnect_attempt < self.reconnect_interval_sec:
            return False

        self.last_reconnect_attempt = now

        try:
            self.get_logger().info(f"Opening serial port: {self.serial_port}")

            self.ser = serial.Serial(
                port=self.serial_port,
                baudrate=self.baudrate,
                timeout=self.read_timeout_sec,
                write_timeout=self.write_timeout_sec,
            )

            time.sleep(self.open_delay_sec)

            self.publish_event(
                {
                    "event": "serial_connected",
                    "serial_port": self.serial_port,
                    "baudrate": self.baudrate,
                }
            )

            self.get_logger().info("Serial connected.")
            return True

        except Exception as exc:
            self.ser = None

            self.publish_event(
                {
                    "event": "serial_connect_failed",
                    "serial_port": self.serial_port,
                    "error": str(exc),
                }
            )

            self.get_logger().warn(f"Serial open failed: {exc}")
            return False

    def close_serial(self):
        if self.ser is None:
            return

        try:
            if self.ser.is_open:
                self.ser.close()
        except Exception:
            pass

        self.ser = None

    def write_command(self, command: str):
        command = command.strip()

        if not command:
            return

        if self.ser is None or not self.ser.is_open:
            if not self.open_serial():
                self.publish_event(
                    {
                        "event": "command_dropped",
                        "reason": "serial_not_connected",
                        "command": command,
                    }
                )
                return

        try:
            data = (command + "\n").encode("utf-8")
            self.ser.write(data)
            self.ser.flush()

            if self.log_tx:
                self.get_logger().info(f"TX > {command}")

            self.publish_event(
                {
                    "event": "command_sent",
                    "command": command,
                }
            )

        except Exception as exc:
            self.get_logger().error(f"Serial write failed: {exc}")

            self.publish_event(
                {
                    "event": "serial_write_failed",
                    "command": command,
                    "error": str(exc),
                }
            )

            self.close_serial()

    def read_serial_lines(self):
        if self.ser is None or not self.ser.is_open:
            return

        try:
            # Read all currently available complete lines.
            while self.ser is not None and self.ser.is_open:
                waiting = self.ser.in_waiting

                if waiting <= 0:
                    break

                raw = self.ser.readline()

                if not raw:
                    break

                text = raw.decode("utf-8", errors="replace").strip()

                if not text:
                    continue

                if self.log_rx:
                    self.get_logger().info(f"RX < {text}")

                msg = String()
                msg.data = text
                self.response_pub.publish(msg)

                # If Pico sent JSON, also publish a normalized event.
                try:
                    parsed = json.loads(text)

                    self.publish_event(
                        {
                            "event": "pico_response",
                            "response": parsed,
                        }
                    )
                except Exception:
                    self.publish_event(
                        {
                            "event": "pico_response_raw",
                            "response": text,
                        }
                    )

        except Exception as exc:
            self.get_logger().error(f"Serial read failed: {exc}")

            self.publish_event(
                {
                    "event": "serial_read_failed",
                    "error": str(exc),
                }
            )

            self.close_serial()

    # ------------------------------------------------------------
    # ROS callbacks
    # ------------------------------------------------------------

    def command_callback(self, msg: String):
        command = msg.data.strip()

        if not command:
            return

        self.command_queue.put(command)

    def loop_once(self):
        if self.ser is None or not self.ser.is_open:
            if self.auto_reconnect:
                self.open_serial()
            return

        while not self.command_queue.empty():
            command = self.command_queue.get_nowait()
            self.write_command(command)

        self.read_serial_lines()

    # ------------------------------------------------------------
    # Interactive terminal
    # ------------------------------------------------------------

    def stdin_loop(self):
        while rclpy.ok():
            try:
                line = input()
            except EOFError:
                return
            except KeyboardInterrupt:
                rclpy.shutdown()
                return

            command = line.strip()

            if command.lower() in ["exit", "quit", ":q"]:
                self.publish_event({"event": "interactive_exit"})
                rclpy.shutdown()
                return

            if command:
                self.command_queue.put(command)

            print("pico> ", end="", flush=True)

    # ------------------------------------------------------------
    # Events
    # ------------------------------------------------------------

    def publish_event(self, payload: dict):
        msg = String()
        msg.data = json.dumps(payload, ensure_ascii=False)
        self.events_pub.publish(msg)

    # ------------------------------------------------------------
    # Shutdown
    # ------------------------------------------------------------

    def destroy_node(self):
        if self.send_stop_on_shutdown:
            try:
                self.write_command("STOP")
                time.sleep(0.05)
            except Exception:
                pass

        self.close_serial()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = PicoDebugNode()

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