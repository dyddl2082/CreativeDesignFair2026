# MacRobot RGB 기준 카메라 TF 및 본선 시연 적용 순서

## 0. 이 문서가 전제하는 현재 상태

- 작업공간: `~/MacRobot`
- ROS 2 Jazzy
- 직렬형 2축 로봇팔 코드 전환 완료
- `macrobot_description` 검증 완료
- 현재 로봇 형상으로 safe-region coarse/fine 검사 완료
- 재부팅 복원·시각 재탐색·지연 인식·PLACE 패치 적용 완료
- URDF의 `camera_link` 원점은 D435 **RGB 렌즈 중심**에 놓인 1 mm 기준 마커
- `base_link -> camera_link`는 `robot_state_publisher`가 URDF에서 게시

이후 해야 할 핵심은 다음 순서다.

```text
RGB 중심 camera_link 축 확인
→ 장치 내부 color/depth/infra TF 캡처
→ 정상 런타임에서 RealSense TF 중복 제거
→ 3차원 위치화 검증
→ 새 팔의 PICK/PLACE keyframe 재기록
→ 물체별 인식·파지 profile 등록
→ 이동·재부팅·PLACE 회귀시험
→ Gateway/LLM 연결
```

---

# 1. 공통 환경 파일 설치

각 터미널에서 반복해서 ROS 환경을 설정하기 위한 파일을 설치한다.

```bash
mkdir -p ~/MacRobot/tools
cp macrobot_env.sh ~/MacRobot/tools/
chmod +x ~/MacRobot/tools/macrobot_env.sh
```

이후 Pi의 새 터미널마다 다음을 실행한다.

```bash
source ~/MacRobot/tools/macrobot_env.sh
```

직접 실행하는 경우에는 다음과 같다.

```bash
set +u
source /opt/ros/jazzy/setup.bash
source ~/MacRobot/install/setup.bash
export ROS_DOMAIN_ID=42
export ROS_AUTOMATIC_DISCOVERY_RANGE=SUBNET
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
unset ROS_LOCALHOST_ONLY
```

WSL2에서는 Python 가상환경이 필요하다면 먼저 활성화한다.

```bash
source ~/MacRobot/.venv-embedding/bin/activate
source ~/MacRobot/tools/macrobot_env.sh
```

---

# 2. 현재 상태 백업

```bash
export WS="$HOME/MacRobot"
export STAMP="$(date +%Y%m%d_%H%M%S)"
export BACKUP="$WS/backup/before_camera_tf_$STAMP"
mkdir -p "$BACKUP"

cp -a "$WS/src/macrobot_description" "$BACKUP/" 2>/dev/null || true
cp -a "$WS/src/macrobot_pick_pipeline" "$BACKUP/" 2>/dev/null || true
cp -a "$WS/data" "$BACKUP/data" 2>/dev/null || true
```

Git을 사용한다면 추가로 커밋한다.

```bash
cd ~/MacRobot
git status --short
git add -A
git commit -m "backup before RGB-anchored RealSense TF integration" || true
```

---

# 3. camera_link 자체의 위치와 축 확인

`camera_link`가 RGB 렌즈 중심에 있는 것만으로는 충분하지 않다. 축도 카메라 body frame의 규약과 맞아야 한다.

## 터미널 A: description 실행

```bash
source ~/MacRobot/tools/macrobot_env.sh
ros2 launch macrobot_description runtime_description.launch.py
```

해당 launch가 없다면 다음 대안을 사용한다.

```bash
source ~/MacRobot/tools/macrobot_env.sh
ros2 launch macrobot_description display_full.launch.py
```

## 터미널 B: TF 수치 확인

```bash
source ~/MacRobot/tools/macrobot_env.sh
ros2 run tf2_ros tf2_echo base_link camera_link
```

## 터미널 C: RViz 확인

```bash
source ~/MacRobot/tools/macrobot_env.sh
rviz2
```

RViz에서 다음을 추가한다.

```text
Add → TF
Show Axes = true
Show Names = true
Frame Timeout = 15
```

`camera_link`의 원점이 RGB 렌즈 중심에 있는지 확인한다. 축은 다음 의미를 갖도록 만드는 것이 권장된다.

```text
camera_link +X: 카메라가 바라보는 방향
camera_link +Y: 카메라를 뒤에서 보았을 때 왼쪽
camera_link +Z: 위쪽
```

현재 마커의 축이 이미 이 방향이면 이후 캡처에서 RPY 보정값을 모두 `0.0`으로 사용한다. 마커가 위치만 맞고 축이 `base_link`를 그대로 상속했다면, 카메라 장착 방향에 따라 `anchor_color_roll/pitch/yaw`가 필요하다.

대표적인 수평 장착 예시는 다음과 같다. 아래 표는 표준적인 `base_link`의 +X가 로봇 전방이라는 전제다.

| RGB 렌즈가 보는 방향 | `anchor_color_yaw` 후보 |
|---|---:|
| `base_link +X` | `0.0` |
| `base_link +Y` | `1.57079632679` |
| `base_link -X` | `3.14159265359` |
| `base_link -Y` | `-1.57079632679` |

