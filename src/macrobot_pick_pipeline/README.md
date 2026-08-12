# macrobot_pick_pipeline 0.6.0

저장 위치 기반 finder, `base_link` 3D 정렬, Pi-local aligned-depth refinement, semantic grasp keyframe IK 실행을 연결한다.

## 핵심 변경

```text
카메라 중심 정렬 제거
→ DINO patch center + aligned depth + TF(base_link)

느린 사람 trajectory 기본 경로 제거
→ OPEN / PRE_GRASP / GRASP_OPEN / CLOSE / LIFT keyframe
→ 현재 물체 위치에 맞춰 IK 재계산
```

legacy arm_demo trajectory는 기존 파일 호환용으로만 유지한다.

## 실행

```bash
SAFE_CSV=$HOME/MacRobot/data/safe_region_collision_v2_fine/safe_connected_samples.csv
ros2 launch macrobot_pick_pipeline pick_pipeline_robot.launch.py \
  safe_region_csv:="$SAFE_CSV" \
  start_pico_debug:=true \
  start_base_alignment:=true \
  start_grasp_keyframes:=true \
  start_camera_teach:=false
```

## Keyframe 기록

```bash
ros2 run macrobot_pick_pipeline grasp_keyframe_cli capture Eraser Eraser OPEN
ros2 run macrobot_pick_pipeline grasp_keyframe_cli capture Eraser Eraser PRE_GRASP
ros2 run macrobot_pick_pipeline grasp_keyframe_cli capture Eraser Eraser GRASP_OPEN
ros2 run macrobot_pick_pipeline grasp_keyframe_cli capture Eraser Eraser CLOSE
ros2 run macrobot_pick_pipeline grasp_keyframe_cli capture Eraser Eraser LIFT
ros2 run macrobot_pick_pipeline grasp_keyframe_cli finalize Eraser
```

## Stored object 등록

```bash
ros2 run macrobot_pick_pipeline stored_object_pick_cli \
  record Eraser --profile Eraser --grasp-keyframes Eraser
```

## 실행

```bash
ros2 run macrobot_pick_pipeline stored_object_pick_cli visible-test Eraser --profile Eraser
ros2 run macrobot_pick_pipeline stored_object_pick_cli run Eraser --profile Eraser
```

모든 팔 동작은 `/macrobot/arm/joint_goal → validator → safe-region → servo bridge` 경로를 유지한다.

## ALIGN 성공과 취소

semantic keyframe profile이 연결된 stored object는 bearing/range/height만 맞았다고 ALIGN 성공으로 끝내지 않는다. 현재 object point에서 다섯 stage의 IK를 다시 계산하고, 현재 q부터 모든 stage까지 sampled safe-region preflight가 통과해야 성공한다. 실제 실행 중에는 기존 validator와 servo bridge가 다시 검사한다.

trajectory 도중 cancel은 `/macrobot/arm/stop`을 보낸 뒤 `trajectory_stopped`를 확인해야 `CANCELED`가 된다. 확인 timeout이면 `SAFE_STOP_UNCONFIRMED`로 실패하고 그리퍼를 자동으로 열지 않는다.
