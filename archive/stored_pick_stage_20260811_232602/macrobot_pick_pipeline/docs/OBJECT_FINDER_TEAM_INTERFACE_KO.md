# 물체 탐색 팀 ROS 2 연동 계약

이 문서는 물체 탐색 알고리즘을 담당하는 팀원이 **카메라 입력을 어디서 받고**, **어떤 목표 명령을 구독하며**, **어떤 결과를 발행해야 하는지**를 고정한다.

알고리즘 내부 구조는 자유다. DINOv2, detection model, segmentation, tracking, multi-view retrieval 중 무엇을 사용하더라도 아래 입출력 계약만 유지하면 `macrobot_pick_pipeline`, 차체 정렬, 로봇팔 pick 코드와 연결된다.

---

## 1. RealSense D435 입력

권장 실행:

```bash
ros2 launch realsense2_camera rs_launch.py \
  enable_color:=true \
  enable_depth:=true \
  enable_infra1:=false \
  enable_infra2:=false \
  align_depth.enable:=true \
  enable_sync:=true \
  pointcloud.enable:=true \
  rgb_camera.color_profile:=640x480x30 \
  depth_module.depth_profile:=640x480x30 \
  rgb_camera.color_format:=RGB8 \
  depth_module.depth_format:=Z16
```

설치된 RealSense wrapper 버전에 따라 namespace가 달라질 수 있으므로 실제 토픽을 먼저 확인한다.

```bash
ros2 topic list | grep camera
```

현재 프로젝트 기본 토픽:

| 토픽 | 타입 | 의미 |
|---|---|---|
| `/camera/camera/color/image_raw` | `sensor_msgs/msg/Image` | RGB 영상 |
| `/camera/camera/aligned_depth_to_color/image_raw` | `sensor_msgs/msg/Image` | color pixel과 정렬된 depth |
| `/camera/camera/color/camera_info` | `sensor_msgs/msg/CameraInfo` | color intrinsics `fx, fy, cx, cy` |
| `/camera/camera/depth/color/points` | `sensor_msgs/msg/PointCloud2` | 선택적 aligned point cloud |

### 영상·depth 의미

- `center_x`, `center_y`는 **color image pixel 좌표**다.
- `depth_m`는 해당 color pixel 또는 object mask 내부의 대표 깊이를 **meter**로 변환한 값이다.
- `Z16` depth image는 일반적으로 raw integer이므로 wrapper의 depth scale을 반영해야 한다. 결과 topic에는 반드시 meter를 넣는다.
- RGB와 depth는 같은 시점이어야 한다. 가능하면 message header timestamp를 보존한다.
- image subscriber는 `qos_profile_sensor_data` 또는 이에 대응하는 Best Effort QoS를 사용한다.

### 좌표계

ROS optical frame:

```text
+X: 영상 오른쪽
+Y: 영상 아래
+Z: 카메라가 보는 방향
```

주요 TF frame은 설치된 wrapper에서 확인한다.

```bash
ros2 run tf2_ros tf2_echo base_link camera_color_optical_frame
```

대표 frame 이름:

```text
camera_link
camera_depth_frame
camera_depth_optical_frame
camera_color_frame
camera_color_optical_frame
```

aligned depth와 color pixel을 사용하면 source frame은 보통 `camera_color_optical_frame`이다.

---

## 2. 탐색 제어 입력

### `/object_finder/goal`

타입:

```text
std_msgs/msg/String
```

JSON 예:

```json
{
  "object_name": "Buds3",
  "timeout_sec": 60.0,
  "continuous": true,
  "request_id": "align-pick-..."
}
```

필드:

| 필드 | 필수 | 의미 |
|---|---:|---|
| `object_name` | 예 | 찾을 등록 물체 이름 |
| `timeout_sec` | 권장 | 탐색 제한 시간 |
| `continuous` | 권장 | 한 번 찾은 뒤에도 추적 결과를 계속 발행할지 |
| `request_id` | 선택 | 상위 요청 correlation용 |

### `/object_finder/cancel`

타입:

```text
std_msgs/msg/String
```

수신 즉시 현재 탐색/추적을 중단하고 내부 track을 정리한다.

### `/macrobot/pick/active_target`

타입:

```text
std_msgs/msg/String
```

상위 pick/alignment 계층이 현재 활성 물체 이름을 발행한다. 팀 알고리즘은 `/object_finder/goal`을 주 입력으로 사용하되, 이 토픽을 target switch 또는 디버그 상태 동기화에 활용할 수 있다. 빈 문자열은 target 해제를 의미한다.

---

## 3. 탐색 결과 출력 계약

두 형식 중 하나를 선택한다. 현재 설치 기본값은 legacy JSON이다.

## 3.1 즉시 호환되는 legacy JSON

토픽:

```text
/object_finder/result
```

타입:

```text
std_msgs/msg/String
```

### 방식 A: pixel + depth

```json
{
  "event": "object_found",
  "found": true,
  "object_name": "Buds3",
  "score": 0.82,
  "center_px": {"x": 321.4, "y": 238.7},
  "depth_m": 0.428,
  "frame_id": "camera_color_optical_frame",
  "stamp_sec": 1780000000.123,
  "track_id": 12
}
```

필수 필드:

```text
found=true
object_name
score
center_px.x / center_px.y
depth_m
```

권장 필드:

