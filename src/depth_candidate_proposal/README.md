# depth_candidate_proposal 0.2.0

Raspberry Pi-side edge vision for MacRobot on ROS 2 Jazzy.

The package now runs two independent nodes:

```text
D435f aligned depth ──> aligned_depth_candidate
                              │
                              └─ /depth_candidates/candidates
                                            │
D435f RGB ────────────> rgb_candidate_crop ─┤
                                            ├─ /depth_candidates/rgb_crops
                                            └─ /depth_candidates/top_rgb_crop/compressed
```

`aligned_depth_candidate` performs depth segmentation and bbox generation.
`rgb_candidate_crop` keeps a short buffer of RGB frames, matches each proposal
frame by timestamp, extracts the corresponding RGB ROIs, and publishes one
bounded JPEG message per candidate. Expensive identity recognition remains on
the WSL2 PC.

Keeping the stages as separate nodes gives independent QoS, rates, profiling,
and failure handling while keeping both executables in one Pi-side package.

## Packages and interfaces

Copy both updated package directories into `~/MacRobot/src`:

- `macrobot_interfaces`
- `depth_candidate_proposal`

New interface:

```text
macrobot_interfaces/msg/RgbCandidateCrop
```

Important fields:

```text
proposal_header             depth proposal timestamp
image.header                matched RGB timestamp
candidate                   original depth candidate and distance metadata
crop_roi                    actual ROI applied to the RGB frame
color_time_offset_sec       RGB timestamp - depth proposal timestamp
frame_crop_count            crop messages expected for this proposal frame
crop_index                  index in the current crop frame
encoded_width/height        JPEG dimensions after optional downscaling
jpeg_size_bytes             final payload size
jpeg_quality                quality selected by the adaptive encoder
size_limit_met              whether max_jpeg_bytes was met
image                       sensor_msgs/CompressedImage containing the JPEG
```

A proposal frame with three selected candidates produces three
`RgbCandidateCrop` messages with the same `proposal_header`,
`frame_crop_count=3`, and `crop_index=0,1,2`.

## Why each crop is a separate message

Publishing a single array containing every JPEG would create a large DDS sample.
One message per candidate keeps samples small, lets the PC start inference
immediately, and prevents one large batch from being lost as a unit.

The encoder first lowers JPEG quality and then reduces resolution until the
configured `max_jpeg_bytes` target is met. The default target is 55 kB.

## Install dependencies on Raspberry Pi

```bash
sudo apt update
sudo apt install -y \
  ros-jazzy-cv-bridge \
  python3-opencv \
  python3-numpy
```

## Replace v1 and rebuild on Raspberry Pi

After copying the two v2 package directories into `~/MacRobot/src`:

```bash
cd ~/MacRobot
source /opt/ros/jazzy/setup.bash

rm -rf \
  build/macrobot_interfaces \
  install/macrobot_interfaces \
  build/depth_candidate_proposal \
  install/depth_candidate_proposal

rosdep install --from-paths src --ignore-src -r -y

colcon build --symlink-install --packages-select \
  macrobot_interfaces \
  depth_candidate_proposal

source ~/MacRobot/install/setup.bash
```

Check the new message and executable:

```bash
ros2 interface show macrobot_interfaces/msg/RgbCandidateCrop
ros2 pkg executables depth_candidate_proposal
```

Expected executables include:

```text
depth_candidate_proposal aligned_depth_candidate_node
depth_candidate_proposal rgb_candidate_crop_node
```

## Update the interface package on WSL2

The PC does not need the Pi processing package yet, but it must have the exact
same custom message definition before it can inspect or subscribe to crop data.
Copy only the updated `macrobot_interfaces` package to WSL2, then rebuild:

```bash
cd ~/MacRobot
source /opt/ros/jazzy/setup.bash

rm -rf build/macrobot_interfaces install/macrobot_interfaces

colcon build --symlink-install --packages-select macrobot_interfaces
source ~/MacRobot/install/setup.bash
```

Verify:

```bash
ros2 interface show macrobot_interfaces/msg/RgbCandidateCrop
```

