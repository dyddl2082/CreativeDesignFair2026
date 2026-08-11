from pathlib import Path


def _gateway_source() -> str:
    root = Path(__file__).resolve().parents[1]
    return (root / "macrobot_action_gateway" / "gateway_node.py").read_text(encoding="utf-8")


def test_stored_pick_goal_uses_request_id_and_full_mode():
    text = _gateway_source()
    assert '"request_id": request_id' in text
    assert '"mode": "full"' in text
    assert '"start_finder": True' in text


def test_gateway_waits_for_confirmed_terminal_cancel():
    text = _gateway_source()
    assert "def _wait_align_pick_cancel" in text
    assert 'in {"CANCELED", "TIMED_OUT", "FAILED"}' in text
    assert '"SAFE_STOP_UNCONFIRMED"' in text
    assert 'canceled=True' in text
    assert 'timed_out=True' in text


def test_gateway_default_turn_speed_matches_tracked_base_calibration():
    root = Path(__file__).resolve().parents[1]
    config = (root / "config" / "gateway.yaml").read_text(encoding="utf-8")
    runtime = (root / "macrobot_action_gateway" / "gateway_runtime.py").read_text(encoding="utf-8")
    assert "turn_speed: 150" in config
    assert 'base_motion.turn_speed", 150' in runtime
