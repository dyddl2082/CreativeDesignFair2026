# macrobot_pick_pipeline 0.5.0

MacRobot의 D435 기반 물체 위치 추정, 저장 위치 기반 차체 복귀·탐색, 카메라 폐루프 정렬, 검증된 로봇팔 동작 기록·재생을 연결한다.

## 이번 버전의 핵심

```text
물체 등록 시
  Pico encoder odom의 차체 pose
  + base_link 기준 물체 3D 점
  + 잡기 가능한 camera-relative 기준점
  + arm_demo trajectory 이름
을 함께 기록

정식 실행 시
  저장 pose 근처로 encoder odom 기반 coarse return
  → 저장 방향 주변 bounded finder scan
  → live object point를 저장 camera-relative 점에 맞춤
  → 기록한 arm trajectory 재생
```

차체 odometry는 약 1% 오차와 무한궤도 회전 drift가 있으므로 최종 정렬 근거로 사용하지 않는다. 저장 위치는 탐색 시작점을 좁히는 coarse 정보이며, 마지막 자세는 항상 카메라 재검출과 visual alignment로 보정한다.

## 새 실행 파일

```text
stored_object_pick_node
visible_pick_test_node
stored_object_pick_cli
```

기존 호환 이름도 유지한다.

```text
base_alignment_node → stored_object_pick_node alias
```

기존 Robot Action Gateway가 사용하는 다음 토픽도 그대로 지원한다.

```text
/macrobot/align_pick/goal
/macrobot/base_alignment/cancel
/macrobot/base_alignment/status
/macrobot/base_alignment/result
```

## 새 공개 토픽

```text
/macrobot/stored_pick/record   std_msgs/String JSON
/macrobot/stored_pick/goal     std_msgs/String JSON
/macrobot/stored_pick/cancel   std_msgs/String
/macrobot/stored_pick/admin    std_msgs/String JSON
/macrobot/stored_pick/status   std_msgs/String JSON
/macrobot/stored_pick/result   std_msgs/String JSON

/macrobot/visible_pick_test/goal
/macrobot/visible_pick_test/cancel
/macrobot/visible_pick_test/status
/macrobot/visible_pick_test/result
```

## 필요한 기존 노드

```text
Pi
- pico_debug_node
- macrobot_arm_control arm pipeline
- detection_localizer_node
- stored_object_pick_node
- arm_demo_recorder_node

WSL2
- candidate_filter_node
- embedding_retrieval_node
- temporal_confirmation_node
- macrobot_object_finder
```

전체 RGB/depth/point cloud를 WSL2 RViz로 보내지 않는다. 기존처럼 Pi에서 후보 crop만 생성하여 WSL2 인식 노드로 전달한다.

## 필수 사전 작업

1. `arm_demo_cli`로 고정 배치에서 실제 잡기 trajectory를 기록한다.
2. 물체와 차체를 잡기 좋은 위치에 둔다.
3. finder/localizer가 해당 물체의 stable 3D 점을 발행하는 상태에서 object profile을 기록한다.
4. visible test로 align + recorded grasp를 검증한다.
5. step-mode teleop으로 차체를 이동한다.
6. full mode로 저장 위치 복귀 → finder → align → grasp를 검증한다.

## 실행

```bash
SAFE_CSV=$HOME/MacRobot/data/safe_region_collision_v2_fine/safe_connected_samples.csv

ros2 launch macrobot_pick_pipeline pick_pipeline_robot.launch.py \
  safe_region_csv:="$SAFE_CSV" \
  start_pico_debug:=true \
  serial_port:=/dev/ttyACM0 \
  start_base_alignment:=true \
  start_visible_pick_test:=true \
  start_arm_demo_recorder:=true \
  start_camera_teach:=false
```

Object finder는 WSL2에서 별도로 실행한다.

```bash
source ~/MacRobot/.venv-embedding/bin/activate
source /opt/ros/jazzy/setup.bash
source ~/MacRobot/install/setup.bash

ros2 launch macrobot_object_finder object_finder_wsl.launch.py
```

