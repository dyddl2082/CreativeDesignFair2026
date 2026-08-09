# depth_candidate_proposal

**상태:** 필수 · 사용자 목록에서 누락됨 · Raspberry Pi/D435 edge vision

## 역할

두 실행 노드를 한 package에 둔다.

```text
aligned_depth_candidate_node
- aligned depth에서 지배 평면 제거
- foreground mask와 connected component 생성
- bbox, center, median depth, stability, proposal score 계산

rgb_candidate_crop_node
- proposal timestamp와 가장 가까운 RGB frame 선택
- 후보 ROI crop/JPEG 생성
- candidate-local foreground mask PNG 생성
```

## 입출력

```text
입력:
/camera/camera/aligned_depth_to_color/image_raw
/camera/camera/color/image_raw
/camera/camera/color/camera_info

출력:
/depth_candidates/candidates
/depth_candidates/debug/compressed
/depth_candidates/rgb_crops
/depth_candidates/top_rgb_crop/compressed
```

`candidate_filter`는 `/depth_candidates/rgb_crops`가 없으면 동작하지 않는다.

## 빌드

```bash
cd ~/MacRobot
source /opt/ros/jazzy/setup.bash

rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install --packages-select \
  macrobot_interfaces \
  depth_candidate_proposal

source ~/MacRobot/install/setup.bash
```

## 실행

RealSense 실행 후:

```bash
ros2 launch depth_candidate_proposal edge_candidate_pipeline.launch.py
```

Depth node만:

```bash
ros2 launch depth_candidate_proposal depth_candidate.launch.py
```

Crop node만:

```bash
ros2 launch depth_candidate_proposal rgb_candidate_crop.launch.py
```

## 확인

```bash
ros2 topic hz /depth_candidates/candidates
ros2 topic hz /depth_candidates/rgb_crops
ros2 topic bw /depth_candidates/rgb_crops
```

```bash
ros2 topic echo --once \
  --qos-reliability best_effort \
  /depth_candidates/rgb_crops \
  macrobot_interfaces/msg/RgbCandidateCrop
```

```bash
ros2 run image_view image_view --ros-args \
  -r image:=/depth_candidates/top_rgb_crop \
  -p image_transport:=compressed
```

## 주요 설정

- `color_buffer_size`, `sync_tolerance_sec`
- `max_crops_per_frame`
- `min_proposal_score`
- `max_crop_side_px`, `jpeg_quality`, `max_jpeg_bytes`
- `reliable_crop_output`

RGB crop은 candidate당 한 메시지이므로 crop Hz는 proposal frame Hz보다 높을 수 있다.
