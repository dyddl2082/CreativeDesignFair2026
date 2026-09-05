# macrobot_camera_tf

MacRobot의 URDF `camera_link` 원점이 D435 RGB 렌즈 중심에 놓인 경우를 위한 ROS 2 Jazzy TF 패키지다.

## 설계 원칙

- `base_link -> camera_link`는 CAD/URDF가 게시한다.
- `camera_link`의 원점은 RGB 렌즈 중심이다.
- RealSense wrapper의 장치 내부 센서 변환은 실제 장치에서 한 번 캡처한다.
- 정상 실행에서는 RealSense wrapper를 `publish_tf:=false`로 실행한다.
- 이 패키지가 `camera_link` 아래에 color/depth/infra body 및 optical frame을 정적 TF로 게시한다.
- 인식 위치화는 aligned depth와 color CameraInfo를 사용하므로 `camera_color_optical_frame`을 기준으로 고정한다.

RealSense wrapper의 기본 `camera_link` 원점은 RGB가 아니라 좌측 IR/depth 쪽이다. MacRobot은 같은 이름을 RGB 중심으로 사용하므로 wrapper TF를 그대로 켜면 서로 다른 의미의 `camera_link`가 충돌한다.

## camera_link 축 방향

원점이 RGB 중심이라는 사실과 축 방향이 맞다는 사실은 별개다. 캡처 도구는 다음 회전을 지원한다.

```text
anchor_color_roll
anchor_color_pitch
anchor_color_yaw
```

이 값은 URDF `camera_link`에서 RealSense의 ROS body frame인 `camera_color_frame`으로 가는 고정 RPY다. `camera_link`가 이미 카메라의 X-forward, Y-left, Z-up 방향이면 모두 `0.0`을 사용한다.

## 설치

번들 최상위에서 실행한다.

```bash
bash install_camera_rgb_anchor.sh "$HOME/MacRobot"
```

수동 설치:

```bash
cp -a macrobot_camera_tf ~/MacRobot/src/
cd ~/MacRobot
set +u
source /opt/ros/jazzy/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --packages-select macrobot_camera_tf --symlink-install
source install/setup.bash
```

## 장치별 내부 TF 캡처

기존 RealSense 노드를 모두 종료하고, D435 한 대만 연결한 상태에서 실행한다.

```bash
ros2 launch macrobot_camera_tf capture_d435_rgb_anchor.launch.py \
  output_file:="$HOME/MacRobot/data/camera_tf/d435_rgb_anchor.yaml" \
  anchor_color_roll:=0.0 \
  anchor_color_pitch:=0.0 \
  anchor_color_yaw:=0.0
```

출력 파일은 장치 내부 color/depth/infra extrinsic과 optical-frame 회전을 RGB 중심에 재기준화해 저장한다.

## 정상 런타임

```bash
ros2 launch macrobot_camera_tf camera_rgb_anchor.launch.py \
  calibration_file:="$HOME/MacRobot/data/camera_tf/d435_rgb_anchor.yaml"
```

이 launch는 RealSense를 `publish_tf:=false`, `enable_sync:=true`, `align_depth.enable:=true`로 시작하고 저장된 TF를 게시한다.

## 검증

URDF의 `base_link -> camera_link`도 필요하므로 로봇 description/pick stack을 동시에 실행한 상태에서:

```bash
bash verify_camera_tf_runtime.sh "$HOME/MacRobot"
```

RViz에서 TF 축을 확인할 때 `camera_color_optical_frame`은 다음 방향이어야 한다.

```text
+Z(파랑): RGB 렌즈가 보는 앞쪽
+X(빨강): 영상의 오른쪽
+Y(초록): 영상의 아래쪽
```

방향이 다르면 URDF 원점 위치를 옮기지 말고 캡처의 `anchor_color_roll/pitch/yaw`만 바로잡은 뒤 YAML을 다시 생성한다.
