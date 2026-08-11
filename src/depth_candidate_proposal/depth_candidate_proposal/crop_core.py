"""Pure OpenCV helpers for RGB proposal cropping and bounded JPEG encoding."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Tuple

import cv2
import numpy as np


@dataclass(frozen=True)
class CropEncodingConfig:
    """Configuration for resize and adaptive JPEG encoding."""

    jpeg_quality: int = 70
    min_jpeg_quality: int = 35
    jpeg_quality_step: int = 8
    max_jpeg_bytes: int = 55_000
    max_crop_side_px: int = 320
    min_crop_side_px: int = 32
    resize_factor: float = 0.80
    max_resize_iterations: int = 6

    def validate(self) -> None:
        if not (1 <= self.min_jpeg_quality <= self.jpeg_quality <= 100):
            raise ValueError(
                "Expected 1 <= min_jpeg_quality <= jpeg_quality <= 100"
            )
        if self.jpeg_quality_step < 1:
            raise ValueError("jpeg_quality_step must be positive")
        if self.max_jpeg_bytes < 1_024:
            raise ValueError("max_jpeg_bytes must be at least 1024")
        if self.max_crop_side_px < 1:
            raise ValueError("max_crop_side_px must be positive")
        if self.min_crop_side_px < 1:
            raise ValueError("min_crop_side_px must be positive")
        if self.min_crop_side_px > self.max_crop_side_px:
            raise ValueError("min_crop_side_px cannot exceed max_crop_side_px")
        if not (0.25 <= self.resize_factor < 1.0):
            raise ValueError("resize_factor must be in [0.25, 1.0)")
        if self.max_resize_iterations < 0:
            raise ValueError("max_resize_iterations cannot be negative")


@dataclass(frozen=True)
class EncodedCrop:
    """Result of bounded JPEG encoding."""

    data: bytes
    width: int
    height: int
    quality: int
    size_limit_met: bool


@dataclass(frozen=True)
class PixelRoi:
    """Integer pixel ROI using x, y, width, and height."""

    x: int
    y: int
    width: int
    height: int


def map_and_pad_roi(
    roi_x: int,
    roi_y: int,
    roi_width: int,
    roi_height: int,
    proposal_width: int,
    proposal_height: int,
    color_width: int,
    color_height: int,
    extra_padding_px: int = 0,
    extra_padding_ratio: float = 0.0,
) -> PixelRoi:
    """Map a proposal ROI into RGB coordinates and clamp it."""

    dimensions = (
        proposal_width,
        proposal_height,
        color_width,
        color_height,
        roi_width,
        roi_height,
    )

    if any(value <= 0 for value in dimensions):
        raise ValueError(
            "Image dimensions and ROI size must be positive"
        )

    if extra_padding_px < 0:
        raise ValueError(
            "extra_padding_px cannot be negative"
        )

    if extra_padding_ratio < 0.0:
        raise ValueError(
            "extra_padding_ratio cannot be negative"
        )

    scale_x = float(color_width) / float(proposal_width)
    scale_y = float(color_height) / float(proposal_height)

    x0 = int(math.floor(float(roi_x) * scale_x))
    y0 = int(math.floor(float(roi_y) * scale_y))

    x1 = int(
        math.ceil(
            float(roi_x + roi_width) * scale_x
        )
    )

    y1 = int(
        math.ceil(
            float(roi_y + roi_height) * scale_y
        )
    )

    mapped_width = max(x1 - x0, 1)
    mapped_height = max(y1 - y0, 1)

    pad_x = (
        int(extra_padding_px)
        + int(round(mapped_width * extra_padding_ratio))
    )

    pad_y = (
        int(extra_padding_px)
        + int(round(mapped_height * extra_padding_ratio))
    )

    x0 = max(0, x0 - pad_x)
    y0 = max(0, y0 - pad_y)

    x1 = min(color_width, x1 + pad_x)
    y1 = min(color_height, y1 + pad_y)

    if x1 <= x0 or y1 <= y0:
        raise ValueError(
            "Mapped ROI is empty after clamping"
        )

    return PixelRoi(
        x=x0,
        y=y0,
        width=x1 - x0,
        height=y1 - y0,
    )


def extract_crop(image_bgr: np.ndarray, roi: PixelRoi) -> np.ndarray:
    """Extract a defensive copy of one BGR crop."""
    if image_bgr.ndim != 3 or image_bgr.shape[2] != 3:
        raise ValueError("Expected a three-channel BGR image")
    height, width = image_bgr.shape[:2]
    if roi.x < 0 or roi.y < 0 or roi.width <= 0 or roi.height <= 0:
        raise ValueError("Invalid ROI")
    if roi.x + roi.width > width or roi.y + roi.height > height:
        raise ValueError("ROI lies outside the image")
    return image_bgr[
        roi.y : roi.y + roi.height,
        roi.x : roi.x + roi.width,
    ].copy()


def decode_binary_mask(data: bytes | bytearray) -> np.ndarray:
    encoded = np.frombuffer(bytes(data), dtype=np.uint8)

    if encoded.size == 0:
        raise ValueError("Foreground mask data is empty")

    mask = cv2.imdecode(encoded, cv2.IMREAD_GRAYSCALE)

    if mask is None or mask.size == 0:
        raise ValueError("Foreground mask PNG decoding failed")

    return np.where(mask > 0, 255, 0).astype(np.uint8)


def isolate_component_near_point(
    mask_u8: np.ndarray,
    point_x: float,
    point_y: float,
) -> np.ndarray:
    if mask_u8.ndim != 2:
        raise ValueError("Expected a single-channel binary mask")

    binary = np.where(mask_u8 > 0, 255, 0).astype(np.uint8)

    count, labels, stats, centroids = cv2.connectedComponentsWithStats(
        binary,
        connectivity=8,
    )

    if count <= 1:
        return np.zeros_like(binary)

    height, width = binary.shape
    px = int(np.clip(round(point_x), 0, width - 1))
    py = int(np.clip(round(point_y), 0, height - 1))

    selected_label = int(labels[py, px])

    if selected_label == 0:
        candidate_labels = range(1, count)

        selected_label = min(
            candidate_labels,
            key=lambda label: (
                float(centroids[label, 0]) - float(point_x)
            ) ** 2
            + (
                float(centroids[label, 1]) - float(point_y)
            ) ** 2,
        )

    return np.where(
        labels == selected_label,
        255,
        0,
    ).astype(np.uint8)


def create_candidate_crop_mask(
    frame_mask: np.ndarray,
    roi: PixelRoi,
    proposal_width: int,
    proposal_height: int,
    color_width: int,
    color_height: int,
    candidate_center_x: float,
    candidate_center_y: float,
) -> np.ndarray:
    if frame_mask.ndim != 2:
        raise ValueError("Frame mask must be single-channel")

    if frame_mask.shape != (proposal_height, proposal_width):
        frame_mask = cv2.resize(
            frame_mask,
            (proposal_width, proposal_height),
            interpolation=cv2.INTER_NEAREST,
        )

    if (
        proposal_width != color_width
        or proposal_height != color_height
    ):
        color_mask = cv2.resize(
            frame_mask,
            (color_width, color_height),
            interpolation=cv2.INTER_NEAREST,
        )
    else:
        color_mask = frame_mask

    mask_crop = color_mask[
        roi.y : roi.y + roi.height,
        roi.x : roi.x + roi.width,
    ].copy()

    center_color_x = (
        float(candidate_center_x)
        * float(color_width)
        / float(proposal_width)
    )
    center_color_y = (
        float(candidate_center_y)
        * float(color_height)
        / float(proposal_height)
    )

    local_center_x = center_color_x - float(roi.x)
    local_center_y = center_color_y - float(roi.y)

    return isolate_component_near_point(
        mask_crop,
        local_center_x,
        local_center_y,
    )


def encode_crop_mask_png(
    mask_u8: np.ndarray,
    target_width: int,
    target_height: int,
    compression: int = 3,
) -> tuple[bytes, float]:
    if target_width <= 0 or target_height <= 0:
        raise ValueError("Invalid target mask dimensions")

    resized = cv2.resize(
        mask_u8,
        (target_width, target_height),
        interpolation=cv2.INTER_NEAREST,
    )

    binary = np.where(resized > 0, 255, 0).astype(np.uint8)

    fill_ratio = float(
        np.count_nonzero(binary)
    ) / float(max(binary.size, 1))

    success, encoded = cv2.imencode(
        ".png",
        binary,
        [
            int(cv2.IMWRITE_PNG_COMPRESSION),
            int(np.clip(compression, 0, 9)),
        ],
    )

    if not success:
        raise RuntimeError("OpenCV failed to encode candidate mask")

    return encoded.tobytes(), fill_ratio


def _resize_to_max_side(image_bgr: np.ndarray, max_side_px: int) -> np.ndarray:
    height, width = image_bgr.shape[:2]
    longest = max(width, height)
    if longest <= max_side_px:
        return image_bgr
    scale = float(max_side_px) / float(longest)
    resized_width = max(1, int(round(width * scale)))
    resized_height = max(1, int(round(height * scale)))
    return cv2.resize(
        image_bgr,
        (resized_width, resized_height),
        interpolation=cv2.INTER_AREA,
    )


def _quality_ladder(start: int, minimum: int, step: int) -> list[int]:
    values = list(range(start, minimum - 1, -step))
    if not values or values[-1] != minimum:
        values.append(minimum)
    return values


def encode_jpeg_bounded(
    crop_bgr: np.ndarray,
    config: CropEncodingConfig,
) -> EncodedCrop:
    """Encode a crop while trying to keep each DDS sample below a byte limit.

    Quality is reduced first. If the JPEG is still too large, the crop is
    progressively downscaled. The smallest successful encoding is returned;
    if the configured limit cannot be met, the smallest attempted JPEG is
    returned with ``size_limit_met=False``.
    """
    config.validate()
    if crop_bgr.ndim != 3 or crop_bgr.shape[2] != 3 or crop_bgr.size == 0:
        raise ValueError("Expected a non-empty three-channel BGR crop")

    working = _resize_to_max_side(crop_bgr, config.max_crop_side_px)
    best: tuple[bytes, int, int, int] | None = None
    qualities = _quality_ladder(
        config.jpeg_quality,
        config.min_jpeg_quality,
        config.jpeg_quality_step,
    )

    for resize_index in range(config.max_resize_iterations + 1):
        height, width = working.shape[:2]
        for quality in qualities:
            success, encoded = cv2.imencode(
                ".jpg",
                working,
                [int(cv2.IMWRITE_JPEG_QUALITY), int(quality)],
            )
            if not success:
                raise RuntimeError("OpenCV failed to encode a JPEG crop")
            data = encoded.tobytes()
            if best is None or len(data) < len(best[0]):
                best = (data, width, height, quality)
            if len(data) <= config.max_jpeg_bytes:
                return EncodedCrop(
                    data=data,
                    width=width,
                    height=height,
                    quality=quality,
                    size_limit_met=True,
                )

        if resize_index >= config.max_resize_iterations:
            break
        if min(width, height) <= config.min_crop_side_px:
            break

        next_width = max(
            config.min_crop_side_px,
            int(round(width * config.resize_factor)),
        )
        next_height = max(
            config.min_crop_side_px,
            int(round(height * config.resize_factor)),
        )
        if next_width == width and next_height == height:
            break
        working = cv2.resize(
            working,
            (next_width, next_height),
            interpolation=cv2.INTER_AREA,
        )

    if best is None:
        raise RuntimeError("No JPEG encoding attempt was produced")
    data, width, height, quality = best
    return EncodedCrop(
        data=data,
        width=width,
        height=height,
        quality=quality,
        size_limit_met=False,
    )
