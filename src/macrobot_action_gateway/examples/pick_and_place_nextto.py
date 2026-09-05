def main() -> TaskOutcome:
    pick = robot.PICK_OBJECT(object_id=ObjectId.BUDS3)
    pick_result = robot.WAIT_ACTION(pick, timeout_s=180.0)
    if pick_result.state != ActionState.SUCCEEDED:
        return TaskOutcome(
            status=TaskStatus.FAILED,
            message=pick_result.error_message or "Buds3 파지에 실패했습니다.",
        )

    place = robot.PLACE_NEXTTO_OBJECT(reference_object_id=ObjectId.CUP)
    place_result = robot.WAIT_ACTION(place, timeout_s=180.0)
    if place_result.state != ActionState.SUCCEEDED:
        return TaskOutcome(
            status=TaskStatus.PARTIALLY_SUCCEEDED,
            message=(
                "Buds3는 집었지만 Cup 옆에 놓지 못했습니다. "
                + (place_result.error_message or "배치 실패")
            ),
        )

    return TaskOutcome(
        status=TaskStatus.SUCCEEDED,
        message="Buds3를 찾아 집은 뒤 Cup 옆에 놓았습니다.",
    )