## 잡기 trajectory 기록

```bash
ros2 run macrobot_pick_pipeline arm_demo_cli
```

메뉴 4로 사용자가 jog하면서 전체 동작을 기록한다. 예:

```text
Buds3_FIXED_PICK_V1
```

저장 파일:

```text
~/MacRobot/data/arm_primitives/Buds3_FIXED_PICK_V1.yaml
```

## 물체 runtime profile 기록

```bash
ros2 run macrobot_pick_pipeline stored_object_pick_cli \
  record Buds3 \
  --profile Buds3 \
  --grasp-trajectory Buds3_FIXED_PICK_V1
```

기록되는 값:

```text
- 현재 Pico encoder odom pose
- 현재 base_link 기준 stable object point
- odom frame으로 변환한 object point
- 해당 camera-relative point를 재현할 alignment 기준
- arm demo trajectory 이름
```

저장 파일:

```text
~/MacRobot/data/stored_objects/runtime_profiles.yaml
```

이 YAML은 현재 runtime adapter다. 팀원이 정의하는 최종 물체 구조체와는 별개이며 이후 adapter를 교체할 수 있다.

## 이미 찾은 상태의 동적 테스트

finder가 continuous tracking 중이고 `/macrobot/perception/localized_detection`이 최근 값을 내는 상태에서:

```bash
ros2 run macrobot_pick_pipeline stored_object_pick_cli \
  visible-test Buds3 \
  --profile Buds3
```

흐름:

```text
latest localized detection 확인
→ coarse odom 복귀 생략
→ live visual alignment
→ Buds3_FIXED_PICK_V1 재생
```

정렬만 시험:

```bash
ros2 run macrobot_pick_pipeline stored_object_pick_cli \
  visible-test Buds3 \
  --profile Buds3 \
  --align-only
```

## teleop 이동 후 정식 실행

teleop은 반드시 encoder-bounded step mode를 사용한다. `MOTOR` velocity mode는 odometry를 unreliable로 만들 수 있어 full mode가 안전하게 거부한다.

이동이 끝난 뒤:

```bash
ros2 run macrobot_pick_pipeline stored_object_pick_cli \
  run Buds3 \
  --profile Buds3
```

흐름:

```text
ODOM? 확인
→ 기록 search pose로 turn / move / turn
→ finder 시작
→ 기록 방향 주변 bounded yaw scan
→ 물체 검출
→ camera-relative visual alignment
→ recorded arm trajectory
```

## 취소

```bash
ros2 run macrobot_pick_pipeline stored_object_pick_cli cancel
```

또는:

```bash
ros2 topic pub --once \
  /macrobot/stored_pick/cancel \
  std_msgs/msg/String \
  "{data: 'user_cancel'}"
```

취소 상태 전이:

```text
RUNNING
→ CANCEL_REQUESTED
→ base STOP / arm trajectory stop / finder cancel
→ 정지 확인
→ CANCELED
```

결과의 `partial_state`에는 마지막 odometry, object point, current_q, base motion response가 포함된다. 부분 이동 후 odometry의 `reliable=false`도 그대로 보존한다.

## 중요한 제한

- 저장 위치는 `pico_odom_session` 범위다.
- profile 기록 뒤 Pico를 재부팅하거나 `RESET_ODOM`하면 full mode의 위치 의미가 사라진다.
- 장기·재부팅 간 persistent 위치에는 SLAM, AprilTag, 외부 map localization 같은 절대 기준이 필요하다.
- encoder odom은 coarse search용이며 최종 파지 자세의 근거가 아니다.
- 실제 arm joint encoder가 없으므로 arm 완료는 validated commanded trajectory 완료를 의미한다.
- recorded grasp 재생 중 취소해도 그리퍼를 자동으로 열지 않는다.

상세 문서:

```text
docs/STORED_OBJECT_PICK_KO.md
docs/CANCELLATION_CONTRACT_KO.md
docs/TEAM_GATEWAY_MAPPING_KO.md
docs/TEST_PROCEDURE_KO.md
```
