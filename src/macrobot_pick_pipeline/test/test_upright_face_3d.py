import math

import numpy as np

from macrobot_pick_pipeline.upright_face_3d import (
    estimate_upright_face_orientation,
    quaternion_rotation_matrix,
)


OPTICAL_TO_BASE = (
    (0.0, 0.0, 1.0),
    (-1.0, 0.0, 0.0),
    (0.0, -1.0, 0.0),
)


def axial_error(a: float, b: float) -> float:
    delta = abs((a - b) % 180.0)
    return min(delta, 180.0 - delta)


def plane_depth_image(*, yaw_deg: float, add_holes: bool = False):
    height, width = 160, 200
    fx = fy = 220.0
    cx, cy = 100.0, 80.0
    center_depth = 0.45
    roi = (58.0, 28.0, 84.0, 112.0)
    rotation = np.asarray(OPTICAL_TO_BASE, dtype=np.float64)
    yaw = math.radians(yaw_deg)
    normal_base = np.asarray((math.cos(yaw), math.sin(yaw), 0.0))
    normal_optical = rotation.T @ normal_base
    center_ray = np.asarray((0.0, 0.0, 1.0))
    plane_offset = float(normal_optical @ (center_ray * center_depth))

    depth = np.zeros((height, width), dtype=np.float32)
    x0, y0, w, h = (int(value) for value in roi)
    for v in range(y0, y0 + h):
        for u in range(x0, x0 + w):
            ray = np.asarray(((u - cx) / fx, (v - cy) / fy, 1.0))
            denominator = float(normal_optical @ ray)
            if abs(denominator) > 1e-6:
                z = plane_offset / denominator
                if 0.1 < z < 1.5:
                    depth[v, u] = z
    if add_holes:
        depth[y0 + 6 : y0 + h - 10 : 7, x0 + 5 : x0 + w - 5 : 9] = 0.0
    return depth, center_depth, roi, fx, fy, cx, cy


def test_front_face_normal_is_base_forward():
    depth, center_depth, roi, fx, fy, cx, cy = plane_depth_image(yaw_deg=0.0)
    result = estimate_upright_face_orientation(
        depth_m=depth,
        center_x=cx,
        center_y=cy,
        center_depth_m=center_depth,
        roi_xywh=roi,
        fx=fx,
        fy=fy,
        cx=cx,
        cy=cy,
        optical_to_base_rotation=OPTICAL_TO_BASE,
        minimum_points=40,
    )
    assert result.available, result.reason
    assert axial_error(result.yaw_deg, 0.0) < 1.0
    assert result.vertical_span_m > 0.05
    assert result.horizontal_span_m > 0.03
    assert result.inlier_fraction > 0.8


def test_oblique_upright_face_recovers_yaw_with_depth_holes():
    depth, center_depth, roi, fx, fy, cx, cy = plane_depth_image(
        yaw_deg=32.0,
        add_holes=True,
    )
    result = estimate_upright_face_orientation(
        depth_m=depth,
        center_x=cx,
        center_y=cy,
        center_depth_m=center_depth,
        roi_xywh=roi,
        fx=fx,
        fy=fy,
        cx=cx,
        cy=cy,
        optical_to_base_rotation=OPTICAL_TO_BASE,
        minimum_points=40,
        depth_gate_m=0.12,
    )
    assert result.available, result.reason
    assert axial_error(result.yaw_deg, 32.0) < 2.0
    assert result.quality > 0.6


def test_floor_plane_is_rejected_by_horizontal_normal_constraint():
    height, width = 120, 160
    depth = np.zeros((height, width), dtype=np.float32)
    # Synthetic plane whose base-frame normal is vertical; it represents floor.
    # Use a shallow depth gradient down the image to make a valid optical plane.
    for v in range(20, 110):
        depth[v, 40:120] = 0.35 + 0.002 * (v - 20)
    result = estimate_upright_face_orientation(
        depth_m=depth,
        center_x=80.0,
        center_y=60.0,
        center_depth_m=float(depth[60, 80]),
        roi_xywh=(40.0, 20.0, 80.0, 90.0),
        fx=180.0,
        fy=180.0,
        cx=80.0,
        cy=60.0,
        optical_to_base_rotation=OPTICAL_TO_BASE,
        minimum_points=30,
        depth_gate_m=0.2,
        bottom_exclusion_ratio=0.0,
    )
    assert not result.available
    assert result.reason in {
        "upright_face_ransac_no_vertical_plane",
        "upright_face_normal_not_horizontal",
    }


def test_too_few_depth_points_reports_explicit_reason():
    depth = np.zeros((80, 80), dtype=np.float32)
    depth[40, 40] = 0.4
    result = estimate_upright_face_orientation(
        depth_m=depth,
        center_x=40.0,
        center_y=40.0,
        center_depth_m=0.4,
        roi_xywh=(20.0, 10.0, 40.0, 60.0),
        fx=100.0,
        fy=100.0,
        cx=40.0,
        cy=40.0,
        optical_to_base_rotation=OPTICAL_TO_BASE,
        minimum_points=20,
    )
    assert not result.available
    assert result.reason == "not_enough_upright_face_depth_points"


def test_quaternion_rotation_matrix_identity():
    matrix = np.asarray(quaternion_rotation_matrix(0.0, 0.0, 0.0, 1.0))
    assert np.allclose(matrix, np.eye(3))
