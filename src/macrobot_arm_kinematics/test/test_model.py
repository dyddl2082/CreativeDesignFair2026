import math

from macrobot_arm_kinematics.model import JointLimits, MacRobotArmModel, normalize_angle


def test_zero_pose():
    model = MacRobotArmModel()
    pose = model.forward(0.0, 0.0, 0.0)
    assert abs(pose.x - (-0.163806)) < 1e-9
    assert abs(pose.y - 0.064500) < 1e-9
    assert abs(pose.z - 0.158595) < 1e-9
    assert abs(pose.pitch) < 1e-9


def test_round_trip_with_general_tool_offset():
    model = MacRobotArmModel()
    for q1, q2, q3 in [
        (0.0, 0.0, 0.0),
        (0.25, -0.20, -0.30),
        (-0.35, 0.45, -0.55),
        (0.70, -0.55, -0.80),
    ]:
        target = model.forward(q1, q2, q3)
        solutions = model.inverse(target.x, target.z, seed=(q1, q2), gripper_q=q3)
        assert solutions
        best = solutions[0]
        pose = model.forward(best.q1, best.q2, q3)
        assert math.hypot(pose.x - target.x, pose.z - target.z) < 1e-8


def test_unreachable():
    model = MacRobotArmModel()
    assert model.inverse(1.0, 1.0) == []


def test_arm_parallelogram_mapping():
    for q1, q2 in [(0.0, 0.0), (0.2, -0.3), (-0.4, 0.5), (0.8, -0.6)]:
        mapped = MacRobotArmModel.full_visual_joint_positions(q1, q2)
        front_long = mapped['lift_ratio']
        bottom_short = -mapped['tilt_ratio']  # ratio_right axis is -Y
        rear_long = bottom_short + mapped['rear_passive']
        top_short = rear_long - mapped['top_passive']  # top joint axis is -Y
        assert abs(normalize_angle(rear_long - front_long)) < 1e-10
        assert abs(normalize_angle(top_short - bottom_short)) < 1e-10


def test_four_bar_toggle_guard():
    limits = JointLimits(four_bar_margin=math.radians(10.0))
    assert limits.contains(0.0, 0.0, 0.0)
    assert not limits.contains(0.0, math.radians(89.0), 0.0)
    assert not limits.contains(0.0, math.radians(-89.0), 0.0)


def test_gripper_mapping_and_gap():
    model = MacRobotArmModel()
    q3 = -0.6
    mapped = model.full_visual_joint_positions(0.0, 0.0, q3)
    assert mapped['gripper_servo'] == 2.0 * q3
    assert mapped['gripper_right_gear'] == -q3
    assert mapped['gripper_left_addition'] == q3
    assert mapped['gripper_right_addition'] == -q3
    assert mapped['gripper_left_clamp'] == -q3
    assert mapped['gripper_right_clamp'] == q3
    assert model.gripper_gap(-0.8) < model.gripper_gap(0.0)