실제 MacRobot의 축 규약이 다르면 RViz의 TF 축을 기준으로 결정한다. 임의의 값을 추정해서 적용하지 않는다.

---

# 4. macrobot_camera_tf 설치

번들의 최상위에서 실행한다.

```bash
bash install_camera_rgb_anchor.sh "$HOME/MacRobot"
```

이 스크립트는 다음을 수행한다.

```text
macrobot_camera_tf 패키지 설치
macrobot_pick_pipeline/config/perception.yaml 백업
optical_frame_override를 camera_color_optical_frame으로 설정
관련 패키지 빌드
```

설치 뒤 현재 셸을 갱신한다.

```bash
source ~/MacRobot/tools/macrobot_env.sh
ros2 pkg prefix macrobot_camera_tf
```

설치된 perception 설정을 확인한다.

```bash
grep -nE \
  'camera_info_topic|aligned_depth_topic|base_frame|optical_frame_override' \
  ~/MacRobot/src/macrobot_pick_pipeline/config/perception.yaml
```

다음 값이어야 한다.

```yaml
camera_info_topic: /camera/camera/color/camera_info
aligned_depth_topic: /camera/camera/aligned_depth_to_color/image_raw
base_frame: base_link
optical_frame_override: camera_color_optical_frame
```

---

# 5. D435 장치 내부 TF를 RGB 중심으로 캡처

이 작업은 카메라 장치 또는 펌웨어/보정값이 바뀌지 않는 한 한 번만 수행하면 된다.

## 5.1 기존 카메라 프로세스 종료

RealSense를 사용하는 기존 launch를 모두 `Ctrl+C`로 종료한다. 남아 있는 노드를 확인한다.

```bash
source ~/MacRobot/tools/macrobot_env.sh
ros2 node list | grep -E 'camera|realsense' || true
```

카메라가 여전히 점유되어 있다면 실행 중인 launch 터미널을 종료한다. 강제 종료는 마지막 수단으로만 사용한다.

```bash
pkill -f realsense2_camera_node || true
sleep 2
```

## 5.2 카메라가 한 대인지 확인

```bash
rs-enumerate-devices -s
```

`rs-enumerate-devices`가 없다면:

```bash
sudo apt update
sudo apt install -y librealsense2-utils
```

## 5.3 RGB 기준 TF 캡처

먼저 축 보정이 필요 없다고 가정하고 캡처한다.

```bash
source ~/MacRobot/tools/macrobot_env.sh
export CAMERA_TF="$HOME/MacRobot/data/camera_tf/d435_rgb_anchor.yaml"
mkdir -p "$(dirname "$CAMERA_TF")"

ros2 launch macrobot_camera_tf capture_d435_rgb_anchor.launch.py \
  output_file:="$CAMERA_TF" \
  anchor_color_roll:=0.0 \
  anchor_color_pitch:=0.0 \
  anchor_color_yaw:=0.0 \
  require_infra_frames:=false
```

성공하면 launch가 YAML을 저장하고 캡처 노드가 종료된다. RealSense launch는 계속 남을 수 있으므로 `Ctrl+C`로 종료한다.

카메라가 여러 대라면 장치 serial을 문자열로 지정한다. 현재 설치된 RealSense wrapper가 요구하는 따옴표 형식에 맞춰야 한다.

```bash
ros2 launch macrobot_camera_tf capture_d435_rgb_anchor.launch.py \
  output_file:="$CAMERA_TF" \
  serial_no:="'YOUR_D435_SERIAL'" \
  anchor_color_roll:=0.0 \
  anchor_color_pitch:=0.0 \
  anchor_color_yaw:=0.0
```

## 5.4 캡처 파일 검사

```bash
python3 - "$CAMERA_TF" <<'PY'
from pathlib import Path
import sys
import yaml

path = Path(sys.argv[1]).expanduser().resolve()
root = yaml.safe_load(path.read_text(encoding="utf-8"))
print("file:", path)
print("schema_version:", root.get("schema_version"))
print("metadata:")
for key, value in (root.get("metadata") or {}).items():
    print(f"  {key}: {value}")
print("transforms:")
for item in root.get("transforms", []):
    print(f"  {item['parent']} -> {item['child']}")
    print(f"    xyz={item['xyz']}")
    print(f"    q={item['quaternion_xyzw']}")
PY
```

최소한 다음 체인이 있어야 한다.

```text
camera_link -> camera_color_frame
camera_color_frame -> camera_color_optical_frame
camera_link -> camera_depth_frame
camera_depth_frame -> camera_depth_optical_frame
```

infra stream 캡처에 성공했다면 다음도 들어간다.

```text
camera_link -> camera_infra1_frame
camera_infra1_frame -> camera_infra1_optical_frame
camera_link -> camera_infra2_frame
camera_infra2_frame -> camera_infra2_optical_frame
```

---

# 6. 카메라 TF 단독 런타임 검증

## 터미널 A: robot description

```bash
source ~/MacRobot/tools/macrobot_env.sh
ros2 launch macrobot_description runtime_description.launch.py
```

## 터미널 B: RGB 기준 RealSense 런타임

