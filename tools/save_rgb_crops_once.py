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

from macrobot_interfaces.msg import RgbCandidateCrop


class CropSaver(Node):
    def __init__(self):
        super().__init__("debug_rgb_crop_saver")

        self.declare_parameter("topic", "/depth_candidates/rgb_crops")
        self.declare_parameter("output_dir", str(Path.home() / "MacRobot/debug/rgb_crops"))
        self.declare_parameter("max_crops", 30)

        self.topic = self.get_parameter("topic").value
        self.output_dir = Path(self.get_parameter("output_dir").value)
        self.max_crops = int(self.get_parameter("max_crops").value)

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
            RgbCandidateCrop,
            self.topic,
            self.callback,
            qos,
        )

        self.get_logger().info(f"Saving crops from {self.topic}")
        self.get_logger().info(f"Output directory: {self.output_dir}")
        self.get_logger().info(f"Will stop after {self.max_crops} crops")

    def callback(self, msg: RgbCandidateCrop):
        self.count += 1

        candidate_id = getattr(msg.candidate, "id", self.count)
        score = getattr(msg.candidate, "proposal_score", 0.0)
        depth_m = getattr(msg.candidate, "median_depth_m", 0.0)

        stem = (
            f"crop_{self.count:04d}"
            f"_cand{candidate_id}"
            f"_score{score:.3f}"
            f"_depth{depth_m:.3f}"
        )

        image_path = self.output_dir / f"{stem}.jpg"
        meta_path = self.output_dir / f"{stem}.json"

        with image_path.open("wb") as f:
            f.write(bytes(msg.image.data))

        metadata = {
            "count": self.count,
            "candidate_id": int(candidate_id),
            "proposal_score": float(score),
            "median_depth_m": float(depth_m),
            "color_time_offset_sec": float(msg.color_time_offset_sec),
            "jpeg_size_bytes": int(msg.jpeg_size_bytes),
            "jpeg_quality": int(msg.jpeg_quality),
            "size_limit_met": bool(msg.size_limit_met),
            "encoded_width": int(msg.encoded_width),
            "encoded_height": int(msg.encoded_height),
            "frame_crop_count": int(msg.frame_crop_count),
            "crop_index": int(msg.crop_index),
            "crop_roi": {
                "x_offset": int(msg.crop_roi.x_offset),
                "y_offset": int(msg.crop_roi.y_offset),
                "width": int(msg.crop_roi.width),
                "height": int(msg.crop_roi.height),
            },
            "candidate_roi": {
                "x_offset": int(msg.candidate.roi.x_offset),
                "y_offset": int(msg.candidate.roi.y_offset),
                "width": int(msg.candidate.roi.width),
                "height": int(msg.candidate.roi.height),
            },
        }

        with meta_path.open("w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        self.get_logger().info(f"[{self.count}/{self.max_crops}] saved {image_path.name}")

        if self.count >= self.max_crops:
            self.get_logger().info("Done")
            rclpy.shutdown()


def main():
    rclpy.init()
    node = CropSaver()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
