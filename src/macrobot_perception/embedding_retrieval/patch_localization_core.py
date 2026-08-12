"""Pure DINOv2 patch-token localization helpers.

The global descriptor decides *what* the candidate is.  Patch tokens refine
*where inside the crop* the registered object is.  The functions in this file
have no ROS dependency so they can be unit tested off-robot.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Optional, Sequence, Tuple

import cv2
import numpy as np


@dataclass(frozen=True)
class SquarePadGeometry:
    source_width: int
    source_height: int
    padded_side: int
    left: int
    top: int


@dataclass(frozen=True)
class PatchLocalization:
    available: bool
    method: str = "dinov2_patch_margin"
    quality: float = 0.0
    peak_positive: float = -1.0
    peak_margin: float = -1.0
    center_x_source: float = 0.0
    center_y_source: float = 0.0
    bbox_x_source: float = 0.0
    bbox_y_source: float = 0.0
    bbox_width_source: float = 0.0
    bbox_height_source: float = 0.0
    mask_area_source_px: int = 0
    orientation_deg: float = 0.0
    orientation_class: str = "unknown"
    orientation_quality: float = 0.0
    reason: str = ""


def square_pad_geometry(width: int, height: int, padding_ratio: float) -> SquarePadGeometry:
    if width <= 0 or height <= 0:
        raise ValueError("source dimensions must be positive")
    extra = int(round(max(width, height) * max(float(padding_ratio), 0.0)))
    side = max(width, height) + 2 * extra
    left = (side - width) // 2
    top = (side - height) // 2
    return SquarePadGeometry(width, height, side, left, top)


def _normalize_rows(values: np.ndarray) -> np.ndarray:
    array = np.asarray(values, dtype=np.float32)
    if array.ndim == 1:
        array = array.reshape(1, -1)
    norms = np.linalg.norm(array, axis=1, keepdims=True)
    return array / np.maximum(norms, 1e-12)


def patch_score_maps(
    patch_embeddings: np.ndarray,
    positive_embeddings: np.ndarray,
    negative_embeddings: Optional[np.ndarray],
    *,
    negative_weight: float = 1.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return per-patch best positive, best negative, and localization margin."""

    patches = np.asarray(patch_embeddings, dtype=np.float32)
    if patches.ndim != 3:
        raise ValueError("patch_embeddings must have shape [grid_h, grid_w, dim]")
    grid_h, grid_w, dimension = patches.shape
    patch_rows = _normalize_rows(patches.reshape(-1, dimension))
    positives = _normalize_rows(positive_embeddings)
    if positives.ndim != 2 or positives.shape[0] == 0 or positives.shape[1] != dimension:
        raise ValueError("positive embeddings are empty or dimension-mismatched")
    positive_scores = patch_rows @ positives.T
    positive_best = np.max(positive_scores, axis=1)

    negative_best = np.full_like(positive_best, -1.0)
    if negative_embeddings is not None:
        negatives = np.asarray(negative_embeddings, dtype=np.float32)
        if negatives.ndim == 2 and negatives.shape[0] > 0:
            if negatives.shape[1] != dimension:
                raise ValueError("negative embedding dimension mismatch")
            negatives = _normalize_rows(negatives)
            negative_best = np.max(patch_rows @ negatives.T, axis=1)

    margin = positive_best.copy()
    if np.any(negative_best > -0.999):
        margin = positive_best - float(negative_weight) * negative_best
    return (
        positive_best.reshape(grid_h, grid_w),
        negative_best.reshape(grid_h, grid_w),
        margin.reshape(grid_h, grid_w),
    )


def _orientation(points_xy: np.ndarray, weights: np.ndarray) -> tuple[float, str, float]:
    if points_xy.shape[0] < 2:
        return 0.0, "unknown", 0.0
    weights = np.asarray(weights, dtype=np.float64)
    weights = np.maximum(weights, 1e-8)
    weights /= np.sum(weights)
    mean = np.sum(points_xy * weights[:, None], axis=0)
    centered = points_xy - mean
    covariance = (centered * weights[:, None]).T @ centered
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    order = np.argsort(eigenvalues)[::-1]
    major = eigenvectors[:, order[0]]
    largest = float(max(eigenvalues[order[0]], 0.0))
    smallest = float(max(eigenvalues[order[-1]], 0.0))
    angle = math.degrees(math.atan2(float(major[1]), float(major[0]))) % 180.0
    quality = (largest - smallest) / max(largest + smallest, 1e-9)
    if angle <= 25.0 or angle >= 155.0:
        label = "horizontal"
    elif 65.0 <= angle <= 115.0:
        label = "vertical"
    else:
        label = "diagonal"
    return angle, label, float(np.clip(quality, 0.0, 1.0))


