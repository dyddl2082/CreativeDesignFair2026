import math

from macrobot_pick_pipeline.camera_teach_core import (
    CameraReferenceSample,
    aggregate_camera_reference,
)
from macrobot_pick_pipeline.orientation_control import assess_orientation


def axis(yaw_deg: float):
    angle = math.radians(yaw_deg)
    return (math.cos(angle), math.sin(angle), 0.0)


def sample(index: int, yaw_deg: float, source: str, semantics: str):
    return CameraReferenceSample(
        point_base=(0.25 + 0.0001 * index, 0.06, 0.08),
        orientation_deg=yaw_deg,
        orientation_class="diagonal",
        orientation_quality=0.82,
        localization_quality=0.90,
        depth_std_m=0.002,
        center_std_px=0.5,
        score=0.85,
        source_stamp_sec=float(index),
        published_stamp_sec=float(index),
        orientation_source=source,
        orientation_coordinate_frame="base_link",
        orientation_semantics=semantics,
        orientation_axis_base=axis(yaw_deg),
        orientation_3d_available=True,
        orientation_2d_deg=70.0,
        orientation_2d_class="vertical",
        orientation_2d_quality=0.8,
    )


def test_teaching_prefers_upright_face_domain_over_old_long_axis():
    samples = [
        sample(0, 12.0, "depth_axis_3d", "axial_yaw"),
        sample(1, 13.0, "depth_axis_3d", "axial_yaw"),
        sample(2, 14.0, "depth_axis_3d", "axial_yaw"),
        sample(3, 31.0, "upright_face_plane_3d", "face_normal_yaw_mod_180"),
        sample(4, 32.0, "upright_face_plane_3d", "face_normal_yaw_mod_180"),
        sample(5, 33.0, "upright_face_plane_3d", "face_normal_yaw_mod_180"),
    ]
    reference = aggregate_camera_reference(
        samples,
        minimum_count=6,
        orientation_mode="auto",
        minimum_3d_orientation_samples=3,
    )
    assert reference.orientation_source == "upright_face_plane_3d"
    assert reference.orientation_coordinate_frame == "base_link"
    assert reference.orientation_semantics == "face_normal_yaw_mod_180"
    assert abs(reference.orientation_deg - 32.0) < 0.6


def test_upright_face_axis_is_compared_directly():
    result = assess_orientation(
        current_deg=0.0,
        current_quality=0.8,
        reference_deg=0.0,
        minimum_quality=0.45,
        tolerance_deg=4.0,
        current_axis_base=axis(17.0),
        reference_axis_base=axis(7.0),
        current_coordinate_frame="base_link",
        reference_coordinate_frame="base_link",
        current_semantics="face_normal_yaw_mod_180",
        reference_semantics="face_normal_yaw_mod_180",
    )
    assert result.comparison_mode == "base_link_axis_3d"
    assert result.state == "angle_mismatch"
    assert abs(result.signed_error_deg - 10.0) < 1e-9
