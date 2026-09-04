# 조인트 방향 검토 결과

## 결론

최신 내보내기의 원시 축을 그대로 사용하지 않고, 이전 실물·RViz에서 확인한 논리 방향을 유지하도록 정규화했습니다.

| 논리 관절 | 양수 방향의 기대 동작 | 검토 결과 |
|---|---|---|
| `arm_lift_joint` (`q1`) | 영점 부근에서 파지점이 `+base X`, `+base Z` 방향 | 유지 |
| `wrist_pitch_joint` (`q2`) | 영점 부근에서 파지점이 주로 `+base Z` 방향 | 유지 |
| `gripper_joint` (`q3`) | 집게 간격 감소, 닫힘 | 유지 |
| `gripper_servo_joint` | `+2*q3`, 왼쪽 큰 기어와 반대 회전 | 원시 축 부호를 교정 |

shoulder axis in base:

```text
0.000000020 1.000000000 0.000000022
```

wrist axis in base at zero:

```text
0.000000020 1.000000000 -0.000000305
```

axis dot product:

```text
1.000000000000
```

## RViz 시험

```bash
ros2 launch macrobot_description display_full.launch.py
```

한 축씩 시험합니다.

```text
q1: 0 -> +0.05 -> 0 -> -0.05 -> 0
q2: 0 -> +0.05 -> 0 -> -0.05 -> 0
q3: 0 -> +0.05 -> +0.10 -> 0
```

기대 좌표는 `validation/KINEMATIC_SANITY_SAMPLES.csv`와 `validation/GRIPPER_DIRECTION_SAMPLES.csv`에 기록되어 있습니다.
