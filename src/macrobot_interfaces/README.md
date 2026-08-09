# macrobot_interfaces

**상태:** 필수 · Raspberry Pi와 WSL2에 반드시 동일한 버전 설치

## 역할

카메라 인식 pipeline의 typed ROS 2 messages를 제공한다.

```text
DepthCandidate
DepthCandidateArray
RgbCandidateCrop
CandidateFilterResult
FilteredCandidateCrop
EmbeddingRetrievalResult
EmbeddingMatchedCandidate
TemporalConfirmationResult
```

`interface_additions`에서 배포하던 embedding 메시지는 이 package에 통합되었다. `interface_additions`는 더 이상 build하지 않는다.

## 빌드

```bash
cd ~/MacRobot
source /opt/ros/jazzy/setup.bash

rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install --packages-select macrobot_interfaces

source ~/MacRobot/install/setup.bash
```

## 확인

```bash
ros2 interface show macrobot_interfaces/msg/DepthCandidate
ros2 interface show macrobot_interfaces/msg/DepthCandidateArray
ros2 interface show macrobot_interfaces/msg/RgbCandidateCrop
ros2 interface show macrobot_interfaces/msg/CandidateFilterResult
ros2 interface show macrobot_interfaces/msg/EmbeddingRetrievalResult
ros2 interface show macrobot_interfaces/msg/TemporalConfirmationResult
```

## interface 변경 규칙

`.msg`를 한 글자라도 바꾸면 Pi와 WSL 양쪽에서 clean rebuild한다.

```bash
rm -rf \
  ~/MacRobot/build/macrobot_interfaces \
  ~/MacRobot/install/macrobot_interfaces

cd ~/MacRobot
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --packages-select macrobot_interfaces
source ~/MacRobot/install/setup.bash
```

서로 다른 interface definition을 가진 시스템끼리는 custom message 통신이 실패한다.
