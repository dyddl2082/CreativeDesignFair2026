# macrobot_perception

## 상태

**유지 — WSL2 물체 인식 핵심 패키지.**

다음 세 기존 패키지를 하나의 ROS 2 배포 단위로 통합한다.

```text
candidate_filter
embedding_retrieval
temporal_confirmation
```

세 node는 별도 process로 유지되므로 QoS, 장애 격리, 성능 측정은 그대로 가능하다. 바뀌는 것은 package/launch 관리 단위다. 기존 node와 topic 이름은 유지한다.

## 전체 흐름

```text
/depth_candidates/rgb_crops
        ↓
candidate_filter_node
        ↓ /candidate_filter/accepted_crops
embedding_retrieval_node
        ↓ /embedding_retrieval/results
temporal_confirmation_node
        ↓ /temporal_confirmation/confirmed
        └ /object_finder/result
```

Temporal frame heartbeat:

```text
/depth_candidates/candidates
```

## 실행 위치

```text
Windows PC / WSL2
```

실제 D435 runtime에서는 Pi의 `depth_candidate_proposal`가 입력을 공급해야 한다.

## 실행 파일

```text
candidate_filter_node
embedding_retrieval_node
temporal_confirmation_node
```

## Python 환경

```bash
python3 -m venv --system-site-packages ~/MacRobot/.venv-embedding
source ~/MacRobot/.venv-embedding/bin/activate
python -m pip install --upgrade pip
python -m pip install \
  'transformers>=4.36,<6' \
  'safetensors>=0.4' \
  'Pillow>=10'
```

Embedding wrapper는 기본적으로 다음 Python을 사용한다.

```text
~/MacRobot/.venv-embedding/bin/python
```

다른 경로:

```bash
export MACROBOT_EMBEDDING_PYTHON=/path/to/python
```

## 빌드

```bash
cd ~/MacRobot
source /opt/ros/jazzy/setup.bash

colcon build --symlink-install --packages-select \
  macrobot_interfaces \
  macrobot_perception

source ~/MacRobot/install/setup.bash
```

## 통합 실행

```bash
source ~/MacRobot/.venv-embedding/bin/activate
source /opt/ros/jazzy/setup.bash
source ~/MacRobot/install/setup.bash

ros2 launch macrobot_perception pc_recognition_pipeline.launch.py
```

개별 실행:

```bash
ros2 launch macrobot_perception candidate_filter.launch.py
ros2 launch macrobot_perception embedding_retrieval.launch.py
ros2 launch macrobot_perception temporal_confirmation.launch.py
```

## Target 변경

```bash
TARGET=Cup

ros2 topic pub --once /candidate_filter/target \
  std_msgs/msg/String "{data: '$TARGET'}"

ros2 topic pub --once /embedding_retrieval/target \
  std_msgs/msg/String "{data: '$TARGET'}"
```

세 config의 `target_object`도 동일하게 유지한다.

```text
config/candidate_filter.yaml
config/embedding_retrieval.yaml
config/temporal_confirmation.yaml
```

## Reload

```bash
ros2 service call /candidate_filter/reload_profile \
  std_srvs/srv/Trigger '{}'

ros2 service call /embedding_retrieval/rebuild_banks \
  std_srvs/srv/Trigger '{}'

ros2 service call /temporal_confirmation/reset \
  std_srvs/srv/Trigger '{}'
```

## 결과

```bash
ros2 topic echo --no-daemon --spin-time 3.0 \
  /temporal_confirmation/confirmed \
  macrobot_interfaces/msg/TemporalConfirmationResult
```

```bash
ros2 topic echo --no-daemon --spin-time 3.0 \
  --field data --full-length \
  /object_finder/result std_msgs/msg/String
```

## Status와 threshold

```bash
ros2 param get /embedding_retrieval min_positive_similarity
ros2 param get /embedding_retrieval min_margin
ros2 param get /temporal_confirmation decision_source
```

```bash
ros2 topic echo --no-daemon --spin-time 3.0 --once \
  --field data --full-length \
  /embedding_retrieval/status std_msgs/msg/String
```

현재 tuned threshold는 local YAML/runtime parameter를 최종 기준으로 삼는다.

## 데이터

```text
~/MacRobot/data/curated/objects/<target>/
~/MacRobot/data/negative/backgrounds/
~/MacRobot/data/negative/library/
~/MacRobot/data/negative/confusers/<target>/
```

## Debug image

```bash
ros2 run image_view image_view --ros-args \
  -r image:=/embedding_retrieval/debug \
  -p image_transport:=compressed
```
