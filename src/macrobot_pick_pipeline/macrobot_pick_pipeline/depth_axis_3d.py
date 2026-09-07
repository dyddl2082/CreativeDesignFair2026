"""Depth-assisted 3-D major-axis estimation for MacRobot.

The WSL DINO pipeline already supplies a target centre, ROI and an axial
image-plane angle.  This module samples aligned depth along that 2-D axis,
deprojects the samples, fits a robust 3-D line and reports an axial yaw in the
robot base frame.  It has no ROS dependency and is therefore unit-testable.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable, Sequence, Tuple

import numpy as np


Vector3 = Tuple[float, float, float]
Pixel = Tuple[float, float]


@dataclass(frozen=True)
class Axis3DEstimate:
    available: bool
    axis_optical: Vector3 = (0.0, 0.0, 0.0)
    center_optical: Vector3 = (0.0, 0.0, 0.0)
    quality: float = 0.0
    sample_count: int = 0
    measured_sample_count: int = 0
    measured_fraction: float = 0.0
    span_m: float = 0.0
    median_residual_m: float = 0.0
    linearity: float = 0.0
    source: str = "unavailable"
    reason: str = ""


@dataclass(frozen=True)
class BaseAxisOrientation:
    available: bool
    yaw_deg: float = 0.0
    elevation_deg: float = 0.0
    quality: float = 0.0
    horizontal_ratio: float = 0.0
    axis_base: Vector3 = (0.0, 0.0, 0.0)
    source: str = "unavailable"
    reason: str = ""


def _normalise(vector: Sequence[float]) -> np.ndarray:
    array = np.asarray(vector, dtype=np.float64)
    norm = float(np.linalg.norm(array))
    if not math.isfinite(norm) or norm <= 1e-12:
        raise ValueError("axis vector has zero length")
    return array / norm


def _line_extent_to_box(
    center: Pixel,
    direction: Pixel,
    roi_xywh: Sequence[float],
) -> tuple[float, float]:
    """Return negative/positive line distances from centre to an ROI box."""

    if len(roi_xywh) != 4:
        raise ValueError("ROI must contain x, y, width and height")
    x, y, width, height = (float(value) for value in roi_xywh)
    if width <= 1.0 or height <= 1.0:
        raise ValueError("ROI is too small for an axis fit")
    u, v = (float(center[0]), float(center[1]))
    du, dv = _normalise(direction)
    x0, x1 = x, x + width - 1.0
    y0, y1 = y, y + height - 1.0

    def extent(sign: float) -> float:
        candidates: list[float] = []
        sx = sign * float(du)
        sy = sign * float(dv)
        if sx > 1e-9:
            candidates.append((x1 - u) / sx)
        elif sx < -1e-9:
            candidates.append((x0 - u) / sx)
        if sy > 1e-9:
            candidates.append((y1 - v) / sy)
        elif sy < -1e-9:
            candidates.append((y0 - v) / sy)
        positive = [value for value in candidates if math.isfinite(value) and value > 0.0]
        if not positive:
            return 0.0
        return min(positive)

    return extent(-1.0), extent(1.0)


def axis_sample_pixels(
    *,
    center_x: float,
    center_y: float,
    roi_xywh: Sequence[float],
    orientation_deg: float,
    sample_count: int = 11,
    inset_ratio: float = 0.18,
) -> tuple[Pixel, ...]:
    """Generate pixels along the image-plane principal axis inside the ROI."""

    count = max(3, int(sample_count))
    if count % 2 == 0:
        count += 1
    angle = math.radians(float(orientation_deg) % 180.0)
    direction = (math.cos(angle), math.sin(angle))
    negative, positive = _line_extent_to_box(
        (float(center_x), float(center_y)), direction, roi_xywh
    )
    keep = max(0.2, min(0.95, 1.0 - float(inset_ratio)))
    negative *= keep
    positive *= keep
    if negative + positive < 4.0:
        raise ValueError("image-axis segment is too short")
    parameters = np.linspace(-negative, positive, count)
    return tuple(
        (
            float(center_x) + float(parameter) * direction[0],
            float(center_y) + float(parameter) * direction[1],
        )
        for parameter in parameters
    )


def axis_strip_sample_pixels(
    *,
    center_x: float,
    center_y: float,
    roi_xywh: Sequence[float],
    orientation_deg: float,
    major_sample_count: int = 11,
    minor_track_count: int = 3,
    strip_half_width_ratio: float = 0.12,
) -> tuple[Pixel, ...]:
    """Generate a narrow oriented strip of pixels around the 2-D major axis.

    A single pixel line is vulnerable to RealSense depth holes and specular
    patches.  Parallel minor-axis tracks add redundant depth samples while the
    strip remains narrow enough that PCA is still dominated by the object's
    major direction.
    """

    major = axis_sample_pixels(
        center_x=center_x,
        center_y=center_y,
        roi_xywh=roi_xywh,
        orientation_deg=orientation_deg,
        sample_count=major_sample_count,
    )
    tracks = max(1, int(minor_track_count))
    if tracks % 2 == 0:
        tracks += 1
    angle = math.radians(float(orientation_deg) % 180.0)
    perpendicular = (-math.sin(angle), math.cos(angle))
    negative, positive = _line_extent_to_box(
        (float(center_x), float(center_y)),
        perpendicular,
        roi_xywh,
    )
    ratio = max(0.0, min(0.45, float(strip_half_width_ratio)))
    half_width = min(negative, positive) * ratio
    offsets = (
        (0.0,)
        if tracks == 1 or half_width <= 0.5
        else tuple(float(value) for value in np.linspace(-half_width, half_width, tracks))
    )
    x, y, width, height = (float(value) for value in roi_xywh)
    x1 = x + width - 1.0
    y1 = y + height - 1.0
    result: list[Pixel] = []
    for offset in offsets:
        for u, v in major:
            candidate = (
                u + offset * perpendicular[0],
                v + offset * perpendicular[1],
            )
            if x <= candidate[0] <= x1 and y <= candidate[1] <= y1:
                result.append(candidate)
    return tuple(result)


def _window_depth(
    depth_m: np.ndarray,
    pixel: Pixel,
    *,
    radius_px: int,
    minimum_depth_m: float,
    maximum_depth_m: float,
    center_depth_m: float,
    depth_gate_m: float,
) -> float | None:
    image = np.asarray(depth_m, dtype=np.float32)
    if image.ndim != 2 or image.size == 0:
        return None
    u = int(round(float(pixel[0])))
    v = int(round(float(pixel[1])))
    radius = max(0, int(radius_px))
    x0 = max(0, u - radius)
    x1 = min(image.shape[1], u + radius + 1)
    y0 = max(0, v - radius)
    y1 = min(image.shape[0], v + radius + 1)
    if x0 >= x1 or y0 >= y1:
        return None
    values = image[y0:y1, x0:x1].reshape(-1)
    valid = np.isfinite(values)
    valid &= values >= float(minimum_depth_m)
    valid &= values <= float(maximum_depth_m)
    if math.isfinite(float(center_depth_m)) and float(center_depth_m) > 0.0:
        valid &= np.abs(values - float(center_depth_m)) <= abs(float(depth_gate_m))
    values = values[valid]
    if values.size == 0:
        return None
    return float(np.median(values))


def deproject_pixel(
    pixel: Pixel,
    depth_m: float,
    *,
    fx: float,
    fy: float,
    cx: float,
    cy: float,
) -> Vector3:
    if fx <= 0.0 or fy <= 0.0:
        raise ValueError("camera focal lengths must be positive")
    u, v = float(pixel[0]), float(pixel[1])
    z = float(depth_m)
    return ((u - cx) * z / fx, (v - cy) * z / fy, z)


def _fit_line(points: np.ndarray) -> tuple[np.ndarray, np.ndarray, float, float, float]:
    if points.ndim != 2 or points.shape[1] != 3 or points.shape[0] < 3:
        raise ValueError("at least three 3-D points are required")
    center = np.median(points, axis=0)
    centered = points - center
    covariance = centered.T @ centered / max(points.shape[0], 1)
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    order = np.argsort(eigenvalues)[::-1]
    axis = _normalise(eigenvectors[:, order[0]])
    projections = centered @ axis
    residual_vectors = centered - projections[:, None] * axis[None, :]
    residuals = np.linalg.norm(residual_vectors, axis=1)
    span = float(np.max(projections) - np.min(projections))
    largest = float(max(eigenvalues[order[0]], 0.0))
    second = float(max(eigenvalues[order[1]], 0.0))
    linearity = max(0.0, min(1.0, (largest - second) / max(largest, 1e-12)))
    median_residual = float(np.median(residuals))
    return center, axis, span, median_residual, linearity


def estimate_axis_3d(
    *,
    depth_m: np.ndarray,
    center_x: float,
    center_y: float,
    center_depth_m: float,
    roi_xywh: Sequence[float],
    orientation_2d_deg: float,
    orientation_2d_quality: float,
    fx: float,
    fy: float,
    cx: float,
    cy: float,
    sample_count: int = 11,
    minor_track_count: int = 3,
    strip_half_width_ratio: float = 0.12,
    window_radius_px: int = 2,
    minimum_valid_samples: int = 5,
    depth_gate_m: float = 0.06,
    minimum_depth_m: float = 0.08,
    maximum_depth_m: float = 2.0,
    minimum_span_m: float = 0.018,
    maximum_residual_m: float = 0.012,
    allow_center_depth_fallback: bool = True,
) -> Axis3DEstimate:
    """Estimate a robust 3-D line from aligned depth along a DINO 2-D axis."""

    try:
        pixels = axis_strip_sample_pixels(
            center_x=center_x,
            center_y=center_y,
            roi_xywh=roi_xywh,
            orientation_deg=orientation_2d_deg,
            major_sample_count=sample_count,
            minor_track_count=minor_track_count,
            strip_half_width_ratio=strip_half_width_ratio,
        )
    except (TypeError, ValueError) as error:
        return Axis3DEstimate(False, reason=str(error))

    points: list[Vector3] = []
    measured_flags: list[bool] = []
    for pixel in pixels:
        measured = _window_depth(
            depth_m,
            pixel,
            radius_px=window_radius_px,
            minimum_depth_m=minimum_depth_m,
            maximum_depth_m=maximum_depth_m,
            center_depth_m=center_depth_m,
            depth_gate_m=depth_gate_m,
        )
        used_measured = measured is not None
        if measured is None:
            if not allow_center_depth_fallback:
                continue
            measured = float(center_depth_m)
            if not math.isfinite(measured) or not (
                minimum_depth_m <= measured <= maximum_depth_m
            ):
                continue
        try:
            points.append(
                deproject_pixel(pixel, measured, fx=fx, fy=fy, cx=cx, cy=cy)
            )
            measured_flags.append(used_measured)
        except ValueError:
            continue

    if len(points) < max(3, int(minimum_valid_samples)):
        return Axis3DEstimate(
            False,
            sample_count=len(points),
            measured_sample_count=sum(measured_flags),
            reason="not_enough_axis_depth_samples",
        )

    array = np.asarray(points, dtype=np.float64)
    try:
        center, axis, span, residual, linearity = _fit_line(array)
        projections = (array - center) @ axis
        residual_vectors = (array - center) - projections[:, None] * axis[None, :]
        residuals = np.linalg.norm(residual_vectors, axis=1)
        median = float(np.median(residuals))
        mad = float(np.median(np.abs(residuals - median)))
        dynamic_limit = median + 2.5 * max(mad, 0.001)
        trim_limit = max(0.003, min(abs(float(maximum_residual_m)), dynamic_limit))
        keep = residuals <= trim_limit
        if int(np.count_nonzero(keep)) >= max(3, int(minimum_valid_samples)):
            array = array[keep]
            flags = np.asarray(measured_flags, dtype=bool)[keep]
            center, axis, span, residual, linearity = _fit_line(array)
        else:
            flags = np.asarray(measured_flags, dtype=bool)
    except (ValueError, np.linalg.LinAlgError) as error:
        return Axis3DEstimate(False, reason=f"axis_fit_failed: {error}")

    measured_count = int(np.count_nonzero(flags))
    measured_fraction = measured_count / float(max(len(flags), 1))
    valid_fraction = len(flags) / float(max(len(pixels), 1))
    span_quality = max(0.0, min(1.0, span / max(float(minimum_span_m), 1e-6)))
    residual_quality = math.exp(
        -max(0.0, residual) / max(float(maximum_residual_m), 1e-6)
    )
    image_quality = max(0.0, min(1.0, float(orientation_2d_quality)))
    geometry_quality = (
        0.30 * valid_fraction
        + 0.30 * linearity
        + 0.20 * span_quality
        + 0.20 * residual_quality
    )
    # Measured depth is substantially more trustworthy than the constant-depth
    # projection fallback, but the latter still provides a base-frame hint.
    depth_authority = 0.35 + 0.65 * measured_fraction
    quality = max(
        0.0,
        min(1.0, geometry_quality * depth_authority * (0.55 + 0.45 * image_quality)),
    )
    source = (
        "depth_axis_3d"
        if measured_count >= max(3, int(minimum_valid_samples))
        else "projected_axis_3d_fallback"
    )
    return Axis3DEstimate(
        available=True,
        axis_optical=tuple(float(value) for value in axis),
        center_optical=tuple(float(value) for value in center),
        quality=quality,
        sample_count=int(len(flags)),
        measured_sample_count=measured_count,
        measured_fraction=measured_fraction,
        span_m=span,
        median_residual_m=residual,
        linearity=linearity,
        source=source,
    )


def base_axis_orientation(
    axis_base: Sequence[float],
    *,
    quality: float,
    source: str,
    minimum_horizontal_ratio: float = 0.30,
) -> BaseAxisOrientation:
    """Convert a 3-D base-frame axis into an axial XY yaw."""

    try:
        axis = _normalise(axis_base)
    except ValueError as error:
        return BaseAxisOrientation(False, reason=str(error))
    horizontal = float(math.hypot(float(axis[0]), float(axis[1])))
    minimum = max(0.0, min(1.0, float(minimum_horizontal_ratio)))
    if horizontal < minimum:
        return BaseAxisOrientation(
            False,
            quality=0.0,
            horizontal_ratio=horizontal,
            axis_base=tuple(float(value) for value in axis),
            source=source,
            reason="axis_horizontal_projection_too_small",
        )
    yaw = math.degrees(math.atan2(float(axis[1]), float(axis[0]))) % 180.0
    elevation = math.degrees(math.atan2(float(axis[2]), horizontal))
    combined_quality = max(0.0, min(1.0, float(quality) * horizontal))
    return BaseAxisOrientation(
        available=True,
        yaw_deg=yaw,
        elevation_deg=elevation,
        quality=combined_quality,
        horizontal_ratio=horizontal,
        axis_base=tuple(float(value) for value in axis),
        source=str(source),
    )


def orientation_class_from_yaw(yaw_deg: float) -> str:
    angle = float(yaw_deg) % 180.0
    if angle <= 25.0 or angle >= 155.0:
        return "horizontal"
    if 65.0 <= angle <= 115.0:
        return "vertical"
    return "diagonal"
