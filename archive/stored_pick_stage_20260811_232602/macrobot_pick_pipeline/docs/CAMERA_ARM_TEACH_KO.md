# 카메라–로봇팔 Teach & Record

## 1. 변경 목적

기존 `macrobot_arm_commissioning`의 메뉴 5~7을 카메라–로봇팔 통합 계층으로 이동한다.

```text
기존 메뉴 5: 실제 grasp_frame 보정
기존 메뉴 6: 기본 primitive 정의·시험
기존 메뉴 7: 물체별 grasp profile 기록
```

이제 위 세 기능은 `macrobot_pick_pipeline`의 다음 노드가 담당한다.

```text
pick_teach_node
pick_teach_cli
```

메뉴 1~4는 기존 commissioning 패키지에 그대로 남긴다.

## 2. 왜 카메라 통합 계층에서 기록하는가

기존 메뉴 5~7은 사용자가 X/Z 위치와 q값을 수동으로 입력했다. 새 구조에서는 카메라가 고정한 `base_link` 기준 물체 3D 위치와 현재 동적 `grasp_frame` 위치를 동시에 기록한다.

따라서 물체별 profile에는 단순 joint seed뿐 아니라 다음 값이 저장된다.

```text
grasp_offset_base
pregrasp_offset_base
lift_offset_base
pre_grasp_seed_q
grasp_seed_q
lift_seed_q
open_q3
close_q3
```

물체가 다른 위치에 놓여도 카메라 3D 위치에 Cartesian offset을 적용하고 IK로 다시 계산할 수 있다.

## 3. 노드 구조

```text
/object_finder/result
        ↓
detection_localizer_node
        ↓
/macrobot/perception/localized_detection
        ↓
pick_teach_node
        ├─ stable target lock
        ├─ grasp-frame sample capture
        ├─ primitive capture
        ├─ grasp profile capture
        ├─ report YAML 저장
        └─ profile reload

시험 이동:
pick_teach_node
→ /macrobot/arm/joint_goal
→ validator
→ safe-region
→ servo bridge
→ Pico
```

## 4. 출력 파일

기존 commissioning report와 같은 파일을 사용한다.

```text
~/MacRobot/data/commissioning/arm_commissioning_report.yaml
```

추가로 pick profile overlay를 생성한다.

```text
~/MacRobot/data/commissioning/pick_profiles_recorded.yaml
```

`pick_coordinator_node`는 report의 `grasp_profiles`를 즉시 reload할 수 있다.

## 5. 실행 전 조건

다음이 먼저 동작해야 한다.

```text
D435 / realsense2_camera
물체 인식 파이프라인
/object_finder/result
pick_pipeline_robot.launch.py 또는 동일한 arm pipeline
/macrobot/perception/localized_detection
/macrobot/arm/logical_joint_states
/macrobot/arm/tool_pose
/macrobot/arm/validation_status
/macrobot/arm/servo_bridge/status
```

실제 하드웨어에서는 반드시 최신 safe-region을 켠다.

## 6. 권장 분산 실행

report 파일과 `pick_coordinator_node`가 같은 파일시스템을 보도록 **teach node는 Raspberry Pi에서 실행**하는 것을 권장한다. WSL2에서는 CLI와 RViz만 실행한다.

### Raspberry Pi: arm/pick/teach 전체 headless stack

```bash
source /opt/ros/jazzy/setup.bash
source ~/MacRobot/install/setup.bash

export SAFE_CSV="$HOME/MacRobot/data/safe_region_collision_v2_fine/safe_connected_samples.csv"

ros2 launch macrobot_pick_pipeline pick_pipeline_robot.launch.py \
  safe_region_csv:="$SAFE_CSV" \
  start_pico_debug:=true \
  serial_port:=/dev/ttyACM0 \
  start_teach:=true \
  allow_teach_motion:=true
```

이 구성에서는 Pi의 다음 파일을 coordinator와 teach node가 함께 사용한다.

```text
~/MacRobot/data/commissioning/arm_commissioning_report.yaml
```

### WSL2: 대화형 CLI

```bash
source /opt/ros/jazzy/setup.bash
source ~/MacRobot/install/setup.bash

ros2 run macrobot_pick_pipeline pick_teach_cli
```

### WSL2: RViz

```bash
ros2 launch macrobot_pick_pipeline real_camera_rviz.launch.py
```

WSL2의 CLI는 ROS command만 보내며 report를 직접 쓰지 않는다. 작업이 끝난 뒤 report를 WSL로 복사하려면 다음을 사용한다.

```bash
rsync -av <PI_USER>@<PI_IP>:~/MacRobot/data/commissioning/ \
  ~/MacRobot/data/commissioning/
```

Pi와 WSL의 `ROS_DOMAIN_ID`, RMW, discovery 범위가 같아야 한다.

`pick_teach.launch.py`에서 teach node를 WSL에 직접 띄우는 방식은 coordinator도 WSL에 있거나 report 경로를 네트워크 공유한 경우에만 사용한다.

## 7. 메뉴 5: 카메라 보조 grasp_frame 보정

