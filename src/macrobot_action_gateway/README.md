# macrobot_action_gateway 0.2.0

LLM이 만든 제한 Python과 실제 ROS 2 하드웨어 사이의 실행 경계다. 이번 버전은 시각 재탐색 기반 PICK과 안전한 PLACE runtime을 연결한다.

## 공개 manipulation API

```text
ALIGN_WITH_OBJECT(ObjectId)
PICK_OBJECT(ObjectId)
PLACE_NEXTTO_OBJECT(reference_object_id=ObjectId)
```

`PLACE_NEXTTO_OBJECT`는 더 이상 미구현 safe-fail이 아니다. Gateway가 `/macrobot/stored_pick/goal`에 상관관계 ID가 포함된 PLACE goal을 보내고, `/macrobot/stored_pick/result`의 동일 ID 결과만 기다린다.

```text
reference object 시각 재탐색
→ 기준 물체 옆 배치점 생성
→ semantic reverse-pick preflight
→ PLACE_ABOVE / DESCEND / RELEASE / RETREAT
```

기본 배치 offset은 `config/gateway.yaml`에 있고, 물체별 값은 `config/object_catalog.yaml`에서 덮어쓸 수 있다.

## 실행

```bash
ros2 launch macrobot_action_gateway action_gateway.launch.py \
  real_motion_enabled:=false
```

하위 파이프라인의 dry-run을 확인한 뒤에만 실제 motion을 허용한다.

```bash
ros2 launch macrobot_action_gateway action_gateway.launch.py \
  real_motion_enabled:=true
```

## LLM 프로그램 예제

```bash
SHARE="$(ros2 pkg prefix --share macrobot_action_gateway)"

ros2 run macrobot_action_gateway robot_code_runner \
  --code "$SHARE/examples/pick_and_place_nextto.py" \
  --validate-only
```

실행 시에는 기존과 같이 사용자 승인 플래그가 필요하다.

```bash
ros2 run macrobot_action_gateway robot_code_runner \
  --code "$SHARE/examples/pick_and_place_nextto.py" \
  --execute --approved
```

## 안전 상태

- PICK 성공 후 Gateway와 object-task node가 모두 보유 물체를 기록한다.
- PLACE 성공 후 보유 상태를 empty로 바꾼다.
- PLACE 도중 실패·timeout이 발생하면 보유 상태를 unknown으로 바꾼다.
- 기준 물체를 찾지 못하거나 전체 배치 경로가 안전하지 않으면 gripper release를 시작하지 않는다.
- 힘 센서가 없으므로 PICK/PLACE 완료는 commanded sequence 완료 기준이다.

## 재부팅 후 보유 상태 동기화

Gateway는 시작 시 그리퍼가 비어 있다고 가정하지 않고 held-object state를 `unknown`으로 둔다. `resilient_object_task_node`가 `/macrobot/stored_pick/status`에 주기적으로 발행하는 heartbeat를 받은 뒤 `empty`, `holding`, `unknown`으로 동기화한다. 상태가 unknown인 동안 `PICK_OBJECT`와 `PLACE_NEXTTO_OBJECT`는 모두 fail-safe로 거부된다.
