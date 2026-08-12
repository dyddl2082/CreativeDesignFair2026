# Pick Pipeline 연동

```text
/object_finder/result
→ detection_localizer_node
→ Pi aligned depth refinement
→ TF(base_link)
→ /macrobot/perception/localized_detection
→ stored_object_pick_node
→ visual alignment
→ semantic grasp keyframes
```

신규 stored profile은 다음처럼 기록한다.

```bash
ros2 run macrobot_pick_pipeline stored_object_pick_cli \
  record Eraser --profile Eraser --grasp-keyframes Eraser
```
