"""Depth-based facing-direction estimation for upright MacRobot objects.

All registered demonstration objects are placed upright.  Their long 3-D axis
is therefore close to ``base_link +Z`` and cannot define a chassis yaw.  This
module instead fits the visible vertical surface inside the DINO ROI and uses
its horizontal plane normal as the orientation signal.

The module has no ROS dependency.  The caller supplies the camera intrinsics
and the optical-to-base rotation matrix obtained from TF.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence, Tuple

import numpy as np


Vector3 = Tuple[float, float, float]
Matrix3 = Tuple[Vector3, Vector3, Vector3]


PATCH_MARKER = "macrobot_upright_face_orientation_v1"


@dataclass(frozen=True)
class UprightFaceEstimate:
    available: bool
    normal_base: Vector3 = (0.0, 0.0, 0.0)
    center_base_rotation_only: Vector3 = (0.0, 0.0, 0.0)
    quality: float = 0.0
    sample_count: int = 0
    inlier_count: int = 0
    inlier_fraction: float = 0.0
    median_residual_m: float = 0.0
    planarity: float = 0.0
    horizontal_span_m: float = 0.0
    vertical_span_m: float = 0.0
    center_plane_distance_m: float = 0.0
    source: str = "unavailable"
    reason: str = ""

    @property
    def yaw_deg(self) -> float:
        if not self.available:
            raise ValueError("upright face orientation is unavailable")
        return math.degrees(
            math.atan2(self.normal_base[1], self.normal_base[0])
        ) % 180.0


@dataclass(frozen=True)
class _PlaneFit:
    center: np.ndarray
    normal: np.ndarray
    inliers: np.ndarray
    residuals: np.ndarray
    eigenvalues: np.ndarray


def _normalise(vector: Sequence[float]) -> np.ndarray:
    array = np.asarray(vector, dtype=np.float64)
    if array.shape != (3,):
        raise ValueError("vector must contain exactly three values")
    norm = float(np.linalg.norm(array))
    if not math.isfinite(norm) or norm <= 1e-12:
        raise ValueError("vector has zero length")
    return array / norm


def _rotation_matrix(value: Sequence[Sequence[float]]) -> np.ndarray:
    matrix = np.asarray(value, dtype=np.float64)
    if matrix.shape != (3, 3) or not np.all(np.isfinite(matrix)):
        raise ValueError("optical_to_base_rotation must be a finite 3x3 matrix")
    # Remove small numerical scale/skew errors without accepting a reflection.
    u, _, vh = np.linalg.svd(matrix)
    rotation = u @ vh
    if float(np.linalg.det(rotation)) < 0.0:
        u[:, -1] *= -1.0
        rotation = u @ vh
    return rotation


def quaternion_rotation_matrix(
    x: float,
    y: float,
    z: float,
    w: float,
) -> Matrix3:
    """Return a normalised quaternion's active 3-D rotation matrix."""

    q = np.asarray((x, y, z, w), dtype=np.float64)
    norm = float(np.linalg.norm(q))
    if not math.isfinite(norm) or norm <= 1e-12:
        raise ValueError("quaternion has zero length")
    x, y, z, w = (float(value) for value in q / norm)
    matrix = np.asarray(
        (
            (
                1.0 - 2.0 * (y * y + z * z),
                2.0 * (x * y - z * w),
                2.0 * (x * z + y * w),
            ),
            (
                2.0 * (x * y + z * w),
                1.0 - 2.0 * (x * x + z * z),
                2.0 * (y * z - x * w),
            ),
            (
                2.0 * (x * z - y * w),
                2.0 * (y * z + x * w),
                1.0 - 2.0 * (x * x + y * y),
            ),
        ),
        dtype=np.float64,
    )
    return tuple(tuple(float(item) for item in row) for row in matrix)  # type: ignore[return-value]


def _roi_bounds(
    image_shape: tuple[int, int],
    roi_xywh: Sequence[float],
    *,
    inset_ratio: float,
    top_exclusion_ratio: float,
    bottom_exclusion_ratio: float,
) -> tuple[int, int, int, int]:
    if len(roi_xywh) != 4:
        raise ValueError("ROI must contain x, y, width and height")
    height_px, width_px = image_shape
    x, y, width, height = (float(item) for item in roi_xywh)
    if not all(math.isfinite(item) for item in (x, y, width, height)):
        raise ValueError("ROI values must be finite")
    if width <= 2.0 or height <= 2.0:
        raise ValueError("ROI is too small for upright face fitting")

    inset = max(0.0, min(0.40, float(inset_ratio)))
    top = max(0.0, min(0.40, float(top_exclusion_ratio)))
    bottom = max(0.0, min(0.45, float(bottom_exclusion_ratio)))

    x0 = int(math.floor(x + width * inset))
    x1 = int(math.ceil(x + width * (1.0 - inset)))
    y0 = int(math.floor(y + height * top))
    y1 = int(math.ceil(y + height * (1.0 - bottom)))

    x0 = max(0, min(width_px - 1, x0))
    x1 = max(x0 + 1, min(width_px, x1))
    y0 = max(0, min(height_px - 1, y0))
    y1 = max(y0 + 1, min(height_px, y1))
    if x1 - x0 < 3 or y1 - y0 < 3:
        raise ValueError("usable upright-face ROI is too small")
    return x0, y0, x1, y1


