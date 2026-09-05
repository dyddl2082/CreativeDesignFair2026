import numpy as np

from macrobot_pick_pipeline.depth_clearance_core import estimate_clearance


def test_clearance_uses_conservative_low_percentile():
    depth = np.full((100, 100), 2.0, dtype=np.float32)
    depth[50:70, 45:55] = 0.35
    result = estimate_clearance(
        depth,
        width_fraction=0.30,
        y_min_fraction=0.30,
        y_max_fraction=0.90,
        percentile=10.0,
        minimum_valid_fraction=0.01,
    )
    assert result.available
    assert 0.30 <= result.clearance_m <= 2.0


def test_clearance_fails_closed_when_depth_is_missing():
    depth = np.zeros((40, 40), dtype=np.float32)
    result = estimate_clearance(depth, minimum_valid_fraction=0.1)
    assert not result.available
    assert result.reason == "insufficient_valid_depth"
