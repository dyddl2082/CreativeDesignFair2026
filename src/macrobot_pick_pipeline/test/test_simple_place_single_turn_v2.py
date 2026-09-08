import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAMERA = ROOT / "macrobot_pick_pipeline" / "camera_authoritative_task_node.py"


def _camera_class():
    tree = ast.parse(CAMERA.read_text(encoding="utf-8"))
    classes = [
        node for node in tree.body
        if isinstance(node, ast.ClassDef)
        and node.name == "CameraAuthoritativeTaskNode"
    ]
    assert len(classes) == 1
    return classes[0]


def test_simple_place_override_is_unique_effective_alignment_method():
    cls = _camera_class()
    methods = [
        node.name for node in cls.body
        if isinstance(node, ast.FunctionDef)
    ]
    assert "_alignment_complete_before_simple_place_v2" in methods
    assert methods[-2:].count("_alignment_complete") <= 1
    assert methods[-1] == "_after_camera_motion" or "_alignment_complete" in methods[-3:]


def test_simple_place_override_is_unique_effective_after_motion_method():
    cls = _camera_class()
    methods = [
        node.name for node in cls.body
        if isinstance(node, ast.FunctionDef)
    ]
    assert "_after_camera_motion_before_simple_place_v2" in methods
    assert methods[-1] == "_after_camera_motion"


def test_single_turn_goes_directly_to_preflight():
    source = CAMERA.read_text(encoding="utf-8")
    assert "SIMPLE_PLACE_SINGLE_TURN_V2" in source
    assert "chunks=1" in source
    assert "recenter_after_turn=False" in source
    assert "super(CameraAuthoritativeTaskNode, self)._send_turn(" in source
    assert '"resilient_place_side_turn_simple"' in source
    assert '"place_side_turn_completed"' in source
    assert "self._start_place_preflight()" in source


def test_placement_uses_held_taught_reachable_point():
    source = CAMERA.read_text(encoding="utf-8")
    assert "held_runtime.alignment.reference_point_base" in source
    assert "legacy_offset_used=False" in source
    assert (
        'placement_policy="single_side_turn_then_held_taught_reachable_point"'
        in source
    )


def test_turn_sign_contract_is_not_reimplemented():
    source = CAMERA.read_text(encoding="utf-8")
    block = source.split("SIMPLE_PLACE_SINGLE_TURN_V2", 1)[1]
    assert 'command = f"TURN_DEG' not in block
    assert "pico_turn_positive_is_right =" not in block
