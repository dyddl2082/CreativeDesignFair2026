def main() -> TaskOutcome:
    move = robot.MOVE_BASE(distance_m=0.20)
    move_result = robot.WAIT_ACTION(move, timeout_s=10.0)
    if move_result.state != ActionState.SUCCEEDED:
        return TaskOutcome(
            status=TaskStatus.FAILED,
            message=move_result.error_message or "전진에 실패했습니다.",
        )

    turn = robot.TURN_BASE(angle_deg=30.0)
    turn_result = robot.WAIT_ACTION(turn, timeout_s=8.0)
    if turn_result.state != ActionState.SUCCEEDED:
        return TaskOutcome(
            status=TaskStatus.PARTIALLY_SUCCEEDED,
            message=turn_result.error_message or "전진은 완료했지만 회전에 실패했습니다.",
        )

    return TaskOutcome(
        status=TaskStatus.SUCCEEDED,
        message="전진과 좌회전을 완료했습니다.",
    )