```bash
source ~/MacRobot/tools/macrobot_env.sh
export CAMERA_TF="$HOME/MacRobot/data/camera_tf/d435_rgb_anchor.yaml"

ros2 launch macrobot_camera_tf camera_rgb_anchor.launch.py \
  calibration_file:="$CAMERA_TF" \
  start_realsense:=true \
  initial_reset:=false \
  color_profile:=640x480x15 \
  depth_profile:=640x480x15
```

이 launch를 사용하는 동안 별도의 `realsense2_camera rs_launch.py`를 동시에 실행하지 않는다.

## 터미널 C: 자동 검사

```bash
source ~/MacRobot/tools/macrobot_env.sh
bash verify_camera_tf_runtime.sh "$HOME/MacRobot"
```

다음 항목이 모두 통과해야 한다.

```text
/camera/camera의 publish_tf=false
/macrobot/camera_tf/status 수신
color CameraInfo 수신
aligned depth 수신
base_link -> camera_link 변환 존재
base_link -> camera_color_optical_frame 변환 존재
base_link -> camera_depth_optical_frame 변환 존재
localizer optical_frame_override 확인
```

## 터미널 D: 프레임 헤더 확인

```bash
source ~/MacRobot/tools/macrobot_env.sh

ros2 topic echo \
  /camera/camera/color/camera_info \
  --once --field header.frame_id

ros2 topic echo \
  /camera/camera/aligned_depth_to_color/image_raw \
  --once --field header.frame_id
```

일반적으로 color와 color 정렬 depth는 `camera_color_optical_frame`을 기준으로 해석한다.

## 터미널 E: TF 수치 확인

```bash
source ~/MacRobot/tools/macrobot_env.sh

ros2 run tf2_ros tf2_echo \
  base_link camera_color_optical_frame
```

```bash
ros2 run tf2_ros tf2_echo \
  camera_link camera_color_optical_frame
```

```bash
ros2 run tf2_ros tf2_echo \
  camera_link camera_depth_optical_frame
```

## RViz 광학축 확인

```bash
source ~/MacRobot/tools/macrobot_env.sh
rviz2
```

TF를 표시하고 `camera_color_optical_frame`을 확인한다.

```text
파란 +Z: RGB 영상이 바라보는 방향
빨간 +X: 영상 오른쪽
초록 +Y: 영상 아래쪽
```

이 방향이 맞으면 캡처 결과를 확정한다.

방향이 틀렸다면 `camera_link`의 위치는 유지하고 캡처를 다시 수행한다. 예를 들어 180° yaw 보정이 필요하다고 확인된 경우:

```bash
# 실행 중인 RealSense 런타임을 먼저 종료한다.
source ~/MacRobot/tools/macrobot_env.sh

ros2 launch macrobot_camera_tf capture_d435_rgb_anchor.launch.py \
  output_file:="$HOME/MacRobot/data/camera_tf/d435_rgb_anchor.yaml" \
  anchor_color_roll:=0.0 \
  anchor_color_pitch:=0.0 \
  anchor_color_yaw:=3.14159265359
```

RPY는 한 번에 하나씩 바꾸고, 매번 RViz 축을 확인한다.

---

# 7. TF 중복 게시 검사

정상 런타임에서는 RealSense wrapper의 TF가 꺼져 있어야 한다.

```bash
ros2 param get /camera/camera publish_tf
```

기대값:

```text
Boolean value is: False
```

TF publisher를 확인한다.

```bash
ros2 topic info /tf_static --verbose
```

다음 두 역할만 존재하는 것이 정상이다.

```text
robot_state_publisher: base_link -> camera_link 포함
macrobot_rgb_anchor_tf_publisher: camera_link 아래의 카메라 내부 frame
```

현재 TF 그래프를 저장한다.

```bash
mkdir -p ~/MacRobot/data/tf_checks
cd ~/MacRobot/data/tf_checks
ros2 run tf2_tools view_frames
```

생성된 PDF에서 다음과 같은 단일 트리를 확인한다.

```text
base_link
└─ camera_link
   ├─ camera_color_frame
   │  └─ camera_color_optical_frame
   ├─ camera_depth_frame
   │  └─ camera_depth_optical_frame
   ├─ camera_infra1_frame
   │  └─ camera_infra1_optical_frame
   └─ camera_infra2_frame
      └─ camera_infra2_optical_frame
```

`camera_link`에 부모가 두 개 있거나 동일한 child frame을 두 노드가 게시하면 정상 실행을 중단하고 중복 launch를 제거한다.

---

# 8. safe-region 결과를 다시 만들어야 하는지 판단

이번 방식은 URDF의 `base_link -> camera_link`를 바꾸지 않고, 카메라 내부의 **collision 없는 고정 TF**를 별도 노드가 게시한다. 다음 조건을 모두 만족하면 기존에 완료한 arm safe-region을 다시 생성할 필요가 없다.

```text
arm_lift_joint/wrist_pitch_joint/gripper_joint의 origin, axis, limit 불변
팔·그리퍼 collision mesh 불변
base_link/바닥 collision 불변
D435 본체나 브래킷 collision 형상을 새로 추가하지 않음
safe-region CSV가 현재 model revision으로 생성됨
```

현재 모델 revision을 확인한다.

```bash
cat ~/MacRobot/src/macrobot_description/config/collision_model_revision.txt
```

