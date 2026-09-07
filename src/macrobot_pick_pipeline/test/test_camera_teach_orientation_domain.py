import math

import pytest

from macrobot_pick_pipeline.camera_teach_core import (
    CameraReferenceSample,
    aggregate_camera_reference,
)


def axis(yaw_deg: float):
    angle = math.radians(yaw_deg)
    return (math.cos(angle), math.sin(angle), 0.0)


def sample(index: int, *, mode: str, yaw: float):
    common = dict(
        point_base=(0.25 + index * 0.0002, 0.06, 0.08),
        orientation_deg=yaw,
        orientation_class="diagonal",
        orientation_quality=0.8,
        localization_quality=0.9,
        depth_std_m=0.002,
        center_std_px=0.4,
        score=0.8,
        source_stamp_sec=float(index),
        published_stamp_sec=float(index),
        orientation_2d_deg=40.0 + index * 0.2,
        orientation_2d_class="diagonal",
        orientation_2d_quality=0.8,
    )
    if mode == "3d":
        common.update(
            orientation_source="depth_axis_3d",
            orientation_coordinate_frame="base_link",
            orientation_semantics="axial_yaw",
            orientation_axis_base=axis(yaw),
            orientation_3d_available=True,
        )
    else:
        common.update(
            orientation_source="image_axis_2d",
            orientation_coordinate_frame="camera_image",
            orientation_semantics="axial_angle",
        )
    return CameraReferenceSample(**common)


def test_auto_prefers_measured_3d_without_mixing_2d():
    samples = [
        sample(0, mode="2d", yaw=40.0),
        sample(1, mode="3d", yaw=19.0),
        sample(2, mode="3d", yaw=20.0),
        sample(3, mode="2d", yaw=41.0),
        sample(4, mode="3d", yaw=21.0),
        sample(5, mode="2d", yaw=42.0),
        sample(6, mode="2d", yaw=43.0),
    ]
    reference = aggregate_camera_reference(
        samples,
        minimum_count=7,
        orientation_mode="auto",
        minimum_3d_orientation_samples=3,
    )
    assert reference.orientation_mode == "3d"
    assert reference.orientation_source == "depth_axis_3d"
    assert reference.orientation_coordinate_frame == "base_link"
    assert reference.orientation_semantics == "axial_yaw"
    assert reference.orientation_sample_count == 3
    assert reference.orientation_deg == pytest.approx(20.0, abs=0.5)
    assert reference.orientation_axis_base is not None


def test_explicit_3d_mode_rejects_insufficient_3d_samples():
    samples = [sample(index, mode="2d", yaw=40.0) for index in range(5)]
    with pytest.raises(ValueError, match="not_enough_3d_orientation_samples"):
        aggregate_camera_reference(
            samples,
            minimum_count=5,
            orientation_mode="3d",
            minimum_3d_orientation_samples=3,
        )


def test_auto_falls_back_to_consistent_raw_2d():
    samples = [sample(index, mode="2d", yaw=40.0) for index in range(5)]
    reference = aggregate_camera_reference(
        samples,
        minimum_count=5,
        orientation_mode="auto",
        minimum_3d_orientation_samples=3,
    )
    assert reference.orientation_mode == "2d"
    assert reference.orientation_source == "image_axis_2d"
    assert reference.orientation_coordinate_frame == "camera_image"
    assert reference.orientation_deg == pytest.approx(40.4, abs=0.5)


def test_auto_mode_can_fallback_to_raw_2d_from_3d_payloads():
    from dataclasses import replace

    samples = [
        replace(
            sample(index, mode="3d", yaw=30.0 + 0.1 * index),
            orientation_quality=0.2,
            orientation_2d_deg=72.0 + 0.1 * index,
            orientation_2d_quality=0.8,
        )
        for index in range(5)
    ]
    reference = aggregate_camera_reference(
        samples,
        minimum_count=5,
        orientation_mode="auto",
        minimum_orientation_quality=0.45,
        minimum_3d_orientation_samples=3,
        minimum_2d_orientation_samples=3,
    )
    assert reference.orientation_mode == "2d"
    assert reference.orientation_coordinate_frame == "camera_image"
    assert abs(reference.orientation_deg - 72.2) < 0.5
