# `/object_finder/result` 계약

성공 예시:

```json
{
  "event": "object_found",
  "found": true,
  "object_name": "Buds3",
  "request_id": "find-...",
  "score": 0.82,
  "center_px": {"x": 321.0, "y": 239.0},
  "depth_m": 0.42,
  "frame_id": "camera_color_optical_frame",
  "stamp_sec": 10.5,
  "track_id": 7,
  "bbox": {"x": 10, "y": 20, "width": 30, "height": 40}
}
```

실패·timeout 예시:

```json
{
  "event": "object_not_found",
  "found": false,
  "object_name": "Buds3",
  "reason": "timeout"
}
```

`detection_localizer_node`는 `center_px + depth_m + frame_id`를 CameraInfo와 TF로 `base_link` 점으로 변환한다.
