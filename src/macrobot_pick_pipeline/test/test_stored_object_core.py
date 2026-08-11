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
