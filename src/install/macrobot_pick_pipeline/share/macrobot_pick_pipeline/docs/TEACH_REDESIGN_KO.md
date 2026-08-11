# Camera Teach와 Arm Demonstration Recorder 재설계

## 1. 문제

기존 `pick_teach_node`는 다음 세 기능을 하나의 메뉴로 제공했다.

```text
5. 카메라 보조 grasp_frame 보정
6. primitive pose 기록
7. 카메라 기준 grasp profile 기록
```

하지만 메뉴 5와 7은 D435의 3D 위치가 없으면 의미가 없고, 메뉴 6은 카메라와 무관하다. 또한 기존 메뉴 6은 현재 자세 한 점만 저장했기 때문에 사용자가 실제로 팔을 조종한 경로를 기록하지 못했다.

## 2. 새로운 역할 분리

### Camera-dependent

```text
camera_teach_node
├─ 최근 CameraInfo health 확인
├─ stable target lock
├─ grasp_frame calibration sample 기록
└─ object-specific grasp profile 기록
```

D435가 없으면 node를 시작하지 않아도 된다. 시작해도 `camera_ready=false`이며 메뉴 5와 7을 거부한다.

### Camera-independent

```text
arm_demo_recorder_node
├─ /logical_joint_states 수동 기록
├─ pose primitive 저장
├─ trajectory primitive 저장
├─ mark 추가
└─ validated keyframe replay
```

이 노드는 카메라 topic을 전혀 구독하지 않는다.

## 3. 사용자가 조작하면서 기록하는 구조

```text
사용자 조종 도구
   └─ /macrobot/arm/joint_goal
          ↓
       validator
          ↓
     servo_bridge
          ├─ 실제 서보 또는 dry-run RViz
          └─ /macrobot/arm/logical_joint_states
                         ↓
                 arm_demo_recorder_node
                         ↓
          ~/MacRobot/data/arm_primitives/*.yaml
```

record node는 조종 입력의 출처를 강제하지 않는다. 다음이 모두 가능하다.

```text
- 내장 arm_demo_cli keyboard jog
- 다른 팀원이 만든 GUI/조이스틱
- 상위 behavior executor
- 개발자가 /macrobot/arm/joint_goal에 보낸 validated goal
```

단, `/pico_debug/cmd`로 raw pulse를 직접 보내면 논리 상태와 실제 팔이 어긋날 수 있으므로 recording workflow에서 금지한다.

## 4. 저장 형식

```yaml
schema: macrobot.arm_primitive/v2
name: DEMO_PICK
kind: trajectory
joint_names:
  - arm_lift_joint
  - wrist_pitch_joint
  - gripper_joint
source_state: commanded_logical_state
warning: logical_joint_states are command-derived unless external joint encoders are added
speed_scale: 0.5
duration_sec: 4.2
waypoint_count: 18
marks:
  - t_sec: 1.4
    label: CONTACT
waypoints:
  - t_sec: 0.0
    q: [0.0, 0.0, 0.0]
  - t_sec: 0.3
    q: [0.05, 0.0, 0.0]
```

PCA9685 pulse와 passive gear joint는 저장하지 않는다. 보정값·기어비·URDF가 바뀌어도 논리 q trajectory를 재검증할 수 있기 때문이다.

## 5. 재생 정책

실제 사용자의 raw timing을 그대로 고주파 publish하지 않는다.

```text
recorded trajectory
→ 변화가 충분한 keyframe으로 축약
→ 각 keyframe을 /macrobot/arm/joint_goal에 publish
→ goal_validated 확인
→ trajectory_completed 확인
→ 다음 keyframe
```

따라서 재생은 시간적으로 완전히 동일한 모션 캡처가 아니라 안전 우선의 경로 재현이다.

정밀한 time-parameterized trajectory가 필요해지면 이후 `FollowJointTrajectory` 기반 controller로 확장한다.

## 6. 메뉴 구조

### `arm_demo_cli`

```text
1. 상태 / 목록
2. pose primitive 기록
3. 외부 조종 중 trajectory 기록
4. 내장 keyboard jog + trajectory 기록
5. 안전 재생
6. jog만 실행
7. 삭제
```

### `pick_teach_cli`

```text
5. camera grasp_frame calibration
7. camera object grasp profile
8. camera status
```

D435가 없으면 5와 7은 명확하게 비활성 상태가 된다.

## 7. 로봇이 없는 WSL2

arm pipeline을 dry-run으로 실행하고 recorder를 붙인다.

```bash
ros2 launch macrobot_arm_control arm_pipeline.launch.py \
  dry_run:=true \
  require_safe_region:=false \
  start_rviz:=true
```

다른 터미널:

```bash
ros2 launch macrobot_pick_pipeline arm_demo.launch.py \
  start_rviz:=false

ros2 run macrobot_pick_pipeline arm_demo_cli
```

## 8. 실제 로봇

최신 safe-region을 사용한 arm pipeline이 먼저 실행되어야 한다.

```bash
ros2 launch macrobot_pick_pipeline pick_pipeline_robot.launch.py \
  safe_region_csv:="$SAFE_CSV" \
  start_arm_demo_recorder:=true \
  start_camera_teach:=false
```

그 후:

```bash
ros2 run macrobot_pick_pipeline arm_demo_cli
```

D435가 연결되면 `start_camera_teach:=true`로 바꾸고 `pick_teach_cli`를 추가 실행한다.
