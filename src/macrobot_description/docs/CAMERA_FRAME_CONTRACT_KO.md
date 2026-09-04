# 카메라 프레임 계약

`camera_link`는 D435 하우징 중심이 아니라 RGB 렌즈에 붙인 1 mm CAD 마커의 중심입니다.

```text
base_link -> camera_link
xyz = -0.030650 0.060623 0.025820 m
rpy = 0.0 0.0 0.0
```

`camera_color_frame`, `camera_color_optical_frame`, `camera_depth_frame` 등의 내부 프레임은 이 URDF에 중복 정의하지 않습니다. 기존 `macrobot_camera_tf` 패키지가 `camera_link`를 anchor로 사용하고 RealSense wrapper는 `publish_tf:=false`로 실행해야 합니다.

이번 CAD 내보내기에서 `base_link -> camera_link`는 r3와 동일하므로 기존 RGB-anchor calibration 파일을 유지할 수 있습니다. 다만 실제 실행 시 TF 중복과 optical 축은 다시 확인해야 합니다.
