# MacRobot D435 detector 배치 구조

## Raspberry Pi

```text
D435 color + aligned depth
→ depth_candidate_proposal
→ /depth_candidates/candidates        작은 metadata
→ /depth_candidates/rgb_crops          후보별 JPEG + foreground mask
```

Pi에서는 전체 RGB/depth frame을 WSL용 노드가 구독하지 않는다. `object_finder_pi.launch.py`는 depth debug와 top-crop preview도 기본 비활성화한다.

## WSL2

```text
candidate_filter
→ embedding_retrieval (DINOv2 / Intel Arc XPU)
→ temporal_confirmation
→ macrobot_object_finder
→ /object_finder/result
```

`macrobot_object_finder`는 이미지 토픽을 구독하지 않는다. CameraInfo, 후보 metadata, status, typed confirmation만 받는다.

## Raspberry Pi pick stack

```text
/object_finder/result
→ detection_localizer_node
→ /macrobot/perception/object_point
→ base alignment / pick coordinator
```
