def main() -> TaskOutcome:
    pick_action = robot.PICK_OBJECT(
        object_id=ObjectId.RUBBER,
    )
    pick_result = robot.WAIT_ACTION(
        pick_action,
        timeout_s=2410.0,
    )

    if pick_result.state != ActionState.SUCCEEDED:
        return TaskOutcome(
            status=TaskStatus.FAILED,
            message=pick_result.error_message or "고무를 집지 못했습니다.",
        )

    return TaskOutcome(
        status=TaskStatus.SUCCEEDED,
        message="고무 파지 동작을 완료했습니다.",
    )
