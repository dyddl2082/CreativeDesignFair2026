from pathlib import Path

import cv2
import numpy as np
import pytest

from d435_capture_crop.capture_core import (
    Roi,
    atomic_write_bytes,
    compute_depth_stats,
    crop_array,
    depth_to_meters,
    encode_image,
    map_roi_between_sizes,
    normalize_roi,
    sanitize_component,
)


def test_sanitize_component_preserves_korean_and_blocks_paths():
    assert sanitize_component("  Buds3 정면  ") == "Buds3_정면"
    value = sanitize_component("../../위험/이름")
    assert "/" not in value
    assert "\\" not in value
    assert value not in {".", ".."}


def test_normalize_roi_clamps_and_supports_negative_drag():
    assert normalize_roi({"x": 90, "y": 80, "width": 30, "height": 30}, 100, 100) == Roi(
        90, 80, 10, 20
    )
    assert normalize_roi({"x": 50, "y": 50, "width": -20, "height": -10}, 100, 100) == Roi(
        30, 40, 20, 10
    )


def test_normalize_roi_rejects_tiny_crop():
    with pytest.raises(ValueError):
        normalize_roi({"x": 1, "y": 1, "width": 5, "height": 5}, 100, 100, 10, 10)


def test_map_roi_between_color_and_depth_sizes():
    roi = Roi(160, 120, 320, 240)
    mapped = map_roi_between_sizes(roi, 640, 480, 320, 240)
    assert mapped == Roi(80, 60, 160, 120)


def test_depth_conversion_and_statistics():
    raw = np.array([[0, 500, 1000], [1500, 2000, 0]], dtype=np.uint16)
    depth_m = depth_to_meters(raw, "16UC1", 0.001)
    stats = compute_depth_stats(depth_m, min_depth_m=0.1, max_depth_m=3.0)
    assert stats.available
    assert stats.valid_count == 4
    assert stats.valid_ratio == pytest.approx(4 / 6)
    assert stats.median_m == pytest.approx(1.25)


def test_crop_and_atomic_jpeg_write(tmp_path: Path):
    image = np.zeros((80, 100, 3), dtype=np.uint8)
    image[20:60, 30:70] = (0, 255, 0)
    crop = crop_array(image, Roi(30, 20, 40, 40))
    assert crop.shape == (40, 40, 3)
    encoded = encode_image(crop, ".jpg", quality=90)
    destination = tmp_path / "crop.jpg"
    atomic_write_bytes(destination, encoded)
    decoded = cv2.imread(str(destination), cv2.IMREAD_COLOR)
    assert decoded is not None
    assert decoded.shape[:2] == (40, 40)
