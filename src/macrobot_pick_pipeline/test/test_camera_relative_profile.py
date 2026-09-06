from pathlib import Path

from macrobot_pick_pipeline.alignment_core import AlignmentProfile
from macrobot_pick_pipeline.stored_object_core import (
    OdomPose,
    StoredObjectProfileStore,
    StoredObjectRuntimeProfile,
)


def test_camera_relative_profile_does_not_require_reliable_odom(tmp_path: Path):
    alignment = AlignmentProfile(
        name="Eraser",
        object_name="Eraser",
        pick_profile="Eraser",
        reference_point_base=(0.245, 0.062, 0.078),
        recorded_at="now",
        require_orientation_match=True,
        reference_orientation_deg=91.0,
        reference_orientation_class="vertical",
        reference_orientation_quality=0.8,
    )
    placeholder = OdomPose(0.0, 0.0, 0.0, False, None)
    profile = StoredObjectRuntimeProfile(
        name="Eraser",
        object_name="Eraser",
        recorded_at="now",
        search_pose_odom=placeholder,
        object_point_odom=(0.0, 0.0, 0.078),
        alignment=alignment,
        grasp_pose_odom=placeholder,
        recognition_point_base=alignment.reference_point_base,
        recognition_score=0.8,
        recording_state="complete",
        grasp_executor="keyframes",
        grasp_keyframe_profile="Eraser_r4",
        pick_profile="Eraser",
        position_scope="camera_relative",
        distance_handoff_enabled=False,
    )
    profile.validate_for_execution()

    store = StoredObjectProfileStore(tmp_path / "profiles.yaml", alignment)
    store.upsert(profile)
    loaded = StoredObjectProfileStore(tmp_path / "profiles.yaml", alignment).get(
        "Eraser"
    )
    assert loaded.position_scope == "camera_relative"
    assert loaded.distance_handoff_enabled is False
    mapping = loaded.to_mapping()
    assert mapping["execution_authority"] == "fresh_rgbd_localization"


def test_camera_relative_profile_refuses_legacy_odom_target():
    alignment = AlignmentProfile(
        name="Eraser",
        object_name="Eraser",
        pick_profile="Eraser",
        reference_point_base=(0.245, 0.062, 0.078),
        recorded_at="now",
    )
    profile = StoredObjectRuntimeProfile(
        name="Eraser",
        object_name="Eraser",
        recorded_at="now",
        search_pose_odom=OdomPose(0.0, 0.0, 0.0, False, None),
        object_point_odom=(0.0, 0.0, 0.078),
        alignment=alignment,
        grasp_pose_odom=OdomPose(0.0, 0.0, 0.0, False, None),
        recording_state="complete",
        grasp_executor="keyframes",
        grasp_keyframe_profile="Eraser_r4",
        position_scope="camera_relative",
        distance_handoff_enabled=False,
    )
    try:
        profile.target_grasp_pose((1.0, 2.0, 0.078))
    except ValueError as error:
        assert "do not define an odometry grasp pose" in str(error)
    else:
        raise AssertionError("camera-relative profile unexpectedly produced odom target")
