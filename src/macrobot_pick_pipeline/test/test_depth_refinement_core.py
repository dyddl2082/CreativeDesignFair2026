import numpy as np

from macrobot_pick_pipeline.depth_refinement_core import (
    decode_depth_image,
    refine_depth_window,
)


def test_decode_z16_and_refine_patch_center():
    raw = np.full((20, 20), 1000, dtype=np.uint16)
    raw[8:13, 8:13] = 420
    image = decode_depth_image(
        data=raw.tobytes(), width=20, height=20, step=40,
        encoding="16UC1", is_bigendian=False,
    )
    estimate = refine_depth_window(
        image, center_x=10, center_y=10, radius_px=2,
        fallback_depth_m=0.42, minimum_samples=8,
    )
    assert estimate.available
    assert abs(estimate.depth_m - 0.42) < 1e-6
    assert estimate.source == "aligned_depth_window"
