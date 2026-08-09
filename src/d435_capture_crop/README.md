# d435_capture_crop

**상태:** 유지 · 데이터 제작 전용 · 실제 D435/Pi가 있을 때 사용

실시간 탐색에 항상 켜는 package가 아니라 positive/negative 등록 사진을 만드는 웹 도구다.

## 기능

- D435 color, aligned depth, CameraInfo 구독
- 브라우저에서 frame freeze와 ROI crop
- ROI depth 통계 확인
- positive, shared negative, background, hard negative 저장
- 등록 물체와 공용 negative를 target별 `_auto` 상대 symlink로 재사용

## 저장 경로

```text
positive:
~/MacRobot/data/curated/objects/<object>/

shared negative:
~/MacRobot/data/negative/library/<label>/

background:
~/MacRobot/data/negative/backgrounds/<scene>/

hard negative:
~/MacRobot/data/negative/confusers/<target>/manual/<label>/
```

## 빌드

```bash
cd ~/MacRobot
source /opt/ros/jazzy/setup.bash

rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install --packages-select d435_capture_crop

source ~/MacRobot/install/setup.bash
```

## 실행

RealSense를 먼저 실행한다.

```bash
ros2 launch realsense2_camera rs_launch.py \
  enable_color:=true \
  enable_depth:=true \
  align_depth.enable:=true \
  enable_sync:=true \
  rgb_camera.color_profile:=640x480x30 \
  depth_module.depth_profile:=640x480x30
```

촬영 UI:

```bash
ros2 launch d435_capture_crop d435_capture_crop.launch.py
```

브라우저:

```text
http://<PI_IP>:8090
```

## CLI frame freeze

Positive:

```bash
ros2 topic pub --once \
  /capture_object_name \
  std_msgs/msg/String \
  "{data: 'Buds3'}"
```

Hard negative:

```bash
ros2 topic pub --once \
  /capture_object_name \
  std_msgs/msg/String \
  "{data: '{\"dataset_role\":\"hard_negative\",\"object_name\":\"white_cup\",\"target_object\":\"Buds3\",\"view_label\":\"close\"}'}"
```

CLI는 frame을 고정하고, crop 확정과 저장은 브라우저에서 한다.

## Pi→WSL 데이터 동기화

```bash
rsync -av \
  <PI_USER>@<PI_IP>:~/MacRobot/data/ \
  ~/MacRobot/data/
```

동기화 후 profile/bank/track 갱신:

```bash
ros2 service call /candidate_filter/reload_profile \
  std_srvs/srv/Trigger "{}"

ros2 service call /embedding_retrieval/rebuild_banks \
  std_srvs/srv/Trigger "{}"

ros2 service call /temporal_confirmation/reset \
  std_srvs/srv/Trigger "{}"
```

## 주의

웹 preview와 JPEG/depth 저장은 Pi 부하를 늘리므로 데이터 수집이 끝나면 종료한다. `_auto` symlink 보존을 위해 동기화에는 `rsync -a`를 사용한다.
