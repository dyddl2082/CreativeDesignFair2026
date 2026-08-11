# API 사양 검토 후 결정한 다음 단계

## 결정

`macrobot_llm_robot_api_spec_v0.2.md` 다음 구현 단계는 **LLM prompt 작성이 아니라 Robot Action Gateway MVP 구현**이다.

사양에는 이미 다음이 합의되어 있다.

```text
사용자 자연어
→ 제한된 Python 코드
→ 결정론적 검사와 사용자 승인
→ 격리 Code Worker
→ robot facade
→ Robot Action Gateway
→ ROS 2 / 하드웨어
```

따라서 지금 가장 큰 공백은 `robot.MOVE_BASE(...)`, `robot.PICK_OBJECT(...)` 같은 공개 호출을 실제 프로젝트의 ROS 2 topic과 안전 계층에 연결하는 실행 경계였다.

## 이번 단계에서 구현한 항목

1. 사양의 canonical 함수 20개를 가진 `RobotFacade`
2. 동기 결과와 비동기 `ActionHandle` / `ActionResult`
3. run별 액션 소유권과 취소
4. 원자적인 resource 획득
5. run wall timeout과 internal motion-step budget
6. Unix domain socket 기반 Code Worker↔Gateway IPC
7. 제한 Python AST 검사
8. 별도 process Code Worker와 CPU·메모리·loop 제한
9. 사용자 승인 플래그가 없으면 실행하지 않는 runner
10. 현재 ROS 2 topic으로의 adapter
11. 코드가 active action을 남긴 채 종료되면 자동 취소하는 orphan-action 방어

## 현재 프로젝트에 연결한 함수

| 공개 함수 | 현재 프로젝트 연결 |
|---|---|
| `MOVE_BASE` | `/pico_debug/cmd`의 `MOVE_CM` |
| `TURN_BASE` | `/pico_debug/cmd`의 `TURN_DEG`; 공개 양수 CCW를 현재 Pico 부호로 변환 |
| `STOP` | Pico `STOP` + `/macrobot/arm/stop` + alignment cancel |
| `SET_ARM_JOINTS` | 현재 gripper를 보존하여 `/macrobot/arm/joint_goal` publish |
| `SET_GRIPPER` | 현재 두 arm joint를 보존하여 `/macrobot/arm/joint_goal` publish |
| `SAVE_ARM_PRIMITIVE` | Gateway session registry에 팔 두 관절만 저장 |
| `SET_ARM_PRIMITIVE` | gripper를 유지한 validated logical goal |
| `ALIGN_WITH_OBJECT` | `/macrobot/align_pick/goal`, `execute_pick=false` |
| `PICK_OBJECT` | `/macrobot/align_pick/goal`, `execute_pick=true` |
| `GET_OBJECT_STATE` | `/object_finder/status`와 `/object_finder/result`의 최신 snapshot |
| `GET_ROBOT_POS` | command history + `/macrobot/arm/logical_joint_states` |

## 의도적으로 미완성으로 둔 항목

### `PLACE_NEXTTO_OBJECT`

공개 함수와 오류 계약은 구현했지만 현재 프로젝트에는 다음이 확정되지 않았다.

```text
placement profile schema
안전한 옆 배치 후보 생성
release/post-place sequence
placement verification policy
```

따라서 현재는 `PLACEMENT_PROFILE_NOT_FOUND`로 안전하게 실패한다.

### 실제 파지 검증

현재 `PICK_OBJECT` 성공은 하위 align/pick sequence가 완료되었다는 뜻이다. 힘 센서·전류·그리퍼 encoder가 없으므로 물체가 실제로 유지되고 있다는 강한 보장은 하지 않는다.

### authoritative limit

업로드 사양의 여러 수치가 TBD다. `config/gateway.yaml`의 값은 provisional이며 실제 로봇 시험 후 고정해야 한다.

### 운영 수준 sandbox

현재는 AST 검사, 별도 subprocess, Unix socket 권한, resource limit을 제공한다. 적대적 코드를 실행하는 운영판이라면 별도 Linux 사용자, container, namespace, seccomp/AppArmor 수준의 추가 격리가 필요하다.

## 그다음 개발 순서

1. Gateway dry-run으로 20개 API 계약 확인
2. 작은 단일 motion으로 실제 ROS adapter 확인
3. LLM 팀이 생성한 코드 validator 연결
4. 사용자 승인 UI와 source hash 고정
5. 실제 hardware limit·timeout 확정
6. placement profile/runtime 설계
7. 파지·배치 verification sensor 정책 확정
