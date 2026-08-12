# MacRobot 적응형 인식·정밀 위치·Semantic Grasp 통합판

이 번들은 다음 다섯 항목을 한 번에 적용한다.

1. 운영자가 대상 물체가 보인다고 명시한 경우에만 수행되는 물체별·환경별 DINOv2 threshold 보정
2. 등록 이미지의 positive/negative patch prototype bank와 DINOv2 patch-token heatmap을 이용한 crop 내부 물체 중심·영역·영상면 방향 추정
3. WSL2에서는 crop만 처리하고, Raspberry Pi의 aligned depth를 정제된 pixel에서 다시 표본화
4. 카메라가 차체 왼쪽에 있어도 `camera optical frame → base_link` TF를 거쳐 수행되는 3D 정렬
5. 사람이 천천히 조작한 시간을 재생하지 않고 `OPEN → PRE_GRASP → GRASP_OPEN → CLOSE → LIFT` 의미 keyframe을 현재 물체 위치에 맞춰 IK로 재계산하는 파지

팀 LLM의 공개 API는 바꾸지 않는다.

```text
robot.ALIGN_WITH_OBJECT(ObjectId.ERASER)
robot.PICK_OBJECT(ObjectId.ERASER)
```

threshold 보정, patch heatmap, depth 재표본화, 카메라 offset, IK, safe-region preflight는 전부 내부 ROS 계층에서 처리한다.

## 패키지 버전

```text
macrobot_perception     0.3.0
macrobot_object_finder  0.2.0
macrobot_pick_pipeline  0.6.0
```

`macrobot_interfaces`의 다음 두 메시지도 양쪽 장치에서 함께 갱신해야 한다.

```text
EmbeddingRetrievalResult.msg
TemporalConfirmationResult.msg
```

## 설치

Pi와 WSL2 양쪽에서 같은 번들을 사용한다. 설치 스크립트는 기존 source package를 archive에 백업하고, custom interface를 먼저 빌드한 뒤 관련 package를 빌드한다.

```bash
cd ~/Downloads/macrobot_adaptive_perception_grasp_stage
chmod +x install_adaptive_stage.sh verify_adaptive_stage.sh scripts/*.sh
./install_adaptive_stage.sh ~/MacRobot
```

설치 후 새 터미널에서:

```bash
source /opt/ros/jazzy/setup.bash
source ~/MacRobot/install/setup.bash
```

## 통신 구조

```text
Raspberry Pi
D435 aligned depth/color
→ depth_candidate_proposal
→ 후보 JPEG crop + metadata
                 │
                 └─────────────── DDS ────────────────┐
                                                     WSL2
                                             candidate_filter
                                             DINOv2 global retrieval
                                             DINOv2 patch heatmap
                                             temporal confirmation
                                             object_finder
                 ┌──────── compact result ────────────┘
Raspberry Pi     ↓
detection_localizer
→ patch 중심의 aligned depth 재표본화
→ optical 3D
→ TF(base_link)
→ stored-object visual alignment
→ semantic grasp keyframes / IK / safe-region
```

전체 RGB, 전체 depth, PointCloud2를 WSL2 RViz로 보내지 않는다.

## 1. Pi: D435와 후보 crop

```bash
ros2 launch realsense2_camera rs_launch.py \
  enable_color:=true \
  enable_depth:=true \
  pointcloud.enable:=false \
  align_depth.enable:=true \
  enable_sync:=true \
  rgb_camera.color_profile:=640x480x15 \
  depth_module.depth_profile:=640x480x15
```

```bash
ros2 launch depth_candidate_proposal edge_candidate_pipeline.launch.py
```

## 2. WSL2: Finder + threshold profile + DINO patch heatmap

```bash
source ~/MacRobot/.venv-embedding/bin/activate
source /opt/ros/jazzy/setup.bash
source ~/MacRobot/install/setup.bash

ros2 launch macrobot_object_finder object_finder_wsl.launch.py \
  environment_id:=competition_arena_1
```

