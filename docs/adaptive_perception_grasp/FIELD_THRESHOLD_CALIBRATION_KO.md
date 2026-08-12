# 물체별·환경별 DINOv2 threshold 현장 보정


> 보정 시작 시 calibrator는 `/candidate_filter/target`과 `/embedding_retrieval/target`을 함께 설정한다. 따라서 object별 color profile과 DINO positive/negative bank가 같은 대상 이름을 사용한다.

## 목적

고정 global threshold 하나를 모든 조명·배경·대회장에 사용하는 대신, 운영자가 대상 물체가 보인다고 명시적으로 확인한 짧은 세션에서 target과 현장 negative 점수 분포를 수집한다.

정상 탐색 중에는 threshold를 자동으로 낮추지 않는다.

## 계산

```text
target_positive_p10
negative_positive_p99
→ min_positive_similarity = 중간값

target_margin_p10
negative_margin_p99
→ min_margin = 중간값
```

다음 최소 분리 폭을 만족하지 않으면 적용을 거부한다.

```text
positive separation >= 0.03
margin separation   >= 0.02
```

## 실행

```bash
ros2 run macrobot_object_finder threshold_calibration_cli \
  calibrate Eraser --environment arena_1 --duration 10 --confirm-visible
```

`--confirm-visible`이 없으면 명령을 거부한다.

결과:

```bash
ros2 topic echo --field data /object_finder/calibration/result
```

저장:

```text
~/MacRobot/data/perception/threshold_profiles.yaml
```

## 실패 해석

```text
insufficient_target_samples
→ crop/embedding 결과 수가 부족

target_and_field_negative_distributions_overlap
→ threshold만으로 분리 불가능; positive view 또는 hard negative 추가 필요

embedding_set_parameters_service_unavailable
→ embedding_retrieval node가 실행 중인지 확인
```

활성 환경 ID는 launch에서 고정한다.

```bash
ros2 launch macrobot_object_finder object_finder_wsl.launch.py \
  environment_id:=competition_arena_1
```

이 값은 목표 물체가 바뀔 때 어떤 threshold profile을 자동 적용할지 결정한다.

## 점수 계층 분리

현장 보정이 바꾸는 값은 DINO embedding의 `min_positive_similarity`와 `min_margin`이다. temporal confirmation은 embedding 결과의 `accepted` 상태를 사용하며, localizer·alignment·camera-teach의 별도 `minimum_score` 기본값은 `0.0`으로 두어 같은 숫자를 여러 의미로 중복 적용하지 않는다. 정렬 안전성은 localization quality, depth/center uncertainty, stability, orientation, IK와 safe-region으로 판단한다.
