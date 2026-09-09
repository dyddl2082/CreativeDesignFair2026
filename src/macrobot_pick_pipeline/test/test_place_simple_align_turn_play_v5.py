import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAMERA = ROOT / "macrobot_pick_pipeline" / "camera_authoritative_task_node.py"
CONFIG = ROOT / "config" / "stored_object_pick.yaml"
MARKER = "PLACE_SIMPLE_ALIGN_TURN_PLAY_V5"


def _source_and_class():
    source = CAMERA.read_text(encoding="utf-8")
    tree = ast.parse(source)
    classes = [
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef)
        and node.name == "CameraAuthoritativeTaskNode"
    ]
    assert len(classes) == 1
    return source, classes[0]


def _last_method_line(cls, name):
    methods = [
        node
        for node in cls.body
        if isinstance(node, ast.FunctionDef) and node.name == name
    ]
    assert methods, name
    return methods[-1].lineno


def test_v5_methods_are_effective_after_legacy_blocks():
    source, cls = _source_and_class()
    marker_line = source[: source.rfind(MARKER)].count("\n") + 1
    assert _last_method_line(cls, "_declare_parameters") > marker_line
    assert "_declare_parameters_before_place_simple_v5" in [
        node.name
        for node in cls.body
        if isinstance(node, ast.FunctionDef)
    ]
    for name in (
        "_start_place_goal",
        "_mark_identity_confirmed",
        "_try_search_or_align",
        "_try_alignment_step",
        "_fail",
        "_restart_full_search",
        "_alignment_complete",
        "_send_turn",
        "_after_camera_motion",
    ):
        assert _last_method_line(cls, name) > marker_line, name


def test_reference_uses_normal_resilient_search_and_alignment():
    source, _ = _source_and_class()
    block = source.split(MARKER, 1)[1]
    assert "ResilientObjectTaskNode._start_place_goal(self, request)" in block
    assert "ResilientObjectTaskNode._mark_identity_confirmed(self, source)" in block
    assert "ResilientObjectTaskNode._try_search_or_align(self)" in block
    assert "ResilientObjectTaskNode._try_alignment_step(self)" in block
    assert "place_specific_identity_debounce=False" in block
    assert "place_specific_reacquire=False" in block


def test_one_15_degree_turn_then_immediate_place():
    source, _ = _source_and_class()
    block = source.split(MARKER, 1)[1]
    assert '"resilient_place_final_turn_v5"' in block
    assert 'chunks=1' in block
    assert 'correction_after_turn=False' in block
    assert 'perception_after_turn="not_used"' in block
    assert 'self._start_place_preflight()' in block


def test_place_uses_held_taught_reachable_point():
    source, _ = _source_and_class()
    block = source.split(MARKER, 1)[1]
    assert "held_runtime.alignment.reference_point_base" in block
    assert "legacy_cartesian_offset_used=False" in block


def test_turn_sign_is_delegated_to_existing_boundary():
    source, _ = _source_and_class()
    block = source.split(MARKER, 1)[1]
    assert "ResilientObjectTaskNode._send_turn(self, bounded, purpose)" in block
    assert 'command = f"TURN_DEG' not in block
    assert "pico_turn_positive_is_right =" not in block


def test_parameters_are_declared_by_effective_camera_class():
    source, _ = _source_and_class()
    block = source.split(MARKER, 1)[1]
    assert "def _declare_parameters(self) -> None:" in block
    assert "self._declare_parameters_before_place_simple_v5()" in block
    assert '"simple_place_final_turn_deg": 15.0' in block
    assert '"simple_place_final_turn_max_abs_deg": 30.0' in block


def test_config_has_v5_turn_and_disables_old_side_turn_flags():
    config = CONFIG.read_text(encoding="utf-8")
    assert "simple_place_final_turn_deg: 15.0" in config
    assert "simple_place_final_turn_max_abs_deg: 30.0" in config
    if "place_side_turn_enabled:" in config:
        assert "place_side_turn_enabled: false" in config
    if "place_side_turn_deg:" in config:
        assert "place_side_turn_deg: 0.0" in config
    if "place_final_side_turn_deg:" in config:
        assert "place_final_side_turn_deg: 0.0" in config
