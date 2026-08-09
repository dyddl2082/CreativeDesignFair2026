# macrobot_arm_kinematics

**상태:** 필수 · FK/IK 및 폐루프 visual mapping

## 역할

- reduced q1/q2/q3 모델의 FK/IK
- q1/q2를 full 4-bar joint들로 변환하여 평행사변형 유지
- q3를 그리퍼 기어·addition·clamp joint에 대칭 매핑
- `tool0`, 동적 `grasp_frame`, gripper gap 계산

## 실행 파일

```text
linkage_state_node
ik_node
```

## 주요 토픽

```text
/macrobot/arm/logical_joint_states
/macrobot/arm/target_point
/macrobot/arm/ik_solution
/macrobot/arm/ik_status
/macrobot/arm/tool_pose
/macrobot/gripper/gap
/joint_states
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

## 모델 확인

```bash
ros2 launch macrobot_description display_full.launch.py \
  auto_apply_ik:=true \
  start_rviz:=true
```

직접 logical state를 시각화할 때:

```bash
ros2 topic pub --once \
  /macrobot/arm/logical_joint_states \
  sensor_msgs/msg/JointState \
  "{name: ['arm_lift_joint', 'wrist_pitch_joint', 'gripper_joint'], position: [0.15, 0.0, 0.15]}"
```

IK target:

```bash
ros2 topic pub --once \
  /macrobot/arm/target_point \
  geometry_msgs/msg/PointStamped \
  "{header: {frame_id: 'base_link'}, point: {x: -0.15, y: 0.0645, z: 0.12}}"
```

## 안전 주의

실제 하드웨어가 연결된 상태에서 `/macrobot/arm/logical_joint_states`에 직접 publish하면 validator를 우회한 것처럼 모델/실물 상태가 어긋날 수 있다. 실물 목표는 `/macrobot/arm/joint_goal`로 보낸다.
