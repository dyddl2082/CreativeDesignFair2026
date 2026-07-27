# v2 changes

- Added `macrobot_interfaces/msg/RgbCandidateCrop.msg`.
- Added Pi-side `rgb_candidate_crop_node`.
- Matches proposal timestamps to buffered RGB frames.
- Maps proposal ROIs into RGB coordinates and clamps them safely.
- Publishes one bounded JPEG crop per candidate on `/depth_candidates/rgb_crops`.
- Adaptively lowers JPEG quality and crop resolution to target 55 kB or less.
- Limits candidates per frame and preserves full depth-candidate metadata.
- Added optional 1 Hz top-candidate preview for `image_view`.
- Added combined `edge_candidate_pipeline.launch.py`.
- Reduced depth debug stream to half resolution, JPEG quality 50, QoS depth 1.
