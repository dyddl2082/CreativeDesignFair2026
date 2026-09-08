import math

from macrobot_pick_pipeline.legacy_2d_controller import (
    axial_error_deg,
    choose_legacy_2d_plan,
)


def plan(**kwargs):
    base = dict(
        current_point=(0.40, 0.00),
        reference_point=(0.30, 0.00),
        current_orientation_deg=10.0,
        reference_orientation_deg=0.0,
        orientation_quality=0.8,
        orientation_corrections_used=0,
    )
    base.update(kwargs)
    return choose_legacy_2d_plan(**base)


def test_axial_wrap():
    assert axial_error_deg(175.0, 5.0) == -10.0
    assert axial_error_deg(5.0, 175.0) == 10.0


def test_bearing_is_corrected_before_range():
    p = plan(current_point=(0.40, 0.10))
    assert p.stage == "position_bearing"
    assert p.command_kind == "turn"
    assert 0.0 < p.command_yaw_deg <= 10.0


def test_range_move_after_bearing_ok():
    p = plan(current_point=(0.40, 0.0))
    assert p.stage == "position_range"
    assert p.command_kind == "move"
    assert 0.0 < p.command_amount <= 0.05


def test_reverse_is_bounded():
    p = plan(current_point=(0.25, 0.0))
    assert p.command_kind == "move"
    assert -0.020 <= p.command_amount < 0.0


def test_reverse_can_be_disabled():
    p = plan(current_point=(0.25, 0.0), allow_reverse=False)
    assert p.blocked
    assert p.reason == "reverse_required_but_disabled"


def test_orientation_is_soft_and_small():
    p = plan(
        current_point=(0.30, 0.0),
        current_orientation_deg=40.0,
        reference_orientation_deg=0.0,
    )
    assert p.stage == "orientation_soft"
    assert p.command_kind == "turn"
    assert math.isclose(p.command_yaw_deg, 7.0)


def test_orientation_low_quality_never_blocks():
    p = plan(
        current_point=(0.30, 0.0),
        current_orientation_deg=40.0,
        orientation_quality=0.1,
    )
    assert p.reached
    assert "quality_low" in p.reason


def test_orientation_budget_never_loops_forever():
    p = plan(
        current_point=(0.30, 0.0),
        current_orientation_deg=50.0,
        orientation_corrections_used=2,
    )
    assert p.reached
    assert "budget_exhausted" in p.reason


def test_inside_soft_orientation_band_reaches():
    p = plan(
        current_point=(0.30, 0.0),
        current_orientation_deg=15.0,
    )
    assert p.reached


def test_large_lateral_error_blocks_instead_of_pose_chasing():
    p = plan(current_point=(0.30, 0.03))
    assert p.blocked
    assert "lateral_error" in p.reason
