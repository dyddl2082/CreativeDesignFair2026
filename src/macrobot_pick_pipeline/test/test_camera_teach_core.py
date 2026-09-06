import pytest

from macrobot_pick_pipeline.camera_teach_core import (
    CameraReferenceSample,
    aggregate_camera_reference,
    axial_error_deg,
    axial_mean_deg,
)


def _sample(
    x=0.245,
    y=0.062,
    z=0.078,
    angle=91.0,
    orientation_quality=0.80,
    localization_quality=0.90,
    depth_std=0.003,
    center_std=1.0,
):
    return CameraReferenceSample(
        point_base=(x, y, z),
        orientation_deg=angle,
        orientation_class="vertical",
        orientation_quality=orientation_quality,
        localization_quality=localization_quality,
        depth_std_m=depth_std,
        center_std_px=center_std,
        score=0.75,
        source_stamp_sec=100.0,
        published_stamp_sec=101.0,
    )


def test_camera_reference_uses_one_stable_point_and_orientation():
    samples = [
        _sample(x=0.245 + index * 0.0004, angle=90.0 + index * 0.4)
        for index in range(5)
    ]
    reference = aggregate_camera_reference(samples)
    assert reference.sample_count == 5
    assert reference.point_radius_m < 0.008
    assert axial_error_deg(reference.orientation_deg, 90.8) < 0.5
    assert reference.orientation_quality >= 0.45


def test_camera_reference_rejects_position_jitter():
    samples = [_sample() for _ in range(4)] + [_sample(x=0.280)]
    with pytest.raises(ValueError, match="camera_reference_position_unstable"):
        aggregate_camera_reference(samples)


def test_camera_reference_rejects_orientation_spread():
    samples = [_sample(angle=value) for value in (10.0, 12.0, 14.0, 50.0, 52.0)]
    with pytest.raises(ValueError, match="camera_reference_orientation_unstable"):
        aggregate_camera_reference(samples)


def test_axial_mean_handles_wraparound():
    result = axial_mean_deg([178.0, 179.0, 1.0, 2.0])
    assert min(result, 180.0 - result) < 2.0
