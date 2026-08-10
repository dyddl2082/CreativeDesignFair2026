# macrobot_arm_commissioning

**상태:** 유지 · 실물 로봇팔 commissioning/정비 도구 · 상시 runtime 아님

## 메뉴

```text
0 시스템 연결 상태
1 pulse / 영점 / 방향 보정
2 모델-실물 방향 및 4-bar 확인
3 safe-region 대표 경계 확인
4 반복 정밀도·하중·온도 시험
5 실제 grasp_frame 보정
6 HOME/STOW/OPEN/CLOSE/PRE_GRASP/LOWER/LIFT/PLACE
7 물체별 grasp profile
8 보고서 상태
9 종료
```

결과 파일:

```text
~/MacRobot/data/commissioning/arm_commissioning_report.yaml
```

## 빌드

```bash
cd ~/MacRobot
source /opt/ros/jazzy/setup.bash

rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install --packages-select \
  macrobot_arm_commissioning

source ~/MacRobot/install/setup.bash
```

## WSL2 dry-run

```bash
ros2 launch macrobot_arm_commissioning \
  commissioning_pipeline.launch.py \
  dry_run:=true \
  require_safe_region:=false \
  start_rviz:=true
```

CLI:

```bash
mkdir -p ~/MacRobot/data/commissioning

ros2 run macrobot_arm_commissioning commissioning_cli --ros-args \
  -p allow_motion_commands:=true \
  -p allow_raw_pulse_commands:=false \
  -p "report_path:=$HOME/MacRobot/data/commissioning/arm_commissioning_report.yaml"
```

## 실물 safe-region 사용

```bash
SAFE_DIR=$HOME/MacRobot/data/safe_region_collision_v2_fine
SAFE_CSV=$SAFE_DIR/safe_connected_samples.csv
ALL_CSV=$SAFE_DIR/safe_samples.csv
REPORT=$HOME/MacRobot/data/commissioning/arm_commissioning_report.yaml
```

Pipeline:

```bash
ros2 launch macrobot_arm_commissioning \
  commissioning_pipeline.launch.py \
  dry_run:=false \
  start_pico_debug:=true \
  serial_port:=/dev/ttyACM0 \
  require_safe_region:=true \
  safe_region_csv:="$SAFE_CSV" \
  start_rviz:=false
```

CLI:

```bash
ros2 run macrobot_arm_commissioning commissioning_cli --ros-args \
  -p allow_motion_commands:=true \
  -p allow_raw_pulse_commands:=false \
  -p "safe_region_csv:=$SAFE_CSV" \
  -p "all_samples_csv:=$ALL_CSV" \
  -p "report_path:=$REPORT"
```

## 보고서 확인

```bash
ros2 run macrobot_arm_commissioning \
  commissioning_report_summary \
  ~/MacRobot/data/commissioning/arm_commissioning_report.yaml
```

## 안전 원칙

- Raw pulse는 메뉴 1 보정에서만 임시 허용한다.
- 메뉴 3 이상은 `require_safe_region:=true`와 최신 CSV를 사용한다.
- Commissioning node가 `/pico_debug/cmd` direct publisher로 남지 않도록 `allow_raw_pulse_commands:=false`를 사용한다.
- 실제 명령은 validator 경로 `/macrobot/arm/joint_goal`을 사용한다.