## Run RealSense

```bash
source /opt/ros/jazzy/setup.bash
source ~/MacRobot/install/setup.bash

ros2 launch realsense2_camera rs_launch.py \
  enable_color:=true \
  enable_depth:=true \
  enable_infra1:=false \
  enable_infra2:=false \
  pointcloud.enable:=false \
  align_depth.enable:=true \
  rgb_camera.color_profile:=640x480x30 \
  depth_module.depth_profile:=640x480x30 \
  rgb_camera.color_format:=RGB8 \
  depth_module.depth_format:=Z16
```

## Run both Pi nodes

```bash
source /opt/ros/jazzy/setup.bash
source ~/MacRobot/install/setup.bash

ros2 launch depth_candidate_proposal edge_candidate_pipeline.launch.py
```

The original depth-only launch remains available:

```bash
ros2 launch depth_candidate_proposal depth_candidate.launch.py
```

Run only the crop extractor when the depth node is already running:

```bash
ros2 launch depth_candidate_proposal rgb_candidate_crop.launch.py
```

## Topics

Inputs:

```text
/camera/camera/aligned_depth_to_color/image_raw  sensor_msgs/Image
/camera/camera/color/camera_info                 sensor_msgs/CameraInfo
/camera/camera/color/image_raw                   sensor_msgs/Image
/depth_candidates/candidates                     macrobot_interfaces/DepthCandidateArray
```

Outputs:

```text
/depth_candidates/candidates                     macrobot_interfaces/DepthCandidateArray
/depth_candidates/debug/compressed               sensor_msgs/CompressedImage
/depth_candidates/rgb_crops                      macrobot_interfaces/RgbCandidateCrop
/depth_candidates/top_rgb_crop/compressed        sensor_msgs/CompressedImage
```

The top-crop preview is only a low-rate test stream. The real PC inference input
is `/depth_candidates/rgb_crops` because it preserves candidate metadata.

## Verify on Raspberry Pi

```bash
ros2 topic hz /depth_candidates/candidates
ros2 topic hz /depth_candidates/rgb_crops
ros2 topic bw /depth_candidates/rgb_crops
```

Inspect one crop message. The default crop publisher is Best Effort:

```bash
ros2 topic echo \
  --qos-reliability best_effort \
  --once \
  /depth_candidates/rgb_crops \
  macrobot_interfaces/msg/RgbCandidateCrop
```

Useful fields to inspect:

```text
candidate.id
candidate.roi
crop_roi
candidate.median_depth_m
candidate.proposal_score
color_time_offset_sec
jpeg_size_bytes
jpeg_quality
size_limit_met
```

## Verify on WSL2 without the ros2cli daemon

Use the network environment that already worked for Pi-to-WSL communication:

```bash
source /opt/ros/jazzy/setup.bash
source ~/MacRobot/install/setup.bash

export ROS_DOMAIN_ID=42
export ROS_AUTOMATIC_DISCOVERY_RANGE=SUBNET
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
unset ROS_LOCALHOST_ONLY
```

List the topics without the daemon:

```bash
ros2 topic list --no-daemon --spin-time 3.0 -t | grep depth_candidates
```

Inspect one crop message:

```bash
ros2 topic echo \
  --no-daemon \
  --spin-time 3.0 \
  --qos-reliability best_effort \
  --once \
  /depth_candidates/rgb_crops \
  macrobot_interfaces/msg/RgbCandidateCrop
```

Measure the crop stream:

```bash
ros2 topic hz /depth_candidates/rgb_crops --spin-time 3.0
ros2 topic bw /depth_candidates/rgb_crops
```

`rgb_crops` publishes one message per candidate, so this Hz value is the crop
message rate rather than the proposal-frame rate. Use
`/depth_candidates/candidates` for proposal-frame Hz, or group crop messages by
`proposal_header` and `frame_crop_count` on the PC.

## View the top candidate crop

The optional preview is a standard compressed image topic. On WSL2:

```bash
ros2 run image_view image_view --ros-args \
  -r image:=/depth_candidates/top_rgb_crop \
  -p image_transport:=compressed
```

