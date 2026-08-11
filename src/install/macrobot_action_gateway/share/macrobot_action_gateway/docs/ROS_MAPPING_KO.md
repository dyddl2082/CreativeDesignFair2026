# Robot API ↔ 현재 ROS 2 mapping

## 차체

```text
MOVE_BASE
→ /pico_debug/cmd: MOVE_CM <cm> <speed> <timeout>
← /pico_debug/response: event=move_cm_result, status=done
```

```text
TURN_BASE
→ public +angle = CCW/left
→ 현재 Pico +angle = right이면 Gateway에서 sign 반전
→ /pico_debug/cmd: TURN_DEG ...
← event=turn_deg_result
```

정지:

```text
/pico_debug/cmd: STOP
← event=stopped
```

## 팔·그리퍼

```text
/macrobot/arm/joint_goal
  sensor_msgs/JointState
  names = arm_lift_joint, wrist_pitch_joint, gripper_joint
  positions = radians
```

검증:

```text
/macrobot/arm/validation_status
  goal_validated
  goal_rejected
```

실행 결과:

```text
/macrobot/arm/servo_bridge/status
  trajectory_started
  trajectory_completed
  trajectory_stopped
  runtime_interpolation_rejected
  defense_in_depth_rejection
  pico_error
```

Commanded state:

```text
/macrobot/arm/logical_joint_states
```

## 인지

```text
/object_finder/status
/object_finder/result
```

`GET_OBJECT_STATE`는 최신 snapshot만 읽으며 `/object_finder/goal`을 보내지 않는다.

## 정렬·파지

```text
ALIGN_WITH_OBJECT
→ /macrobot/align_pick/goal
   execute_pick=false
← /macrobot/base_alignment/result
   event=alignment_completed
```

```text
PICK_OBJECT
→ /macrobot/align_pick/goal
   execute_pick=true
← /macrobot/base_alignment/result
   event=align_pick_completed
```

Cancel:

```text
/macrobot/base_alignment/cancel
```

## 동시 publisher 주의

Gateway의 resource lock은 Gateway를 통한 액션 간에는 강제된다. 그러나 다른 CLI나 teleop이 ROS topic을 직접 publish하면 Gateway 밖의 명령이다. 실제 LLM 실행 중에는 다음을 동시에 사용하지 않는다.

```text
teleop_twist_keyboard
base_alignment_cli 수동 실행
arm_demo_cli jog
/pico_debug/cmd 직접 publish
/macrobot/arm/joint_goal 직접 publish
```

## 저장 위치 기반 정식 node와 취소 확인

현재 legacy topic 이름은 팀 API와의 호환을 위해 유지하지만 실제 consumer는 `stored_object_pick_node`다.

```text
/macrobot/align_pick/goal
→ mode=full, start_finder=true
→ 저장 odom 위치 coarse return
→ bounded finder scan
→ camera-relative alignment
→ recorded grasp trajectory
```

Gateway는 각 요청에 `request_id`를 넣고 같은 ID의 결과만 수신한다.

```text
cancel publish
→ action_state=CANCEL_REQUESTED
→ 하위 정지 확인
→ CANCELED / TIMED_OUT / FAILED terminal result
```

terminal 결과가 오지 않으면 `SAFE_STOP_UNCONFIRMED`이며 public action을 성공적으로 취소했다고 보고하지 않는다.
