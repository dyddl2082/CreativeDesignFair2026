# macrobot_arm_control

**상태:** 필수 · 팔 안전 제어 runtime

## 노드

### `ik_validator_node`

검사 항목:

- 논리 q1/q2/q3 범위
- 2:1 기어비와 실제 서보 command 범위
- `q1 + q2` 결합 제한
- 4-bar toggle margin
- offline safe-region CSV
- 현재 자세부터 목표 자세까지 joint-space 경로

### `servo_bridge_node`

- validated goal만 수신
- q1/q2/q3 trajectory 보간
- 각 중간 자세 재검사
- 논리 관절을 3채널 pulse로 변환
- `ARM_US <left> <right> <gripper>` publish
- RViz용 `/macrobot/arm/logical_joint_states` publish

## 주요 토픽

```text
입력:
/macrobot/arm/joint_goal
/macrobot/arm/ik_solution

출력:
/macrobot/arm/validated_joint_goal
/macrobot/arm/rejected_joint_goal
/macrobot/arm/validation_status
/macrobot/arm/logical_joint_states
/macrobot/arm/servo_bridge/status
/macrobot/arm/servo_bridge/command_preview
/pico_debug/cmd
```

정지/출력 해제:

```text
/macrobot/arm/stop
/macrobot/arm/disable_servos
```

## 현재 물리 convention

```text
q1 > 0
→ 왼쪽 MG996R CCW
→ 팔 전방 기울기

q1 + q2 > 0
→ 오른쪽 MG996R CW
→ 뒤쪽 링크 상승

q3 = 0
→ open

q3 > 0
→ MG90S CCW
→ close
```

500/1500/2500µs 기준 Home/Open은:

```text
ARM_US 1500 1500 500
```

## 빌드

```bash
cd ~/MacRobot
source /opt/ros/jazzy/setup.bash

rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install --packages-select \
  macrobot_arm_kinematics \
  macrobot_description \
  macrobot_safe_region \
  macrobot_arm_control

source ~/MacRobot/install/setup.bash
```

## WSL2 dry-run

```bash
ros2 launch macrobot_arm_control arm_pipeline.launch.py \
  dry_run:=true \
  require_safe_region:=false \
  command_home_on_start:=false \
  start_rviz:=true
```

목표:

```bash
ros2 topic pub --once \
  /macrobot/arm/joint_goal \
  sensor_msgs/msg/JointState \
  "{name: ['arm_lift_joint', 'wrist_pitch_joint', 'gripper_joint'], position: [0.15, 0.0, 0.0]}"
```

Preview/상태:

```bash
ros2 topic echo /macrobot/arm/servo_bridge/command_preview
ros2 topic echo /macrobot/arm/validation_status
ros2 topic echo /macrobot/arm/servo_bridge/status
```

## 실제 모드

```bash
SAFE_CSV=$HOME/MacRobot/data/safe_region_collision_v2_fine/safe_connected_samples.csv

ros2 launch macrobot_arm_control arm_pipeline.launch.py \
  dry_run:=false \
  require_safe_region:=true \
  safe_region_csv:="$SAFE_CSV" \
  command_home_on_start:=false \
  start_rviz:=false
```

별도로 `pico_debug_node`를 실행한다. 첫 실물 실행에서 `command_home_on_start`는 반드시 false로 둔다.

## 안전 원칙

- 일반 명령은 `/macrobot/arm/joint_goal`만 사용한다.
- `/validated_joint_goal`, `/logical_joint_states`, `/pico_debug/cmd` 직접 publish는 일반 운용에서 금지한다.
- `require_safe_region:=false`는 모델 개발/보정 단계에만 사용한다.
- `goal_rejected` 뒤에 새로운 `ARM_US`가 발행되면 실행을 중단하고 publisher 경로를 점검한다.
