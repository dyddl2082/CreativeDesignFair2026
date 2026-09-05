from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import time

import rclpy
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.time import Time
from tf2_ros import Buffer, TransformException, TransformListener
import yaml

from .calibration_schema import (
    TransformSpec,
    as_yaml_mapping,
    compose_transforms,
    quaternion_from_rpy,
)



class CaptureNode(Node):
    """Capture factory RealSense TFs and re-anchor them at the RGB body frame.

    Run the RealSense wrapper temporarily with a non-conflicting camera name,
    normally ``calib_camera``, and with ``publish_tf:=true``.  The CAD frame
    ``camera_link`` is assumed to be located at and oriented like the wrapper's
    ``<source_camera_name>_color_frame``.
    """

    def __init__(self) -> None:
        super().__init__("macrobot_capture_realsense_rgb_anchor")
        defaults = {
            "output_file": "~/MacRobot/data/camera_tf/d435_rgb_anchor.yaml",
            "source_camera_name": "calib_camera",
            "target_camera_name": "camera",
            "urdf_anchor_frame": "camera_link",
            "timeout_sec": 25.0,
            "poll_period_sec": 0.20,
            "require_infra_frames": False,
            "anchor_color_roll": 0.0,
            "anchor_color_pitch": 0.0,
            "anchor_color_yaw": 0.0,
        }
        for name, value in defaults.items():
            self.declare_parameter(name, value)

        self.output_file = Path(
            str(self.get_parameter("output_file").value)
        ).expanduser().resolve()
        self.source_name = str(self.get_parameter("source_camera_name").value).strip()
        self.target_name = str(self.get_parameter("target_camera_name").value).strip()
        self.anchor_frame = str(self.get_parameter("urdf_anchor_frame").value).strip()
        self.timeout_sec = float(self.get_parameter("timeout_sec").value)
        self.require_infra = bool(self.get_parameter("require_infra_frames").value)
        self.anchor_color_rpy = (
            float(self.get_parameter("anchor_color_roll").value),
            float(self.get_parameter("anchor_color_pitch").value),
            float(self.get_parameter("anchor_color_yaw").value),
        )
        poll = max(0.05, float(self.get_parameter("poll_period_sec").value))

        if not self.source_name or not self.target_name or not self.anchor_frame:
            raise ValueError("source_camera_name, target_camera_name and urdf_anchor_frame are required")

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.started = time.monotonic()
        self.timer = self.create_timer(poll, self._try_capture)
        self.completed = False

        self.get_logger().info(
            "Waiting for RealSense TF tree; RGB anchor is "
            f"{self.source_name}_color_frame and output is {self.output_file}"
        )

    def _lookup(self, parent: str, child: str) -> TransformSpec:
        value = self.tf_buffer.lookup_transform(
            parent,
            child,
            Time(),
            timeout=Duration(seconds=0.15),
        )
        t = value.transform.translation
        q = value.transform.rotation
        return TransformSpec(
            parent=parent,
            child=child,
            xyz=(float(t.x), float(t.y), float(t.z)),
            quaternion_xyzw=(float(q.x), float(q.y), float(q.z), float(q.w)),
        )

    def _rename(self, frame: str) -> str:
        source_prefix = self.source_name + "_"
        if not frame.startswith(source_prefix):
            raise ValueError(f"source frame does not start with {source_prefix}: {frame}")
        return self.target_name + "_" + frame[len(source_prefix):]

    def _capture_pair(
        self,
        source_parent: str,
        source_child: str,
        target_parent: str,
        target_child: str,
    ) -> TransformSpec:
        captured = self._lookup(source_parent, source_child)
        return TransformSpec(
            parent=target_parent,
            child=target_child,
            xyz=captured.xyz,
            quaternion_xyzw=captured.quaternion_xyzw,
        )

    def _try_capture(self) -> None:
        if self.completed:
            return

        source_color = f"{self.source_name}_color_frame"
        target_color = f"{self.target_name}_color_frame"
        target_color_optical = f"{self.target_name}_color_optical_frame"

        anchor_to_color = TransformSpec(
            parent=self.anchor_frame,
            child=target_color,
            xyz=(0.0, 0.0, 0.0),
            quaternion_xyzw=quaternion_from_rpy(*self.anchor_color_rpy),
        )
        transforms: list[TransformSpec] = [anchor_to_color]

        missing: list[str] = []
        try:
            transforms.append(
                self._capture_pair(
                    source_color,
                    f"{self.source_name}_color_optical_frame",
                    target_color,
                    target_color_optical,
                )
            )
            source_color_to_depth = self._lookup(
                source_color, f"{self.source_name}_depth_frame"
            )
            transforms.append(
                compose_transforms(
                    anchor_to_color,
                    source_color_to_depth,
                    parent=self.anchor_frame,
                    child=f"{self.target_name}_depth_frame",
                )
            )
            transforms.append(
                self._capture_pair(
                    f"{self.source_name}_depth_frame",
                    f"{self.source_name}_depth_optical_frame",
                    f"{self.target_name}_depth_frame",
                    f"{self.target_name}_depth_optical_frame",
                )
            )
        except TransformException as error:
            missing.append(str(error))

        if missing:
            if time.monotonic() - self.started < self.timeout_sec:
                return
            self.get_logger().error(
                "Required color/depth TFs were not available before timeout: " + "; ".join(missing)
            )
            self.completed = True
            rclpy.shutdown()
            return

        optional_missing: list[str] = []
        for stream in ("infra1", "infra2"):
            source_stream_frame = f"{self.source_name}_{stream}_frame"
            target_stream_frame = f"{self.target_name}_{stream}_frame"
            try:
                source_color_to_stream = self._lookup(source_color, source_stream_frame)
                transforms.append(
                    compose_transforms(
                        anchor_to_color,
                        source_color_to_stream,
                        parent=self.anchor_frame,
                        child=target_stream_frame,
                    )
                )
                transforms.append(
                    self._capture_pair(
                        source_stream_frame,
                        f"{self.source_name}_{stream}_optical_frame",
                        target_stream_frame,
                        f"{self.target_name}_{stream}_optical_frame",
                    )
                )
            except TransformException:
                optional_missing.append(source_stream_frame)

        if self.require_infra and optional_missing:
            if time.monotonic() - self.started < self.timeout_sec:
                return
            self.get_logger().error(
                "Infra TFs were required but unavailable: " + ", ".join(optional_missing)
            )
            self.completed = True
            rclpy.shutdown()
            return

        metadata = {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "source_camera_name": self.source_name,
            "source_rgb_anchor_frame": source_color,
            "target_camera_name": self.target_name,
            "urdf_anchor_frame": self.anchor_frame,
            "anchor_assumption": (
                "URDF camera_link origin is at the RGB lens center.  The configured "
                "anchor_color_rpy rotates camera_link into the RealSense color_frame body axes."
            ),
            "anchor_color_rpy_rad": [float(value) for value in self.anchor_color_rpy],
            "optional_frames_missing": optional_missing,
            "runtime_requirement": "launch RealSense with publish_tf=false",
        }
        root = as_yaml_mapping(metadata=metadata, transforms=transforms)
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        self.output_file.write_text(
            yaml.safe_dump(root, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        self.get_logger().info(
            f"Captured {len(transforms)} static transforms to {self.output_file}"
        )
        if optional_missing:
            self.get_logger().warning(
                "Optional infrared frames were not captured: " + ", ".join(optional_missing)
            )
        self.completed = True
        rclpy.shutdown()


def main(args=None) -> None:
    rclpy.init(args=args)
    node = CaptureNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
