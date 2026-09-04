from macrobot_arm_control.servo_mapping import LogicalLimits, ServoAxis, ServoMapping


def _mapping() -> ServoMapping:
    limits = LogicalLimits(-1.0, 1.0, -1.3, 1.3, 0.0, 1.57)
    axis = lambda name, channel: ServoAxis(name, channel, 90.0, 1.0, 1.0, 0.0, 180.0)
    return ServoMapping(limits, axis("lift", 0), axis("wrist", 1), axis("gripper", 2))


def test_wrist_servo_uses_q2_only():
    mapping = _mapping()
    first = mapping.servo_commands_deg(0.5, 0.2, 0.0)["tilt"]
    second = mapping.servo_commands_deg(-0.5, 0.2, 0.0)["tilt"]
    assert first == second


def test_joint_outputs_remain_three_axis():
    commands = _mapping().servo_commands_deg(0.1, -0.2, 0.3)
    assert set(commands) == {"lift", "tilt", "gripper"}
