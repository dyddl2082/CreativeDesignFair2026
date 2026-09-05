# MacRobot 재부팅 복원·시각 재탐색·비동기 인식·놓기 설계

## 적용 범위

이 변경은 URDF, MoveIt SRDF, 관절축과 collision mesh를 수정하지 않는다. 현재 로봇팔 모델이 확정되기 전까지 인식, 작업 orchestration, 메모리와 Gateway 계층만 변경한다.

## 1. 위치와 작업 기술의 분리

기존 stored-object profile에는 다음 성격이 다른 정보가 함께 존재했다.

- wheel/Pico odometry에서 얻은 물체 위치: 현재 주행 세션에 종속
- DINO 등록 데이터와 grasp keyframe: 재부팅 후에도 재사용 가능한 작업 기술

새 구조는 위치를 `~/MacRobot/data/object_memory/memory.yaml`에 별도로 기록하며, 각 위치에 Linux boot ID와 가능한 경우 Pico boot/uptime 정보를 붙인다. host 또는 Pico epoch가 달라지면 좌표를 삭제하지는 않지만 `stale`로 분류하고 자동 이동에 사용하지 않는다. 반면 DINO reference bank와 `~/MacRobot/data/grasp_keyframes/profiles.yaml`은 그대로 유지한다.

```text
재부팅 전: location=fresh, skill=valid
재부팅 후: location=stale, skill=valid
실행 방법: 현재 카메라에서 다시 찾고 같은 상대 keyframe으로 파지
```

## 2. 로봇 컨셉

수정 후 컨셉은 “저장된 좌표로 가서 물체를 확인하는 로봇”이 아니라 다음과 같다.

> 등록된 물체의 시각적 특징과 물체 상대 파지 기술을 기억하고, 현재 카메라 관측을 이용해 물체의 새 위치를 찾아 접근하는 로봇

저장 위치는 같은 부팅 세션에서 최근에 관측된 경우에만 한 번의 작은 카메라 방향 힌트로 사용한다. 해당 방향에서 물체가 확인되지 않아도 좌표를 진실로 가정하지 않고 일반 시각 탐색을 계속한다.

## 3. 저회전 시각 탐색

탐색 우선순위는 다음과 같다.

1. 현재 정지 화면 관측
2. aligned depth가 확보된 경우에만 8 cm 단위의 짧은 전진 probe
3. 실제로 전진한 거리만 같은 corridor로 후진
4. 10도 이하의 연속적인 카메라 시야 sweep

기존처럼 `+30 -> -30`과 같이 큰 상대 회전을 반복하지 않는다. `0 -> +10 -> +20 -> +30 -> +20 -> +10 -> 0 -> -10 ...` 방식으로 한 번의 명령 회전량을 제한한다. 회전은 정확한 pose 측정이 아니라 카메라 시야를 바꾸는 수단으로만 사용한다.

## 4. 주행 중 비동기 인식

### WSL2/XPU

- 처리 대기열은 오래된 FIFO가 아니라 `latest_frame` 정책을 사용한다.
- 새 카메라 frame이 들어오면 아직 시작하지 않은 이전 frame은 제거한다.
- 최신 frame의 후보가 queue 용량보다 많으면 filter score 상위 후보를 보존한다.
- 입력이 너무 오래되었으면 DINO 추론 전에 폐기한다.

### Raspberry Pi/task node

차체가 4 cm 또는 4도 단위의 짧은 동작을 수행하는 동안에도 finder와 DINO 파이프라인을 중지하지 않는다. 양성 결과가 동작 완료 후 도착하면 다음과 같이 처리한다.

```text
물체 point_base @ camera capture time
-> capture-time base pose를 이용해 point_odom 계산
-> 현재 base pose로 다시 point_base 변환
-> 다음 짧은 이동 목표 재계산
```

따라서 짧은 동작은 중간에 끊지 않지만, 긴 탐색·접근 작업은 각 동작 경계에서 늦게 도착한 결과에 따라 목적지가 바뀐다.

## 5. 바닥에 따른 회전 오차 완화

- 회전 명령을 4도 단위로 제한한다.
- 회전 완료 후 wheel odometry만으로 직진하지 않는다.
- 새로운 시각 관측이 들어오기 전에는 다음 translation을 금지한다.
- 직선 이동도 4 cm 단위로 나누어 매 구간 후 목표를 다시 계산한다.
- 물체가 근거리이고 최근 시각 관측이 있을 때만 최대 10 cm의 translation-only dead reckoning을 허용한다.

이 정책은 회전 calibration을 없애지는 않지만, 회전 오차가 여러 단계의 위치 추정에 누적되는 것을 막는다.

## 6. PLACE: semantic PICK의 안전한 역과정

PLACE는 기록된 관절각을 단순히 반대 순서로 재생하지 않는다. 기준 물체를 현재 카메라로 찾고, 그 위치에 offset을 적용해 새 배치점을 만든 뒤 보유 물체의 Cartesian grasp keyframe을 재계산한다.

```text
PLACE_ABOVE
- LIFT의 물체 상대 offset
- gripper closed

PLACE_DESCEND
- GRASP_OPEN의 물체 상대 offset
- gripper closed

PLACE_RELEASE
- 같은 arm pose
- gripper open

PLACE_RETREAT
- PRE_GRASP의 물체 상대 offset
- gripper open
```

모든 단계와 단계 사이 interpolation이 기존 safe-region을 통과한 경우에만 실행한다. 기준 물체 옆 offset은 기본 12 cm이며, 8~25 cm의 수평 범위와 5 cm 이하의 수직 차이만 허용한다.

## 7. 안전하게 남겨 둔 한계

- 로컬 depth gate는 전방의 짧은 이동을 허용할지 판단할 뿐, Nav2 수준의 장애물 경로 계획이 아니다.
- 안정적인 global frame 없이 임의의 방 전체에서 옮겨진 물체를 반드시 찾을 수는 없다. 범위를 넓히려면 기존 카메라로 인식하는 home landmark/dock, AprilTag 또는 visual SLAM이 필요하다.
- wheel odometry는 동일 boot/session 안에서 지연 결과를 보정하는 데만 사용한다.
- 재부팅 후 실제 보유 물체 여부는 센서로 증명할 수 없어 `unknown`이 되며 운영자 확인이 필요하다.
- PLACE 성공은 안전한 command sequence 완료이며, 힘·전류 센서가 없으면 실제 release를 직접 검증하지 못한다.
