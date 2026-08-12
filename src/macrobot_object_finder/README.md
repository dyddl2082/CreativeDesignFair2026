# macrobot_object_finder 0.2.0

D435 후보 crop 인식 pipeline에 goal/cancel/session을 추가하고, typed temporal result를 pick pipeline용 JSON으로 정규화한다. 전체 RGB/depth/point cloud를 WSL2로 구독하지 않는다.

## 실행

```bash
source ~/MacRobot/.venv-embedding/bin/activate
source /opt/ros/jazzy/setup.bash
source ~/MacRobot/install/setup.bash
ros2 launch macrobot_object_finder object_finder_wsl.launch.py
```

이 launch가 함께 실행하는 노드:

```text
candidate_filter_node
embedding_retrieval_node
temporal_confirmation_node
threshold_calibrator_node
object_finder_node
```

## 찾기

```bash
ros2 run macrobot_object_finder object_finder_cli find Eraser --timeout 60
```

## 명시적 현장 threshold 보정

```bash
ros2 run macrobot_object_finder threshold_calibration_cli \
  calibrate Eraser --environment arena_1 --duration 10 --confirm-visible
```

일반 탐색 중에는 threshold를 자동으로 낮추지 않는다. target/negative 점수 분포가 겹치면 적용을 거부한다.

## 결과

```text
/object_finder/result
/object_finder/status
/object_finder/calibration/status
/object_finder/calibration/result
```

결과 JSON에는 patch-localized center, localization quality, object image-plane orientation이 포함된다. 이미지 중심 기반 turn suggestion은 제거됐다.

활성 환경 ID는 launch에서 고정한다.

```bash
ros2 launch macrobot_object_finder object_finder_wsl.launch.py \
  environment_id:=competition_arena_1
```

이 값은 목표 물체가 바뀔 때 어떤 threshold profile을 자동 적용할지 결정한다.
