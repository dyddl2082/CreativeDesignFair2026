# macrobot_pick_pipeline 0.8.0

MacRobot의 물체 탐색·정렬·파지·놓기를 **시각 재탐색 중심**으로 실행한다. 기존 공개 토픽과 저장 프로필 형식은 유지하되, 저장된 odometry 좌표를 영구 위치로 취급하지 않는다.

## 핵심 정책

```text
영구 저장
- 물체 ID와 DINO 등록 데이터
- 물체 상대 grasp keyframe/profile: 잡는 방법

현재 부팅 세션에서만 유효
- wheel/Pico odometry 기반 마지막 관측 위치
- 이동 중 계산한 물체 위치와 차체 pose history
```

호스트 또는 Pico 세션이 바뀌면 위치 힌트는 `stale`로 분류되지만, 물체 인식 데이터와 grasp keyframe은 삭제하지 않는다. 실행은 현재 카메라 화면부터 다시 시작한다.

## 새 실행 흐름

```text
현재 화면 관측
→ depth-clearance가 확보된 짧은 직선 탐색
→ 작은 각도의 연속 시야 sweep
→ DINO 결과가 늦게 도착하면 촬영 시점 pose에서 현재 pose로 보정
→ 4 cm 이동 또는 4° 회전 단위로 재계획
→ semantic PICK 또는 PLACE preflight
→ validator / safe-region / servo bridge
```

회전 결과만으로 다음 직진을 허가하지 않는다. 회전 후에는 새로운 카메라 위치가 들어와야 접근을 계속한다.

## 실행

```bash
SAFE_CSV=$HOME/MacRobot/data/safe_region_collision_v2_fine/safe_connected_samples.csv

ros2 launch macrobot_pick_pipeline pick_pipeline_robot.launch.py \
  safe_region_csv:="$SAFE_CSV" \
  start_pico_debug:=true \
  start_base_alignment:=true \
  start_grasp_keyframes:=true \
  task_executable:=resilient_object_task_node
```

기존 동작으로 임시 rollback할 때만 다음을 사용한다.

```bash
ros2 launch macrobot_pick_pipeline pick_pipeline_robot.launch.py \
  safe_region_csv:="$SAFE_CSV" \
  task_executable:=stored_object_pick_node
```

## 찾기와 파지

```bash
ros2 run macrobot_pick_pipeline stored_object_pick_cli \
  run Eraser --profile Eraser --timeout 180
```

물체를 옮긴 뒤에도 같은 명령을 사용한다. 같은 세션의 마지막 위치는 작은 시야 방향 힌트로만 쓰고, 실제 목표는 현재 카메라 관측으로 다시 결정한다.

## 위치 메모리 확인

```bash
ros2 run macrobot_pick_pipeline stored_object_pick_cli memory
ros2 run macrobot_pick_pipeline stored_object_pick_cli forget-location Eraser
```

## 놓기

```bash
ros2 run macrobot_pick_pipeline stored_object_pick_cli \
  place Cup --offset-base 0.0 0.12 0.0 --timeout 180
```

PLACE는 관절값을 단순 역재생하지 않는다.

```text
PLACE_ABOVE   = LIFT 상대 자세를 새 배치점에서 IK로 재계산, gripper closed
PLACE_DESCEND = GRASP_OPEN 상대 자세를 새 배치점에서 재계산, gripper closed
PLACE_RELEASE = 같은 자세에서 gripper open
PLACE_RETREAT = PRE_GRASP 상대 자세로 후퇴
```

네 단계 전체가 safe-region preflight를 통과해야 첫 동작을 시작한다.

## 재부팅 후 보유 물체

로봇이나 제어 프로세스가 재시작되면 센서 피드백만으로 실제 보유 여부를 증명할 수 없으므로 상태를 `unknown`으로 바꾼다. 실제로 물체를 들고 있는 경우에만 운영자가 확인한다.

```bash
ros2 run macrobot_pick_pipeline stored_object_pick_cli \
  confirm-held Eraser Eraser
```

그리퍼가 비어 있으면 다음을 사용한다.

```bash
ros2 run macrobot_pick_pipeline stored_object_pick_cli clear-held
```

## 안전 범위

- depth clearance는 짧은 전진 probe를 막는 보수적 gate이며 완전한 장애물 회피기가 아니다.
- 임의의 방 전체에서 물체를 반드시 찾는 기능은 아니다. 현재 시야와 제한된 로컬 탐색 범위를 벗어나면 시각 landmark, dock 또는 SLAM이 필요하다.
- PLACE 성공은 안전한 명령 시퀀스 완료를 뜻한다. 힘·전류 센서가 없으므로 실제 보유·방출 여부를 직접 증명하지 않는다.
- URDF, 관절축 또는 collision mesh가 바뀌면 기존 safe-region과 keyframe을 다시 생성해야 한다.
