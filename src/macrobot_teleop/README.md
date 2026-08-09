# macrobot_teleop

**상태:** 유지 · 실물 차체 수동 운전/디버깅

## 역할

`teleop_twist_keyboard`의 `/cmd_vel`을 Pico 명령으로 변환한다.

- `step` 모드: `MOVE_CM`, `TURN_DEG`; 엔코더 동기화 사용
- `velocity` 모드: `MOTOR left right`; open-loop 수동 조작

## 빌드

```bash
sudo apt update
sudo apt install -y ros-jazzy-teleop-twist-keyboard

cd ~/MacRobot
source /opt/ros/jazzy/setup.bash

rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install --packages-select \
  pico_debug \
  macrobot_teleop

source ~/MacRobot/install/setup.bash
```

## 실행

터미널 1:

```bash
ros2 launch macrobot_teleop teleop_pico_bridge.launch.py \
  serial_port:=/dev/ttyACM0 \
  control_mode:=step \
  step_cm:=3.0 \
  turn_deg:=10.0 \
  step_speed:=80 \
  turn_speed:=70
```

터미널 2:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

기본 키:

```text
i 전진
, 후진
j 좌회전
l 우회전
k 정지
```

## 주의

- Encoder correction 확인은 `step` 모드에서 한다.
- 실제 pick sequence와 동시에 수동 teleop을 실행하지 않는다.
- `/pico_debug/cmd` publisher가 여러 개면 직접 명령 충돌이 날 수 있다.
- 현재 WSL2-only 단계에서는 유지하되 실행하지 않아도 된다.
