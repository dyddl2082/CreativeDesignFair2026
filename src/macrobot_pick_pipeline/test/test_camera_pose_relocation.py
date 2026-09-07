import math

from macrobot_pick_pipeline.camera_pose_relocation import (
    MotionPrimitive,
    apply_ideal_primitive_to_object,
    decompose_drive_then_turn,
    decompose_turn_move_turn,
    object_after_relative_robot_pose,
    plan_range_relocation,
    plan_viewpoint_relocation,
    relative_pose_from_primitives,
    robot_pose_for_object_target,
    signed_axial_error_deg,
)


def execute(point, orientation, primitives, *, turn_scale=1.0, move_scale=1.0):
    for primitive in primitives:
        point, orientation = apply_ideal_primitive_to_object(
            point,
            orientation,
            primitive,
            turn_scale=turn_scale,
            move_scale=move_scale,
        )
    return point, orientation


def common_kwargs(**overrides):
    values = dict(
        current_object_xy=(0.38, 0.02),
        reference_object_xy=(0.22, 0.05),
        current_orientation_deg=48.0,
        reference_orientation_deg=10.0,
        anchor_range_m=math.hypot(0.38, 0.02),
        orientation_tolerance_deg=4.0,
        orbit_bearing_tolerance_deg=5.0,
        orbit_range_tolerance_m=0.025,
        forward_tolerance_m=0.005,
        lateral_tolerance_m=0.005,
        requested_progress=0.80,
        maximum_translation_m=0.12,
        maximum_turn_primitive_deg=95.0,
        minimum_object_range_m=0.10,
        allow_reverse=True,
        reverse_turn_penalty_deg=10.0,
        minimum_turn_deg=0.5,
        minimum_move_m=0.003,
        prefer_drive_rel=True,
        maximum_drive_yaw_deg=80.0,
        minimum_drive_radius_m=0.08,
    )
    values.update(overrides)
    return values


def test_robot_pose_maps_object_to_target_exactly():
    current = (0.33, 0.12)
    desired = (0.29, 0.06)
    pose = robot_pose_for_object_target(current, desired, 24.0)
    result = object_after_relative_robot_pose(current, pose)
    assert math.dist(result, desired) < 1e-9


def test_turn_move_turn_is_exact_in_ideal_kinematics():
    current = (0.31, -0.08)
    desired = (0.27, 0.05)
    current_orientation = 64.0
    reference_orientation = 12.0
    yaw = signed_axial_error_deg(current_orientation, reference_orientation)
    pose = robot_pose_for_object_target(current, desired, yaw)
    primitives = decompose_turn_move_turn(
        pose,
        allow_reverse=True,
        reverse_turn_penalty_deg=10.0,
        minimum_turn_deg=0.0,
        minimum_move_m=0.0,
    )
    point, orientation = execute(current, current_orientation, primitives)
    assert math.dist(point, desired) < 1e-9
    assert abs(signed_axial_error_deg(orientation, reference_orientation)) < 1e-9


def test_drive_then_turn_is_exact_and_uses_at_most_two_primitives():
    pose = robot_pose_for_object_target((0.35, 0.10), (0.31, 0.04), 28.0)
    primitives = decompose_drive_then_turn(
        pose,
        maximum_drive_yaw_deg=100.0,
        minimum_drive_radius_m=0.04,
        minimum_turn_deg=0.0,
        minimum_move_m=0.0,
    )
    assert len(primitives) <= 2
    assert primitives[0].kind == "drive"
    composed = relative_pose_from_primitives(primitives)
    assert math.hypot(composed.x_m - pose.x_m, composed.y_m - pose.y_m) < 1e-9
    assert abs(signed_axial_error_deg(composed.yaw_deg, pose.yaw_deg)) < 1e-9


