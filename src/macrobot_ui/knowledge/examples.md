# MacRobot Custom GPT 코드 생성 예제

이 파일은 `llm_bundle.yaml`을 사용하는 Custom GPT가 따라야 할 대표 응답 패턴을 보여준다. 예제의 자연어 표현을 그대로 암기하기보다 다음 원칙을 일반화한다.

- 모든 실행 코드는 `def main() -> TaskOutcome:`으로 시작한다.
- 비동기 구동함수의 반환값은 `ActionHandle` 변수에 저장한다.
- 다음 단계가 완료 여부에 의존하면 `WAIT_ACTION`으로 terminal 상태를 확인한다.
- 성공은 오직 `result.state == ActionState.SUCCEEDED`로 판단한다.
- 일반적인 이동·조작 액션은 `SUCCEEDED`가 아닌 모든 terminal 결과를 하나의 실패로 처리한다. `CANCELED`와 `TIMED_OUT`를 별도로 분기하지 않는다.
- 사용자가 명시적으로 취소 또는 정지를 요청한 예제에서만 `TaskStatus.CANCELED`를 사용한다.
- `PICK_OBJECT`와 `PLACE_NEXTTO_OBJECT`는 필요한 `ALIGN`을 내부에서 수행한다.
- raw 물체 문자열 대신 `ObjectId` enum을 사용한다.
- 실패 후 자동 재시도는 사용자가 명시했을 때만 작성한다.
- 아래 `python` 코드 블록은 유효한 예제이고, `python-invalid` 블록은 생성하면 안 되는 패턴이다.

---

## 1. 단일 차체 이동

### 사용자

> 앞으로 20cm 이동해.

### 응답

STATUS: CODE

OBJECT_BINDINGS:
- 없음

ASSUMPTIONS:
- 없음

CODE:

```python
def main() -> TaskOutcome:
    move_action = robot.MOVE_BASE(distance_m=0.20)
    move_result = robot.WAIT_ACTION(
        move_action,
        timeout_s=25.0,
    )

    if move_result.state != ActionState.SUCCEEDED:
        return TaskOutcome(
            status=TaskStatus.FAILED,
            message=move_result.error_message or "이동에 실패했습니다.",
        )

    return TaskOutcome(
        status=TaskStatus.SUCCEEDED,
        message="앞으로 20cm 이동했습니다.",
    )
```

---

## 2. 순차 이동과 회전

### 사용자

> 앞으로 20cm 간 다음 왼쪽으로 30도 돌아.

### 응답

STATUS: CODE

OBJECT_BINDINGS:
- 없음

ASSUMPTIONS:
- 없음

CODE:

```python
def main() -> TaskOutcome:
    move_action = robot.MOVE_BASE(distance_m=0.20)
    move_result = robot.WAIT_ACTION(
        move_action,
        timeout_s=25.0,
    )

    if move_result.state != ActionState.SUCCEEDED:
        return TaskOutcome(
            status=TaskStatus.FAILED,
            message=move_result.error_message or "첫 번째 이동에 실패했습니다.",
        )

    turn_action = robot.TURN_BASE(angle_deg=30.0)
    turn_result = robot.WAIT_ACTION(
        turn_action,
        timeout_s=25.0,
    )

    if turn_result.state != ActionState.SUCCEEDED:
        return TaskOutcome(
            status=TaskStatus.PARTIALLY_SUCCEEDED,
            message=turn_result.error_message or "이동은 완료했지만 회전에 실패했습니다.",
        )

    return TaskOutcome(
        status=TaskStatus.SUCCEEDED,
        message="앞으로 20cm 이동한 뒤 왼쪽으로 30도 회전했습니다.",
    )
```

---

## 3. per-call 제한을 만족하기 위한 명시적 이동 분할

### 사용자

> 앞으로 60cm 이동해.

### 응답

STATUS: CODE

OBJECT_BINDINGS:
- 없음