def _foreground_prior_grid(
    foreground_mask_source: Optional[np.ndarray],
    geometry: SquarePadGeometry,
    grid_width: int,
    grid_height: int,
) -> Optional[np.ndarray]:
    if foreground_mask_source is None or foreground_mask_source.size == 0:
        return None
    mask = np.asarray(foreground_mask_source)
    if mask.ndim == 3:
        mask = mask[:, :, 0]
    if mask.shape[:2] != (geometry.source_height, geometry.source_width):
        mask = cv2.resize(
            mask,
            (geometry.source_width, geometry.source_height),
            interpolation=cv2.INTER_NEAREST,
        )
    padded = np.zeros((geometry.padded_side, geometry.padded_side), dtype=np.uint8)
    y0 = geometry.top
    x0 = geometry.left
    padded[y0 : y0 + geometry.source_height, x0 : x0 + geometry.source_width] = (
        mask > 0
    ).astype(np.uint8)
    return cv2.resize(
        padded,
        (grid_width, grid_height),
        interpolation=cv2.INTER_AREA,
    ).astype(np.float32)


def localize_patch_tokens(
    *,
    patch_embeddings: np.ndarray,
    positive_embeddings: np.ndarray,
    negative_embeddings: Optional[np.ndarray],
    source_width: int,
    source_height: int,
    square_padding_ratio: float,
    foreground_mask_source: Optional[np.ndarray] = None,
    selection_quantile: float = 0.80,
    minimum_patch_margin: float = -0.10,
    minimum_component_patches: int = 2,
    maximum_component_area_ratio: float = 0.70,
    negative_weight: float = 1.0,
    foreground_prior_weight: float = 0.12,
) -> PatchLocalization:
    """Localize the most target-like connected patch region.

    ``source_*`` refers to the decoded RGB crop before square padding.  Returned
    coordinates are in that source-crop coordinate system.
    """

    try:
        geometry = square_pad_geometry(source_width, source_height, square_padding_ratio)
        positive_map, _, margin_map = patch_score_maps(
            patch_embeddings,
            positive_embeddings,
            negative_embeddings,
            negative_weight=negative_weight,
        )
    except (ValueError, cv2.error) as error:
        return PatchLocalization(False, reason=str(error))

    grid_h, grid_w = margin_map.shape
    finite = np.isfinite(margin_map)
    if not np.any(finite):
        return PatchLocalization(False, reason="patch_margin_unavailable")

    prior = _foreground_prior_grid(
        foreground_mask_source,
        geometry,
        grid_w,
        grid_h,
    )
    adjusted = margin_map.copy()
    if prior is not None:
        adjusted = adjusted + float(foreground_prior_weight) * np.clip(prior, 0.0, 1.0)

    quantile = float(np.clip(selection_quantile, 0.0, 1.0))
    threshold = max(
        float(np.quantile(adjusted[finite], quantile)),
        float(minimum_patch_margin),
    )
    binary = np.logical_and(finite, adjusted >= threshold).astype(np.uint8)
    if int(np.count_nonzero(binary)) < max(int(minimum_component_patches), 1):
        # Rescue the strongest patches. This is deterministic and still bounded.
        flat = np.argsort(adjusted.reshape(-1))[::-1]
        binary[:] = 0
        for index in flat[: max(int(minimum_component_patches), 1)]:
            y, x = divmod(int(index), grid_w)
            if finite[y, x]:
                binary[y, x] = 1

    component_count, labels, stats, _ = cv2.connectedComponentsWithStats(
        binary,
        connectivity=8,
    )
    if component_count <= 1:
        return PatchLocalization(False, reason="no_patch_component")

    best_label = -1
    best_score = -float("inf")
    max_area = max(1, int(round(grid_h * grid_w * maximum_component_area_ratio)))
    for label in range(1, component_count):
        area = int(stats[label, cv2.CC_STAT_AREA])
        if area < max(int(minimum_component_patches), 1) or area > max_area:
            continue
        component = labels == label
        mean_margin = float(np.mean(margin_map[component]))
        mean_positive = float(np.mean(positive_map[component]))
        overlap = float(np.mean(prior[component])) if prior is not None else 0.5
        score = mean_margin + 0.18 * mean_positive + 0.08 * overlap + 0.01 * math.sqrt(area)
        if score > best_score:
            best_score = score
            best_label = label

    if best_label < 0:
        return PatchLocalization(False, reason="no_component_passed_area_limits")

    component = labels == best_label
    ys, xs = np.nonzero(component)
    margins = margin_map[component]
    positives = positive_map[component]
    # Positive weights avoid unstable cancellation when margins are negative.
    weights = adjusted[component] - float(np.min(adjusted[component])) + 1e-4
    center_x_grid = float(np.average(xs + 0.5, weights=weights))
    center_y_grid = float(np.average(ys + 0.5, weights=weights))

    scale_x = geometry.padded_side / float(grid_w)
    scale_y = geometry.padded_side / float(grid_h)
    center_x_padded = center_x_grid * scale_x
    center_y_padded = center_y_grid * scale_y
    center_x_source = float(np.clip(center_x_padded - geometry.left, 0.0, source_width - 1.0))
    center_y_source = float(np.clip(center_y_padded - geometry.top, 0.0, source_height - 1.0))

    x_min_pad = float(np.min(xs) * scale_x)
    x_max_pad = float((np.max(xs) + 1) * scale_x)
    y_min_pad = float(np.min(ys) * scale_y)
    y_max_pad = float((np.max(ys) + 1) * scale_y)
    x0 = float(np.clip(x_min_pad - geometry.left, 0.0, source_width - 1.0))
    y0 = float(np.clip(y_min_pad - geometry.top, 0.0, source_height - 1.0))
    x1 = float(np.clip(x_max_pad - geometry.left, x0 + 1.0, float(source_width)))
    y1 = float(np.clip(y_max_pad - geometry.top, y0 + 1.0, float(source_height)))

    points_source = np.column_stack(
        (
            (xs + 0.5) * scale_x - geometry.left,
            (ys + 0.5) * scale_y - geometry.top,
        )
    )
    orientation_deg, orientation_class, orientation_quality = _orientation(
        points_source,
        weights,
    )

    selected_mean = float(np.mean(margins))
    outside = margin_map[np.logical_and(finite, ~component)]
    outside_median = float(np.median(outside)) if outside.size else selected_mean
    contrast = selected_mean - outside_median
    contrast_quality = 1.0 / (1.0 + math.exp(-8.0 * contrast))
    peak_margin = float(np.max(margins))
    peak_positive = float(np.max(positives))
    peak_quality = float(np.clip((peak_positive + 1.0) * 0.5, 0.0, 1.0))
    overlap_quality = float(np.mean(prior[component])) if prior is not None else 0.6
    quality = float(
        np.clip(
            0.55 * contrast_quality + 0.25 * peak_quality + 0.20 * overlap_quality,
            0.0,
            1.0,
        )
    )
    area_source = int(round(np.count_nonzero(component) * scale_x * scale_y))

    return PatchLocalization(
        available=True,
        quality=quality,
        peak_positive=peak_positive,
        peak_margin=peak_margin,
        center_x_source=center_x_source,
        center_y_source=center_y_source,
        bbox_x_source=x0,
        bbox_y_source=y0,
        bbox_width_source=max(1.0, x1 - x0),
        bbox_height_source=max(1.0, y1 - y0),
        mask_area_source_px=max(1, area_source),
        orientation_deg=orientation_deg,
        orientation_class=orientation_class,
        orientation_quality=orientation_quality,
    )


