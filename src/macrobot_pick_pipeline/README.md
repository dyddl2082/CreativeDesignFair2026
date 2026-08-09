# macrobot_pick_pipeline

**상태:** 필수 · 카메라 인식 결과와 검증된 팔 동작 연결

## 노드

### `detection_localizer_node`

`/object_finder/result`의 pixel center와 depth를 CameraInfo/TF로 `base_link` 3D point로 변환한다.

### `pick_coordinator_node`

```text
SEARCHING
→ target 안정화
→ OPEN
→ PRE_GRASP
→ APPROACH
→ CLOSE
→ LIFT
→ DONE
```

각 팔 목표는 `/macrobot/arm/joint_goal`로 보내 validator와 servo bridge를 반드시 거친다.

### `mock_perception_node`

실제 카메라가 없을 때 WSL2 dry-run용 가상 3D target을 발행한다.

## 주요 토픽

```text
입력:
/macrobot/pick/goal
/macrobot/pick/cancel
/object_finder/result
/camera/camera/color/camera_info

출력:
/macrobot/pick/status
/macrobot/pick/result
/macrobot/pick/markers
/macrobot/arm/joint_goal
/macrobot/base/alignment_request
```

## 빌드

```bash
cd ~/MacRobot
source /opt/ros/jazzy/setup.bash

rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install --packages-select \
  macrobot_description \
  macrobot_arm_kinematics \
  macrobot_arm_control \
  macrobot_pick_pipeline

source ~/MacRobot/install/setup.bash
```

## 현재 WSL2 mock 시험

```bash
ros2 launch macrobot_pick_pipeline pick_pipeline_wsl.launch.py \
  use_mock_perception:=true \
  use_finder:=false \
  require_safe_region:=false \
  start_rviz:=true
```

Pick 목표:

```bash
ros2 topic pub --once \
  /macrobot/pick/goal \
  std_msgs/msg/String \
  "{data: '{\"object_name\":\"Buds3\",\"profile\":\"Buds3\",\"execute\":true}'}"
```

Localization만:

```bash
ros2 topic pub --once \
  /macrobot/pick/goal \
  std_msgs/msg/String \
  "{data: '{\"object_name\":\"Buds3\",\"execute\":false}'}"
```

상태:

```bash
ros2 topic echo /macrobot/pick/status
ros2 topic echo /macrobot/pick/result
ros2 topic echo /macrobot/arm/validation_status
```

취소:

```bash
ros2 topic pub --once \
  /macrobot/pick/cancel \
  std_msgs/msg/String \
  "{data: 'cancel'}"
```

## 실제 로봇 실행

카메라 인식 pipeline과 최신 safe CSV가 준비된 뒤:

```bash
SAFE_CSV=$HOME/MacRobot/data/safe_region_collision_v2_fine/safe_connected_samples.csv

ros2 launch macrobot_pick_pipeline pick_pipeline_robot.launch.py \
  safe_region_csv:="$SAFE_CSV" \
  serial_port:=/dev/ttyACM0 \
  start_pico_debug:=true
```

## Finder 입력 계약

기본 localizer는 `/object_finder/result` JSON에서 다음을 읽는다.

```text
object_name
score
center_px.x / center_px.y
depth_m
```

`camera_depth_optical_frame` 계열 TF가 `base_link`까지 연결되어야 한다. 현재 팔은 X-Z 평면 2-DOF이므로 target y가 arm plane에서 벗어나면 base alignment를 요청한다.
