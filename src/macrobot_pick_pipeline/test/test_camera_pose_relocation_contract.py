from pathlib import Path


PACKAGE = Path(__file__).resolve().parents[1]
NODE = PACKAGE / "macrobot_pick_pipeline" / "camera_authoritative_task_node.py"
MODULE = PACKAGE / "macrobot_pick_pipeline" / "camera_pose_relocation.py"


def test_camera_task_contains_two_stage_pose_relocation_contract():
    source = NODE.read_text(encoding="utf-8")
    for token in (
        "camera_reset_pose_relocation_v1",
        "plan_viewpoint_relocation",
        "plan_range_relocation",
        "pose_relocation_maneuver_started",
        "pose_relocation_maneuver_completed",
        "single_fresh_camera_comparison",
        "DRIVE_REL",
        "drive_relative_result",
    ):
        assert token in source


def test_camera_observation_is_not_requested_between_compound_primitives():
    source = NODE.read_text(encoding="utf-8")
    assert "camera_observation_between_primitives=False" in source
    assert "if self.pose_relocation_queue:" in source
    assert "self._dispatch_pose_relocation_primitive()" in source


def test_planner_keeps_camera_as_state_authority():
    source = MODULE.read_text(encoding="utf-8")
    assert "After the whole manoeuvre finishes" in source
    assert "plan_viewpoint_relocation" in source
    assert "plan_range_relocation" in source
    assert "DRIVE_REL" in source
    assert "TURN -> MOVE -> TURN" in source
