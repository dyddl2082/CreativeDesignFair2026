# 단계별 시험

## A. 코드 검사만

```bash
source /opt/ros/jazzy/setup.bash
source ~/MacRobot/install/setup.bash

CODE="$(ros2 pkg prefix --share macrobot_action_gateway)/examples/pick_buds3.py"
ros2 run macrobot_action_gateway robot_code_runner \
  --code "$CODE" \
  --validate-only
```

## B. Gateway dry-run

터미널 1:

```bash
ros2 launch macrobot_action_gateway action_gateway.launch.py \
  real_motion_enabled:=false
```

터미널 2:

```bash
CODE="$(ros2 pkg prefix --share macrobot_action_gateway)/examples/move_then_turn.py"
ros2 run macrobot_action_gateway robot_code_runner \
  --code "$CODE" \
  --execute \
  --approved
```

상태:

```bash
ros2 run macrobot_action_gateway action_gateway_cli status
```

## C. 하위 ROS stack dry-run 연동 확인

Gateway의 `real_motion_enabled=false`는 하위 노드 없이도 facade/action semantics를 검사한다.

하위 topic 계약을 확인하려면 arm/pick stack은 별도로 dry-run으로 실행하고 Gateway는 아직 false로 둔다.

## D. 실제 motion 전 체크

```text
[ ] /pico_debug/response 정상
[ ] /macrobot/arm/logical_joint_states 정상
[ ] /macrobot/arm/validation_status 정상
[ ] /macrobot/arm/servo_bridge/status 정상
[ ] /object_finder/status 최신
[ ] /macrobot/base_alignment/result stack 정상
[ ] safe-region 최신 collision revision 기준
[ ] direct publisher/teleop 종료
[ ] Gateway config provisional limit 검토
```

실제 모드:

```bash
ros2 launch macrobot_action_gateway action_gateway.launch.py \
  real_motion_enabled:=true
```

처음에는 `SET_GRIPPER`, 작은 `SET_ARM_JOINTS`, 짧은 `MOVE_BASE` 순으로 별도 승인 코드를 시험한다.


## PICK 후 PLACE dry-run

```bash
SHARE="$(ros2 pkg prefix --share macrobot_action_gateway)"
ros2 run macrobot_action_gateway robot_code_runner   --code "$SHARE/examples/pick_and_place_nextto.py"   --validate-only

ros2 run macrobot_action_gateway robot_code_runner   --code "$SHARE/examples/pick_and_place_nextto.py"   --execute --approved
```
