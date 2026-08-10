# macrobot_pick_pipeline 0.4.0

MacRobot의 카메라 기반 물체 위치 추정·검증된 pick 실행·교시(teach) 기능을 제공한다.

## 0.4.0: 기록된 카메라 위치 기반 차체 정렬 + pick

이번 버전은 물체 탐색 알고리즘과 하위 로봇 제어 사이의 계약을 명확히 하고, 사용자가 한 번 기록한 **잡을 수 있는 카메라 상대 위치**로 차체를 반복 정렬한 뒤 기존 validated pick sequence를 실행한다.

```text
물체 finder 결과
→ detection_localizer_node
→ base_link object point
→ base_alignment_node
→ 작은 TURN_DEG / MOVE_CM 반복
→ 기록 위치 도달
→ pick_coordinator_node
→ validator / safe-region / servo bridge
```

추가 실행 파일:

```text
base_alignment_node
base_alignment_cli
```

추가 문서:

```text
docs/OBJECT_FINDER_TEAM_INTERFACE_KO.md
docs/BASE_ALIGNMENT_AND_PICK_KO.md
```

팀 detector는 기존 `/object_finder/result` JSON 또는 `macrobot_interfaces/msg/TemporalConfirmationResult` 중 하나를 발행할 수 있다. 기본 설정은 legacy JSON이며 `perception_input_mode:=typed`로 typed 결과를 선택한다.

정렬 위치 기록/실행 CLI:

```bash
ros2 run macrobot_pick_pipeline base_alignment_cli
```

전체 실제 로봇 stack:

```bash
export SAFE_CSV="$HOME/MacRobot/data/safe_region_collision_v2_fine/safe_connected_samples.csv"

ros2 launch macrobot_pick_pipeline pick_pipeline_robot.launch.py \
  safe_region_csv:="$SAFE_CSV" \
  start_pico_debug:=true \
  serial_port:=/dev/ttyACM0 \
  start_base_alignment:=true \
  alignment_dry_run:=false \
  perception_input_mode:=legacy
```


이번 버전에서 교시 기능을 두 경로로 분리했다.

```text
카메라 없음
└─ arm_demo_recorder_node
   ├─ 현재 pose 기록
   ├─ 사용자가 조종하는 동안 q1/q2/q3 trajectory 기록
   └─ validator를 거친 keyframe 안전 재생

D435 연결됨
└─ camera_teach_node
   ├─ grasp_frame 보정 (기존 메뉴 5)
   └─ 물체별 grasp profile 기록 (기존 메뉴 7)
```

기존 메뉴 6은 더 이상 카메라 teach node가 담당하지 않는다. `arm_demo_cli`를 사용한다.

## 안전 원칙

- 기록은 `/macrobot/arm/logical_joint_states`를 수동으로 관찰한다.
- 사용자의 조종과 재생은 `/macrobot/arm/joint_goal`을 사용한다.
- `/pico_debug/cmd`, `ARM_US`, `SERVO_US`를 직접 기록하거나 재생하지 않는다.
- hobby servo에 외부 encoder가 없으므로 저장된 q는 실제 측정각이 아니라 명령 기반 상태일 수 있다.
- 따라서 전원을 끄고 팔을 손으로 직접 움직이는 teach-by-hand는 현재 하드웨어만으로 기록할 수 없다. 사용자는 키보드·GUI·조이스틱처럼 `/macrobot/arm/joint_goal`을 보내는 조종 수단을 사용해야 한다.
- trajectory 재생은 원래의 raw timing을 그대로 밀어 넣지 않고, validator가 확인하는 keyframe 경로로 재생한다.

## Camera-independent 메뉴 6

노드 실행:

```bash
ros2 launch macrobot_pick_pipeline arm_demo.launch.py \
  start_rviz:=false \
  allow_motion_commands:=true
```

대화형 CLI:

```bash
ros2 run macrobot_pick_pipeline arm_demo_cli
```

지원 기능:

```text
- 현재 자세를 pose primitive로 저장
- 다른 조종 도구를 사용하는 동안 trajectory 기록
- 내장 키보드 jog를 사용하면서 trajectory 기록
- mark 삽입
- 저장된 trajectory 목록 확인
- validator + safe-region을 거친 안전 재생
```

기본 저장 위치:

```text
~/MacRobot/data/arm_primitives/<name>.yaml
```

commissioning report에도 호환 정보를 기록한다.

```text
~/MacRobot/data/commissioning/arm_commissioning_report.yaml
```

## 내장 keyboard jog

```text
w / s : q1 증가 / 감소
e / d : q2 증가 / 감소
r / f : q3 증가 / 감소
h     : [0, 0, 0]
[ / ] : step 감소 / 증가
m     : recording mark
space : stop
x     : jog 종료
```

각 키는 `/macrobot/arm/joint_goal`로 목표를 보내므로 validator와 servo bridge를 우회하지 않는다.

## Camera-dependent 메뉴 5·7

D435와 `realsense2_camera`, detection localizer가 정상일 때만 실행한다.

```bash
ros2 launch macrobot_pick_pipeline camera_teach.launch.py \
  start_localizer:=true \
  start_coordinator:=true \
  start_rviz:=true \
  require_camera_health:=true
```

CLI:

```bash
ros2 run macrobot_pick_pipeline pick_teach_cli
```

CameraInfo가 최근 3초 이내에 들어오지 않으면 메뉴 5와 7은 비활성으로 표시된다.

## 실제 로봇 통합 launch

```bash
export SAFE_CSV="$HOME/MacRobot/data/safe_region_collision_v2_fine/safe_connected_samples.csv"

ros2 launch macrobot_pick_pipeline pick_pipeline_robot.launch.py \
  safe_region_csv:="$SAFE_CSV" \
  start_pico_debug:=true \
  serial_port:=/dev/ttyACM0 \
  start_arm_demo_recorder:=true \
  start_camera_teach:=false
```

D435 교시를 시작할 때만 다음을 켠다.

```bash
start_camera_teach:=true
```

## 주요 실행 파일

```text
detection_localizer_node
pick_coordinator_node
mock_perception_node
camera_teach_node
pick_teach_node          # camera_teach_node 호환 alias
pick_teach_cli           # 메뉴 5·7
arm_demo_recorder_node   # 메뉴 6
arm_demo_cli             # 기록·jog·재생 UI
base_alignment_node      # 기록된 object pose로 차체 정렬 후 pick hand-off
base_alignment_cli       # 정렬 profile 기록·정렬·align-and-pick UI
```

## 주요 토픽

Camera teach:

```text
/macrobot/pick/teach/command
/macrobot/pick/teach/status
/macrobot/pick/teach/result
/macrobot/pick/teach/markers
```

Arm demonstration recorder:

```text
/macrobot/arm/demo/command
/macrobot/arm/demo/status
/macrobot/arm/demo/result
```

공통 arm 제어:

```text
/macrobot/arm/joint_goal
/macrobot/arm/logical_joint_states
/macrobot/arm/validation_status
/macrobot/arm/servo_bridge/status
```

자세한 설계는 `docs/TEACH_REDESIGN_KO.md`, `docs/OBJECT_FINDER_TEAM_INTERFACE_KO.md`, `docs/BASE_ALIGNMENT_AND_PICK_KO.md`를 참고한다.
