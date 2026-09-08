import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAMERA = ROOT / "macrobot_pick_pipeline" / "camera_authoritative_task_node.py"
CONFIG = ROOT / "config" / "stored_object_pick.yaml"


def _class_methods():
    tree = ast.parse(CAMERA.read_text(encoding="utf-8"))
    classes = [
        node for node in tree.body
        if isinstance(node, ast.ClassDef)
        and node.name == "CameraAuthoritativeTaskNode"
    ]
    assert len(classes) == 1
    return [
        node.name for node in classes[0].body
        if isinstance(node, ast.FunctionDef)
    ]


def test_emergency_methods_are_effective_last_definitions():
    methods = _class_methods()
    for name in (
        "_start_place_goal",
        "_mark_identity_confirmed",
        "_try_alignment_step",
        "_alignment_complete",
        "_fail",
        "_restart_full_search",
        "_send_turn",
    ):
        assert name in methods
    assert methods[-1] == "_send_turn"


def test_place_commits_without_post_alignment_base_turn():
    source = CAMERA.read_text(encoding="utf-8")
    block = source.split("PLACE_STOP_SPIN_V3", 1)[1]
    assert 'post_alignment_base_turn_deg=0.0' in block
    assert 'placement_policy="held_taught_reachable_point_no_base_turn"' in block
    assert 'held_runtime.alignment.reference_point_base' in block
    assert 'self._start_place_preflight()' in block
    assert 'super(CameraAuthoritativeTaskNode, self)._send_turn(' not in block
    assert '"resilient_place_side_turn_simple"' not in block


def test_identity_loss_cannot_restart_full_search():
    source = CAMERA.read_text(encoding="utf-8")
    block = source.split("PLACE_STOP_SPIN_V3", 1)[1]
    assert "PLACE_REFERENCE_LOST_AFTER_IDENTITY" in block
    assert "automatic_full_search_disabled=True" in block
    assert 'resume_mode="manual"' in block
    assert 'purpose.startswith("resilient_search")' in block
    assert 'physical_motion="not_commanded"' in block


def test_first_aligned_observation_commits_place():
    source = CAMERA.read_text(encoding="utf-8")
    block = source.split("PLACE_STOP_SPIN_V3", 1)[1]
    assert "self.aligned_confirmations >= 1" in block
    assert '"place_first_alignment_accepted"' in block


def test_search_turn_chunk_is_conservatively_bounded():
    config = CONFIG.read_text(encoding="utf-8")
    assert re.search(
        r"(?m)^\s*camera_search_turn_chunk_deg:\s*4(?:\.0)?\s*$",
        config,
    )
