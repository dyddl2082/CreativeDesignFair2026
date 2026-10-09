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

    turn_action = robot.TURN_BASE(
        angle_deg=-90.0,
    )
    turn_result = robot.WAIT_ACTION(
        turn_action,
        timeout_s=20.0,
    )

    if turn_result.state != ActionState.SUCCEEDED:
        return TaskOutcome(
            status=TaskStatus.PARTIALLY_SUCCEEDED,
            message=turn_result.error_message or "고무는 집었지만 오른쪽으로 90도 회전하지 못했습니다.",
        )

    return TaskOutcome(
        status=TaskStatus.SUCCEEDED,
        message="고무를 집고 오른쪽으로 90도 회전했습니다.",
    )
