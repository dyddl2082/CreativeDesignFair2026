# 카메라 좌측 offset과 정렬

이미지 중심에 물체를 놓는 방식은 사용하지 않는다.

```text
DINO patch center pixel
+ Pi aligned depth
+ CameraInfo
→ camera optical 3D
→ TF(base_link ← camera optical)
→ point_base
```

TF에 카메라의 좌측 offset, 높이, 회전이 포함되므로 카메라가 차체 중앙이 아니어도 별도의 turn-left/right 보정식을 추가하지 않는다.

정렬은 현재 `point_base`와 실제 파지 성공 시 기록한 `reference_point_base`를 비교한다.

```text
bearing error
range error
height error
localization quality
depth uncertainty
center uncertainty
optional axial orientation error
```

height는 평면 차체로 수정할 수 없으므로 허용 범위를 넘으면 거부한다. bearing과 range는 작은 `TURN_DEG`, `MOVE_CM` 후 다시 카메라로 관측하는 폐루프 방식이다.

정밀 정렬의 기본값은 `allow_candidate_depth_fallback: false`이다. DINO patch 중심에서 동기화된 aligned-depth 표본을 얻지 못하면 coarse candidate median depth로 정렬하지 않고 해당 관측을 폐기한다. 현장 진단 중에만 이 옵션을 명시적으로 완화한다.

## ALIGN 성공의 추가 조건

신규 semantic-keyframe profile을 사용하는 경우, bearing/range/height가 허용 범위에 들어온 것만으로 `ALIGN_WITH_OBJECT` 성공을 보고하지 않는다.

```text
현재 object point
→ OPEN/PRE_GRASP/GRASP_OPEN/CLOSE/LIFT 목표 재구성
→ 각 Cartesian stage IK
→ 관절 한계
→ 현재 q부터 모든 stage까지 sampled safe-region segment preflight
→ 모두 통과
→ ALIGN 성공 또는 실제 grasp 시작
```

따라서 위치는 맞지만 현재 물체점에서 IK가 없거나 중간 경로가 safe-region 밖이면 `TARGET_NOT_GRASPABLE`, `IK_FAILED`, 또는 `ARM_PATH_UNSAFE` 계열로 끝난다. 이 preflight는 조기 거부용이며 실제 실행 중 endpoint/path/interpolation을 다시 검사하는 runtime validator와 servo bridge를 대체하지 않는다.
