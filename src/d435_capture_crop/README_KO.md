# MacRobot D435 촬영·크롭 노드 v1

Intel RealSense D435/D435f가 Raspberry Pi에서 발행하는 ROS 2 이미지 토픽을 구독하고, 사용자가 브라우저에서 **촬영 → 프레임 고정 → 드래그 크롭 → Depth 확인 → 최종 저장**을 수행하는 패키지입니다.

기존 USB 카메라를 직접 여는 `cv2.VideoCapture` 방식과 달리, 이 노드는 `realsense2_camera`가 발행하는 다음 토픽을 사용합니다.

```text
/camera/camera/color/image_raw
/camera/camera/aligned_depth_to_color/image_raw
/camera/camera/color/camera_info
```

## 설계 원칙

```text
D435 / realsense2_camera
        │
        ├─ color Image
        ├─ aligned depth Image
        └─ color CameraInfo
        │
        ▼
Raspberry Pi: d435_capture_crop_node
        │
        ├─ 최신 프레임만 보관
        ├─ 저속 JPEG 웹 미리보기
        ├─ 촬영 시 RGB + 가장 가까운 depth 프레임 고정
        └─ 사용자가 저장을 누를 때만 디스크 기록
        │
        ▼
Windows PC 브라우저
        ├─ 물체명/뷰 라벨 입력
        ├─ 현재 프레임 촬영
        ├─ 사각형 crop 드래그
        ├─ 선택 영역의 depth 통계 확인
        └─ 최종 저장 또는 폐기
```

이 패키지는 기존 USB 촬영 노드와 충돌하지 않도록 새 ROS 패키지 `d435_capture_crop`으로 분리했습니다. 기존 촬영 노드가 8090 포트를 사용 중이라면 먼저 종료하거나 이 노드의 `port`를 변경해야 합니다.

---

## 1. 제공 파일

```text
d435_capture_crop/
├── config/
│   └── d435_capture_crop.yaml
├── d435_capture_crop/
│   ├── __init__.py
│   ├── capture_core.py
│   ├── d435_capture_crop_node.py
│   └── web_server.py
├── launch/
│   └── d435_capture_crop.launch.py
├── resource/
│   └── d435_capture_crop
├── test/
│   └── test_capture_core.py
├── web/
│   ├── app.js
│   ├── index.html
│   └── style.css
├── package.xml
├── setup.cfg
└── setup.py
```

---

## 2. Raspberry Pi 설치

압축을 푼 뒤 패키지를 작업공간으로 복사합니다.

```bash
mkdir -p ~/MacRobot/src

cp -a \
  macrobot_d435_capture_crop_v1/d435_capture_crop \
  ~/MacRobot/src/
```

필요 패키지를 설치합니다.

```bash
sudo apt update
sudo apt install -y \
  ros-jazzy-cv-bridge \
  python3-opencv \
  python3-numpy
```

빌드합니다.

```bash
cd ~/MacRobot
source /opt/ros/jazzy/setup.bash

rm -rf \
  build/d435_capture_crop \
  install/d435_capture_crop

colcon build \
  --symlink-install \
  --packages-select d435_capture_crop
```

환경을 적용합니다.

```bash
source /opt/ros/jazzy/setup.bash
source ~/MacRobot/install/setup.bash
```

실행 파일을 확인합니다.

```bash
ros2 pkg executables d435_capture_crop
```

예상 결과:

```text
d435_capture_crop d435_capture_crop_node
```

---

## 3. D435 실행

Raspberry Pi에서 RealSense ROS wrapper를 실행합니다.

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
  enable_sync:=true \
  rgb_camera.color_profile:=640x480x30 \
  depth_module.depth_profile:=640x480x30 \
  rgb_camera.color_format:=RGB8 \
  depth_module.depth_format:=Z16
```

실제 토픽을 확인합니다.

```bash
ros2 topic list | grep -E "color/image_raw|aligned_depth|camera_info"
```

기본 설정에서 필요한 토픽:

```text
/camera/camera/color/image_raw
/camera/camera/aligned_depth_to_color/image_raw
/camera/camera/color/camera_info
```

주기를 확인합니다.

```bash
ros2 topic hz /camera/camera/color/image_raw
ros2 topic hz /camera/camera/aligned_depth_to_color/image_raw
```

---

## 4. 촬영·크롭 노드 실행

새 Pi 터미널에서:

```bash
source /opt/ros/jazzy/setup.bash
source ~/MacRobot/install/setup.bash

