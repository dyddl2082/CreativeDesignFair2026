from __future__ import annotations

import math

from macrobot_pick_pipeline.orientation_control import assess_orientation
from macrobot_pick_pipeline.orientation_domain import (
    axis_from_mapping,
    axial_yaw_deg,
    signed_axial_axis_error_deg,
)


def axis(yaw_deg: float):
    angle = math.radians(yaw_deg)
    return (math.cos(angle), math.sin(angle), 0.0)


def test_signed_axis_error_is_axial_and_signed():
    assert abs(signed_axial_axis_error_deg(axis(12.0), axis(2.0)) - 10.0) < 1e-9
    assert abs(signed_axial_axis_error_deg(axis(2.0), axis(12.0)) + 10.0) < 1e-9
    assert abs(signed_axial_axis_error_deg(axis(182.0), axis(2.0))) < 1e-9


def test_axis_mapping_is_normalized():
    parsed = axis_from_mapping({"x": 3.0, "y": 4.0, "z": 0.0})
    assert parsed is not None
    assert abs(math.sqrt(sum(value * value for value in parsed)) - 1.0) < 1e-9
    assert abs(axial_yaw_deg(parsed) - math.degrees(math.atan2(4.0, 3.0))) < 1e-9


def test_assessment_uses_3d_axis_domain():
    result = assess_orientation(
        current_deg=0.0,
        current_quality=0.8,
        reference_deg=0.0,
        minimum_quality=0.45,
        tolerance_deg=4.0,
        current_axis_base=axis(15.0),
        reference_axis_base=axis(5.0),
        current_coordinate_frame="base_link",
        reference_coordinate_frame="base_link",
        current_semantics="axial_yaw",
        reference_semantics="axial_yaw",
    )
    assert result.comparison_mode == "base_link_axis_3d"
    assert result.state == "angle_mismatch"
    assert abs(result.signed_error_deg - 10.0) < 1e-9


def test_one_sided_domain_metadata_is_rejected():
    result = assess_orientation(
        current_deg=10.0,
        current_quality=0.9,
        reference_deg=10.0,
        minimum_quality=0.45,
        tolerance_deg=4.0,
        current_coordinate_frame="base_link",
        current_semantics="axial_yaw",
    )
    assert result.state == "quality_low"
    assert result.comparison_mode == "incompatible"
    assert "orientation_domain_mismatch" in result.reason
