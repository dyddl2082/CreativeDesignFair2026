from __future__ import annotations

from pathlib import Path

import yaml


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def test_gateway_uses_latest_visible_test_pick_entry() -> None:
    root = _repo_root()
    source = (
        root
        / "src/macrobot_action_gateway/macrobot_action_gateway/gateway_node.py"
    ).read_text(encoding="utf-8")

    assert '"/macrobot/visible_pick_test/goal"' in source
    assert '"/macrobot/visible_pick_test/cancel"' in source
    assert '"/macrobot/visible_pick_test/status"' in source
    assert '"/macrobot/visible_pick_test/result"' in source
    assert '"request_id": request_id' in source
    assert '"profile": profile' in source
    assert '"execute_pick": execute_pick' in source
    assert '"timeout_sec": timeout_s' in source
    assert '"start_finder": True' in source
    assert '"rebuild_banks": False' in source
    assert (
        'expected = "stored_pick_completed" if execute_pick else '
        '"stored_alignment_completed"'
    ) in source


def test_place_payload_matches_camera_authoritative_place_contract() -> None:
    root = _repo_root()
    gateway = (
        root
        / "src/macrobot_action_gateway/macrobot_action_gateway/gateway_node.py"
    ).read_text(encoding="utf-8")
    resilient = (
        root
        / "src/macrobot_pick_pipeline/macrobot_pick_pipeline/resilient_object_task_node.py"
    ).read_text(encoding="utf-8")
    camera = (
        root
        / "src/macrobot_pick_pipeline/macrobot_pick_pipeline/camera_authoritative_task_node.py"
    ).read_text(encoding="utf-8")

    for marker in (
        '"task": "place"',
        '"reference_object": reference_object_id.value',
        '"held_object": held_object_id.value',
        '"held_runtime_profile": held_runtime_profile',
        '"grasp_keyframe_profile": grasp_keyframe_profile',
        '"placement_offset_base": list(placement_offset_base)',
        '"confirm_held": False',
        '"stored_place_completed"',
    ):
        assert marker in gateway

    for marker in (
        '"action": "preflight_place"',
        '"action": "place"',
        '"stored_place_completed"',
        'self.object_memory.set_empty(source="place_result")',
    ):
        assert marker in resilient

    assert "class CameraAuthoritativeTaskNode(ResilientObjectTaskNode):" in camera


def test_turn_sign_is_counterclockwise_positive_end_to_end() -> None:
    root = _repo_root()
    gateway_source = (
        root
        / "src/macrobot_action_gateway/macrobot_action_gateway/gateway_node.py"
    ).read_text(encoding="utf-8")
    launch_source = (
        root
        / "src/macrobot_action_gateway/launch/action_gateway.launch.py"
    ).read_text(encoding="utf-8")
    pick_cfg = yaml.safe_load(
        (root / "src/macrobot_pick_pipeline/config/stored_object_pick.yaml").read_text(
            encoding="utf-8"
        )
    )
    stored_source = (
        root
        / "src/macrobot_pick_pipeline/macrobot_pick_pipeline/stored_object_pick_node.py"
    ).read_text(encoding="utf-8")

    assert 'self.declare_parameter("pico_turn_positive_is_right", False)' in gateway_source
    assert 'default_value="false"' in launch_source
    assert (
        pick_cfg["macrobot_stored_object_pick"]["ros__parameters"]
        ["pico_turn_positive_is_right"]
        is False
    )
    assert (
        '"pico_turn_positive_is_right": False' in stored_source
        or "'pico_turn_positive_is_right': False" in stored_source
    )
    assert (
        "pico_angle = -angle_deg if self.pico_turn_positive_is_right else angle_deg"
        in gateway_source
    )

    legacy_adapter = (
        "pico_angle = -angle_deg if self.pico_turn_positive_is_right else angle_deg"
        in stored_source
    )
    compact_stored = stored_source.replace(" ", "")
    alignment_core = (
        root
        / "src/macrobot_pick_pipeline/macrobot_pick_pipeline/alignment_core.py"
    ).read_text(encoding="utf-8")
    helper_adapter = (
        "pico_turn_command_deg(" in stored_source
        and "pico_positive_is_right=self.pico_turn_positive_is_right"
        in compact_stored
        and "return-valueifpico_positive_is_rightelsevalue"
        in alignment_core.replace(" ", "")
    )
    assert legacy_adapter or helper_adapter
