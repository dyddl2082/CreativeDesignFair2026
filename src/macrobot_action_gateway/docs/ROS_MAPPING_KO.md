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


## PLACE runtime

```text
PLACE_NEXTTO_OBJECT(reference_object_id)
  -> /macrobot/stored_pick/goal
     {task: place, request_id, reference_object, reference_profile,
      held_object, placement_offset_base, timeout_sec}
  <- /macrobot/stored_pick/result
     stored_place_completed | stored_place_failed | stored_place_timed_out
  -> /macrobot/stored_pick/cancel      # cancel/timeout
```

Gateway는 `request_id`가 일치하는 결과만 수락한다. 성공하면 held-object state를 empty로, 동작이 시작된 뒤 실패하면 unknown으로 바꾼다.

## held-object heartbeat

```text
/macrobot/stored_pick/status
  event=resilient_state_heartbeat
  held_object.state=empty | holding | unknown
```

Gateway는 시작 시 held-object state를 `unknown`으로 두고, 위 heartbeat를 받은 뒤에만 `PICK_OBJECT` 또는 `PLACE_NEXTTO_OBJECT`를 허용한다. `holding`일 때는 `held_object.object_name`을 object catalog의 ID로 변환한다.
