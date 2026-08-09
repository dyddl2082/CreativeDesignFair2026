# macrobot_safe_region

**상태:** 필수 · WSL2 offline 생성 도구 · 매 frame runtime MoveIt이 아님

## 역할

q1/q2/q3 grid를 sampling하여 다음을 검사한다.

- 논리 joint, tool pitch, 4-bar toggle 제한
- MG996R/MG90S command·pulse 제한
- full detailed collision model의 self/world collision
- home에서 안전한 grid edge로 연결된 component

출력 CSV를 `macrobot_arm_control`의 validator와 servo bridge가 runtime lookup table로 사용한다.

## 빌드

```bash
cd ~/MacRobot
source /opt/ros/jazzy/setup.bash

rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install --packages-select \
  macrobot_description \
  macrobot_moveit_config \
  macrobot_safe_region

source ~/MacRobot/install/setup.bash
```

## Coarse scan

```bash
rm -rf ~/MacRobot/data/safe_region_collision_v2_coarse

ros2 launch macrobot_safe_region \
  generate_safe_region_exact_gripper.launch.py \
  output_directory:=$HOME/MacRobot/data/safe_region_collision_v2_coarse
```

## Fine scan

```bash
rm -rf ~/MacRobot/data/safe_region_collision_v2_fine

ros2 launch macrobot_safe_region \
  generate_safe_region_exact_gripper.launch.py \
  scan_config:=$(ros2 pkg prefix --share macrobot_safe_region)/config/full_fine_scan.yaml \
  output_directory:=$HOME/MacRobot/data/safe_region_collision_v2_fine
```

## 결과

```text
safe_samples.csv
safe_connected_samples.csv
safe_q2_intervals_by_q1_q3.csv
safe_region_summary.yaml
```

```bash
cat ~/MacRobot/data/safe_region_collision_v2_fine/safe_region_summary.yaml
```

## 반드시 재생성하는 경우

- URDF joint axis/origin/collision mesh 변경
- SRDF collision pair 변경
- q1/q2/q3 부호·범위 변경
- 서보 zero/sign/pulse/command 범위 변경
- gripper geometry 또는 `grasp_frame` 변경

실물 메뉴 3 검증 전에는 collision-only RViz와 dry-run에서 결과를 먼저 확인한다.
