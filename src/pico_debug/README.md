# pico_debug

**상태:** 필수 · Raspberry Pi↔Pico USB serial bridge 및 저수준 디버깅

이름은 debug지만 실제 하드웨어 runtime에서도 팔·차체 명령을 Pico로 전달한다.

## 토픽

```text
구독:
/pico_debug/cmd       std_msgs/String

발행:
/pico_debug/response  std_msgs/String
/pico_debug/events    std_msgs/String
```

## 빌드

```bash
sudo apt update
sudo apt install -y python3-serial

cd ~/MacRobot
source /opt/ros/jazzy/setup.bash

rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install --packages-select pico_debug

source ~/MacRobot/install/setup.bash
```

## 실행

```bash
ros2 run pico_debug pico_debug_node --ros-args \
  -p serial_port:=/dev/ttyACM0 \
  -p baudrate:=115200 \
  -p interactive:=false \
  -p auto_reconnect:=true
```

응답:

```bash
ros2 topic echo /pico_debug/response
```

## 주요 Pico 명령

```text
PING, STATUS?, ENC?, RESET_ENC
MOVE_CM, TURN_DEG, MOVE_TICKS, MOTOR, STOP, ESTOP
SERVO_US, ARM_US, SERVO_DEG, ARM_DEG
SERVO_STATE?, SERVO_OFF, ARM_OFF
```

연결 확인:

```bash
ros2 topic pub --once \
  /pico_debug/cmd \
  std_msgs/msg/String \
  "{data: 'PING'}"
```

현재 Home/Open pulse 직접 시험:

```bash
ros2 topic pub --once \
  /pico_debug/cmd \
  std_msgs/msg/String \
  "{data: 'ARM_US 1500 1500 500'}"
```

## 안전

- 일반 팔 동작은 직접 `ARM_US`가 아니라 `/macrobot/arm/joint_goal`→validator 경로를 사용한다.
- `ARM_OFF`는 토크를 풀므로 팔을 받친 상태에서만 실행한다.
- Thonny 또는 `mpremote`와 동시에 `/dev/ttyACM0`을 열지 않는다.
- Pico raw 출력이 JSON list/text여도 servo bridge가 죽지 않도록 callback type guard가 적용되어 있어야 한다.
