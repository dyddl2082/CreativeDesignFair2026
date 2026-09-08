from __future__ import annotations

import math
import time

import pytest

from macrobot_pick_pipeline.joint_pose_controller import (
    JointPoseConfig,
    ObjectPoseState,
    ObjectPoseTarget,
    Primitive,
    apply_primitive,
    apply_sequence,
    axis_corridor_error,
    candidate_maneuvers,
    fuse_axial_orientation_error,
    goal_error,
    is_aligned,
    primitive_admissibility,
    representative_primitive,
    robot_goal_for_taught_object_pose,
    select_joint_pose_plan,
    states_near,
    wrap_axial_deg,
)


def config(**updates) -> JointPoseConfig:
    values = JointPoseConfig().__dict__.copy()
    values.update(
        {
            "allow_reverse": True,
            "drive_enabled": True,
            "maximum_predicted_bearing_deg": 58.0,
            "maximum_object_range_m": 1.0,
        }
    )
    values.update(updates)
    return JointPoseConfig(**values)


def test_exact_robot_goal_recreates_taught_point_and_axis() -> None:
    state = ObjectPoseState(0.34, 0.035, 17.0)
    target = ObjectPoseTarget(0.26, -0.004)
    goal = robot_goal_for_taught_object_pose(
        state, target, orientation_required=True
    )
    heading = math.degrees(math.atan2(goal.y_m, goal.x_m))
    distance = math.hypot(goal.x_m, goal.y_m)
    sequence = (
        Primitive("turn", heading),
        Primitive("move", distance),
        Primitive("turn", goal.yaw_deg - heading),
    )
    observed = apply_sequence(state, sequence)
    assert observed.forward_m == pytest.approx(target.forward_m, abs=1e-9)
    assert observed.lateral_m == pytest.approx(target.lateral_m, abs=1e-9)
    assert observed.orientation_error_deg == pytest.approx(0.0, abs=1e-9)


def test_rigid_body_turn_changes_point_and_axis_together() -> None:
    state = ObjectPoseState(0.30, 0.02, 12.0)
    predicted = apply_primitive(state, Primitive("turn", 4.0))
    assert predicted.planar_range_m == pytest.approx(state.planar_range_m)
    assert predicted.bearing_deg == pytest.approx(state.bearing_deg - 4.0)
    assert predicted.orientation_error_deg == pytest.approx(8.0)


def test_straight_retreat_can_shrink_bearing_without_fixing_axis() -> None:
    state = ObjectPoseState(0.25, 0.04, 0.0)
    target = ObjectPoseTarget(0.25, 0.0)
    cfg = config()
    before_axis = axis_corridor_error(
        robot_goal_for_taught_object_pose(
            state, target, orientation_required=True
        )
    )
    retreated = apply_primitive(state, Primitive("move", -0.04))
    after_axis = axis_corridor_error(
        robot_goal_for_taught_object_pose(
            retreated, target, orientation_required=True
        )
    )
    assert abs(retreated.bearing_deg) < abs(state.bearing_deg)
    assert retreated.orientation_error_deg == pytest.approx(
        state.orientation_error_deg
    )
    assert after_axis.cross_track_m == pytest.approx(before_axis.cross_track_m)
    assert goal_error(
        retreated, target, cfg, orientation_required=True
    ) > 0.0


def test_translation_orientation_filter_rejects_fake_improvement() -> None:
    cfg = config()
    result = fuse_axial_orientation_error(
        previous_error_deg=15.0,
        measured_error_deg=7.0,
        measurement_quality=1.0,
        expected_robot_yaw_deg=0.0,
        motion_kind="move",
        config=cfg,
    )
    assert result.mode == "translation_invariant"
    assert result.clipped_innovation_deg == pytest.approx(-1.0)
    assert result.filtered_error_deg == pytest.approx(14.97)
    assert result.filtered_error_deg > 14.0


def test_orientation_filter_tracks_commanded_yaw() -> None:
    cfg = config()
    result = fuse_axial_orientation_error(
        previous_error_deg=15.0,
        measured_error_deg=9.0,
        measurement_quality=1.0,
        expected_robot_yaw_deg=5.0,
        motion_kind="yaw_macro",
        config=cfg,
    )
    assert result.mode == "yaw_prediction_fusion"
    assert result.predicted_error_deg == pytest.approx(10.0)
    assert result.filtered_error_deg == pytest.approx(9.55)