ASSUMPTIONS:
- 30cm씩 두 번의 연속 이동으로 분할합니다.

CODE:

```python
def main() -> TaskOutcome:
    for step_index in range(2):
        move_action = robot.MOVE_BASE(distance_m=0.30)
        move_result = robot.WAIT_ACTION(
            move_action,
            timeout_s=25.0,
        )

        if move_result.state != ActionState.SUCCEEDED:
            if step_index == 0:
                return TaskOutcome(
                    status=TaskStatus.FAILED,
                    message=move_result.error_message or "60cm 이동을 시작하지 못했습니다.",
                    data={"completed_steps": 0},
                )

            return TaskOutcome(
                status=TaskStatus.PARTIALLY_SUCCEEDED,
                message=move_result.error_message or "60cm 중 일부만 이동했습니다.",
                data={"completed_steps": step_index},
            )

    return TaskOutcome(
        status=TaskStatus.SUCCEEDED,
        message="앞으로 60cm 이동했습니다.",
    )
```

---

## 4. 물체 정렬만 수행

### 사용자

> 버즈를 잡을 수 있는 범위로 정렬해.

### 응답

STATUS: CODE

OBJECT_BINDINGS:
- 버즈 -> ObjectId.BUDS3

ASSUMPTIONS:
- 없음

CODE:

```python
def main() -> TaskOutcome:
    align_action = robot.ALIGN_WITH_OBJECT(
        object_id=ObjectId.BUDS3,
    )
    align_result = robot.WAIT_ACTION(
        align_action,
        timeout_s=50.0,
    )

    if align_result.state == ActionState.SUCCEEDED:
        return TaskOutcome(
            status=TaskStatus.SUCCEEDED,
            message="버즈를 향해 회전하고 파지 가능한 범위로 거리 정렬을 완료했습니다.",
        )

    return TaskOutcome(
        status=TaskStatus.FAILED,
        message=align_result.error_message or "버즈 정렬에 실패했습니다.",
    )
```

---

## 5. 일반적인 물체 파지

### 사용자

> 버즈를 집어 줘.

### 응답

STATUS: CODE

OBJECT_BINDINGS:
- 버즈 -> ObjectId.BUDS3

ASSUMPTIONS:
- 없음

CODE:

```python
def main() -> TaskOutcome:
    pick_action = robot.PICK_OBJECT(
        object_id=ObjectId.BUDS3,
    )
    pick_result = robot.WAIT_ACTION(
        pick_action,
        timeout_s=70.0,
    )

    if pick_result.state != ActionState.SUCCEEDED:
        return TaskOutcome(
            status=TaskStatus.FAILED,
            message=pick_result.error_message or "버즈를 집지 못했습니다.",
        )

    return TaskOutcome(
        status=TaskStatus.SUCCEEDED,
        message="버즈 파지 동작을 완료했습니다.",
    )
```

`PICK_OBJECT`가 물체 확인, 필요한 내부 정렬, 거리 조정, 파지와 검증을 포함하므로 별도의 `ALIGN_WITH_OBJECT`를 앞에 추가하지 않는다.

---

## 6. 물체가 보일 때만 파지

### 사용자

> 버즈가 지금 보이면 집고, 안 보이면 아무것도 하지 마.

### 응답

STATUS: CODE

OBJECT_BINDINGS:
- 버즈 -> ObjectId.BUDS3

ASSUMPTIONS:
- 없음

CODE:

```python
def main() -> TaskOutcome:
    object_state = robot.GET_OBJECT_STATE(
        object_id=ObjectId.BUDS3,
    )

    if object_state.state != ObjectState.VISIBLE:
        return TaskOutcome(
            status=TaskStatus.FAILED,
            message=object_state.error_message or "버즈가 현재 보이지 않아 파지를 시작하지 않았습니다.",
        )

    pick_action = robot.PICK_OBJECT(
        object_id=ObjectId.BUDS3,
    )
    pick_result = robot.WAIT_ACTION(
        pick_action,
        timeout_s=70.0,
    )

    if pick_result.state == ActionState.SUCCEEDED:
        return TaskOutcome(
            status=TaskStatus.SUCCEEDED,
            message="보이는 버즈를 집었습니다.",
        )

    return TaskOutcome(
        status=TaskStatus.FAILED,
        message=pick_result.error_message or "버즈 파지에 실패했습니다.",
    )
```

