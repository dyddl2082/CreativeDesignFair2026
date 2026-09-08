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
            message=pick_result.error_message or "고무를 잡지 못했습니다.",
        )

    place_action = robot.PLACE_NEXTTO_OBJECT(
        reference_object_id=ObjectId.ERASER,
    )
    place_result = robot.WAIT_ACTION(
        place_action,
        timeout_s=2410.0,
    )

    if place_result.state != ActionState.SUCCEEDED:
        return TaskOutcome(
            status=TaskStatus.PARTIALLY_SUCCEEDED,
            message=place_result.error_message or "고무를 잡았지만 지우개 옆에 놓지 못했습니다.",
        )

    return TaskOutcome(
        status=TaskStatus.SUCCEEDED,
        message="고무를 잡아 지우개 옆에 놓았습니다.",
    )
