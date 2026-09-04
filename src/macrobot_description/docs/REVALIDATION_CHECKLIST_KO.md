# r4 적용 후 재검증 체크리스트

- [ ] description validator 통과
- [ ] RViz q1/q2/q3 소범위 방향 확인
- [ ] 실물 서보 영점·부호·배율·기계 한계 확인
- [ ] `macrobot_arm_kinematics`가 r4 YAML을 읽는지 확인
- [ ] FK/IK 정상·도달 불가·연속 입력 시험
- [ ] MoveIt SRDF/self-collision matrix 재생성
- [ ] r4 coarse safe-region 생성
- [ ] r4 fine connected safe-region 생성
- [ ] 카메라 RGB-anchor TF 중복·optical 축 검사
- [ ] `base_link` 물체 3차원 위치화 재검증
- [ ] PICK keyframe/profile 재기록 또는 전 경로 재검증
- [ ] PLACE 역과정 전 경로 재검증
- [ ] 재부팅 persistence patch의 object bank/profile 유지 확인
- [ ] stale odometry 위치가 자동 목적지로 사용되지 않는지 확인
- [ ] dry-run 후 무부하 저속 시험
- [ ] 실제 물체 PICK/PLACE 통합시험
