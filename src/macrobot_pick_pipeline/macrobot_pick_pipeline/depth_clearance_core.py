"""Robust central-corridor clearance estimate from aligned depth."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Optional

import numpy as np


@dataclass(frozen=True)
class ClearanceEstimate:
    available: bool
    clearance_m: float
    valid_fraction: float
    sample_count: int
    reason: str = ""


def estimate_clearance(
    depth_m: np.ndarray,
    *,
    width_fraction: float = 0.28,
    y_min_fraction: float = 0.35,
    y_max_fraction: float = 0.82,
    minimum_depth_m: float = 0.05,
    maximum_depth_m: float = 4.0,
    percentile: float = 10.0,
    minimum_valid_fraction: float = 0.05,
) -> ClearanceEstimate:
    array = np.asarray(depth_m, dtype=np.float32)
    if array.ndim != 2 or array.size == 0:
        return ClearanceEstimate(False, 0.0, 0.0, 0, "invalid_depth_shape")
    height, width = array.shape
    half = max(1, int(round(width * max(0.02, min(1.0, width_fraction)) / 2.0)))
    center = width // 2
    x0 = max(0, center - half)
    x1 = min(width, center + half)
    y0 = max(0, min(height - 1, int(round(height * y_min_fraction))))
    y1 = max(y0 + 1, min(height, int(round(height * y_max_fraction))))
    roi = array[y0:y1, x0:x1]
    valid = np.isfinite(roi) & (roi >= minimum_depth_m) & (roi <= maximum_depth_m)
    count = int(np.count_nonzero(valid))
    fraction = count / float(max(1, roi.size))
    if count == 0 or fraction < max(0.0, minimum_valid_fraction):
        return ClearanceEstimate(False, 0.0, fraction, count, "insufficient_valid_depth")
    value = float(np.percentile(roi[valid], max(0.0, min(100.0, percentile))))
    if not math.isfinite(value):
        return ClearanceEstimate(False, 0.0, fraction, count, "non_finite_clearance")
    return ClearanceEstimate(True, value, fraction, count, "")