Patch localization 확인:

```bash
ros2 topic echo /embedding_retrieval/results \
  macrobot_interfaces/msg/EmbeddingRetrievalResult
```

중요 필드:

```text
localization_available
localization_quality
localized_center_x / localized_center_y
localized_roi
orientation_deg / orientation_class / orientation_quality
```

## 3. 대회장 현장 threshold 보정

물체가 카메라에 실제로 보인다고 운영자가 확인한 상태에서만 실행한다.

```bash
ros2 run macrobot_object_finder threshold_calibration_cli \
  calibrate Eraser \
  --environment competition_arena_1 \
  --duration 10 \
  --confirm-visible
```

이 명령은 target track의 낮은 분위수와 주변 crop negative의 높은 분위수를 비교한다. 분포가 겹치면 threshold를 낮추지 않고 실패한다.

저장 파일:

```text
~/MacRobot/data/perception/threshold_profiles.yaml
```

저장 profile 재적용:

```bash
ros2 run macrobot_object_finder threshold_calibration_cli \
  apply Eraser \
  --environment competition_arena_1
```

목표 물체가 변경되면 해당 environment profile을 자동 적용하도록 기본 설정되어 있다.


## 점수 계층 분리

현장 보정이 바꾸는 값은 DINO embedding의 `min_positive_similarity`와 `min_margin`이다. temporal confirmation은 embedding 결과의 `accepted` 상태를 사용하며, localizer·alignment·camera-teach의 별도 `minimum_score` 기본값은 `0.0`으로 두어 같은 숫자를 여러 의미로 중복 적용하지 않는다. 정렬 안전성은 localization quality, depth/center uncertainty, stability, orientation, IK와 safe-region으로 판단한다.

## 4. Pi: 팔·localizer·stored pick stack

```bash
SAFE_CSV=$HOME/MacRobot/data/safe_region_collision_v2_fine/safe_connected_samples.csv

ros2 launch macrobot_pick_pipeline pick_pipeline_robot.launch.py \
  safe_region_csv:="$SAFE_CSV" \
  start_pico_debug:=true \
  serial_port:=/dev/ttyACM0 \
  start_base_alignment:=true \
  start_grasp_keyframes:=true \
  start_arm_demo_recorder:=true \
  start_camera_teach:=false \
  perception_input_mode:=legacy
```

## 5. Semantic grasp keyframe 기록

팔을 `arm_demo_cli`의 jog-only 기능으로 원하는 자세에 놓은 뒤 각 의미 단계만 저장한다. 사람의 조작 시간은 저장하지 않는다.

```bash
ros2 run macrobot_pick_pipeline arm_demo_cli
```

다른 터미널에서:

```bash
ros2 run macrobot_pick_pipeline grasp_keyframe_cli capture Eraser Eraser OPEN
ros2 run macrobot_pick_pipeline grasp_keyframe_cli capture Eraser Eraser PRE_GRASP
ros2 run macrobot_pick_pipeline grasp_keyframe_cli capture Eraser Eraser GRASP_OPEN
ros2 run macrobot_pick_pipeline grasp_keyframe_cli capture Eraser Eraser CLOSE
ros2 run macrobot_pick_pipeline grasp_keyframe_cli capture Eraser Eraser LIFT
ros2 run macrobot_pick_pipeline grasp_keyframe_cli finalize Eraser
```

사전 검사:

```bash
ros2 run macrobot_pick_pipeline grasp_keyframe_cli preflight Eraser \
  --object-name Eraser
```

실행:

```bash
ros2 run macrobot_pick_pipeline grasp_keyframe_cli play Eraser \
  --object-name Eraser
```

각 Cartesian keyframe은 현재 물체 3D 위치에 object-relative offset을 더한 뒤 IK를 다시 계산한다. 실행 전에는 모든 segment를 safe-region CSV에서 preflight하고, 실행 중에는 기존 validator와 servo bridge가 다시 검사한다.

## 6. 저장 위치 기반 전체 profile 기록

