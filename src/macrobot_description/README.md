# macrobot_description

**상태:** 필수 · URDF/Xacro, detailed collision, TF, RViz

## 포함 내용

- Fusion visual/collision DAE meshes
- full 4-bar 및 그리퍼 visual tree
- reduced 3-DOF IK model
- D435F depth origin의 `camera_link`
- `tool0`, 동적 `grasp_frame`
- 현재 물리 서보 방향과 q1/q2/q3 convention

## 현재 논리 관절 convention

```text
q1 > 0
→ 왼쪽 MG996R CCW
→ 팔이 전방으로 기울어짐

q1 + q2 > 0
→ 오른쪽 MG996R CW
→ 뒤쪽 링크가 올라감

q3 = 0
→ gripper open

q3 > 0
→ MG90S CCW
→ gripper close
```

## 주요 모델

```text
urdf/macrobot_full_visual.urdf.xacro
urdf/macrobot_full_exact_gripper.urdf.xacro
urdf/macrobot_full_collision.urdf.xacro
urdf/macrobot_arm_kinematic.urdf.xacro
```

## 빌드

```bash
cd ~/MacRobot
source /opt/ros/jazzy/setup.bash

rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install --packages-select \
  macrobot_arm_kinematics \
  macrobot_description

source ~/MacRobot/install/setup.bash
```

## WSL2 full model + RViz

```bash
ros2 launch macrobot_description display_full.launch.py \
  auto_apply_ik:=true \
  start_rviz:=true
```

Headless/Pi:

```bash
ros2 launch macrobot_description display_full.launch.py \
  auto_apply_ik:=false \
  start_rviz:=false
```

## Collision-only 확인

```bash
ros2 launch macrobot_description \
  display_full_exact_collision.launch.py \
  start_rviz:=true
```

RViz RobotModel에서 `Visual Enabled=false`, `Collision Enabled=true`로 확인한다.

## TF 확인

```bash
ros2 run tf2_ros tf2_echo world base_link
ros2 run tf2_ros tf2_echo base_link camera_link
ros2 run tf2_ros tf2_echo base_link grasp_frame
```

## 모델 변경 후 조치

다음이 바뀌면 기존 safe-region CSV를 폐기하고 재생성한다.

- joint axis/origin
- collision geometry 또는 SRDF pair
- q1/q2/q3 부호·범위
- gripper linkage 또는 `grasp_frame`
- 서보 mapping
