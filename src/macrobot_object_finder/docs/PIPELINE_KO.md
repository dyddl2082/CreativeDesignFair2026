# MacRobot Object Finder v0.2 Pipeline

```text
Pi: D435 → depth candidate → JPEG crop
WSL2: filter → DINO global retrieval → DINO patch heatmap → temporal track
Finder: goal/session/result normalization
Pi: patch pixel의 aligned depth 재표본화 → optical 3D → base_link TF
```

## Threshold profile

운영자가 물체가 보인다고 확인한 명시적 calibration 세션만 threshold를 변경할 수 있다. 일반 finder는 threshold를 스스로 낮추지 않는다.

## 네트워크

전체 RGB/depth/PointCloud2는 WSL2 finder가 구독하지 않는다. 후보 crop과 작은 metadata만 전송한다.
