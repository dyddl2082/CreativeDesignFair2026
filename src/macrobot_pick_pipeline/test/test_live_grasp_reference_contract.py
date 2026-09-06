from pathlib import Path


def _source(name: str) -> str:
    root = Path(__file__).resolve().parents[1]
    return (root / "macrobot_pick_pipeline" / name).read_text(encoding="utf-8")


def test_record_grasp_defaults_to_live_visual_reference():
    node = _source("stored_object_pick_node.py")
    cli = _source("stored_object_pick_cli.py")
    assert '"record_grasp_live_visual": True' in node
    assert '"record_grasp_live"' in node
    assert "_complete_live_grasp_recording_with_odom" in node
    assert '"use_live_visual": not args.no_live_reference' in cli
    assert '"start_finder": not args.no_live_reference' in cli


def test_precision_runtime_contract_is_present():
    node = _source("resilient_object_task_node.py")
    assert "choose_precision_docking_action" in node
    assert '"precision_stability_count": 4' in node
    assert '"precision_confirmation_count": 3' in node
    assert '"precision_orientation_tolerance_deg": 8.0' in node


def test_close_grasp_orientation_is_authoritative_and_low_quality_record_waits():
    stored = _source("stored_object_pick_node.py")
    resilient = _source("resilient_object_task_node.py")
    assert '"record_grasp_min_orientation_quality": 0.45' in stored
    assert '"record_grasp_waiting_for_reliable_orientation"' in stored
    assert 'close_reference_is_reliable' in resilient
    assert 'self.orientation_reference_source = "stored_alignment_profile"' in resilient


def test_preflight_uses_same_close_orientation_reference_as_docking():
    resilient = _source("resilient_object_task_node.py")
    keyframe = _source("grasp_keyframe_node.py")
    assert 'payload["orientation_reference"] = orientation_reference' in resilient
    assert 'data.get("orientation_reference")' in keyframe
    assert 'orientation_error = axial_orientation_error_deg(\n                current_angle, reference_angle' in keyframe
