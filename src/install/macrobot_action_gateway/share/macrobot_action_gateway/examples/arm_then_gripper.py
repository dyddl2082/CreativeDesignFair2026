def main() -> TaskOutcome:
    arm = robot.SET_ARM_JOINTS(
        arm_lift_deg=10.0,
        wrist_pitch_deg=-5.0,
    )
    arm_result = robot.WAIT_ACTION(arm, timeout_s=20.0)
    if arm_result.state != ActionState.SUCCEEDED:
        return TaskOutcome(
            TaskStatus.FAILED,
            arm_result.error_message or "팔 이동에 실패했습니다.",
        )

    gripper = robot.SET_GRIPPER(gripper_deg=30.0)
    gripper_result = robot.WAIT_ACTION(gripper, timeout_s=12.0)
    if gripper_result.state != ActionState.SUCCEEDED:
        return TaskOutcome(
            TaskStatus.PARTIALLY_SUCCEEDED,
            gripper_result.error_message or "팔은 이동했지만 그리퍼 동작에 실패했습니다.",
        )

    return TaskOutcome(TaskStatus.SUCCEEDED, "팔과 그리퍼 동작을 완료했습니다.")
