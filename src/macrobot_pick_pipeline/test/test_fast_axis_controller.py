import math

from macrobot_pick_pipeline.fast_axis_controller import (
    apply_primitives_to_object,
    axis_frame_error,
    choose_fast_axis_plan,
    simulate_until_handoff,
)


def test_axis_frame_error_uses_orientation_and_depth_together():
    error = axis_frame_error((0.40, 0.08), (0.28, 0.0), 40.0, 0.0)
    assert math.isclose(error.desired_robot_yaw_deg, 40.0, abs_tol=1e-9)
    assert abs(error.cross_track_error_m) > 0.10
    assert error.along_axis_error_m > 0.05


def test_lateral_offset_selects_one_atomic_axis_dogleg():
    plan = choose_fast_axis_plan((0.28, 0.05), (0.28, 0.0), 0.0, 0.0)
    assert plan.stage == "axis_intercept"
    assert plan.primitives
    assert [item.kind for item in plan.primitives] == ["turn", "move", "turn"]
    assert plan.target_point[1] == 0.0


def test_axis_intercept_targets_pregrasp_standoff_when_far():
    plan = choose_fast_axis_plan((0.55, 0.12), (0.28, 0.0), 35.0, 0.0)
    assert plan.stage == "axis_intercept"
    assert plan.target_point[0] <= 0.28 + 0.08 + 1e-9
    assert plan.target_point[1] == 0.0


def test_already_axis_aligned_target_uses_large_axial_approach():
    plan = choose_fast_axis_plan((0.48, 0.0), (0.28, 0.0), 0.0, 0.0)
    assert plan.stage == "axial_approach"
    assert plan.primitives
    assert plan.total_move_m > 0.05
    assert plan.total_move_m <= 0.150 + 1e-9


def test_default_planner_never_uses_reverse():
    cases = [
        ((0.40, 0.08), (0.28, 0.0), 40.0, 0.0),
        ((0.42, -0.08), (0.30, 0.01), 55.0, 5.0),
        ((0.28, 0.05), (0.28, 0.0), 0.0, 0.0),
    ]
    for current, reference, orientation, reference_orientation in cases:
        plan = choose_fast_axis_plan(
            current,
            reference,
            orientation,
            reference_orientation,
        )
        assert plan.primitives
        for primitive in plan.primitives:
            if primitive.kind in {"move", "drive"}:
                assert primitive.amount >= 0.0


def test_axis_macro_reduces_cross_track_and_orientation():
    current = (0.40, 0.08)
    reference = (0.28, 0.0)
    plan = choose_fast_axis_plan(current, reference, 40.0, 0.0)
    assert plan.stage == "axis_intercept"
    point, orientation = apply_primitives_to_object(
        current,
        40.0,
        plan.primitives,
    )
    after = axis_frame_error(point, reference, orientation, 0.0)
    assert abs(after.cross_track_error_m) < abs(plan.cross_track_error_m)
    assert abs(after.desired_robot_yaw_deg) < abs(plan.orientation_error_deg)


def test_calibrated_encoder_error_reaches_handoff_in_few_camera_cycles_a():
    reached, steps, _, _, stages = simulate_until_handoff(
        (0.55, 0.12),
        (0.28, 0.0),
        35.0,
        0.0,
        maximum_steps=8,
        move_scale=0.98,
        turn_scale=1.02,
    )
    assert reached
    assert steps <= 4
    assert "axis_intercept" in stages
    assert "axial_approach" in stages


def test_calibrated_encoder_error_reaches_handoff_in_few_camera_cycles_b():
    reached, steps, _, _, stages = simulate_until_handoff(
        (0.42, -0.08),
        (0.30, 0.01),
        55.0,
        5.0,
        maximum_steps=8,
        move_scale=1.02,
        turn_scale=0.97,
    )
    assert reached
    assert steps <= 5
    assert stages[-1] == "precision_handoff"


def test_modulo_180_axis_is_used():
    error = axis_frame_error((0.35, 0.02), (0.28, 0.0), 175.0, 5.0)
    assert math.isclose(error.desired_robot_yaw_deg, -10.0, abs_tol=1e-9)


def test_inside_handoff_box_emits_no_coarse_motion():
    plan = choose_fast_axis_plan((0.29, 0.004), (0.28, 0.0), 2.0, 0.0)
    assert plan.handoff_ready
    assert plan.stage == "precision_handoff"
    assert plan.primitives == ()


def test_extreme_axis_rotation_never_chooses_a_negative_target_range():
    plan = choose_fast_axis_plan(
        (0.41, -0.16),
        (0.30, 0.0),
        86.0,
        15.0,
    )
    assert plan.stage == "axis_intercept"
    assert plan.target_point[0] >= 0.12


def test_cleaned_subthreshold_primitive_is_accepted_with_bounded_residual():
    plan = choose_fast_axis_plan(
        (0.595, -0.090),
        (0.280, -0.005),
        -20.6,
        -12.4,
    )
    assert plan.primitives
    assert plan.reason == "fast_axis_compound_motion_selected"


def test_orientation_assessment_override_controls_axis_yaw():
    # A compatible 3-D axis assessment can differ from the scalar image angle.
    # The planner must use the assessed base_link-axis error for robot yaw.
    plan = choose_fast_axis_plan(
        (0.42, 0.06),
        (0.28, 0.0),
        4.0,
        0.0,
        orientation_error_override_deg=31.0,
    )
    assert math.isclose(plan.orientation_error_deg, 31.0, abs_tol=1e-9)
    assert math.isclose(plan.robot_target.yaw_deg, 31.0 * plan.progress, abs_tol=1e-6)
