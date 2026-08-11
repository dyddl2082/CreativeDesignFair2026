# WSL2 전용 테스트

현재 실제 로봇이 없는 동안 사용할 절차다.

## 1. 설치

압축의 `macrobot_pick_pipeline` 폴더를 workspace에 복사한다.

```bash
cp -r macrobot_pick_pipeline ~/MacRobot/src/

cd ~/MacRobot
source /opt/ros/jazzy/setup.bash

rosdep install --from-paths src --ignore-src -r -y

colcon build \
  --packages-select macrobot_pick_pipeline \
  --symlink-install

source ~/MacRobot/install/setup.bash
```

## 2. 가장 간단한 mock 테스트

```bash
ros2 launch macrobot_pick_pipeline pick_pipeline_wsl.launch.py \
  use_mock_perception:=true \
  use_finder:=false \
  require_safe_region:=false \
  start_rviz:=true
```

이 launch는 다음을 실행한다.

```text
full robot model
IK validator
servo bridge dry-run
mock perception
pick coordinator
RViz
```

실제 Pico 명령은 전송하지 않는다.

## 3. Pick goal

```bash
ros2 topic pub --once \
  /macrobot/pick/goal \
  std_msgs/msg/String \
  "{data: '{\"object_name\":\"Buds3\",\"profile\":\"Buds3\",\"execute\":true}'}"
```

예상 RViz 동작:

```text
그리퍼 open
→ pre-grasp
→ object point 접근
→ close
→ 위로 lift
```

RViz marker 색상:

```text
빨강: 검출 물체
노랑: pre-grasp
초록: grasp
파랑: lift
```

## 4. 상태 확인

```bash
ros2 topic echo /macrobot/pick/status
```

```bash
ros2 topic echo /macrobot/pick/result
```

```bash
ros2 topic echo /macrobot/arm/validation_status
```

```bash
ros2 topic echo /macrobot/arm/servo_bridge/status
```

정상 이벤트 순서:

```text
pick_started
target_locked
pick_step_commanded / pick_step_validated / pick_step_completed 반복
pick_completed
```

## 5. 위치만 찾고 팔은 움직이지 않기

```bash
ros2 topic pub --once \
  /macrobot/pick/goal \
  std_msgs/msg/String \
  "{data: '{\"object_name\":\"Buds3\",\"execute\":false}'}"
```

## 6. 취소

```bash
ros2 topic pub --once \
  /macrobot/pick/cancel \
  std_msgs/msg/String \
  "{data: 'cancel'}"
```

## 7. safe-region 포함

WSL2에도 최신 collision-v2 CSV가 있을 경우:

```bash
export SAFE_CSV="$HOME/MacRobot/data/safe_region_collision_v2_fine/safe_connected_samples.csv"

ros2 launch macrobot_pick_pipeline pick_pipeline_wsl.launch.py \
  use_mock_perception:=true \
  use_finder:=false \
  require_safe_region:=true \
  safe_region_csv:="$SAFE_CSV" \
  start_rviz:=true
```

CSV revision이 현재 arm-control package와 다르면 validator가 시작 단계에서 거부한다.

## 8. mock 물체 위치 바꾸기

launch 실행 시 mock node parameter를 직접 바꾸려면 별도 실행이 편하다.

```bash
ros2 run macrobot_pick_pipeline mock_perception_node --ros-args \
  -p point_x:=-0.14 \
  -p point_y:=0.0645 \
  -p point_z:=0.13
```

이 경우 launch에서는:

```text
use_mock_perception:=false
```

로 두고 mock node를 별도 실행한다.

## 9. base alignment 시험

mock Y를 arm plane에서 멀리 두면:

```bash
ros2 run macrobot_pick_pipeline mock_perception_node --ros-args \
  -p point_x:=-0.15 \
  -p point_y:=0.15 \
  -p point_z:=0.12
```

coordinator가 팔을 움직이지 않고 다음을 publish해야 한다.

```text
/macrobot/base/alignment_request
base_alignment_required
```
