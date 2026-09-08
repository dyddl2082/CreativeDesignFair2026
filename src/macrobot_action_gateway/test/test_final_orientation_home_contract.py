from pathlib import Path

from macrobot_action_gateway.ast_validator import validate_source
from macrobot_action_gateway.gateway_runtime import ASYNC_FUNCTIONS
from macrobot_action_gateway.robot_facade import RobotFacade


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def test_arm_home_is_public_and_facade_exposes_it():
    assert "ARM_HOME" in ASYNC_FUNCTIONS
    assert callable(getattr(RobotFacade, "ARM_HOME", None))


def test_ast_validator_accepts_arm_home_program():
    source = """
def main() -> TaskOutcome:
    action = robot.ARM_HOME()
    result = robot.WAIT_ACTION(action, timeout_s=25.0)
    if result.state != ActionState.SUCCEEDED:
        return TaskOutcome(TaskStatus.FAILED, result.error_message or "home failed")
    return TaskOutcome(TaskStatus.SUCCEEDED, "home")
"""
    _, report = validate_source(source)
    assert report.valid, report.summary()


def test_orientation_angular_tolerance_is_twenty_and_quality_is_preserved():
    text = (_repo_root() / "src/macrobot_pick_pipeline/config/stored_object_pick.yaml").read_text(encoding="utf-8")
    for key in (
        "camera_record_min_orientation_quality",
        "orientation_auto_reference_quality",
        "record_grasp_min_orientation_quality",
        "precision_orientation_min_quality",
    ):
        assert f"{key}: 0.45" in text
    assert "orientation_tolerance_deg: 20.0" in text
    assert "precision_orientation_tolerance_deg: 20.0" in text


def test_place_requires_post_home_and_keeps_held_empty_on_home_failure():
    text = (_repo_root() / "src/macrobot_action_gateway/macrobot_action_gateway/gateway_runtime.py").read_text(encoding="utf-8")
    assert "final-orientation-home-v1: post-place ARM_HOME" in text
    assert "POST_PLACE_HOME_FAILED" in text
    assert text.index("self.state.set_held_object(None, known=True)") < text.index("POST_PLACE_HOME_FAILED")


def test_llm_bundle_knows_arm_home():
    text = (_repo_root() / "src/macrobot_ui/knowledge/llm_bundle.yaml").read_text(encoding="utf-8")
    assert "  ARM_HOME:\n    block: arm_gripper\n" in text
    assert "로봇팔 HOME으로" in text
    assert "arm_home_after_successful_release_and_retreat" in text