safe-region summary를 찾는다.

```bash
find ~/MacRobot/data -type f -name safe_region_summary.yaml -print
```

사용할 결과를 변수로 지정한다.

```bash
export SAFE_DIR="$HOME/MacRobot/data/safe_region_serial2r_fine"
export SAFE_CSV="$SAFE_DIR/safe_connected_samples.csv"
export SAFE_SUMMARY="$SAFE_DIR/safe_region_summary.yaml"

ls -lh "$SAFE_CSV" "$SAFE_SUMMARY"
grep -nE 'model_revision|safe|connected|home' "$SAFE_SUMMARY" || true
```

다음 중 하나라도 발생했다면 safe-region을 다시 생성한다.

```text
base_link -> camera_link 자체를 수정함
카메라 또는 브래킷 collision을 추가/이동함
팔 링크 또는 joint origin/axis/limit을 수정함
기존 safe-region이 r1/r2/4-bar revision임
```

카메라 내부 TF만 추가한 경우에는 safe-region 대신 **3차원 인식 좌표와 접근 동작**을 다시 검증한다.

---

# 9. 카메라 위치화 정확도 검증

카메라 TF가 존재한다는 것과 `base_link` 위치가 정확하다는 것은 다르다. 알려진 위치의 물체 또는 마커를 이용해 오차를 측정한다.

## 9.1 pick stack 없이 localizer만 실행하는 경우

카메라와 인식 결과 source가 실행 중인 상태에서:

```bash
source ~/MacRobot/tools/macrobot_env.sh

ros2 run macrobot_pick_pipeline detection_localizer_node \
  --ros-args \
  --params-file \
  "$(ros2 pkg prefix --share macrobot_pick_pipeline)/config/perception.yaml"
```

다른 터미널에서:

```bash
ros2 topic echo \
  /macrobot/perception/localized_detection \
  --field data --full-length
```

```bash
ros2 topic echo \
  /macrobot/perception/localizer_status \
  --field data --full-length
```

## 9.2 측정 절차

1. `base_link` 기준 좌표를 줄자와 직각자로 측정할 수 있는 물체를 놓는다.
2. 정면·좌측·우측, 근거리·중거리에서 각각 10회 이상 관측한다.
3. 출력된 `point_base`와 실측값의 평균오차 및 최대오차를 기록한다.
4. 방향성 있는 일정 오차는 `base_link -> camera_link` 장착 transform 문제다.
5. 거리와 위치에 따라 불규칙한 오차는 depth 품질·동기화·patch 중심 문제일 가능성이 높다.

카메라 토픽 동기화를 확인한다.

```bash
ros2 topic hz /camera/camera/color/image_raw
ros2 topic hz /camera/camera/aligned_depth_to_color/image_raw
ros2 topic hz /camera/camera/color/camera_info
```

`camera_info.header.frame_id`, aligned depth header, `optical_frame_override`가 모두 같은 color optical 기준으로 해석되는지 확인한다.

---

# 10. 재부팅 패치 적용 상태와 단위시험 확인

패키지 위치를 확인한다.

```bash
source ~/MacRobot/tools/macrobot_env.sh

ros2 pkg prefix macrobot_perception
ros2 pkg prefix macrobot_pick_pipeline
ros2 pkg prefix macrobot_action_gateway
```

재부팅 기능의 실행 파일이 있는지 확인한다.

```bash
ros2 pkg executables macrobot_pick_pipeline | grep -E \
  'resilient_object_task_node|stored_object_pick_cli|grasp_keyframe_cli'
```

관련 단위시험을 실행한다.

```bash
cd ~/MacRobot
source ~/MacRobot/tools/macrobot_env.sh

colcon test --packages-select \
  macrobot_perception \
  macrobot_pick_pipeline \
  macrobot_action_gateway \
  --event-handlers console_direct+

colcon test-result --verbose
```

현재 boot ID를 기록한다.

```bash
cat /proc/sys/kernel/random/boot_id
```

메모리 저장 경로를 준비한다.

```bash
mkdir -p ~/MacRobot/data/object_memory
mkdir -p ~/MacRobot/data/stored_objects
mkdir -p ~/MacRobot/data/grasp_keyframes
mkdir -p ~/MacRobot/data/commissioning
mkdir -p ~/MacRobot/data/arm_primitives

touch ~/MacRobot/data/object_memory/.write_test
rm ~/MacRobot/data/object_memory/.write_test
```

---

# 11. 전체 시스템 실행 순서

## Pi 터미널 1: RGB 기준 카메라와 내부 TF

```bash
source ~/MacRobot/tools/macrobot_env.sh
export CAMERA_TF="$HOME/MacRobot/data/camera_tf/d435_rgb_anchor.yaml"

ros2 launch macrobot_camera_tf camera_rgb_anchor.launch.py \
  calibration_file:="$CAMERA_TF" \
  start_realsense:=true \
  color_profile:=640x480x15 \
  depth_profile:=640x480x15
```

## Pi 터미널 2: depth 후보와 RGB crop

```bash
source ~/MacRobot/tools/macrobot_env.sh

ros2 launch depth_candidate_proposal \
  edge_candidate_pipeline.launch.py
```

launch 이름이 다른 경우:

