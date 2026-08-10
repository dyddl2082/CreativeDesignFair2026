# macrobot_pick_pipeline 0.2.0

카메라의 3D 물체 위치를 검증된 로봇팔 제어 경로에 연결하고, 실제 카메라와 로봇팔을 함께 사용해 다음 항목을 기록하는 패키지다.

- 물체 탐색과 파지 실행
- 카메라 보조 `grasp_frame` 보정
- 팔 primitive 기록·시험
- 물체별 grasp profile 기록·시험

## 실행 노드

```text
detection_localizer_node
pick_coordinator_node
mock_perception_node
pick_teach_node
pick_teach_cli
```

## 안전 원칙

`pick_teach_node`의 모든 시험 이동은 다음 경로만 사용한다.

```text
/macrobot/arm/joint_goal
→ IK validator
→ MoveIt safe-region
→ servo bridge
→ Pico
```

`/pico_debug/cmd`, `SERVO_US`, `ARM_US`를 직접 사용하지 않는다.

상세 사용법은 [`docs/CAMERA_ARM_TEACH_KO.md`](docs/CAMERA_ARM_TEACH_KO.md)를 확인한다.
