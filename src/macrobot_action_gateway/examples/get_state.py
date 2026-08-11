def main() -> TaskOutcome:
    robot_state = robot.GET_ROBOT_POS()
    object_state = robot.GET_OBJECT_STATE(object_id=ObjectId.BUDS3)

    return TaskOutcome(
        TaskStatus.SUCCEEDED,
        "현재 Gateway snapshot을 조회했습니다.",
        data={
            "robot_snapshot_state": str(robot_state.snapshot_state),
            "arm_state": str(robot_state.arm_state),
            "gripper_state": str(robot_state.gripper_state),
            "buds3_state": str(object_state.state),
        },
    )