이 조건문은 사용자가 명시적으로 “보이면”이라고 요청했기 때문에 `GET_OBJECT_STATE`를 사용한다. 일반적인 “버즈를 집어 줘”에는 `PICK_OBJECT`만 사용한다.

---

## 7. 사용자가 명시한 조건부 재시도

### 사용자

> 버즈를 집어 보고 실패하면 한 번만 다시 시도해.

### 응답

STATUS: CODE

OBJECT_BINDINGS:
- 버즈 -> ObjectId.BUDS3

ASSUMPTIONS:
- 최초 시도와 추가 1회를 합쳐 최대 두 번 시도합니다.

CODE:

```python
def main() -> TaskOutcome:
    for attempt_index in range(2):
        pick_action = robot.PICK_OBJECT(
            object_id=ObjectId.BUDS3,
        )
        pick_result = robot.WAIT_ACTION(
            pick_action,
            timeout_s=70.0,
        )

        if pick_result.state == ActionState.SUCCEEDED:
            return TaskOutcome(
                status=TaskStatus.SUCCEEDED,
                message="버즈 파지에 성공했습니다.",
                data={"attempt_number": attempt_index + 1},
            )

    return TaskOutcome(
        status=TaskStatus.FAILED,
        message=pick_result.error_message or "두 번의 버즈 파지 시도가 모두 실패했습니다.",
    )
```

자동 재시도는 이처럼 사용자가 명시했을 때만 생성한다.

---

## 8. 위치 저장 후 복귀

### 사용자

> 현재 위치를 start_point로 저장하고, 앞으로 20cm 이동했다가 다시 돌아와.

### 응답

STATUS: CODE

OBJECT_BINDINGS:
- 없음

ASSUMPTIONS:
- `start_point`는 현재 세션에서 새로 저장할 위치 ID입니다.

CODE:

```python
def main() -> TaskOutcome:
    save_result = robot.SAVE_POS(
        position_id="start_point",
        overwrite=False,
    )

    if not save_result.success:
        return TaskOutcome(
            status=TaskStatus.FAILED,
            message=save_result.error_message or "현재 위치 저장에 실패했습니다.",
        )

    move_action = robot.MOVE_BASE(distance_m=0.20)
    move_result = robot.WAIT_ACTION(
        move_action,
        timeout_s=25.0,
    )

    if move_result.state != ActionState.SUCCEEDED:
        return TaskOutcome(
            status=TaskStatus.PARTIALLY_SUCCEEDED,
            message=move_result.error_message or "위치는 저장했지만 이동에 실패했습니다.",
        )

    return_action = robot.MOVE_BASE_TO_POS(
        position_id="start_point",
    )
    return_result = robot.WAIT_ACTION(
        return_action,
        timeout_s=50.0,
    )

    if return_result.state != ActionState.SUCCEEDED:
        return TaskOutcome(
            status=TaskStatus.PARTIALLY_SUCCEEDED,
            message=return_result.error_message or "이동은 했지만 저장 위치 복귀에 실패했습니다.",
        )

    return TaskOutcome(
        status=TaskStatus.SUCCEEDED,
        message="이동 후 저장한 위치와 방향으로 복귀했습니다.",
    )
```

---

## 9. 팔 관절과 그리퍼를 순차 제어

### 사용자

> 팔 리프트를 20도, 손목을 -15도로 움직인 다음 그리퍼를 완전히 열어.

### 응답

STATUS: CODE

OBJECT_BINDINGS:
- 없음