def source_to_color_coordinates(
    localization: PatchLocalization,
    *,
    source_width: int,
    source_height: int,
    crop_x: int,
    crop_y: int,
    crop_width: int,
    crop_height: int,
) -> PatchLocalization:
    """Map source-crop coordinates into the original color-image coordinate system."""

    if not localization.available:
        return localization
    if source_width <= 0 or source_height <= 0 or crop_width <= 0 or crop_height <= 0:
        return PatchLocalization(False, reason="invalid_crop_mapping_dimensions")
    sx = crop_width / float(source_width)
    sy = crop_height / float(source_height)
    return PatchLocalization(
        available=True,
        method=localization.method,
        quality=localization.quality,
        peak_positive=localization.peak_positive,
        peak_margin=localization.peak_margin,
        center_x_source=crop_x + localization.center_x_source * sx,
        center_y_source=crop_y + localization.center_y_source * sy,
        bbox_x_source=crop_x + localization.bbox_x_source * sx,
        bbox_y_source=crop_y + localization.bbox_y_source * sy,
        bbox_width_source=localization.bbox_width_source * sx,
        bbox_height_source=localization.bbox_height_source * sy,
        mask_area_source_px=int(round(localization.mask_area_source_px * sx * sy)),
        orientation_deg=localization.orientation_deg,
        orientation_class=localization.orientation_class,
        orientation_quality=localization.orientation_quality,
        reason=localization.reason,
    )