ros2 launch \
  d435_capture_crop \
  d435_capture_crop.launch.py
```

정상 로그 예:

```text
D435 capture/crop node ready: color='/camera/camera/color/image_raw',
depth='/camera/camera/aligned_depth_to_color/image_raw',
web='http://<PI_IP>:8090'
```

Raspberry Pi 주소 확인:

```bash
hostname -I
```

Windows PC 브라우저에서 다음 주소를 엽니다.

```text
http://라즈베리파이_IP:8090
```

WSL2 내부에서 GUI를 띄울 필요는 없습니다. Windows 브라우저가 Pi의 HTTP UI에 직접 접속합니다.

---

## 5. 사용 순서

1. `물체 이름`에 `Buds3`처럼 저장할 이름을 입력합니다.
2. `뷰 라벨`에 `front`, `left`, `right`, `tilted`처럼 촬영 각도를 입력합니다.
3. 실시간 화면에서 `현재 프레임 촬영`을 누릅니다.
4. 프레임이 고정되면 물체 주변을 드래그합니다.
5. 오른쪽 crop 미리보기와 aligned-depth 대표 거리를 확인합니다.
6. 원본과 depth 저장 여부를 선택합니다.
7. `크롭 확정 및 저장`을 누릅니다.
8. 잘못 촬영했다면 `버리고 다시 촬영`을 누릅니다.

중요:

```text
촬영 버튼
→ RGB/depth 프레임을 메모리에 고정
→ 아직 파일을 만들지 않음

크롭 확정 및 저장 버튼
→ 이때 처음으로 파일을 생성
```

---

## 6. 저장 구조

기본 `base_dir`은 다음입니다.

```text
~/MacRobot/data
```

`Buds3`, `front`로 저장한 예:

```text
~/MacRobot/data/
├── objects/
│   └── Buds3/
│       └── 20260728_153012_123_front_a1b2c3_original.jpg
│
└── curated/
    ├── objects/
    │   └── Buds3/
    │       └── 20260728_153012_123_front_a1b2c3.jpg
    │
    ├── depth/
    │   └── Buds3/
    │       └── 20260728_153012_123_front_a1b2c3_depth.png
    │
    └── metadata/
        └── Buds3/
            └── 20260728_153012_123_front_a1b2c3.json