ASSUMPTIONS:
- “완전히 열어”는 개발 설정의 열린 기준값인 0도로 해석합니다.

CODE:

```python
def main() -> TaskOutcome:
    arm_action = robot.SET_ARM_JOINTS(
        arm_lift_deg=20.0,
        wrist_pitch_deg=-15.0,
    )
    arm_result = robot.WAIT_ACTION(
        arm_action,
        timeout_s=20.0,
    )

    if arm_result.state != ActionState.SUCCEEDED:
        return TaskOutcome(
            status=TaskStatus.FAILED,
            message=arm_result.error_message or "팔 관절 이동에 실패했습니다.",
        )

    gripper_action = robot.SET_GRIPPER(
        gripper_deg=0.0,
    )
    gripper_result = robot.WAIT_ACTION(
        gripper_action,
        timeout_s=12.0,
    )

    if gripper_result.state == ActionState.SUCCEEDED:
        return TaskOutcome(
            status=TaskStatus.SUCCEEDED,
            message="팔을 지정 각도로 이동하고 그리퍼를 열었습니다.",
        )

    return TaskOutcome(
        status=TaskStatus.PARTIALLY_SUCCEEDED,
        message=gripper_result.error_message or "팔 이동은 완료했지만 그리퍼 열기에 실패했습니다.",
    )
```

`SET_GRIPPER` 성공은 물체 파지 성공을 의미하지 않는다.

---

## 10. 팔 primitive 저장과 복원

### 사용자

> 현재 팔 자세를 inspect_pose로 저장하고, 팔을 0도 0도로 움직였다가 inspect_pose로 되돌려.

### 응답

STATUS: CODE

OBJECT_BINDINGS:
- 없음

ASSUMPTIONS:
- `inspect_pose`는 현재 세션에서 새로 저장할 팔 primitive ID입니다.

CODE:

```python
def main() -> TaskOutcome:
    save_result = robot.SAVE_ARM_PRIMITIVE(
        primitive_id="inspect_pose",
        overwrite=False,
    )

    if not save_result.success:
        return TaskOutcome(
            status=TaskStatus.FAILED,
            message=save_result.error_message or "현재 팔 자세 저장에 실패했습니다.",
        )

    neutral_action = robot.SET_ARM_JOINTS(
        arm_lift_deg=0.0,
        wrist_pitch_deg=0.0,
    )
    neutral_result = robot.WAIT_ACTION(
        neutral_action,
        timeout_s=20.0,
    )

    if neutral_result.state != ActionState.SUCCEEDED:
        return TaskOutcome(
            status=TaskStatus.PARTIALLY_SUCCEEDED,
            message=neutral_result.error_message or "팔 자세는 저장했지만 중립 자세 이동에 실패했습니다.",
        )

    restore_action = robot.SET_ARM_PRIMITIVE(
        primitive_id="inspect_pose",
    )
    restore_result = robot.WAIT_ACTION(
        restore_action,
        timeout_s=20.0,
    )

    if restore_result.state == ActionState.SUCCEEDED:
        return TaskOutcome(
            status=TaskStatus.SUCCEEDED,
            message="저장한 팔 자세로 복귀했습니다.",
        )

    return TaskOutcome(
        status=TaskStatus.PARTIALLY_SUCCEEDED,
        message=restore_result.error_message or "중립 자세 이동은 완료했지만 저장 자세 복귀에 실패했습니다.",
    )
```

`SAVE_ARM_PRIMITIVE`는 그리퍼 각도를 저장하지 않으며, `SET_ARM_PRIMITIVE`도 현재 그리퍼 명령을 유지한다.

---

## 11. 현재 들고 있는 물체를 기준 물체 옆에 놓기

### 사용자

> 지금 들고 있는 물체를 버즈 옆에 놓아 줘.

### 응답

STATUS: CODE

OBJECT_BINDINGS:
- 버즈 -> ObjectId.BUDS3

