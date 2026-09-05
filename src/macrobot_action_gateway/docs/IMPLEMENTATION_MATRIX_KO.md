# API v0.2 구현 정합성 표

| 공개 함수 | 현재 구현 | 하위 연결 | 비고 |
|---|---|---|---|
| `WAIT_SECOND` | 구현 | Gateway interruptible wait | plain sleep 미노출 |
| `WAIT_ACTION` | 구현 | action registry | timeout 시 cancel 요청 |
| `WAIT_RESOURCE` | 구현 | resource condition | 예약하지 않음 |
| `CHECK_ACTION` | 구현 | action snapshot | synthetic failure 지원 |
| `CANCEL_ACTION` | 구현 | cancel event + 하위 stop | bounded 확인 |
| `CANCEL_ALL` | 구현 | 현재 run action만 | STOP과 구분 |
| `STOP` | 구현 | Pico `STOP` + arm `/stop` + align cancel | 같은 run 후속 motion 금지 |
| `GET_OBJECT_STATE` | 구현 | `/object_finder/result`, `/object_finder/status` | snapshot, 탐색 시작 안 함 |
| `GET_ROBOT_POS` | 구현 | command history + logical joint state | 실제 encoder arm 측정 아님 |
| `MOVE_BASE` | 구현 | `MOVE_CM` | positive=forward |
| `TURN_BASE` | 구현 | `TURN_DEG` sign adapter | public positive=CCW/left |
| `SAVE_POS` | 구현 | in-memory session registry | command-history pose |
| `MOVE_BASE_TO_POS` | 구현 | turn→move→turn | obstacle avoidance 없음 |
| `ALIGN_WITH_OBJECT` | 구현 | `/macrobot/align_pick/goal`, `execute_pick=false` | 기존 visual alignment 사용 |
| `SET_ARM_JOINTS` | 구현 | `/macrobot/arm/joint_goal` | 현재 gripper 보존 |
| `SET_GRIPPER` | 구현 | `/macrobot/arm/joint_goal` | 현재 arm q1/q2 보존 |
| `SAVE_ARM_PRIMITIVE` | 구현 | Gateway session registry | arm 2축만 저장 |
| `SET_ARM_PRIMITIVE` | 구현 | validator→servo bridge | 현재 gripper 보존 |
| `PICK_OBJECT` | 구현 | align-and-pick stack | 필요 시 내부 ALIGN |
| `PLACE_NEXTTO_OBJECT` | 구현 | resilient stored-object PLACE runtime | 기준 물체 재탐색 후 역파지 4단계 |

## 사양과 현재 프로젝트의 핵심 mismatch 해결

### 1. 세 관절 명령 하위 bridge

하위 servo bridge는 q1/q2/q3 전체 goal을 요구한다. Gateway가 다음을 원자적으로 구성한다.

```text
SET_ARM_JOINTS(q1,q2)
→ 현재 q3 읽기
→ [q1,q2,current_q3] publish

SET_GRIPPER(q3)
→ 현재 q1,q2 읽기
→ [current_q1,current_q2,q3] publish
```

### 2. primitive

기존 일부 recorder는 q1/q2/q3를 모두 저장하지만 LLM API session primitive는 q1/q2만 별도 registry에 저장한다. 기존 commissioning 파일을 자동 변환하지 않는다.

### 3. 상태 표현

팔과 그리퍼 성공은 commanded logical trajectory 완료를 뜻한다. 실제 encoder 도달이나 실제 파지를 과장하지 않는다.

### 4. PICK

Gateway의 `PICK_OBJECT`는 `/macrobot/align_pick/goal`에 `execute_pick=true`를 보내므로 외부 생성 코드가 ALIGN을 중복 호출할 필요가 없다.
