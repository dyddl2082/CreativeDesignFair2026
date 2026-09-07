import math

import numpy as np

from macrobot_pick_pipeline.depth_axis_3d import (
    axis_sample_pixels,
    axis_strip_sample_pixels,
    base_axis_orientation,
    estimate_axis_3d,
)


def test_axis_sample_pixels_stays_inside_roi():
    pixels = axis_sample_pixels(
        center_x=50.0,
        center_y=40.0,
        roi_xywh=(20.0, 10.0, 60.0, 60.0),
        orientation_deg=35.0,
        sample_count=9,
    )
    assert len(pixels) == 9
    assert all(20.0 <= u <= 79.0 and 10.0 <= v <= 69.0 for u, v in pixels)



def test_strip_sampling_adds_parallel_tracks():
    pixels = axis_strip_sample_pixels(
        center_x=50.0,
        center_y=40.0,
        roi_xywh=(20.0, 10.0, 60.0, 60.0),
        orientation_deg=20.0,
        major_sample_count=9,
        minor_track_count=3,
        strip_half_width_ratio=0.15,
    )
    assert len(pixels) > 9
    rounded_v = {round(v, 2) for _, v in pixels}
    assert len(rounded_v) > 3
    assert all(20.0 <= u <= 79.0 and 10.0 <= v <= 69.0 for u, v in pixels)

def test_constant_depth_horizontal_axis_is_recovered():
    depth = np.full((100, 120), 0.50, dtype=np.float32)
    estimate = estimate_axis_3d(
        depth_m=depth,
        center_x=60.0,
        center_y=50.0,
        center_depth_m=0.50,
        roi_xywh=(25.0, 40.0, 70.0, 20.0),
        orientation_2d_deg=0.0,
        orientation_2d_quality=0.9,
        fx=100.0,
        fy=100.0,
        cx=60.0,
        cy=50.0,
        sample_count=11,
        minimum_valid_samples=5,
    )
    assert estimate.available
    assert estimate.source == "depth_axis_3d"
    assert estimate.measured_fraction > 0.9
    orientation = base_axis_orientation(
        estimate.axis_optical,
        quality=estimate.quality,
        source=estimate.source,
    )
    assert orientation.available
    assert min(orientation.yaw_deg, 180.0 - orientation.yaw_deg) < 2.0


def test_depth_gradient_changes_3d_axis_but_remains_finite():
    depth = np.full((120, 120), 0.55, dtype=np.float32)
    for x in range(20, 101):
        depth[40:81, x] = 0.45 + 0.0012 * (x - 20)
    estimate = estimate_axis_3d(
        depth_m=depth,
        center_x=60.0,
        center_y=60.0,
        center_depth_m=0.50,
        roi_xywh=(20.0, 40.0, 81.0, 41.0),
        orientation_2d_deg=0.0,
        orientation_2d_quality=0.85,
        fx=110.0,
        fy=110.0,
        cx=60.0,
        cy=60.0,
        sample_count=11,
        depth_gate_m=0.12,
    )
    assert estimate.available
    assert estimate.span_m > 0.01
    assert math.isfinite(estimate.quality)


def test_center_depth_fallback_is_low_authority():
    depth = np.zeros((100, 100), dtype=np.float32)
    estimate = estimate_axis_3d(
        depth_m=depth,
        center_x=50.0,
        center_y=50.0,
        center_depth_m=0.50,
        roi_xywh=(20.0, 40.0, 60.0, 20.0),
        orientation_2d_deg=0.0,
        orientation_2d_quality=0.9,
        fx=100.0,
        fy=100.0,
        cx=50.0,
        cy=50.0,
        sample_count=9,
        minimum_valid_samples=5,
        allow_center_depth_fallback=True,
    )
    assert estimate.available
    assert estimate.source == "projected_axis_3d_fallback"
    assert estimate.measured_fraction == 0.0
    assert estimate.quality < 0.45
