# depth_candidate_proposal

Raspberry Pi-side ROS 2 Jazzy node for MacRobot. It consumes the RealSense
aligned-depth image and the color CameraInfo, removes the dominant background
plane, extracts foreground connected components, and publishes small proposal
metadata instead of performing expensive object recognition on the Pi.

## Topics

Input:

- `/camera/camera/aligned_depth_to_color/image_raw` (`sensor_msgs/Image`)
- `/camera/camera/color/camera_info` (`sensor_msgs/CameraInfo`)

Output:

- `/depth_candidates/candidates` (`macrobot_interfaces/DepthCandidateArray`)
- `/depth_candidates/debug/compressed` (`sensor_msgs/CompressedImage`)

The output header is copied from the aligned-depth frame. A future PC-side node
should pair this message with the RGB frame using the timestamp and crop the RGB
image with each `roi`.

## Algorithm

1. Convert `16UC1` or `32FC1` depth to meters.
2. Keep the configured working range and image ROI.
3. Fit the dominant plane from downsampled 3D points with RANSAC.
4. Keep pixels closer than the fitted plane by `plane_clearance_m`.
5. Apply binary close/open morphology.
6. Extract and filter connected components.
7. Publish padded RGB-compatible ROIs and robust depth statistics.
8. Fall back to percentile foreground extraction when CameraInfo or a plane is unavailable.

## Build

```bash
sudo apt update
sudo apt install -y \
  ros-jazzy-cv-bridge \
  python3-opencv \
  python3-numpy

cd ~/MacRobot/src
# Copy macrobot_interfaces and depth_candidate_proposal here.

cd ~/MacRobot
source /opt/ros/jazzy/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install --packages-select \
  macrobot_interfaces depth_candidate_proposal
source ~/MacRobot/install/setup.bash
```

## Run

Start RealSense with color-depth alignment enabled, then:

```bash
ros2 launch depth_candidate_proposal depth_candidate.launch.py
```

Check:

```bash
ros2 topic hz /depth_candidates/candidates
ros2 topic echo /depth_candidates/candidates
ros2 topic info /depth_candidates/debug/compressed -v
```

On WSL2, `rqt_image_view` can be used to inspect the compressed debug topic.

## First parameters to tune

- Too much background remains: raise `plane_clearance_m` from `0.025` toward `0.04`.
- Small objects disappear: lower `min_component_area_px` and `min_bbox_*_px`.
- One object splits into fragments: raise `close_kernel_px` from `9` to `11` or `13`.
- Nearby objects merge: lower `close_kernel_px`.
- Robot body appears at the bottom: lower `roi_bottom_ratio`, for example `0.90`.
- Pi load is high: lower `process_hz`, raise `plane_sample_stride`, or lower `plane_ransac_iterations`.

The proposal score is only a sorting heuristic. It is not the final object identity
confidence; DINOv2/CLIP or another PC-side verifier should make that decision.
