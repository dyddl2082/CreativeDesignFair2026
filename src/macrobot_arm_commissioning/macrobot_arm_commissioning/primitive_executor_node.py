from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional, Tuple

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Empty, String
import yaml


Q = Tuple[float, float, float]


class PrimitiveExecutorNode(Node):
    """Publish validated logical goals stored in the commissioning report."""

    def __init__(self) -> None:
        super().__init__("macrobot_primitive_executor")
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
        self.declare_parameter("command_topic", "/macrobot/arm/primitive_command")
        self.declare_parameter("joint_goal_topic", "/macrobot/arm/joint_goal")
        self.declare_parameter("stop_topic", "/macrobot/arm/stop")
        self.declare_parameter("disable_topic", "/macrobot/arm/disable_servos")
        self.declare_parameter("status_topic", "/macrobot/arm/primitive_status")

        self.report_path = Path(
            str(self.get_parameter("report_path").value)
        ).expanduser().resolve()
        self.goal_pub = self.create_publisher(
            JointState, str(self.get_parameter("joint_goal_topic").value), 10
        )
        self.stop_pub = self.create_publisher(
            Empty, str(self.get_parameter("stop_topic").value), 10
        )
        self.disable_pub = self.create_publisher(
            Empty, str(self.get_parameter("disable_topic").value), 10
        )
        self.status_pub = self.create_publisher(
            String, str(self.get_parameter("status_topic").value), 10
        )
        self.create_subscription(
            String,
            str(self.get_parameter("command_topic").value),
            self._command_callback,
            10,
        )

    def _load_primitive(self, name: str) -> Optional[Dict[str, object]]:
        if not self.report_path.exists():
            return None
        with self.report_path.open("r", encoding="utf-8") as stream:
            report = yaml.safe_load(stream) or {}
        primitives = (
            report.get("sections", {})
            .get("primitives", {})
            .get("primitives", {})
        )
        if not isinstance(primitives, dict):
            return None
        value = primitives.get(name.upper())
        return value if isinstance(value, dict) else None

    def _publish_status(self, ok: bool, event: str, **details: object) -> None:
        message = String()
        message.data = json.dumps(
            {"ok": ok, "event": event, **details},
            ensure_ascii=False,
        )
        self.status_pub.publish(message)

    def _command_callback(self, msg: String) -> None:
        text = msg.data.strip()
        try:
            parsed = json.loads(text)
            name = str(parsed.get("name", "")).upper()
        except Exception:
            name = text.upper()

        if name == "STOP":
            self.stop_pub.publish(Empty())
            self._publish_status(True, "stop_published")
            return
        if name == "DISABLE":
            self.disable_pub.publish(Empty())
            self._publish_status(True, "disable_published")
            return

        primitive = self._load_primitive(name)
        if primitive is None:
            self._publish_status(
                False,
                "primitive_not_found",
                name=name,
                report_path=str(self.report_path),
            )
            return
        q = primitive.get("target_q")
        if not isinstance(q, list) or len(q) != 3:
            self._publish_status(False, "invalid_primitive", name=name)
            return

        goal = JointState()
        goal.header.stamp = self.get_clock().now().to_msg()
        goal.name = [
            "arm_lift_joint",
            "wrist_pitch_joint",
            "gripper_joint",
        ]
        goal.position = [float(value) for value in q]
        self.goal_pub.publish(goal)
        self._publish_status(True, "primitive_goal_published", name=name, q=q)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = PrimitiveExecutorNode()
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
