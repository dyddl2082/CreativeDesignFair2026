# macrobot_description

현재 Fusion 내보내기 `macrobot_description(4).zip`를 MacRobot 실행 구조에 맞게 검토한 ROS 2 Jazzy description 패키지입니다.

- 모델 revision: `macrobot-serial-2axis-2026-09-04-r4`
- 활성 논리 관절: `arm_lift_joint`, `wrist_pitch_joint`, `gripper_joint`
- 로봇팔: 독립 직렬 2축; `q2`는 `q1+q2`가 아니라 직접 사용
- 그리퍼: `q3=0` 열림, 양수 닫힘; 작은 서보 기어는 `+2*q3`
- 카메라: `camera_link`는 RGB 렌즈 중심의 1 mm CAD 마커
- Fusion generic `ros2_control` 블록 제거
- 최신 DAE에서 변환한 exact binary STL collision 포함

## 빌드

```bash
cd ~/MacRobot
source /opt/ros/jazzy/setup.bash
colcon build --packages-select macrobot_description --symlink-install
source install/setup.bash
```

## 정적 검사

```bash
python3 ~/MacRobot/src/macrobot_description/scripts/validate_description.py \
  ~/MacRobot/src/macrobot_description
```

## RViz 방향 검사

```bash
ros2 launch macrobot_description display_full.launch.py
```

GUI에서 각 축을 한 번에 하나씩 `0 -> +0.05 -> 0 -> -0.05 -> 0`으로 시험합니다. 상세 기대값은 `docs/JOINT_DIRECTION_AUDIT_KO.md`를 참고하십시오.

이 패키지를 적용하면 이전 revision의 MoveIt self-collision 결과, safe-region, PICK/PLACE keyframe은 무효입니다.
