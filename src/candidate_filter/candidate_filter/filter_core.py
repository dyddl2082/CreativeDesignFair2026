"""Pure OpenCV/NumPy scoring utilities for MacRobot candidate filtering."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence
import math

import cv2
import numpy as np

_IMAGE_EXTENSIONS = {".bmp", ".jpeg", ".jpg", ".png", ".tif", ".tiff", ".webp"}


def clamp01(value: float) -> float:
    return float(max(0.0, min(1.0, value)))


@dataclass(frozen=True)
class FilterConfig:
    analysis_long_side_px: int = 192
    color_hist_bins: int = 16
    color_mask_ratio: float = 0.84
    color_top_k: int = 3
    canny_low_threshold: int = 60
    canny_high_threshold: int = 160

    min_crop_side_px: int = 32
    min_crop_area_px: int = 1024
    min_depth_m: float = 0.18
    max_depth_m: float = 1.50
    preferred_depth_min_m: float = 0.25
    preferred_depth_max_m: float = 1.00
    min_valid_depth_ratio: float = 0.35
    valid_depth_good_ratio: float = 0.85
    max_depth_std_m: float = 0.20
    depth_std_good_m: float = 0.035
    min_foreground_height_m: float = 0.0
    max_foreground_height_m: float = 0.50
    preferred_foreground_min_m: float = 0.012
    preferred_foreground_max_m: float = 0.18
    max_sync_offset_sec: float = 0.150
    sync_good_sec: float = 0.020

    reject_border_candidates: bool = False
    reject_oversize_jpeg: bool = False

    min_sharpness: float = 2.0
    sharpness_good: float = 80.0
    dark_pixel_threshold: int = 20
    bright_pixel_threshold: int = 250
    max_dark_ratio: float = 0.98
    max_bright_clip_ratio: float = 0.98

    hard_aspect_ratio_min: float = 0.15
    hard_aspect_ratio_max: float = 6.0
    preferred_aspect_ratio_min: float = 0.45
    preferred_aspect_ratio_max: float = 2.20
    min_fill_ratio: float = 0.05
    preferred_fill_ratio_min: float = 0.25
    preferred_fill_ratio_max: float = 0.90
    max_edge_density: float = 0.70
    preferred_edge_density_min: float = 0.008
    preferred_edge_density_max: float = 0.22

    enable_physical_size_filter: bool = False
    physical_short_side_min_m: float = 0.015
    physical_short_side_max_m: float = 0.14
    physical_long_side_min_m: float = 0.025
    physical_long_side_max_m: float = 0.20
    physical_short_side_preferred_min_m: float = 0.025
    physical_short_side_preferred_max_m: float = 0.10
    physical_long_side_preferred_min_m: float = 0.035
    physical_long_side_preferred_max_m: float = 0.15

    enable_color_hard_reject: bool = False
    min_color_score: float = 0.18
    enforce_soft_score: bool = False
    min_filter_score: float = 0.45

    depth_weight: float = 0.30
    quality_weight: float = 0.20
    color_weight: float = 0.25
    shape_weight: float = 0.20
    physical_size_weight: float = 0.05

    def validate(self) -> None:
        if self.analysis_long_side_px < 32:
            raise ValueError("analysis_long_side_px must be at least 32")
        if self.color_hist_bins < 4:
            raise ValueError("color_hist_bins must be at least 4")
        if not 0.20 <= self.color_mask_ratio <= 1.0:
            raise ValueError("color_mask_ratio must be in [0.20, 1.0]")
        if self.color_top_k < 1:
            raise ValueError("color_top_k must be at least 1")
        if self.min_crop_side_px < 1 or self.min_crop_area_px < 1:
            raise ValueError("minimum crop dimensions must be positive")
        if not 0.0 < self.min_depth_m < self.max_depth_m:
            raise ValueError("depth range is invalid")
        if not self.min_depth_m <= self.preferred_depth_min_m:
            raise ValueError("preferred_depth_min_m is below min_depth_m")
        if not self.preferred_depth_min_m <= self.preferred_depth_max_m:
            raise ValueError("preferred depth range is invalid")
        if not self.preferred_depth_max_m <= self.max_depth_m:
            raise ValueError("preferred_depth_max_m exceeds max_depth_m")
        if not 0.0 <= self.min_valid_depth_ratio <= self.valid_depth_good_ratio <= 1.0:
            raise ValueError("valid depth ratio range is invalid")
        if self.max_depth_std_m <= 0.0:
            raise ValueError("max_depth_std_m must be positive")
        if self.max_sync_offset_sec < 0.0:
            raise ValueError("max_sync_offset_sec cannot be negative")
        if self.hard_aspect_ratio_min <= 0.0:
            raise ValueError("hard_aspect_ratio_min must be positive")
        if self.hard_aspect_ratio_min >= self.hard_aspect_ratio_max:
            raise ValueError("hard aspect ratio range is invalid")
        if not 0.0 <= self.min_filter_score <= 1.0:
            raise ValueError("min_filter_score must be in [0, 1]")
        weights = (
            self.depth_weight,
            self.quality_weight,
            self.color_weight,
            self.shape_weight,
            self.physical_size_weight,
        )
        if any(weight < 0.0 for weight in weights) or sum(weights) <= 0.0:
            raise ValueError("score weights are invalid")


@dataclass(frozen=True)
class ReferenceProfile:
    target_object: str
    directory: str
    image_paths: tuple[str, ...]
    color_histograms: tuple[np.ndarray, ...]

    @property
    def available(self) -> bool:
        return bool(self.color_histograms)

    @property
    def image_count(self) -> int:
        return len(self.color_histograms)


@dataclass(frozen=True)
class ImageFeatures:
    width: int
    height: int
    sharpness: float
    mean_brightness: float
    dark_ratio: float
    bright_clip_ratio: float
    edge_density: float
    color_histogram: np.ndarray


@dataclass(frozen=True)
class CandidateMeasurements:
    encoded_width: int
    encoded_height: int
    bbox_width_px: int
    bbox_height_px: int
    median_depth_m: float
    depth_std_m: float
    valid_depth_ratio: float
    fill_ratio: float
    foreground_height_m: float
    proposal_score: float
    touches_border: bool
    sync_offset_abs_sec: float
    size_limit_met: bool
    estimated_width_m: Optional[float] = None
    estimated_height_m: Optional[float] = None


@dataclass(frozen=True)
class FilterEvaluation:
    accepted: bool
    reject_stage: str
    reject_reason: str
    filter_score: float
    depth_score: float
    quality_score: float
    color_score: Optional[float]
    shape_score: float
    physical_size_score: Optional[float]
    color_similarity: Optional[float]
    aspect_ratio: float


def _resize_long_side(image: np.ndarray, target_long_side: int) -> np.ndarray:
    height, width = image.shape[:2]
    longest = max(height, width)
    if longest <= 0:
        raise ValueError("image has invalid dimensions")
    scale = target_long_side / float(longest)
    size = (max(1, round(width * scale)), max(1, round(height * scale)))
    interpolation = cv2.INTER_AREA if scale < 1.0 else cv2.INTER_LINEAR
    return cv2.resize(image, size, interpolation=interpolation)


def _center_ellipse_mask(height: int, width: int, ratio: float) -> Optional[np.ndarray]:
    if ratio >= 0.999:
        return None
    mask = np.zeros((height, width), dtype=np.uint8)
    center = (width // 2, height // 2)
    axes = (
        max(1, round(width * ratio * 0.5)),
        max(1, round(height * ratio * 0.5)),
    )
    cv2.ellipse(mask, center, axes, 0.0, 0.0, 360.0, 255, thickness=-1)
    return mask


def compute_lab_histogram(image_bgr: np.ndarray, bins: int, mask_ratio: float) -> np.ndarray:
    if image_bgr is None or image_bgr.size == 0:
        raise ValueError("cannot compute histogram from an empty image")
    lab = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2LAB)
    height, width = lab.shape[:2]
    mask = _center_ellipse_mask(height, width, mask_ratio)
    pieces: list[np.ndarray] = []
    for channel in range(3):
        hist = cv2.calcHist([lab], [channel], mask, [bins], [0, 256])
        hist = hist.astype(np.float32).reshape(-1)
        total = float(hist.sum())
        if total > 0.0:
            hist /= total
        pieces.append(hist)
    combined = np.concatenate(pieces).astype(np.float32)
    total = float(combined.sum())
    if total > 0.0:
        combined /= total
    return combined.reshape(-1, 1)


def compute_image_features(image_bgr: np.ndarray, config: FilterConfig) -> ImageFeatures:
    if image_bgr is None or image_bgr.size == 0:
        raise ValueError("decoded crop is empty")
    if image_bgr.ndim != 3 or image_bgr.shape[2] != 3:
        raise ValueError("decoded crop must be a BGR image")
    analysis = _resize_long_side(image_bgr, config.analysis_long_side_px)
    gray = cv2.cvtColor(analysis, cv2.COLOR_BGR2GRAY)
    sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    mean_brightness = float(gray.mean())
    dark_ratio = float(np.mean(gray <= config.dark_pixel_threshold))
    bright_clip_ratio = float(np.mean(gray >= config.bright_pixel_threshold))
    edges = cv2.Canny(gray, config.canny_low_threshold, config.canny_high_threshold)
    edge_density = float(np.mean(edges > 0))
    color_histogram = compute_lab_histogram(
        analysis,
        bins=config.color_hist_bins,
        mask_ratio=config.color_mask_ratio,
    )
    height, width = image_bgr.shape[:2]
    return ImageFeatures(
        width=int(width),
        height=int(height),
        sharpness=sharpness,
        mean_brightness=mean_brightness,
        dark_ratio=dark_ratio,
        bright_clip_ratio=bright_clip_ratio,
        edge_density=edge_density,
        color_histogram=color_histogram,
    )


def _iter_reference_images(directory: Path) -> list[Path]:
    if not directory.is_dir():
        return []
    paths = []
    for path in directory.rglob("*"):
        if not path.is_file():
            continue
        if ".bak" in path.name.lower() or path.suffix.lower() not in _IMAGE_EXTENSIONS:
            continue
        paths.append(path)
    return sorted(paths, key=lambda item: str(item).lower())


def load_reference_profile(
    target_object: str,
    directory: str | Path,
    config: FilterConfig,
    max_images: int = 64,
) -> ReferenceProfile:
    path = Path(directory).expanduser().resolve()
    image_paths: list[str] = []
    histograms: list[np.ndarray] = []
    for image_path in _iter_reference_images(path)[: max(1, int(max_images))]:
        image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
        if image is None or image.size == 0:
            continue
        try:
            resized = _resize_long_side(image, config.analysis_long_side_px)
            histogram = compute_lab_histogram(
                resized,
                bins=config.color_hist_bins,
                mask_ratio=config.color_mask_ratio,
            )
        except (cv2.error, ValueError):
            continue
        image_paths.append(str(image_path))
        histograms.append(histogram)
    return ReferenceProfile(
        target_object=target_object,
        directory=str(path),
        image_paths=tuple(image_paths),
        color_histograms=tuple(histograms),
    )


def color_similarity_to_profile(
    candidate_histogram: np.ndarray,
    profile: Optional[ReferenceProfile],
    top_k: int,
) -> Optional[float]:
    if profile is None or not profile.available:
        return None
    scores = []
    candidate = candidate_histogram.astype(np.float32)
    for reference_histogram in profile.color_histograms:
        reference = reference_histogram.astype(np.float32)
        if candidate.shape != reference.shape:
            continue
        distance = cv2.compareHist(
            candidate,
            reference,
            cv2.HISTCMP_BHATTACHARYYA,
        )
        scores.append(clamp01(1.0 - float(distance)))
    if not scores:
        return None
    scores.sort(reverse=True)
    selected = scores[: max(1, min(int(top_k), len(scores)))]
    return float(np.mean(selected))


def _higher_is_better(value: float, bad: float, good: float) -> float:
    if good <= bad:
        return 1.0 if value >= good else 0.0
    return clamp01((value - bad) / (good - bad))


def _lower_is_better(value: float, good: float, bad: float) -> float:
    if bad <= good:
        return 1.0 if value <= good else 0.0
    return clamp01((bad - value) / (bad - good))


def _range_score(
    value: float,
    hard_min: float,
    ideal_min: float,
    ideal_max: float,
    hard_max: float,
) -> float:
    if value < hard_min or value > hard_max:
        return 0.0
    if ideal_min <= value <= ideal_max:
        return 1.0
    if value < ideal_min:
        return _higher_is_better(value, hard_min, ideal_min)
    return _lower_is_better(value, ideal_max, hard_max)


def _weighted_average(items: Sequence[tuple[float, float]]) -> float:
    active = [(score, weight) for score, weight in items if weight > 0.0]
    total_weight = sum(weight for _, weight in active)
    if total_weight <= 0.0:
        return 0.0
    return clamp01(sum(score * weight for score, weight in active) / total_weight)


def _first_hard_reject(
    measurements: CandidateMeasurements,
    features: ImageFeatures,
    color_similarity: Optional[float],
    config: FilterConfig,
) -> Optional[str]:
    width = max(measurements.encoded_width, features.width)
    height = max(measurements.encoded_height, features.height)
    if min(width, height) < config.min_crop_side_px:
        return "crop_too_small"
    if width * height < config.min_crop_area_px:
        return "crop_area_too_small"
    depth = measurements.median_depth_m
    if not math.isfinite(depth) or depth <= 0.0:
        return "invalid_depth"
    if depth < config.min_depth_m:
        return "depth_too_near"
    if depth > config.max_depth_m:
        return "depth_too_far"
    if measurements.valid_depth_ratio < config.min_valid_depth_ratio:
        return "valid_depth_ratio_low"
    if measurements.depth_std_m > config.max_depth_std_m:
        return "depth_variation_high"
    foreground_height = measurements.foreground_height_m
    if foreground_height > 0.0:
        if foreground_height < config.min_foreground_height_m:
            return "foreground_height_low"
        if foreground_height > config.max_foreground_height_m:
            return "foreground_height_high"
    if measurements.sync_offset_abs_sec > config.max_sync_offset_sec:
        return "rgb_depth_sync_offset_high"
    if config.reject_border_candidates and measurements.touches_border:
        return "candidate_touches_border"
    if config.reject_oversize_jpeg and not measurements.size_limit_met:
        return "jpeg_size_limit_not_met"
    if features.sharpness < config.min_sharpness:
        return "crop_too_blurry"
    if features.dark_ratio > config.max_dark_ratio:
        return "crop_too_dark"
    if features.bright_clip_ratio > config.max_bright_clip_ratio:
        return "crop_overexposed"
    bbox_height = max(1, measurements.bbox_height_px)
    aspect_ratio = measurements.bbox_width_px / float(bbox_height)
    if aspect_ratio < config.hard_aspect_ratio_min:
        return "aspect_ratio_too_narrow"
    if aspect_ratio > config.hard_aspect_ratio_max:
        return "aspect_ratio_too_wide"
    if measurements.fill_ratio < config.min_fill_ratio:
        return "foreground_fill_ratio_low"
    if features.edge_density > config.max_edge_density:
        return "edge_density_too_high"
    physical_width = measurements.estimated_width_m
    physical_height = measurements.estimated_height_m
    if (
        config.enable_physical_size_filter
        and physical_width is not None
        and physical_height is not None
    ):
        short_side, long_side = sorted((physical_width, physical_height))
        if short_side < config.physical_short_side_min_m:
            return "physical_short_side_too_small"
        if short_side > config.physical_short_side_max_m:
            return "physical_short_side_too_large"
        if long_side < config.physical_long_side_min_m:
            return "physical_long_side_too_small"
        if long_side > config.physical_long_side_max_m:
            return "physical_long_side_too_large"
    if (
        config.enable_color_hard_reject
        and color_similarity is not None
        and color_similarity < config.min_color_score
    ):
        return "target_color_mismatch"
    return None


def evaluate_candidate(
    measurements: CandidateMeasurements,
    features: ImageFeatures,
    profile: Optional[ReferenceProfile],
    config: FilterConfig,
) -> FilterEvaluation:
    config.validate()
    color_similarity = color_similarity_to_profile(
        features.color_histogram,
        profile,
        top_k=config.color_top_k,
    )
    hard_reason = _first_hard_reject(
        measurements,
        features,
        color_similarity,
        config,
    )

    depth_parts = [
        (
            _range_score(
                measurements.median_depth_m,
                config.min_depth_m,
                config.preferred_depth_min_m,
                config.preferred_depth_max_m,
                config.max_depth_m,
            ),
            1.0,
        ),
        (
            _higher_is_better(
                measurements.valid_depth_ratio,
                config.min_valid_depth_ratio,
                config.valid_depth_good_ratio,
            ),
            1.0,
        ),
        (
            _lower_is_better(
                measurements.depth_std_m,
                config.depth_std_good_m,
                config.max_depth_std_m,
            ),
            1.0,
        ),
        (clamp01(measurements.proposal_score), 0.75),
    ]
    if measurements.foreground_height_m > 0.0:
        depth_parts.append(
            (
                _range_score(
                    measurements.foreground_height_m,
                    max(0.0, config.min_foreground_height_m),
                    config.preferred_foreground_min_m,
                    config.preferred_foreground_max_m,
                    config.max_foreground_height_m,
                ),
                1.0,
            )
        )
    depth_score = _weighted_average(depth_parts)

    quality_score = _weighted_average(
        [
            (
                _higher_is_better(
                    float(min(features.width, features.height)),
                    float(config.min_crop_side_px),
                    96.0,
                ),
                1.0,
            ),
            (
                _higher_is_better(
                    features.sharpness,
                    config.min_sharpness,
                    config.sharpness_good,
                ),
                1.0,
            ),
            (_lower_is_better(features.dark_ratio, 0.0, config.max_dark_ratio), 0.5),
            (
                _lower_is_better(
                    features.bright_clip_ratio,
                    0.0,
                    config.max_bright_clip_ratio,
                ),
                0.5,
            ),
            (
                _lower_is_better(
                    measurements.sync_offset_abs_sec,
                    config.sync_good_sec,
                    config.max_sync_offset_sec,
                ),
                0.75,
            ),
            (1.0 if measurements.size_limit_met else 0.75, 0.25),
        ]
    )

    bbox_height = max(1, measurements.bbox_height_px)
    aspect_ratio = measurements.bbox_width_px / float(bbox_height)
    shape_score = _weighted_average(
        [
            (
                _range_score(
                    aspect_ratio,
                    config.hard_aspect_ratio_min,
                    config.preferred_aspect_ratio_min,
                    config.preferred_aspect_ratio_max,
                    config.hard_aspect_ratio_max,
                ),
                1.0,
            ),
            (
                _range_score(
                    measurements.fill_ratio,
                    config.min_fill_ratio,
                    config.preferred_fill_ratio_min,
                    config.preferred_fill_ratio_max,
                    1.0,
                ),
                1.0,
            ),
            (
                _range_score(
                    features.edge_density,
                    0.0,
                    config.preferred_edge_density_min,
                    config.preferred_edge_density_max,
                    config.max_edge_density,
                ),
                1.0,
            ),
        ]
    )

    physical_score: Optional[float] = None
    physical_width = measurements.estimated_width_m
    physical_height = measurements.estimated_height_m
    if physical_width is not None and physical_height is not None:
        short_side, long_side = sorted((physical_width, physical_height))
        physical_score = _weighted_average(
            [
                (
                    _range_score(
                        short_side,
                        config.physical_short_side_min_m,
                        config.physical_short_side_preferred_min_m,
                        config.physical_short_side_preferred_max_m,
                        config.physical_short_side_max_m,
                    ),
                    1.0,
                ),
                (
                    _range_score(
                        long_side,
                        config.physical_long_side_min_m,
                        config.physical_long_side_preferred_min_m,
                        config.physical_long_side_preferred_max_m,
                        config.physical_long_side_max_m,
                    ),
                    1.0,
                ),
            ]
        )

    active_scores: list[tuple[float, float]] = [
        (depth_score, config.depth_weight),
        (quality_score, config.quality_weight),
        (shape_score, config.shape_weight),
    ]
    if color_similarity is not None:
        active_scores.append((color_similarity, config.color_weight))
    if physical_score is not None:
        active_scores.append((physical_score, config.physical_size_weight))
    filter_score = _weighted_average(active_scores)

    if hard_reason is not None:
        accepted = False
        reject_stage = "hard"
        reject_reason = hard_reason
    elif config.enforce_soft_score and filter_score < config.min_filter_score:
        accepted = False
        reject_stage = "soft"
        reject_reason = "filter_score_below_threshold"
    else:
        accepted = True
        reject_stage = ""
        reject_reason = ""
    return FilterEvaluation(
        accepted=accepted,
        reject_stage=reject_stage,
        reject_reason=reject_reason,
        filter_score=filter_score,
        depth_score=depth_score,
        quality_score=quality_score,
        color_score=color_similarity,
        shape_score=shape_score,
        physical_size_score=physical_score,
        color_similarity=color_similarity,
        aspect_ratio=aspect_ratio,
    )


def decode_compressed_image(data: bytes | bytearray | Sequence[int]) -> np.ndarray:
    encoded = np.frombuffer(bytes(data), dtype=np.uint8)
    if encoded.size == 0:
        raise ValueError("compressed image data is empty")
    image = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
    if image is None or image.size == 0:
        raise ValueError("JPEG decoding failed")
    return image