def test_reverse_drive_arc_can_reach_a_target_behind_the_robot():
    pose = robot_pose_for_object_target((0.20, 0.0), (0.35, 0.04), 12.0)
    primitives = decompose_drive_then_turn(
        pose,
        maximum_drive_yaw_deg=100.0,
        minimum_drive_radius_m=0.04,
        minimum_turn_deg=0.0,
        minimum_move_m=0.0,
    )
    assert primitives[0].kind == "drive"
    assert primitives[0].amount < 0.0
    composed = relative_pose_from_primitives(primitives)
    assert math.hypot(composed.x_m - pose.x_m, composed.y_m - pose.y_m) < 1e-9


def test_viewpoint_stage_preserves_anchor_range_and_matches_reference_bearing():
    plan = plan_viewpoint_relocation(**common_kwargs())
    assert not plan.reached
    assert plan.primitives
    assert plan.total_move_m <= 0.12 + 1e-9
    assert max(
        [
            abs(item.amount if item.kind == "turn" else item.yaw_deg)
            for item in plan.primitives
            if item.kind in {"turn", "drive"}
        ]
        or [0.0]
    ) <= 95.0 + 1e-9
    assert plan.decomposition in {
        "drive_rel_then_turn",
        "turn_move_turn_fallback",
    }


def test_range_stage_reports_reached_at_five_millimetres_and_four_degrees():
    plan = plan_range_relocation(
        **common_kwargs(
            current_object_xy=(0.224, 0.046),
            reference_object_xy=(0.22, 0.05),
            current_orientation_deg=13.5,
            reference_orientation_deg=10.0,
            anchor_range_m=0.30,
            requested_progress=0.85,
            maximum_translation_m=0.10,
        )
    )
    assert plan.reached
    assert not plan.primitives


def test_closed_loop_converges_with_five_percent_motion_scale_error():
    point = (0.35, 0.12)
    orientation = 60.0
    reference = (0.22, 0.05)
    reference_orientation = 10.0
    anchor = math.hypot(*point)
    stage = "viewpoint"

    for _ in range(18):
        kwargs = common_kwargs(
            current_object_xy=point,
            reference_object_xy=reference,
            current_orientation_deg=orientation,
            reference_orientation_deg=reference_orientation,
            anchor_range_m=anchor,
            requested_progress=0.80 if stage == "viewpoint" else 0.85,
            maximum_translation_m=0.12 if stage == "viewpoint" else 0.10,
        )
        plan = (
            plan_viewpoint_relocation(**kwargs)
            if stage == "viewpoint"
            else plan_range_relocation(**kwargs)
        )
        if plan.reached:
            if stage == "viewpoint":
                stage = "range"
                continue
            break
        point, orientation = execute(
            point,
            orientation,
            plan.primitives,
            turn_scale=0.95,
            move_scale=1.05,
        )
    else:
        raise AssertionError("controller did not converge")

    assert stage == "range"
    assert abs(point[0] - reference[0]) <= 0.005
    assert abs(point[1] - reference[1]) <= 0.005
    assert abs(
        signed_axial_error_deg(orientation, reference_orientation)
    ) <= 4.0


def test_tight_drive_arc_falls_back_to_turn_move_turn():
    plan = plan_viewpoint_relocation(
        **common_kwargs(
            current_object_xy=(0.28, 0.18),
            reference_object_xy=(0.25, -0.12),
            current_orientation_deg=70.0,
            reference_orientation_deg=5.0,
            minimum_drive_radius_m=0.50,
        )
    )
    assert plan.decomposition == "turn_move_turn_fallback"
    assert any(item.kind == "move" for item in plan.primitives)


def test_reverse_candidate_can_reduce_turning_in_fallback():
    pose = robot_pose_for_object_target((0.20, 0.0), (0.35, 0.0), 0.0)
    primitives = decompose_turn_move_turn(
        pose,
        allow_reverse=True,
        reverse_turn_penalty_deg=0.0,
        minimum_turn_deg=0.0,
        minimum_move_m=0.0,
    )
    move = next(item for item in primitives if item.kind == "move")
    assert move.amount < 0.0
