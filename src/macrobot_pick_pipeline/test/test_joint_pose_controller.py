from __future__ import annotations

import math

import pytest

from macrobot_pick_pipeline.joint_pose_controller import (
    JointPoseConfig,
    ObjectPoseState,
    ObjectPoseTarget,
    Primitive,
    apply_primitive,
    apply_sequence,
    goal_error,
    is_aligned,
    primitive_admissibility,
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
        state,
        target,
        orientation_required=True,
    )
    angle = math.radians(goal.yaw_deg)
    translated = (state.forward_m - goal.x_m, state.lateral_m - goal.y_m)
    observed = (
        math.cos(angle) * translated[0] + math.sin(angle) * translated[1],
        -math.sin(angle) * translated[0] + math.cos(angle) * translated[1],
    )
    assert observed[0] == pytest.approx(target.forward_m, abs=1e-9)
    assert observed[1] == pytest.approx(target.lateral_m, abs=1e-9)
    assert wrap_axial_deg(state.orientation_error_deg - goal.yaw_deg) == pytest.approx(
        0.0, abs=1e-9
    )


def test_rigid_body_turn_changes_point_and_axis_together() -> None:
    state = ObjectPoseState(0.30, 0.02, 12.0)
    predicted = apply_primitive(state, Primitive("turn", 4.0))
    assert predicted.planar_range_m == pytest.approx(state.planar_range_m)
    assert predicted.bearing_deg == pytest.approx(state.bearing_deg - 4.0)
    assert predicted.orientation_error_deg == pytest.approx(8.0)


@pytest.mark.parametrize(
    "state",
    [
        ObjectPoseState(0.26, 0.0, 9.21, 0.8, True),
        ObjectPoseState(0.36, 0.035, 16.0, 0.8, True),
        ObjectPoseState(0.22, -0.022, -12.0, 0.8, True),
    ],
)
def test_weighted_lattice_finds_a_joint_goal_route(state: ObjectPoseState) -> None:
    cfg = config()
    target = ObjectPoseTarget(0.26, 0.0)
    decision = select_joint_pose_plan(
        state,
        target,
        cfg,
        orientation_required=True,
    )
    assert not decision.hold
    assert decision.search_reached_goal
    assert decision.sequence
    assert len(decision.sequence) == 1
    terminal = apply_sequence(state, decision.route_preview)
    assert is_aligned(terminal, target, cfg, orientation_required=True)
    assert decision.planned_terminal_cost < decision.current_cost


def test_every_selected_route_state_respects_range_front_and_fov_bounds() -> None:
    cfg = config()
    state = ObjectPoseState(0.36, 0.035, 16.0, 0.8, True)
    target = ObjectPoseTarget(0.26, 0.0)
    decision = select_joint_pose_plan(
        state,
        target,
        cfg,
        orientation_required=True,
    )
    current = state
    for primitive in decision.route_preview:
        valid, reason, current, minimum_range, maximum_bearing = (
            primitive_admissibility(current, primitive, cfg)
        )
        assert valid, reason
        assert minimum_range >= cfg.minimum_object_range_m
        assert maximum_bearing <= cfg.maximum_predicted_bearing_deg
        assert current.forward_m >= cfg.minimum_object_forward_m


def test_planner_can_accept_non_monotonic_first_step_for_a_better_joint_route() -> None:
    cfg = config()
    state = ObjectPoseState(0.26, 0.0, 9.21, 0.8, True)
    target = ObjectPoseTarget(0.26, 0.0)
    decision = select_joint_pose_plan(
        state,
        target,
        cfg,
        orientation_required=True,
    )
    immediate = goal_error(
        decision.predicted_state,
        target,
        cfg,
        orientation_required=True,
    )
    # The first camera observation need not improve.  What matters is that the
    # bounded route jointly restores point and direction.
    assert decision.planned_terminal_cost < decision.current_cost
    assert immediate >= 0.0
    assert decision.search_reached_goal


def test_recent_two_cycle_is_hard_rejected_at_first_action() -> None:
    cfg = config(hard_reject_recent_cycle=True)
    state = ObjectPoseState(0.36, 0.035, 16.0, 0.8, True)
    target = ObjectPoseTarget(0.26, 0.0)
    baseline = select_joint_pose_plan(
        state,
        target,
        cfg,
        orientation_required=True,
    )
    forbidden = apply_primitive(state, baseline.sequence[0])
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


