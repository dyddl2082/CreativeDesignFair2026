def main() -> TaskOutcome:
    action = robot.SET_ARM_JOINTS(
        arm_lift_deg=0.0,
        wrist_pitch_deg=0.0,
    )
    result = robot.WAIT_ACTION(
        action,
        timeout_s=25.0,
    )
    if result.state != ActionState.SUCCEEDED:
        return TaskOutcome(
            status=TaskStatus.FAILED,
            message=result.error_message or "로봇팔 HOME 이동에 실패했습니다.",
        )
    return TaskOutcome(
        status=TaskStatus.SUCCEEDED,
        message="로봇팔을 HOME 위치로 이동했습니다.",
    )
