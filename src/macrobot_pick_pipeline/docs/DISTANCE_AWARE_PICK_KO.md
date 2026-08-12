# 원거리 인식 → 근거리 파지 Handoff

## 문제

현재 로봇팔의 안정적인 작업 반경은 약 0.30 m 이내지만, DINOv2는 물체가 조금 더 멀리 있어 전체 형태가 crop에 들어올 때 더 높은 점수를 낸다. 따라서 같은 threshold를 파지 직전까지 강제하면 다음 현상이 생긴다.

```text
원거리: 전체 물체가 보임 → DINO 점수 높음 → confirmed
근거리: 일부만 보이거나 crop 분포가 바뀜 → 점수 하락 → expired/object_lost
```

## 해결 방식

정식 pick은 두 거리에서 역할을 분리한다.

```text
1. Recognition pose
   - 팔 작업 반경 밖이어도 됨
   - DINO threshold를 엄격하게 적용
   - 대상 identity와 3D point를 확정

2. Distance handoff
   - 확정한 물체점을 Pico odom 좌표로 잠금
   - finder를 취소해 근거리 점수 하락을 실패로 해석하지 않음
   - 좌우 궤도 encoder odom으로 기록된 grasp pose까지 짧게 접근

3. Grasp pose
   - 물체가 설정된 최대 0.30 m 안에 있는지 확인
   - 이동 오차와 회전 drift를 uncertainty budget으로 계산
   - semantic keyframe IK와 safe-region preflight
   - OPEN → PRE_GRASP → GRASP_OPEN → CLOSE → LIFT
```

이 방식은 근거리 DINO score를 낮춰서 억지로 통과시키는 것이 아니다. **대상 identity는 원거리에서 확정하고, 근거리에서는 동일한 정지 물체의 odom 좌표를 사용한다.**

## 안전 가정

Distance handoff 동안 다음을 가정한다.

- 물체가 움직이지 않는다.
- Pico가 재부팅되지 않는다.
- `RESET_ODOM`을 실행하지 않는다.
- open-loop `MOTOR`를 사용하지 않는다.
- 충돌이나 큰 track slip으로 차체가 밀리지 않는다.

다음 uncertainty를 합산한다.

```text
원거리 localized point 안정 반경
원거리 depth 표준편차
직선 이동 오차율 기본 1.5%
회전각 오차율 기본 2%
360° 회전당 전후 drift 기본 1 cm
```

추정 uncertainty가 기본 2.5 cm를 넘으면 `POSE_ESTIMATE_UNRELIABLE`로 중단한다.

## 신규 등록 절차

### 1. 원거리 search pose 기록

Eraser 전체가 잘 보이고 threshold를 안정적으로 통과하는 거리에 로봇을 둔다.

```bash
ros2 run macrobot_pick_pipeline stored_object_pick_cli \
  record-search Eraser \
  --profile Eraser
```

저장 항목:

```text
search_pose_odom
object_point_odom
recognition point/range/score
```

### 2. Teleop으로 30 cm 이내 grasp pose로 접근

Pico 전원을 유지하고 encoder-bounded `MOVE_CM`/`TURN_DEG` 기반 step teleop만 사용한다.

### 3. Close grasp pose 기록

이 단계에서는 DINO 결과가 필요 없다. 원거리에서 저장한 `object_point_odom`과 현재 `ODOM?`으로 물체의 현재 `base_link` 위치를 재구성한다.

```bash
ros2 run macrobot_pick_pipeline stored_object_pick_cli \
  record-grasp Eraser \
  --profile Eraser \
  --grasp-keyframes Eraser \
  --max-grasp-range 0.30
```

30 cm보다 멀면 저장을 거부한다.

### 4. Semantic keyframe 기록

근거리 DINO가 불안정해도 저장된 close reference를 명시적으로 사용한다.

```bash
ros2 run macrobot_pick_pipeline grasp_keyframe_cli \
  capture Eraser Eraser OPEN \
  --stored-profile Eraser

ros2 run macrobot_pick_pipeline grasp_keyframe_cli \
  capture Eraser Eraser PRE_GRASP \
  --stored-profile Eraser

ros2 run macrobot_pick_pipeline grasp_keyframe_cli \
  capture Eraser Eraser GRASP_OPEN \
  --stored-profile Eraser

ros2 run macrobot_pick_pipeline grasp_keyframe_cli \
  capture Eraser Eraser CLOSE \
  --stored-profile Eraser

ros2 run macrobot_pick_pipeline grasp_keyframe_cli \
  capture Eraser Eraser LIFT \
  --stored-profile Eraser
```

`OPEN`과 `CLOSE`는 object point를 사용하지 않지만 같은 명령 형식을 사용해도 된다.

완료:

```bash
ros2 run macrobot_pick_pipeline grasp_keyframe_cli finalize Eraser
```

## 실행

### 현재 원거리에서 물체가 보이는 시험

```bash
ros2 run macrobot_pick_pipeline stored_object_pick_cli \
  visible-test Eraser \
  --profile Eraser
```

### 저장 위치 복귀부터 전체 실행

```bash
ros2 run macrobot_pick_pipeline stored_object_pick_cli \
  run Eraser \
  --profile Eraser
```

정식 흐름:

```text
far search pose 복귀
→ finder/DINO confirmed
→ object_point_odom 잠금
→ finder 취소
→ recorded grasp pose까지 bounded odom approach
→ 30 cm reach + uncertainty gate
→ IK/safe-region preflight
→ semantic grasp
```

## 왜 threshold를 근거리에서 낮추지 않는가

근거리 score 하락은 물체가 아닌 후보와의 분리가 나빠지는 현상일 수 있다. 자동으로 threshold를 낮추면 false positive 위험이 커진다. 이번 방식은 acquisition threshold를 유지하고, 한 번 확정한 정지 물체만 제한된 거리와 motion budget 안에서 추적한다.

## 공개 API 영향

팀원이 호출하는 API는 바뀌지 않는다.

```python
robot.ALIGN_WITH_OBJECT(object_id=ObjectId.ERASER)
robot.PICK_OBJECT(object_id=ObjectId.ERASER)
```

원거리 acquisition, finder cancel, odom handoff, arm reach gate, IK preflight는 내부 black-box 단계다.
