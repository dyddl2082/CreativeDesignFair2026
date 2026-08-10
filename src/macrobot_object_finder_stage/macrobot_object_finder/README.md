# macrobot_object_finder

기존 MacRobot D435 파이프라인을 명령 가능한 detector/finder로 완성하는 ROS 2 Jazzy 패키지다.

## 왜 새 package가 필요한가

기존 구성은 이미 다음 핵심 알고리즘을 갖고 있다.

```text
D435 aligned depth 후보
→ 후보 RGB crop + foreground mask
→ candidate objectness filter
→ DINOv2 positive/negative retrieval
→ temporal K-of-N confirmation
```

이 패키지는 이를 다시 구현하지 않고 다음 누락된 기능을 담당한다.

```text
/object_finder/goal session 관리
목표 물체 변경과 bank reload 연결
search timeout / cancel / lost 처리
TemporalConfirmationResult를 pick pipeline용 표준 JSON으로 변환
카메라 optical frame PointStamped 디버그 출력
파이프라인 health 통합
```

**전체 RGB/depth 이미지를 WSL로 구독하지 않는다.** Pi→WSL 전송은 후보 crop과 작은 metadata만 사용한다.

## 필수 기존 package

```text
Raspberry Pi:
- realsense2_camera
- depth_candidate_proposal
- macrobot_interfaces

WSL2:
- macrobot_interfaces
- macrobot_perception
- macrobot_object_finder
```

## 설치

새 package는 **WSL2에 설치한다.** Raspberry Pi는 기존 `realsense2_camera`와 `depth_candidate_proposal`만 실행하면 된다.

```bash
cd ~/Downloads/macrobot_object_finder_stage
chmod +x install_object_finder_stage.sh
./install_object_finder_stage.sh ~/MacRobot
```

## 공통 ROS 환경

```bash
source /opt/ros/jazzy/setup.bash
source ~/MacRobot/install/setup.bash
export ROS_DOMAIN_ID=42
export ROS_AUTOMATIC_DISCOVERY_RANGE=SUBNET
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
unset ROS_LOCALHOST_ONLY
```

## Pi 실행

D435 driver:

```bash
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
```

저대역폭 candidate crop pipeline:

```bash
ros2 launch depth_candidate_proposal edge_candidate_pipeline.launch.py
```

확인:

```bash
ros2 topic hz /depth_candidates/candidates
ros2 topic hz /depth_candidates/rgb_crops
```

## WSL2 실행

Intel Arc용 venv를 활성화한 뒤 실행한다.

```bash
source ~/MacRobot/.venv-embedding/bin/activate
source /opt/ros/jazzy/setup.bash
source ~/MacRobot/install/setup.bash

ros2 launch macrobot_object_finder object_finder_wsl.launch.py
```

이 launch는 다음을 실행한다.

```text
candidate_filter_node
embedding_retrieval_node
temporal_confirmation_node
object_finder_node
```

Temporal node의 직접 legacy `/object_finder/result`는 비활성화되어, canonical result publisher는 하나만 남는다.

## 찾기 명령

```bash
ros2 run macrobot_object_finder object_finder_cli \
  find Buds3 --timeout 60
```

한 번 찾고 종료하는 session:

```bash
ros2 run macrobot_object_finder object_finder_cli \
  find Buds3 --timeout 60 --once
```

등록 이미지를 강제로 다시 임베딩:

```bash
ros2 run macrobot_object_finder object_finder_cli \
  find Buds3 --rebuild-banks
```

직접 topic:

```bash
ros2 topic pub --once /object_finder/goal std_msgs/msg/String \
  "{data: '{\"object_name\":\"Buds3\",\"timeout_sec\":60.0,\"continuous\":true}'}"
```

## 결과와 상태

```bash
ros2 topic echo --full-length --field data /object_finder/result
ros2 topic echo --full-length --field data /object_finder/status
ros2 topic echo /object_finder/point_camera
```

`/object_finder/point_camera`는 full image가 아니라 한 개의 `PointStamped`다.

## 취소

```bash
ros2 run macrobot_object_finder object_finder_cli cancel
```

## 새 물체 등록

1. `d435_capture_crop`으로 positive와 negative를 촬영한다.
2. Pi의 data tree를 WSL에 복사한다.

```bash
rsync -av <PI_USER>@<PI_IP>:~/MacRobot/data/ ~/MacRobot/data/
```

3. 새 target으로 finder를 실행한다.

```bash
ros2 run macrobot_object_finder object_finder_cli \
  find Cup --rebuild-banks
```

## pick pipeline 연동

`pick_coordinator_node`는 이미 `/object_finder/goal`을 발행한다. 따라서 Pi에서 pick stack을 실행하고 WSL에서 이 finder launch를 실행하면 자동 연동된다.

```text
pick goal
→ object_finder goal
→ D435 detector
→ /object_finder/result
→ detection localizer
→ base alignment / arm pick
```

자세한 구조는 `docs/PIPELINE_KO.md`, 결과 계약은 `docs/RESULT_CONTRACT_KO.md`를 확인한다.
