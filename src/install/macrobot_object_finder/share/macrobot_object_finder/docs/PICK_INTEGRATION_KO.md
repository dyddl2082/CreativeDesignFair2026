# `macrobot_pick_pipeline` 연동

## 프로세스 배치

### Raspberry Pi 터미널 1: D435 후보 생성

```bash
source /opt/ros/jazzy/setup.bash
source ~/MacRobot/install/setup.bash
export ROS_DOMAIN_ID=42
export ROS_AUTOMATIC_DISCOVERY_RANGE=SUBNET
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
unset ROS_LOCALHOST_ONLY

ros2 launch realsense2_camera rs_launch.py \
  enable_color:=true \
  enable_depth:=true \
  enable_infra1:=false \
  enable_infra2:=false \
  pointcloud.enable:=false \
  align_depth.enable:=true \
  enable_sync:=true \
  rgb_camera.color_profile:=640x480x15 \
  depth_module.depth_profile:=640x480x15 \
  rgb_camera.color_format:=RGB8 \
  depth_module.depth_format:=Z16

# 별도 Pi 터미널
ros2 launch depth_candidate_proposal edge_candidate_pipeline.launch.py
```

### WSL2: 인식과 finder manager

```bash
source ~/MacRobot/.venv-embedding/bin/activate
source /opt/ros/jazzy/setup.bash
source ~/MacRobot/install/setup.bash
export ROS_DOMAIN_ID=42
export ROS_AUTOMATIC_DISCOVERY_RANGE=SUBNET
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
unset ROS_LOCALHOST_ONLY

ros2 launch macrobot_object_finder object_finder_wsl.launch.py
```

### Raspberry Pi 터미널 2: 팔·정렬·pick stack

```bash
export SAFE_CSV="$HOME/MacRobot/data/safe_region_collision_v2_fine/safe_connected_samples.csv"

ros2 launch macrobot_pick_pipeline pick_pipeline_robot.launch.py \
  safe_region_csv:="$SAFE_CSV" \
  start_pico_debug:=true \
  serial_port:=/dev/ttyACM0 \
  perception_input_mode:=legacy \
  start_base_alignment:=true \
  start_camera_teach:=false
```

`perception_input_mode:=legacy`는 새 finder가 발행하는 canonical JSON `/object_finder/result`를 localizer가 사용한다는 뜻이다.

## pick 명령

```bash
ros2 topic pub --once /macrobot/pick/goal std_msgs/msg/String \
  "{data: '{\"object_name\":\"Buds3\",\"profile\":\"Buds3\",\"execute\":true}'}"
```

흐름:

```text
pick coordinator
→ /object_finder/goal
→ macrobot_object_finder
→ /object_finder/result
→ detection localizer
→ /macrobot/perception/object_point
→ alignment / arm plan
```

## 확인

```bash
ros2 topic info /object_finder/result -v
```

publisher는 `macrobot_object_finder` 하나여야 한다.

```bash
ros2 topic echo --full-length --field data /object_finder/result
ros2 topic echo /macrobot/perception/object_point
ros2 topic echo --full-length --field data /macrobot/pick/status
```
