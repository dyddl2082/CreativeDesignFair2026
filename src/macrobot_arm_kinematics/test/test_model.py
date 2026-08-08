import math

from macrobot_arm_kinematics.model import (
    JointLimits,
    MacRobotArmModel,
    normalize_angle,
)


def test_forward_inverse_round_trip():
    model = MacRobotArmModel()
    cases = [
        (0.0, 0.0, 0.0),
        (0.2, -0.1, 0.3),
        (-0.3, 0.2, 1.0),
        (0.4, 0.1, 1.4),
    ]
    for q1, q2, q3 in cases:
        pose = model.forward(q1, q2, q3)
        solutions = model.inverse(
            pose.x,
            pose.z,
            seed=(q1, q2),
            gripper_q=q3,
        )
        assert solutions
        best = solutions[0]
        assert abs(normalize_angle(best.q1 - q1)) < 1e-8
        assert abs(normalize_angle(best.q2 - q2)) < 1e-8
        assert best.position_error < 1e-9


def test_corrected_full_visual_mapping():
    q1 = 0.15
    q2 = 0.10
    q3 = 0.40
    mapped = MacRobotArmModel.full_visual_joint_positions(q1, q2, q3)

    # Left servo CCW and right servo CW for positive logical motion.
    assert abs(mapped['lift_servo'] - 2.0 * q1) < 1e-12
    assert abs(mapped['tilt_servo'] + 2.0 * (q1 + q2)) < 1e-12

    # Driven arm gears and passive joints preserve the linkage.
    assert abs(mapped['lift_ratio'] - q1) < 1e-12
    assert abs(mapped['tilt_ratio'] - (q1 + q2)) < 1e-12
    assert abs(mapped['rear_passive'] - q2) < 1e-12
    assert abs(mapped['top_passive'] - q2) < 1e-12

    # Positive q3 closes. The servo joint has -Z axis, hence negative coordinate.
    assert abs(mapped['gripper_servo'] + 2.0 * q3) < 1e-12
    assert abs(mapped['gripper_left_gear'] + q3) < 1e-12
    assert abs(mapped['gripper_right_gear'] - q3) < 1e-12


def test_gripper_positive_closes_and_reaches_180_servo_degrees():
    limits = JointLimits()
    assert limits.contains(0.0, 0.0, 0.0)
    assert limits.contains(0.0, 0.0, math.pi / 2.0)
    assert not limits.contains(0.0, 0.0, -0.01)
    assert not limits.contains(0.0, 0.0, math.pi / 2.0 + 0.01)


def test_four_bar_toggle_guard():
    limits = JointLimits(four_bar_margin=math.radians(10.0))
    assert limits.contains(0.0, 0.0, 0.0)
    assert not limits.contains(0.0, math.radians(89.0), 0.0)
    assert not limits.contains(0.0, math.radians(-89.0), 0.0)
