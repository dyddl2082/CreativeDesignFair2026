"""ROS 2 node that filters Raspberry Pi RGB candidate crops on the PC."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import json
import math
import time
from typing import Optional, Tuple

import cv2
from macrobot_interfaces.msg import (
    CandidateFilterResult,
    FilteredCandidateCrop,
    RgbCandidateCrop,
)
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import CameraInfo, CompressedImage
from std_msgs.msg import String
from std_srvs.srv import Trigger

from .filter_core import (
    CandidateMeasurements,
    FilterConfig,
    FilterEvaluation,
    ImageFeatures,
    ReferenceProfile,
    compute_image_features,
    decode_compressed_image,
    evaluate_candidate,
    load_reference_profile,
    decode_compressed_mask,
)


class CandidateFilterNode(Node):
    """Apply generic hard filters and target-aware soft scores on WSL2."""

    def __init__(self) -> None:
        super().__init__("candidate_filter")
        self._declare_parameters()

        self._target_object = str(self.get_parameter("target_object").value).strip()
        self._profile: Optional[ReferenceProfile] = None
        self._camera_info: Optional[CameraInfo] = None
        self._last_debug_monotonic = 0.0
        self._last_status_monotonic = 0.0
        self._received = 0
        self._accepted = 0
        self._rejected = 0
        self._decode_failures = 0
        self._published_bytes = 0
        self._reject_reasons: Counter[str] = Counter()
        self._last_result_summary = "not_started"

        initial_config = self._filter_config()
        initial_config.validate()

        input_qos = QoSProfile(depth=4)
        input_qos.reliability = ReliabilityPolicy.BEST_EFFORT
        camera_qos = QoSProfile(depth=1)
        camera_qos.reliability = ReliabilityPolicy.BEST_EFFORT
        result_qos = QoSProfile(depth=20)
        result_qos.reliability = ReliabilityPolicy.RELIABLE
        accepted_qos = QoSProfile(depth=2)
        accepted_qos.reliability = (
            ReliabilityPolicy.RELIABLE
            if bool(self.get_parameter("reliable_accepted_output").value)
            else ReliabilityPolicy.BEST_EFFORT
        )
        debug_qos = QoSProfile(depth=1)
        debug_qos.reliability = ReliabilityPolicy.BEST_EFFORT
        status_qos = QoSProfile(depth=1)
        status_qos.reliability = ReliabilityPolicy.RELIABLE

        input_topic = str(self.get_parameter("input_crop_topic").value)
        camera_info_topic = str(self.get_parameter("camera_info_topic").value)
        target_topic = str(self.get_parameter("target_topic").value)
        result_topic = str(self.get_parameter("result_topic").value)
        accepted_topic = str(self.get_parameter("accepted_topic").value)
        debug_topic = str(self.get_parameter("debug_topic").value)
        status_topic = str(self.get_parameter("status_topic").value)
        reload_service = str(self.get_parameter("reload_service").value)

        self._result_publisher = self.create_publisher(
            CandidateFilterResult, result_topic, result_qos
        )
        self._accepted_publisher = self.create_publisher(
            FilteredCandidateCrop, accepted_topic, accepted_qos
        )
        self._debug_publisher = self.create_publisher(
            CompressedImage, debug_topic, debug_qos
        )
        self._status_publisher = self.create_publisher(String, status_topic, status_qos)

        self._crop_subscription = self.create_subscription(
            RgbCandidateCrop, input_topic, self._crop_callback, input_qos
        )
        self._camera_info_subscription = self.create_subscription(
            CameraInfo,
            camera_info_topic,
            self._camera_info_callback,
            camera_qos,
        )
        self._target_subscription = self.create_subscription(
            String, target_topic, self._target_callback, result_qos
        )
        self._reload_service = self.create_service(
            Trigger, reload_service, self._reload_profile_service
        )

        reload_period = float(self.get_parameter("profile_reload_period_sec").value)
        self._reload_timer = None
        if reload_period > 0.0:
            self._reload_timer = self.create_timer(
                max(reload_period, 1.0), self._periodic_profile_reload
            )

        self._reload_profile(log_result=True)
        accepted_reliability = (
            "reliable"
            if accepted_qos.reliability == ReliabilityPolicy.RELIABLE
            else "best_effort"
        )
        self.get_logger().info(
            "Candidate filter ready: "
            f"input='{input_topic}', results='{result_topic}', "
            f"accepted='{accepted_topic}' ({accepted_reliability}), "
            f"target='{self._target_object}', "
            f"soft_enforcement={initial_config.enforce_soft_score}"
        )

    def _declare_parameters(self) -> None:
        defaults = {
            "input_crop_topic": "/depth_candidates/rgb_crops",
            "camera_info_topic": "/camera/camera/color/camera_info",
            "target_topic": "/candidate_filter/target",
            "result_topic": "/candidate_filter/results",
            "accepted_topic": "/candidate_filter/accepted_crops",
            "debug_topic": "/candidate_filter/debug/compressed",
            "status_topic": "/candidate_filter/status",
            "reload_service": "/candidate_filter/reload_profile",
            "target_object": "Buds3",
            "object_root": "~/MacRobot/data/curated/objects",
            "reference_dir": "",
            "max_reference_images": 64,
            "profile_reload_period_sec": 0.0,
            "analysis_long_side_px": 192,
            "color_hist_bins": 16,
            "color_mask_ratio": 0.84,
            "color_top_k": 3,
            "canny_low_threshold": 60,
            "canny_high_threshold": 160,
            "min_crop_side_px": 32,
            "min_crop_area_px": 1024,
            "min_depth_m": 0.18,
            "max_depth_m": 1.50,
            "preferred_depth_min_m": 0.25,
            "preferred_depth_max_m": 1.00,
            "min_valid_depth_ratio": 0.35,
            "valid_depth_good_ratio": 0.85,
            "max_depth_std_m": 0.20,
            "depth_std_good_m": 0.035,
            "min_foreground_height_m": 0.010,
            "max_foreground_height_m": 0.50,
            "preferred_foreground_min_m": 0.012,
            "preferred_foreground_max_m": 0.18,
            "max_sync_offset_sec": 0.150,
            "sync_good_sec": 0.020,
            "reject_border_candidates": False,
            "reject_oversize_jpeg": False,
            "min_sharpness": 2.0,
            "sharpness_good": 80.0,
            "dark_pixel_threshold": 20,
            "bright_pixel_threshold": 250,
            "max_dark_ratio": 0.98,
            "max_bright_clip_ratio": 0.98,
            "hard_aspect_ratio_min": 0.15,
            "hard_aspect_ratio_max": 6.0,
            "preferred_aspect_ratio_min": 0.45,
            "preferred_aspect_ratio_max": 2.20,
            "min_fill_ratio": 0.05,
            "preferred_fill_ratio_min": 0.25,
            "preferred_fill_ratio_max": 0.90,
            "max_edge_density": 0.70,
            "preferred_edge_density_min": 0.008,
            "preferred_edge_density_max": 0.22,
            "enable_physical_size_filter": False,
            "physical_short_side_min_m": 0.015,
            "physical_short_side_max_m": 0.14,
            "physical_long_side_min_m": 0.025,
            "physical_long_side_max_m": 0.20,
            "physical_short_side_preferred_min_m": 0.025,
            "physical_short_side_preferred_max_m": 0.10,
            "physical_long_side_preferred_min_m": 0.035,
            "physical_long_side_preferred_max_m": 0.15,
            "require_plane_for_objectness": True,
            "enforce_objectness_score": False,
            "min_objectness_score": 0.45,

            "objectness_depth_weight": 0.40,
            "objectness_quality_weight": 0.25,
            "objectness_shape_weight": 0.35,

            "target_color_weight": 0.80,
            "target_physical_size_weight": 0.20,
            "reliable_accepted_output": False,
            "publish_accepted_crops": True,
            "publish_debug": True,
            "debug_mode": "all",
            "debug_hz": 2.0,
            "debug_jpeg_quality": 78,
            "status_log_period_sec": 5.0,
            "require_plane_for_objectness": True,
            "require_foreground_mask": True,
            "min_mask_pixels": 120,
            "min_mask_fill_ratio": 0.08,
            "max_mask_fill_ratio": 0.98,
            "solidity_bad": 0.25,
            "solidity_good": 0.85,
        }
        for name, value in defaults.items():
            self.declare_parameter(name, value)

    def _filter_config(self) -> FilterConfig:
        value = lambda name: self.get_parameter(name).value
        return FilterConfig(
            analysis_long_side_px=int(value("analysis_long_side_px")),
            color_hist_bins=int(value("color_hist_bins")),
            color_mask_ratio=float(value("color_mask_ratio")),
            color_top_k=int(value("color_top_k")),
            canny_low_threshold=int(value("canny_low_threshold")),
            canny_high_threshold=int(value("canny_high_threshold")),
            min_crop_side_px=int(value("min_crop_side_px")),
            min_crop_area_px=int(value("min_crop_area_px")),
            min_depth_m=float(value("min_depth_m")),
            max_depth_m=float(value("max_depth_m")),
            preferred_depth_min_m=float(value("preferred_depth_min_m")),
            preferred_depth_max_m=float(value("preferred_depth_max_m")),
            min_valid_depth_ratio=float(value("min_valid_depth_ratio")),
            valid_depth_good_ratio=float(value("valid_depth_good_ratio")),
            max_depth_std_m=float(value("max_depth_std_m")),
            depth_std_good_m=float(value("depth_std_good_m")),
            min_foreground_height_m=float(value("min_foreground_height_m")),
            max_foreground_height_m=float(value("max_foreground_height_m")),
            preferred_foreground_min_m=float(value("preferred_foreground_min_m")),
            preferred_foreground_max_m=float(value("preferred_foreground_max_m")),
            max_sync_offset_sec=float(value("max_sync_offset_sec")),
            sync_good_sec=float(value("sync_good_sec")),
            reject_border_candidates=bool(value("reject_border_candidates")),
            reject_oversize_jpeg=bool(value("reject_oversize_jpeg")),
            min_sharpness=float(value("min_sharpness")),
            sharpness_good=float(value("sharpness_good")),
            dark_pixel_threshold=int(value("dark_pixel_threshold")),
            bright_pixel_threshold=int(value("bright_pixel_threshold")),
            max_dark_ratio=float(value("max_dark_ratio")),
            max_bright_clip_ratio=float(value("max_bright_clip_ratio")),
            hard_aspect_ratio_min=float(value("hard_aspect_ratio_min")),
            hard_aspect_ratio_max=float(value("hard_aspect_ratio_max")),
            preferred_aspect_ratio_min=float(value("preferred_aspect_ratio_min")),
            preferred_aspect_ratio_max=float(value("preferred_aspect_ratio_max")),
            min_fill_ratio=float(value("min_fill_ratio")),
            preferred_fill_ratio_min=float(value("preferred_fill_ratio_min")),
            preferred_fill_ratio_max=float(value("preferred_fill_ratio_max")),
            max_edge_density=float(value("max_edge_density")),
            preferred_edge_density_min=float(value("preferred_edge_density_min")),
            preferred_edge_density_max=float(value("preferred_edge_density_max")),
            enable_physical_size_filter=bool(value("enable_physical_size_filter")),
            physical_short_side_min_m=float(value("physical_short_side_min_m")),
            physical_short_side_max_m=float(value("physical_short_side_max_m")),
            physical_long_side_min_m=float(value("physical_long_side_min_m")),
            physical_long_side_max_m=float(value("physical_long_side_max_m")),
            physical_short_side_preferred_min_m=float(
                value("physical_short_side_preferred_min_m")
            ),
            physical_short_side_preferred_max_m=float(
                value("physical_short_side_preferred_max_m")
            ),
            physical_long_side_preferred_min_m=float(
                value("physical_long_side_preferred_min_m")
            ),
            physical_long_side_preferred_max_m=float(
                value("physical_long_side_preferred_max_m")
            ),
            require_plane_for_objectness=bool(
                value("require_plane_for_objectness")
            ),
            require_foreground_mask=bool(
                value("require_foreground_mask")
            ),
            min_mask_pixels=int(value("min_mask_pixels")),
            min_mask_fill_ratio=float(
                value("min_mask_fill_ratio")
            ),
            max_mask_fill_ratio=float(
                value("max_mask_fill_ratio")
            ),
            solidity_bad=float(value("solidity_bad")),
            solidity_good=float(value("solidity_good")),
            enable_color_hard_reject=bool(value("enable_color_hard_reject")),
            min_color_score=float(value("min_color_score")),
            enforce_soft_score=bool(value("enforce_soft_score")),
            min_filter_score=float(value("min_filter_score")),
            enforce_objectness_score=bool(
                value("enforce_objectness_score")
            ),
            min_objectness_score=float(
                value("min_objectness_score")
            ),
            objectness_depth_weight=float(
                value("objectness_depth_weight")
            ),
            objectness_quality_weight=float(
                value("objectness_quality_weight")
            ),
            objectness_shape_weight=float(
                value("objectness_shape_weight")
            ),
            target_color_weight=float(
                value("target_color_weight")
            ),
            target_physical_size_weight=float(
                value("target_physical_size_weight")
            ),
        )

    def _reference_directory(self) -> Path:
        override = str(self.get_parameter("reference_dir").value).strip()
        if override:
            return Path(override).expanduser()
        root = Path(str(self.get_parameter("object_root").value)).expanduser()
        return root / self._target_object

    def _reload_profile(self, log_result: bool) -> bool:
        try:
            config = self._filter_config()
            config.validate()
            profile = load_reference_profile(
                target_object=self._target_object,
                directory=self._reference_directory(),
                config=config,
                max_images=int(self.get_parameter("max_reference_images").value),
            )
        except (ValueError, OSError, cv2.error) as error:
            self.get_logger().error(f"Reference profile reload failed: {error}")
            return False
        self._profile = profile
        if log_result:
            if profile.available:
                self.get_logger().info(
                    f"Loaded target profile '{self._target_object}': "
                    f"{profile.image_count} images from '{profile.directory}'"
                )
            else:
                self.get_logger().warning(
                    f"No usable reference images for '{self._target_object}' in "
                    f"'{profile.directory}'. Color score will be unavailable."
                )
        return profile.available

    def _periodic_profile_reload(self) -> None:
        self._reload_profile(log_result=False)

    def _reload_profile_service(
        self, request: Trigger.Request, response: Trigger.Response
    ) -> Trigger.Response:
        del request
        available = self._reload_profile(log_result=True)
        response.success = available
        if self._profile is None:
            response.message = "profile reload failed"
        else:
            response.message = (
                f"target={self._target_object}, "
                f"images={self._profile.image_count}, "
                f"directory={self._profile.directory}"
            )
        return response

    def _target_callback(self, message: String) -> None:
        target = message.data.strip()
        if not target:
            self.get_logger().warning("Ignoring an empty candidate filter target")
            return
        if target in {".", ".."} or "/" in target or "\\" in target:
            self.get_logger().warning(f"Ignoring unsafe target name: '{target}'")
            return
        self._target_object = target
        self._reload_profile(log_result=True)

    def _camera_info_callback(self, message: CameraInfo) -> None:
        self._camera_info = message

    def _estimate_physical_size(
        self, message: RgbCandidateCrop
    ) -> Tuple[Optional[float], Optional[float]]:
        info = self._camera_info
        if info is None or len(info.k) < 9:
            return None, None
        fx = float(info.k[0])
        fy = float(info.k[4])
        proposal_width = int(message.proposal_image_width)
        proposal_height = int(message.proposal_image_height)
        info_width = int(info.width)
        info_height = int(info.height)
        depth = float(message.candidate.median_depth_m)
        if (
            fx <= 0.0
            or fy <= 0.0
            or min(proposal_width, proposal_height, info_width, info_height) <= 0
            or not math.isfinite(depth)
            or depth <= 0.0
        ):
            return None, None
        fx_proposal = fx * proposal_width / float(info_width)
        fy_proposal = fy * proposal_height / float(info_height)
        width_m = float(message.candidate.roi.width) * depth / fx_proposal
        height_m = float(message.candidate.roi.height) * depth / fy_proposal
        return width_m, height_m

    def _crop_callback(self, message: RgbCandidateCrop) -> None:
        start = time.perf_counter()
        now_monotonic = time.monotonic()
        self._received += 1
        try:
            config = self._filter_config()
            config.validate()

            image_bgr = decode_compressed_image(
                message.image.data
            )

            object_mask = None

            if (
                message.foreground_mask_available
                and message.foreground_mask.data
            ):
                object_mask = decode_compressed_mask(
                    message.foreground_mask.data
                )

            features = compute_image_features(
                image_bgr,
                config,
                object_mask=object_mask,
            )
        except (ValueError, cv2.error) as error:
            self._decode_failures += 1
            self._rejected += 1
            self._reject_reasons["decode_failed"] += 1
            result = self._build_failure_result(message, "decode", "decode_failed")
            self._result_publisher.publish(result)
            self._last_result_summary = f"reject decode_failed: {error}"
            self.get_logger().warning(
                f"Candidate {message.candidate.id} preparation failed: {error}"
            )
            self._publish_status_if_due(now_monotonic, start)
            return

        estimated_width_m, estimated_height_m = self._estimate_physical_size(message)
        measurements = CandidateMeasurements(
            encoded_width=int(message.encoded_width),
            encoded_height=int(message.encoded_height),
            bbox_width_px=int(message.candidate.roi.width),
            bbox_height_px=int(message.candidate.roi.height),
            median_depth_m=float(message.candidate.median_depth_m),
            depth_std_m=float(message.candidate.depth_std_m),
            valid_depth_ratio=float(message.candidate.valid_depth_ratio),
            fill_ratio=float(message.candidate.fill_ratio),
            foreground_height_m=float(message.candidate.foreground_height_m),
            plane_found=bool(message.plane_found),
            foreground_height_valid=bool(
                message.candidate.foreground_height_valid
            ),
            proposal_score=float(message.candidate.proposal_score),
            touches_border=bool(message.candidate.touches_border),
            sync_offset_abs_sec=abs(float(message.color_time_offset_sec)),
            size_limit_met=bool(message.size_limit_met),
            estimated_width_m=estimated_width_m,
            estimated_height_m=estimated_height_m,
        )
        evaluation = evaluate_candidate(
            measurements=measurements,
            features=features,
            profile=self._profile,
            config=config,
        )
        result = self._build_result(
            message,
            evaluation,
            features,
            estimated_width_m,
            estimated_height_m,
        )
        self._result_publisher.publish(result)

        if evaluation.accepted:
            self._accepted += 1
            if bool(self.get_parameter("publish_accepted_crops").value):
                accepted_message = FilteredCandidateCrop()
                accepted_message.result = result
                accepted_message.crop = message
                self._accepted_publisher.publish(accepted_message)
                self._published_bytes += int(message.jpeg_size_bytes)
            target_text = (
                f"{evaluation.target_hint_score:.3f}"
                if evaluation.target_hint_score is not None
                else "n/a"
            )

            self._last_result_summary = (
                f"accept id={message.candidate.id} "
                f"objectness={evaluation.objectness_score:.3f} "
                f"target_hint={target_text}"
            )
        else:
            self._rejected += 1
            self._reject_reasons[evaluation.reject_reason] += 1
            self._last_result_summary = (
                f"reject id={message.candidate.id} "
                f"reason={evaluation.reject_reason} "
                f"objectness={evaluation.filter_score:.3f}"
            )

        self._publish_debug_if_due(
            message, image_bgr, evaluation, features, now_monotonic
        )
        self._publish_status_if_due(now_monotonic, start)

    def _base_result(self, message: RgbCandidateCrop) -> CandidateFilterResult:
        result = CandidateFilterResult()
        result.proposal_header = message.proposal_header
        result.image_header = message.image.header
        result.candidate_id = int(message.candidate.id)
        result.crop_index = int(message.crop_index)
        result.frame_crop_count = int(message.frame_crop_count)
        result.target_object = self._target_object
        result.reference_profile_available = bool(
            self._profile is not None and self._profile.available
        )
        result.reference_image_count = (
            int(self._profile.image_count) if self._profile is not None else 0
        )
        result.sync_offset_abs_sec = abs(float(message.color_time_offset_sec))
        result.candidate = message.candidate
        result.crop_roi = message.crop_roi
        result.plane_found = bool(message.plane_found)
        result.foreground_height_valid = bool(
            message.candidate.foreground_height_valid
        )
        result.foreground_mask_available = bool(
            message.foreground_mask_available
        )
        return result

    def _build_failure_result(
        self,
        message: RgbCandidateCrop,
        reject_stage: str,
        reject_reason: str,
    ) -> CandidateFilterResult:
        result = self._base_result(message)
        result.camera_info_available = False
        result.accepted = False
        result.reject_stage = reject_stage
        result.reject_reason = reject_reason
        result.filter_score = -1.0
        result.depth_score = -1.0
        result.quality_score = -1.0
        result.color_score = -1.0
        result.shape_score = -1.0
        result.physical_size_score = -1.0
        result.sharpness = -1.0
        result.mean_brightness = -1.0
        result.dark_ratio = -1.0
        result.bright_clip_ratio = -1.0
        result.edge_density = -1.0
        result.color_similarity = -1.0
        result.aspect_ratio = -1.0
        result.estimated_width_m = -1.0
        result.estimated_height_m = -1.0
        result.objectness_score = -1.0
        result.target_hint_score = -1.0
        result.mask_fill_ratio = -1.0
        result.mask_solidity = -1.0
        return result

    def _build_result(
        self,
        message: RgbCandidateCrop,
        evaluation: FilterEvaluation,
        features: ImageFeatures,
        estimated_width_m: Optional[float],
        estimated_height_m: Optional[float],
    ) -> CandidateFilterResult:
        result = self._base_result(message)
        result.camera_info_available = bool(
            estimated_width_m is not None and estimated_height_m is not None
        )
        result.accepted = bool(evaluation.accepted)
        result.reject_stage = evaluation.reject_stage
        result.reject_reason = evaluation.reject_reason
        result.objectness_score = float(
            evaluation.objectness_score
        )

        result.target_hint_score = (
            float(evaluation.target_hint_score)
            if evaluation.target_hint_score is not None
            else -1.0
        )
        result.filter_score = float(evaluation.objectness_score)
        result.depth_score = float(evaluation.depth_score)
        result.quality_score = float(evaluation.quality_score)
        result.color_score = (
            float(evaluation.color_score)
            if evaluation.color_score is not None
            else -1.0
        )
        result.shape_score = float(evaluation.shape_score)
        result.physical_size_score = (
            float(evaluation.physical_size_score)
            if evaluation.physical_size_score is not None
            else -1.0
        )
        result.sharpness = float(features.sharpness)
        result.mean_brightness = float(features.mean_brightness)
        result.dark_ratio = float(features.dark_ratio)
        result.bright_clip_ratio = float(features.bright_clip_ratio)
        result.edge_density = float(features.edge_density)
        result.color_similarity = (
            float(evaluation.color_similarity)
            if evaluation.color_similarity is not None
            else -1.0
        )
        result.aspect_ratio = float(evaluation.aspect_ratio)
        result.estimated_width_m = (
            float(estimated_width_m) if estimated_width_m is not None else -1.0
        )
        result.estimated_height_m = (
            float(estimated_height_m) if estimated_height_m is not None else -1.0
        )
        result.mask_fill_ratio = float(
            features.mask_fill_ratio
        )
        result.mask_solidity = float(
            features.mask_solidity
        )
        return result

    def _publish_debug_if_due(
        self,
        message: RgbCandidateCrop,
        image_bgr,
        evaluation: FilterEvaluation,
        features: ImageFeatures,
        now_monotonic: float,
    ) -> None:
        if not bool(self.get_parameter("publish_debug").value):
            return
        mode = str(self.get_parameter("debug_mode").value).strip().lower()
        if mode not in {"all", "accepted", "rejected"}:
            mode = "all"
        if mode == "accepted" and not evaluation.accepted:
            return
        if mode == "rejected" and evaluation.accepted:
            return
        debug_hz = max(float(self.get_parameter("debug_hz").value), 0.1)
        if now_monotonic - self._last_debug_monotonic < 1.0 / debug_hz:
            return
        self._last_debug_monotonic = now_monotonic

        canvas = cv2.copyMakeBorder(
            image_bgr,
            76,
            2,
            2,
            2,
            cv2.BORDER_CONSTANT,
            value=(24, 24, 24),
        )
        decision = "ACCEPT" if evaluation.accepted else "REJECT"
        reason = evaluation.reject_reason or "passed"
        color_score = (
            f"{evaluation.color_score:.2f}"
            if evaluation.color_score is not None
            else "n/a"
        )
        physical_score = (
            f"{evaluation.physical_size_score:.2f}"
            if evaluation.physical_size_score is not None
            else "n/a"
        )
        target_hint_text = (
            f"{evaluation.target_hint_score:.2f}"
            if evaluation.target_hint_score is not None
            else "n/a"
        )

        lines = [
            (
                f"{decision} id={message.candidate.id} "
                f"O={evaluation.objectness_score:.2f} "
                f"T={target_hint_text} {reason}"
            ),
            (
                f"D={evaluation.depth_score:.2f} "
                f"Q={evaluation.quality_score:.2f} "
                f"C={color_score} "
                f"S={evaluation.shape_score:.2f} "
                f"P={physical_score}"
            ),
            (
                f"mask={features.mask_fill_ratio:.2f} "
                f"sol={features.mask_solidity:.2f} "
                f"z={message.candidate.median_depth_m:.3f}m"
            ),
        ]
        for index, line in enumerate(lines):
            cv2.putText(
                canvas,
                line,
                (8, 20 + index * 23),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.48,
                (235, 235, 235),
                1,
                cv2.LINE_AA,
            )
        border_value = (60, 210, 60) if evaluation.accepted else (40, 40, 230)
        cv2.rectangle(
            canvas,
            (1, 75),
            (canvas.shape[1] - 2, canvas.shape[0] - 2),
            border_value,
            2,
        )
        quality = max(
            30, min(95, int(self.get_parameter("debug_jpeg_quality").value))
        )
        success, encoded = cv2.imencode(
            ".jpg", canvas, [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        )
        if not success:
            return
        debug_message = CompressedImage()
        debug_message.header = message.image.header
        debug_message.format = "bgr8; jpeg compressed bgr8"
        debug_message.data = encoded.tobytes()
        self._debug_publisher.publish(debug_message)

    def _publish_status_if_due(self, now_monotonic: float, start_time: float) -> None:
        period = max(float(self.get_parameter("status_log_period_sec").value), 1.0)
        if now_monotonic - self._last_status_monotonic < period:
            return
        self._last_status_monotonic = now_monotonic
        profile = self._profile
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        top_reasons = self._reject_reasons.most_common(5)
        payload = {
            "target_object": self._target_object,
            "profile_available": bool(profile is not None and profile.available),
            "reference_image_count": int(profile.image_count) if profile else 0,
            "received": self._received,
            "accepted": self._accepted,
            "rejected": self._rejected,
            "decode_failures": self._decode_failures,
            "accepted_jpeg_bytes": self._published_bytes,
            "top_reject_reasons": top_reasons,
            "last_result": self._last_result_summary,
            "last_processing_ms": round(elapsed_ms, 3),
            "objectness_enforcement": bool(
                self.get_parameter(
                    "enforce_objectness_score"
                ).value
            ),
            "min_objectness_score": float(
                self.get_parameter(
                    "min_objectness_score"
                ).value
            ),
        }
        status_message = String()
        status_message.data = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        self._status_publisher.publish(status_message)
        self.get_logger().info(
            f"received={self._received}, accepted={self._accepted}, "
            f"rejected={self._rejected}, profile={payload['reference_image_count']}, "
            f"processing={elapsed_ms:.1f} ms, reasons={top_reasons}"
        )


def main(args=None) -> None:
    rclpy.init(args=args)
    node = CandidateFilterNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