def test_off_axis_decision_is_never_pure_retreat_or_pure_turn() -> None:
    cfg = config()
    state = ObjectPoseState(0.36, 0.035, 16.0, 0.8, True)
    target = ObjectPoseTarget(0.25, 0.0)
    decision = select_joint_pose_plan(
        state, target, cfg, orientation_required=True
    )
    assert not decision.hold
    assert decision.sequence
    assert abs(decision.current_axis_error.cross_track_m) > cfg.axis_corridor_tolerance_m
    assert any(abs(item.effective_move_m) > 0.0 for item in decision.sequence)
    assert any(
        abs(item.effective_turn_deg) >= cfg.minimum_coupled_steering_deg
        for item in decision.sequence
    )
    assert not (
        len(decision.sequence) == 1
        and decision.sequence[0].kind in {"move", "turn"}
    )


def test_final_pure_turn_is_allowed_only_at_the_axis_gate() -> None:
    angle_deg = 2.0
    angle = math.radians(angle_deg)
    target = ObjectPoseTarget(0.25, 0.0)
    state = ObjectPoseState(
        0.25 * math.cos(angle),
        0.25 * math.sin(angle),
        angle_deg,
    )
    cfg = config(orientation_tolerance_deg=0.5)
    decision = select_joint_pose_plan(
        state, target, cfg, orientation_required=True
    )
    assert decision.maneuver_type == "final_axis_turn"
    assert decision.sequence == (Primitive("turn", angle_deg),)
    assert is_aligned(
        decision.predicted_state,
        target,
        cfg,
        orientation_required=True,
    )


def test_alignment_gate_checks_exact_final_axis_not_only_independent_tolerances() -> None:
    cfg = config(
        orientation_tolerance_deg=4.0,
        axis_corridor_tolerance_m=0.008,
    )
    state = ObjectPoseState(0.25, 0.0, 2.0)
    target = ObjectPoseTarget(0.25, 0.0)
    # Point and orientation pass their individual limits, but 2 degrees at
    # 0.25 m still implies about 8.7 mm of final-axis displacement.
    assert abs(state.orientation_error_deg) < cfg.orientation_tolerance_deg
    assert not is_aligned(state, target, cfg, orientation_required=True)


def test_reverse_clearance_gate_reports_required_local_shift() -> None:
    state = ObjectPoseState(0.20, -0.04, -5.0, 0.8, True)
    target = ObjectPoseTarget(0.25, 0.0)
    blocked = select_joint_pose_plan(
        state,
        target,
        config(allow_reverse=False),
        orientation_required=True,
    )
    assert blocked.hold
    assert blocked.reason == "joint_pose_local_axis_shift_requires_reverse_clearance"

    allowed = select_joint_pose_plan(
        state,
        target,
        config(allow_reverse=True),
        orientation_required=True,
    )
    assert not allowed.hold
    assert any(item.effective_move_m < 0.0 for item in allowed.sequence)
    assert any(abs(item.effective_turn_deg) > 0.0 for item in allowed.sequence)


def test_drive_candidates_obey_minimum_radius() -> None:
    cfg = config(drive_enabled=True, minimum_drive_radius_m=0.09)
    state = ObjectPoseState(0.36, 0.035, 16.0)
    target = ObjectPoseTarget(0.25, 0.0)
    drives = [
        sequence[0]
        for kind, sequence in candidate_maneuvers(
            state, target, cfg, orientation_required=True
        )
        if kind.startswith("drive")
    ]
    assert drives
    for primitive in drives:
        radius = abs(primitive.amount / math.radians(primitive.yaw_deg))
        assert radius >= cfg.minimum_drive_radius_m - 1e-9


def test_selected_macro_respects_range_front_and_fov_bounds() -> None:
    cfg = config()
    state = ObjectPoseState(0.36, 0.035, 16.0, 0.8, True)
    target = ObjectPoseTarget(0.25, 0.0)
    decision = select_joint_pose_plan(
        state, target, cfg, orientation_required=True
    )
    current = state
    for primitive in decision.sequence:
        valid, reason, current, minimum_range, maximum_bearing = (
            primitive_admissibility(current, primitive, cfg)
        )
        assert valid, reason
        assert minimum_range >= cfg.minimum_object_range_m
        assert maximum_bearing <= cfg.maximum_predicted_bearing_deg
        assert current.forward_m >= cfg.minimum_object_forward_m


def test_recent_cycle_is_hard_rejected() -> None:
    cfg = config(
        hard_reject_recent_cycle=True,
        cycle_required_cost_improvement=100.0,
    )
    state = ObjectPoseState(0.36, 0.035, 16.0, 0.8, True)
    target = ObjectPoseTarget(0.25, 0.0)
    baseline = select_joint_pose_plan(
        state, target, cfg, orientation_required=True
    )
    forbidden = baseline.predicted_state
    revised = select_joint_pose_plan(
        state,
        target,
        cfg,
        orientation_required=True,
        recent_states=(forbidden,),
    )
    assert revised.hold or not states_near(
        revised.predicted_state,
        forbidden,
        cfg,
        orientation_required=True,
    )


