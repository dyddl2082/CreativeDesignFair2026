"""Publish a conservative forward-clearance estimate from aligned depth.

No additional sensor is required.  The estimate is used only to gate short
forward search/approach chunks; it is not a replacement for a full obstacle
map or certified collision avoidance.
"""

from __future__ import annotations

import json
import math
import time
from typing import Optional

import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import Image
from std_msgs.msg import String

from .depth_clearance_core import estimate_clearance


class DepthClearanceNode(Node):
    def __init__(self) -> None:
        super().__init__("macrobot_depth_clearance")
        defaults = {
            "input_topic": "/camera/camera/aligned_depth_to_color/image_raw",
            "output_topic": "/macrobot/perception/forward_clearance",
            "width_fraction": 0.28,
            "y_min_fraction": 0.35,
            "y_max_fraction": 0.82,
            "minimum_depth_m": 0.05,
            "maximum_depth_m": 4.0,
            "percentile": 10.0,
            "minimum_valid_fraction": 0.05,
            "publish_hz": 10.0,
        }
        for name, value in defaults.items():
            self.declare_parameter(name, value)

        qos = QoSProfile(depth=2)
        qos.reliability = ReliabilityPolicy.BEST_EFFORT
        self.publisher = self.create_publisher(
            String, str(self.get_parameter("output_topic").value), 10
        )
        self.subscription = self.create_subscription(
            Image,
            str(self.get_parameter("input_topic").value),
            self._callback,
            qos,
        )
        self.last_publish = 0.0
        self.get_logger().info(
            "Depth clearance ready: aligned-depth central corridor -> forward clearance"
        )

    @staticmethod
    def _stamp_sec(message: Image) -> float:
        stamp = message.header.stamp
        value = float(stamp.sec) + float(stamp.nanosec) * 1e-9
        return value if value > 0.0 else time.time()

    @staticmethod
    def _decode(message: Image) -> Optional[np.ndarray]:
        encoding = str(message.encoding).strip().upper()
        height = int(message.height)
        width = int(message.width)
        step = int(message.step)
        if height <= 0 or width <= 0 or step <= 0:
            return None
        raw = memoryview(message.data)
        if encoding in {"16UC1", "MONO16", "TYPE_16UC1"}:
            itemsize = 2
            if len(raw) < height * step:
                return None
            rows = np.frombuffer(raw, dtype=np.uint16, count=height * (step // itemsize))
            rows = rows.reshape(height, step // itemsize)[:, :width]
            if bool(message.is_bigendian):
                rows = rows.byteswap()
            return rows.astype(np.float32) * 0.001
        if encoding in {"32FC1", "TYPE_32FC1"}:
            itemsize = 4
            if len(raw) < height * step:
                return None
            rows = np.frombuffer(raw, dtype=np.float32, count=height * (step // itemsize))
            rows = rows.reshape(height, step // itemsize)[:, :width]
            if bool(message.is_bigendian):
                rows = rows.byteswap()
            return rows.astype(np.float32, copy=False)
        return None

    def _callback(self, message: Image) -> None:
        now = time.monotonic()
        period = 1.0 / max(0.2, float(self.get_parameter("publish_hz").value))
        if now - self.last_publish < period:
            return
        self.last_publish = now
        depth = self._decode(message)
        if depth is None:
            estimate = None
            payload = {
                "event": "forward_clearance",
                "ok": False,
                "available": False,
                "reason": f"unsupported_or_invalid_depth_encoding:{message.encoding}",
                "stamp_sec": self._stamp_sec(message),
                "published_at_sec": time.time(),
            }
        else:
            estimate = estimate_clearance(
                depth,
                width_fraction=float(self.get_parameter("width_fraction").value),
                y_min_fraction=float(self.get_parameter("y_min_fraction").value),
                y_max_fraction=float(self.get_parameter("y_max_fraction").value),
                minimum_depth_m=float(self.get_parameter("minimum_depth_m").value),
                maximum_depth_m=float(self.get_parameter("maximum_depth_m").value),
                percentile=float(self.get_parameter("percentile").value),
                minimum_valid_fraction=float(
                    self.get_parameter("minimum_valid_fraction").value
                ),
            )
            payload = {
                "event": "forward_clearance",
                "ok": estimate.available,
                "available": estimate.available,
                "clearance_m": estimate.clearance_m,
                "valid_fraction": estimate.valid_fraction,
                "sample_count": estimate.sample_count,
                "reason": estimate.reason,
                "stamp_sec": self._stamp_sec(message),
                "published_at_sec": time.time(),
            }
        out = String()
        out.data = json.dumps(payload, ensure_ascii=False)
        self.publisher.publish(out)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = DepthClearanceNode()
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
