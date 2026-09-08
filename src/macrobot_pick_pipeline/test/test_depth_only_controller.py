from __future__ import annotations

import math
import pytest

from macrobot_pick_pipeline.depth_only_controller import (
    choose_depth_only_plan,
    simulate_depth_loop,
)


def test_far_object_gets_large_forward_step() -> None:
    plan = choose_depth_only_plan(0.42, 0.24)
    assert not plan.reached
    assert not plan.blocked
    assert plan.command_m == pytest.approx(0.08)
    assert plan.predicted_depth_m == pytest.approx(0.34)
    assert plan.reason == "bounded_forward_depth_correction"


def test_near_zone_uses_smaller_proportional_step() -> None:
    plan = choose_depth_only_plan(0.27, 0.24)
    assert not plan.reached
    assert not plan.blocked
    assert plan.progress == pytest.approx(0.65)
    assert plan.command_m == pytest.approx(0.0195)


def test_too_close_object_gets_bounded_reverse() -> None:
    plan = choose_depth_only_plan(0.18, 0.24)
    assert not plan.reached
    assert not plan.blocked
    assert plan.command_m == pytest.approx(-0.04)
    assert plan.predicted_depth_m == pytest.approx(0.22)
    assert plan.reason == "bounded_reverse_depth_correction"


def test_reverse_can_be_disabled() -> None:
    plan = choose_depth_only_plan(0.18, 0.24, allow_reverse=False)
    assert plan.blocked
    assert plan.command_m == 0.0
    assert plan.reason == "reverse_required_but_disabled"


def test_reached_ignores_orientation_by_api_design() -> None:
    plan = choose_depth_only_plan(0.246, 0.24)
    assert plan.reached
    assert not plan.blocked
    assert plan.reason == "forward_depth_within_tolerance"
    assert plan.command_m == 0.0


def test_lateral_value_is_not_corrected() -> None:
    plan = choose_depth_only_plan(
        0.34,
        0.24,
        current_lateral_m=0.05,
        reference_lateral_m=0.02,
    )
    assert not plan.blocked
    assert plan.command_m > 0.0
    assert plan.predicted_depth_m == pytest.approx(0.26)
    assert plan.current_lateral_m == pytest.approx(0.05)


def test_lateral_guard_blocks_but_never_turns() -> None:
    plan = choose_depth_only_plan(
        0.34,
        0.24,
        current_lateral_m=0.11,
        reference_lateral_m=0.0,
        maximum_lateral_delta_m=0.08,
    )
    assert plan.blocked
    assert plan.command_m == 0.0
    assert plan.reason == "lateral_delta_outside_depth_only_safety_guard"


def test_bearing_guard_blocks_large_off_axis_target() -> None:
    plan = choose_depth_only_plan(
        0.20,
        0.24,
        current_lateral_m=0.13,
        reference_lateral_m=0.13,
        maximum_lateral_delta_m=0.20,
        maximum_abs_bearing_deg=28.0,
    )
    assert abs(plan.bearing_deg) > 28.0
    assert plan.blocked
    assert plan.reason == "bearing_outside_depth_only_safety_guard"


def test_lateral_guards_can_be_disabled_explicitly() -> None:
    plan = choose_depth_only_plan(
        0.34,
        0.24,
        current_lateral_m=0.20,
        reference_lateral_m=0.0,
        lateral_guard_enabled=False,
    )
    assert not plan.blocked
    assert plan.command_m > 0.0


def test_forward_motion_never_crosses_minimum_depth() -> None:
    plan = choose_depth_only_plan(
        0.135,
        0.120,
        forward_tolerance_m=0.001,
        minimum_object_forward_m=0.12,
    )
    assert not plan.blocked
    assert plan.command_m <= 0.015 + 1e-12
    assert plan.predicted_depth_m >= 0.12 - 1e-12


def test_invalid_taught_depth_below_safety_limit_is_blocked() -> None:
    plan = choose_depth_only_plan(
        0.20,
        0.10,
        minimum_object_forward_m=0.12,
    )
    assert plan.blocked
    assert plan.reason == "taught_target_depth_below_minimum_object_forward"


@pytest.mark.parametrize("scale", [0.72, 0.90, 1.0, 1.08, 1.22])
def test_closed_loop_converges_despite_move_scale_error(scale: float) -> None:
    reached, steps, final_depth = simulate_depth_loop(
        0.46,
        0.24,
        move_scale=scale,
        maximum_steps=12,
    )
    assert reached
    assert steps <= 8
    assert abs(final_depth - 0.24) <= 0.008 + 1e-12


@pytest.mark.parametrize("scale", [0.75, 1.0, 1.20])
def test_reverse_closed_loop_converges(scale: float) -> None:
    reached, steps, final_depth = simulate_depth_loop(
        0.15,
        0.24,
        move_scale=scale,
        maximum_steps=12,
    )
    assert reached
    assert steps <= 8
    assert abs(final_depth - 0.24) <= 0.008 + 1e-12


def test_nonfinite_inputs_are_rejected() -> None:
    with pytest.raises(ValueError):
        choose_depth_only_plan(math.nan, 0.24)
