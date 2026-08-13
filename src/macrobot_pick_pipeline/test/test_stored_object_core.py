from pathlib import Path

import pytest

from macrobot_pick_pipeline.alignment_core import AlignmentProfile
from macrobot_pick_pipeline.stored_object_core import (
    OdomPose,
    StoredObjectProfileStore,
    StoredObjectRuntimeProfile,
    absolute_offsets_to_relative_turns,
    plan_return_to_pose,
    point_base_to_odom,
    pico_session_is_compatible,
    search_offsets,
)


def _alignment(name="Buds3"):
    return AlignmentProfile(
        name=name,
        object_name=name,
        pick_profile=name,
        reference_point_base=(-0.30, 0.05, 0.10),
        recorded_at="now",
        turn_speed=150,
        move_speed=80,
    )


def test_point_base_to_odom_respects_macrobot_axis_convention():
    # MacRobot forward is -base_link.x. At yaw=0, an object 30 cm ahead and
    # 5 cm left becomes odom (+0.30, +0.05).
    point = point_base_to_odom(
        (-0.30, 0.05, 0.10),
        OdomPose(1.0, 2.0, 0.0),
        forward_axis_sign=-1.0,
        lateral_axis_sign=1.0,
    )
    assert point == pytest.approx((1.30, 2.05, 0.10))


def test_point_base_to_odom_rotates_with_base_yaw():
    point = point_base_to_odom(
        (-0.30, 0.0, 0.10),
        OdomPose(1.0, 2.0, 90.0),
        forward_axis_sign=-1.0,
        lateral_axis_sign=1.0,
    )
    assert point == pytest.approx((1.0, 2.30, 0.10), abs=1e-8)


def test_return_plan_turn_move_turn():
    plan = plan_return_to_pose(
        OdomPose(0.0, 0.0, 0.0),
        OdomPose(1.0, 1.0, 90.0),
        position_tolerance_m=0.001,
        angle_tolerance_deg=0.1,
    )
    assert plan.initial_turn_deg == pytest.approx(45.0)
    assert plan.move_distance_m == pytest.approx(2 ** 0.5)
    assert plan.final_turn_deg == pytest.approx(45.0)
    assert plan.motion_count == 3


def test_search_offsets_return_sequence_can_be_closed():
    offsets = search_offsets(30.0, 10.0)
    assert offsets == (0.0, 10.0, -10.0, 20.0, -20.0, 30.0, -30.0)
    relative = absolute_offsets_to_relative_turns((*offsets, 0.0))
    assert relative == pytest.approx((0.0, 10.0, -20.0, 30.0, -40.0, 50.0, -60.0, 30.0))
    assert sum(relative) == pytest.approx(0.0)


def test_profile_store_roundtrip(tmp_path: Path):
    default = _alignment("default")
    store = StoredObjectProfileStore(tmp_path / "profiles.yaml", default)
    profile = StoredObjectRuntimeProfile(
        name="Buds3",
        object_name="Buds3",
        recorded_at="now",
        search_pose_odom=OdomPose(0.2, -0.1, 15.0, True, 1234),
        object_point_odom=(0.6, 0.0, 0.1),
        alignment=_alignment("Buds3"),
        grasp_executor="arm_demo",
        grasp_trajectory="Buds3_FIXED_PICK_V1",
        pick_profile="Buds3",
    )
    store.upsert(profile)
    loaded_store = StoredObjectProfileStore(tmp_path / "profiles.yaml", default)
    loaded = loaded_store.get("Buds3")
    assert loaded.object_name == "Buds3"
    assert loaded.search_pose_odom.x_m == pytest.approx(0.2)
    assert loaded.alignment.turn_speed == 150
    assert loaded.grasp_trajectory == "Buds3_FIXED_PICK_V1"


def test_pico_session_reset_guard():
    assert pico_session_is_compatible(10000, 12000, tolerance_ms=2000)
    assert pico_session_is_compatible(10000, 8500, tolerance_ms=2000)
    assert not pico_session_is_compatible(10000, 7000, tolerance_ms=2000)
    assert pico_session_is_compatible(None, 100, tolerance_ms=0)


def test_point_odom_to_base_roundtrip():
    from macrobot_pick_pipeline.stored_object_core import point_odom_to_base

    base = OdomPose(0.3, -0.2, 37.0)
    original = (-0.48, 0.06, 0.09)
    odom_point = point_base_to_odom(original, base)
    reconstructed = point_odom_to_base(odom_point, base)
    assert reconstructed == pytest.approx(original, abs=1e-9)


