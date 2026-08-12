# DINOv2 Patch Heatmap 위치 정제

## 기존 문제

큰 candidate crop에 케이블과 목표 물체가 함께 있으면 global DINO similarity는 목표를 맞게 식별해도 candidate bbox 중심은 케이블 쪽일 수 있다.

## 새 처리

```text
DINOv2 forward 1회
├─ CLS/global embedding → 물체 식별
└─ patch token grid
    ├─ positive bank와 patch cosine similarity
    ├─ negative bank와 patch cosine similarity
    ├─ patch margin heatmap
    ├─ foreground mask soft prior
    ├─ connected target-like region
    └─ center, ROI, axial orientation, quality
```

정제 center는 원본 color image pixel로 다시 매핑된다. WSL2는 전체 카메라 영상을 새로 구독하지 않는다. 이미 전송된 후보 JPEG crop만 사용한다.

Pi의 `detection_localizer_node`는 해당 pixel 주변의 aligned depth를 다시 읽어 median/MAD/std 기반으로 정제한다.

## 확인 필드

```text
localization_available
localization_method = dinov2_patch_margin
localization_quality
localization_peak_positive
localization_peak_margin
localized_center_x/y
localized_roi
orientation_deg/class/quality
```

## 한계와 실패 정책

- 방향은 2D 이미지 평면의 180° 주축이며 6D pose가 아니다.
- reference image global embeddings와 patch token의 cosine map을 사용한다.
- patch localization 품질이 기준보다 낮으면 해당 관측은 정렬 입력으로 사용하지 않는다.
- 정밀 운용 기본값은 `allow_candidate_depth_fallback: false`이다. patch 중심과 동기화된 Pi aligned-depth frame을 얻지 못하면 candidate bbox의 coarse median depth로 조용히 대체하지 않고 관측을 폐기한다.
- WSL debug crop에는 patch ROI, 중심, 주축이 작은 JPEG overlay로 표시될 수 있지만 전체 D435 RGB/depth stream을 새로 구독하지 않는다.

## Reference patch prototype bank

Heatmap은 query patch token을 global CLS bank에만 비교하지 않는다. 등록 positive/negative 이미지에서도 DINO patch token을 추출하고, 각 이미지의 global descriptor와 잘 맞는 salient patch를 선택한 뒤 cosine farthest-point 방식으로 압축한 same-token prototype bank를 사용한다.

기본값:

```yaml
max_positive_patch_reference_images: 32
max_negative_patch_reference_images: 64
reference_patch_max_per_image: 32
positive_patch_prototype_count: 192
negative_patch_prototype_count: 256
```

첫 `rebuild_banks`는 patch prototype 생성 때문에 오래 걸릴 수 있지만, 이후에는 `*_patch_prototypes.npz` cache를 사용한다. 등록 이미지 또는 patch 설정이 바뀌면 signature가 달라져 자동 재생성된다.
