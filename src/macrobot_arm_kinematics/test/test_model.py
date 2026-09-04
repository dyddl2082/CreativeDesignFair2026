import math

from macrobot_arm_kinematics.model import JointLimits, MacRobotArmModel


def test_zero_pose_matches_active_urdf():
    pose = MacRobotArmModel().forward(0.0, 0.0, 0.0)
    expected = (-0.188551055282, 0.0807000018617, 0.226997932739)
    actual = (pose.x, pose.y, pose.z)
    assert max(abs(a - b) for a, b in zip(actual, expected)) < 2e-6


def test_fk_ik_round_trip_serial_2r():
    model = MacRobotArmModel()
    for q1, q2 in ((0.0, 0.0), (0.20, -0.10), (-0.20, 0.15)):
        pose = model.forward(q1, q2, 0.0)
        solutions = model.inverse_xyz(pose.x, pose.y, pose.z, seed=(q1, q2))
        assert solutions
        best = solutions[0]
        reconstructed = model.forward(best.q1, best.q2, 0.0)
        assert math.dist(
            (pose.x, pose.y, pose.z),
            (reconstructed.x, reconstructed.y, reconstructed.z),
        ) < 1e-5


def test_q2_is_independent_and_four_bar_guard_is_removed():
    model = MacRobotArmModel()
    assert model.limits.contains(0.8, -1.0, 0.0)
    mapped_a = model.full_visual_joint_positions(0.25, 0.10, 0.0, 2.0, -2.0, 2.0)
    mapped_b = model.full_visual_joint_positions(-0.25, 0.10, 0.0, 2.0, -2.0, 2.0)
    assert mapped_a["tilt_servo"] == mapped_b["tilt_servo"] == -0.20


def test_joint_limits_are_independent():
    limits = JointLimits()
    assert not limits.contains(limits.arm_lift_max + 0.01, 0.0, 0.0)
    assert not limits.contains(0.0, limits.wrist_pitch_max + 0.01, 0.0)
    assert not limits.contains(0.0, 0.0, limits.gripper_max + 0.01)