def test_two_stage_profile_translates_grasp_pose_with_object_shift():
    search_only = StoredObjectRuntimeProfile(
        name="Eraser",
        object_name="Eraser",
        recorded_at="now",
        search_pose_odom=OdomPose(0.0, 0.0, 0.0, True, 1000),
        object_point_odom=(0.50, 0.00, 0.09),
        alignment=_alignment("Eraser"),
        recording_state="search_only",
        recognition_point_base=(-0.50, 0.0, 0.09),
    )
    complete = search_only.with_grasp_recording(
        point_base=(-0.25, 0.0, 0.09),
        grasp_pose=OdomPose(0.25, 0.0, 0.0, True, 2000),
        object_name="Eraser",
        grasp_executor="keyframes",
        grasp_trajectory="",
        grasp_keyframe_profile="Eraser",
        pick_profile="Eraser",
        graspable_max_range_m=0.30,
    )
    target = complete.target_grasp_pose((0.60, -0.10, 0.09))
    assert target.x_m == pytest.approx(0.35)
    assert target.y_m == pytest.approx(-0.10)
    assert target.yaw_deg == pytest.approx(0.0)


def test_execution_profile_rejects_reference_outside_arm_reach():
    profile = StoredObjectRuntimeProfile(
        name="Eraser",
        object_name="Eraser",
        recorded_at="now",
        search_pose_odom=OdomPose(0.0, 0.0, 0.0, True, 1000),
        object_point_odom=(0.50, 0.0, 0.09),
        alignment=AlignmentProfile(
            name="Eraser",
            object_name="Eraser",
            pick_profile="Eraser",
            reference_point_base=(-0.35, 0.0, 0.09),
            recorded_at="now",
        ),
        grasp_pose_odom=OdomPose(0.15, 0.0, 0.0, True, 2000),
        recording_state="complete",
        grasp_executor="keyframes",
        grasp_keyframe_profile="Eraser",
        graspable_max_range_m=0.30,
    )
    with pytest.raises(ValueError, match="exceeds arm reach"):
        profile.validate_for_execution()


def test_handoff_uncertainty_includes_turn_translation_drift():
    from macrobot_pick_pipeline.stored_object_core import estimate_handoff_uncertainty_m

    value = estimate_handoff_uncertainty_m(
        acquisition_radius_m=0.005,
        acquisition_depth_std_m=0.004,
        traveled_distance_m=0.20,
        accumulated_turn_deg=360.0,
        target_range_m=0.25,
        linear_error_fraction=0.01,
        turn_error_fraction=0.0,
        turn_translation_drift_m_per_360=0.01,
    )
    assert value > 0.01


def test_return_plan_uses_reverse_for_pose_behind_with_similar_heading():
    plan = plan_return_to_pose(
        OdomPose(0.0, 0.0, 0.0),
        OdomPose(-0.17, 0.0, 0.0),
        position_tolerance_m=0.001,
        angle_tolerance_deg=0.1,
        allow_reverse=True,
        reverse_heading_tolerance_deg=90.0,
    )
    assert plan.initial_turn_deg == pytest.approx(0.0)
    assert plan.move_distance_m == pytest.approx(-0.17)
    assert plan.final_turn_deg == pytest.approx(0.0)
    assert plan.drive_direction == "reverse"
    assert plan.uses_reverse
    assert plan.motion_count == 1


def test_return_plan_does_not_reverse_for_front_half_plane_target():
    plan = plan_return_to_pose(
        OdomPose(0.0, 0.0, 0.0),
        OdomPose(0.17, 0.0, 0.0),
        position_tolerance_m=0.001,
        angle_tolerance_deg=0.1,
        allow_reverse=True,
        reverse_heading_tolerance_deg=90.0,
    )
    assert plan.initial_turn_deg == pytest.approx(0.0)
    assert plan.move_distance_m == pytest.approx(0.17)
    assert plan.final_turn_deg == pytest.approx(0.0)
    assert plan.drive_direction == "forward"
    assert not plan.uses_reverse


def test_return_plan_does_not_reverse_when_target_heading_differs_by_90_or_more():
    plan = plan_return_to_pose(
        OdomPose(0.0, 0.0, 0.0),
        OdomPose(-0.17, 0.0, 100.0),
        position_tolerance_m=0.001,
        angle_tolerance_deg=0.1,
        allow_reverse=True,
        reverse_heading_tolerance_deg=90.0,
    )
    assert plan.move_distance_m > 0.0
    assert plan.drive_direction == "forward"


def test_return_plan_uses_strictly_less_than_90_degree_reverse_threshold():
    plan = plan_return_to_pose(
        OdomPose(0.0, 0.0, 0.0),
        OdomPose(-0.17, 0.0, 90.0),
        position_tolerance_m=0.001,
        angle_tolerance_deg=0.1,
        allow_reverse=True,
        reverse_heading_tolerance_deg=90.0,
    )
    assert plan.drive_direction == "forward"
    assert plan.move_distance_m > 0.0