def _deproject_grid(
    u: np.ndarray,
    v: np.ndarray,
    depth: np.ndarray,
    *,
    fx: float,
    fy: float,
    cx: float,
    cy: float,
) -> np.ndarray:
    if fx <= 0.0 or fy <= 0.0:
        raise ValueError("camera focal lengths must be positive")
    z = depth.astype(np.float64, copy=False)
    x = (u.astype(np.float64, copy=False) - float(cx)) * z / float(fx)
    y = (v.astype(np.float64, copy=False) - float(cy)) * z / float(fy)
    return np.column_stack((x, y, z))


def _fit_plane_svd(points: np.ndarray, inliers: np.ndarray | None = None) -> _PlaneFit:
    selected = points if inliers is None else points[inliers]
    if selected.ndim != 2 or selected.shape[1] != 3 or selected.shape[0] < 3:
        raise ValueError("at least three 3-D points are required for a plane")
    center = np.median(selected, axis=0)
    centered = selected - center
    covariance = centered.T @ centered / max(selected.shape[0], 1)
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    order = np.argsort(eigenvalues)
    eigenvalues = eigenvalues[order]
    normal = _normalise(eigenvectors[:, order[0]])
    residuals_all = np.abs((points - center) @ normal)
    used = np.ones(points.shape[0], dtype=bool) if inliers is None else inliers
    return _PlaneFit(
        center=center,
        normal=normal,
        inliers=used,
        residuals=residuals_all,
        eigenvalues=eigenvalues,
    )


def _ransac_vertical_plane(
    points_base: np.ndarray,
    *,
    iterations: int,
    inlier_threshold_m: float,
    maximum_abs_normal_z: float,
    center_point_base: np.ndarray,
    maximum_center_plane_distance_m: float,
) -> _PlaneFit:
    count = points_base.shape[0]
    if count < 3:
        raise ValueError("not_enough_upright_face_points")
    rng = np.random.default_rng(0)
    best_inliers: np.ndarray | None = None
    best_key: tuple[int, float, float] | None = None
    threshold = max(0.001, abs(float(inlier_threshold_m)))
    max_normal_z = max(0.0, min(0.95, abs(float(maximum_abs_normal_z))))
    max_center_distance = max(0.001, abs(float(maximum_center_plane_distance_m)))

    for _ in range(max(16, int(iterations))):
        indices = rng.choice(count, size=3, replace=False)
        first, second, third = points_base[indices]
        normal_raw = np.cross(second - first, third - first)
        norm = float(np.linalg.norm(normal_raw))
        if not math.isfinite(norm) or norm <= 1e-8:
            continue
        normal = normal_raw / norm
        if abs(float(normal[2])) > max_normal_z:
            continue
        center_distance = abs(float(np.dot(center_point_base - first, normal)))
        if center_distance > max_center_distance:
            continue
        residuals = np.abs((points_base - first) @ normal)
        inliers = residuals <= threshold
        inlier_count = int(np.count_nonzero(inliers))
        if inlier_count < 3:
            continue
        median_residual = float(np.median(residuals[inliers]))
        # Prefer more support, then a plane nearer the DINO centre, then lower residual.
        key = (inlier_count, -center_distance, -median_residual)
        if best_key is None or key > best_key:
            best_key = key
            best_inliers = inliers

    if best_inliers is None:
        raise ValueError("upright_face_ransac_no_vertical_plane")

    fit = _fit_plane_svd(points_base, best_inliers)
    # Reclassify once with the refined plane and refit.
    refined_inliers = fit.residuals <= threshold
    if int(np.count_nonzero(refined_inliers)) >= 3:
        fit = _fit_plane_svd(points_base, refined_inliers)
    if abs(float(fit.normal[2])) > max_normal_z:
        raise ValueError("upright_face_normal_not_horizontal")
    return fit