def test_clear_improvement_inside_cycle_radius_is_not_false_rejected() -> None:
    cfg = config(
        hard_reject_recent_cycle=True,
        cycle_required_cost_improvement=0.20,
    )
    state = ObjectPoseState(
        0.25164657834038745,
        -0.005090288876304486,
        0.07905751812479878,
        0.8,
        True,
    )
    target = ObjectPoseTarget(0.25, 0.0)
    # This older state is within the 10 mm cycle neighbourhood of a useful
    # terminal state, but its joint-pose cost is substantially worse.  The
    # controller must permit progress rather than confusing proximity with a
    # repeated loop.
    recent = ObjectPoseState(
        0.24746877011279358,
        -0.006250468279056219,
        0.07905751812479878,
        0.8,
        True,
    )
    decision = select_joint_pose_plan(
        state,
        target,
        cfg,
        orientation_required=True,
        recent_states=(recent,),
    )
    assert not decision.hold
    assert decision.expected_improvement > 0.0
    assert goal_error(
        decision.predicted_state,
        target,
        cfg,
        orientation_required=True,
    ) < goal_error(recent, target, cfg, orientation_required=True) - 0.20


def test_unreliable_orientation_approaches_position_then_holds() -> None:
    cfg = config(position_only_when_orientation_unreliable=True)
    target = ObjectPoseTarget(0.25, 0.0)
    far = ObjectPoseState(0.34, 0.018, 30.0, 0.2, False)
    approach = select_joint_pose_plan(
        far, target, cfg, orientation_required=True
    )
    assert not approach.orientation_effective
    assert approach.sequence

    at_position = ObjectPoseState(0.25, 0.0, 30.0, 0.2, False)
    hold = select_joint_pose_plan(
        at_position, target, cfg, orientation_required=True
    )
    assert hold.hold
    assert hold.reason == "position_reached_orientation_unreliable_hold"


def simulate_closed_loop(
    initial: ObjectPoseState, max_steps: int = 40
) -> ObjectPoseState:
    cfg = config()
    target = ObjectPoseTarget(0.25, 0.0)
    state = initial
    previous = None
    recent: list[ObjectPoseState] = []
    for _ in range(max_steps):
        decision = select_joint_pose_plan(
            state,
            target,
            cfg,
            orientation_required=True,
            previous_primitive=previous,
            recent_states=tuple(recent[-8:]),
        )
        if decision.aligned:
            return state
        assert not decision.hold, (state, decision.reason)
        actual: list[Primitive] = []
        for primitive in decision.sequence:
            # Deterministic track/encoder scale mismatch.  Each complete short
            # macro is followed by a fresh camera-state replan.
            if primitive.kind == "turn":
                actual.append(Primitive("turn", primitive.amount * 0.97))
            elif primitive.kind == "move":
                actual.append(Primitive("move", primitive.amount * 1.02))
            else:
                actual.append(
                    Primitive(
                        "drive",
                        primitive.amount * 1.02,
                        primitive.yaw_deg * 0.97,
                    )
                )
        recent.append(state)
        state = apply_sequence(state, actual)
        previous = representative_primitive(decision.sequence)
    raise AssertionError(f"controller did not converge: {state}")


@pytest.mark.parametrize(
    "initial",
    [
        ObjectPoseState(0.26, 0.0, 9.21, 0.8, True),
        ObjectPoseState(0.36, 0.035, 16.0, 0.8, True),
        ObjectPoseState(0.22, -0.022, -12.0, 0.8, True),
    ],
)
def test_camera_reset_macro_replanning_converges_with_actuator_scale_error(
    initial: ObjectPoseState,
) -> None:
    cfg = config()
    target = ObjectPoseTarget(0.25, 0.0)
    result = simulate_closed_loop(initial)
    assert is_aligned(result, target, cfg, orientation_required=True)


def test_configuration_rejects_invalid_limits() -> None:
    with pytest.raises(ValueError):
        config(search_maximum_expansions=0).validate()
    with pytest.raises(ValueError):
        config(search_maximum_wall_time_sec=0.0).validate()
    with pytest.raises(ValueError):
        config(search_maximum_depth=4).validate()
    with pytest.raises(ValueError):
        config(execution_prefix_length=4).validate()


def test_selection_runtime_is_bounded() -> None:
    cfg = config(
        allow_reverse=False,
        search_maximum_wall_time_sec=0.025,
        search_maximum_expansions=2000,
    )
    started = time.perf_counter()
    decision = select_joint_pose_plan(
        ObjectPoseState(0.20, -0.04, -5.0, 0.8, True),
        ObjectPoseTarget(0.25, 0.0),
        cfg,
        orientation_required=True,
    )
    elapsed = time.perf_counter() - started
    assert decision.hold
    # Generous CI margin including the reverse-feasibility explanation pass.
    assert elapsed < 0.35
