# macrobot_moveit_config

**상태:** 필수 · WSL2 개발/오프라인 collision 설정

## 역할

- reduced/full collision model용 SRDF
- joint limits
- kinematics/OMPL 설정
- `macrobot_safe_region` PlanningScene 입력

## 주요 파일

```text
config/macrobot.srdf
config/macrobot_full_collision.srdf
config/macrobot_full_exact_gripper.srdf
config/joint_limits.yaml
config/kinematics.yaml
config/ompl_planning.yaml
```

## 빌드

```bash
cd ~/MacRobot
source /opt/ros/jazzy/setup.bash

rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install --packages-select \
  macrobot_description \
  macrobot_moveit_config

source ~/MacRobot/install/setup.bash
```

## Model load 확인

```bash
ros2 launch macrobot_moveit_config model_only.launch.py
```

## `disable_collisions` 원칙

의도된 기어 맞물림이나 tree로 펼친 폐루프의 항상-접촉 pair만 disable한다. 실제 위험한 링크 pair를 disable하면 collision scan이 안전하지 않은 자세를 허용할 수 있다.

SRDF, collision mesh 또는 joint mapping이 바뀌면 기존 safe-region CSV를 폐기하고 다시 생성한다.
