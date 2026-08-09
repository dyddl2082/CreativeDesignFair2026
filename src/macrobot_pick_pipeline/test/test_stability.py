from macrobot_pick_pipeline.planner import DetectionSample, StablePointFilter


def test_stable_cluster():
    filter_ = StablePointFilter()
    now = 100.0
    for index in range(5):
        filter_.add(
            DetectionSample(
                stamp_sec=now - 0.4 + index * 0.05,
                object_name="Buds3",
                score=0.9,
                point_base=(-0.15 + index * 0.0005, 0.0645, 0.12),
            )
        )
    result = filter_.stable(
        now_sec=now,
        object_name="Buds3",
        minimum_score=0.5,
        minimum_count=5,
        window_sec=1.0,
        radius_m=0.01,
    )
    assert result is not None
    assert result.sample_count == 5
    assert result.radius_m < 0.01


def test_unstable_cluster_rejected():
    filter_ = StablePointFilter()
    now = 100.0
    for index in range(5):
        filter_.add(
            DetectionSample(
                stamp_sec=now - 0.4 + index * 0.05,
                object_name="Buds3",
                score=0.9,
                point_base=(-0.15 + index * 0.02, 0.0645, 0.12),
            )
        )
    assert filter_.stable(
        now_sec=now,
        object_name="Buds3",
        minimum_score=0.5,
        minimum_count=5,
        window_sec=1.0,
        radius_m=0.01,
    ) is None
