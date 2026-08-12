from pathlib import Path


def _source(name: str) -> str:
    root = Path(__file__).resolve().parents[1]
    return (root / "macrobot_pick_pipeline" / name).read_text(encoding="utf-8")


def test_formal_node_keeps_legacy_gateway_topics():
    text = _source("stored_object_pick_node.py")
    assert '"legacy_goal_topic": "/macrobot/align_pick/goal"' in text
    assert '"legacy_result_topic": "/macrobot/base_alignment/result"' in text
    assert 'legacy = "align_pick_completed"' in text
    assert 'legacy = "alignment_completed"' in text


def test_cancel_waits_for_motion_stop_confirmation():
    text = _source("stored_object_pick_node.py")
    assert 'self.state = "CANCEL_REQUESTED"' in text
    assert 'self.cancel_wait_base = self.base_active' in text
    assert 'self.cancel_wait_arm = self.arm_active or self.pick_waiting' in text
    assert 'event == "trajectory_stopped"' in text
    assert 'status in {"stopped", "done", "timeout", "stall", "encoder_direction_error"}' in text
    assert '"SAFE_STOP_UNCONFIRMED"' in text


def test_recorded_grasp_uses_validated_arm_demo_player():
    text = _source("stored_object_pick_node.py")
    assert '"action": "play"' in text
    assert '"arm_demo_playback_completed"' in text
    assert 'self.arm_stop_pub.publish(Empty())' in text


def test_visible_test_is_a_thin_client_not_a_motion_controller():
    text = _source("visible_pick_test_node.py")
    assert '"mode": "visible_test"' in text
    assert '"start_finder": False' in text
    assert '/pico_debug/cmd' not in text
    assert '/macrobot/arm/joint_goal' not in text


def test_invalid_or_busy_goal_gets_terminal_result_with_same_request_id():
    text = _source("stored_object_pick_node.py")
    assert "def _publish_command_rejection" in text
    assert '"action_state": "FAILED"' in text
    assert 'event="stored_pick_rejected"' in text
    assert 'error_code=error_code' in text


def test_semantic_alignment_requires_preflight_before_success():
    text = _source("stored_object_pick_node.py")
    assert "def _alignment_complete" in text
    assert 'self.profile.grasp_executor == "keyframes"' in text
    assert "self._start_grasp_preflight()" in text
    assert "self.arm_active = True" in text
    assert '"action": "preflight"' in text


def test_keyframe_executor_assigns_command_id_before_preflight():
    text = _source("grasp_keyframe_node.py")
    start = text.index("def _start_plan")
    section = text[start:text.index("def _preflight", start)]
    assert section.index("self.command_id =") < section.index('self.state = "PREFLIGHT"')
    assert '"grasp_keyframe_preflight_succeeded"' in section


def test_keyframe_cancel_requires_trajectory_stopped_confirmation():
    text = _source("grasp_keyframe_node.py")
    assert '"cancel_confirm_timeout_sec": 4.0' in text
    assert 'if event == "trajectory_stopped"' in text
    assert 'waiting_for="trajectory_stopped"' in text
    assert '"grasp_keyframe_cancel_failed"' in text
    assert 'reason="SAFE_STOP_UNCONFIRMED"' in text


def test_localizer_strict_depth_mode_does_not_silently_use_candidate_depth():
    text = _source("detection_localizer_node.py")
    assert '"allow_candidate_depth_fallback": False' in text
    assert 'reason="aligned_depth_frame_not_synchronized"' in text
    assert 'source="unavailable"' in text
    assert 'source="finder_candidate_depth_fallback"' in text