```bash
ros2 pkg prefix depth_candidate_proposal
find "$(ros2 pkg prefix --share depth_candidate_proposal)/launch" \
  -maxdepth 1 -type f -print
```

## WSL2 터미널 1: DINOv2 인식

```bash
source ~/MacRobot/.venv-embedding/bin/activate
source ~/MacRobot/tools/macrobot_env.sh

ros2 launch macrobot_object_finder \
  object_finder_wsl.launch.py \
  environment_id:=competition_arena_1
```

launch가 `environment_id` 인자를 받지 않는 버전이면 인자를 빼고 실행한다.

```bash
ros2 launch macrobot_object_finder object_finder_wsl.launch.py
```

queue 상태를 확인한다.

```bash
ros2 topic echo /embedding_retrieval/status
```

다음 항목이 있어야 한다.

```text
queue_policy: latest_frame
dropped_queue
dropped_out_of_order
dropped_stale_input
```

## Pi 터미널 3: 팔·차체·localizer·재부팅 task

```bash
source ~/MacRobot/tools/macrobot_env.sh

export SAFE_CSV="$HOME/MacRobot/data/safe_region_serial2r_fine/safe_connected_samples.csv"
test -s "$SAFE_CSV" || { echo "SAFE_CSV missing: $SAFE_CSV"; exit 1; }

ros2 launch macrobot_pick_pipeline pick_pipeline_robot.launch.py \
  safe_region_csv:="$SAFE_CSV" \
  serial_port:=/dev/ttyACM0 \
  start_pico_debug:=true \
  start_base_alignment:=true \
  start_grasp_keyframes:=true \
  start_depth_clearance:=true \
  task_executable:=resilient_object_task_node \
  perception_input_mode:=legacy \
  alignment_dry_run:=true
```

첫 통합시험은 반드시 `alignment_dry_run:=true`로 시작한다. 카메라 위치와 정렬 부호가 확인된 뒤에만 실제 이동을 허용한다.

```bash
# 실제 주행을 허용하는 단계
ros2 launch macrobot_pick_pipeline pick_pipeline_robot.launch.py \
  safe_region_csv:="$SAFE_CSV" \
  serial_port:=/dev/ttyACM0 \
  start_pico_debug:=true \
  start_base_alignment:=true \
  start_grasp_keyframes:=true \
  start_depth_clearance:=true \
  task_executable:=resilient_object_task_node \
  perception_input_mode:=legacy \
  alignment_dry_run:=false
```

`pick_pipeline_robot.launch.py`의 arm pipeline이 `robot_state_publisher`를 시작하므로 이 단계에서는 별도 description launch를 중복 실행하지 않는다.

## Pi/WSL 모니터 터미널

```bash
source ~/MacRobot/tools/macrobot_env.sh

ros2 node list | sort
```

```bash
ros2 topic echo \
  /macrobot/perception/localized_detection \
  --field data --full-length
```

```bash
ros2 topic echo \
  /macrobot/perception/localizer_status \
  --field data --full-length
```

```bash
ros2 topic echo \
  /macrobot/stored_pick/status \
  --field data --full-length
```

```bash
ros2 topic echo /macrobot/perception/forward_clearance
```

---

# 12. 새 직렬형 팔의 keyframe 재기록

safe-region이 끝났더라도 4-bar 시절 또는 이전 URDF에서 기록한 keyframe은 새 팔에 사용하지 않는다.

## 12.1 기존 profile 목록 확인

```bash
source ~/MacRobot/tools/macrobot_env.sh

ros2 run macrobot_pick_pipeline grasp_keyframe_cli list
```

필요하면 과거 profile을 삭제하거나 새 이름을 사용한다.

```bash
ros2 run macrobot_pick_pipeline grasp_keyframe_cli delete Eraser_serial2r
```

## 12.2 팔을 각 의미 자세로 이동

팔 조그 도구를 실행한다.

```bash
ros2 run macrobot_pick_pipeline arm_demo_cli
```

실물에서 한 단계씩 자세를 만든 뒤 별도 터미널에서 캡처한다. 아래 예시는 profile 이름을 `Eraser_serial2r`로 분리한다.

```bash
ros2 run macrobot_pick_pipeline grasp_keyframe_cli \
  capture Eraser_serial2r Eraser OPEN \
  --object-point-base -0.19 0.08 0.10
```

```bash
ros2 run macrobot_pick_pipeline grasp_keyframe_cli \
  capture Eraser_serial2r Eraser PRE_GRASP \
  --object-point-base -0.19 0.08 0.10
```

```bash
ros2 run macrobot_pick_pipeline grasp_keyframe_cli \
  capture Eraser_serial2r Eraser GRASP_OPEN \
  --object-point-base -0.19 0.08 0.10
```

```bash
ros2 run macrobot_pick_pipeline grasp_keyframe_cli \
  capture Eraser_serial2r Eraser CLOSE \
  --object-point-base -0.19 0.08 0.10
```

```bash
ros2 run macrobot_pick_pipeline grasp_keyframe_cli \
  capture Eraser_serial2r Eraser LIFT \
  --object-point-base -0.19 0.08 0.10
```

위 `--object-point-base`는 예시이므로 현재 `localized_detection`의 실제 `point_base`로 바꾼다.

