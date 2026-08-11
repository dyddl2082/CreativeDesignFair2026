# 실제 D435F와 로봇을 다시 사용할 때

지금은 실행하지 않고, 실물이 돌아왔을 때 사용할 절차다.

## 1. RealSense

```bash
ros2 launch realsense2_camera rs_launch.py \
  enable_color:=true \
  enable_depth:=true \
  align_depth.enable:=true \
  pointcloud.enable:=false
```

확인:

```bash
ros2 topic echo /camera/camera/color/camera_info --once
ros2 run tf2_ros tf2_echo base_link camera_color_optical_frame
```

## 2. 기존 object finder

기존 finder가 최소 다음 값을 결과 JSON에 넣어야 한다.

```text
object_name
found
score
center_px.x / center_px.y
depth_m
depth_valid
```

## 3. 실제 pick pipeline

```bash
export SAFE_CSV="$HOME/MacRobot/data/safe_region_collision_v2_fine/safe_connected_samples.csv"

ros2 launch macrobot_pick_pipeline pick_pipeline_robot.launch.py \
  safe_region_csv:="$SAFE_CSV" \
  serial_port:=/dev/ttyACM0 \
  start_pico_debug:=true
```

이 launch는 RealSense와 object finder를 직접 시작하지 않는다. 두 노드는 먼저 별도 실행되어 있어야 한다.

## 4. 현재 구현의 범위

현재 팔은 planar 2-DOF이므로:

```text
물체가 arm-plane Y 근처에 있고
pre-grasp / grasp / lift 세 점이 IK reachable이며
safe-region을 통과할 때만
```

자동 파지를 수행한다.

물체가 좌우로 벗어나거나 너무 멀면 `/macrobot/base/alignment_request`를 publish한다. 다음 구현 단계는 이 요청을 받아 차체를 조금 회전·전진한 뒤 다시 카메라 검출을 반복하는 `base_alignment_controller`다.
