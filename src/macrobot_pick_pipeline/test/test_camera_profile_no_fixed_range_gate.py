from pathlib import Path

import pytest

from macrobot_pick_pipeline.alignment_core import AlignmentProfile
from macrobot_pick_pipeline.stored_object_core import (
    OdomPose,
    StoredObjectRuntimeProfile,
)


def _profile(*, scope: str, point_x: float) -> StoredObjectRuntimeProfile:
    alignment = AlignmentProfile(
        name="Eraser",
        object_name="Eraser",
        pick_profile="Eraser",
        reference_point_base=(point_x, 0.02, 0.08),
        recorded_at="now",
        require_orientation_match=True,
        reference_orientation_deg=90.0,
        reference_orientation_class="vertical",
        reference_orientation_quality=0.8,
    )
    reliable = scope != "camera_relative"
    odom = OdomPose(0.0, 0.0, 0.0, reliable, None)
    return StoredObjectRuntimeProfile(
        name="Eraser",
        object_name="Eraser",
        recorded_at="now",
        search_pose_odom=odom,
        object_point_odom=(0.0, 0.0, 0.08),
        alignment=alignment,
        grasp_pose_odom=odom,
        recognition_point_base=alignment.reference_point_base,
        recognition_score=0.8,
        recording_state="complete",
        grasp_executor="keyframes",
        grasp_keyframe_profile="Eraser_r4",
        pick_profile="Eraser",
        position_scope=scope,
        distance_handoff_enabled=(scope != "camera_relative"),
        recognition_min_range_m=0.32,
        recognition_max_range_m=1.20,
        graspable_min_range_m=0.08,
        graspable_max_range_m=0.30,
    )


def test_camera_relative_profile_uses_ik_not_fixed_030_gate():
    profile = _profile(scope="camera_relative", point_x=0.45)
    profile.validate_for_execution()
    mapping = profile.to_mapping()
    assert mapping["grasp"]["keyframe_profile"] == "Eraser_r4"
    assert mapping["grasp_keyframe_profile"] == "Eraser_r4"
    assert mapping["fixed_distance_gate_enabled"] is False
    assert "minimum_range_m" not in mapping["recognition"]
    assert "maximum_range_m" not in mapping["recognition"]
    assert "graspable_min_range_m" not in mapping["distance_handoff"]
    assert "graspable_max_range_m" not in mapping["distance_handoff"]
    assert mapping["distance_handoff"]["fixed_range_gate_enabled"] is False


def test_legacy_odom_profile_keeps_fixed_reach_gate():
    profile = _profile(scope="pico_odom_session", point_x=0.45)
    with pytest.raises(ValueError, match="exceeds arm reach"):
        profile.validate_for_execution()