profile을 확정한다.

```bash
ros2 run macrobot_pick_pipeline grasp_keyframe_cli \
  finalize Eraser_serial2r
```

## 12.3 keyframe 사전검사

```bash
ros2 run macrobot_pick_pipeline grasp_keyframe_cli \
  --timeout 30 \
  preflight Eraser_serial2r \
  --object-name Eraser \
  --object-point-base -0.19 0.08 0.10
```

무부하 저속 재생:

```bash
ros2 run macrobot_pick_pipeline grasp_keyframe_cli \
  --timeout 120 \
  play Eraser_serial2r \
  --object-name Eraser \
  --object-point-base -0.19 0.08 0.10
```

모든 endpoint뿐 아니라 단계 사이 경로가 safe-region을 통과하는지 상태를 확인한다.

```bash
ros2 topic echo \
  /macrobot/grasp_keyframes/status \
  --field data --full-length
```

---

# 13. 물체별 인식 및 runtime profile 등록

## 13.1 환경별 threshold 보정

목표 물체만 잘 보이게 놓고 실행한다.

```bash
source ~/MacRobot/tools/macrobot_env.sh

ros2 run macrobot_object_finder threshold_calibration_cli \
  calibrate Eraser \
  --environment competition_arena_1 \
  --duration 10 \
  --confirm-visible
```

```bash
ros2 run macrobot_object_finder threshold_calibration_cli \
  apply Eraser \
  --environment competition_arena_1
```

인식 bank/profile이 생성됐는지 확인한다.

```bash
find ~/MacRobot/data -type f | grep -Ei \
  'Eraser|embedding|prototype|threshold|profile'
```

## 13.2 인식하기 좋은 거리에서 record-search

먼저 Pico odometry 세션을 확인하고 필요한 경우 원점을 초기화한다.

```bash
ros2 topic pub --once \
  /pico_debug/cmd \
  std_msgs/msg/String \
  "{data: 'ODOM?'}"
```

```bash
ros2 topic pub --once \
  /pico_debug/cmd \
  std_msgs/msg/String \
  "{data: 'RESET_ODOM 0 0 0'}"
```

물체가 안정적으로 인식되는 현재 위치에서:

```bash
ros2 run macrobot_pick_pipeline stored_object_pick_cli \
  record-search Eraser \
  --profile Eraser \
  --rebuild-banks \
  --timeout 180
```

이 위치는 재부팅 후 절대 목적지로 사용되는 영구 좌표가 아니라 같은 epoch의 탐색 힌트다.

## 13.3 팔이 닿는 거리에서 record-grasp

로봇을 작은 단계로 이동하고 매 단계 재관측한다. 아래 이동량은 예시이며 현재 바닥과 방향 규약에 맞게 줄여서 사용한다.

```bash
ros2 topic pub --once \
  /pico_debug/cmd \
  std_msgs/msg/String \
  "{data: 'MOVE_CM 4 60 8'}"
```

파지 기준 위치에서:

```bash
ros2 run macrobot_pick_pipeline stored_object_pick_cli \
  record-grasp Eraser \
  --profile Eraser \
  --grasp-keyframes Eraser_serial2r \
  --max-grasp-range 0.30 \
  --timeout 30
```

runtime profile을 확인한다.

```bash
sed -n '1,260p' \
  ~/MacRobot/data/stored_objects/runtime_profiles.yaml
```

---

# 14. PICK 단계별 회귀시험

## 14.1 현재 보이는 물체의 정렬만 시험

```bash
ros2 run macrobot_pick_pipeline stored_object_pick_cli \
  visible-test Eraser \
  --profile Eraser \
  --align-only \
  --timeout 180
```

## 14.2 재탐색 포함 정렬만 시험

```bash
ros2 run macrobot_pick_pipeline stored_object_pick_cli \
  run Eraser \
  --profile Eraser \
  --align-only \
  --timeout 180
```

확인할 핵심 이벤트:

```text
resilient_object_search_started
search_observation_started
search_motion_completed
visual_servo_observation
delayed_detection_retargeted
```

## 14.3 실제 파지

```bash
ros2 run macrobot_pick_pipeline stored_object_pick_cli \
  run Eraser \
  --profile Eraser \
  --timeout 240
```

작업 중에는 다른 CLI, teleop 또는 Gateway가 동시에 motion command를 보내지 않게 한다.

취소:

```bash
ros2 run macrobot_pick_pipeline stored_object_pick_cli cancel
```

팔 keyframe 취소:

```bash
ros2 run macrobot_pick_pipeline grasp_keyframe_cli cancel
```

---

# 15. PLACE 역과정 검증

PLACE는 새 배치점에서 `LIFT → GRASP_OPEN 높이 → RELEASE → PRE_GRASP 후퇴`에 해당하는 Cartesian 역과정을 다시 계산한다.

## 15.1 직접 지정 위치 사전검사

현재 들고 있는 물체를 `base_link` 좌표의 안전한 시험점에 놓는 경우:

```bash
ros2 run macrobot_pick_pipeline grasp_keyframe_cli \
  --timeout 30 \
  preflight-place Eraser_serial2r \
  --object-name Eraser \
  --object-point-base -0.18 0.12 0.08
```

