# Object Finder 결과 계약 v0.2

토픽:

```text
/object_finder/result  std_msgs/msg/String JSON
```

정상 예:

```json
{
  "event": "object_found",
  "found": true,
  "object_name": "Eraser",
  "score": 0.74,
  "center_px": {"x": 318.4, "y": 242.1},
  "depth_m": 0.41,
  "frame_id": "camera_color_optical_frame",
  "stamp_sec": 1780000000.1,
  "track_id": 12,
  "center_std_px": 2.8,
  "depth_std_m": 0.01,
  "localization": {
    "available": true,
    "method": "dinov2_patch_margin",
    "quality": 0.87
  },
  "orientation": {
    "angle_deg": 8.3,
    "class": "horizontal",
    "quality": 0.78
  }
}
```

`center_px`는 candidate bbox 중심이 아니라 DINOv2 patch heatmap으로 정제된 물체 내부 중심이다. `depth_m`은 temporal candidate depth이고, Raspberry Pi의 localizer가 이 pixel의 aligned depth를 다시 표본화한다.

이미지 중심 기반 `turn_left`, `turn_right`, `suggested_turn` 필드는 제공하지 않는다. 실제 정렬은 TF를 적용한 `base_link` 3D point를 사용한다.
