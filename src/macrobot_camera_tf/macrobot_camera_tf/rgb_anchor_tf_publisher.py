from __future__ import annotations

import json
from pathlib import Path

from geometry_msgs.msg import TransformStamped
import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import String
from tf2_ros import StaticTransformBroadcaster

from .calibration_schema import load_calibration


class RgbAnchorTfPublisher(Node):
    def __init__(self) -> None:
        super().__init__("macrobot_rgb_anchor_tf_publisher")
        self.declare_parameter(
            "calibration_file", "~/MacRobot/data/camera_tf/d435_rgb_anchor.yaml"
        )
        self.declare_parameter("status_topic", "/macrobot/camera_tf/status")

        path = Path(str(self.get_parameter("calibration_file").value)).expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError(f"camera TF calibration file not found: {path}")
        metadata, transforms = load_calibration(path)

        self.broadcaster = StaticTransformBroadcaster(self)
        messages: list[TransformStamped] = []
        now = self.get_clock().now().to_msg()
        for spec in transforms:
            msg = TransformStamped()
            msg.header.stamp = now
            msg.header.frame_id = spec.parent
            msg.child_frame_id = spec.child
            msg.transform.translation.x = spec.xyz[0]
            msg.transform.translation.y = spec.xyz[1]
            msg.transform.translation.z = spec.xyz[2]
            msg.transform.rotation.x = spec.quaternion_xyzw[0]
            msg.transform.rotation.y = spec.quaternion_xyzw[1]
            msg.transform.rotation.z = spec.quaternion_xyzw[2]
            msg.transform.rotation.w = spec.quaternion_xyzw[3]
            messages.append(msg)

        self.broadcaster.sendTransform(messages)

        qos = QoSProfile(depth=1)
        qos.reliability = ReliabilityPolicy.RELIABLE
        qos.durability = DurabilityPolicy.TRANSIENT_LOCAL
        self.status_pub = self.create_publisher(
            String, str(self.get_parameter("status_topic").value), qos
        )
        status = String()
        status.data = json.dumps(
            {
                "ok": True,
                "event": "camera_tf_published",
                "calibration_file": str(path),
                "transform_count": len(messages),
                "metadata": metadata,
                "children": [item.child_frame_id for item in messages],
            },
            ensure_ascii=False,
        )
        self.status_pub.publish(status)
        self.get_logger().info(status.data)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = RgbAnchorTfPublisher()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