def estimate_upright_face_orientation(
    *,
    depth_m: np.ndarray,
    center_x: float,
    center_y: float,
    center_depth_m: float,
    roi_xywh: Sequence[float],
    fx: float,
    fy: float,
    cx: float,
    cy: float,
    optical_to_base_rotation: Sequence[Sequence[float]],
    roi_inset_ratio: float = 0.10,
    top_exclusion_ratio: float = 0.06,
    bottom_exclusion_ratio: float = 0.18,
    sample_stride_px: int = 2,
    maximum_points: int = 1400,
    depth_gate_m: float = 0.055,
    minimum_depth_m: float = 0.08,
    maximum_depth_m: float = 2.0,
    minimum_points: int = 60,
    ransac_iterations: int = 96,
    inlier_threshold_m: float = 0.006,
    minimum_inlier_ratio: float = 0.35,
    maximum_abs_normal_z: float = 0.35,
    maximum_median_residual_m: float = 0.006,
    minimum_horizontal_span_m: float = 0.008,
    minimum_vertical_span_m: float = 0.025,
    maximum_center_plane_distance_m: float = 0.018,
) -> UprightFaceEstimate:
    """Estimate the yaw of a visible vertical surface on an upright object.

    The returned ``normal_base`` is horizontal and undirected: ``n`` and ``-n``
    describe the same face orientation.  Consumers must compare it modulo 180°.
    """

    image = np.asarray(depth_m, dtype=np.float32)
    if image.ndim != 2 or image.size == 0:
        return UprightFaceEstimate(False, reason="aligned_depth_unavailable_for_upright_face")
    try:
        rotation = _rotation_matrix(optical_to_base_rotation)
        x0, y0, x1, y1 = _roi_bounds(
            image.shape,
            roi_xywh,
            inset_ratio=roi_inset_ratio,
            top_exclusion_ratio=top_exclusion_ratio,
            bottom_exclusion_ratio=bottom_exclusion_ratio,
        )
    except (TypeError, ValueError, np.linalg.LinAlgError) as error:
        return UprightFaceEstimate(False, reason=str(error))

    center_depth = float(center_depth_m)
    if not math.isfinite(center_depth) or not (
        float(minimum_depth_m) <= center_depth <= float(maximum_depth_m)
    ):
        return UprightFaceEstimate(False, reason="upright_face_center_depth_invalid")

    stride = max(1, int(sample_stride_px))
    crop = image[y0:y1:stride, x0:x1:stride]
    yy, xx = np.indices(crop.shape)
    u = x0 + xx * stride
    v = y0 + yy * stride
    valid = np.isfinite(crop)
    valid &= crop >= float(minimum_depth_m)
    valid &= crop <= float(maximum_depth_m)
    valid &= np.abs(crop - center_depth) <= abs(float(depth_gate_m))

    if int(np.count_nonzero(valid)) < max(3, int(minimum_points)):
        return UprightFaceEstimate(
            False,
            sample_count=int(np.count_nonzero(valid)),
            reason="not_enough_upright_face_depth_points",
        )

    depths = crop[valid]
    pixels_u = u[valid]
    pixels_v = v[valid]
    try:
        points_optical = _deproject_grid(
            pixels_u,
            pixels_v,
            depths,
            fx=fx,
            fy=fy,
            cx=cx,
            cy=cy,
        )
    except ValueError as error:
        return UprightFaceEstimate(False, reason=str(error))

    limit = max(max(3, int(minimum_points)), int(maximum_points))
    if points_optical.shape[0] > limit:
        indices = np.linspace(
            0,
            points_optical.shape[0] - 1,
            limit,
            dtype=np.int64,
        )
        points_optical = points_optical[indices]

    points_base = points_optical @ rotation.T
    center_optical = np.asarray(
        (
            (float(center_x) - float(cx)) * center_depth / float(fx),
            (float(center_y) - float(cy)) * center_depth / float(fy),
            center_depth,
        ),
        dtype=np.float64,
    )
    center_base = rotation @ center_optical

    try:
        fit = _ransac_vertical_plane(
            points_base,
            iterations=ransac_iterations,
            inlier_threshold_m=inlier_threshold_m,
            maximum_abs_normal_z=maximum_abs_normal_z,
            center_point_base=center_base,
            maximum_center_plane_distance_m=maximum_center_plane_distance_m,
        )
    except (ValueError, np.linalg.LinAlgError) as error:
        return UprightFaceEstimate(
            False,
            sample_count=int(points_base.shape[0]),
            reason=str(error),
        )

    inliers = fit.inliers
    inlier_points = points_base[inliers]
    inlier_count = int(inlier_points.shape[0])
    inlier_fraction = inlier_count / float(max(points_base.shape[0], 1))
    if inlier_count < max(3, int(minimum_points)):
        return UprightFaceEstimate(
            False,
            sample_count=int(points_base.shape[0]),
            inlier_count=inlier_count,
            inlier_fraction=inlier_fraction,
            reason="not_enough_upright_face_plane_inliers",
        )
    if inlier_fraction < max(0.0, min(1.0, float(minimum_inlier_ratio))):
        return UprightFaceEstimate(
            False,
            sample_count=int(points_base.shape[0]),
            inlier_count=inlier_count,
            inlier_fraction=inlier_fraction,
            reason="upright_face_inlier_ratio_too_small",
        )

    normal = _normalise(fit.normal)
    horizontal = math.hypot(float(normal[0]), float(normal[1]))
    if horizontal <= 1e-9:
        return UprightFaceEstimate(
            False,
            sample_count=int(points_base.shape[0]),
            inlier_count=inlier_count,
            inlier_fraction=inlier_fraction,
            reason="upright_face_normal_has_no_horizontal_projection",
        )
    normal_horizontal = np.asarray(
        (float(normal[0]) / horizontal, float(normal[1]) / horizontal, 0.0),
        dtype=np.float64,
    )
    tangent = np.asarray(
        (-normal_horizontal[1], normal_horizontal[0], 0.0),
        dtype=np.float64,
    )

    def robust_span(values: np.ndarray) -> float:
        if values.size < 2:
            return 0.0
        low, high = np.percentile(values, (5.0, 95.0))
        return float(high - low)

    horizontal_span = robust_span(inlier_points @ tangent)
    vertical_span = robust_span(inlier_points[:, 2])
    residual = float(np.median(fit.residuals[inliers]))
    center_distance = abs(float(np.dot(center_base - fit.center, normal)))

    eigenvalues = np.maximum(fit.eigenvalues, 0.0)
    plane_mid = float(eigenvalues[1])
    plane_small = float(eigenvalues[0])
    planarity = max(0.0, min(1.0, 1.0 - plane_small / max(plane_mid, 1e-12)))

    if horizontal_span < float(minimum_horizontal_span_m):
        reason = "upright_face_horizontal_span_too_small"
    elif vertical_span < float(minimum_vertical_span_m):
        reason = "upright_face_vertical_span_too_small"
    elif residual > float(maximum_median_residual_m):
        reason = "upright_face_plane_residual_too_large"
    elif center_distance > float(maximum_center_plane_distance_m):
        reason = "upright_face_plane_misses_object_center"
    else:
        reason = ""
    if reason:
        return UprightFaceEstimate(
            False,
            normal_base=tuple(float(item) for item in normal_horizontal),
            center_base_rotation_only=tuple(float(item) for item in fit.center),
            sample_count=int(points_base.shape[0]),
            inlier_count=inlier_count,
            inlier_fraction=inlier_fraction,
            median_residual_m=residual,
            planarity=planarity,
            horizontal_span_m=horizontal_span,
            vertical_span_m=vertical_span,
            center_plane_distance_m=center_distance,
            reason=reason,
        )

    ratio_quality = max(0.0, min(1.0, inlier_fraction))
    residual_quality = math.exp(
        -residual / max(float(maximum_median_residual_m), 1e-6)
    )
    horizontal_span_quality = max(
        0.0,
        min(1.0, horizontal_span / max(float(minimum_horizontal_span_m), 1e-6)),
    )
    vertical_span_quality = max(
        0.0,
        min(1.0, vertical_span / max(float(minimum_vertical_span_m), 1e-6)),
    )
    center_quality = math.exp(
        -center_distance / max(float(maximum_center_plane_distance_m), 1e-6)
    )
    quality = max(
        0.0,
        min(
            1.0,
            0.30 * ratio_quality
            + 0.25 * planarity
            + 0.20 * residual_quality
            + 0.10 * horizontal_span_quality
            + 0.10 * vertical_span_quality
            + 0.05 * center_quality,
        ),
    )

    return UprightFaceEstimate(
        True,
        normal_base=tuple(float(item) for item in normal_horizontal),
        center_base_rotation_only=tuple(float(item) for item in fit.center),
        quality=quality,
        sample_count=int(points_base.shape[0]),
        inlier_count=inlier_count,
        inlier_fraction=inlier_fraction,
        median_residual_m=residual,
        planarity=planarity,
        horizontal_span_m=horizontal_span,
        vertical_span_m=vertical_span,
        center_plane_distance_m=center_distance,
        source="upright_face_plane_3d",
        reason="",
    )


def orientation_class_from_yaw(yaw_deg: float) -> str:
    angle = float(yaw_deg) % 180.0
    if angle <= 25.0 or angle >= 155.0:
        return "horizontal"
    if 65.0 <= angle <= 115.0:
        return "vertical"
    return "diagonal"