실행:

```bash
ros2 run macrobot_pick_pipeline grasp_keyframe_cli \
  --timeout 120 \
  place Eraser_serial2r \
  --object-name Eraser \
  --object-point-base -0.18 0.12 0.08
```

## 15.2 기준 물체 옆에 놓기

Eraser를 들고 있고 Cup을 기준 물체로 사용할 때:

```bash
ros2 run macrobot_pick_pipeline stored_object_pick_cli \
  place Cup \
  --held-object Eraser \
  --held-runtime-profile Eraser \
  --grasp-keyframes Eraser_serial2r \
  --offset-base 0.0 0.12 0.0 \
  --timeout 180
```

보유 상태가 이미 메모리에 정확히 기록되어 있다면 `--held-object` 등의 옵션을 생략할 수 있다.

기대 이벤트:

```text
stored_place_started
place_target_resolved
semantic_place_preflight_started
grasp_keyframe_place_preflight_succeeded
semantic_place_execution_started
stored_place_completed
```

힘·전류 센서가 없으므로 PLACE 성공은 동작 시퀀스 완료를 의미하며, 실제 물체 분리 여부는 육안으로 확인한다.

---

# 16. 재부팅 복원 시험

## 16.1 재부팅 전 상태 확인

```bash
ros2 run macrobot_pick_pipeline stored_object_pick_cli memory
```

영구 데이터 파일을 확인한다.

```bash
ls -lh \
  ~/MacRobot/data/grasp_keyframes/profiles.yaml \
  ~/MacRobot/data/stored_objects/runtime_profiles.yaml \
  ~/MacRobot/data/object_memory/memory.yaml
```

파일 hash를 보관한다.

```bash
sha256sum \
  ~/MacRobot/data/grasp_keyframes/profiles.yaml \
  ~/MacRobot/data/stored_objects/runtime_profiles.yaml \
  > ~/MacRobot/data/reboot_test_before.sha256
```

## 16.2 재부팅

```bash
sudo reboot
```

재부팅 후 전체 시스템을 11절 순서대로 다시 실행한다.

현재 boot ID를 확인한다.

```bash
cat /proc/sys/kernel/random/boot_id
```

## 16.3 재부팅 후 상태 확인

```bash
ros2 run macrobot_pick_pipeline stored_object_pick_cli memory
```

기대 결과:

```text
이전 odometry 기반 물체 위치: stale
인식 bank/threshold: 유지
stored runtime profile: 유지
grasp keyframe: 유지
held object: empty 또는 unknown
```

영구 파일이 바뀌지 않았는지 확인한다.

```bash
sha256sum -c ~/MacRobot/data/reboot_test_before.sha256
```

실제로 물체를 들고 재부팅했다면 운영자가 명시적으로 확인한다.

```bash
ros2 run macrobot_pick_pipeline stored_object_pick_cli \
  confirm-held Eraser Eraser_serial2r
```

실제 그리퍼가 비어 있다면:

```bash
ros2 run macrobot_pick_pipeline stored_object_pick_cli clear-held
```

불확실하면:

```bash
ros2 run macrobot_pick_pipeline stored_object_pick_cli held-unknown
```

---

# 17. 물체 이동 대응 시험

1. Eraser를 기존 등록 위치에서 다른 위치로 옮긴다.
2. 로봇을 이전 위치에 두거나 재부팅한다.
3. `run`을 실행한다.

```bash
ros2 run macrobot_pick_pipeline stored_object_pick_cli \
  run Eraser \
  --profile Eraser \
  --timeout 240
```

다른 터미널에서 상태를 저장한다.

```bash
mkdir -p ~/MacRobot/data/demo_logs
ros2 topic echo \
  /macrobot/stored_pick/status \
  --field data --full-length \
  | tee ~/MacRobot/data/demo_logs/moved_object_test.log
```

평가 기준:

```text
이전 stale 좌표로 장거리 이동하지 않음
현재 시야 관측을 우선함
짧은 전진과 작은 회전 뒤 재관측함
발견 후 visual servo 목표를 갱신함
```

---

# 18. 이동 중 지연 인식 시험

상태 이벤트를 모니터링한다.

```bash
ros2 topic echo \
  /macrobot/stored_pick/status \
  --field data --full-length \
  | grep --line-buffered -E \
  'motion_boundary_perception_processed|delayed_detection_retargeted|visual_servo_observation'
```

다른 터미널에서 탐색을 실행한다.

```bash
ros2 run macrobot_pick_pipeline stored_object_pick_cli \
  run Eraser \
  --profile Eraser \
  --align-only \
  --timeout 240
```

확인할 동작:

```text
짧은 4 cm/4° 동작은 중간에 끊지 않음
도착한 인식 결과를 motion boundary에서 처리
촬영 시점 pose와 현재 pose를 이용해 목표를 재계산
오래된 frame은 latest-frame queue 정책으로 폐기
```

---

# 19. Gateway와 LLM 연결

하위 PICK/PLACE CLI 시험을 모두 통과한 뒤 진행한다.

## 19.1 Gateway dry-run