작고 위치가 명확한 calibration target을 고정한다. 구형·마커 중심처럼 카메라가 측정하는 중심과 실제 clamp 접촉 중심의 관계가 명확한 물체가 좋다.

흐름:

```text
1. calibration target을 stable lock
2. q3=open/mid/near-close에서 그리퍼를 이동
3. 각 상태에서 실제 두 clamp 접촉 중심을 target 중심에 맞춤
4. 현재 q와 camera target point를 기록
5. 세 샘플 이상으로 tool geometry fitting
```

결과:

```text
tool_offset_x
tool_offset_z
gripper_link_length
gripper_base_separation
RMS error
max error
```

추천값은 다음에도 저장된다.

```text
~/MacRobot/data/commissioning/grasp_frame_recommendation.yaml
```

주의: 이 fitting에는 카메라 extrinsic 오차와 target 중심 오차가 함께 들어간다. 적용 전 RViz와 실물에서 검증해야 한다.

## 8. 메뉴 6: primitive 기록

지원 예:

```text
HOME
STOW
OPEN
CLOSE
PRE_GRASP
LOWER
LIFT
PLACE
```

현재 `q1/q2/q3`를 기록하며, 카메라 target이 lock되어 있으면 다음 context도 함께 저장한다.

```text
target_point_base
grasp_frame_point_base
grasp_frame_offset_from_target
gripper_gap_m
```

기록 후 시험을 선택하면 `/macrobot/arm/joint_goal`로만 보내므로 validator를 우회하지 않는다.

## 9. 메뉴 7: 물체별 profile 기록

먼저 실제 물체를 카메라로 lock한다. 이후 다음 상태에서 현재 자세를 기록한다.

```text
PRE_GRASP
GRASP   # 열린 그리퍼로 접근 완료
CLOSE   # 동일 q1/q2 부근에서 실제 안전 close
LIFT
PLACE   # 선택
```

offset 계산:

```text
grasp_offset_base
= CLOSE 상태 grasp_frame - camera object point

pregrasp_offset_base
= PRE_GRASP grasp_frame - CLOSE grasp_frame

lift_offset_base
= LIFT grasp_frame - CLOSE grasp_frame
```

`GRASP` 상태 q는 IK branch seed로 사용하고, 실제 object-centre offset은 닫힌 `CLOSE` 상태의 동적 grasp frame으로 계산한다.

저장 후 `/macrobot/pick/reload_profiles` 서비스를 자동 호출한다. 전체 시험을 선택하면 기존 `/macrobot/pick/goal` state machine이 실행된다.

## 10. 직접 JSON 명령

상태:

```bash
ros2 topic pub --once /macrobot/pick/teach/command std_msgs/msg/String \
  "{data: '{\"action\":\"status\",\"command_id\":\"status-1\"}'}"
```

물체 lock:

```bash
ros2 topic pub --once /macrobot/pick/teach/command std_msgs/msg/String \
  "{data: '{\"action\":\"lock_target\",\"command_id\":\"lock-1\",\"object_name\":\"Buds3\",\"timeout_sec\":30.0}'}"
```

현재 자세를 primitive로 기록:

```bash
ros2 topic pub --once /macrobot/pick/teach/command std_msgs/msg/String \
  "{data: '{\"action\":\"record_primitive\",\"command_id\":\"prim-1\",\"name\":\"PRE_GRASP\",\"speed_scale\":0.5}'}"
```

결과:

```bash
ros2 topic echo /macrobot/pick/teach/result
```

상태 로그:

```bash
ros2 topic echo /macrobot/pick/teach/status
```

## 11. RViz

`pick_pipeline.rviz`에 다음 MarkerArray가 추가된다.

```text
/macrobot/pick/teach/markers
```

표시:

```text
빨강: camera locked target
초록: 현재 grasp_frame
노랑: PRE_GRASP
초록: GRASP
하늘색: CLOSE
파랑: LIFT
보라: PLACE
```

## 12. 안전 규칙

- 메뉴 5~7의 시험 이동도 최신 safe-region을 반드시 사용한다.
- teach 노드는 `/pico_debug/cmd` publisher를 만들지 않는다.
- 충돌이 보이면 즉시 `/macrobot/arm/stop` 또는 물리 전원을 사용한다.
- profile test 전 `require_safe_region=true`를 확인한다.
- 카메라 target이 arm plane에서 벗어나면 pick coordinator가 `base_alignment_required`로 거부한다.
- 기존 commissioning 메뉴 5~7은 legacy로 남지만, 새 기록은 이 workflow를 사용한다.

## 13. 한 장치에서 전부 실행하는 대안

모든 노드가 같은 PC/WSL에서 dry-run으로 동작하거나 report 경로가 공유된 경우에는 standalone teach launch를 사용할 수 있다.

```bash
ros2 launch macrobot_pick_pipeline pick_teach.launch.py \
  start_localizer:=false \
  start_coordinator:=false \
  start_rviz:=true
```

실제 Pi↔WSL 분산 운용에서는 report 일관성을 위해 Pi에서 `start_teach:=true`를 사용하는 구성이 우선이다. 동일한 `pick_teach_node`를 두 장치에서 동시에 실행하지 않는다.