```text
event=object_found
frame_id
stamp_sec
track_id
bbox 또는 roi
```

### 방식 B: 이미 base_link 3D 좌표를 계산한 경우

```json
{
  "event": "object_found",
  "found": true,
  "object_name": "Buds3",
  "score": 0.82,
  "point_base": {"x": -0.31, "y": 0.064, "z": 0.105},
  "frame_id": "base_link",
  "stamp_sec": 1780000000.123
}
```

`point_base`가 있으면 `detection_localizer_node`는 pixel projection을 생략한다. 단, TF와 timestamp를 잘못 처리하면 차체 정렬 오차가 직접 발생하므로, 팀 알고리즘이 3D TF를 책임질 수 있을 때만 이 방식을 사용한다.

### 탐색 실패/timeout

```json
{
  "event": "object_not_found",
  "found": false,
  "object_name": "Buds3",
  "reason": "timeout"
}
```

상위 코드는 `found=false` 결과를 위치 표본으로 사용하지 않는다.

---

## 3.2 권장 typed 결과

토픽:

```text
/temporal_confirmation/confirmed
```

타입:

```text
macrobot_interfaces/msg/TemporalConfirmationResult
```

필수로 채울 필드:

```text
header.stamp
header.frame_id
 target_object
track_id
state = confirmed
event = confirmed 또는 update
confirmed = true
temporal_score
roi
center_x
center_y
depth_m
center_std_px
depth_std_m
horizontal_error_norm
suggested_turn
```

`macrobot_pick_pipeline/config/perception.yaml`에서 다음으로 변경한다.

```yaml
input_mode: typed
```

`both`도 지원하지만 같은 frame을 JSON과 typed로 동시에 발행하면 안정화 표본이 중복될 수 있으므로 운영 시에는 한 형식을 선택하는 것이 좋다.

---

## 4. score와 안정성 의미

- `score` 또는 `temporal_score`는 0~1 범위의 단조로운 신뢰도 값으로 사용한다.
- 확률 calibration까지 요구하지는 않지만, 더 확실한 결과가 더 높은 값을 가져야 한다.
- 한 frame의 raw detection보다 여러 frame의 동일 track을 확인한 결과가 권장된다.
- `center_px`와 `depth_m`는 동일한 object instance/track의 값이어야 한다.
- 오래된 결과를 반복 publish하지 말고 sensor timestamp를 유지한다.

차체 정렬과 pick은 기본적으로 최근 1.5초 안의 5개 표본이 약 12 mm 이내로 모일 때만 움직인다. 이 값은 alignment/pick profile에서 조정된다.

---

## 5. 탐색 결과 이후의 기존 노드

팀 알고리즘은 아래 로직을 구현할 필요가 없다.

```text
/object_finder/result 또는 typed confirmed
        ↓
detection_localizer_node
        ↓
/macrobot/perception/localized_detection   # base_link JSON
/macrobot/perception/object_point          # PointStamped
        ↓
base_alignment_node
        ↓
TURN_DEG / MOVE_CM 반복
        ↓
pick_coordinator_node
        ↓
/macrobot/arm/joint_goal
        ↓
validator → safe-region → servo bridge
```

`/macrobot/perception/localized_detection` 예:

```json
{
  "event": "localized_object",
  "object_name": "Buds3",
  "score": 0.82,
  "frame_id": "base_link",
  "point_base": {"x": -0.31, "y": 0.064, "z": 0.105},
  "stamp_sec": 1780000000.123,
  "source": "legacy_pixel_depth_projection"
}
```

---

## 6. 기존 후보 파이프라인을 재사용하는 경우

Pi 측 후보 생성 패키지를 그대로 사용할 수 있다.

```text
/depth_candidates/candidates
  macrobot_interfaces/msg/DepthCandidateArray

/depth_candidates/rgb_crops
  macrobot_interfaces/msg/RgbCandidateCrop
```

WSL/PC 측 알고리즘은 `/depth_candidates/rgb_crops`를 입력으로 받아 자체 모델을 실행하고, 최종 결과만 위 계약으로 발행하면 된다.

---

## 7. 최소 통합 테스트

카메라 입력:

```bash
ros2 topic hz /camera/camera/color/image_raw
ros2 topic hz /camera/camera/aligned_depth_to_color/image_raw
ros2 topic echo --once /camera/camera/color/camera_info
```

탐색 goal:

```bash
ros2 topic pub --once /object_finder/goal std_msgs/msg/String \
  "{data: '{\"object_name\":\"Buds3\",\"timeout_sec\":60.0,\"continuous\":true}'}"
```

결과:

```bash
ros2 topic echo --full-length --field data /object_finder/result
```

localizer 결과:

```bash
ros2 topic echo --full-length --field data \
  /macrobot/perception/localized_detection

ros2 topic echo /macrobot/perception/object_point
```

TF:

```bash
ros2 run tf2_ros tf2_echo base_link camera_color_optical_frame
```

---

## 8. 팀원이 변경하면 안 되는 하위 제어 경로

탐색 알고리즘은 다음 토픽에 직접 명령을 보내지 않는다.

```text
/pico_debug/cmd
/macrobot/arm/validated_joint_goal
/macrobot/arm/logical_joint_states
```

탐색 팀의 책임 경계는 **물체 이름, 신뢰도, pixel/depth 또는 base_link 3D point를 안정적으로 출력하는 것**까지다.