```

각 파일의 의미:

```text
objects/<물체명>/*_original.jpg
→ D435 전체 RGB 원본

curated/objects/<물체명>/*.jpg
→ 사용자가 확정한 RGB crop
→ 품질 평가와 embedding view bank에 바로 사용

curated/depth/<물체명>/*_depth.png
→ 같은 영역의 aligned depth
→ uint16 millimeter PNG

curated/metadata/<물체명>/*.json
→ ROI, 거리 통계, RGB/depth timestamp 차이,
  CameraInfo 내부 파라미터, 파일 경로, 메모
```

---

## 7. Depth 정보

사용자가 crop을 선택하면 노드는 같은 영역의 depth에서 다음 통계를 계산합니다.

```text
median_m
→ 대표 거리

near_m / far_m
→ 유효 depth의 10% / 90% percentile

valid_ratio
→ 선택 영역 중 정상 depth가 있는 픽셀 비율

RGB–Depth 시간차
→ 고정된 color와 depth timestamp 차이
```

D435의 일반적인 `16UC1` depth는 기본적으로 다음 scale을 적용합니다.

```yaml
depth_scale_m: 0.001
```

즉 raw 값 500은 0.500m로 해석합니다. 실제 카메라 설정이 다르면 YAML을 수정하십시오.

---

## 8. 기존 CLI 촬영 명령과의 호환

다음 명령도 사용할 수 있습니다.

```bash
ros2 topic pub --once \
  /capture_object_name \
  std_msgs/msg/String \
  "{data: 'Buds3'}"
```

이 명령은 최신 프레임을 **고정만** 합니다. 최종 crop과 저장은 브라우저에서 수행합니다.

뷰 라벨도 같이 보내려면 JSON 문자열을 사용합니다.

```bash
ros2 topic pub --once \
  /capture_object_name \
  std_msgs/msg/String \
  "{data: '{\"object_name\":\"Buds3\",\"view_label\":\"left\"}'}"
```

상태 확인:

```bash
ros2 topic echo /object_camera_capture/status
```

저장 결과 확인:

```bash
ros2 topic echo /object_camera_capture/result
```

---

## 9. 주요 설정

파일:

```text
~/MacRobot/src/d435_capture_crop/config/d435_capture_crop.yaml
```

### 웹 포트 변경

기존 노드가 8090을 사용 중이면:

```yaml
port: 8092
```

브라우저:

```text
http://라즈베리파이_IP:8092
```

### 미리보기 부하 감소

Pi 또는 Wi-Fi 부담이 크면:

```yaml
preview_hz: 3.0
preview_max_width: 480
preview_jpeg_quality: 55
```

저장되는 원본과 crop 해상도에는 영향을 주지 않습니다. 이 설정은 브라우저 live preview만 줄입니다.

### Depth 동기화 허용 범위

촬영 화면에서 `Depth 없음`이 자주 뜨지만 두 토픽이 정상이라면:

```yaml
depth_sync_tolerance_sec: 0.180
```

먼저 `enable_sync:=true`를 사용하고, 실제 RGB/depth 시간차를 확인한 뒤 넓히는 것이 좋습니다.

### 최소 crop 크기

```yaml
min_crop_width_px: 24
min_crop_height_px: 24
```

너무 작은 이미지는 이후 임베딩 검색에 유용하지 않으므로 기본적으로 거절합니다.

### 세션 유지 시간

```yaml
session_timeout_sec: 600.0
```

10분 동안 저장하지 않은 고정 프레임은 메모리에서 폐기됩니다. `0.0`이면 자동 만료하지 않습니다.

---

## 10. 문제 해결

### 브라우저에 실시간 화면이 없음

Pi에서:

```bash
ros2 topic hz /camera/camera/color/image_raw
```

그리고 노드 파라미터를 확인합니다.

```bash
ros2 param get /d435_capture_crop color_topic
```

실제 토픽 이름이 다르면 실행 시 덮어씁니다.

```bash
ros2 run d435_capture_crop d435_capture_crop_node --ros-args \
  -p color_topic:=/실제/color/topic \
  -p depth_topic:=/실제/aligned_depth/topic
```

### RGB는 보이지만 Depth가 없음

```bash
ros2 topic hz /camera/camera/aligned_depth_to_color/image_raw
```

RealSense 실행에서 다음이 있어야 합니다.

```text
align_depth.enable:=true
enable_sync:=true
```

### 8090 포트가 이미 사용 중

```bash
sudo ss -ltnp | grep :8090
```

기존 `topic_camera_capture_node` 또는 다른 웹 노드를 종료하거나 포트를 바꿉니다.

### 저장은 되었지만 crop이 작거나 잘못됨

저장 전 crop preview의 해상도와 좌표를 확인하십시오. 잘못 선택했으면 저장하지 말고 `버리고 다시 촬영`을 사용합니다.

### 웹 UI 보안

이 서버에는 로그인 기능이 없습니다. 스마트폰 핫스팟 또는 전용 로봇 공유기처럼 신뢰할 수 있는 로컬 네트워크에서만 `host: 0.0.0.0`을 사용하십시오.

---

## 11. 다음 파이프라인과의 연결

이 노드가 만든 파일은 다음 구조로 바로 이어집니다.

```text
사용자 촬영 및 crop
→ curated/objects/Buds3/*.jpg
→ candidate_filter 색상 프로필
→ DINOv2/CLIP view-bank embedding 생성
→ positive/negative margin 평가
```

즉 등록용 이미지는 처음부터 물체 중심으로 crop되어 저장되므로, 기존 전체 프레임 등록 이미지보다 배경 영향을 줄일 수 있습니다.

---

## 12. 검증 상태

제작 환경에서 완료한 검증:

```text
Python 문법 검사
JavaScript 문법 검사
package.xml XML 파싱
YAML 파싱
Unicode/Hangul 파일명 정리 테스트
ROI clamp와 역방향 드래그 테스트
RGB–depth 해상도 매핑 테스트
16UC1 depth meter 변환 테스트
Depth percentile 통계 테스트
JPEG encode 및 atomic write 테스트
```

순수 로직 테스트 6개가 통과했습니다. 실제 ROS 2 Jazzy, D435 USB 장치, Pi 브라우저 통신에 대한 최종 `colcon build`와 실기 검증은 Raspberry Pi에서 수행해야 합니다.