```bash
ros2 run macrobot_pick_pipeline stored_object_pick_cli \
  record Eraser \
  --profile Eraser \
  --grasp-keyframes Eraser
```

이제 legacy `--grasp-trajectory`는 이전 파일 호환용일 뿐, 신규 기록에는 `--grasp-keyframes`를 사용한다.

현재 이미 찾은 상태에서 정렬만:

```bash
ros2 run macrobot_pick_pipeline stored_object_pick_cli \
  visible-test Eraser --profile Eraser --align-only
```

정렬 후 파지:

```bash
ros2 run macrobot_pick_pipeline stored_object_pick_cli \
  visible-test Eraser --profile Eraser
```

teleop 이동 후 저장 위치 복귀·탐색·정렬·파지:

```bash
ros2 run macrobot_pick_pipeline stored_object_pick_cli \
  run Eraser --profile Eraser
```


## 권장 첫 적용 순서

1. Pi와 WSL2 양쪽에 동일 bundle을 설치하고 `macrobot_interfaces`를 clean rebuild한다.
2. WSL2 finder를 `environment_id`와 함께 실행한다. 첫 bank rebuild는 patch prototype cache 생성 때문에 평소보다 오래 걸릴 수 있다.
3. 운영자가 실제 대상 물체가 보임을 확인한 뒤 explicit threshold calibration을 수행한다.
4. `localized_center_x/y`, patch ROI, localization quality가 정상인지 확인한다.
5. Pi pick stack을 실행하고 optical→`base_link` TF 및 local aligned-depth refinement를 확인한다.
6. semantic keyframe 5단계를 기록하고 `preflight`만 먼저 수행한다.
7. stored-object profile을 `--grasp-keyframes`로 기록한다.
8. `visible-test --align-only` → `visible-test` → teleop 이동 후 full `run` 순서로 확대한다.
9. 차체 또는 팔 동작 중 cancel을 걸어 terminal stop confirmation을 확인한다.

## 취소 안전성

semantic grasp가 움직이는 중에는 cancel 요청만 보낸 것으로 완료 처리하지 않는다. `/macrobot/arm/stop` 이후 servo bridge의 `trajectory_stopped`가 확인돼야 `CANCELED`로 끝난다. 확인되지 않으면 `SAFE_STOP_UNCONFIRMED`로 실패한다.

## 삭제·비활성화된 기존 경로

- `horizontal_error_norm`, `suggested_turn`, 이미지 중심 기반 좌·우 회전 제어를 interface와 active code에서 제거했다.
- 별도 `candidate_refiner_node`와 cable-guard 경로는 포함하지 않는다.
- `macrobot_perception/scripts/embedding_retrieval_node` wrapper를 제거하고 setuptools entry point 하나로 통일했다.
- 연속 `arm_demo` trajectory는 호환용으로만 유지하고 신규 stored-pick 기본 executor는 semantic keyframe이다.
- RViz Image/Depth/PointCloud display를 `real_camera.rviz`에서도 제거해 전체 센서 stream subscriber가 생기지 않게 했다.

## 안전 원칙

- 현장 threshold는 일반 탐색 중 자동으로 낮아지지 않는다.
- 이미지 중앙 기준 회전 대신 `base_link` 3D point만 alignment authority로 사용한다.
- patch heatmap 위치 품질, depth 표준편차, center 안정성, 선택적 물체 방향을 통과해야 정렬한다.
- keyframe 사전검사는 runtime validator를 대체하지 않는다.
- LLM은 ROS나 파일을 직접 접근하지 않고 기존 Robot Action Gateway를 통해서만 호출한다.

자세한 내용은 `docs/`의 문서를 확인한다.

활성 환경 ID는 launch에서 고정한다.

```bash
ros2 launch macrobot_object_finder object_finder_wsl.launch.py \
  environment_id:=competition_arena_1
```

이 값은 목표 물체가 바뀔 때 어떤 threshold profile을 자동 적용할지 결정한다.
