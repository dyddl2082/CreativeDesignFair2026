#!/usr/bin/env python3

import json
import time
from pathlib import Path

import rclpy
from rclpy.node import Node
from rclpy.qos import (
    QoSProfile,
    QoSReliabilityPolicy,
    QoSDurabilityPolicy,
    QoSHistoryPolicy,
)

from macrobot_interfaces.msg import DepthCandidateArray


class CandidateSaver(Node):
    def __init__(self):
        super().__init__("debug_depth_candidate_saver")

        self.declare_parameter("topic", "/depth_candidates/candidates")
        self.declare_parameter(
            "output_dir",
            str(Path.home() / "MacRobot/debug/depth_candidates"),
        )
        self.declare_parameter("max_frames", 20)

        self.topic = self.get_parameter("topic").value
        self.output_dir = Path(self.get_parameter("output_dir").value)
        self.max_frames = int(self.get_parameter("max_frames").value)

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        self.output_dir = self.output_dir / timestamp
        self.output_dir.mkdir(parents=True, exist_ok=True)

        qos = QoSProfile(
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=10,
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            durability=QoSDurabilityPolicy.VOLATILE,
        )

        self.count = 0

        self.sub = self.create_subscription(
            DepthCandidateArray,
            self.topic,
            self.callback,
            qos,
        )

        self.get_logger().info(f"Saving candidates from {self.topic}")
        self.get_logger().info(f"Output directory: {self.output_dir}")

    def _roi_to_dict(self, roi):
        return {
            "x_offset": int(roi.x_offset),
            "y_offset": int(roi.y_offset),
            "width": int(roi.width),
            "height": int(roi.height),
        }

    def callback(self, msg: DepthCandidateArray):
        self.count += 1

        candidates = []

        for c in msg.candidates:
            item = {
                "id": int(getattr(c, "id", -1)),
                "roi": self._roi_to_dict(c.roi),
                "median_depth_m": float(getattr(c, "median_depth_m", 0.0)),
                "mean_depth_m": float(getattr(c, "mean_depth_m", 0.0)),
                "depth_std_m": float(getattr(c, "depth_std_m", 0.0)),
                "proposal_score": float(getattr(c, "proposal_score", 0.0)),
                "area_px": int(
                    int(c.roi.width) * int(c.roi.height)
                ),
            }

            for name in [
                "foreground_height_valid",
                "touches_border",
                "fill_ratio",
                "solidity",
                "edge_density",
            ]:
                if hasattr(c, name):
                    value = getattr(c, name)
                    if isinstance(value, bool):
                        item[name] = bool(value)
                    else:
                        try:
                            item[name] = float(value)
                        except Exception:
                            item[name] = str(value)

            candidates.append(item)

        candidates.sort(
            key=lambda x: x.get("proposal_score", 0.0),
            reverse=True,
        )

        data = {
            "frame": self.count,
            "stamp": {
                "sec": int(msg.header.stamp.sec),
                "nanosec": int(msg.header.stamp.nanosec),
            },
            "candidate_count": len(candidates),
            "candidates": candidates,
        }

        path = self.output_dir / f"candidates_{self.count:04d}.json"

        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        self.get_logger().info(
            f"[{self.count}/{self.max_frames}] "
            f"saved {len(candidates)} candidates"
        )

        if self.count >= self.max_frames:
            rclpy.shutdown()


def main():
    rclpy.init()
    node = CandidateSaver()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
