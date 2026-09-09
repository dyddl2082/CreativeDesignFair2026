"""Depth/objectness gate for rejecting mirror-like RGB candidates before DINO.

The gate intentionally uses only metadata already carried by RgbCandidateCrop.
It does not inspect target identity and it does not change DINO thresholds.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Optional


@dataclass(frozen=True)
class ReflectionGateConfig:
    enabled: bool = True
    require_plane: bool = True
    require_foreground_height: bool = True
    require_foreground_mask: bool = True
    min_foreground_height_m: float = 0.008
    min_valid_depth_ratio: float = 0.60
    max_depth_std_m: float = 0.060
    min_mask_fill_ratio: float = 0.03
    max_mask_fill_ratio: float = 0.98

    def validate(self) -> None:
        if self.min_foreground_height_m < 0.0:
            raise ValueError("min_foreground_height_m cannot be negative")
        if not 0.0 <= self.min_valid_depth_ratio <= 1.0:
            raise ValueError("min_valid_depth_ratio must be in [0, 1]")
        if self.max_depth_std_m <= 0.0:
            raise ValueError("max_depth_std_m must be positive")
        if not 0.0 <= self.min_mask_fill_ratio <= 1.0:
            raise ValueError("min_mask_fill_ratio must be in [0, 1]")
        if not 0.0 <= self.max_mask_fill_ratio <= 1.0:
            raise ValueError("max_mask_fill_ratio must be in [0, 1]")
        if self.min_mask_fill_ratio > self.max_mask_fill_ratio:
            raise ValueError("mask fill ratio range is invalid")


@dataclass(frozen=True)
class ReflectionEvidence:
    plane_found: bool
    foreground_height_valid: bool
    foreground_height_m: float
    valid_depth_ratio: float
    depth_std_m: float
    foreground_mask_available: bool
    mask_fill_ratio: float


def reflection_reject_reason(
    evidence: ReflectionEvidence,
    config: ReflectionGateConfig,
) -> Optional[str]:
    """Return a stable reject code, or None when the candidate is usable."""
    if not config.enabled:
        return None

    if config.require_plane and not evidence.plane_found:
        return "reflection_plane_unavailable"

    if config.require_foreground_height and not evidence.foreground_height_valid:
        return "reflection_height_unavailable"

    if evidence.foreground_height_valid:
        if not math.isfinite(evidence.foreground_height_m):
            return "reflection_height_invalid"
        if evidence.foreground_height_m < config.min_foreground_height_m:
            return "reflection_height_too_low"

    if not math.isfinite(evidence.valid_depth_ratio):
        return "reflection_depth_support_invalid"
    if evidence.valid_depth_ratio < config.min_valid_depth_ratio:
        return "reflection_depth_support_low"

    if not math.isfinite(evidence.depth_std_m) or evidence.depth_std_m < 0.0:
        return "reflection_depth_variation_invalid"
    if evidence.depth_std_m > config.max_depth_std_m:
        return "reflection_depth_variation_high"

    if config.require_foreground_mask and not evidence.foreground_mask_available:
        return "reflection_mask_unavailable"

    if evidence.foreground_mask_available:
        if not math.isfinite(evidence.mask_fill_ratio):
            return "reflection_mask_fill_invalid"
        if evidence.mask_fill_ratio < config.min_mask_fill_ratio:
            return "reflection_mask_fill_low"
        if evidence.mask_fill_ratio > config.max_mask_fill_ratio:
            return "reflection_mask_fill_high"

    return None
