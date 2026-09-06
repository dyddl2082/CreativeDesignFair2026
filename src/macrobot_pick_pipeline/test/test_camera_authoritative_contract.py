from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE = ROOT / "macrobot_pick_pipeline" / "camera_authoritative_task_node.py"
CLI = ROOT / "macrobot_pick_pipeline" / "camera_grasp_teach_cli.py"
LAUNCH = ROOT / "launch" / "pick_pipeline_robot.launch.py"
CONFIG = ROOT / "config" / "stored_object_pick.yaml"


def test_camera_task_is_default_and_legacy_is_rollback():
    launch = LAUNCH.read_text(encoding="utf-8")
    assert 'default_value="camera_authoritative_task_node"' in launch
    assert "resilient_object_task_node" in launch


def test_camera_task_discards_pre_motion_frames_and_suppresses_odom_requests():
    source = NODE.read_text(encoding="utf-8")
    assert "persistent_odometry_request_suppressed" in source
    assert "discard_pre_motion_frames_wait_for_fresh_rgbd" in source
    assert "fresh_post_motion_camera_observation" in source
    assert "point_base_to_odom" not in source
    assert "point_odom_to_base" not in source


def test_integrated_teaching_uses_same_reference_for_keyframes_and_profile():
    source = CLI.read_text(encoding="utf-8")
    assert '"lock_reference"' in source
    assert '"camera_grasp"' in source
    assert "reference_status" in source
    assert "object_point_base" in source
    assert "object_orientation" in source
    assert "PRE_GRASP" in source and "GRASP_OPEN" in source and "LIFT" in source


def test_legacy_handoff_and_location_memory_are_disabled_in_config():
    text = CONFIG.read_text(encoding="utf-8")
    assert "distance_handoff_enabled: false" in text
    assert "use_same_epoch_location_hint: false" in text
    assert "camera_authoritative_mode: true" in text
    assert "camera_allow_legacy_record_commands: false" in text


def test_integrated_teaching_preserves_camera_reference_quality_metadata():
    cli = CLI.read_text(encoding="utf-8")
    node = (ROOT / "macrobot_pick_pipeline" / "grasp_keyframe_node.py").read_text(
        encoding="utf-8"
    )
    assert "reference_metadata" in cli
    assert "reference_metadata = data.get" in node
    assert "multi_frame_camera_teaching" in cli


def test_camera_teaching_rejects_in_flight_samples_from_before_session_start():
    source = CLI.read_text(encoding="utf-8")
    assert "reference_collection_not_before_sec" in source
    assert "sample.published_stamp_sec" in source
