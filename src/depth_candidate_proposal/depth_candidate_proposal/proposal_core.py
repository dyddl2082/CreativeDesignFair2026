"""Pure OpenCV/Numpy implementation of aligned-depth candidate generation.

The module is intentionally independent from ROS so that the segmentation
algorithm can be unit-tested on a development PC.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence

import cv2
import numpy as np


@dataclass(frozen=True)
class CameraIntrinsics:
    """Pinhole intrinsics for the image used by the aligned depth stream."""

    width: int
    height: int
    fx: float
    fy: float
    cx: float
    cy: float

    def scaled_to(self, width: int, height: int) -> "CameraIntrinsics":
        """Scale intrinsics when CameraInfo and image dimensions differ."""
        if self.width <= 0 or self.height <= 0:
            raise ValueError("CameraInfo width and height must be positive")
        scale_x = float(width) / float(self.width)
        scale_y = float(height) / float(self.height)
        return CameraIntrinsics(
            width=width,
            height=height,
            fx=self.fx * scale_x,
            fy=self.fy * scale_y,
            cx=self.cx * scale_x,
            cy=self.cy * scale_y,
        )


@dataclass(frozen=True)
class ProposalConfig:
    """Configuration for one-frame depth proposal generation."""

    min_depth_m: float = 0.18
    max_depth_m: float = 1.50

    enable_plane_removal: bool = True
    plane_sample_stride: int = 4
    plane_ransac_iterations: int = 70
    plane_distance_threshold_m: float = 0.012
    plane_min_inlier_ratio: float = 0.25
    plane_clearance_m: float = 0.025
    plane_max_foreground_m: float = 0.60
    max_plane_samples: int = 16000

    fallback_background_percentile: float = 70.0
    fallback_clearance_m: float = 0.035

    roi_top_ratio: float = 0.00
    roi_bottom_ratio: float = 1.00
    roi_left_ratio: float = 0.00
    roi_right_ratio: float = 1.00

    close_kernel_px: int = 9
    open_kernel_px: int = 3

    min_component_area_px: int = 300
    max_component_area_ratio: float = 0.28
    min_bbox_width_px: int = 14
    min_bbox_height_px: int = 14
    min_fill_ratio: float = 0.10
    min_valid_depth_ratio: float = 0.55
    bbox_padding_px: int = 8
    border_margin_px: int = 2
    reject_border_components: bool = False
    max_candidates: int = 12

    depth_std_score_scale_m: float = 0.060
    random_seed: int = 17

    def validate(self) -> None:
        if not (0.0 < self.min_depth_m < self.max_depth_m):
            raise ValueError("Expected 0 < min_depth_m < max_depth_m")
        if self.plane_sample_stride < 1:
            raise ValueError("plane_sample_stride must be >= 1")
        if self.plane_ransac_iterations < 1:
            raise ValueError("plane_ransac_iterations must be >= 1")
        if self.max_plane_samples < 3:
            raise ValueError("max_plane_samples must be >= 3")
        if not (0.0 <= self.plane_min_inlier_ratio <= 1.0):
            raise ValueError("plane_min_inlier_ratio must be in [0, 1]")
        if not (0.0 < self.fallback_background_percentile < 100.0):
            raise ValueError("fallback_background_percentile must be in (0, 100)")
        ratios = (
            self.roi_top_ratio,
            self.roi_bottom_ratio,
            self.roi_left_ratio,
            self.roi_right_ratio,
        )
        if any(value < 0.0 or value > 1.0 for value in ratios):
            raise ValueError("ROI ratios must be in [0, 1]")
        if self.roi_top_ratio >= self.roi_bottom_ratio:
            raise ValueError("roi_top_ratio must be smaller than roi_bottom_ratio")
        if self.roi_left_ratio >= self.roi_right_ratio:
            raise ValueError("roi_left_ratio must be smaller than roi_right_ratio")
        if self.min_component_area_px < 1:
            raise ValueError("min_component_area_px must be positive")
        if not (0.0 < self.max_component_area_ratio <= 1.0):
            raise ValueError("max_component_area_ratio must be in (0, 1]")
        if self.max_candidates < 1:
            raise ValueError("max_candidates must be positive")


@dataclass(frozen=True)
class PlaneModel:
    """Plane ax + by + cz + d = 0 in the camera optical frame."""

    coefficients: np.ndarray
    inlier_ratio: float


@dataclass(frozen=True)
class DepthCandidateData:
    """Frame-local proposal data returned by the core algorithm."""

    component_label: int
    roi_x: int
    roi_y: int
    roi_width: int
    roi_height: int
    center_x: float
    center_y: float
    median_depth_m: float
    near_depth_m: float
    far_depth_m: float
    depth_std_m: float
    valid_depth_ratio: float
    fill_ratio: float
    area_ratio: float
    foreground_height_m: float
    proposal_score: float
    touches_border: bool


@dataclass(frozen=True)
class ProposalResult:
    mask: np.ndarray
    candidates: Sequence[DepthCandidateData]
    plane: Optional[PlaneModel]
    foreground_height_map_m: np.ndarray
    fallback_background_depth_m: float


def depth_image_to_meters(
    depth_image: np.ndarray,
    encoding: str,
    depth_scale_m: float,
) -> np.ndarray:
    """Convert ROS depth encodings to float32 meters with NaNs for invalid data."""
    if depth_image.ndim != 2:
        raise ValueError(f"Expected a single-channel depth image, got {depth_image.shape}")

    normalized_encoding = encoding.upper()
    if normalized_encoding in {"16UC1", "MONO16"}:
        if depth_scale_m <= 0.0:
            raise ValueError("depth_scale_m must be positive for 16-bit depth images")
        depth_m = depth_image.astype(np.float32, copy=False) * np.float32(depth_scale_m)
    elif normalized_encoding == "32FC1":
        depth_m = depth_image.astype(np.float32, copy=True)
    else:
        raise ValueError(
            f"Unsupported depth encoding '{encoding}'. Expected 16UC1, mono16, or 32FC1."
        )

    invalid = (~np.isfinite(depth_m)) | (depth_m <= 0.0)
    depth_m = depth_m.copy()
    depth_m[invalid] = np.nan
    return depth_m


def _roi_mask(height: int, width: int, cfg: ProposalConfig) -> np.ndarray:
    mask = np.zeros((height, width), dtype=bool)
    y0 = int(round(cfg.roi_top_ratio * height))
    y1 = int(round(cfg.roi_bottom_ratio * height))
    x0 = int(round(cfg.roi_left_ratio * width))
    x1 = int(round(cfg.roi_right_ratio * width))
    y0 = int(np.clip(y0, 0, height - 1))
    y1 = int(np.clip(y1, y0 + 1, height))
    x0 = int(np.clip(x0, 0, width - 1))
    x1 = int(np.clip(x1, x0 + 1, width))
    mask[y0:y1, x0:x1] = True
    return mask


def _sample_points(
    depth_m: np.ndarray,
    valid_mask: np.ndarray,
    intrinsics: CameraIntrinsics,
    cfg: ProposalConfig,
) -> np.ndarray:
    stride = cfg.plane_sample_stride
    sampled_depth = depth_m[::stride, ::stride]
    sampled_valid = valid_mask[::stride, ::stride]
    rows, cols = np.nonzero(sampled_valid)
    if rows.size < 3:
        return np.empty((0, 3), dtype=np.float32)

    z = sampled_depth[rows, cols].astype(np.float32, copy=False)
    u = cols.astype(np.float32) * float(stride)
    v = rows.astype(np.float32) * float(stride)
    x = (u - intrinsics.cx) * z / intrinsics.fx
    y = (v - intrinsics.cy) * z / intrinsics.fy
    points = np.column_stack((x, y, z)).astype(np.float32, copy=False)

    if points.shape[0] > cfg.max_plane_samples:
        rng = np.random.default_rng(cfg.random_seed)
        indices = rng.choice(points.shape[0], cfg.max_plane_samples, replace=False)
        points = points[indices]
    return points


def fit_dominant_plane_ransac(
    depth_m: np.ndarray,
    valid_mask: np.ndarray,
    intrinsics: CameraIntrinsics,
    cfg: ProposalConfig,
) -> Optional[PlaneModel]:
    """Fit the largest planar surface using deterministic RANSAC."""
    points = _sample_points(depth_m, valid_mask, intrinsics, cfg)
    if points.shape[0] < 3:
        return None

    rng = np.random.default_rng(cfg.random_seed)
    best_inliers: Optional[np.ndarray] = None
    best_count = 0

    for _ in range(cfg.plane_ransac_iterations):
        sample_indices = rng.choice(points.shape[0], 3, replace=False)
        p0, p1, p2 = points[sample_indices]
        normal = np.cross(p1 - p0, p2 - p0)
        norm = float(np.linalg.norm(normal))
        if norm < 1e-6:
            continue
        normal = normal / norm
        d = -float(np.dot(normal, p0))
        distances = np.abs(points @ normal + d)
        inliers = distances <= cfg.plane_distance_threshold_m
        count = int(np.count_nonzero(inliers))
        if count > best_count:
            best_count = count
            best_inliers = inliers

    if best_inliers is None:
        return None

    inlier_ratio = float(best_count) / float(points.shape[0])
    if inlier_ratio < cfg.plane_min_inlier_ratio:
        return None

    inlier_points = points[best_inliers]
    centroid = np.mean(inlier_points, axis=0)
    centered = inlier_points - centroid
    try:
        _, _, vh = np.linalg.svd(centered, full_matrices=False)
    except np.linalg.LinAlgError:
        return None

    normal = vh[-1].astype(np.float64, copy=False)
    norm = float(np.linalg.norm(normal))
    if norm < 1e-9:
        return None
    normal = normal / norm
    d = -float(np.dot(normal, centroid))
    coefficients = np.array([normal[0], normal[1], normal[2], d], dtype=np.float32)
    return PlaneModel(coefficients=coefficients, inlier_ratio=inlier_ratio)


def _predict_plane_depth(
    shape: tuple[int, int],
    intrinsics: CameraIntrinsics,
    plane: PlaneModel,
) -> np.ndarray:
    height, width = shape
    a, b, c, d = [float(value) for value in plane.coefficients]
    u = np.arange(width, dtype=np.float32)
    v = np.arange(height, dtype=np.float32)
    ray_x = (u - intrinsics.cx) / intrinsics.fx
    ray_y = (v - intrinsics.cy) / intrinsics.fy
    denominator = a * ray_x[np.newaxis, :] + b * ray_y[:, np.newaxis] + c

    predicted = np.full((height, width), np.nan, dtype=np.float32)
    valid_denominator = np.abs(denominator) > 1e-6
    predicted[valid_denominator] = -d / denominator[valid_denominator]
    predicted[(~np.isfinite(predicted)) | (predicted <= 0.0)] = np.nan
    return predicted


def _cleanup_mask(mask: np.ndarray, cfg: ProposalConfig) -> np.ndarray:
    mask_u8 = np.where(mask, 255, 0).astype(np.uint8)

    if cfg.close_kernel_px >= 2:
        size = cfg.close_kernel_px | 1
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (size, size))
        mask_u8 = cv2.morphologyEx(mask_u8, cv2.MORPH_CLOSE, kernel)

    if cfg.open_kernel_px >= 2:
        size = cfg.open_kernel_px | 1
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (size, size))
        mask_u8 = cv2.morphologyEx(mask_u8, cv2.MORPH_OPEN, kernel)

    return mask_u8


def _proposal_score(
    *,
    area: int,
    image_area: int,
    fill_ratio: float,
    valid_depth_ratio: float,
    depth_std_m: float,
    foreground_height_m: float,
    plane_found: bool,
    touches_border: bool,
    cfg: ProposalConfig,
) -> float:
    fill_denom = max(0.70 - cfg.min_fill_ratio, 1e-6)
    fill_score = float(np.clip((fill_ratio - cfg.min_fill_ratio) / fill_denom, 0.0, 1.0))
    valid_score = float(np.clip(valid_depth_ratio, 0.0, 1.0))
    consistency_score = float(
        np.exp(-max(depth_std_m, 0.0) / max(cfg.depth_std_score_scale_m, 1e-6))
    )

    target_area = max(int(image_area * 0.04), cfg.min_component_area_px + 1)
    area_score = float(
        np.clip(
            np.log1p(max(area, 0) / cfg.min_component_area_px)
            / np.log1p(target_area / cfg.min_component_area_px),
            0.0,
            1.0,
        )
    )

    if plane_found:
        height_score = float(
            np.clip(
                foreground_height_m / max(cfg.plane_clearance_m * 4.0, 1e-6),
                0.0,
                1.0,
            )
        )
    else:
        height_score = 0.50

    score = (
        0.25 * fill_score
        + 0.25 * valid_score
        + 0.23 * consistency_score
        + 0.17 * height_score
        + 0.10 * area_score
    )
    if touches_border:
        score *= 0.75
    return float(np.clip(score, 0.0, 1.0))


def _extract_candidates(
    mask_u8: np.ndarray,
    depth_m: np.ndarray,
    foreground_height_map_m: np.ndarray,
    plane_found: bool,
    cfg: ProposalConfig,
) -> list[DepthCandidateData]:
    height, width = depth_m.shape
    image_area = height * width
    max_area = int(round(cfg.max_component_area_ratio * image_area))

    count, labels, stats, centroids = cv2.connectedComponentsWithStats(
        mask_u8,
        connectivity=8,
    )
    candidates: list[DepthCandidateData] = []

    for label in range(1, count):
        x = int(stats[label, cv2.CC_STAT_LEFT])
        y = int(stats[label, cv2.CC_STAT_TOP])
        box_width = int(stats[label, cv2.CC_STAT_WIDTH])
        box_height = int(stats[label, cv2.CC_STAT_HEIGHT])
        area = int(stats[label, cv2.CC_STAT_AREA])

        if area < cfg.min_component_area_px or area > max_area:
            continue
        if box_width < cfg.min_bbox_width_px or box_height < cfg.min_bbox_height_px:
            continue

        fill_ratio = float(area) / float(max(box_width * box_height, 1))
        if fill_ratio < cfg.min_fill_ratio:
            continue

        component_local = labels[y : y + box_height, x : x + box_width] == label
        depth_local = depth_m[y : y + box_height, x : x + box_width]
        valid_local = component_local & np.isfinite(depth_local) & (depth_local > 0.0)
        valid_count = int(np.count_nonzero(valid_local))
        valid_depth_ratio = float(valid_count) / float(max(area, 1))
        if valid_depth_ratio < cfg.min_valid_depth_ratio or valid_count < 3:
            continue

        values = depth_local[valid_local].astype(np.float32, copy=False)
        median_depth = float(np.median(values))
        near_depth = float(np.percentile(values, 10.0))
        far_depth = float(np.percentile(values, 90.0))
        median_abs_deviation = float(np.median(np.abs(values - median_depth)))
        robust_std = 1.4826 * median_abs_deviation

        if plane_found:
            height_local = foreground_height_map_m[y : y + box_height, x : x + box_width]
            valid_height = valid_local & np.isfinite(height_local)
            if np.any(valid_height):
                foreground_height = float(np.median(height_local[valid_height]))
            else:
                foreground_height = 0.0
        else:
            foreground_height = 0.0

        touches_border = (
            x <= cfg.border_margin_px
            or y <= cfg.border_margin_px
            or x + box_width >= width - cfg.border_margin_px
            or y + box_height >= height - cfg.border_margin_px
        )
        if cfg.reject_border_components and touches_border:
            continue

        padding = cfg.bbox_padding_px
        roi_x = max(0, x - padding)
        roi_y = max(0, y - padding)
        roi_x2 = min(width, x + box_width + padding)
        roi_y2 = min(height, y + box_height + padding)

        score = _proposal_score(
            area=area,
            image_area=image_area,
            fill_ratio=fill_ratio,
            valid_depth_ratio=valid_depth_ratio,
            depth_std_m=robust_std,
            foreground_height_m=foreground_height,
            plane_found=plane_found,
            touches_border=touches_border,
            cfg=cfg,
        )

        candidates.append(
            DepthCandidateData(
                component_label=label,
                roi_x=roi_x,
                roi_y=roi_y,
                roi_width=roi_x2 - roi_x,
                roi_height=roi_y2 - roi_y,
                center_x=float(centroids[label, 0]),
                center_y=float(centroids[label, 1]),
                median_depth_m=median_depth,
                near_depth_m=near_depth,
                far_depth_m=far_depth,
                depth_std_m=robust_std,
                valid_depth_ratio=valid_depth_ratio,
                fill_ratio=fill_ratio,
                area_ratio=float(area) / float(image_area),
                foreground_height_m=foreground_height,
                proposal_score=score,
                touches_border=touches_border,
            )
        )

    candidates.sort(key=lambda candidate: candidate.proposal_score, reverse=True)
    return candidates[: cfg.max_candidates]


def generate_depth_proposals(
    depth_m: np.ndarray,
    intrinsics: Optional[CameraIntrinsics],
    cfg: ProposalConfig,
) -> ProposalResult:
    """Generate object-like 2D proposals from one aligned depth frame."""
    cfg.validate()
    if depth_m.ndim != 2:
        raise ValueError("depth_m must be a two-dimensional array")

    height, width = depth_m.shape
    finite_range = (
        np.isfinite(depth_m)
        & (depth_m >= cfg.min_depth_m)
        & (depth_m <= cfg.max_depth_m)
    )
    working_roi = _roi_mask(height, width, cfg)
    valid_mask = finite_range & working_roi

    plane: Optional[PlaneModel] = None
    foreground_height_map = np.zeros_like(depth_m, dtype=np.float32)
    fallback_background_depth_m = float("nan")

    if cfg.enable_plane_removal and intrinsics is not None:
        scaled_intrinsics = intrinsics.scaled_to(width, height)
        plane = fit_dominant_plane_ransac(
            depth_m,
            valid_mask,
            scaled_intrinsics,
            cfg,
        )
        if plane is not None:
            predicted_depth = _predict_plane_depth(
                depth_m.shape,
                scaled_intrinsics,
                plane,
            )
            foreground_height_map = predicted_depth - depth_m
            foreground_mask = (
                valid_mask
                & np.isfinite(predicted_depth)
                & (foreground_height_map >= cfg.plane_clearance_m)
                & (foreground_height_map <= cfg.plane_max_foreground_m)
            )
        else:
            foreground_mask = np.zeros_like(valid_mask)
    else:
        foreground_mask = np.zeros_like(valid_mask)

    if plane is None:
        valid_values = depth_m[valid_mask]
        if valid_values.size > 0:
            fallback_background_depth_m = float(
                np.percentile(valid_values, cfg.fallback_background_percentile)
            )
            foreground_mask = valid_mask & (
                depth_m <= fallback_background_depth_m - cfg.fallback_clearance_m
            )
        else:
            foreground_mask = np.zeros_like(valid_mask)

    cleaned_mask = _cleanup_mask(foreground_mask, cfg)
    candidates = _extract_candidates(
        cleaned_mask,
        depth_m,
        foreground_height_map,
        plane is not None,
        cfg,
    )
    return ProposalResult(
        mask=cleaned_mask,
        candidates=candidates,
        plane=plane,
        foreground_height_map_m=foreground_height_map,
        fallback_background_depth_m=fallback_background_depth_m,
    )


def make_debug_image(
    depth_m: np.ndarray,
    result: ProposalResult,
    cfg: ProposalConfig,
) -> np.ndarray:
    """Create a compact colorized depth preview with proposal boxes."""
    valid = np.isfinite(depth_m)
    clipped = np.clip(depth_m, cfg.min_depth_m, cfg.max_depth_m)
    normalized = np.zeros(depth_m.shape, dtype=np.uint8)
    span = max(cfg.max_depth_m - cfg.min_depth_m, 1e-6)
    normalized[valid] = np.clip(
        255.0 * (cfg.max_depth_m - clipped[valid]) / span,
        0.0,
        255.0,
    ).astype(np.uint8)
    preview = cv2.applyColorMap(normalized, cv2.COLORMAP_TURBO)
    preview[~valid] = 0

    mask_outline = cv2.Canny(result.mask, 50, 150)
    preview[mask_outline > 0] = (255, 255, 255)

    for index, candidate in enumerate(result.candidates):
        x1 = candidate.roi_x
        y1 = candidate.roi_y
        x2 = x1 + candidate.roi_width
        y2 = y1 + candidate.roi_height
        cv2.rectangle(preview, (x1, y1), (x2, y2), (0, 255, 0), 2)
        label = (
            f"#{index} {candidate.median_depth_m:.2f}m "
            f"s={candidate.proposal_score:.2f}"
        )
        text_y = max(16, y1 - 5)
        cv2.putText(
            preview,
            label,
            (x1, text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )
        cv2.putText(
            preview,
            label,
            (x1, text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (0, 0, 0),
            1,
            cv2.LINE_AA,
        )

    if result.plane is not None:
        status = f"plane=yes inliers={result.plane.inlier_ratio:.2f}"
    elif np.isfinite(result.fallback_background_depth_m):
        status = f"plane=no fallback={result.fallback_background_depth_m:.2f}m"
    else:
        status = "plane=no no-valid-depth"
    cv2.putText(
        preview,
        status,
        (8, 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.52,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )
    cv2.putText(
        preview,
        status,
        (8, 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.52,
        (0, 0, 0),
        1,
        cv2.LINE_AA,
    )
    return preview