def test_unreliable_orientation_approaches_position_then_holds() -> None:
    cfg = config(position_only_when_orientation_unreliable=True)
    target = ObjectPoseTarget(0.26, 0.0)
    far = ObjectPoseState(0.34, 0.018, 30.0, 0.2, False)
    approach = select_joint_pose_plan(
        far,
        target,
        cfg,
        orientation_required=True,
    )
    assert not approach.orientation_effective
    assert approach.sequence

    at_position = ObjectPoseState(0.26, 0.0, 30.0, 0.2, False)
    hold = select_joint_pose_plan(
        at_position,
        target,
        cfg,
        orientation_required=True,
    )
    assert hold.hold
    assert hold.reason == "position_reached_orientation_unreliable_hold"


def test_reverse_safety_gate_can_prevent_an_unsafe_near_pose_manoeuvre() -> None:
    cfg = config(
        allow_reverse=False,
        search_maximum_expansions=3000,
        search_maximum_wall_time_sec=1.0,
        maximum_predicted_bearing_deg=48.0,
    )
    state = ObjectPoseState(0.26, 0.0, 9.21, 0.8, True)
    decision = select_joint_pose_plan(
        state,
        ObjectPoseTarget(0.26, 0.0),
        cfg,
        orientation_required=True,
    )
    assert decision.hold
    assert decision.reason == "joint_lattice_no_safe_improving_route"
    assert decision.search_expansions <= cfg.search_maximum_expansions


def simulate_closed_loop(initial: ObjectPoseState, max_steps: int = 80) -> ObjectPoseState:
    cfg = config()
    target = ObjectPoseTarget(0.26, 0.0)
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
        primitive = decision.sequence[0]
        # Deterministic encoder/track scale error.  The next iteration replans
        # from camera state rather than integrating this model as odometry truth.
        if primitive.kind == "turn":
            actual = Primitive("turn", primitive.amount * 0.97)
        elif primitive.kind == "move":
            actual = Primitive("move", primitive.amount * 1.02)
        else:
            actual = Primitive(
                "drive",
                primitive.amount * 1.02,
                primitive.yaw_deg * 0.97,
            )
        recent.append(state)
        state = apply_primitive(state, actual)
        previous = primitive
    raise AssertionError(f"controller did not converge: {state}")


@pytest.mark.parametrize(
    "initial",
    [
        ObjectPoseState(0.26, 0.0, 9.21, 0.8, True),
        ObjectPoseState(0.36, 0.035, 16.0, 0.8, True),
        ObjectPoseState(0.22, -0.022, -12.0, 0.8, True),
    ],
)
def test_camera_reset_replanning_converges_with_actuator_scale_error(
    initial: ObjectPoseState,
) -> None:
    cfg = config()
    target = ObjectPoseTarget(0.26, 0.0)
    result = simulate_closed_loop(initial)
    assert is_aligned(result, target, cfg, orientation_required=True)


def test_configuration_rejects_invalid_search_limits() -> None:
    with pytest.raises(ValueError):
        config(search_maximum_expansions=0).validate()
    with pytest.raises(ValueError):
        config(search_maximum_wall_time_sec=0.0).validate()


def test_configuration_enforces_one_primitive_per_camera_reset() -> None:
    with pytest.raises(ValueError, match="exactly 1"):
        config(execution_prefix_length=2).validate()


def test_infeasible_search_obeys_wall_time_budget() -> None:
    cfg = config(
        allow_reverse=False,
        search_maximum_expansions=25000,
        search_maximum_wall_time_sec=0.025,
        maximum_predicted_bearing_deg=48.0,
    )
    started = __import__("time").perf_counter()
    decision = select_joint_pose_plan(
        ObjectPoseState(0.26, 0.0, 9.21, 0.8, True),
        ObjectPoseTarget(0.26, 0.0),
        cfg,
        orientation_required=True,
    )
    elapsed = __import__("time").perf_counter() - started
    assert decision.hold
    # Generous CI margin; the algorithm checks time every 16 expansions.
    assert elapsed < 0.25
