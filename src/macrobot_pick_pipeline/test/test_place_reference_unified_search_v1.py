from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAMERA = ROOT / "macrobot_pick_pipeline" / "camera_authoritative_task_node.py"
RESILIENT = ROOT / "macrobot_pick_pipeline" / "resilient_object_task_node.py"
CONFIG = ROOT / "config" / "stored_object_pick.yaml"


def test_place_reference_search_uses_camera_authoritative_pipeline():
    source = CAMERA.read_text(encoding="utf-8")
    assert "PLACE_REFERENCE_UNIFIED_SEARCH_V1" in source
    assert "place_reference_search_unified" in source
    assert "same_camera_authoritative_search_and_alignment" in source
    assert "held_object_changes_search_policy=False" in source
    assert "place_specific_behavior_starts_after_alignment=True" in source


def test_place_lost_reacquisition_preserves_continuous_finder():
    source = CAMERA.read_text(encoding="utf-8")
    assert "def _restart_full_search(self, reason: str) -> None:" in source
    assert "place_reference_keep_finder_on_lost" in source
    assert "place_reference_reacquire_started" in source
    assert "self._start_resilient_search()" in source
    assert "finder_preserved=" in source


def test_non_place_restart_keeps_original_behavior():
    source = CAMERA.read_text(encoding="utf-8")
    assert "super()._restart_full_search(reason)" in source


def test_existing_general_search_and_alignment_remain_in_resilient_core():
    resilient = RESILIENT.read_text(encoding="utf-8")
    assert "def _start_resilient_search(self) -> None:" in resilient
    assert "def _try_search_or_align(self) -> None:" in resilient
    assert "def _try_alignment_step(self) -> None:" in resilient
    assert "visual_target_lost_restarting_full_search" in resilient


def test_config_enables_continuous_place_reacquisition():
    config = CONFIG.read_text(encoding="utf-8")
    assert "place_reference_keep_finder_on_lost: true" in config


def test_place_side_turn_still_happens_only_after_alignment_if_installed():
    source = CAMERA.read_text(encoding="utf-8")
    if "PLACE_SIDE_TURN_CAMERA_POLICY_V1_1" not in source:
        return
    assert "def _alignment_complete(self) -> None:" in source
    assert "place_side_turn_started" in source
    assert 'self._send_turn(amount, "resilient_place_side_turn")' in source
