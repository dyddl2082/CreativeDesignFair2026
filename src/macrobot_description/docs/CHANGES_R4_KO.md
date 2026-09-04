# MacRobot URDF r4 변경 내역

## 기준

- 입력: `macrobot_description(4).zip`
- 이전 실행 revision: `macrobot-serial-2axis-2026-09-01-r3`
- 새 revision: `macrobot-serial-2axis-2026-09-04-r4`

## 최신 CAD에서 실제로 바뀐 항목

- `robot_arm_link` 질량·관성·형상 변경
- `gripper_link` 질량·관성·형상 변경
- 두 번째 팔 관절 원점 Z가 `0.000 m`에서 `0.010 m`로 변경
- 그리퍼 기어·addition·clamp 전체 배치가 이동
- 첫 번째 팔 관절의 내보내기 RPY가 변경
- 작은 그리퍼 서보 기어의 내보내기 축 부호가 `+Z`에서 `-Z`로 변경
- 카메라 마커와 바퀴 관절 위치는 이전 실행 좌표 기준으로 변하지 않음

## 검토 과정에서 적용한 정규화

1. Fusion의 `robot_arm_joint`를 `arm_lift_joint`로 변경했습니다.
2. Fusion의 팔 끝 `gripper_joint`를 `wrist_pitch_joint`로 변경했습니다.
3. 별도 논리 `gripper_joint`를 추가하여 `q3`를 모든 기어·집게 mimic의 master로 만들었습니다.
4. shoulder 유효 축이 `base_link +Y`가 되도록 고정 회전을 보정하여 과거의 수평 비틀림 재발을 막았습니다.
5. 작은 서보 기어는 로컬 축을 `+Z`, mimic을 `+2`로 정규화했습니다. 그 결과 왼쪽 큰 기어와 반대 방향으로 2배 회전합니다.
6. `camera_link`를 1 mm RGB 렌즈 마커 중심으로 다시 잡았습니다.
7. generic `ros2_control`과 모든 4-bar 팔 참조를 활성 모델에서 제거했습니다.
8. 최신 DAE에서 exact collision STL을 다시 생성했습니다.

## 새 기준점

- `base_link -> camera_link`: `-0.030650 0.060623 0.025820` m
- `base_link -> arm_lift_joint`: `0.030000 0.093700 0.057900` m
- `robot_arm_link -> wrist_pitch_joint`: `0.161000 0.000400 0.010000` m
- `gripper_link -> grasp_nominal`: `0.020700 0.211500 -0.008098` m
- 영점 `base_link -> grasp_nominal`: `-0.181900056 0.063000003 0.226997937` m
