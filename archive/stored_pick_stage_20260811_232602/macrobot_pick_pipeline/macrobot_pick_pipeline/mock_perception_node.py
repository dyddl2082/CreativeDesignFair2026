from __future__ import annotations

import json
import math
import random
import time

import rclpy
from geometry_msgs.msg import PointStamped
from rclpy.node import Node
from std_msgs.msg import String


class MockPerceptionNode(Node):
    """Publish a stable synthetic object point for WSL2-only integration tests."""

    def __init__(self) -> None:
        super().__init__("macrobot_mock_perception")
        self.declare_parameter("active_target_topic", "/macrobot/pick/active_target")
        self.declare_parameter(
            "localized_detection_topic", "/macrobot/perception/localized_detection"
        )
        self.declare_parameter("point_topic", "/macrobot/perception/object_point")
        self.declare_parameter("base_frame", "base_link")
        self.declare_parameter("default_object_name", "Buds3")
        self.declare_parameter("point_x", -0.150)
        self.declare_parameter("point_y", 0.0645)
        self.declare_parameter("point_z", 0.120)
        self.declare_parameter("score", 0.95)
        self.declare_parameter("noise_std_m", 0.0015)
        self.declare_parameter("publish_rate_hz", 10.0)
        self.declare_parameter("activation_delay_sec", 0.5)

        self.base_frame = str(self.get_parameter("base_frame").value)
        self.default_name = str(self.get_parameter("default_object_name").value)
        self.nominal_point = (
            float(self.get_parameter("point_x").value),
            float(self.get_parameter("point_y").value),
            float(self.get_parameter("point_z").value),
        )
        self.score = float(self.get_parameter("score").value)
        self.noise = max(0.0, float(self.get_parameter("noise_std_m").value))
        self.activation_delay = max(
            0.0, float(self.get_parameter("activation_delay_sec").value)
        )
        rate = max(1.0, float(self.get_parameter("publish_rate_hz").value))

        self.active_target = ""
        self.activated_at = 0.0
        self.detection_pub = self.create_publisher(
            String,
            str(self.get_parameter("localized_detection_topic").value),
            20,
        )
        self.point_pub = self.create_publisher(
            PointStamped,
            str(self.get_parameter("point_topic").value),
            20,
        )
        self.create_subscription(
            String,
            str(self.get_parameter("active_target_topic").value),
            self._target_callback,
            10,
        )
        self.create_timer(1.0 / rate, self._timer_callback)
        self.get_logger().info(
            f"Mock perception ready at base point {self.nominal_point}"
        )

    def _target_callback(self, msg: String) -> None:
        self.active_target = msg.data.strip()
        self.activated_at = time.monotonic()

    def _timer_callback(self) -> None:
        if not self.active_target:
            return
        if time.monotonic() - self.activated_at < self.activation_delay:
            return
        point = tuple(
            nominal + random.gauss(0.0, self.noise)
            for nominal in self.nominal_point
        )
        if not all(math.isfinite(value) for value in point):
            return
        now = self.get_clock().now()
        point_msg = PointStamped()
        point_msg.header.stamp = now.to_msg()
        point_msg.header.frame_id = self.base_frame
        point_msg.point.x, point_msg.point.y, point_msg.point.z = point
        self.point_pub.publish(point_msg)

        payload = {
            "ok": True,
            "event": "localized_object",
            "object_name": self.active_target or self.default_name,
            "score": self.score,
            "frame_id": self.base_frame,
            "point_base": {"x": point[0], "y": point[1], "z": point[2]},
            "stamp_sec": time.time(),
            "source": "mock_perception",
        }
        message = String()
        message.data = json.dumps(payload, ensure_ascii=False)
        self.detection_pub.publish(message)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = MockPerceptionNode()
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
