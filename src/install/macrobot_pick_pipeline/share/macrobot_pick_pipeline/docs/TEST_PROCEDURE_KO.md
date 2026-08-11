# 실제 시험 절차

## 0. 전제

```text
Pico MOVE_CM / TURN_DEG 보정 완료
회전 PWM 약 150
safe-region 최신
DINOv2 Buds3 threshold 임시 0.45
object finder와 detection localizer 동작
arm demo recorder 동작
```

## 1. 기록된 잡기 동작 만들기

```bash
ros2 run macrobot_pick_pipeline arm_demo_cli
```

메뉴 4에서 실제로:

```text
OPEN
PRE_GRASP
APPROACH
CLOSE
LIFT
```

를 조작해 `Buds3_FIXED_PICK_V1`로 저장한다.

## 2. object profile 기록

차체와 물체를 실제로 잘 잡을 수 있는 위치에 둔다. finder가 Buds3를 continuous tracking하는 상태에서:

```bash
ros2 run macrobot_pick_pipeline stored_object_pick_cli \
  record Buds3 \
  --profile Buds3 \
  --grasp-trajectory Buds3_FIXED_PICK_V1
```

결과 확인:

```bash
cat ~/MacRobot/data/stored_objects/runtime_profiles.yaml
```

## 3. 이미 찾은 상태의 테스트

Buds3가 계속 localized detection으로 나오고 있는 상태에서:

```bash
ros2 run macrobot_pick_pipeline stored_object_pick_cli \
  visible-test Buds3 \
  --profile Buds3 \
  --align-only
```

정렬 성공 후 실제 grasp 포함:

```bash
ros2 run macrobot_pick_pipeline stored_object_pick_cli \
  visible-test Buds3 \
  --profile Buds3
```

## 4. teleop으로 위치 변경

full test를 위해서는 같은 Pico odom session을 유지해야 한다.

- Pico를 reboot하지 않는다.
- `RESET_ODOM`을 하지 않는다.
- teleop은 `step` mode만 사용한다.
- open-loop `MOTOR` mode를 사용하지 않는다.

`pick_pipeline_robot.launch.py`를 종료한 뒤 step teleop으로 이동하고, teleop을 종료한 뒤 pick stack을 다시 시작한다. serial node 두 개를 동시에 실행하지 않는다.

## 5. 정식 find-align-pick

```bash
ros2 run macrobot_pick_pipeline stored_object_pick_cli \
  run Buds3 \
  --profile Buds3 \
  --align-only
```

정렬이 반복적으로 성공하면:

```bash
ros2 run macrobot_pick_pipeline stored_object_pick_cli \
  run Buds3 \
  --profile Buds3
```

## 6. 상태 확인

```bash
ros2 topic echo --field data --full-length /macrobot/stored_pick/status
ros2 topic echo --field data --full-length /macrobot/stored_pick/result
ros2 topic echo --field data --full-length /object_finder/result
ros2 topic echo /macrobot/perception/object_point
ros2 topic echo --field data --full-length /pico_debug/response
ros2 topic echo --field data --full-length /macrobot/arm/servo_bridge/status
```

## 7. 취소 시험

차체 회전 중:

```bash
ros2 topic pub --once \
  /macrobot/stored_pick/cancel \
  std_msgs/msg/String \
  "{data: 'cancel_test'}"
```

확인:

```text
action_state: CANCEL_REQUESTED
Pico response: status=stopped
terminal action_state: CANCELED
partial_state.last_odom 존재
```

팔 trajectory 중에도 같은 cancel을 수행한다.

```text
/macrobot/arm/servo_bridge/status event=trajectory_stopped
terminal action_state=CANCELED
그리퍼 자동 open 없음
```

## 8. Gateway와 직접 CLI를 동시에 사용하지 않기

`stored_object_pick_cli`는 하드웨어 통합 시험용으로 Gateway를 우회한다. LLM/Gateway action이 실행 중일 때 이 CLI나 teleop을 동시에 실행하면 Gateway의 resource lock 밖에서 명령이 들어간다.

```text
직접 시험 시간: Gateway real motion off 또는 종료
LLM 시험 시간: stored_object_pick_cli / teleop / arm_demo jog 종료
```
