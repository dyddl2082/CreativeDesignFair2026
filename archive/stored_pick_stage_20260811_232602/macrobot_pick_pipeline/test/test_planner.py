from pathlib import Path

from macrobot_arm_kinematics.model import MacRobotArmModel
from macrobot_pick_pipeline.planner import build_pick_plan
from macrobot_pick_pipeline.profiles import PickProfileRepository


def test_mock_pick_plan_is_reachable():
    config = Path(__file__).parents[1] / "config" / "pick_profiles.yaml"
    profile = PickProfileRepository(config).get("Buds3")
    model = MacRobotArmModel()
    plan = build_pick_plan(
        model,
        profile,
        "Buds3",
        (-0.150, model.geometry.tool_y, 0.120),
        (0.0, 0.0, 0.0),
    )
    assert [step.name for step in plan.steps] == [
        "OPEN",
        "PRE_GRASP",
        "APPROACH",
        "CLOSE",
        "LIFT",
    ]
    for step in plan.steps:
        assert model.limits.contains(*step.q)

    close = plan.steps[3]
    close_pose = model.forward(*close.q)
    assert abs(close_pose.x - plan.grasp_point_base[0]) < 1e-6
    assert abs(close_pose.z - plan.grasp_point_base[2]) < 1e-6

    lift = plan.steps[4]
    lift_pose = model.forward(*lift.q)
    assert abs(lift_pose.x - plan.lift_point_base[0]) < 1e-6
    assert abs(lift_pose.z - plan.lift_point_base[2]) < 1e-6