Do not remap `image` directly to the `/compressed` suffix. Use the base topic
shown above and select `compressed` as the transport.

## Timestamp matching

The crop node does not simply use the newest RGB frame. It finds the buffered
RGB image whose timestamp is closest to `DepthCandidateArray.header.stamp`.
This avoids applying an old bbox to a newer image while the robot or object is
moving.

Defaults:

```yaml
color_buffer_size: 45
sync_tolerance_sec: 0.080
allow_latest_color_fallback: false
```

At RGB8 640x480, 45 buffered frames require roughly 42 MiB for image payloads.
If the node logs:

```text
No RGB frame within sync tolerance
```

first compare the logged closest time difference. If depth proposal processing
latency is longer than the buffer coverage, increase the YAML value and restart
the crop node:

```yaml
color_buffer_size: 60
```

The deque capacity is allocated when the node starts, so a runtime parameter
change does not resize the existing buffer.

If the streams themselves differ slightly in timestamp, increase tolerance:

```yaml
sync_tolerance_sec: 0.120
```

Keep `allow_latest_color_fallback: false` for moving scenes; enabling it can
produce visually incorrect crops.

## Main crop parameters

Initial settings:

```yaml
max_crops_per_frame: 6
min_proposal_score: 0.0
reject_border_candidates: false
extra_padding_px: 0
extra_padding_ratio: 0.0

max_crop_side_px: 320
jpeg_quality: 70
min_jpeg_quality: 35
max_jpeg_bytes: 55000
reliable_crop_output: false
```

### Reduce Wi-Fi load

```yaml
max_crops_per_frame: 3
min_proposal_score: 0.25
max_crop_side_px: 256
jpeg_quality: 60
max_jpeg_bytes: 40000
publish_top_crop_preview: false
```

### Include more visual context around the bbox

The depth proposal ROI already has `bbox_padding_px`. Add crop-side context only
when embedding matching benefits from it:

```yaml
extra_padding_ratio: 0.10
```

### Prefer delivery over freshness

The default crop publisher is Best Effort with a short queue. To request
retransmission instead:

```yaml
reliable_crop_output: true
```

The future PC subscriber must use matching Reliable QoS. Reliable delivery can
increase latency on an unstable wireless link, so Best Effort is the safer
starting point for live recognition.

## Status log

Every five seconds the crop node reports a line similar to:

```text
source=4, selected=4, published=4, frame=82.5 KiB,
sync=+2.1 ms, processing=8.7 ms,
totals(frames/crops/drops/oversize)=21/74/0/0
```

Interpretation:

```text
source       proposals produced by the depth node
selected     proposals left after score/border/max-count filtering
published    valid JPEG crops actually published
frame        sum of JPEG bytes for the current proposal frame
sync         RGB timestamp minus proposal timestamp
processing   crop extraction and encoding time
sync drops   frames rejected because no timestamp match was available
oversize     crops that could not meet max_jpeg_bytes even after adaptation
```

## Debug-stream change from v1

The depth debug stream is now half-resolution by default:

```yaml
debug_scale: 0.5
debug_jpeg_quality: 50
```

Its publisher queue depth is one and remains Best Effort. This reduces duplicate
network load while the new RGB crop stream is active.

## Unit tests

The pure NumPy/OpenCV proposal and crop helpers can be tested without a camera:

```bash
cd ~/MacRobot
source /opt/ros/jazzy/setup.bash
source ~/MacRobot/install/setup.bash

colcon test --packages-select depth_candidate_proposal
colcon test-result --verbose
```

## Current boundary

Implemented in v2:

```text
aligned depth proposal
bbox generation
RGB timestamp matching
RGB ROI extraction
adaptive JPEG compression
per-candidate metadata transport
low-rate top-crop preview
```

Still belongs on the WSL2 PC:

```text
crop decoding
color/shape filtering
DINOv2 or CLIP embedding inference
positive-view and negative-bank comparison
temporal confirmation
final /object_finder/result publication
```
