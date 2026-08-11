# 팀 Robot API와 formal stored-pick node 연결

## 1. 팀이 호출하는 public API

팀원 LLM은 ROS topic을 직접 호출하지 않고 Robot Action Gateway의 다음 함수만 사용한다.

```python
robot.ALIGN_WITH_OBJECT(object_id=ObjectId.BUDS3)
robot.PICK_OBJECT(object_id=ObjectId.BUDS3)
```

Gateway의 기존 topic mapping은 바꾸지 않아도 된다.

```text
Gateway publish:
/macrobot/align_pick/goal

Gateway cancel:
/macrobot/base_alignment/cancel

Gateway observe:
/macrobot/base_alignment/status
/macrobot/base_alignment/result
```

`stored_object_pick_node`가 이 legacy topic을 함께 지원한다.

## 2. `ALIGN_WITH_OBJECT`

Gateway goal의 `execute_pick=false`는 다음을 수행한다.

```text
stored position coarse return
→ finder
→ camera visual alignment
→ 차체 정지
→ alignment_completed
```

팔과 그리퍼 grasp trajectory는 실행하지 않는다.

## 3. `PICK_OBJECT`

Gateway goal의 `execute_pick=true`는 다음을 수행한다.

```text
stored position coarse return
→ finder
→ visual alignment
→ recorded grasp trajectory
→ align_pick_completed
```

팀 문서의 계약처럼 별도 ALIGN을 반드시 선행할 필요는 없다. `PICK_OBJECT`가 내부에서 필요 단계 전체를 수행한다.

## 4. cancel mapping

```text
CANCEL_ACTION / CANCEL_ALL
→ /macrobot/base_alignment/cancel
→ stored node CANCEL_REQUESTED
→ 하위 STOP 확인
→ legacy result ok=false, event=alignment_cancelled
```

Gateway는 해당 result를 public `ActionState.CANCELED`로 매핑한다.

## 5. team-owned schema boundary

팀원 담당:

```text
ObjectId와 alias
최종 물체 저장 구조체
public 함수 인자 제약
LLM code generation / validation / approval
```

로봇 runtime 담당:

```text
현재 internal profile adapter
Pico odom query
finder goal
search state machine
visual alignment
recorded grasp playback
cancel propagation
```

최종 object structure가 확정되면 runtime adapter에서 다음 값을 제공하면 된다.

```text
object_name
search pose 또는 search location
camera-relative graspable reference
recorded grasp profile/trajectory ID
```
