from macrobot_pick_pipeline.planner import DetectionSample, StablePointFilter


def _sample(angle, quality, stamp):
    return DetectionSample(
        stamp_sec=stamp,
        object_name="Eraser",
        score=0.8,
        point_base=(0.24, 0.06, 0.08),
        localization_quality=0.8,
        center_std_px=1.0,
        depth_std_m=0.002,
        orientation_deg=angle,
        orientation_class="vertical",
        orientation_quality=quality,
    )


def test_consistent_low_quality_angles_do_not_become_quality_one():
    filt = StablePointFilter()
    filt.add(_sample(90.0, 0.10, 1.0))
    filt.add(_sample(91.0, 0.12, 1.1))
    filt.add(_sample(89.0, 0.08, 1.2))
    stable = filt.stable(
        now_sec=1.3,
        object_name="Eraser",
        minimum_score=0.0,
        minimum_count=3,
        window_sec=1.0,
        radius_m=0.01,
    )
    assert stable is not None
    assert 0.0 < stable.orientation_quality < 0.2


def test_good_consistent_angles_keep_useful_quality():
    filt = StablePointFilter()
    filt.add(_sample(90.0, 0.80, 1.0))
    filt.add(_sample(91.0, 0.75, 1.1))
    filt.add(_sample(89.0, 0.85, 1.2))
    stable = filt.stable(
        now_sec=1.3,
        object_name="Eraser",
        minimum_score=0.0,
        minimum_count=3,
        window_sec=1.0,
        radius_m=0.01,
    )
    assert stable is not None
    assert stable.orientation_quality > 0.70