ASSUMPTIONS:
- 배치할 물체는 Gateway가 현재 보유 중이라고 기록한 물체입니다.

CODE:

```python
def main() -> TaskOutcome:
    place_action = robot.PLACE_NEXTTO_OBJECT(
        reference_object_id=ObjectId.BUDS3,
    )
    place_result = robot.WAIT_ACTION(
        place_action,
        timeout_s=70.0,
    )

    if place_result.state == ActionState.SUCCEEDED:
        return TaskOutcome(
            status=TaskStatus.SUCCEEDED,
            message="현재 들고 있던 물체를 버즈 옆에 놓았습니다.",
        )

    return TaskOutcome(
        status=TaskStatus.FAILED,
        message=place_result.error_message or "버즈 옆 배치에 실패했습니다.",
    )
```

`PLACE_NEXTTO_OBJECT`가 기준 물체 확인, 필요한 정렬, 배치 위치 선택과 release를 내부에서 수행하므로 별도의 `ALIGN_WITH_OBJECT`를 추가하지 않는다.

---

## 12. 로봇 추정 상태 조회

### 사용자

> 로봇이 추정한 현재 위치와 팔, 그리퍼 각도를 알려 줘.

### 응답

STATUS: CODE

OBJECT_BINDINGS:
- 없음

ASSUMPTIONS:
- 반환값은 실제 센서 측정이 아니라 명령 이력 또는 commanded state 기반 추정값입니다.

CODE:

```python
def main() -> TaskOutcome:
    position = robot.GET_ROBOT_POS()

    if position.snapshot_state == RobotSnapshotState.UNAVAILABLE:
        return TaskOutcome(
            status=TaskStatus.FAILED,
            message=position.error_message or "로봇 추정 상태를 조회할 수 없습니다.",
        )

    if position.base_state != EstimateState.VALID:
        return TaskOutcome(
            status=TaskStatus.FAILED,
            message="차체 추정 위치를 신뢰할 수 없습니다.",
        )

    if position.arm_state != EstimateState.VALID:
        return TaskOutcome(
            status=TaskStatus.FAILED,
            message="팔의 commanded state를 신뢰할 수 없습니다.",
        )

    if position.gripper_state != EstimateState.VALID:
        return TaskOutcome(
            status=TaskStatus.FAILED,
            message="그리퍼의 commanded state를 신뢰할 수 없습니다.",
        )

    return TaskOutcome(
        status=TaskStatus.SUCCEEDED,
        message="로봇의 추정 상태를 조회했습니다.",
        data={
            "x_m": position.x_m,
            "y_m": position.y_m,
            "yaw_deg": position.yaw_deg,
            "arm_lift_deg": position.arm_lift_deg,
            "wrist_pitch_deg": position.wrist_pitch_deg,
            "gripper_deg": position.gripper_deg,
        },
    )
```

---

## 13. 자원 대기 후 동작 시작

### 사용자

> 차체 자원이 빌 때까지 최대 10초 기다렸다가 앞으로 10cm 이동해.

### 응답

STATUS: CODE

OBJECT_BINDINGS:
- 없음

ASSUMPTIONS:
- 없음

CODE:

```python
def main() -> TaskOutcome:
    wait_result = robot.WAIT_RESOURCE(
        resource_id=ResourceId.BASE_MOTION,
        timeout_s=10.0,
    )

    if not wait_result.success:
        return TaskOutcome(
            status=TaskStatus.FAILED,
            message=wait_result.error_message or "차체 자원이 비기를 기다리지 못했습니다.",
        )

    move_action = robot.MOVE_BASE(distance_m=0.10)
    move_result = robot.WAIT_ACTION(
        move_action,
        timeout_s=25.0,
    )

    if move_result.state == ActionState.SUCCEEDED:
        return TaskOutcome(
            status=TaskStatus.SUCCEEDED,
            message="차체 자원이 빈 것을 확인한 뒤 앞으로 10cm 이동했습니다.",
        )

    return TaskOutcome(
        status=TaskStatus.FAILED,
        message=move_result.error_message or "자원 대기 후 이동을 시작하지 못했습니다.",
    )
```

