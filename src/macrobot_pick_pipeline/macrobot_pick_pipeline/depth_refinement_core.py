"""Local aligned-depth decoding and robust point-depth refinement.

This module is pure Python/numpy.  The aligned depth image remains on the
Raspberry Pi; only the compact candidate crop and metadata cross to WSL2.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Optional

import numpy as np


@dataclass(frozen=True)
class DepthEstimate:
    available: bool
    depth_m: float = 0.0
    sample_count: int = 0
    std_m: float = float("inf")
    median_absolute_deviation_m: float = float("inf")
    source: str = "unavailable"
    reason: str = ""


def decode_depth_image(
    *,
    data: bytes | bytearray | memoryview,
    width: int,
    height: int,
    step: int,
    encoding: str,
    is_bigendian: bool,
    depth_scale_m: float = 0.001,
) -> np.ndarray:
    """Decode ROS ``sensor_msgs/Image`` depth bytes into float32 metres."""

    width = int(width)
    height = int(height)
    step = int(step)
    if width <= 0 or height <= 0 or step <= 0:
        raise ValueError("invalid image dimensions")
    normalized = str(encoding).strip().upper()
    endian = ">" if bool(is_bigendian) else "<"
    raw = memoryview(data)
    if normalized in {"16UC1", "MONO16", "TYPE_16UC1"}:
        dtype = np.dtype(endian + "u2")
        row_values = step // dtype.itemsize
        if row_values < width:
            raise ValueError("depth row step is smaller than image width")
        array = np.frombuffer(raw, dtype=dtype, count=height * row_values)
        array = array.reshape(height, row_values)[:, :width]
        result = array.astype(np.float32) * float(depth_scale_m)
        result[array == 0] = np.nan
        return result
    if normalized in {"32FC1", "TYPE_32FC1"}:
        dtype = np.dtype(endian + "f4")
        row_values = step // dtype.itemsize
        if row_values < width:
            raise ValueError("depth row step is smaller than image width")
        array = np.frombuffer(raw, dtype=dtype, count=height * row_values)
        result = array.reshape(height, row_values)[:, :width].astype(np.float32)
        result[~np.isfinite(result)] = np.nan
        result[result <= 0.0] = np.nan
        return result
    raise ValueError(f"unsupported depth encoding: {encoding}")


def refine_depth_window(
    depth_m: np.ndarray,
    *,
    center_x: float,
    center_y: float,
    radius_px: int = 4,
    minimum_depth_m: float = 0.08,
    maximum_depth_m: float = 2.0,
    minimum_samples: int = 8,
    fallback_depth_m: Optional[float] = None,
    inlier_band_m: float = 0.08,
    maximum_std_m: float = 0.05,
) -> DepthEstimate:
    """Estimate target depth from a small aligned-depth window.

    When the crop contains background or cables, a fallback candidate depth is
    used only as a robust inlier seed; the returned value is always recomputed
    from the Pi-local aligned depth image.
    """

    image = np.asarray(depth_m, dtype=np.float32)
    if image.ndim != 2 or image.size == 0:
        return DepthEstimate(False, reason="depth_image_empty")
    if not math.isfinite(float(center_x)) or not math.isfinite(float(center_y)):
        return DepthEstimate(False, reason="center_non_finite")
    x = int(round(float(center_x)))
    y = int(round(float(center_y)))
    radius = max(0, int(radius_px))
    x0 = max(0, x - radius)
    y0 = max(0, y - radius)
    x1 = min(image.shape[1], x + radius + 1)
    y1 = min(image.shape[0], y + radius + 1)
    if x0 >= x1 or y0 >= y1:
        return DepthEstimate(False, reason="center_outside_depth_image")
    values = image[y0:y1, x0:x1].reshape(-1)
    valid = values[
        np.isfinite(values)
        & (values >= float(minimum_depth_m))
        & (values <= float(maximum_depth_m))
    ]
    if fallback_depth_m is not None and math.isfinite(float(fallback_depth_m)):
        band = max(float(inlier_band_m), 0.0)
        near_seed = valid[np.abs(valid - float(fallback_depth_m)) <= band]
        if near_seed.size >= max(3, int(minimum_samples) // 2):
            valid = near_seed
    if valid.size < max(1, int(minimum_samples)):
        return DepthEstimate(
            False,
            sample_count=int(valid.size),
            reason="insufficient_valid_depth_samples",
        )
    median = float(np.median(valid))
    deviations = np.abs(valid - median)
    mad = float(np.median(deviations))
    robust_sigma = max(1.4826 * mad, 0.002)
    inliers = valid[deviations <= 3.5 * robust_sigma]
    if inliers.size >= max(1, int(minimum_samples)):
        valid = inliers
        median = float(np.median(valid))
        mad = float(np.median(np.abs(valid - median)))
    std = float(np.std(valid))
    if not math.isfinite(median):
        return DepthEstimate(False, reason="depth_median_non_finite")
    if std > float(maximum_std_m):
        return DepthEstimate(
            False,
            depth_m=median,
            sample_count=int(valid.size),
            std_m=std,
            median_absolute_deviation_m=mad,
            reason="depth_window_too_noisy",
        )
    return DepthEstimate(
        True,
        depth_m=median,
        sample_count=int(valid.size),
        std_m=std,
        median_absolute_deviation_m=mad,
        source="aligned_depth_window",
    )
