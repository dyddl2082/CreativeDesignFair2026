from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAMERA = ROOT / "macrobot_pick_pipeline" / "camera_authoritative_task_node.py"
RESILIENT = ROOT / "macrobot_pick_pipeline" / "resilient_object_task_node.py"
STORED = ROOT / "macrobot_pick_pipeline" / "stored_object_pick_node.py"
CONFIG = ROOT / "config" / "stored_object_pick.yaml"


def test_camera_authoritative_place_side_turn_policy_is_present():
    source = CAMERA.read_text(encoding="utf-8")
    assert "PLACE_SIDE_TURN_CAMERA_POLICY_V1_1" in source
    assert 'placement_policy="camera_side_turn_then_held_taught_reachable_point"' in source
    assert 'self._send_turn(amount, "resilient_place_side_turn")' in source
    assert "visual_recenter_after_side_turn=False" in source
    assert "held_runtime.alignment.reference_point_base" in source


def test_side_turn_defaults_are_15_deg_and_chunked():
    source = CAMERA.read_text(encoding="utf-8")
    config = CONFIG.read_text(encoding="utf-8")
    assert '"place_side_turn_deg": 15.0' in source
    assert '"place_side_turn_chunk_deg": 4.0' in source
    assert "place_side_turn_enabled: true" in config
    assert "place_side_turn_deg: 15.0" in config
    assert "place_side_turn_chunk_deg: 4.0" in config


def test_place_override_is_camera_authoritative_only():
    camera = CAMERA.read_text(encoding="utf-8")
    resilient = RESILIENT.read_text(encoding="utf-8")
    assert "def _alignment_complete(self) -> None:" in camera
    assert "PLACE_SIDE_TURN_CAMERA_POLICY_V1_1" not in resilient


def test_turn_sign_contract_remains_in_existing_boundary():
    camera = CAMERA.read_text(encoding="utf-8")
    stored = STORED.read_text(encoding="utf-8")
    config = CONFIG.read_text(encoding="utf-8")
    assert 'self._send_turn(amount, "resilient_place_side_turn")' in camera
    assert "pico_turn_command_deg(" in stored
    assert "pico_positive_is_right=self.pico_turn_positive_is_right" in stored
    assert "pico_turn_positive_is_right: true" in config


def test_legacy_resilient_place_path_is_retained_for_rollback():
    resilient = RESILIENT.read_text(encoding="utf-8")
    assert "self.last_object_point[index] + self.place_offset_base[index]" in resilient