`WAIT_RESOURCE`는 자원을 예약하지 않으므로 `MOVE_BASE`가 경합으로 `RESOURCE_BUSY`를 반환할 가능성은 여전히 있다.

---

## 14. 일정 시간 후 액션 상태를 한 번 확인하고 취소

### 사용자

> 오른쪽으로 180도 회전을 시작하고 2초 뒤에도 실행 중이면 취소해.

### 응답

STATUS: CODE

OBJECT_BINDINGS:
- 없음

ASSUMPTIONS:
- 없음

CODE:

```python
def main() -> TaskOutcome:
    turn_action = robot.TURN_BASE(angle_deg=-180.0)

    wait_result = robot.WAIT_SECOND(seconds=2.0)
    if not wait_result.success:
        cancel_result = robot.CANCEL_ACTION(turn_action)
        return TaskOutcome(
            status=TaskStatus.CANCELED,
            message=cancel_result.error_message or wait_result.error_message or "대기 중 회전 액션을 취소했습니다.",
        )

    turn_state = robot.CHECK_ACTION(turn_action)

    if turn_state.state == ActionState.SUCCEEDED:
        return TaskOutcome(
            status=TaskStatus.SUCCEEDED,
            message="2초 안에 회전을 완료했습니다.",
        )

    if turn_state.state in (
        ActionState.PENDING,
        ActionState.RUNNING,
        ActionState.CANCEL_REQUESTED,
    ):
        cancel_result = robot.CANCEL_ACTION(turn_action)

        if cancel_result.state == ActionState.CANCELED:
            return TaskOutcome(
                status=TaskStatus.CANCELED,
                message="2초 후에도 실행 중이어서 회전을 취소했습니다.",
            )

        if cancel_result.state == ActionState.SUCCEEDED:
            return TaskOutcome(
                status=TaskStatus.SUCCEEDED,
                message="취소 요청 전에 회전이 완료되었습니다.",
            )

        return TaskOutcome(
            status=TaskStatus.FAILED,
            message=cancel_result.error_message or "회전 취소에 실패했습니다.",
        )

    return TaskOutcome(
        status=TaskStatus.FAILED,
        message=turn_state.error_message or "회전 액션이 실패했습니다.",
    )
```

이 예제는 사용자가 특정 시점의 상태 확인과 취소를 명시했기 때문에 `WAIT_SECOND`와 `CHECK_ACTION`을 사용한다. 반복 polling은 만들지 않는다.

---

## 15. 현재 run 액션 전체 취소

### 사용자

> 이 코드에서 실행 중인 액션을 모두 취소해.

### 응답

STATUS: CODE

OBJECT_BINDINGS:
- 없음

ASSUMPTIONS:
- 없음

CODE:

```python
def main() -> TaskOutcome:
    cancel_result = robot.CANCEL_ALL()

    if cancel_result.success:
        return TaskOutcome(
            status=TaskStatus.CANCELED,
            message="현재 실행 코드가 소유한 활성 액션을 모두 취소했습니다.",
        )

    return TaskOutcome(
        status=TaskStatus.FAILED,
        message=cancel_result.error_message or "현재 run의 액션 전체 취소에 실패했습니다.",
    )
```

---

## 16. 시스템 motion 정지

### 사용자

> 로봇의 모든 움직임을 멈춰.

### 응답

STATUS: CODE

OBJECT_BINDINGS:
- 없음

ASSUMPTIONS:
- 없음

CODE:

```python
def main() -> TaskOutcome:
    stop_result = robot.STOP()

    if stop_result.success:
        return TaskOutcome(
            status=TaskStatus.CANCELED,
            message="로봇의 시스템 motion을 정지했습니다.",
        )

    return TaskOutcome(
        status=TaskStatus.FAILED,
        message=stop_result.error_message or "시스템 motion 정지를 확인하지 못했습니다.",
    )
```

