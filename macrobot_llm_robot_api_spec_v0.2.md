# MacRobot LLM 실행용 Robot API 통합 사양 v0.2

- 문서 상태: 초안 합의본
- 작성 기준일: 2026-08-10
- 대상: 사용자 자연어 명령을 제한된 Python 코드로 생성·검토·승인·실행하는 LLM 기반 로봇 시스템
- 공개 호출 형태: `robot.<FUNCTION_NAME>(...)`
- 생성 코드 진입점: `def main() -> TaskOutcome`
- 통합 범위:
  - 제어 블록 9개 함수
  - 차체 구동 블록 5개 함수
  - 팔·그리퍼 블록 6개 함수
- 통합 원본:
  - `macrobot_base_drive_api_spec_v0.1.md`
  - `macrobot_control_api_spec_v0.1.md`

> **v0.2의 핵심 계약**  
> LLM은 실제 Python 코드를 생성하지만 ROS, 하드웨어 객체, 파일 시스템에는 직접 접근하지 않는다. 생성 코드는 사전에 주입된 `robot` facade와 공통 enum·구조체만 사용하며, 실제 안전성·자원 획득·timeout·취소·하드웨어 통신은 Robot Action Gateway가 강제한다.

---

## 목차

1. [문서 목적과 전체 실행 흐름](#1-문서-목적과-전체-실행-흐름)
2. [전체 API 빠른 참조](#2-전체-api-빠른-참조)
3. [생성 Python 코드 계약](#3-생성-python-코드-계약)
4. [공통 타입](#4-공통-타입)
5. [인지·로봇 추정 상태 타입](#5-인지로봇-추정-상태-타입)
6. [공통 런타임·자원·안전 규칙](#6-공통-런타임자원안전-규칙)
7. [제어 블록](#7-제어-블록)
8. [차체 구동 블록](#8-차체-구동-블록)
9. [팔·그리퍼 블록](#9-팔그리퍼-블록)
10. [공통 오류 코드](#10-공통-오류-코드)
11. [LLM 생성 코드 작성 규칙](#11-llm-생성-코드-작성-규칙)
12. [대표 예제](#12-대표-예제)
13. [기계 판독용 registry 초안](#13-기계-판독용-registry-초안)
14. [설정값과 미확정 항목](#14-설정값과-미확정-항목)
15. [현 프로젝트 코드와의 구현 정합성 메모](#15-현-프로젝트-코드와의-구현-정합성-메모)

---

## 1. 문서 목적과 전체 실행 흐름

이 문서는 LLM이 생성하는 Python 코드가 사용할 수 있는 로봇 API의 공개 계약을 하나로 정의한다. 함수 구현 내부는 블랙박스로 둘 수 있지만, 생성 코드와 Gateway는 이 문서에 정의된 함수명, 인자, 반환형, 상태, 자원, 실패 의미를 동일하게 해석해야 한다.

```text
사용자 자연어 명령
    ↓
LLM: 수행 가능성 판단
    ├─ 모호/지원 불가 → 재질문 또는 불가 응답
    └─ 수행 가능
          ↓
      제한된 Python 코드 생성
          ↓
      결정론적 검사 + LLM 보조 검토
          ↓
      최종 코드 사용자 승인
          ↓
      격리된 Code Worker에서 main() 실행
          ↓
      robot facade
          ↓
      Robot Action Gateway
          ├─ 인자·상태·안전 검사
          ├─ 자원 원자적 획득
          ├─ 내부 동작 횟수 제한
          ├─ ROS/하드웨어 호출
          ├─ 취소·timeout·STOP 처리
          └─ 구조화된 결과·로그 생성
          ↓
      결과 설명 전용 LLM이 사용자에게 실행 결과 보고
```

생성 코드 실행 중 실패하더라도 LLM이 코드를 수정하거나 자동 재계획하지 않는다. 모든 실행 결과는 구조화된 로그로 종료 후 설명 LLM에 전달한다.

---

## 2. 전체 API 빠른 참조

### 2.1 제어 블록

| 함수 | 방식 | 반환 | 핵심 역할 |
|---|---|---|---|
| `WAIT_SECOND` | 동기 | `OperationResult` | interruptible 시간 대기 |
| `WAIT_ACTION` | 동기 | `ActionResult` | 액션 terminal 상태까지 대기; timeout 시 자동 취소 |
| `WAIT_RESOURCE` | 동기 | `OperationResult` | 자원이 idle로 관측될 때까지 대기; 예약은 하지 않음 |
| `CHECK_ACTION` | 동기 | `ActionResult` | 액션 현재 상태 snapshot 조회 |
| `CANCEL_ACTION` | 동기 | `ActionResult` | 현재 run 소유 액션 1개 취소 |
| `CANCEL_ALL` | 동기 | `OperationResult` | 현재 run 소유 활성 액션 전체 취소 |
| `STOP` | 동기 | `OperationResult` | 시스템 전체 motion의 제어된 정지 |
| `GET_OBJECT_STATE` | 동기 | `ObjectStateResult` | 등록 물체 최신 인식 상태 조회 |
| `GET_ROBOT_POS` | 동기 | `RobotPosResult` | 차체 추정 pose와 팔·그리퍼 논리 각도 조회 |

### 2.2 차체 구동 블록

| 함수 | 방식 | 반환 | 핵심 역할 |
|---|---|---|---|
| `MOVE_BASE` | 비동기 | `ActionHandle` | 현재 방향 기준 상대 직선 이동 |
| `TURN_BASE` | 비동기 | `ActionHandle` | 현재 방향 기준 상대 회전 |
| `SAVE_POS` | 동기 | `OperationResult` | 명령 이력 기반 추정 pose를 세션 ID로 저장 |
| `MOVE_BASE_TO_POS` | 비동기 | `ActionHandle` | 저장 pose의 위치와 방향으로 복귀 |
| `ALIGN_WITH_OBJECT` | 비동기 | `ActionHandle` | 물체를 탐색·정렬하고 파지 가능 범위로 거리 보정 |

### 2.3 팔·그리퍼 블록

| 함수 | 방식 | 반환 | 핵심 역할 |
|---|---|---|---|
| `SET_ARM_JOINTS` | 비동기 | `ActionHandle` | 그리퍼를 유지하면서 두 팔 논리 관절을 지정 각도로 이동 |
| `SET_GRIPPER` | 비동기 | `ActionHandle` | 팔 관절을 유지하면서 그리퍼 논리 각도를 지정 |
| `SAVE_ARM_PRIMITIVE` | 동기 | `OperationResult` | 현재 팔 관절값만 primitive로 저장; 그리퍼 제외 |
| `SET_ARM_PRIMITIVE` | 비동기 | `ActionHandle` | 저장된 팔 primitive 실행; 그리퍼 유지 |
| `PICK_OBJECT` | 비동기 | `ActionHandle` | 물체 확인 및 필요 시 내부 ALIGN 후 파지 |
| `PLACE_NEXTTO_OBJECT` | 비동기 | `ActionHandle` | 기준 물체 확인 및 내부 ALIGN 후 현재 보유 물체를 옆에 배치 |

---

## 3. 생성 Python 코드 계약

### 3.1 고정 진입점

생성 코드는 반드시 다음 진입점을 하나만 제공한다.

```python
def main() -> TaskOutcome:
    ...
```

- 모듈 최상위에서 로봇 동작을 시작하지 않는다.
- 실행기는 검증된 모듈에서 `main()`만 호출한다.
- 모든 정상 종료 경로는 `TaskOutcome`을 반환한다.
- 검증 실패 또는 worker 비정상 종료는 실행기에서 별도 실패 결과로 기록한다.

### 3.2 허용 제어 흐름

초기 허용 범위:

```text
변수 대입
if / elif / else
for
정적으로 또는 런타임으로 제한되는 while
break / continue
match / case
return
단순 사용자 정의 함수
허용된 구조체·enum의 읽기 전용 필드 접근
```

초기 금지 범위:

```text
try / except / finally
import
class 정의
lambda
async / await
recursion
global / nonlocal
generator / yield
eval / exec / compile
open / 파일 접근
subprocess / 네트워크 접근
getattr / setattr / delattr
globals / locals / vars
__dict__ / __class__ 등 dunder 접근
ROS 객체, 토픽, 서비스, 액션 클라이언트 직접 접근
```

### 3.3 주입되는 이름

생성 코드에는 import 없이 다음 이름이 사전 주입된다.

```text
robot
TaskStatus
TaskOutcome
ActionState
ActionHandle
ActionResult
OperationResult
ResourceId
ObjectId
ObjectState
ObjectStateResult
EstimateState
StateSource
RobotSnapshotState
RobotPosResult
```

`robot` 이외의 임의 객체에서 메서드를 호출하지 않는다.

### 3.4 전체 임무 결과

```python
from dataclasses import dataclass
from enum import Enum


class TaskStatus(str, Enum):
    SUCCEEDED = "succeeded"
    PARTIALLY_SUCCEEDED = "partially_succeeded"
    FAILED = "failed"
    CANCELED = "canceled"
    TIMED_OUT = "timed_out"


@dataclass(frozen=True)
class TaskOutcome:
    status: TaskStatus
    message: str
    data: dict[str, object] | None = None
```

`TaskOutcome`은 Python 프로그램이 정상적으로 종료되었는지만이 아니라 사용자의 임무가 실제로 어느 정도 수행되었는지를 나타낸다.

---

## 4. 공통 타입

### 4.1 `ActionState`

```python
class ActionState(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    CANCEL_REQUESTED = "cancel_requested"

    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"
    TIMED_OUT = "timed_out"
```

Terminal 상태:

```text
SUCCEEDED
FAILED
CANCELED
TIMED_OUT
```

### 4.2 `ActionHandle`

모든 비동기 구동함수는 호출 즉시 `ActionHandle`을 반환한다.

```python
@dataclass(frozen=True)
class ActionHandle:
    action_id: str
    action_name: str
    run_id: str
```

- `action_id`: 액션 한 건을 식별하는 고유 ID
- `action_name`: `MOVE_BASE`, `PICK_OBJECT` 같은 공개 함수 이름
- `run_id`: 액션을 생성한 승인 코드 실행 ID

사전조건 실패나 자원 충돌로 실제 동작이 시작되지 않아도 handle을 반환하며, 해당 액션 결과는 즉시 `FAILED`가 된다.

### 4.3 `ActionResult`

```python
@dataclass(frozen=True)
class ActionResult:
    action_id: str
    action_name: str
    run_id: str

    state: ActionState
    error_code: str | None
    error_message: str | None

    started_at_unix_ms: int | None
    finished_at_unix_ms: int | None
    duration_ms: int | None
```

시각 필드:

- `started_at_unix_ms`: 액션이 실제로 `RUNNING`에 진입한 Unix epoch millisecond
- `finished_at_unix_ms`: terminal 상태에 도달한 Unix epoch millisecond
- `duration_ms`: monotonic clock으로 계산한 실제 실행 지속 시간

| 상태 | `started_at` | `finished_at` | `duration` |
|---|---:|---:|---:|
| `PENDING` | `None` | `None` | `None` |
| `RUNNING` | 실제 시작 시각 | `None` | `None` |
| 시작 전 `FAILED` | `None` | 실패 시각 | `None` |
| 실행 후 terminal | 실제 시작 시각 | 종료 시각 | 실행 시간 |

함수별 payload는 v0.2에서 정의하지 않는다.

### 4.4 `OperationResult`

동기 함수의 공통 결과이다.

```python
@dataclass(frozen=True)
class OperationResult:
    function_name: str
    run_id: str
    success: bool
    error_code: str | None
    error_message: str | None
    finished_at_unix_ms: int
```

### 4.5 `ResourceId`

```python
class ResourceId(str, Enum):
    BASE_MOTION = "base_motion"
    ARM_MOTION = "arm_motion"
    GRIPPER_MOTION = "gripper_motion"
    PICO_MOTION = "pico_motion"
    POSITION_STORE = "position_store"
    ARM_PRIMITIVE_STORE = "arm_primitive_store"
```

`WAIT_RESOURCE`에서 실제로 기다릴 수 있는지는 registry의 `waitable` 값으로 제한한다.

---

## 5. 인지·로봇 추정 상태 타입

### 5.1 `ObjectState`

```python
class ObjectState(str, Enum):
    VISIBLE = "visible"
    NOT_VISIBLE = "not_visible"
    AMBIGUOUS = "ambiguous"
    STALE = "stale"
    PERCEPTION_UNAVAILABLE = "perception_unavailable"
    UNKNOWN = "unknown"
```

| 상태 | 의미 |
|---|---|
| `VISIBLE` | 최신 유효 인지 결과에서 지정 물체가 확인됨 |
| `NOT_VISIBLE` | 인지 파이프라인은 정상이나 지정 물체가 확인되지 않음 |
| `AMBIGUOUS` | 후보를 하나로 확정할 수 없음 |
| `STALE` | 관련 결과가 freshness 기준보다 오래됨 |
| `PERCEPTION_UNAVAILABLE` | 카메라·인지 파이프라인 정상 상태를 확인할 수 없음 |
| `UNKNOWN` | 내부 상태 조합으로 판단 불가 |

### 5.2 `ObjectStateResult`

```python
@dataclass(frozen=True)
class ObjectStateResult:
    run_id: str
    object_id: ObjectId
    state: ObjectState

    confidence: float | None
    observed_at_unix_ms: int | None
    checked_at_unix_ms: int

    error_code: str | None
    error_message: str | None
```

`NOT_VISIBLE`, `AMBIGUOUS`, `STALE`, `PERCEPTION_UNAVAILABLE`는 Python 예외가 아니라 정상적인 상태 결과이다.

### 5.3 로봇 추정 상태 enum

```python
class EstimateState(str, Enum):
    VALID = "valid"
    TRANSIENT = "transient"
    UNRELIABLE = "unreliable"
    UNAVAILABLE = "unavailable"


class StateSource(str, Enum):
    COMMAND_HISTORY = "command_history"
    COMMANDED_STATE = "commanded_state"
    MEASURED_STATE = "measured_state"


class RobotSnapshotState(str, Enum):
    COMPLETE = "complete"
    PARTIAL = "partial"
    UNAVAILABLE = "unavailable"
```

v0.2 기본 source:

```text
차체: COMMAND_HISTORY
팔: COMMANDED_STATE
그리퍼: COMMANDED_STATE
```

### 5.4 `RobotPosResult`

```python
@dataclass(frozen=True)
class RobotPosResult:
    run_id: str
    snapshot_state: RobotSnapshotState
    captured_at_unix_ms: int

    x_m: float | None
    y_m: float | None
    yaw_deg: float | None
    base_state: EstimateState
    base_source: StateSource
    base_updated_at_unix_ms: int | None

    arm_lift_deg: float | None
    wrist_pitch_deg: float | None
    arm_state: EstimateState
    arm_source: StateSource
    arm_updated_at_unix_ms: int | None

    gripper_deg: float | None
    gripper_state: EstimateState
    gripper_source: StateSource
    gripper_updated_at_unix_ms: int | None

    error_code: str | None
    error_message: str | None
```

현재 논리 관절 매핑:

| 반환 필드 | 논리 관절 |
|---|---|
| `arm_lift_deg` | `arm_lift_joint` |
| `wrist_pitch_deg` | `wrist_pitch_joint` |
| `gripper_deg` | `gripper_joint` |

모든 공개 관절 각도 단위는 degree이다. 현재 팔과 그리퍼 값은 실제 encoder 측정값이 아니라 최신 commanded logical state이다.

---

## 6. 공통 런타임·자원·안전 규칙

### 6.1 자원 원자적 획득

구동함수는 자원 상태 확인과 실제 획득을 Gateway 내부의 하나의 원자적 과정으로 수행한다.

```text
idle 확인 → 나중에 획득     금지
검사 + 획득을 원자적으로   필수
```

자원을 획득하지 못하면 기본적으로 대기열에 넣지 않고 즉시 `RESOURCE_BUSY`로 실패한다. `WAIT_RESOURCE`는 자원을 예약하지 않는다.

### 6.2 자원 의미

| 자원 | 의미 |
|---|---|
| `BASE_MOTION` | 차체 이동·회전 액션 간 배타 실행 |
| `ARM_MOTION` | 팔 두 관절 trajectory 간 배타 실행 |
| `GRIPPER_MOTION` | 그리퍼 trajectory 간 배타 실행 |
| `PICO_MOTION` | 차체·팔·그리퍼가 공유할 수 있는 하드웨어 통신/동작 채널 |
| `POSITION_STORE` | 세션 위치 레지스트리 |
| `ARM_PRIMITIVE_STORE` | 팔 primitive 레지스트리 |

인지 조회는 동기 snapshot이며 별도 공개 자원 태그를 사용하지 않는다.

### 6.3 취소·정지 우선순위

```text
일반 액션 < CANCEL_ACTION < CANCEL_ALL < STOP < 외부 ESTOP/하드웨어 안전계층
```

`CANCEL_ACTION`, `CANCEL_ALL`, `STOP`은 대상 motion 자원이 busy라는 이유로 실행을 거부해서는 안 된다.

### 6.4 내부 동작 카운터

공개 API 호출 횟수는 별도로 제한하지 않고, 실제 하드웨어 하위 동작이 `RUNNING`에 들어갈 때만 내부 동작 카운터를 증가시킨다.

카운트 예:

| 하위 동작 | 증가량 |
|---|---:|
| 직선 이동 1회 | +1 |
| 회전 1회 | +1 |
| 팔 trajectory 1회 | +1 |
| 그리퍼 trajectory 1회 | +1 |
| 인지 snapshot | 0 |
| 위치·primitive 저장 | 0 |
| 취소·STOP 신호 | 0 |

높은 수준 함수 `ALIGN_WITH_OBJECT`, `PICK_OBJECT`, `PLACE_NEXTTO_OBJECT`는 내부에서 실제로 시작한 모든 하위 motion을 각각 집계한다.

### 6.5 전체 run 제한

최소한 다음 제한을 Gateway 또는 supervisor가 강제한다.

```text
전체 run wall-clock timeout
run당 최대 내부 motion step
함수별 1회 호출의 최대 내부 motion step
함수별 hard timeout
worker CPU·메모리·출력 제한
```

### 6.6 추정 상태 신뢰성

- 동작이 시작되기 전에 실패하면 관련 추정 상태는 변경하지 않는다.
- 동작이 성공하면 commanded state 또는 명령 이력을 갱신한다.
- 시작 후 실패·취소·timeout이 발생하고 실제 수행량을 알 수 없으면 해당 상태를 `UNRELIABLE`로 표시한다.
- 움직이는 중에는 `TRANSIENT`를 사용할 수 있다.
- `None` 값을 임의로 `0.0`으로 대체하지 않는다.

### 6.7 코드 worker와 Gateway 분리

생성 코드는 별도 process에서 실행하며 실제 ROS 객체를 직접 보유하지 않는다. worker timeout 또는 비정상 종료 시 supervisor가 독립적으로 다음 순서를 수행한다.

```text
새 액션 시작 차단
→ 현재 run 액션 취소
→ 차체·팔 정지 요청
→ terminal/idle 확인
→ worker 종료
→ 안전 상태 미확인 시 별도 오류 보고
```

---

## 7. 제어 블록

제어 블록은 대기, 상태 조회, 취소, 정지, 인지 상태 조회, 로봇 추정 상태 조회를 담당한다.

### 7.1 `WAIT_SECOND`

#### 요약

생성 코드 worker의 현재 제어 흐름을 지정 시간 동안 대기시킨다.

비동기 ROS 액션은 Gateway에서 독립적으로 계속 실행될 수 있다.

#### 시그니처

```python
robot.WAIT_SECOND(
    seconds: float,
) -> OperationResult
```

#### 실행 방식

```text
동기
하드웨어 동작 없음
자원 점유 없음
```

#### 인자

##### `seconds`

- 타입: `float`
- 단위: second
- finite 값만 허용
- `0.0` 이하 금지
- 허용 범위:

```text
0 < seconds <= config.control_limits.max_wait_seconds_per_call
```

#### 동작

- monotonic clock을 기준으로 대기한다.
- plain `time.sleep()`을 생성 코드에 노출하지 않는다.
- supervisor의 run 취소, `STOP`, worker 종료 요청에 반응할 수 있는 interruptible wait로 구현한다.
- 대기 시간은 전체 run wall-clock timeout에 포함된다.

#### 성공 후 보장

- 요청한 대기 시간이 경과함
- 어떤 비동기 액션의 성공 또는 종료도 보장하지 않음
- 로봇 자원 상태를 변경하지 않음

#### 가능한 실패

| error code | 의미 |
|---|---|
| `INVALID_ARGUMENT` | 타입, finite 여부 또는 범위 오류 |
| `RUN_CANCELED` | 현재 run이 외부에서 취소됨 |
| `RUN_STOPPED` | 현재 run에 `STOP`이 적용됨 |
| `RUN_WALL_TIMEOUT` | 전체 코드 실행시간 제한 도달 |
| `INTERNAL_ERROR` | 대기 구현의 예상하지 못한 오류 |

#### 주의

다음 코드는 잘못된 사용이다.

```python
move = robot.MOVE_BASE(distance_m=0.20)
robot.WAIT_SECOND(seconds=3.0)
# 3초가 지났다는 사실만 알 수 있으며 move 성공 여부는 알 수 없다.
```

액션 결과가 필요하면 반드시 `WAIT_ACTION` 또는 `CHECK_ACTION`을 사용한다.

---

### 7.2 `WAIT_ACTION`

#### 요약

지정 비동기 액션이 terminal 상태에 도달할 때까지 제한된 시간 동안 기다린다.

#### 시그니처

```python
robot.WAIT_ACTION(
    action: ActionHandle,
    timeout_s: float,
) -> ActionResult
```

#### 실행 방식

```text
동기 제어 함수
대상 액션 자체는 비동기로 실행됨
```

#### 인자

##### `action`

- 타입: `ActionHandle`
- 현재 `run_id`가 소유한 유효한 handle이어야 함

##### `timeout_s`

- 타입: `float`
- 단위: second
- finite 값만 허용
- `0.0` 이하 금지
- 허용 범위:

```text
0 < timeout_s <= config.control_limits.max_wait_action_timeout_s
```

#### 동작

1. handle 형식, 액션 존재 여부, 소유권 확인
2. 이미 terminal이면 즉시 기존 최종 결과 반환
3. monotonic clock으로 terminal 상태까지 대기
4. 제한시간 안에 종료되면 해당 `ActionResult` 반환
5. timeout이면 해당 액션에 자동 취소 요청
6. 안전한 정지가 확인되면 액션을 `TIMED_OUT` terminal 상태로 종료하고 결과 반환
7. 취소 또는 안전 정지가 확인되지 않으면 `FAILED`와 적절한 오류 코드 반환

#### timeout 규칙

`WAIT_ACTION` timeout과 액션 자체의 hard timeout은 서로 다르다.

```text
WAIT_ACTION timeout:
    현재 생성 코드가 해당 액션 결과를 기다리는 최대 시간

Action hard timeout:
    생성 코드가 기다리는지와 무관하게 액션 자체가 실행될 수 있는 최대 시간
```

`WAIT_ACTION` timeout 시 `cancel_on_timeout=True` 동작을 고정하며 LLM에 이를 변경하는 인자를 노출하지 않는다.

#### 경합 상황

취소 요청과 액션 자연 종료가 거의 동시에 발생할 수 있다.

- 취소가 적용되기 전에 액션이 성공하면 `SUCCEEDED`를 반환할 수 있다.
- 취소가 적용되기 전에 액션이 자체 실패하면 `FAILED`를 반환할 수 있다.
- timeout 취소가 실제로 적용되면 `TIMED_OUT`을 반환한다.

#### 가능한 오류

| error code | 의미 |
|---|---|
| `INVALID_ARGUMENT` | handle 또는 timeout 인자 오류 |
| `ACTION_NOT_FOUND` | 등록되지 않은 action ID |
| `ACTION_OWNERSHIP_MISMATCH` | 현재 run이 소유하지 않은 액션 |
| `WAIT_TIMEOUT` | timeout 후 안전한 취소가 완료되어 `TIMED_OUT`이 됨 |
| `ACTION_NOT_CANCELLABLE` | timeout 취소를 지원하지 않는 액션 |
| `CANCEL_FAILED` | 취소 요청 처리 실패 |
| `SAFE_STOP_UNCONFIRMED` | 취소 후 안전한 정지 확인 실패 |
| `RUN_CANCELED` | 현재 run 전체가 외부에서 취소됨 |
| `RUN_STOPPED` | 현재 run에 `STOP`이 적용됨 |
| `INTERNAL_ERROR` | 액션 registry 또는 대기 처리 오류 |

---

### 7.3 `WAIT_RESOURCE`

#### 요약

지정 자원이 유휴 상태로 관측될 때까지 제한된 시간 동안 기다린다.

#### 시그니처

```python
robot.WAIT_RESOURCE(
    resource_id: ResourceId,
    timeout_s: float,
) -> OperationResult
```

#### 실행 방식

```text
동기
자원을 획득하거나 예약하지 않음
```

#### 핵심 계약

`WAIT_RESOURCE` 성공은 다음 사실만 의미한다.

```text
함수가 반환되는 시점에 해당 자원이 idle 상태로 관측됨
```

다음 구동함수가 자원을 실제로 획득하기 전까지 다른 액션이 자원을 선점할 수 있다.

따라서 실제 구동함수는 항상 자체적으로 원자적 자원 획득을 수행하며 `RESOURCE_BUSY`를 반환할 수 있다.

#### 인자

##### `resource_id`

- 타입: `ResourceId`
- registry에서 `waitable: true`로 지정된 자원만 허용

##### `timeout_s`

- 타입: `float`
- 단위: second
- finite 값만 허용
- `0.0` 이하 금지
- 허용 범위:

```text
0 < timeout_s <= config.control_limits.max_wait_resource_timeout_s
```

#### 동작

- 자원 상태 변경 notification을 이용해 대기하는 것을 권장한다.
- busy polling loop를 생성 코드에 작성하지 않는다.
- timeout이 발생해도 해당 자원을 점유한 액션을 취소하지 않는다.
- 현재 run 취소 또는 `STOP` 시 대기를 중단한다.

#### 성공 후 보장

- 반환 직전 지정 자원이 idle로 관측됨
- 자원 lease 또는 lock은 생성되지 않음
- 기존 액션 상태를 변경하지 않음

#### 가능한 실패

| error code | 의미 |
|---|---|
| `INVALID_ARGUMENT` | resource 또는 timeout 인자 오류 |
| `RESOURCE_NOT_FOUND` | 등록되지 않은 자원 ID |
| `RESOURCE_NOT_WAITABLE` | 공개 대기를 허용하지 않는 자원 |
| `WAIT_TIMEOUT` | 제한시간 안에 idle 상태가 되지 않음 |
| `RUN_CANCELED` | 현재 run이 외부에서 취소됨 |
| `RUN_STOPPED` | 현재 run에 `STOP`이 적용됨 |
| `INTERNAL_ERROR` | resource manager 오류 |

---

### 7.4 `CHECK_ACTION`

#### 요약

지정 액션의 현재 상태 snapshot을 즉시 반환한다.

#### 시그니처

```python
robot.CHECK_ACTION(
    action: ActionHandle,
) -> ActionResult
```

#### 실행 방식

```text
동기
대기 없음
액션 상태 변경 없음
```

#### 동작

- 액션 registry에서 thread-safe snapshot을 생성한다.
- `PENDING`, `RUNNING`, `CANCEL_REQUESTED`, terminal 상태를 모두 반환할 수 있다.
- 호출 시점의 snapshot이므로 반환 직후 상태가 변경될 수 있다.

#### 필드 규칙

- `PENDING`: 모든 시각 필드가 `None`
- `RUNNING`: `started_at_unix_ms`만 설정, `finished_at_unix_ms=None`, `duration_ms=None`
- terminal: 상태 계약에 따라 종료 시각 및 지속 시간 설정

#### 잘못된 handle 처리

예외를 발생시키지 않고 입력 handle의 식별 정보를 가진 synthetic `FAILED` 결과를 반환한다.

가능한 오류:

```text
INVALID_ARGUMENT
ACTION_NOT_FOUND
ACTION_OWNERSHIP_MISMATCH
INTERNAL_ERROR
```

---

### 7.5 `CANCEL_ACTION`

#### 요약

현재 run이 소유한 특정 비동기 액션에 취소를 요청하고 bounded cancellation timeout 동안 terminal 상태를 확인한다.

#### 시그니처

```python
robot.CANCEL_ACTION(
    action: ActionHandle,
) -> ActionResult
```

#### 실행 방식

```text
동기 제어 함수
일반 자원 lock을 기다리지 않는 우선 제어 경로 사용
```

#### 동작

1. handle, 액션 존재 여부, 소유권 확인
2. 액션이 이미 terminal이면 기존 최종 결과를 그대로 반환
3. 취소 가능 여부 확인
4. 액션을 `CANCEL_REQUESTED`로 전환하고 하위 취소 요청 전달
5. 설정된 취소 확인 timeout 동안 실제 terminal 상태 대기
6. 안전한 취소가 완료되면 `CANCELED` 결과 반환

노출되는 별도 timeout 인자는 없다. Gateway 설정의 함수별 취소 확인 timeout을 사용한다.

#### 경합 및 멱등성

- 이미 terminal인 액션에 호출해도 상태를 변경하지 않고 기존 결과를 반환한다.
- 취소 적용 전에 액션이 성공하면 `SUCCEEDED`가 반환될 수 있다.
- 취소 적용 전에 액션이 실패하면 `FAILED`가 반환될 수 있다.
- 반복 호출은 같은 액션을 중복 실행하거나 새로운 액션을 생성하지 않는다.

#### 가능한 오류

| error code | 의미 |
|---|---|
| `INVALID_ARGUMENT` | handle 형식 오류 |
| `ACTION_NOT_FOUND` | 등록되지 않은 액션 |
| `ACTION_OWNERSHIP_MISMATCH` | 현재 run이 소유하지 않음 |
| `ACTION_NOT_CANCELLABLE` | 취소 미지원 액션 |
| `CANCEL_FAILED` | 취소 요청 전달 또는 처리 실패 |
| `SAFE_STOP_UNCONFIRMED` | 대상 액션의 안전한 종료 확인 실패 |
| `INTERNAL_ERROR` | action manager 오류 |

---

### 7.6 `CANCEL_ALL`

#### 요약

현재 `run_id`가 소유한 모든 활성 비동기 액션에 취소를 요청하고 종료를 확인한다.

#### 시그니처

```python
robot.CANCEL_ALL() -> OperationResult
```

#### 실행 방식

```text
동기 제어 함수
현재 run 범위
```

#### 대상

다음 상태의 현재 run 액션을 대상으로 한다.

```text
PENDING
RUNNING
CANCEL_REQUESTED
```

다른 run 또는 외부 수동 제어가 소유한 액션은 취소하지 않는다.

#### 동작

1. 현재 run의 활성 액션 목록을 원자적으로 snapshot
2. 각 액션에 취소 요청
3. 설정된 전체 취소 확인 timeout 동안 terminal 상태 확인
4. 모든 대상이 terminal이면 `success=True`
5. 일부 대상의 취소 또는 종료 확인에 실패하면 `success=False`

활성 액션이 없을 때는 멱등적으로 `success=True`를 반환한다.

#### 성공 후 보장

- 호출 시점에 현재 run이 소유했던 모든 활성 액션이 terminal 상태
- 다른 run의 액션 상태는 변경하지 않음
- 현재 run은 이후 새로운 액션을 시작할 수 있음

`CANCEL_ALL`은 `STOP`과 달리 현재 run을 영구적인 stopped 상태로 만들지 않는다.

#### 가능한 실패

| error code | 의미 |
|---|---|
| `PARTIAL_CANCEL_FAILURE` | 일부 액션만 terminal 상태로 전환됨 |
| `SAFE_STOP_UNCONFIRMED` | 하나 이상의 동작 자원 정지 확인 실패 |
| `CANCEL_FAILED` | 전체 취소 처리 실패 |
| `INTERNAL_ERROR` | active action snapshot 또는 취소 관리 오류 |

세부 액션별 결과는 실행 로그의 `ActionRecord`에서 확인한다.

---

### 7.7 `STOP`

#### 요약

로봇 전체의 현재 동작을 제어된 방식으로 정지시키는 우선 안전 함수이다.

`STOP`은 비상 정지 latch가 아니며, 모터 전원 차단이나 ESTOP 해제를 수행하지 않는다.

#### 시그니처

```python
robot.STOP() -> OperationResult
```

#### 실행 방식

```text
동기
시스템 전체 범위
최우선 제어 경로
```

#### `CANCEL_ALL`과의 차이

| 항목 | `CANCEL_ALL` | `STOP` |
|---|---|---|
| 범위 | 현재 run의 액션 | 시스템 전체 동작 |
| 다른 run 또는 외부 액션 | 변경하지 않음 | 정지 대상이 될 수 있음 |
| 현재 run 이후 재동작 | 가능 | 동일 run에서는 금지 |
| 목적 | 정상적인 작업 취소 | 안전한 전체 정지 |
| ESTOP latch | 아님 | 아님 |

#### 공개 동작 의미

1. 현재 run을 `STOP_REQUESTED` 상태로 표시
2. stop sequence 동안 새로운 motion action 시작 차단
3. 시스템의 활성 motion action에 취소 또는 정지 요청
4. 차체에 즉시 정지 명령
5. 팔 trajectory 정지 및 현재 논리 자세 hold 요청
6. 그리퍼는 기본적으로 현재 명령 상태를 유지
7. 모든 motion resource가 정지 또는 idle인지 확인
8. 성공 또는 실패 결과 기록

그리퍼를 자동으로 열지 않는다. 물체를 들고 있을 때 자동 open은 낙하 위험이 있기 때문이다.

#### 성공 후 보장

- Gateway가 관찰 가능한 범위에서 차체와 팔 동작이 정지됨
- 현재 run에서 이후 새로운 motion action 시작이 거부됨
- 동일 코드에서 후속 이동이 필요하면 `STOP` 대신 `CANCEL_ACTION` 또는 `CANCEL_ALL`을 사용해야 함
- 새 사용자 명령은 별도의 승인된 새 run으로 실행 가능

#### 정지 후 상태

- 차체가 부분 이동한 뒤 실제 이동량을 알 수 없으면 base estimate를 `UNRELIABLE`로 표시
- 팔은 후퇴하지 않고 현재 논리 자세를 hold할 수 있음
- 그리퍼는 현재 상태를 유지
- 비상 정지 latch나 servo power-off 상태는 별도 안전 계층이 관리

#### 가능한 실패

| error code | 의미 |
|---|---|
| `SAFE_STOP_UNCONFIRMED` | 하나 이상의 motion domain 정지 확인 실패 |
| `PICO_COMMUNICATION_ERROR` | 하드웨어 정지 명령 통신 오류 |
| `ARM_STOP_FAILED` | 팔 trajectory 정지 확인 실패 |
| `BASE_STOP_FAILED` | 차체 정지 확인 실패 |
| `INTERNAL_ERROR` | stop supervisor 내부 오류 |

`STOP` 실패 시에도 Gateway는 watchdog과 하드웨어 안전 계층을 통해 추가 정지 시도를 수행하고, 사용자에게 안전 상태가 확인되지 않았음을 명확히 보고해야 한다.

---

### 7.8 `GET_OBJECT_STATE`

#### 요약

등록 물체의 최신 인식 상태를 동기 snapshot으로 반환한다.

#### 시그니처

```python
robot.GET_OBJECT_STATE(
    object_id: ObjectId,
) -> ObjectStateResult
```

#### 실행 방식

```text
동기
즉시 snapshot 반환
차체, 팔, 그리퍼 동작 없음
```

#### 인자

##### `object_id`

- 타입: 프로젝트 공통 `ObjectId` enum
- 사용자 표현을 매칭한 canonical ID만 사용

허용 예:

```python
state = robot.GET_OBJECT_STATE(
    object_id=ObjectId.BUDS3,
)
```

금지 예:

```python
robot.GET_OBJECT_STATE(object_id="버즈")
robot.GET_OBJECT_STATE(object_id="Buds 3")
```

#### 공개 동작 의미

- 최신 인지 pipeline snapshot을 읽는다.
- 차체를 회전하여 물체를 새로 탐색하지 않는다.
- 인지 target을 장시간 재설정하거나 reference bank 로딩을 기다리지 않는다.
- 물체의 좌표, bounding box, depth 등 원시 데이터는 반환하지 않는다.
- 파지 가능 위치로 정렬해야 하면 `ALIGN_WITH_OBJECT` 또는 `PICK_OBJECT`를 사용한다.

#### 상태 판단 기준

세부 알고리즘은 블랙박스로 두되 공개 계약상 다음을 만족해야 한다.

- `VISIBLE`: 설정된 최신성 기준을 만족하는 확정 인식 결과가 존재
- `NOT_VISIBLE`: pipeline health와 freshness가 정상이나 지정 물체가 확정되지 않음
- `AMBIGUOUS`: 복수 후보 또는 식별 충돌로 하나의 목표를 선택할 수 없음
- `STALE`: 마지막 관련 결과가 `perception.object_state_max_age_ms`보다 오래됨
- `PERCEPTION_UNAVAILABLE`: 필수 인지 노드, 카메라 또는 상태 heartbeat 사용 불가
- `UNKNOWN`: 내부 상태 조합으로 명확한 분류가 불가능

#### 성공 후 보장

이 함수는 query 결과를 반환할 뿐 로봇이나 인지 pipeline의 상태를 변경하지 않는다.

`NOT_VISIBLE`, `AMBIGUOUS`, `STALE`, `PERCEPTION_UNAVAILABLE`는 Python 예외가 아니라 정상적인 상태 값이다.

#### 가능한 error code

| error code | 의미 |
|---|---|
| `OBJECT_NOT_REGISTERED` | catalog에 없는 object ID |
| `PERCEPTION_STATE_ERROR` | 인지 상태 snapshot 생성 오류 |
| `INTERNAL_ERROR` | 예상하지 못한 Gateway 오류 |

`error_code`가 설정될 경우 상태는 보통 `UNKNOWN` 또는 `PERCEPTION_UNAVAILABLE`이다.

---

### 7.9 `GET_ROBOT_POS`

#### 요약

차체 추정 pose와 팔·그리퍼의 최신 논리적 각도 상태를 하나의 동기 snapshot으로 반환한다.

#### 시그니처

```python
robot.GET_ROBOT_POS() -> RobotPosResult
```

#### 실행 방식

```text
동기
즉시 snapshot 반환
로봇 동작 없음
```

#### 공개 동작 의미

Gateway가 다음 상태를 가능한 한 같은 snapshot 시점에 수집한다.

```text
차체:
    x_m
    y_m
    yaw_deg
    추정 신뢰 상태

팔:
    arm_lift_joint 논리 각도
    wrist_pitch_joint 논리 각도
    추정 신뢰 상태

그리퍼:
    gripper_joint 논리 각도
    추정 신뢰 상태
```

#### 좌표와 단위

차체 좌표계:

```text
시스템 세션 시작 pose = (0.0, 0.0, 0.0)
+x = 세션 시작 시 로봇 전방
+y = 세션 시작 시 로봇 좌측
+yaw 양수 = 반시계 방향
```

단위:

```text
x_m, y_m: meter
yaw_deg: degree
팔 및 그리퍼 각도: degree
```

#### snapshot 원자성

- 개별 상태 source를 thread-safe하게 읽는다.
- 각 source의 갱신 시각을 함께 반환한다.
- 서로 다른 하드웨어 source를 완전히 같은 물리 시각에 측정했다는 보장은 없다.
- `captured_at_unix_ms`는 Gateway가 최종 snapshot 객체를 구성한 시각이다.

#### 이동 중 호출

호출 자체를 거부하지 않는다.

- 이동 중인 하위 시스템은 `TRANSIENT`로 표시
- 차체 값은 마지막 확정 명령 누적값일 수 있음
- 팔과 그리퍼 값은 최신 commanded logical state일 수 있음
- 실제 물리 위치를 기반으로 정밀 제어하거나 안전 우회를 수행하는 근거로 사용해서는 안 됨

#### 성공 후 보장

- 로봇 상태를 변경하지 않음
- 반환된 값의 source, validity, timestamp를 함께 제공
- 값이 없으면 `None`과 `UNAVAILABLE`을 사용하며 임의의 0을 생성하지 않음

#### 가능한 error code

| error code | 의미 |
|---|---|
| `ROBOT_STATE_PARTIAL` | 일부 하위 상태만 구성 가능; `snapshot_state=PARTIAL` |
| `ROBOT_STATE_UNAVAILABLE` | snapshot을 구성할 수 없음 |
| `INTERNAL_ERROR` | 상태 집계 처리 오류 |

`ROBOT_STATE_PARTIAL`은 값 일부가 유용할 수 있으므로 반드시 전체 실패로 간주할 필요는 없다. 생성 코드는 사용하려는 하위 필드의 `EstimateState`를 확인해야 한다.

---

---

## 8. 차체 구동 블록

차체 구동 블록은 상대 이동·회전, 명령 이력 기반 위치 저장·복귀, 물체 기준 정렬을 담당한다.

### 8.1 `MOVE_BASE`

#### 요약

현재 차체가 바라보는 방향을 기준으로 지정 거리만큼 전진 또는 후진한다.

#### 시그니처

```python
robot.MOVE_BASE(
    distance_m: float,
) -> ActionHandle
```

#### 실행 방식

```text
비동기
취소 가능
```

#### 인자

##### `distance_m`

- 타입: `float`
- 단위: meter
- 양수: 전진
- 음수: 후진
- `0.0` 금지
- `NaN`, `inf`, `-inf` 금지
- 허용 범위:

```text
0 < abs(distance_m) <= config.base_limits.max_move_distance_m_per_call
```

최대 거리의 실제 수치는 하드웨어 테스트 후 설정 파일에서 확정한다.

#### 자원

```yaml
exclusive_resources:
  - BASE_MOTION
  - PICO_MOTION
```

#### 사전조건

- 비상 정지 상태가 아님
- 차체 및 하드웨어 통신 계층이 준비됨
- `BASE_MOTION`, `PICO_MOTION`을 획득할 수 있음
- 현재 run에 내부 동작 1회를 실행할 여유가 있음
- 안전 계층이 현재 이동을 허용함

추정 자세가 `unreliable`이어도 상대 이동 자체는 허용할 수 있다. 단, 이동 후에도 추정 자세는 `unreliable`로 유지된다.

#### 동작

1. 인자 및 사전조건 검사
2. 자원 원자적 획득
3. 상대 직선 이동 명령 시작
4. 내부 동작 카운터 1 증가
5. 완료, 실패, 취소 또는 timeout까지 상태 추적
6. 차체 정지 확인
7. 성공한 경우 추정 좌표 갱신
8. 자원 해제

#### 성공 후 보장

- 결과 상태는 `SUCCEEDED`
- 차체가 정지 상태
- 설정된 허용 오차 내에서 요청 이동이 완료됨
- 기존 추정 자세가 valid였다면 요청 거리만큼 논리적 추정 좌표가 갱신됨

#### 취소

- 취소 지원
- 취소 요청 후 `CANCEL_REQUESTED` 상태로 전환 가능
- 실제 차체 정지가 확인된 뒤 `CANCELED` terminal 상태가 됨
- 시작 후 취소되어 실제 이동량을 알 수 없으면 추정 자세는 `unreliable`

#### 가능한 실패와 로봇 상태

| error code | 의미 | 실제 동작 시작 여부 | 가능한 종료 상태 |
|---|---|---:|---|
| `INVALID_ARGUMENT` | 타입, 값 또는 범위 오류 | 아니오 | 차체 상태 불변 |
| `ESTOP_ACTIVE` | 비상 정지 활성 | 아니오 | 차체 정지 |
| `BASE_NOT_READY` | 차체 계층 준비 안 됨 | 아니오 | 기존 상태 유지 |
| `RESOURCE_BUSY` | 필요한 자원 사용 중 | 아니오 | 기존 액션 상태 유지 |
| `RUN_LIMIT_EXCEEDED` | 내부 동작 제한 초과 | 아니오 | 차체 상태 불변 |
| `SAFETY_BLOCKED` | 안전 계층이 이동을 거부 | 보통 아니오 | 정지 |
| `MOTION_EXECUTION_FAILED` | 하위 이동 명령 실패 | 가능 | 정지 시도, 부분 이동 가능 |
| `PICO_COMMUNICATION_ERROR` | 하드웨어 통신 오류 | 가능 | 실제 위치 불확실 가능 |
| `ACTION_HARD_TIMEOUT` | 액션 최대 실행시간 초과 | 예 | 정지 시도, 부분 이동 가능 |
| `CANCEL_FAILED` | 취소 또는 정지 확인 실패 | 예 | 실제 상태 불확실 가능 |

#### 예시

```python
move = robot.MOVE_BASE(distance_m=0.20)
move_result = robot.WAIT_ACTION(move, timeout_s=10.0)

if move_result.state != ActionState.SUCCEEDED:
    return TaskOutcome(
        status=TaskStatus.FAILED,
        message=move_result.error_message or "차체 이동에 실패했습니다.",
    )
```

---

### 8.2 `TURN_BASE`

#### 요약

현재 방향을 기준으로 지정 각도만큼 상대 회전한다.

#### 시그니처

```python
robot.TURN_BASE(
    angle_deg: float,
) -> ActionHandle
```

#### 실행 방식

```text
비동기
취소 가능
```

#### 인자

##### `angle_deg`

- 타입: `float`
- 단위: degree
- 양수: 좌회전, 반시계 방향
- 음수: 우회전, 시계 방향
- `0.0` 금지
- `NaN`, `inf`, `-inf` 금지
- 허용 범위:

```text
0 < abs(angle_deg) <= config.base_limits.max_turn_angle_deg_per_call
```

최대 회전각의 실제 수치는 하드웨어 테스트 후 설정 파일에서 확정한다.

#### 자원

```yaml
exclusive_resources:
  - BASE_MOTION
  - PICO_MOTION
```

#### 사전조건

- 비상 정지 상태가 아님
- 차체 및 하드웨어 통신 계층이 준비됨
- 필요한 자원을 획득할 수 있음
- 현재 run에 내부 동작 1회를 실행할 여유가 있음
- 안전 계층이 현재 회전을 허용함

#### 동작

1. 인자 및 사전조건 검사
2. 자원 원자적 획득
3. 상대 회전 시작
4. 내부 동작 카운터 1 증가
5. 완료, 실패, 취소 또는 timeout까지 상태 추적
6. 차체 정지 확인
7. 성공한 경우 추정 yaw 갱신
8. 자원 해제

#### 성공 후 보장

- 결과 상태는 `SUCCEEDED`
- 차체가 정지 상태
- 설정된 허용 오차 내에서 상대 회전 완료
- 기존 추정 자세가 valid였다면 yaw가 갱신되고 `[-180, 180)`으로 정규화됨

#### 취소

`MOVE_BASE`와 동일한 취소 규칙을 사용한다.

#### 가능한 실패와 로봇 상태

`MOVE_BASE`의 공통 오류를 사용하며 회전 계층 오류는 `MOTION_EXECUTION_FAILED`로 반환한다.

| 주요 error code | 가능한 종료 상태 |
|---|---|
| `INVALID_ARGUMENT` | 차체 상태 불변 |
| `RESOURCE_BUSY` | 기존 액션 상태 유지 |
| `RUN_LIMIT_EXCEEDED` | 차체 상태 불변 |
| `SAFETY_BLOCKED` | 정지 |
| `MOTION_EXECUTION_FAILED` | 부분 회전 후 정지 가능 |
| `PICO_COMMUNICATION_ERROR` | 실제 yaw 불확실 가능 |
| `ACTION_HARD_TIMEOUT` | 부분 회전 가능, 정지 시도 |
| `CANCEL_FAILED` | 실제 상태 불확실 가능 |

#### 예시

```python
turn = robot.TURN_BASE(angle_deg=-30.0)
turn_result = robot.WAIT_ACTION(turn, timeout_s=8.0)

if turn_result.state != ActionState.SUCCEEDED:
    return TaskOutcome(
        status=TaskStatus.FAILED,
        message=turn_result.error_message or "차체 회전에 실패했습니다.",
    )
```

---

### 8.3 `SAVE_POS`

#### 요약

현재 명령 이력 기반 추정 자세 `(x_m, y_m, yaw_deg)`를 세션 위치 레지스트리에 저장한다.

#### 시그니처

```python
robot.SAVE_POS(
    position_id: str,
    overwrite: bool = False,
) -> OperationResult
```

#### 실행 방식

```text
동기
모터 동작 없음
내부 동작 카운터 증가 없음
```

#### 인자

##### `position_id`

- 타입: `str`
- 생성 코드에서는 canonical ASCII snake_case ID 사용
- 권장 정규식:

```regex
^[a-z][a-z0-9_]{0,31}$
```

허용 예:

```text
start
start_position
pickup_zone_1
```

금지 예:

```text
Start Position
처음위치
../position
__system_home
```

`__`로 시작하는 이름은 시스템 예약 이름으로 간주하여 금지한다.

##### `overwrite`

- 타입: `bool`
- 기본값: `False`
- `False`: 동일 ID가 존재하면 실패
- `True`: 기존 ID를 현재 추정 자세로 교체
- 향후 자동 실행 모드에서는 `overwrite=True` 호출을 금지하거나 별도 승인 대상으로 분류할 수 있음

#### 자원

```yaml
resources:
  exclusive:
    - POSITION_STORE
  requires_idle:
    - BASE_MOTION
```

#### 사전조건

- 추정 자세가 valid 상태
- 실행 중인 차체 이동 액션이 없음
- 위치 저장소 사용 가능
- `position_id`가 규칙에 맞음

#### 동작

1. ID와 overwrite 인자 검사
2. 차체가 정지 상태인지 확인
3. 현재 추정 자세 snapshot 획득
4. 위치 레지스트리에 저장 또는 교체
5. `OperationResult` 반환

#### 성공 후 보장

- `success=True`
- 현재 세션 위치 레지스트리에 `position_id`가 존재
- 저장값은 호출 시점의 추정 `(x_m, y_m, yaw_deg)`
- 차체와 팔의 실제 물리 상태는 변경하지 않음

#### 가능한 실패와 상태

| error code | 의미 | 가능한 상태 |
|---|---|---|
| `POSITION_ID_INVALID` | ID 형식 오류 또는 예약 이름 | 저장소 불변 |
| `POSITION_ALREADY_EXISTS` | 동일 ID가 있고 overwrite가 False | 저장소 불변 |
| `POSE_ESTIMATE_UNRELIABLE` | 현재 추정 자세를 신뢰할 수 없음 | 저장소 불변 |
| `RESOURCE_BUSY` | 차체가 움직이는 중이거나 저장소 사용 중 | 저장소 불변 |
| `POSITION_STORE_ERROR` | 내부 위치 레지스트리 오류 | 일부 저장 여부는 Gateway 로그 확인 필요 |
| `INTERNAL_ERROR` | 예상하지 못한 시스템 오류 | 저장 여부 불확실 가능 |

#### 예시

```python
save_result = robot.SAVE_POS(
    position_id="start_position",
    overwrite=False,
)

if not save_result.success:
    return TaskOutcome(
        status=TaskStatus.FAILED,
        message=save_result.error_message or "현재 위치를 저장하지 못했습니다.",
    )
```

---

### 8.4 `MOVE_BASE_TO_POS`

#### 요약

세션 위치 레지스트리에 저장된 추정 자세로 차체를 복귀시킨다. 위치와 최종 방향을 모두 복원한다.

#### 시그니처

```python
robot.MOVE_BASE_TO_POS(
    position_id: str,
) -> ActionHandle
```

#### 실행 방식

```text
비동기
취소 가능
```

#### 인자

##### `position_id`

`SAVE_POS`와 동일한 canonical ID 형식을 사용한다.

#### 자원

```yaml
exclusive_resources:
  - BASE_MOTION
  - PICO_MOTION
shared_or_read_resources:
  - POSITION_STORE
```

#### 사전조건

- `position_id`가 현재 세션 위치 레지스트리에 존재
- 현재 추정 자세가 valid
- 저장된 추정 자세가 valid
- 비상 정지 상태가 아님
- 차체 계층 준비 완료
- 자원 획득 가능
- 최대 3회의 내부 동작을 시작할 수 있는 run budget이 남아 있음

#### 공개 동작 의미

v0.1은 경로 계획이나 장애물 우회를 수행하지 않는다.

내부 기본 절차:

```text
1. 현재 추정 위치에서 목표 위치의 방위각 계산
2. 목표 위치 방향으로 상대 회전
3. 목표 위치까지 직선 이동
4. 저장된 최종 yaw로 상대 회전
5. 차체 정지 확인
```

각 단계가 설정된 허용 오차 안에 이미 들어오면 해당 내부 동작을 생략한다.

후진을 이용한 최단 경로 최적화는 v0.1 범위에 포함하지 않는다. 기본적으로 목표 방향을 바라본 뒤 전진한다.

#### 성공 후 보장

- 결과 상태는 `SUCCEEDED`
- 차체 정지
- 논리적 추정 pose가 저장된 `(x_m, y_m, yaw_deg)`에 설정 허용 오차 내로 복귀
- 성공 시 논리적 추정 pose는 저장된 pose 값으로 정규화하여 갱신 가능

이 성공은 실제 외부 좌표계에서 정확히 같은 물리 위치에 도달했다는 보장이 아니다. 명령 이력 기반 추정 좌표에 대한 성공이다.

#### 취소

- 모든 내부 하위 이동에 취소가 전파됨
- 차체 정지 확인 후 `CANCELED`
- 일부 하위 이동 후 취소되어 실제 이동량을 알 수 없으면 추정 자세는 `unreliable`

#### 내부 동작 카운트

```text
초기 회전: 수행 시 +1
직선 이동: 수행 시 +1
최종 회전: 수행 시 +1
최대: 3
```

#### 가능한 실패와 상태

| error code | 의미 | 가능한 종료 상태 |
|---|---|---|
| `POSITION_ID_INVALID` | ID 형식 오류 | 차체 상태 불변 |
| `POSITION_NOT_FOUND` | 세션에 저장된 위치 없음 | 차체 상태 불변 |
| `POSE_ESTIMATE_UNRELIABLE` | 현재 또는 저장 위치 계산에 필요한 추정값 무효 | 차체 상태 불변 |
| `RESOURCE_BUSY` | 차체/Pico 자원 사용 중 | 기존 상태 유지 |
| `RUN_LIMIT_EXCEEDED` | 최대 내부 동작 budget 부족 | 차체 상태 불변 |
| `SAFETY_BLOCKED` | 안전 계층이 하위 이동을 거부 | 정지, 부분 이동 가능 |
| `MOTION_EXECUTION_FAILED` | 회전 또는 직선 이동 실패 | 부분 경로 수행 가능 |
| `PICO_COMMUNICATION_ERROR` | 하드웨어 통신 오류 | 실제 위치 불확실 가능 |
| `ACTION_HARD_TIMEOUT` | 전체 복귀 timeout | 부분 경로 수행 가능, 정지 시도 |
| `CANCEL_FAILED` | 안전한 취소 확인 실패 | 실제 상태 불확실 가능 |

#### 예시

```python
return_action = robot.MOVE_BASE_TO_POS(
    position_id="start_position",
)
return_result = robot.WAIT_ACTION(
    return_action,
    timeout_s=30.0,
)

if return_result.state != ActionState.SUCCEEDED:
    return TaskOutcome(
        status=TaskStatus.FAILED,
        message=return_result.error_message or "저장 위치로 복귀하지 못했습니다.",
    )
```

---

### 8.5 `ALIGN_WITH_OBJECT`

#### 요약

등록된 물체를 탐색하고, 필요하면 차체를 회전 및 전후 이동하여 해당 물체가 로봇팔이 잡을 수 있는 설정된 작업 범위 안에 오도록 차체를 정렬한다.

내부 인지 및 정렬 알고리즘, 허용 오차, 검색 패턴, 보정 횟수는 공개 Python API에서 숨기는 블랙박스로 둔다.

#### 시그니처

```python
robot.ALIGN_WITH_OBJECT(
    object_id: ObjectId,
) -> ActionHandle
```

#### 실행 방식

```text
비동기
취소 가능
인지 조회는 내부 동기 호출
```

#### 인자

##### `object_id`

- 타입: 프로젝트 공통 `ObjectId` enum
- LLM은 사용자 표현을 canonical ID로 매칭한 뒤 enum만 사용

허용 예:

```python
robot.ALIGN_WITH_OBJECT(
    object_id=ObjectId.BUDS3,
)
```

금지 예:

```python
robot.ALIGN_WITH_OBJECT(object_id="버즈")
robot.ALIGN_WITH_OBJECT(object_id="Buds 3")
```

#### 자원

```yaml
exclusive_resources:
  - BASE_MOTION
  - PICO_MOTION
```

인지 관련 배타 자원은 사용하지 않지만, 인지 시스템 정상 상태를 사전조건으로 확인한다.

#### 사전조건

- `object_id`가 등록 물체 catalog에 존재
- 인지 파이프라인이 준비됨
- 필요한 카메라 결과가 유효함
- 비상 정지 상태가 아님
- 차체 계층 준비 완료
- 차체 및 Pico 자원 획득 가능
- 설정된 최대 내부 정렬 동작을 실행할 수 있는 run budget이 남아 있음

#### 공개 동작 의미

내부 동작은 구현 세부사항이지만 공개 계약상 다음 목적을 만족해야 한다.

```text
1. 지정 물체 탐색 또는 존재 확인
2. 물체 방향에 대한 차체 회전 정렬
3. 필요한 경우 전후 거리 조정
4. 물체가 로봇팔 파지 가능 작업 범위에 들어왔는지 재확인
5. 차체 정지
```

`ALIGN_WITH_OBJECT`는 팔 관절이나 그리퍼를 직접 구동하지 않는다.

`PICK_OBJECT`와 `PLACE_NEXT_TO_OBJECT`는 필요할 경우 이 정렬 기능을 내부에서 수행할 수 있다.

#### 성공 후 보장

- 결과 상태는 `SUCCEEDED`
- 지정 물체가 완료 시점에 인지됨
- 차체 정지
- 물체가 설정된 정렬 허용 오차와 파지 가능 거리 범위 안에 있음
- 팔 또는 그리퍼는 동작하지 않음

성공 결과는 물체가 이후에도 움직이지 않는다는 보장이나 실제 파지 성공 보장을 포함하지 않는다.

#### 취소

- 현재 수행 중인 차체 보정 명령에 취소 전파
- 안전한 정지 확인 후 `CANCELED`
- 부분 보정 후 실제 이동량을 알 수 없으면 추정 자세를 `unreliable`로 표시

#### 내부 동작 카운트

- 실제 수행된 회전 보정 1회마다 +1
- 실제 수행된 직선 보정 1회마다 +1
- 인지 조회, confidence 계산, 상태 확인은 카운트하지 않음
- 한 호출당 최대 내부 동작 수는 설정 파일로 제한

#### 가능한 실패와 상태

| error code | 의미 | 가능한 종료 상태 |
|---|---|---|
| `OBJECT_NOT_REGISTERED` | catalog에 없는 object ID | 차체 상태 불변 |
| `PERCEPTION_UNAVAILABLE` | 카메라 또는 인지 파이프라인 사용 불가 | 보통 차체 상태 불변 |
| `OBJECT_NOT_FOUND` | 검색 범위 안에서 물체를 찾지 못함 | 검색 회전 후 정지 가능 |
| `OBJECT_AMBIGUOUS` | 같은 목표를 하나로 확정할 수 없음 | 정지 |
| `OBJECT_LOST` | 정렬 과정 중 목표를 놓침 | 부분 이동 후 정지 가능 |
| `TARGET_NOT_GRASPABLE` | 허용된 보정 범위 안에서 파지 가능 영역에 넣을 수 없음 | 정지 |
| `ALIGNMENT_TIMEOUT` | 정렬 시간 또는 내부 보정 횟수 초과 | 부분 이동 후 정지 |
| `RESOURCE_BUSY` | 차체/Pico 자원 사용 중 | 기존 상태 유지 |
| `RUN_LIMIT_EXCEEDED` | 내부 동작 budget 부족 | 시작 전이면 상태 불변 |
| `SAFETY_BLOCKED` | 안전 계층이 보정 이동을 거부 | 정지 |
| `MOTION_EXECUTION_FAILED` | 하위 회전 또는 이동 실패 | 부분 이동 가능 |
| `PICO_COMMUNICATION_ERROR` | 하드웨어 통신 오류 | 실제 위치 불확실 가능 |
| `ACTION_HARD_TIMEOUT` | 전체 정렬 hard timeout | 정지 시도, 부분 이동 가능 |
| `CANCEL_FAILED` | 안전한 취소 확인 실패 | 실제 상태 불확실 가능 |

#### 예시

```python
align = robot.ALIGN_WITH_OBJECT(
    object_id=ObjectId.BUDS3,
)
align_result = robot.WAIT_ACTION(
    align,
    timeout_s=25.0,
)

if align_result.state != ActionState.SUCCEEDED:
    return TaskOutcome(
        status=TaskStatus.FAILED,
        message=align_result.error_message or "물체 정렬에 실패했습니다.",
    )
```

---

---

## 9. 팔·그리퍼 블록

### 9.0 공통 의미

팔·그리퍼 블록의 공개 논리 관절은 다음 세 개이다.

```text
arm_lift_joint     → arm_lift_deg
wrist_pitch_joint  → wrist_pitch_deg
gripper_joint      → gripper_deg
```

단위와 방향:

- 모든 공개 각도는 degree이다.
- `gripper_deg = 0`은 열린 기준 자세이다.
- `gripper_deg > 0`은 닫힘 방향이다.
- 현재 모델의 논리적 gripper 범위는 기본적으로 `0°`부터 `90°`이다. 실제 최종 범위는 runtime config가 우선한다.

> **Primitive 계약**  
> 팔 primitive는 `arm_lift_deg`, `wrist_pitch_deg` 두 값만 저장하고 실행한다. 그리퍼 각도는 primitive에 포함하지 않으며, `SET_ARM_PRIMITIVE` 실행 전후의 그리퍼 명령 상태를 유지한다.

#### 팔·그리퍼 자원 규칙

```text
SET_ARM_JOINTS       : ARM_MOTION + PICO_MOTION
SET_GRIPPER          : GRIPPER_MOTION + PICO_MOTION
SAVE_ARM_PRIMITIVE   : ARM_PRIMITIVE_STORE, ARM_MOTION idle 필요
SET_ARM_PRIMITIVE    : ARM_MOTION + PICO_MOTION
PICK_OBJECT          : BASE_MOTION + ARM_MOTION + GRIPPER_MOTION + PICO_MOTION
PLACE_NEXTTO_OBJECT  : BASE_MOTION + ARM_MOTION + GRIPPER_MOTION + PICO_MOTION
```

현재 하드웨어 명령이 팔·그리퍼 전체 logical state를 함께 전송한다면 Gateway는 변경하지 않는 관절의 최신 유효 값을 원자적으로 읽어 보존해야 한다.

### 9.1 `SET_ARM_JOINTS`

#### 요약

그리퍼의 현재 논리 명령값을 유지하면서 두 팔 논리 관절을 지정 각도로 이동한다.

#### 시그니처

```python
robot.SET_ARM_JOINTS(
    arm_lift_deg: float,
    wrist_pitch_deg: float,
) -> ActionHandle
```

#### 실행 방식

```text
비동기
취소 가능
내부 motion step: 실제 팔 trajectory 시작 시 1
```

#### 인자

| 인자 | 타입 | 단위 | 규칙 |
|---|---|---|---|
| `arm_lift_deg` | `float` | degree | finite; runtime arm limit와 safe-region 통과 필요 |
| `wrist_pitch_deg` | `float` | degree | finite; runtime arm limit와 safe-region 통과 필요 |

현재 프로젝트 설정의 참고 범위는 대략 다음과 같지만 최종 Gateway 설정과 승인된 safe-region이 authoritative하다.

```text
arm_lift_deg: 약 -57.3° ~ +57.3°
wrist_pitch_deg: 약 -74.5° ~ +74.5°
```

단순 개별 범위 안에 들어와도 두 관절 조합 또는 이동 경로가 unsafe이면 거부한다.

#### 사전조건

- ESTOP 비활성
- 팔 제어 계층과 servo bridge 준비 완료
- 승인된 관절 한계와 safe-region 사용 가능
- `ARM_MOTION`, `PICO_MOTION` 원자적 획득 가능
- 현재 그리퍼 logical state를 안전하게 읽을 수 있음
- 현재 run의 내부 motion budget이 1 이상 남음

#### 동작

1. 인자와 finite 여부 검사
2. 현재 그리퍼 logical angle snapshot 획득
3. 목표 팔 관절 조합과 전체 경로 안전성 검사
4. 자원 원자적 획득
5. 그리퍼 값을 유지한 full logical goal 생성
6. 팔 trajectory 시작 및 내부 motion counter +1
7. 완료·실패·취소·timeout 추적
8. commanded arm state 갱신 및 자원 해제

#### 성공 후 보장

- 결과 상태 `SUCCEEDED`
- 팔 trajectory 종료 및 hold/idle 상태
- commanded arm state가 목표 각도로 갱신됨
- 그리퍼 logical command는 변경되지 않음

현재 물리 encoder 피드백이 없다면 성공은 실제 관절 측정 도달이 아니라 승인된 명령 trajectory 완료를 의미한다.

#### 가능한 실패

| error code | 의미 | 가능한 상태 |
|---|---|---|
| `INVALID_ARGUMENT` | 타입, finite 여부 또는 인자 형식 오류 | 상태 불변 |
| `ARM_LIMIT_VIOLATION` | 개별 관절 범위 위반 | 상태 불변 |
| `ARM_PATH_UNSAFE` | 목표 조합 또는 이동 경로가 safe-region 밖 | 상태 불변 |
| `ARM_NOT_READY` | 팔 제어 계층 준비 안 됨 | 기존 상태 유지 |
| `ROBOT_STATE_UNAVAILABLE` | 보존할 그리퍼 상태를 읽을 수 없음 | 상태 불변 |
| `RESOURCE_BUSY` | 팔/Pico 자원 사용 중 | 기존 액션 유지 |
| `RUN_LIMIT_EXCEEDED` | 내부 motion budget 부족 | 상태 불변 |
| `ARM_EXECUTION_FAILED` | trajectory 실행 실패 | 부분 이동 가능 |
| `PICO_COMMUNICATION_ERROR` | servo 명령 통신 오류 | 실제 팔 상태 불확실 가능 |
| `ACTION_HARD_TIMEOUT` | 팔 액션 hard timeout | 정지 시도, 부분 이동 가능 |
| `CANCEL_FAILED` | 취소 또는 hold 확인 실패 | 실제 상태 불확실 가능 |

### 9.2 `SET_GRIPPER`

#### 요약

팔 두 관절의 현재 logical command를 유지하면서 그리퍼를 지정 논리 각도로 이동한다.

#### 시그니처

```python
robot.SET_GRIPPER(
    gripper_deg: float,
) -> ActionHandle
```

#### 실행 방식

```text
비동기
취소 가능
내부 motion step: 실제 그리퍼 trajectory 시작 시 1
```

#### 인자

- 타입: `float`
- 단위: degree
- finite 값만 허용
- `0°`: 열린 기준 자세
- 양수: 닫힘 방향
- 허용 범위:

```text
config.gripper_limits.min_deg <= gripper_deg <= config.gripper_limits.max_deg
```

현재 논리 모델의 참고 범위는 `0°`부터 `90°`이다. `90°` logical close가 물리 servo shaft의 90°를 뜻하는 것은 아니며, 현재 기구 매핑에서는 더 큰 물리 shaft 회전에 대응할 수 있다.

#### 사전조건

- ESTOP 비활성
- 그리퍼 제어 계층 준비 완료
- `GRIPPER_MOTION`, `PICO_MOTION` 획득 가능
- 보존할 두 팔 logical state를 읽을 수 있음
- 내부 motion budget이 1 이상 남음

#### 동작

1. 인자와 logical gripper 범위 검사
2. 현재 두 팔 logical angle snapshot 획득
3. 자원 획득
4. 팔 값을 유지한 full logical goal 생성
5. 그리퍼 trajectory 시작 및 내부 motion counter +1
6. 완료·실패·취소·timeout 추적
7. commanded gripper state 갱신 및 자원 해제

#### 성공 후 보장

- 결과 상태 `SUCCEEDED`
- commanded gripper state가 목표 각도로 갱신됨
- 팔 두 관절의 logical command는 변경되지 않음

`SET_GRIPPER` 성공은 물체를 실제로 잡았다는 보장이 아니다. 파지 임무에는 `PICK_OBJECT`를 사용한다.

#### 가능한 실패

```text
INVALID_ARGUMENT
GRIPPER_LIMIT_VIOLATION
GRIPPER_NOT_READY
ROBOT_STATE_UNAVAILABLE
RESOURCE_BUSY
RUN_LIMIT_EXCEEDED
GRIPPER_EXECUTION_FAILED
PICO_COMMUNICATION_ERROR
ACTION_HARD_TIMEOUT
CANCEL_FAILED
```

### 9.3 `SAVE_ARM_PRIMITIVE`

#### 요약

호출 시점의 안정된 팔 관절값 두 개를 이름 있는 primitive로 저장한다. 그리퍼 각도는 저장하지 않는다.

#### 시그니처

```python
robot.SAVE_ARM_PRIMITIVE(
    primitive_id: str,
    overwrite: bool = False,
) -> OperationResult
```

#### 실행 방식

```text
동기
로봇 motion 없음
내부 motion step 증가 없음
```

#### primitive ID

권장 정규식:

```regex
^[a-z][a-z0-9_]{0,31}$
```

허용 예:

```text
pre_grasp
carry_pose
user_pose_1
```

금지 예:

```text
PRE GRASP
기본자세
../home
__system_home
```

#### 저장 namespace

v0.2 권장 기본안:

- 시스템 primitive: commissioning/config에서 로드, 영구적, 생성 코드에서 읽기 전용
- 세션 primitive: `SAVE_ARM_PRIMITIVE`가 저장, 시스템 프로세스가 유지되는 동안만 유효
- 시스템 primitive와 동일한 ID를 덮어쓸 수 없음
- `overwrite=True`는 기존 세션 primitive에만 적용

사용자 primitive의 영구 저장은 이후 버전에서 별도 승인 정책과 함께 추가한다.

#### 사전조건

- 팔 motion이 idle
- `arm_state == EstimateState.VALID`
- `arm_lift_deg`, `wrist_pitch_deg` 모두 존재
- 현재 팔 자세가 승인된 safe-region 안에 있음
- `ARM_PRIMITIVE_STORE` 사용 가능
- primitive ID 유효

#### 성공 후 보장

- primitive에는 `arm_lift_deg`, `wrist_pitch_deg`만 저장됨
- 그리퍼 상태는 저장·변경되지 않음
- 차체와 팔의 실제 상태는 변경되지 않음

#### 가능한 실패

| error code | 의미 |
|---|---|
| `PRIMITIVE_ID_INVALID` | ID 형식 또는 예약 이름 오류 |
| `PRIMITIVE_ALREADY_EXISTS` | 같은 세션 ID가 있고 overwrite가 False |
| `PROTECTED_PRIMITIVE` | 시스템 primitive 저장·덮어쓰기 시도 |
| `ARM_STATE_UNAVAILABLE` | 저장할 팔 상태 없음 |
| `ARM_STATE_TRANSIENT` | 팔이 움직이는 중 |
| `ARM_STATE_UNRELIABLE` | 팔 추정 상태를 저장할 수 없음 |
| `ARM_PATH_UNSAFE` | 현재 pose가 승인 safe-region 밖 |
| `RESOURCE_BUSY` | 팔 또는 primitive 저장소 사용 중 |
| `PRIMITIVE_STORE_ERROR` | registry 저장 오류 |

### 9.4 `SET_ARM_PRIMITIVE`

#### 요약

저장된 팔 primitive를 실행한다. 그리퍼 logical command는 유지한다.

#### 시그니처

```python
robot.SET_ARM_PRIMITIVE(
    primitive_id: str,
) -> ActionHandle
```

#### 실행 방식

```text
비동기
취소 가능
내부 motion step: 실제 팔 trajectory 시작 시 1
```

#### 동작

1. primitive ID 검사 및 registry 조회
2. 저장된 `arm_lift_deg`, `wrist_pitch_deg` 읽기
3. 현재 그리퍼 logical state snapshot 획득
4. 현재 상태에서 primitive까지의 경로 안전성 재검사
5. `ARM_MOTION`, `PICO_MOTION` 자원 획득
6. gripper 유지 full goal 실행
7. 완료·실패·취소·timeout 추적

저장 당시 안전했던 primitive라도 현재 pose에서 그 위치까지 가는 경로가 unsafe이면 실행을 거부한다.

#### 성공 후 보장

- commanded arm state가 primitive의 두 관절값으로 갱신됨
- 그리퍼 logical command 유지
- 팔 trajectory 종료 및 hold/idle 상태

#### 가능한 실패

```text
PRIMITIVE_ID_INVALID
PRIMITIVE_NOT_FOUND
INVALID_PRIMITIVE
ARM_NOT_READY
ARM_PATH_UNSAFE
ROBOT_STATE_UNAVAILABLE
RESOURCE_BUSY
RUN_LIMIT_EXCEEDED
ARM_EXECUTION_FAILED
PICO_COMMUNICATION_ERROR
ACTION_HARD_TIMEOUT
CANCEL_FAILED
```

### 9.5 `PICK_OBJECT`

#### 요약

등록 물체를 확인하고, 필요하면 내부적으로 `ALIGN_WITH_OBJECT`에 해당하는 탐색·회전·거리 보정을 수행한 뒤 팔과 그리퍼를 사용해 물체를 파지한다.

호출자가 미리 `ALIGN_WITH_OBJECT`를 실행할 필요는 없다. 이미 파지 가능 범위에 정렬되어 있으면 내부 정렬 단계를 생략할 수 있다.

#### 시그니처

```python
robot.PICK_OBJECT(
    object_id: ObjectId,
) -> ActionHandle
```

#### 실행 방식

```text
비동기 높은 수준 액션
취소 가능
내부 인지·차체·팔·그리퍼 단계는 블랙박스
```

#### 자원

```yaml
exclusive_resources:
  - BASE_MOTION
  - ARM_MOTION
  - GRIPPER_MOTION
  - PICO_MOTION
```

높은 수준 액션이 진행되는 동안 다른 motion 액션이 중간에 끼어들지 않도록 필요한 자원을 전체 임무 범위에서 관리한다.

#### 공개 동작 의미

최소 공개 계약:

```text
1. object_id 등록 여부와 인지 파이프라인 상태 확인
2. 물체 탐색 또는 최신 유효 관측 확인
3. 필요 시 내부 ALIGN 수행
   - 회전 정렬
   - 전후 거리 보정
   - 파지 가능 범위 재확인
4. 팔 도달 가능성·IK·safe path 검사
5. pre-grasp 및 grasp trajectory 수행
6. 그리퍼 닫기
7. 설정된 방식으로 파지 결과 확인
8. 필요 시 lift/hold 또는 안전한 post-grasp pose 이동
9. 차체·팔 정지 및 보유 상태 기록
```

세부 탐색 패턴, 접근 오프셋, primitive, 그리퍼 각도, lift 높이는 물체별 grasp profile과 Gateway 설정으로 관리한다.

#### 사전조건

- `object_id`가 catalog에 등록됨
- 인지 파이프라인 사용 가능
- 차체·팔·그리퍼 제어 계층 준비 완료
- 이미 다른 물체를 보유 중이지 않음
- 필요한 자원 획득 가능
- 높은 수준 함수의 최대 내부 motion step을 수행할 run budget이 남음
- 물체별 grasp profile과 승인된 safe-region 사용 가능

#### 성공 후 보장

- 결과 상태 `SUCCEEDED`
- 내부 ALIGN 성공 또는 불필요 판정 완료
- 설정된 grasp verification policy가 성공 조건을 만족함
- Gateway의 logical held-object state가 `object_id`로 기록됨
- 차체 정지
- 팔·그리퍼가 완료 상태 또는 설정된 hold pose

실제 힘·전류·encoder 피드백이 없는 구성에서는 성공 보장의 강도가 제한될 수 있다. 결과 설명은 사용한 검증 source 이상으로 실제 파지를 과장해서는 안 된다.

#### 취소

- 현재 내부 차체·팔·그리퍼 단계에 취소를 전파한다.
- 가능한 경우 차체 정지, 팔 hold, 그리퍼 현재 상태 유지 후 terminal 상태로 전환한다.
- 물체를 들고 있을 가능성이 있는 단계에서는 자동으로 그리퍼를 열지 않는다.
- 취소 후 held-object state가 확정되지 않으면 `UNRELIABLE` 또는 별도 unknown 상태로 기록한다.

#### 가능한 실패

| error code | 의미 |
|---|---|
| `OBJECT_NOT_REGISTERED` | catalog에 없는 물체 |
| `PERCEPTION_UNAVAILABLE` | 인지 파이프라인 사용 불가 |
| `OBJECT_NOT_FOUND` | 검색 범위에서 물체를 찾지 못함 |
| `OBJECT_AMBIGUOUS` | 목표를 하나로 확정하지 못함 |
| `OBJECT_LOST` | 정렬·접근 중 목표를 놓침 |
| `TARGET_NOT_GRASPABLE` | 허용 보정 범위 내 파지 위치를 만들 수 없음 |
| `ALIGNMENT_TIMEOUT` | 내부 정렬 시간·횟수 초과 |
| `ALREADY_HOLDING_OBJECT` | 다른 물체를 이미 보유 중 |
| `GRASP_PROFILE_NOT_FOUND` | 물체별 grasp profile 없음 |
| `IK_FAILED` | 목표 팔 자세 계산 실패 |
| `ARM_PATH_UNSAFE` | 접근 경로가 safe-region 밖 |
| `GRIPPER_EXECUTION_FAILED` | 그리퍼 명령 실패 |
| `GRASP_FAILED` | 파지 검증 실패 |
| `GRASP_VERIFICATION_UNAVAILABLE` | 필수 파지 확인 source 사용 불가 |
| `RESOURCE_BUSY` | 필요한 motion 자원 사용 중 |
| `RUN_LIMIT_EXCEEDED` | 내부 motion budget 부족 |
| `ACTION_HARD_TIMEOUT` | 전체 pick hard timeout |
| `CANCEL_FAILED` | 안전한 취소 확인 실패 |

### 9.6 `PLACE_NEXTTO_OBJECT`

#### 요약

현재 보유 중인 물체를 등록된 기준 물체 옆의 안전한 배치 위치에 놓는다. 기준 물체 확인과 필요한 차체 정렬은 함수 내부에서 수행한다.

호출자가 미리 `ALIGN_WITH_OBJECT`를 실행할 필요는 없다.

#### 시그니처

```python
robot.PLACE_NEXTTO_OBJECT(
    reference_object_id: ObjectId,
) -> ActionHandle
```

#### 실행 방식

```text
비동기 높은 수준 액션
취소 가능
내부 인지·차체·팔·그리퍼 단계는 블랙박스
```

#### 공개 동작 의미

```text
1. 현재 held-object state 확인
2. reference_object_id 등록 여부와 인지 상태 확인
3. 기준 물체 탐색 또는 최신 관측 확인
4. 필요 시 내부 ALIGN 수행
   - 기준 물체 방향 회전
   - 배치 가능한 거리로 전후 보정
5. 기준 물체 주변의 설정된 배치 후보 중 안전한 위치 선택
6. 팔 도달 가능성·IK·safe path 검사
7. 배치 pose로 이동
8. 그리퍼를 열어 보유 물체 해제
9. 필요 시 팔을 안전한 post-place primitive로 이동
10. 차체·팔 정지 및 held-object state 해제
```

“옆”의 방향과 간격은 LLM이 좌표 계산으로 결정하지 않는다. 물체별 placement profile과 내부 알고리즘이 안전한 후보를 선택한다.

#### 자원

```yaml
exclusive_resources:
  - BASE_MOTION
  - ARM_MOTION
  - GRIPPER_MOTION
  - PICO_MOTION
```

#### 사전조건

- Gateway가 현재 보유 물체를 알고 있음
- 기준 물체가 catalog에 등록됨
- 인지·차체·팔·그리퍼 계층 준비 완료
- 기준 물체용 placement profile 사용 가능
- 필요한 motion 자원과 run budget 사용 가능

#### 성공 후 보장

- 결과 상태 `SUCCEEDED`
- 내부 ALIGN 성공 또는 불필요 판정 완료
- 그리퍼가 설정된 release 상태에 도달
- logical held-object state가 비어 있음
- 배치 후 팔과 차체가 정지 또는 설정된 post-place 상태

실제 물체가 목표 위치에 안정적으로 놓였다는 보장의 강도는 placement verification source에 따른다.

#### 취소

- 물체를 아직 보유 중이면 기본적으로 그리퍼를 유지하고 팔 hold를 시도한다.
- release가 이미 실행된 뒤 취소되면 물체를 다시 잡는 자동 복구를 수행하지 않는다.
- partial placement 상태를 로그에 명확히 기록한다.

#### 가능한 실패

| error code | 의미 |
|---|---|
| `NO_HELD_OBJECT` | 배치할 보유 물체가 없음 |
| `OBJECT_NOT_REGISTERED` | 기준 물체가 catalog에 없음 |
| `PERCEPTION_UNAVAILABLE` | 인지 사용 불가 |
| `OBJECT_NOT_FOUND` | 기준 물체를 찾지 못함 |
| `OBJECT_AMBIGUOUS` | 기준 물체를 하나로 확정하지 못함 |
| `OBJECT_LOST` | 정렬·배치 중 기준 물체를 놓침 |
| `TARGET_NOT_GRASPABLE` | 허용 범위에서 배치 작업 자세를 만들 수 없음 |
| `ALIGNMENT_TIMEOUT` | 내부 정렬 시간·횟수 초과 |
| `PLACEMENT_PROFILE_NOT_FOUND` | 기준 물체용 placement profile 없음 |
| `PLACEMENT_POSITION_NOT_FOUND` | 안전한 옆 배치 후보 없음 |
| `IK_FAILED` | 배치 팔 자세 계산 실패 |
| `ARM_PATH_UNSAFE` | 배치 경로가 safe-region 밖 |
| `GRIPPER_EXECUTION_FAILED` | release 명령 실패 |
| `PLACE_FAILED` | 배치 검증 실패 |
| `RESOURCE_BUSY` | 필요한 motion 자원 사용 중 |
| `RUN_LIMIT_EXCEEDED` | 내부 motion budget 부족 |
| `ACTION_HARD_TIMEOUT` | 전체 place hard timeout |
| `CANCEL_FAILED` | 안전한 취소 확인 실패 |

---

## 10. 공통 오류 코드

프로젝트 전체에서 단일 enum 또는 registry로 관리한다. 각 함수는 아래 코드의 일부만 반환한다.

### 10.1 입력·실행기·run

```text
INVALID_ARGUMENT
INTERNAL_ERROR
ESTOP_ACTIVE
RUN_CANCELED
RUN_STOPPED
RUN_WALL_TIMEOUT
RUN_LIMIT_EXCEEDED
```

### 10.2 액션·대기·취소

```text
ACTION_NOT_FOUND
ACTION_OWNERSHIP_MISMATCH
ACTION_NOT_CANCELLABLE
ACTION_HARD_TIMEOUT
WAIT_TIMEOUT
CANCEL_FAILED
PARTIAL_CANCEL_FAILURE
SAFE_STOP_UNCONFIRMED
```

### 10.3 자원

```text
RESOURCE_NOT_FOUND
RESOURCE_NOT_WAITABLE
RESOURCE_BUSY
```

### 10.4 차체·위치

```text
BASE_NOT_READY
BASE_STOP_FAILED
SAFETY_BLOCKED
MOTION_EXECUTION_FAILED
PICO_COMMUNICATION_ERROR
POSITION_ID_INVALID
POSITION_ALREADY_EXISTS
POSITION_NOT_FOUND
POSE_ESTIMATE_UNRELIABLE
POSITION_STORE_ERROR
```

### 10.5 인지·물체

```text
OBJECT_NOT_REGISTERED
PERCEPTION_UNAVAILABLE
PERCEPTION_STATE_ERROR
OBJECT_NOT_FOUND
OBJECT_AMBIGUOUS
OBJECT_LOST
TARGET_NOT_GRASPABLE
ALIGNMENT_TIMEOUT
```

### 10.6 로봇 상태

```text
ROBOT_STATE_PARTIAL
ROBOT_STATE_UNAVAILABLE
ARM_STATE_UNAVAILABLE
ARM_STATE_TRANSIENT
ARM_STATE_UNRELIABLE
```

### 10.7 팔·그리퍼·primitive

```text
ARM_NOT_READY
ARM_STOP_FAILED
ARM_LIMIT_VIOLATION
ARM_PATH_UNSAFE
ARM_EXECUTION_FAILED
GRIPPER_NOT_READY
GRIPPER_LIMIT_VIOLATION
GRIPPER_EXECUTION_FAILED
PRIMITIVE_ID_INVALID
PRIMITIVE_ALREADY_EXISTS
PRIMITIVE_NOT_FOUND
PROTECTED_PRIMITIVE
INVALID_PRIMITIVE
PRIMITIVE_STORE_ERROR
```

### 10.8 pick·place

```text
ALREADY_HOLDING_OBJECT
NO_HELD_OBJECT
GRASP_PROFILE_NOT_FOUND
PLACEMENT_PROFILE_NOT_FOUND
PLACEMENT_POSITION_NOT_FOUND
IK_FAILED
GRASP_FAILED
GRASP_VERIFICATION_UNAVAILABLE
PLACE_FAILED
```

`error_message`에는 사람이 이해할 수 있는 안전한 설명만 포함한다. Python stack trace, API key, 내부 파일 경로, ROS 객체 주소는 포함하지 않는다.

---

## 11. LLM 생성 코드 작성 규칙

1. 모든 로봇 호출은 `robot.<FUNCTION_NAME>(...)` 형태로 작성한다.
2. 비동기 함수 반환값은 항상 `ActionHandle` 변수에 저장한다.
3. 다음 동작이 앞 동작 완료에 의존하면 `WAIT_ACTION`으로 terminal 상태를 확인한다.
4. 성공은 `result.state == ActionState.SUCCEEDED`로만 판단한다.
5. `WAIT_SECOND`가 끝났다는 사실을 액션 완료로 해석하지 않는다.
6. `WAIT_RESOURCE` 성공을 자원 예약 또는 다음 액션 성공으로 해석하지 않는다.
7. `CHECK_ACTION`은 순간 snapshot이며 반환 직후 바뀔 수 있음을 고려한다.
8. raw 물체 문자열 대신 `ObjectId` canonical enum을 사용한다.
9. `GET_OBJECT_STATE(VISIBLE)`을 정렬 완료나 파지 가능으로 해석하지 않는다.
10. `GET_ROBOT_POS` 값은 실제 센서 측정값이라고 표현하지 않는다.
11. `GET_ROBOT_POS` 값을 사용할 때 관련 `EstimateState`를 먼저 확인한다.
12. 차체 motion 두 개 또는 상충 자원을 요구하는 motion을 임의로 동시에 시작하지 않는다.
13. `SET_ARM_JOINTS`와 `SET_GRIPPER`의 성공을 실제 encoder 도달 또는 파지 성공으로 확대 해석하지 않는다.
14. `SAVE_ARM_PRIMITIVE`에는 그리퍼가 저장된다고 가정하지 않는다.
15. `SET_ARM_PRIMITIVE`는 그리퍼 상태를 바꾸지 않는다고 가정한다.
16. `PICK_OBJECT`와 `PLACE_NEXTTO_OBJECT`는 필요한 ALIGN을 내부에서 수행하므로 불필요한 중복 정렬을 만들지 않는다.
17. `PICK_OBJECT` 성공을 검증 source가 보장하는 수준 이상으로 설명하지 않는다.
18. `STOP` 호출 후 동일 run에서 새로운 motion을 시작하지 않는다.
19. 사용자 명령에 명확히 포함되지 않은 자동 재시도는 생성하지 않는다.
20. `try-except`, direct sleep, busy polling, 무제한 while, 임의 import를 생성하지 않는다.

---

## 12. 대표 예제

### 12.1 전진 후 좌회전

```python
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
```

### 12.2 위치 저장 후 복귀

```python
def main() -> TaskOutcome:
    saved = robot.SAVE_POS(position_id="start_position")
    if not saved.success:
        return TaskOutcome(TaskStatus.FAILED, saved.error_message or "위치 저장에 실패했습니다.")

    move = robot.MOVE_BASE(distance_m=0.30)
    move_result = robot.WAIT_ACTION(move, timeout_s=12.0)
    if move_result.state != ActionState.SUCCEEDED:
        return TaskOutcome(TaskStatus.FAILED, move_result.error_message or "이동에 실패했습니다.")

    go_back = robot.MOVE_BASE_TO_POS(position_id="start_position")
    back_result = robot.WAIT_ACTION(go_back, timeout_s=30.0)
    if back_result.state != ActionState.SUCCEEDED:
        return TaskOutcome(
            TaskStatus.PARTIALLY_SUCCEEDED,
            back_result.error_message or "이동은 완료했지만 복귀하지 못했습니다.",
        )

    return TaskOutcome(TaskStatus.SUCCEEDED, "저장한 추정 위치와 방향으로 복귀했습니다.")
```

### 12.3 팔 관절 이동 후 그리퍼 닫기

```python
def main() -> TaskOutcome:
    arm = robot.SET_ARM_JOINTS(
        arm_lift_deg=20.0,
        wrist_pitch_deg=-15.0,
    )
    arm_result = robot.WAIT_ACTION(arm, timeout_s=12.0)

    if arm_result.state != ActionState.SUCCEEDED:
        return TaskOutcome(TaskStatus.FAILED, arm_result.error_message or "팔 이동에 실패했습니다.")

    gripper = robot.SET_GRIPPER(gripper_deg=60.0)
    gripper_result = robot.WAIT_ACTION(gripper, timeout_s=6.0)

    if gripper_result.state != ActionState.SUCCEEDED:
        return TaskOutcome(
            TaskStatus.PARTIALLY_SUCCEEDED,
            gripper_result.error_message or "팔은 이동했지만 그리퍼 동작에 실패했습니다.",
        )

    return TaskOutcome(TaskStatus.SUCCEEDED, "요청한 팔과 그리퍼 명령을 완료했습니다.")
```

### 12.4 팔 primitive 저장 및 실행

```python
def main() -> TaskOutcome:
    saved = robot.SAVE_ARM_PRIMITIVE(
        primitive_id="user_pose_1",
        overwrite=False,
    )

    if not saved.success:
        return TaskOutcome(TaskStatus.FAILED, saved.error_message or "팔 자세 저장에 실패했습니다.")

    move = robot.SET_ARM_PRIMITIVE(primitive_id="user_pose_1")
    move_result = robot.WAIT_ACTION(move, timeout_s=12.0)

    if move_result.state != ActionState.SUCCEEDED:
        return TaskOutcome(TaskStatus.FAILED, move_result.error_message or "저장 자세 실행에 실패했습니다.")

    return TaskOutcome(
        TaskStatus.SUCCEEDED,
        "팔 primitive를 저장하고 실행했습니다. 그리퍼 상태는 primitive에 포함되지 않았습니다.",
    )
```

### 12.5 물체 상태 확인 후 파지

```python
def main() -> TaskOutcome:
    state = robot.GET_OBJECT_STATE(object_id=ObjectId.BUDS3)

    if state.state != ObjectState.VISIBLE:
        return TaskOutcome(
            TaskStatus.FAILED,
            state.error_message or "현재 Buds3를 최신 인식 결과에서 확인하지 못했습니다.",
        )

    pick = robot.PICK_OBJECT(object_id=ObjectId.BUDS3)
    pick_result = robot.WAIT_ACTION(pick, timeout_s=45.0)

    if pick_result.state != ActionState.SUCCEEDED:
        return TaskOutcome(TaskStatus.FAILED, pick_result.error_message or "Buds3 파지에 실패했습니다.")

    return TaskOutcome(TaskStatus.SUCCEEDED, "Buds3 파지 절차를 완료했습니다.")
```

`PICK_OBJECT`는 내부에서 물체를 다시 확인하고 필요 시 ALIGN을 수행하므로 사전 `GET_OBJECT_STATE`는 사용자 명령의 조건 분기를 표현할 때만 필요하다.

### 12.6 현재 보유 물체를 기준 물체 옆에 배치

```python
def main() -> TaskOutcome:
    place = robot.PLACE_NEXTTO_OBJECT(
        reference_object_id=ObjectId.CUP,
    )
    place_result = robot.WAIT_ACTION(place, timeout_s=45.0)

    if place_result.state != ActionState.SUCCEEDED:
        return TaskOutcome(
            TaskStatus.FAILED,
            place_result.error_message or "기준 물체 옆 배치에 실패했습니다.",
        )

    return TaskOutcome(
        TaskStatus.SUCCEEDED,
        "현재 보유 물체를 기준 물체 옆에 배치했습니다.",
    )
```

### 12.7 전체 동작 정지

```python
def main() -> TaskOutcome:
    stopped = robot.STOP()

    if not stopped.success:
        return TaskOutcome(
            TaskStatus.FAILED,
            stopped.error_message or "안전한 정지를 확인하지 못했습니다.",
        )

    return TaskOutcome(TaskStatus.CANCELED, "현재 로봇 동작을 정지했습니다.")
```

---

## 13. 기계 판독용 registry 초안

아래 YAML을 LLM prompt, AST validator, runtime argument validator, 개발자 문서의 단일 원본으로 발전시킨다.

```yaml
api:
  name: macrobot_llm_robot_api
  version: 0.2.0
  facade: robot
  entrypoint: main
  entrypoint_return: TaskOutcome

conventions:
  distance_unit: meter
  angle_unit: degree
  time_unit: second
  timestamp_unit: unix_ms
  duration_clock: monotonic
  positive_linear_direction: forward
  positive_angular_direction: counterclockwise
  try_except_allowed: false
  direct_import_allowed: false
  direct_sleep_allowed: false
  speed_argument_exposed: false

resources:
  BASE_MOTION: {waitable: true}
  ARM_MOTION: {waitable: true}
  GRIPPER_MOTION: {waitable: true}
  PICO_MOTION: {waitable: true}
  POSITION_STORE: {waitable: false}
  ARM_PRIMITIVE_STORE: {waitable: false}

run_limits:
  max_wall_time_s_from_config: run_limits.max_wall_time_s
  max_internal_motion_steps_from_config: run_limits.max_internal_motion_steps_per_run

functions:
  WAIT_SECOND:
    block: control
    mode: sync
    returns: OperationResult
    arguments:
      seconds: {type: float, finite: true, min_exclusive: 0.0, max_from_config: control_limits.max_wait_seconds_per_call}

  WAIT_ACTION:
    block: control
    mode: sync
    returns: ActionResult
    cancel_on_timeout: true
    arguments:
      action: {type: ActionHandle, current_run_only: true}
      timeout_s: {type: float, finite: true, min_exclusive: 0.0, max_from_config: control_limits.max_wait_action_timeout_s}

  WAIT_RESOURCE:
    block: control
    mode: sync
    returns: OperationResult
    reserves_resource: false
    arguments:
      resource_id: {type: ResourceId, waitable_only: true}
      timeout_s: {type: float, finite: true, min_exclusive: 0.0, max_from_config: control_limits.max_wait_resource_timeout_s}

  CHECK_ACTION:
    block: control
    mode: sync
    returns: ActionResult
    arguments:
      action: {type: ActionHandle, current_run_only: true}

  CANCEL_ACTION:
    block: control
    mode: sync
    returns: ActionResult
    priority: control
    arguments:
      action: {type: ActionHandle, current_run_only: true}

  CANCEL_ALL:
    block: control
    mode: sync
    returns: OperationResult
    priority: control
    scope: current_run

  STOP:
    block: control
    mode: sync
    returns: OperationResult
    priority: highest
    scope: system_motion
    bypasses_motion_budget: true
    blocks_new_motion_in_current_run: true
    gripper_behavior: hold_current_command

  GET_OBJECT_STATE:
    block: control
    mode: sync
    returns: ObjectStateResult
    arguments:
      object_id: {type: ObjectId, canonical_only: true}

  GET_ROBOT_POS:
    block: control
    mode: sync
    returns: RobotPosResult
    base_source: command_history
    arm_source: commanded_state
    gripper_source: commanded_state

  MOVE_BASE:
    block: base_drive
    mode: async
    returns: ActionHandle
    cancellable: true
    resources: {exclusive: [BASE_MOTION, PICO_MOTION]}
    arguments:
      distance_m: {type: float, finite: true, nonzero: true, max_abs_from_config: base_limits.max_move_distance_m_per_call}
    internal_motion_step_limit: 1

  TURN_BASE:
    block: base_drive
    mode: async
    returns: ActionHandle
    cancellable: true
    resources: {exclusive: [BASE_MOTION, PICO_MOTION]}
    arguments:
      angle_deg: {type: float, finite: true, nonzero: true, max_abs_from_config: base_limits.max_turn_angle_deg_per_call}
    internal_motion_step_limit: 1

  SAVE_POS:
    block: base_drive
    mode: sync
    returns: OperationResult
    resources: {exclusive: [POSITION_STORE], requires_idle: [BASE_MOTION]}
    persistence: system_session
    arguments:
      position_id: {type: str, regex: '^[a-z][a-z0-9_]{0,31}$'}
      overwrite: {type: bool, default: false}

  MOVE_BASE_TO_POS:
    block: base_drive
    mode: async
    returns: ActionHandle
    cancellable: true
    resources: {exclusive: [BASE_MOTION, PICO_MOTION], read: [POSITION_STORE]}
    restore_heading: true
    obstacle_avoidance: false
    internal_motion_step_limit: 3
    arguments:
      position_id: {type: str, regex: '^[a-z][a-z0-9_]{0,31}$'}

  ALIGN_WITH_OBJECT:
    block: base_drive
    mode: async
    returns: ActionHandle
    cancellable: true
    resources: {exclusive: [BASE_MOTION, PICO_MOTION]}
    arguments:
      object_id: {type: ObjectId, canonical_only: true}
    includes: [object_confirmation, rotational_alignment, distance_adjustment, graspable_region_confirmation]
    excludes: [arm_motion, gripper_motion, object_pick]
    internal_motion_step_limit_from_config: alignment.max_motion_steps_per_call

  SET_ARM_JOINTS:
    block: arm_gripper
    mode: async
    returns: ActionHandle
    cancellable: true
    resources: {exclusive: [ARM_MOTION, PICO_MOTION]}
    preserves: [gripper_deg]
    arguments:
      arm_lift_deg: {type: float, finite: true, range_from_config: arm_limits.arm_lift_deg}
      wrist_pitch_deg: {type: float, finite: true, range_from_config: arm_limits.wrist_pitch_deg}
    requires_safe_path: true
    internal_motion_step_limit: 1

  SET_GRIPPER:
    block: arm_gripper
    mode: async
    returns: ActionHandle
    cancellable: true
    resources: {exclusive: [GRIPPER_MOTION, PICO_MOTION]}
    preserves: [arm_lift_deg, wrist_pitch_deg]
    arguments:
      gripper_deg: {type: float, finite: true, range_from_config: gripper_limits.logical_deg}
    internal_motion_step_limit: 1

  SAVE_ARM_PRIMITIVE:
    block: arm_gripper
    mode: sync
    returns: OperationResult
    resources: {exclusive: [ARM_PRIMITIVE_STORE], requires_idle: [ARM_MOTION]}
    stores: [arm_lift_deg, wrist_pitch_deg]
    excludes: [gripper_deg]
    persistence: system_session
    arguments:
      primitive_id: {type: str, regex: '^[a-z][a-z0-9_]{0,31}$'}
      overwrite: {type: bool, default: false, session_primitives_only: true}

  SET_ARM_PRIMITIVE:
    block: arm_gripper
    mode: async
    returns: ActionHandle
    cancellable: true
    resources: {exclusive: [ARM_MOTION, PICO_MOTION], read: [ARM_PRIMITIVE_STORE]}
    preserves: [gripper_deg]
    arguments:
      primitive_id: {type: str, regex: '^[a-z][a-z0-9_]{0,31}$'}
    requires_safe_path: true
    internal_motion_step_limit: 1

  PICK_OBJECT:
    block: arm_gripper
    mode: async
    returns: ActionHandle
    cancellable: true
    resources: {exclusive: [BASE_MOTION, ARM_MOTION, GRIPPER_MOTION, PICO_MOTION]}
    arguments:
      object_id: {type: ObjectId, canonical_only: true}
    includes: [object_confirmation, align_if_needed, reachability_check, grasp, verification, post_grasp]
    internal_motion_step_limit_from_config: manipulation.pick_max_motion_steps_per_call

  PLACE_NEXTTO_OBJECT:
    block: arm_gripper
    mode: async
    returns: ActionHandle
    cancellable: true
    resources: {exclusive: [BASE_MOTION, ARM_MOTION, GRIPPER_MOTION, PICO_MOTION]}
    arguments:
      reference_object_id: {type: ObjectId, canonical_only: true}
    requires_held_object: true
    includes: [reference_confirmation, align_if_needed, placement_candidate_selection, place, release, post_place]
    internal_motion_step_limit_from_config: manipulation.place_max_motion_steps_per_call
```

---

## 14. 설정값과 미확정 항목

하드웨어·통합 테스트 후 다음 값을 확정한다.

```yaml
run_limits:
  max_wall_time_s: TBD
  max_internal_motion_steps_per_run: TBD

control_limits:
  max_wait_seconds_per_call: TBD
  max_wait_action_timeout_s: TBD
  max_wait_resource_timeout_s: TBD

control_timeouts:
  cancel_action_s: TBD
  cancel_all_s: TBD
  stop_s: TBD

base_limits:
  max_move_distance_m_per_call: TBD
  max_turn_angle_deg_per_call: TBD

base_timeouts:
  move_base_s: TBD
  turn_base_s: TBD
  move_base_to_pos_s: TBD

alignment:
  max_motion_steps_per_call: TBD
  hard_timeout_s: TBD
  angular_tolerance_deg: TBD
  graspable_distance_min_m: TBD
  graspable_distance_max_m: TBD

arm_limits:
  arm_lift_deg: TBD
  wrist_pitch_deg: TBD

arm_timeouts:
  set_arm_joints_s: TBD
  set_arm_primitive_s: TBD

gripper_limits:
  logical_deg: TBD

gripper_timeouts:
  set_gripper_s: TBD

manipulation:
  pick_max_motion_steps_per_call: TBD
  place_max_motion_steps_per_call: TBD
  pick_hard_timeout_s: TBD
  place_hard_timeout_s: TBD
  grasp_verification_policy: TBD
  placement_verification_policy: TBD

perception:
  object_state_max_age_ms: TBD

robot_state:
  base_state_max_age_ms: TBD
  arm_state_max_age_ms: TBD
  gripper_state_max_age_ms: TBD
```

추가 결정이 필요한 정책:

- 사용자 저장 primitive를 향후 재부팅 후에도 영구 보존할지
- 시스템 primitive ID와 목록
- 물체별 grasp/placement profile schema
- 파지·배치 성공을 확인할 센서 또는 카메라 기준
- held-object state의 `known / unknown / empty` 상세 enum
- 함수별 `ActionResult.payload` 구조

---

## 15. 현 프로젝트 코드와의 구현 정합성 메모

1. 현재 `primitive_executor_node.py`는 primitive의 `target_q`를 세 값으로 읽어 `arm_lift_joint`, `wrist_pitch_joint`, `gripper_joint`를 함께 publish한다. 본 통합 API의 primitive 계약은 **팔 두 관절만 저장·실행하고 그리퍼를 유지**하는 것이므로 adapter 또는 commissioning report schema 수정이 필요하다.
2. `SET_ARM_JOINTS`는 현재 gripper logical state를 보존하고, `SET_GRIPPER`는 현재 두 arm logical state를 보존해야 한다. 현재 하위 bridge가 세 관절을 한 명령으로 요구한다면 Gateway가 완전한 goal을 구성한다.
3. 현재 팔·그리퍼 state가 commanded state 기반이면 `SUCCEEDED`를 실제 encoder 도달 또는 실제 물체 파지로 표현하면 안 된다.
4. `PICK_OBJECT`와 `PLACE_NEXTTO_OBJECT`는 필요한 물체 확인과 `ALIGN_WITH_OBJECT` 기능을 내부에서 실행한다. 외부 코드가 반드시 별도 ALIGN을 선행해야 하는 계약으로 만들지 않는다.
5. 차체·팔·그리퍼가 동일한 Pico motion channel을 공유하면 `PICO_MOTION` 배타 자원이 실제 동시 명령을 차단해야 한다.
6. 함수명은 본 문서의 canonical spelling을 그대로 사용한다. 특히 `CANCEL_ACTION`, `CANCEL_ALL`, `PLACE_NEXTTO_OBJECT`의 철자를 prompt, registry, validator, runtime에서 동일하게 유지한다.

---

## 변경 이력

| 버전 | 날짜 | 변경 사항 |
|---|---|---|
| v0.1 | 2026-08-10 | 차체 구동 블록 및 제어 블록 개별 사양 작성 |
| v0.2 | 2026-08-10 | 두 문서 통합, 생성 코드 공통 계약 정리, 팔·그리퍼 블록 6개 함수 추가, PICK/PLACE 내부 ALIGN 명시 |
