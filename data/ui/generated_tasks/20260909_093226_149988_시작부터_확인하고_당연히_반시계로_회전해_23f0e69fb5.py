def main() -> TaskOutcome:
    for angle_index in range(7):
        object_state = robot.GET_OBJECT_STATE(
            object_id=ObjectId.RUBBER,
        )

        if object_state.state == ObjectState.VISIBLE:
            pick_action = robot.PICK_OBJECT(
                object_id=ObjectId.RUBBER,
            )
            pick_result = robot.WAIT_ACTION(
                pick_action,
                timeout_s=2410.0,
            )

            if pick_result.state != ActionState.SUCCEEDED:
                return TaskOutcome(
                    status=TaskStatus.PARTIALLY_SUCCEEDED,
                    message=pick_result.error_message or "고무를 찾았지만 집지 못했습니다.",
                    data={"checked_angle_deg": angle_index * 60},
                )

            return TaskOutcome(
                status=TaskStatus.SUCCEEDED,
                message="고무를 찾아 집었습니다.",
                data={"found_angle_deg": angle_index * 60},
            )

        if object_state.state != ObjectState.NOT_VISIBLE:
            if angle_index == 0:
                return TaskOutcome(
                    status=TaskStatus.FAILED,
                    message=object_state.error_message or "현재 방향에서 고무의 가시 상태를 확인할 수 없습니다.",
                )

            return TaskOutcome(
                status=TaskStatus.PARTIALLY_SUCCEEDED,
                message=object_state.error_message or "회전 탐색 중 고무의 가시 상태를 확인할 수 없습니다.",
                data={"completed_turns": angle_index},
            )

        if angle_index < 6:
            turn_action = robot.TURN_BASE(
                angle_deg=60.0,
            )
            turn_result = robot.WAIT_ACTION(
                turn_action,
                timeout_s=20.0,
            )

            if turn_result.state != ActionState.SUCCEEDED:
                return TaskOutcome(
                    status=TaskStatus.PARTIALLY_SUCCEEDED,
                    message=turn_result.error_message or "고무 탐색 중 반시계 방향 회전에 실패했습니다.",
                    data={"completed_turns": angle_index},
                )

    return TaskOutcome(
        status=TaskStatus.FAILED,
        message="반시계 방향으로 한 바퀴 돌며 확인했지만 고무를 찾지 못했습니다.",
        data={"completed_turns": 6},
    )
