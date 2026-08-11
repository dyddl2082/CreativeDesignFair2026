# Pico 및 composite pick 취소 계약

## 1. 결론

Pico의 모든 문자열 명령이 같은 방식으로 취소되는 것은 아니다. 공개 Robot API에서 요구하는 취소 가능성은 **raw serial 명령 전체**가 아니라 **비동기 motion action**에 적용해야 한다.

| Pico 명령 종류 | Pico 내부 취소 | 상위 액션 처리 |
|---|---|---|
| `MOVE_CM`, `TURN_DEG`, `MOVE_TICKS`, `DRIVE_REL` | 실행 루프에서 `STOP`/`ESTOP` polling | `STOP` 후 최종 `status=stopped` 응답을 확인하고 `CANCELED` |
| `MOTOR` | `STOP`으로 중단 | 실제 이동량 불확실 가능; odom `unreliable` |
| `ARM_US`, `SERVO_US`, `ARM_DEG`, `SERVO_DEG` | 이미 기록된 pulse write 자체는 되돌릴 수 없음 | servo bridge의 후속 trajectory sample을 중단하고 현재 pulse hold |
| `ARM_OFF`, `SERVO_OFF` | 취소 개념 부적합 | 토크 해제 명령이며 일반 cancel로 사용 금지 |
| 상태·설정 명령 | 매우 짧은 동기 명령 | cancel 대상 아님 |

## 2. 차체 cancel

현재 Pico closed-loop motion은 blocking loop 안에서도 serial을 확인한다.

```text
MOVE_CM 또는 TURN_DEG 실행
→ STOP 수신
→ 모터 PWM 0
→ move/turn 결과 status=stopped
→ left_count/right_count/odom 반환
```

정식 node는 `STOP`을 보낸 직후 취소 완료라고 하지 않는다.

```text
RUNNING
→ CANCEL_REQUESTED
→ STOP
→ move_cm_result 또는 turn_deg_result status=stopped 확인
→ CANCELED
```

부분 이동 후 `odom.reliable=false`이면 그대로 결과에 기록한다.

## 3. 팔·그리퍼 cancel

Pico의 `ARM_US`는 PCA9685 register write 한 번이므로 그 write를 취소할 수 없다. 실제 async arm action은 Raspberry Pi의 servo bridge가 여러 logical trajectory sample을 보낸다.

```text
/macrobot/arm/stop
→ servo bridge interpolation 중단
→ 현재 logical command hold
→ trajectory_stopped
```

그리퍼를 자동 open하지 않는다. 물체를 들고 있을 수 있기 때문이다.

## 4. raw protocol의 제한

현재 Pico serial protocol에는 `command_id`가 없다. 따라서 selective cancel은 불가능하고 active base motion 하나에 대한 `STOP`만 가능하다.

이 제한은 다음 조건에서 허용 가능하다.

```text
- Gateway가 PICO_MOTION을 exclusive resource로 관리
- 동시에 둘 이상의 base/arm raw publisher를 실행하지 않음
- formal stored pick node가 한 번에 goal 하나만 허용
```

추후 raw protocol을 확장한다면 다음 형식을 권장한다.

```text
MOVE_CM <command_id> <cm> ...
CANCEL <command_id>
```

현재 단계에서는 필요하지 않다. Robot Action Gateway의 action ID와 single-owner resource lock이 public cancel 의미를 제공한다.

## 5. composite action cancel 결과

`stored_object_pick_node`는 다음 하위 동작을 모두 중단한다.

```text
finder cancel
Pico STOP
arm demo stop
/macrobot/arm/stop
pick coordinator cancel
```

정지 확인이 되면:

```json
{
  "action_state": "CANCELED",
  "error_code": "RUN_CANCELED",
  "partial_state": {
    "last_odom": {},
    "last_object_point_base": [],
    "current_q": [],
    "last_base_response": {}
  }
}
```

정지 확인 timeout이면 `CANCELED`가 아니라:

```text
FAILED / SAFE_STOP_UNCONFIRMED
```

으로 종료한다.
