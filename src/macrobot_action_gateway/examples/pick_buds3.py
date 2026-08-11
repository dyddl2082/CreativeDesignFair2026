def main() -> TaskOutcome:
    pick = robot.PICK_OBJECT(object_id=ObjectId.BUDS3)
    result = robot.WAIT_ACTION(pick, timeout_s=150.0)
    if result.state != ActionState.SUCCEEDED:
        return TaskOutcome(
            status=TaskStatus.FAILED,
            message=result.error_message or "Buds3 파지에 실패했습니다.",
        )
    return TaskOutcome(
        status=TaskStatus.SUCCEEDED,
        message="Buds3 파지 절차를 완료했습니다.",
    )
