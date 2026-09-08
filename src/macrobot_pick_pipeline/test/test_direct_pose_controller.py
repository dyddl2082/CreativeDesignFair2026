import math

from macrobot_pick_pipeline.direct_pose_controller import (
    apply_macro_to_object,
    choose_direct_pose_macro,
    exact_robot_pose_for_taught_view,
    simulate_closed_loop,
    signed_axial_error_deg,
)


def test_axial_error_is_modulo_180():
    assert math.isclose(signed_axial_error_deg(175.0, 5.0), -10.0, abs_tol=1e-9)
    assert math.isclose(signed_axial_error_deg(5.0, 175.0), 10.0, abs_tol=1e-9)


def test_exact_goal_uses_position_and_orientation_together():
    pose = exact_robot_pose_for_taught_view((0.35, 0.0), (0.28, 0.0), 30.0, 0.0)
    assert pose[0] > 0.09
    assert pose[1] < -0.13
    assert math.isclose(pose[2], 30.0, abs_tol=1e-9)


def test_default_planner_never_reverses():
    plan = choose_direct_pose_macro((0.40, 0.08), (0.28, 0.0), 40.0, 0.0)
    assert plan.primitives
    for primitive in plan.primitives:
        if primitive.kind in {"move", "drive"}:
            assert primitive.amount >= 0.0


def test_macro_moves_joint_pose_toward_reference():
    current = (0.35, 0.05)
    reference = (0.28, 0.0)
    plan = choose_direct_pose_macro(current, reference, 25.0, 0.0)
    assert plan.primitives
    point, orientation = apply_macro_to_object(current, 25.0, plan.primitives)
    before_position = math.hypot(current[0] - reference[0], current[1] - reference[1])
    after_position = math.hypot(point[0] - reference[0], point[1] - reference[1])
    assert after_position < before_position
    assert abs(signed_axial_error_deg(orientation, 0.0)) < 25.0


def test_noisy_encoder_closed_loop_converges_case_a():
    reached, steps, _, _ = simulate_closed_loop(
        (0.35, 0.05),
        (0.28, 0.0),
        25.0,
        0.0,
        maximum_steps=20,
        move_scale=1.02,
        turn_scale=0.97,
        planner_kwargs={"minimum_move_m": 0.002},
    )
    assert reached
    assert steps <= 8


def test_noisy_encoder_closed_loop_converges_case_b():
    reached, steps, _, _ = simulate_closed_loop(
        (0.40, 0.08),
        (0.28, 0.0),
        40.0,
        0.0,
        maximum_steps=20,
        move_scale=0.96,
        turn_scale=1.04,
        planner_kwargs={"minimum_move_m": 0.002},
    )
    assert reached
    assert steps <= 8


def test_lateral_offset_converges_without_reverse():
    reached, steps, _, _ = simulate_closed_loop(
        (0.28, 0.05),
        (0.28, 0.0),
        0.0,
        0.0,
        maximum_steps=20,
        planner_kwargs={"minimum_move_m": 0.002},
    )
    assert reached
    assert steps <= 5


def test_large_orientation_and_position_error_converges():
    reached, steps, _, _ = simulate_closed_loop(
        (0.42, -0.08),
        (0.30, 0.01),
        55.0,
        5.0,
        maximum_steps=20,
        planner_kwargs={"minimum_move_m": 0.002},
    )
    assert reached
    assert steps <= 10