```bash
source ~/MacRobot/tools/macrobot_env.sh

ros2 launch macrobot_action_gateway action_gateway.launch.py \
  real_motion_enabled:=false
```

다른 터미널에서 제한 Python 검증:

```bash
source ~/MacRobot/tools/macrobot_env.sh
export GW_SHARE="$(ros2 pkg prefix --share macrobot_action_gateway)"

ros2 run macrobot_action_gateway robot_code_runner \
  --code "$GW_SHARE/examples/pick_and_place_nextto.py" \
  --validate-only
```

## 19.2 Gateway 실제 실행

CLI와 teleop을 모두 종료한 뒤:

```bash
source ~/MacRobot/tools/macrobot_env.sh

ros2 launch macrobot_action_gateway action_gateway.launch.py \
  real_motion_enabled:=true
```

실제 작업 중에는 다음을 동시에 사용하지 않는다.

```text
stored_object_pick_cli의 motion 명령
arm_demo_cli 조그
수동 Pico MOVE/ROTATE
Gateway 실제 action
```

STOP 경로를 미리 확인한다.

```bash
ros2 topic list | grep -E 'stop|cancel'
```

---

# 20. 본선 시연 당일 시작 순서

## 시연 전 하드웨어

```text
바닥판과 벽면 고정
카메라 브래킷 풀림 확인
USB·Pico serial 확인
배터리 전압 확인
그리퍼 안에 물체가 없는지 확인
물체와 조명 배치 확인
```

## 1단계: 네트워크

Pi와 WSL2 양쪽에서:

```bash
source ~/MacRobot/tools/macrobot_env.sh
echo "$ROS_DOMAIN_ID"
echo "$RMW_IMPLEMENTATION"
hostname -I
```

상대 장치가 보이는지 확인한다.

```bash
ros2 node list
```

## 2단계: 카메라와 TF

Pi:

```bash
ros2 launch macrobot_camera_tf camera_rgb_anchor.launch.py \
  calibration_file:="$HOME/MacRobot/data/camera_tf/d435_rgb_anchor.yaml"
```

다른 터미널:

```bash
bash verify_camera_tf_runtime.sh ~/MacRobot
```

## 3단계: 후보 생성과 WSL 인식

Pi:

```bash
ros2 launch depth_candidate_proposal edge_candidate_pipeline.launch.py
```

WSL:

```bash
source ~/MacRobot/.venv-embedding/bin/activate
source ~/MacRobot/tools/macrobot_env.sh
ros2 launch macrobot_object_finder object_finder_wsl.launch.py \
  environment_id:=competition_arena_1
```

## 4단계: 로봇 파이프라인

Pi:

```bash
source ~/MacRobot/tools/macrobot_env.sh
export SAFE_CSV="$HOME/MacRobot/data/safe_region_serial2r_fine/safe_connected_samples.csv"

ros2 launch macrobot_pick_pipeline pick_pipeline_robot.launch.py \
  safe_region_csv:="$SAFE_CSV" \
  serial_port:=/dev/ttyACM0 \
  task_executable:=resilient_object_task_node \
  alignment_dry_run:=false
```

## 5단계: 보유 상태 동기화

```bash
ros2 run macrobot_pick_pipeline stored_object_pick_cli memory
ros2 run macrobot_pick_pipeline stored_object_pick_cli clear-held
```

## 6단계: 시연 직전 무동작 확인

```bash
ros2 topic echo --once /macrobot/perception/forward_clearance
ros2 topic echo --once /macrobot/camera_tf/status
ros2 topic echo --once /embedding_retrieval/status
```

## 7단계: Gateway/GUI

```bash
ros2 launch macrobot_action_gateway action_gateway.launch.py \
  real_motion_enabled:=true
```

---

# 21. 종료 순서

1. 진행 중 action을 cancel 또는 STOP한다.
2. Gateway를 종료한다.
3. pick pipeline을 종료한다.
4. WSL 인식을 종료한다.
5. depth candidate를 종료한다.
6. 카메라 launch를 종료한다.
7. 팔을 지지한 뒤 서보 전원을 끈다.
8. 차체 전원과 Pi를 정상 종료한다.

Pi 정상 종료:

```bash
sudo poweroff
```

---

# 22. 다시 safe-region 또는 카메라 캡처가 필요한 변경

## safe-region 재생성이 필요한 경우

```text
팔 joint origin/axis/limit 변경
gripper mimic 또는 관절 범위 변경
팔·그리퍼·카메라 브래킷 collision mesh 변경
base_link 또는 바닥 collision 변경
```

## 카메라 TF 캡처를 다시 해야 하는 경우

```text
D435 장치 교체
카메라 firmware/보정 변경이 의심됨
camera_link 축 방향 변경
카메라 내부 frame naming 변경
RealSense wrapper를 큰 버전으로 교체
```

## 3차원 위치화만 재검증하면 되는 경우

```text
카메라 브래킷을 풀었다 다시 조임
base_link -> camera_link 위치 또는 각도 변경
시연 바닥·조명·거리 조건 변경
```

`base_link -> camera_link`가 바뀐 경우 내부 RGB-depth 캡처 파일은 같은 장치라면 유지할 수 있지만, 로봇 기준 위치화와 정렬 파라미터는 반드시 다시 검증한다.
