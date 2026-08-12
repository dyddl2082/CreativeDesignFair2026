from pathlib import Path

from macrobot_object_finder.threshold_core import (
    ScoreSample,
    ThresholdProfileStore,
    recommend_thresholds,
    split_target_and_negative,
)


def sample(frame, candidate, positive, margin, x, depth=0.4):
    return ScoreSample(frame, candidate, positive, positive-margin, margin, x, 100.0, depth, 0.8)


def test_field_calibration_separates_target_and_negatives(tmp_path: Path):
    frames = {}
    for frame in range(20):
        frames[frame] = [
            sample(frame, 1, 0.60 + 0.01 * (frame % 3), 0.12, 100.0 + frame * 0.2),
            sample(frame, 2, 0.34 + 0.01 * (frame % 2), 0.01, 300.0),
        ]
    target, negative = split_target_and_negative(frames)
    recommendation = recommend_thresholds(target, negative)
    assert recommendation.safe_to_apply
    assert 0.35 < recommendation.min_positive_similarity < 0.60
    assert 0.01 < recommendation.min_margin < 0.12

    store = ThresholdProfileStore(tmp_path / "thresholds.yaml")
    store.upsert("Eraser", "arena", recommendation, applied=False)
    loaded = ThresholdProfileStore(tmp_path / "thresholds.yaml").get("Eraser", "arena")
    assert loaded["embedding"]["min_positive_similarity"] == recommendation.min_positive_similarity


def test_calibration_refuses_overlapping_distributions():
    target = [sample(i, 1, 0.45, 0.04, 100.0) for i in range(20)]
    negative = [sample(i, 2, 0.44, 0.035, 300.0) for i in range(20)]
    recommendation = recommend_thresholds(target, negative)
    assert not recommendation.safe_to_apply
    assert recommendation.reason == "target_and_field_negative_distributions_overlap"
