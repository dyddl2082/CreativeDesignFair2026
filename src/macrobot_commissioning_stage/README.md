# MacRobot Arm Commissioning Stage

이 패키지는 카메라 연동 전에 필요한 다음 시험을 한 번에 관리한다.

1. MG996R/MG90S pulse, zero, sign, command range 보정
2. q1/q2/q3 방향 및 4-bar·평행 clamp 확인
3. MoveIt full-model safe-region 대표 경계 실물 검증
4. 반복 정밀도, 백래시, 하중, 온도 시험
5. 실제 grasp_frame 기하 파라미터 피팅
6. HOME/STOW/OPEN/CLOSE/PRE_GRASP/LOWER/LIFT/PLACE 정의
7. 물체별 grasp profile 기록

모든 자동 결과와 수동 측정값은 하나의 파일에 누적된다.

```text
~/MacRobot/data/commissioning/arm_commissioning_report.yaml
```

## 포함 패키지

```text
macrobot_arm_commissioning
```

기존 다음 패키지가 설치되어 있어야 한다.

```text
macrobot_description
macrobot_arm_kinematics
macrobot_arm_control
macrobot_safe_region
pico_debug (실물 serial 연결을 launch에서 시작할 경우)
```

## 설치

```bash
cp -r macrobot_commissioning_stage/macrobot_arm_commissioning \
  ~/MacRobot/src/

cd ~/MacRobot

rosdep install \
  --from-paths src \
  --ignore-src \
  -r \
  -y

colcon build \
  --packages-select macrobot_arm_commissioning \
  --symlink-install

source /opt/ros/jazzy/setup.bash
source ~/MacRobot/install/setup.bash
```

## 실행

먼저 저속 파이프라인을 실행한다.

```bash
ros2 launch macrobot_arm_commissioning commissioning_pipeline.launch.py \
  dry_run:=true \
  require_safe_region:=true \
  safe_region_csv:=$HOME/MacRobot/data/safe_region_exact_gripper_fine/safe_connected_samples.csv
```

새 터미널에서 대화형 도구를 실행한다.

```bash
ros2 run macrobot_arm_commissioning commissioning_cli --ros-args \
  -p allow_motion_commands:=true \
  -p safe_region_csv:=$HOME/MacRobot/data/safe_region_exact_gripper_fine/safe_connected_samples.csv \
  -p all_samples_csv:=$HOME/MacRobot/data/safe_region_exact_gripper_fine/safe_samples.csv \
  -p report_path:=$HOME/MacRobot/data/commissioning/arm_commissioning_report.yaml
```

실물 pulse jog가 필요할 때만 다음을 추가한다.

```bash
-p allow_raw_pulse_commands:=true
```

상세 설명:

```text
macrobot_arm_commissioning/docs/README_KO.md
macrobot_arm_commissioning/docs/WORKFLOW_KO.md
```
