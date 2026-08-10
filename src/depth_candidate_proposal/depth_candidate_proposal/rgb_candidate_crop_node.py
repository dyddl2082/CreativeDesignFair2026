"""Match RGB frames to depth proposals and publish bounded JPEG crops on Pi."""

from __future__ import annotations

from collections import deque
import time
from typing import Deque, Optional, Sequence, Tuple

import rclpy
from cv_bridge import CvBridge, CvBridgeError
from macrobot_interfaces.msg import (
    DepthCandidate,
    DepthCandidateArray,
    RgbCandidateCrop,
)
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import CompressedImage, Image, RegionOfInterest

from .crop_core import (
    CropEncodingConfig,
    create_candidate_crop_mask,
    decode_binary_mask,
    encode_crop_mask_png,
    encode_jpeg_bounded,
    extract_crop,
    map_and_pad_roi,
)


def _stamp_to_nanoseconds(stamp) -> int:
    return int(stamp.sec) * 1_000_000_000 + int(stamp.nanosec)


class RgbCandidateCropNode(Node):
    """Create network-efficient RGB crops from frame-local depth candidates."""

    def __init__(self) -> None:
        super().__init__("rgb_candidate_crop")
        self._declare_parameters()

        self._bridge = CvBridge()
        buffer_size = max(int(self.get_parameter("color_buffer_size").value), 2)
        self._color_buffer: Deque[Image] = deque(maxlen=buffer_size)

        self._last_status_monotonic = 0.0
        self._last_sync_warning_monotonic = 0.0
        self._last_preview_monotonic = 0.0
        self._published_frames = 0
        self._published_crops = 0
        self._published_bytes = 0
        self._sync_drops = 0
        self._oversize_crops = 0

        color_topic = str(self.get_parameter("color_topic").value)
        candidate_topic = str(self.get_parameter("candidate_topic").value)
        crop_topic = str(self.get_parameter("crop_topic").value)
        preview_topic = str(self.get_parameter("top_crop_preview_topic").value)

        color_qos = QoSProfile(depth=10)
        color_qos.reliability = ReliabilityPolicy.BEST_EFFORT

        candidate_qos = QoSProfile(depth=5)
        candidate_qos.reliability = ReliabilityPolicy.RELIABLE

        crop_qos = QoSProfile(depth=2)
        crop_qos.reliability = (
            ReliabilityPolicy.RELIABLE
            if bool(self.get_parameter("reliable_crop_output").value)
            else ReliabilityPolicy.BEST_EFFORT
        )

        preview_qos = QoSProfile(depth=1)
        preview_qos.reliability = ReliabilityPolicy.BEST_EFFORT

        self._crop_publisher = self.create_publisher(
            RgbCandidateCrop,
            crop_topic,
            crop_qos,
        )
        self._preview_publisher = self.create_publisher(
            CompressedImage,
            preview_topic,
            preview_qos,
        )
        self._color_subscription = self.create_subscription(
            Image,
            color_topic,
            self._color_callback,
            color_qos,
        )
        self._candidate_subscription = self.create_subscription(
            DepthCandidateArray,
            candidate_topic,
            self._candidate_callback,
            candidate_qos,
        )

        reliability_text = (
            "reliable"
            if crop_qos.reliability == ReliabilityPolicy.RELIABLE
            else "best_effort"
        )
        self.get_logger().info(
            "RGB candidate crop node ready: "
            f"color='{color_topic}', candidates='{candidate_topic}', "
            f"output='{crop_topic}', qos={reliability_text}, "
            f"buffer={buffer_size} frames"
        )

    def _declare_parameters(self) -> None:
        defaults = {
            "color_topic": "/camera/camera/color/image_raw",
            "candidate_topic": "/depth_candidates/candidates",
            "crop_topic": "/depth_candidates/rgb_crops",
            "top_crop_preview_topic": "/depth_candidates/top_rgb_crop/compressed",
            "color_buffer_size": 45,
            "sync_tolerance_sec": 0.080,
            "allow_latest_color_fallback": False,
            "max_crops_per_frame": 6,
            "min_proposal_score": 0.0,
            "reject_border_candidates": False,
            "extra_padding_px": 0,
            "extra_padding_ratio": 0.0,
            "force_square_crop": False,
            "min_context_side_px": 0,
            "max_context_side_px": 0,
            "max_crop_side_px": 320,
            "min_crop_side_px": 32,
            "jpeg_quality": 70,
            "min_jpeg_quality": 35,
            "jpeg_quality_step": 8,
            "max_jpeg_bytes": 55_000,
            "jpeg_resize_factor": 0.80,
            "jpeg_max_resize_iterations": 6,
            "reliable_crop_output": False,
            "publish_foreground_mask": True,
            "mask_png_compression": 3,
            "publish_top_crop_preview": True,
            "top_crop_preview_hz": 1.0,
            "status_log_period_sec": 5.0,
        }
        for name, value in defaults.items():
            self.declare_parameter(name, value)

    def _color_callback(self, message: Image) -> None:
        self._color_buffer.append(message)

    def _encoding_config(self) -> CropEncodingConfig:
        get = lambda name: self.get_parameter(name).value
        return CropEncodingConfig(
            jpeg_quality=int(get("jpeg_quality")),
            min_jpeg_quality=int(get("min_jpeg_quality")),
            jpeg_quality_step=int(get("jpeg_quality_step")),
            max_jpeg_bytes=int(get("max_jpeg_bytes")),
            max_crop_side_px=int(get("max_crop_side_px")),
            min_crop_side_px=int(get("min_crop_side_px")),
            resize_factor=float(get("jpeg_resize_factor")),
            max_resize_iterations=int(get("jpeg_max_resize_iterations")),
        )

    def _find_color_frame(
        self,
        proposal_stamp,
    ) -> Tuple[Optional[Image], float, float]:
        """Return frame, signed delta seconds, and closest absolute delta."""
        if not self._color_buffer:
            return None, 0.0, float("inf")

        proposal_ns = _stamp_to_nanoseconds(proposal_stamp)
        if proposal_ns <= 0:
            return self._color_buffer[-1], 0.0, 0.0

        closest = min(
            self._color_buffer,
            key=lambda image: abs(
                _stamp_to_nanoseconds(image.header.stamp) - proposal_ns
            ),
        )
        signed_delta_sec = (
            _stamp_to_nanoseconds(closest.header.stamp) - proposal_ns
        ) / 1_000_000_000.0
        absolute_delta_sec = abs(signed_delta_sec)
        tolerance = max(
            float(self.get_parameter("sync_tolerance_sec").value),
            0.0,
        )
        if absolute_delta_sec <= tolerance:
            return closest, signed_delta_sec, absolute_delta_sec

        if bool(self.get_parameter("allow_latest_color_fallback").value):
            latest = self._color_buffer[-1]
            latest_delta = (
                _stamp_to_nanoseconds(latest.header.stamp) - proposal_ns
            ) / 1_000_000_000.0
            return latest, latest_delta, abs(latest_delta)
        return None, signed_delta_sec, absolute_delta_sec

    def _select_candidates(
        self,
        candidates: Sequence[DepthCandidate],
    ) -> list[DepthCandidate]:
        minimum_score = float(self.get_parameter("min_proposal_score").value)
        reject_border = bool(
            self.get_parameter("reject_border_candidates").value
        )
        selected = [
            candidate
            for candidate in candidates
            if candidate.proposal_score >= minimum_score
            and not (reject_border and candidate.touches_border)
        ]
        maximum = max(int(self.get_parameter("max_crops_per_frame").value), 1)
        return selected[:maximum]

    def _candidate_callback(self, message: DepthCandidateArray) -> None:
        start = time.perf_counter()
        now_monotonic = time.monotonic()

        if not message.candidates:
            self._log_status_if_due(
                now_monotonic,
                source_count=0,
                selected_count=0,
                published_count=0,
                frame_bytes=0,
                sync_delta_sec=0.0,
                elapsed_ms=(time.perf_counter() - start) * 1000.0,
            )
            return

        color_message, sync_delta_sec, closest_delta_sec = self._find_color_frame(
            message.header.stamp
        )
        if color_message is None:
            self._sync_drops += 1
            if now_monotonic - self._last_sync_warning_monotonic >= 5.0:
                self.get_logger().warning(
                    "No RGB frame within sync tolerance: "
                    f"closest={closest_delta_sec * 1000.0:.1f} ms, "
                    f"buffered={len(self._color_buffer)}. Increase "
                    "color_buffer_size if proposal processing latency is high."
                )
                self._last_sync_warning_monotonic = now_monotonic
            return

        try:
            color_bgr = self._bridge.imgmsg_to_cv2(
                color_message,
                desired_encoding="bgr8",
            )
            encoding_config = self._encoding_config()
            encoding_config.validate()
        except (CvBridgeError, ValueError) as error:
            self.get_logger().error(f"RGB crop preparation failed: {error}")
            return
        
        frame_mask = None

        if (
            bool(self.get_parameter("publish_foreground_mask").value)
            and message.foreground_mask_available
            and message.foreground_mask.data
        ):
            try:
                frame_mask = decode_binary_mask(
                    message.foreground_mask.data
                )
            except ValueError as error:
                self.get_logger().warning(
                    f"Foreground mask decode failed: {error}"
                )

        source_count = len(message.candidates)
        selected = self._select_candidates(message.candidates)
        selected_count = len(selected)
        frame_bytes = 0
        first_preview: Optional[CompressedImage] = None
        prepared = []

        proposal_width = int(message.image_width)
        proposal_height = int(message.image_height)
        color_height, color_width = color_bgr.shape[:2]
        if proposal_width <= 0 or proposal_height <= 0:
            self.get_logger().warning("Ignoring candidates with invalid image dimensions")
            return

        for candidate in selected:
            try:
                roi = map_and_pad_roi(
                    roi_x=int(candidate.roi.x_offset),
                    roi_y=int(candidate.roi.y_offset),
                    roi_width=int(candidate.roi.width),
                    roi_height=int(candidate.roi.height),
                    proposal_width=proposal_width,
                    proposal_height=proposal_height,
                    color_width=color_width,
                    color_height=color_height,
                    extra_padding_px=int(
                        self.get_parameter("extra_padding_px").value
                    ),
                    extra_padding_ratio=float(
                        self.get_parameter("extra_padding_ratio").value
                    ),
                    force_square_crop=bool(
                        self.get_parameter("force_square_crop").value
                    ),
                    min_context_side_px=int(
                        self.get_parameter("min_context_side_px").value
                    ),
                    max_context_side_px=int(
                        self.get_parameter("max_context_side_px").value
                    ),
                )
                crop_bgr = extract_crop(color_bgr, roi)
                encoded = encode_jpeg_bounded(crop_bgr, encoding_config)
                mask_data = b""
                mask_fill_ratio = 0.0
                mask_available = False

                if frame_mask is not None:
                    candidate_mask = create_candidate_crop_mask(
                        frame_mask=frame_mask,
                        roi=roi,
                        proposal_width=proposal_width,
                        proposal_height=proposal_height,
                        color_width=color_width,
                        color_height=color_height,
                        candidate_center_x=float(candidate.center_x),
                        candidate_center_y=float(candidate.center_y),
                    )

                    mask_data, mask_fill_ratio = encode_crop_mask_png(
                        candidate_mask,
                        target_width=encoded.width,
                        target_height=encoded.height,
                        compression=int(
                            self.get_parameter(
                                "mask_png_compression"
                            ).value
                        ),
                    )

                    mask_available = bool(mask_data)
            except (ValueError, RuntimeError) as error:
                self.get_logger().warning(
                    f"Skipping candidate {candidate.id}: {error}"
                )
                continue

            prepared.append(
                (
                    candidate,
                    roi,
                    encoded,
                    mask_available,
                    mask_fill_ratio,
                    mask_data,
                )
            )

        published_count = len(prepared)
        for crop_index, (
            candidate,
            roi,
            encoded,
            mask_available,
            mask_fill_ratio,
            mask_data,
        ) in enumerate(prepared):
            crop_message = RgbCandidateCrop()
            crop_message.proposal_header = message.header
            crop_message.proposal_image_width = proposal_width
            crop_message.proposal_image_height = proposal_height
            crop_message.color_image_width = color_width
            crop_message.color_image_height = color_height
            crop_message.source_candidate_count = source_count
            crop_message.frame_crop_count = published_count
            crop_message.crop_index = crop_index
            crop_message.candidate = candidate
            crop_message.crop_roi = RegionOfInterest(
                x_offset=roi.x,
                y_offset=roi.y,
                width=roi.width,
                height=roi.height,
                do_rectify=False,
            )
            crop_message.color_time_offset_sec = float(sync_delta_sec)
            crop_message.plane_found = bool(message.plane_found)

            crop_message.foreground_mask_available = bool(
                mask_available
            )
            crop_message.mask_fill_ratio = float(mask_fill_ratio)

            if mask_available:
                crop_message.foreground_mask.header = (
                    color_message.header
                )
                crop_message.foreground_mask.format = (
                    "mono8; png compressed"
                )
                crop_message.foreground_mask.data = mask_data
            crop_message.encoded_width = encoded.width
            crop_message.encoded_height = encoded.height
            crop_message.jpeg_size_bytes = len(encoded.data)
            crop_message.jpeg_quality = encoded.quality
            crop_message.size_limit_met = encoded.size_limit_met
            crop_message.image.header = color_message.header
            crop_message.image.format = "bgr8; jpeg compressed bgr8"
            crop_message.image.data = encoded.data
            self._crop_publisher.publish(crop_message)

            if first_preview is None:
                first_preview = CompressedImage()
                first_preview.header = color_message.header
                first_preview.format = crop_message.image.format
                first_preview.data = encoded.data

            frame_bytes += len(encoded.data)
            if not encoded.size_limit_met:
                self._oversize_crops += 1

        if published_count > 0:
            self._published_frames += 1
            self._published_crops += published_count
            self._published_bytes += frame_bytes
            self._publish_top_preview_if_due(first_preview, now_monotonic)

        self._log_status_if_due(
            now_monotonic,
            source_count=source_count,
            selected_count=selected_count,
            published_count=published_count,
            frame_bytes=frame_bytes,
            sync_delta_sec=sync_delta_sec,
            elapsed_ms=(time.perf_counter() - start) * 1000.0,
        )

    def _publish_top_preview_if_due(
        self,
        preview: Optional[CompressedImage],
        now_monotonic: float,
    ) -> None:
        if preview is None:
            return
        if not bool(self.get_parameter("publish_top_crop_preview").value):
            return
        preview_hz = max(
            float(self.get_parameter("top_crop_preview_hz").value),
            0.1,
        )
        if now_monotonic - self._last_preview_monotonic < 1.0 / preview_hz:
            return
        self._last_preview_monotonic = now_monotonic
        self._preview_publisher.publish(preview)

    def _log_status_if_due(
        self,
        now_monotonic: float,
        source_count: int,
        selected_count: int,
        published_count: int,
        frame_bytes: int,
        sync_delta_sec: float,
        elapsed_ms: float,
    ) -> None:
        period = max(
            float(self.get_parameter("status_log_period_sec").value),
            1.0,
        )
        if now_monotonic - self._last_status_monotonic < period:
            return
        self._last_status_monotonic = now_monotonic
        self.get_logger().info(
            f"source={source_count}, selected={selected_count}, "
            f"published={published_count}, frame={frame_bytes / 1024.0:.1f} KiB, "
            f"sync={sync_delta_sec * 1000.0:+.1f} ms, "
            f"processing={elapsed_ms:.1f} ms, "
            f"totals(frames/crops/drops/oversize)="
            f"{self._published_frames}/{self._published_crops}/"
            f"{self._sync_drops}/{self._oversize_crops}"
        )


def main(args=None) -> None:
    """Run the RGB candidate crop node."""
    rclpy.init(args=args)
    node = RgbCandidateCropNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
