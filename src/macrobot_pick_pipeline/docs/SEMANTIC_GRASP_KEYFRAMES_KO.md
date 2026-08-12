# Semantic Grasp Keyframe

## 기록 단계

```text
OPEN
PRE_GRASP
GRASP_OPEN
CLOSE
LIFT
```

`OPEN`, `CLOSE`는 그리퍼 논리값만 저장한다. 나머지 세 단계는 현재 grasp_frame과 물체 3D 점의 상대 offset 및 IK seed를 저장한다.

## 실행 단계

```text
현재 object point
+ 기록된 object-relative offset
→ 현재 Cartesian target
→ IK
→ joint limit
→ safe-region 모든 segment preflight
→ /macrobot/arm/joint_goal
→ runtime validator
→ servo bridge interpolation
```

사람이 조작하는 데 걸린 시간은 저장하지 않는다. 각 단계의 이동 속도는 servo bridge 설정이 결정한다.

## 기록 예

```bash
ros2 run macrobot_pick_pipeline grasp_keyframe_cli capture Eraser Eraser OPEN
ros2 run macrobot_pick_pipeline grasp_keyframe_cli capture Eraser Eraser PRE_GRASP
ros2 run macrobot_pick_pipeline grasp_keyframe_cli capture Eraser Eraser GRASP_OPEN
ros2 run macrobot_pick_pipeline grasp_keyframe_cli capture Eraser Eraser CLOSE
ros2 run macrobot_pick_pipeline grasp_keyframe_cli capture Eraser Eraser LIFT
ros2 run macrobot_pick_pipeline grasp_keyframe_cli finalize Eraser
```

## 안전 거부

```text
*_ik_failed
*_lateral_alignment_failed
safe_region_path_rejected
object_orientation_class_mismatch
object_orientation_angle_mismatch
object_orientation_unreliable
```

## ALIGN 및 stored-pick 통합

`stored_object_pick_node`는 semantic keyframe executor를 기본으로 사용할 때 정렬 완료 직후 `preflight` subaction을 먼저 수행한다. `--align-only`에서도 이 검사를 통과해야 성공하므로, "기록 당시 상대 위치에 있음"과 "현재 상태에서 실제 파지 경로가 안전하고 도달 가능함"을 함께 확인한다.

## 취소 계약

물리 trajectory가 진행 중일 때 cancel은 다음 순서를 사용한다.

```text
RUNNING
→ CANCEL_REQUESTED
→ /macrobot/arm/stop
→ servo bridge trajectory_stopped 확인
→ CANCELED
```

`cancel_confirm_timeout_sec` 안에 `trajectory_stopped`가 확인되지 않으면 성공한 cancel로 보고하지 않고 `grasp_keyframe_cancel_failed / SAFE_STOP_UNCONFIRMED`로 종료한다. keyframe 사이에는 이전 trajectory가 이미 완료됐으므로 즉시 안전하게 취소할 수 있다. 그리퍼를 자동으로 열지 않는다.
