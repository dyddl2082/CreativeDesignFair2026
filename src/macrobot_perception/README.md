# macrobot_perception 0.3.0

WSL2에서 후보 crop만 받아 candidate filter, DINOv2 global retrieval, DINOv2 patch-token localization, temporal confirmation을 수행한다.

## 핵심 변경

```text
DINO global embedding → 물체 식별
DINO patch heatmap    → crop 안의 실제 물체 중심/ROI/영상면 방향 정제
```

더 이상 `horizontal_error_norm`이나 `suggested_turn`을 발행하지 않는다. 정렬은 Pi의 `detection_localizer_node`가 만든 `base_link` 3D point로 수행한다.

## 실행

```bash
source ~/MacRobot/.venv-embedding/bin/activate
source /opt/ros/jazzy/setup.bash
source ~/MacRobot/install/setup.bash
ros2 launch macrobot_perception pc_recognition_pipeline.launch.py
```

전체 finder를 사용할 때는 이 launch 대신 다음 하나만 실행한다.

```bash
ros2 launch macrobot_object_finder object_finder_wsl.launch.py
```

## 결과

```text
/candidate_filter/results
/embedding_retrieval/results
/temporal_confirmation/confirmed
```

`EmbeddingRetrievalResult`의 새 필드:

```text
localization_available / localization_quality
localized_center_x/y / localized_roi
orientation_deg/class/quality
```

기본 DINO threshold는 현재 임시값 `0.45`, margin `0.05`이며, 현장에서는 `threshold_calibration_cli`로 물체별 profile을 만들어 적용한다.

## DINO patch prototype cache

Patch heatmap은 query patch를 등록 이미지의 same-token positive/negative prototype과 비교한다. 처음 bank를 만들 때는 global embedding cache보다 시간이 더 걸릴 수 있다. 이후에는 embedding cache 아래의 `positive_patch_prototypes.npz`, `negative_patch_prototypes.npz`를 재사용한다. 등록 이미지 또는 patch parameter가 바뀌면 cache signature가 자동으로 무효화된다.
