# 카메라–로봇팔 연동 구조

## 1. 토픽 구조

```text
/macrobot/pick/goal (std_msgs/String)
        ↓
macrobot_pick_coordinator
        ├─ /object_finder/goal
        ├─ /macrobot/pick/active_target
        │
        └─ /macrobot/perception/localized_detection 수신
                     ↓
              안정성 필터
                     ↓
              3D grasp 계획
                     ↓
/macrobot/arm/joint_goal
        ↓
기존 macrobot_ik_validator
        ↓
/macrobot/arm/validated_joint_goal
        ↓
기존 macrobot_arm_servo_bridge
        ↓
WSL2: dry-run RViz
실물: ARM_US → Pico → PCA9685
```

## 2. 실제 D435F 경로

기존 `object_finder` 결과가 다음 값을 포함한다고 가정한다.

```json
{
  "event": "object_found",
  "object_name": "Buds3",
  "found": true,
  "score": 0.82,
  "center_px": {"x": 320, "y": 240},
  "depth_m": 0.42,
  "depth_valid": true
}
```

`detection_localizer_node`는 color `CameraInfo`의 `(fx, fy, cx, cy)`를 이용해 optical-frame 3D 좌표를 만든다.

```text
X = (u - cx) Z / fx
Y = (v - cy) Z / fy
Z = depth_m
```

이후 tf2로:

```text
camera_color_optical_frame → base_link
```

변환하고 `/macrobot/perception/localized_detection`에 게시한다.

## 3. 안정된 detection 판정

한 프레임 검출만으로 팔을 움직이지 않는다.

기본 조건:

```text
최근 1.5초 안에 5회 이상
score ≥ 0.55
3D 점들의 최대 반경 ≤ 12 mm
물체 이름 일치
```

조건을 만족한 점들의 median을 실제 목표로 고정한다.

## 4. arm-plane 제약

현재 팔 IK는 base X–Z 평면의 2자유도 모델이다. grasp frame의 Y는 약:

```text
Y = 0.0645 m
```

이다. 검출 물체가 이 평면에서 너무 멀면 팔만으로 잡을 수 없으므로 다음 이벤트를 낸다.

```text
/macrobot/base/alignment_request
```

현재 단계에서는 차체를 자동으로 움직이지 않고 `base_alignment_required`로 종료한다. 향후 차체 정렬 노드가 이 요청을 처리하게 된다.

## 5. grasp plan

profile은 다음 offset을 가진다.

```text
grasp_point   = object_point + grasp_offset_base
pregrasp      = grasp_point  + pregrasp_offset_base
lift          = grasp_point  + lift_offset_base
```

기본 순서:

```text
OPEN
PRE_GRASP
APPROACH
CLOSE
LIFT
```

중요한 구현 사항:

- `PRE_GRASP`는 열린 그리퍼 형상으로 IK를 푼다.
- 최종 `GRASP` 위치의 q1/q2는 **닫힌 q3 형상**으로 IK를 푼다.
- 실제 접근 시에는 동일 q1/q2에 q3만 open으로 둔다.
- CLOSE 후 동적인 `grasp_frame`이 물체 중심에 오도록 하기 위한 방식이다.

## 6. commissioning report 연동

다음 파일이 존재하면 자동으로 읽는다.

```text
~/MacRobot/data/commissioning/arm_commissioning_report.yaml
```

다음 항목을 object profile seed로 사용한다.

```text
pre_grasp_q → pre_grasp_seed_q
grasp_q     → grasp_seed_q
lift_q      → lift_seed_q
close_q3    → close_q3
```

기존 음수-q3 시절의 report가 들어오면 `close_q3 < 0` 값은 무시한다.

## 7. 안전 경로

pick coordinator가 publish하는 모든 자세는 다음 토픽으로만 보낸다.

```text
/macrobot/arm/joint_goal
```

따라서 기존:

```text
IK validator
safe-region
servo bridge runtime interpolation validator
```

를 전부 거친다. `/validated_joint_goal`, `/logical_joint_states`, `/pico_debug/cmd`로 직접 publish하지 않는다.
