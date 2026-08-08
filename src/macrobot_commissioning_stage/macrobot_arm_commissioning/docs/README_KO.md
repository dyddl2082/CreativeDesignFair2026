# MacRobot Arm Commissioning

이 패키지는 카메라 연동 전에 필요한 로봇팔 시험을 대화형으로 수행하고, 모든 자동 결과와 수동 측정값을 하나의 YAML 보고서에 누적한다.

기본 보고서 경로:

```text
~/MacRobot/data/commissioning/arm_commissioning_report.yaml
```

## 포함 시험

1. MG996R/MG90S pulse, zero, sign, command range 기록
2. q1 +0.05, q2 +0.05, q3 -0.05 방향 및 4-bar/gripper 제약 확인
3. MoveIt safe-region에서 자동 선택한 대표 경계 자세 시험
4. 무부하·하중 반복 정밀도, 백래시, 온도 시험
5. q3별 실제 clamp 접촉 중심을 이용한 grasp_frame 기하 보정
6. HOME/STOW/OPEN/CLOSE/PRE_GRASP/LOWER/LIFT/PLACE 정의와 시험
7. 물체별 grasp profile 기록

## 안전 원칙

- `allow_motion_commands` 기본값은 `false`다.
- raw pulse 교정은 `allow_raw_pulse_commands=true`일 때만 가능하다.
- raw pulse 모드는 validator와 servo bridge를 우회하므로, 기어를 분리하거나 팔을 지지한 상태에서만 사용한다.
- 모든 일반 동작은 `/macrobot/arm/joint_goal`을 통해 validator를 거친다.
- 보고서는 매 입력마다 원자적으로 저장되므로 중간 종료 후 재개할 수 있다.

## 1. 파이프라인 실행

dry-run:

```bash
ros2 launch macrobot_arm_commissioning commissioning_pipeline.launch.py \
  dry_run:=true \
  require_safe_region:=true \
  safe_region_csv:=$HOME/MacRobot/data/safe_region_exact_gripper_fine/safe_connected_samples.csv
```

실물:

```bash
ros2 launch macrobot_arm_commissioning commissioning_pipeline.launch.py \
  dry_run:=false \
  start_pico_debug:=true \
  serial_port:=/dev/ttyACM0 \
  require_safe_region:=true \
  safe_region_csv:=$HOME/MacRobot/data/safe_region_exact_gripper_fine/safe_connected_samples.csv
```

이 launch는 초기 시험용으로 q1/q2 0.08 rad/s, q3 0.12 rad/s의 낮은 속도를 적용한다.

## 2. 대화형 시험 실행

새 터미널에서:

```bash
source /opt/ros/jazzy/setup.bash
source ~/MacRobot/install/setup.bash

ros2 run macrobot_arm_commissioning commissioning_cli --ros-args \
  -p allow_motion_commands:=true \
  -p safe_region_csv:=$HOME/MacRobot/data/safe_region_exact_gripper_fine/safe_connected_samples.csv \
  -p all_samples_csv:=$HOME/MacRobot/data/safe_region_exact_gripper_fine/safe_samples.csv \
  -p report_path:=$HOME/MacRobot/data/commissioning/arm_commissioning_report.yaml
```

pulse 교정까지 할 때만 추가:

```bash
-p allow_raw_pulse_commands:=true
```

## 대표 경계 자동 선택

`safe_connected_samples.csv`에서 다음을 자동으로 고른다.

- home
- q1/q2/q3 최소·최대에서 한 grid 안쪽
- q3 half
- q1+q2 최소·최대에서 한 grid 안쪽
- `safe_samples.csv`의 빈번한 collision pair 바로 안쪽 안전 자세

각 자세는 validator와 servo bridge를 통과한 뒤 사람이 실물 충돌·binding을 확인한다.

## grasp_frame 피팅

현재 모델식은 다음과 같다.

```text
offset_x(q3) = tool_offset_x - gripper_link_length * sin(q3)
offset_z(q3) = tool_offset_z
```

q3=0, 약 -0.6, 실제 close 상태에서 접촉 중심을 측정하면 다음 값을 최소제곱으로 계산한다.

```text
tool_offset_x
tool_offset_z
gripper_link_length
gripper_base_separation (gap을 입력한 경우)
```

추천값은 보고서의 `recommended_kinematics_parameters`에 저장된다.

## primitive 실행

커미셔닝 보고서에 primitive를 저장한 뒤:

```bash
ros2 run macrobot_arm_commissioning primitive_executor_node --ros-args \
  -p report_path:=$HOME/MacRobot/data/commissioning/arm_commissioning_report.yaml
```

명령:

```bash
ros2 topic pub --once \
  /macrobot/arm/primitive_command \
  std_msgs/msg/String \
  "{data: 'HOME'}"
```

```bash
ros2 topic pub --once \
  /macrobot/arm/primitive_command \
  std_msgs/msg/String \
  "{data: 'PRE_GRASP'}"
```

`STOP`, `DISABLE`도 같은 topic으로 보낼 수 있다.

## 보고서 요약

```bash
ros2 run macrobot_arm_commissioning commissioning_report_summary \
  $HOME/MacRobot/data/commissioning/arm_commissioning_report.yaml
```


## 보정 결과를 설정 파일에 적용

보정 메뉴는 실행 중인 validator와 servo bridge를 즉시 바꾸지 않는다. 보고서에서 새 설정 파일을 만들고 파이프라인을 재시작한다.

```bash
ros2 run macrobot_arm_commissioning apply_report_recommendations \
  --report $HOME/MacRobot/data/commissioning/arm_commissioning_report.yaml \
  --actuator-input $HOME/MacRobot/src/macrobot_safe_region/config/actuator_limits.yaml \
  --actuator-output $HOME/MacRobot/data/commissioning/actuator_limits_calibrated.yaml
```

그 다음 커미셔닝 파이프라인에서 새 파일을 사용하도록 기존 `actuator_limits.yaml`에 반영하거나, 백업 후 교체한다. `--in-place`를 사용하면 원본 옆에 timestamp 백업을 만든 뒤 직접 수정한다.

```bash
ros2 run macrobot_arm_commissioning apply_report_recommendations \
  --report $HOME/MacRobot/data/commissioning/arm_commissioning_report.yaml \
  --actuator-input $HOME/MacRobot/src/macrobot_safe_region/config/actuator_limits.yaml \
  --kinematics-input $HOME/MacRobot/src/macrobot_description/config/kinematics.yaml \
  --in-place
```

적용 후 관련 패키지를 다시 빌드하고 파이프라인을 재시작한다.


보정된 actuator 파일을 직접 사용하려면 launch argument로 지정한다.

```bash
ros2 launch macrobot_arm_commissioning commissioning_pipeline.launch.py \
  dry_run:=false \
  start_pico_debug:=true \
  serial_port:=/dev/ttyACM0 \
  actuator_limits_file:=$HOME/MacRobot/data/commissioning/actuator_limits_calibrated.yaml \
  safe_region_csv:=$HOME/MacRobot/data/safe_region_exact_gripper_fine/safe_connected_samples.csv
```

대화형 CLI에도 같은 파일을 전달한다.

```bash
ros2 run macrobot_arm_commissioning commissioning_cli --ros-args \
  -p allow_motion_commands:=true \
  -p actuator_limits_file:=$HOME/MacRobot/data/commissioning/actuator_limits_calibrated.yaml \
  -p safe_region_csv:=$HOME/MacRobot/data/safe_region_exact_gripper_fine/safe_connected_samples.csv
```
