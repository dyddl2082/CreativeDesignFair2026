"""Orientation-domain helpers for MacRobot.

The perception stack may expose either an image-plane axial angle or a
base-frame depth-assisted 3-D axis.  Those values are not interchangeable.
This module normalises orientation metadata, compares only compatible domains,
and computes the shortest signed axial error for undirected axes.
"""

from __future__ import annotations

import math
from typing import Any, Mapping, Optional, Sequence, Tuple


PATCH_MARKER = "macrobot_3d_orientation_only_v1"


Vector3 = Tuple[float, float, float]


def _finite(value: Any) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("orientation value must be finite")
    return result


def axis_from_mapping(value: Any) -> Optional[Vector3]:
    """Return a normalised 3-D axis from a mapping/sequence, or ``None``."""

    if isinstance(value, Mapping):
        raw = (value.get("x"), value.get("y"), value.get("z"))
    elif isinstance(value, (list, tuple)) and len(value) == 3:
        raw = value
    else:
        return None
    try:
        axis = tuple(_finite(item) for item in raw)
    except (TypeError, ValueError):
        return None
    norm = math.sqrt(sum(component * component for component in axis))
    if norm <= 1e-12:
        return None
    normalised = tuple(component / norm for component in axis)
    return canonical_axis(normalised)


def canonical_axis(axis: Sequence[float]) -> Vector3:
    """Canonicalise an undirected axis without changing its physical line."""

    values = tuple(_finite(item) for item in axis)
    if len(values) != 3:
        raise ValueError("axis must contain three values")
    norm = math.sqrt(sum(component * component for component in values))
    if norm <= 1e-12:
        raise ValueError("axis has zero length")
    values = tuple(component / norm for component in values)
    # Use the first significant component to choose a deterministic sign.
    for component in values:
        if abs(component) <= 1e-12:
            continue
        if component < 0.0:
            values = tuple(-item for item in values)
        break
    return values  # type: ignore[return-value]


def axis_mapping(axis: Optional[Sequence[float]]) -> Optional[dict[str, float]]:
    if axis is None:
        return None
    normalised = canonical_axis(axis)
    return {
        "x": normalised[0],
        "y": normalised[1],
        "z": normalised[2],
    }


def axial_yaw_deg(axis: Sequence[float]) -> float:
    normalised = canonical_axis(axis)
    horizontal = math.hypot(normalised[0], normalised[1])
    if horizontal <= 1e-9:
        raise ValueError("axis has no usable horizontal projection")
    return math.degrees(math.atan2(normalised[1], normalised[0])) % 180.0


def signed_axial_axis_error_deg(
    current_axis: Sequence[float],
    reference_axis: Sequence[float],
) -> float:
    """Shortest signed yaw error between two undirected base-frame axes."""

    current = canonical_axis(current_axis)
    reference = canonical_axis(reference_axis)
    current_yaw = axial_yaw_deg(current)
    reference_yaw = axial_yaw_deg(reference)
    return ((current_yaw - reference_yaw + 90.0) % 180.0) - 90.0


def orientation_domain(mapping: Mapping[str, Any]) -> tuple[str, str]:
    return (
        str(mapping.get("coordinate_frame", "")).strip(),
        str(mapping.get("semantics", "")).strip(),
    )


def compatible_orientation_domains(
    current: Mapping[str, Any],
    reference: Mapping[str, Any],
) -> bool:
    current_frame, current_semantics = orientation_domain(current)
    reference_frame, reference_semantics = orientation_domain(reference)
    if not current_frame or not current_semantics:
        return not reference_frame and not reference_semantics
    return (
        current_frame == reference_frame
        and current_semantics == reference_semantics
    )


def normalise_orientation_mapping(value: Any) -> dict[str, Any]:
    """Sanitise an orientation payload while preserving domain metadata."""

    if not isinstance(value, Mapping):
        return {}
    try:
        angle = _finite(value.get("angle_deg", 0.0)) % 180.0
        quality = max(0.0, min(1.0, _finite(value.get("quality", 0.0))))
    except (TypeError, ValueError):
        return {}
    result: dict[str, Any] = {
        "angle_deg": angle,
        "class": str(value.get("class", "unknown")).strip() or "unknown",
        "quality": quality,
        "source": str(value.get("source", "")).strip(),
        "coordinate_frame": str(value.get("coordinate_frame", "")).strip(),
        "semantics": str(value.get("semantics", "")).strip(),
    }
    axis = axis_from_mapping(value.get("axis_base"))
    if axis is not None:
        result["axis_base"] = axis_mapping(axis)
    for key in (
        "elevation_deg",
        "spread_deg",
        "sample_count",
        "measured_sample_count",
        "measured_fraction",
        "span_m",
        "median_residual_m",
        "linearity",
        "horizontal_ratio",
    ):
        if key in value:
            result[key] = value[key]
    return result
