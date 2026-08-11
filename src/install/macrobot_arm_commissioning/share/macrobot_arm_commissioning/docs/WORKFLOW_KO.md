# 권장 커미셔닝 순서

## 1. dry-run 연결 확인

```bash
ros2 launch macrobot_arm_commissioning commissioning_pipeline.launch.py \
  dry_run:=true \
  require_safe_region:=true \
  safe_region_csv:=$HOME/MacRobot/data/safe_region_exact_gripper_fine/safe_connected_samples.csv
```

대화형 CLI에서 메뉴 0으로 topic 연결과 현재 상태를 기록한다.

## 2. pulse와 영점 보정

실물 서보를 안전하게 지지하고, 필요할 때만 raw pulse jog를 사용한다.

보정 결과는 하나의 보고서에 저장된다.

```text
~/MacRobot/data/commissioning/arm_commissioning_report.yaml
```

## 3. 보정값 적용 및 재시작

```bash
ros2 run macrobot_arm_commissioning apply_report_recommendations \
  --report $HOME/MacRobot/data/commissioning/arm_commissioning_report.yaml \
  --actuator-input $HOME/MacRobot/src/macrobot_safe_region/config/actuator_limits.yaml \
  --in-place
```

관련 패키지를 다시 빌드하고 파이프라인을 재시작한다.

## 4. safe-region 재생성 판단

다음 값이 달라졌다면 기존 safe-region CSV를 재사용하면 안 된다.

```text
zero_deg
sign
command_min_deg
command_max_deg
model_multiplier
논리 joint limit
collision geometry
```

pulse_min/center/max만 바뀌고 nominal command degree mapping이 그대로라면 MoveIt 기하 안전영역은 바뀌지 않지만, 실제 pulse 출력은 달라진다.

보정 후 전체 형상 scan:

```bash
ros2 launch macrobot_safe_region \
  generate_safe_region_exact_gripper.launch.py \
  scan_config:=$(
    ros2 pkg prefix --share macrobot_safe_region
  )/config/full_fine_scan.yaml \
  output_directory:=$HOME/MacRobot/data/safe_region_exact_gripper_fine_calibrated
```

## 5. 방향과 기구 제약 시험

새 보정 파일과 새 safe-region을 사용해 q1 +0.15, q2 +0.15, q3 +0.15를 시험한다.

## 6. 대표 경계 시험

커미셔닝 도구는 safe-region grid의 connected 경로를 따라 저속 waypoint를 전송한다. 다음을 자동 선택한다.

```text
home
q1/q2 min/max 안쪽
gripper open/half/near-close
q1+q2 결합 경계 안쪽
빈번한 collision pair 바로 안쪽
```

## 7. 반복 정밀도, 하중, 온도

무부하와 실제 예상 하중 조건을 각각 별도 시험으로 기록한다.

## 8. grasp_frame 보정

세 개 이상의 q3 상태에서 실제 clamp 접촉 중심을 측정하고 기하 파라미터를 피팅한다.

## 9. primitive와 grasp profile

HOME, STOW, OPEN, CLOSE, PRE_GRASP, LOWER, LIFT, PLACE를 검증된 logical joint goal로 저장한다. 이후 물체별 profile을 같은 보고서에 추가한다.