`STOP` 성공 후 같은 run에서 새로운 motion을 시작하지 않는다.

---

# 코드 대신 질문하거나 지원 불가로 응답하는 예제

## 17. 물체 지시어가 모호함

### 사용자

> 그거 집어 줘.

### 응답

STATUS: NEED_CLARIFICATION

QUESTION: 어떤 등록 물체를 집을까요? 현재 등록된 물체 중에서는 갤럭시 버즈3를 지정할 수 있습니다.

---

## 18. 이동 거리가 없음

### 사용자

> 앞으로 조금 가.

### 응답

STATUS: NEED_CLARIFICATION

QUESTION: 앞으로 몇 cm 이동할까요?

---

## 19. 낮은 수준 팔 각도가 없음

### 사용자

> 팔을 조금 올려.

### 응답

STATUS: NEED_CLARIFICATION

QUESTION: `arm_lift_deg`와 `wrist_pitch_deg`를 각각 몇 도로 설정할까요?

---

## 20. 등록되지 않은 물체

### 사용자

> 빨간 컵을 집어 줘.

### 응답

STATUS: UNSUPPORTED

REASON: 현재 ObjectId 카탈로그에는 빨간 컵이 등록되어 있지 않아 유효한 `PICK_OBJECT` 코드를 생성할 수 없습니다.

---

## 21. 공개 API에 없는 능력

### 사용자

> 계단을 올라가서 2층으로 가.

### 응답

STATUS: UNSUPPORTED

REASON: 현재 공개 Robot API에는 계단 이동이나 층간 내비게이션 기능이 없습니다.

---

# 생성하면 안 되는 코드 패턴

## A. 직접 import와 sleep

```python-invalid
import time

def main() -> TaskOutcome:
    time.sleep(3.0)
    return TaskOutcome(
        status=TaskStatus.SUCCEEDED,
        message="기다렸습니다.",
    )
```

문제:
- `import`가 금지되어 있다.
- 직접 `time.sleep()` 대신 `robot.WAIT_SECOND()`를 사용해야 한다.

---

## B. raw 물체 문자열 사용

```python-invalid
def main() -> TaskOutcome:
    pick_action = robot.PICK_OBJECT(object_id="버즈")
    pick_result = robot.WAIT_ACTION(pick_action, timeout_s=70.0)
    return TaskOutcome(
        status=TaskStatus.SUCCEEDED,
        message="완료했습니다.",
    )
```

문제:
- `object_id`에는 `ObjectId.BUDS3` 같은 canonical enum만 사용할 수 있다.
- 실제 `pick_result.state`를 확인하지 않고 성공을 선언했다.

---

## C. 비동기 완료 확인 누락

```python-invalid
def main() -> TaskOutcome:
    robot.MOVE_BASE(distance_m=0.20)
    return TaskOutcome(
        status=TaskStatus.SUCCEEDED,
        message="이동했습니다.",
    )
```

문제:
- 비동기 반환값을 `ActionHandle` 변수에 저장하지 않았다.
- terminal 상태를 확인하지 않았다.

---

## D. PICK 앞의 불필요한 ALIGN 중복

```python-invalid
def main() -> TaskOutcome:
    align_action = robot.ALIGN_WITH_OBJECT(object_id=ObjectId.BUDS3)
    align_result = robot.WAIT_ACTION(align_action, timeout_s=50.0)

    pick_action = robot.PICK_OBJECT(object_id=ObjectId.BUDS3)
    pick_result = robot.WAIT_ACTION(pick_action, timeout_s=70.0)

    return TaskOutcome(
        status=TaskStatus.SUCCEEDED,
        message="버즈를 집었습니다.",
    )
```

문제:
- 일반적인 파지 요청에서 `PICK_OBJECT`는 필요한 ALIGN을 내부에서 수행한다.
- 두 결과의 성공 여부를 확인하지 않았다.
- 사용자가 정렬을 독립적인 단계로 명시하지 않았다.

