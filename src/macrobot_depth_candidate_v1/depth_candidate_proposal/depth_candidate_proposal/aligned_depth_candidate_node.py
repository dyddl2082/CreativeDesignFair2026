"""ROS 2 node that generates lightweight object proposals on Raspberry Pi."""

from __future__ import annotations

import time
from typing import Optional

import cv2
import numpy as np
import rclpy
from cv_bridge import CvBridge, CvBridgeError
from macrobot_interfaces.msg import DepthCandidate, DepthCandidateArray
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, qos_profile_sensor_data
from sensor_msgs.msg import CameraInfo, CompressedImage, Image, RegionOfInterest

from .proposal_core import (
    CameraIntrinsics,
    ProposalConfig,
    depth_image_to_meters,
    generate_depth_proposals,
    make_debug_image,
)


class AlignedDepthCandidateNode(Node):
    """Generate depth proposals and publish only small metadata over Wi-Fi."""

    def __init__(self) -> None:
        super().__init__("aligned_depth_candidate")
        self._declare_parameters()

        self._bridge = CvBridge()
        self._intrinsics: Optional[CameraIntrinsics] = None
        self._last_process_monotonic = 0.0
        self._last_debug_monotonic = 0.0
        self._last_status_monotonic = 0.0
        self._warned_missing_intrinsics = False

        self._depth_topic = str(self.get_parameter("depth_topic").value)
        self._camera_info_topic = str(self.get_parameter("camera_info_topic").value)
        candidate_topic = str(self.get_parameter("candidate_topic").value)
        debug_topic = str(self.get_parameter("debug_topic").value)

        candidate_qos = QoSProfile(depth=5)
        candidate_qos.reliability = ReliabilityPolicy.RELIABLE
        self._candidate_publisher = self.create_publisher(
            DepthCandidateArray,
            candidate_topic,
            candidate_qos,
        )
        self._debug_publisher = self.create_publisher(
            CompressedImage,
            debug_topic,
            qos_profile_sensor_data,
        )

        self._camera_info_subscription = self.create_subscription(
            CameraInfo,
            self._camera_info_topic,
            self._camera_info_callback,
            qos_profile_sensor_data,
        )
        self._depth_subscription = self.create_subscription(
            Image,
            self._depth_topic,
            self._depth_callback,
            qos_profile_sensor_data,
        )

        self.get_logger().info(
            "Aligned-depth candidate node ready: "
            f"depth='{self._depth_topic}', camera_info='{self._camera_info_topic}', "
            f"output='{candidate_topic}'"
        )

    def _declare_parameters(self) -> None:
        defaults = {
            "depth_topic": "/camera/camera/aligned_depth_to_color/image_raw",
            "camera_info_topic": "/camera/camera/color/camera_info",
            "candidate_topic": "/depth_candidates/candidates",
            "debug_topic": "/depth_candidates/debug/compressed",
            "process_hz": 5.0,
            "depth_scale_m": 0.001,
            "publish_debug": True,
            "debug_hz": 2.0,
            "debug_jpeg_quality": 72,
            "min_depth_m": 0.18,
            "max_depth_m": 1.50,
            "enable_plane_removal": True,
            "plane_sample_stride": 4,
            "plane_ransac_iterations": 70,
            "plane_distance_threshold_m": 0.012,
            "plane_min_inlier_ratio": 0.25,
            "plane_clearance_m": 0.025,
            "plane_max_foreground_m": 0.60,
            "max_plane_samples": 16000,
            "fallback_background_percentile": 70.0,
            "fallback_clearance_m": 0.035,
            "roi_top_ratio": 0.00,
            "roi_bottom_ratio": 1.00,
            "roi_left_ratio": 0.00,
            "roi_right_ratio": 1.00,
            "close_kernel_px": 9,
            "open_kernel_px": 3,
            "min_component_area_px": 300,
            "max_component_area_ratio": 0.28,
            "min_bbox_width_px": 14,
            "min_bbox_height_px": 14,
            "min_fill_ratio": 0.10,
            "min_valid_depth_ratio": 0.55,
            "bbox_padding_px": 8,
            "border_margin_px": 2,
            "reject_border_components": False,
            "max_candidates": 12,
            "depth_std_score_scale_m": 0.060,
            "random_seed": 17,
        }
        for name, value in defaults.items():
            self.declare_parameter(name, value)

    def _build_config(self) -> ProposalConfig:
        get = lambda name: self.get_parameter(name).value
        return ProposalConfig(
            min_depth_m=float(get("min_depth_m")),
            max_depth_m=float(get("max_depth_m")),
            enable_plane_removal=bool(get("enable_plane_removal")),
            plane_sample_stride=int(get("plane_sample_stride")),
            plane_ransac_iterations=int(get("plane_ransac_iterations")),
            plane_distance_threshold_m=float(get("plane_distance_threshold_m")),
            plane_min_inlier_ratio=float(get("plane_min_inlier_ratio")),
            plane_clearance_m=float(get("plane_clearance_m")),
            plane_max_foreground_m=float(get("plane_max_foreground_m")),
            max_plane_samples=int(get("max_plane_samples")),
            fallback_background_percentile=float(get("fallback_background_percentile")),
            fallback_clearance_m=float(get("fallback_clearance_m")),
            roi_top_ratio=float(get("roi_top_ratio")),
            roi_bottom_ratio=float(get("roi_bottom_ratio")),
            roi_left_ratio=float(get("roi_left_ratio")),
            roi_right_ratio=float(get("roi_right_ratio")),
            close_kernel_px=int(get("close_kernel_px")),
            open_kernel_px=int(get("open_kernel_px")),
            min_component_area_px=int(get("min_component_area_px")),
            max_component_area_ratio=float(get("max_component_area_ratio")),
            min_bbox_width_px=int(get("min_bbox_width_px")),
            min_bbox_height_px=int(get("min_bbox_height_px")),
            min_fill_ratio=float(get("min_fill_ratio")),
            min_valid_depth_ratio=float(get("min_valid_depth_ratio")),
            bbox_padding_px=int(get("bbox_padding_px")),
            border_margin_px=int(get("border_margin_px")),
            reject_border_components=bool(get("reject_border_components")),
            max_candidates=int(get("max_candidates")),
            depth_std_score_scale_m=float(get("depth_std_score_scale_m")),
            random_seed=int(get("random_seed")),
        )

    def _camera_info_callback(self, message: CameraInfo) -> None:
        if message.width <= 0 or message.height <= 0 or len(message.k) < 9:
            self.get_logger().warning("Ignoring invalid CameraInfo message")
            return
        fx = float(message.k[0])
        fy = float(message.k[4])
        cx = float(message.k[2])
        cy = float(message.k[5])
        if fx <= 0.0 or fy <= 0.0:
            self.get_logger().warning("Ignoring CameraInfo with non-positive focal length")
            return
        self._intrinsics = CameraIntrinsics(
            width=int(message.width),
            height=int(message.height),
            fx=fx,
            fy=fy,
            cx=cx,
            cy=cy,
        )
        self._warned_missing_intrinsics = False

    def _depth_callback(self, message: Image) -> None:
        process_hz = max(float(self.get_parameter("process_hz").value), 0.1)
        now_monotonic = time.monotonic()
        if now_monotonic - self._last_process_monotonic < 1.0 / process_hz:
            return
        self._last_process_monotonic = now_monotonic
        start = time.perf_counter()

        try:
            depth_cv = self._bridge.imgmsg_to_cv2(message, desired_encoding="passthrough")
            depth_m = depth_image_to_meters(
                np.asarray(depth_cv),
                message.encoding,
                float(self.get_parameter("depth_scale_m").value),
            )
            config = self._build_config()
            if config.enable_plane_removal and self._intrinsics is None:
                if not self._warned_missing_intrinsics:
                    self.get_logger().warning(
                        "No color CameraInfo received yet; using percentile "
                        "fallback until it arrives."
                    )
                    self._warned_missing_intrinsics = True
            result = generate_depth_proposals(depth_m, self._intrinsics, config)
        except (CvBridgeError, ValueError, RuntimeError) as error:
            self.get_logger().error(f"Depth proposal processing failed: {error}")
            return

        output = DepthCandidateArray()
        output.header = message.header
        output.image_width = int(message.width)
        output.image_height = int(message.height)
        output.plane_found = result.plane is not None
        if result.plane is not None:
            output.plane_inlier_ratio = float(result.plane.inlier_ratio)
            output.plane_coefficients = [
                float(value) for value in result.plane.coefficients
            ]
        else:
            output.plane_inlier_ratio = 0.0
            output.plane_coefficients = [0.0, 0.0, 0.0, 0.0]

        for candidate_id, data in enumerate(result.candidates):
            candidate = DepthCandidate()
            candidate.id = candidate_id
            candidate.roi = RegionOfInterest(
                x_offset=int(data.roi_x),
                y_offset=int(data.roi_y),
                height=int(data.roi_height),
                width=int(data.roi_width),
                do_rectify=False,
            )
            candidate.center_x = float(data.center_x)
            candidate.center_y = float(data.center_y)
            candidate.median_depth_m = float(data.median_depth_m)
            candidate.near_depth_m = float(data.near_depth_m)
            candidate.far_depth_m = float(data.far_depth_m)
            candidate.depth_std_m = float(data.depth_std_m)
            candidate.valid_depth_ratio = float(data.valid_depth_ratio)
            candidate.fill_ratio = float(data.fill_ratio)
            candidate.area_ratio = float(data.area_ratio)
            candidate.foreground_height_m = float(data.foreground_height_m)
            candidate.proposal_score = float(data.proposal_score)
            candidate.touches_border = bool(data.touches_border)
            output.candidates.append(candidate)

        self._candidate_publisher.publish(output)
        self._publish_debug_if_due(message, depth_m, result, config, now_monotonic)

        if now_monotonic - self._last_status_monotonic >= 5.0:
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            plane_text = (
                f"yes/{result.plane.inlier_ratio:.2f}"
                if result.plane is not None
                else "no"
            )
            self.get_logger().info(
                f"candidates={len(result.candidates)}, plane={plane_text}, "
                f"processing={elapsed_ms:.1f} ms"
            )
            self._last_status_monotonic = now_monotonic

    def _publish_debug_if_due(
        self,
        source_message: Image,
        depth_m: np.ndarray,
        result,
        config: ProposalConfig,
        now_monotonic: float,
    ) -> None:
        if not bool(self.get_parameter("publish_debug").value):
            return
        debug_hz = max(float(self.get_parameter("debug_hz").value), 0.1)
        if now_monotonic - self._last_debug_monotonic < 1.0 / debug_hz:
            return
        self._last_debug_monotonic = now_monotonic

        preview = make_debug_image(depth_m, result, config)
        requested_quality = int(self.get_parameter("debug_jpeg_quality").value)
        quality = int(np.clip(requested_quality, 20, 95))
        success, encoded = cv2.imencode(
            ".jpg",
            preview,
            [int(cv2.IMWRITE_JPEG_QUALITY), quality],
        )
        if not success:
            self.get_logger().warning("Failed to encode depth debug image")
            return

        debug_message = CompressedImage()
        debug_message.header = source_message.header
        debug_message.format = "jpeg"
        debug_message.data = encoded.tobytes()
        self._debug_publisher.publish(debug_message)


def main(args=None) -> None:
    """Run the aligned-depth candidate node."""
    rclpy.init(args=args)
    node = AlignedDepthCandidateNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
