def main() -> TaskOutcome:
    move_action = robot.MOVE_BASE(
        distance_m=0.10,
    )
    move_result = robot.WAIT_ACTION(
        move_action,
        timeout_s=20.0,
    )

    if move_result.state != ActionState.SUCCEEDED:
        return TaskOutcome(
            status=TaskStatus.FAILED,
            message=move_result.error_message or "앞으로 10cm 이동하지 못했습니다.",
        )

    return TaskOutcome(
        status=TaskStatus.SUCCEEDED,
        message="앞으로 10cm 이동했습니다.",
    )