---

## E. busy polling

```python-invalid
def main() -> TaskOutcome:
    move_action = robot.MOVE_BASE(distance_m=0.20)

    while robot.CHECK_ACTION(move_action).state == ActionState.RUNNING:
        pass

    return TaskOutcome(
        status=TaskStatus.SUCCEEDED,
        message="완료했습니다.",
    )
```

문제:
- 무제한 while과 busy polling이 금지되어 있다.
- 완료 대기에는 `WAIT_ACTION`을 사용해야 한다.

---

## F. STOP 이후 새 motion 시작

```python-invalid
def main() -> TaskOutcome:
    stop_result = robot.STOP()
    move_action = robot.MOVE_BASE(distance_m=0.10)
    move_result = robot.WAIT_ACTION(move_action, timeout_s=25.0)
    return TaskOutcome(
        status=TaskStatus.SUCCEEDED,
        message="정지한 뒤 이동했습니다.",
    )
```

문제:
- `STOP` 성공 후 같은 run에서는 새로운 motion을 시작할 수 없다.
- `STOP` 결과도 확인하지 않았다.

---

## G. GET_ROBOT_POS의 추정값을 실제 측정값으로 단정

```python-invalid
def main() -> TaskOutcome:
    position = robot.GET_ROBOT_POS()
    return TaskOutcome(
        status=TaskStatus.SUCCEEDED,
        message=f"실제 위치는 {position.x_m}, {position.y_m}입니다.",
    )
```

문제:
- 관련 `EstimateState`를 확인하지 않았다.
- 반환값은 실제 센서 측정값이 아니라 추정값 또는 commanded state일 수 있다.

---

## H. 사용자 요청에 없는 자동 재시도

```python-invalid
def main() -> TaskOutcome:
    for attempt_index in range(3):
        pick_action = robot.PICK_OBJECT(object_id=ObjectId.BUDS3)
        pick_result = robot.WAIT_ACTION(pick_action, timeout_s=70.0)
        if pick_result.state == ActionState.SUCCEEDED:
            return TaskOutcome(
                status=TaskStatus.SUCCEEDED,
                message="버즈를 집었습니다.",
            )

    return TaskOutcome(
        status=TaskStatus.FAILED,
        message="버즈를 집지 못했습니다.",
    )
```

문제:
- 사용자가 재시도를 요청하지 않았는데 임의로 세 번 시도했다.

---

# 검토 체크리스트

Custom GPT가 생성한 예제를 검토할 때 다음을 확인한다.

1. 응답 첫 줄이 `STATUS: ...` 형식인가?
2. `CODE`일 때 `OBJECT_BINDINGS`, `ASSUMPTIONS`, `CODE`가 모두 있는가?
3. `def main() -> TaskOutcome:`이 정확히 하나인가?
4. 모든 로봇 호출이 `robot.<공개 함수>` 형태인가?
5. 비동기 함수의 handle을 저장했는가?
6. 의존하는 다음 단계 전에 `WAIT_ACTION`으로 성공을 확인했는가?
7. `ObjectId` canonical enum을 사용했는가?
8. `PICK_OBJECT`나 `PLACE_NEXTTO_OBJECT` 앞에 불필요한 ALIGN을 중복하지 않았는가?
9. 사용자가 요청하지 않은 재시도나 추가 동작이 없는가?
10. `STOP` 뒤에 motion이 없는가?
11. 거리, 각도, 시간과 관절값이 현재 개발 제한 안에 있는가?
12. 부분 성공과 전체 성공을 구분했는가?
13. 결과를 확인하지 않고 성공했다고 말하지 않는가?
14. import, try-except, direct sleep, busy polling, dunder 접근이 없는가?
15. 실제 센서 측정이 아닌 값을 실제 물리 상태라고 과장하지 않는가?
