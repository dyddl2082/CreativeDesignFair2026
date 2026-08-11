# macrobot_action_gateway

## 역할

LLM이 생성한 제한 Python 코드가 ROS 2, Pico, 파일 시스템을 직접 호출하지 않도록 하는 실행 경계다.

```text
robot.MOVE_BASE(...)
robot.PICK_OBJECT(...)
        ↓
RobotFacade / Unix socket
        ↓
MacRobotActionGatewayNode
        ↓
기존 ROS 2 안전 파이프라인
```

## 실행 파일

```text
action_gateway_node
robot_code_runner
action_gateway_cli
```

## 공개 API

```text
WAIT_SECOND
WAIT_ACTION
WAIT_RESOURCE
CHECK_ACTION
CANCEL_ACTION
CANCEL_ALL
STOP
GET_OBJECT_STATE
GET_ROBOT_POS

MOVE_BASE
TURN_BASE
SAVE_POS
MOVE_BASE_TO_POS
ALIGN_WITH_OBJECT

SET_ARM_JOINTS
SET_GRIPPER
SAVE_ARM_PRIMITIVE
SET_ARM_PRIMITIVE
PICK_OBJECT
PLACE_NEXTTO_OBJECT
```

## 빌드

```bash
cd ~/MacRobot
source /opt/ros/jazzy/setup.bash

rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install --packages-select macrobot_action_gateway
source ~/MacRobot/install/setup.bash
```

## 1단계: Gateway dry-run

```bash
ros2 launch macrobot_action_gateway action_gateway.launch.py \
  real_motion_enabled:=false
```

상태:

```bash
ros2 run macrobot_action_gateway action_gateway_cli status
```

## 2단계: 생성 코드 검사

```bash
EXAMPLE="$(ros2 pkg prefix --share macrobot_action_gateway)/examples/move_then_turn.py"

ros2 run macrobot_action_gateway robot_code_runner \
  --code "$EXAMPLE" \
  --validate-only
```

## 3단계: 승인된 코드를 dry-run으로 실행

```bash
ros2 run macrobot_action_gateway robot_code_runner \
  --code "$EXAMPLE" \
  --execute \
  --approved
```

`--approved`가 없으면 실행되지 않는다. `main()`이 비동기 액션을 남긴 채 반환하면 Gateway가 해당 액션을 취소하고 실행을 실패 처리한다.

로그:

```text
~/MacRobot/data/llm_runs/<run_id>/run.json
```

## 실제 로봇 모드

먼저 기존 하위 노드가 모두 정상이어야 한다.

```text
pico_debug_node
macrobot_arm_control arm pipeline
macrobot_pick_pipeline base-alignment/pick stack
macrobot_object_finder
```

Gateway는 마지막에 명시적으로 실제 motion을 허용한다.

```bash
ros2 launch macrobot_action_gateway action_gateway.launch.py \
  real_motion_enabled:=true
```

실제 모드에서는 `/pico_debug/cmd`, `/macrobot/arm/joint_goal`, `/macrobot/align_pick/goal`을 외부 도구가 동시에 직접 publish하지 않도록 한다.

## DINOv2 임시 threshold 0.45 저장

실행 중 parameter만 바꾸려면:

```bash
ros2 param set /embedding_retrieval min_positive_similarity 0.45
```

YAML에도 저장하려면 번들 root에서:

```bash
./scripts/set_embedding_threshold_045.sh ~/MacRobot
```

threshold enforcement까지 켜려면:

```bash
./scripts/set_embedding_threshold_045.sh ~/MacRobot --enable
```

이 도구는 `min_margin`을 임의로 변경하지 않는다.

## primitive 계약

`SAVE_ARM_PRIMITIVE`는 다음 두 값만 저장한다.

```text
arm_lift_deg
wrist_pitch_deg
```

그리퍼는 저장하지 않으며 `SET_ARM_PRIMITIVE` 실행 시 현재 gripper commanded state를 유지한다.

## ObjectId

초기 enum은 사양 예제에 나온 두 항목이다.

```text
ObjectId.BUDS3
ObjectId.CUP
```

새 등록 물체를 public LLM API로 노출할 때는 다음 두 파일을 함께 갱신해야 한다.

```text
macrobot_action_gateway/api_types.py
config/object_catalog.yaml
```

## STOP

`STOP()`은 현재 run뿐 아니라 시스템 motion 전체에 정지를 요청하고, 같은 run에서 이후 새 motion을 금지한다. 새 사용자 명령은 새 run으로 실행해야 한다.

## 추가 예제

```bash
SHARE="$(ros2 pkg prefix --share macrobot_action_gateway)"

ros2 run macrobot_action_gateway robot_code_runner \
  --code "$SHARE/examples/arm_then_gripper.py" \
  --validate-only

ros2 run macrobot_action_gateway robot_code_runner \
  --code "$SHARE/examples/get_state.py" \
  --validate-only
```

## 설계 결정

업로드된 API 사양을 검토한 뒤 왜 Gateway가 다음 단계인지, 현재 ROS에 어떤 방식으로 연결했는지는 `docs/NEXT_ACTION_DECISION_KO.md`에 정리되어 있다.
