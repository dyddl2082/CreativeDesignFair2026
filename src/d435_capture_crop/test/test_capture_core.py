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


def _dataset_roots(tmp_path: Path) -> dict[str, Path]:
    return {
        "original": tmp_path / "objects",
        "curated": tmp_path / "curated" / "objects",
        "depth": tmp_path / "curated" / "depth",
        "metadata": tmp_path / "curated" / "metadata",
        "negative_library": tmp_path / "negative" / "library",
        "negative_backgrounds": tmp_path / "negative" / "backgrounds",
        "negative_confusers": tmp_path / "negative" / "confusers",
        "negative_originals": tmp_path / "negative" / "originals",
        "negative_depth": tmp_path / "negative" / "depth",
        "negative_metadata": tmp_path / "negative" / "metadata",
    }


def test_dataset_role_paths_keep_shared_negative_single_copy(tmp_path: Path):
    from d435_capture_crop.capture_core import build_dataset_paths

    roots = _dataset_roots(tmp_path)
    positive = build_dataset_paths(
        roots,
        dataset_role="positive",
        label="Buds3",
        target_object="",
        suffix="front_001",
    )
    assert positive.crop == tmp_path / "curated/objects/Buds3/front_001.jpg"
    assert positive.auto_negative_for_other_targets
    assert positive.requires_negative_sync

    shared = build_dataset_paths(
        roots,
        dataset_role="shared_negative",
        label="white_cup",
        target_object="",
        suffix="side_001",
    )
    assert shared.crop == tmp_path / "negative/library/white_cup/side_001.jpg"
    assert shared.reusable_for_all_targets
    assert shared.requires_negative_sync

    hard = build_dataset_paths(
        roots,
        dataset_role="hard_negative",
        label="white_cup",
        target_object="Buds3",
        suffix="close_001",
    )
    assert hard.crop == (
        tmp_path
        / "negative/confusers/Buds3/manual/white_cup/close_001.jpg"
    )
    assert not hard.reusable_for_all_targets


def test_hard_negative_requires_target(tmp_path: Path):
    from d435_capture_crop.capture_core import build_dataset_paths

    with pytest.raises(ValueError):
        build_dataset_paths(
            _dataset_roots(tmp_path),
            dataset_role="hard_negative",
            label="cup",
            target_object="",
            suffix="001",
        )


def test_negative_sync_reuses_other_objects_and_library(tmp_path: Path):
    from d435_capture_crop.negative_library import sync_negative_views

    curated = tmp_path / "curated" / "objects"
    library = tmp_path / "negative" / "library"
    confusers = tmp_path / "negative" / "confusers"

    (curated / "Buds3").mkdir(parents=True)
    (curated / "Cup").mkdir(parents=True)
    (library / "Mouse").mkdir(parents=True)
    (library / "Buds3").mkdir(parents=True)
    (confusers / "Buds3" / "manual" / "Cup").mkdir(parents=True)

    for path, value in [
        (curated / "Buds3" / "front.jpg", 30),
        (curated / "Cup" / "front.jpg", 80),
        (library / "Mouse" / "side.jpg", 120),
        (library / "Buds3" / "wrong.jpg", 160),
        (confusers / "Buds3" / "manual" / "Cup" / "manual.jpg", 200),
    ]:
        image = np.full((12, 12, 3), value, dtype=np.uint8)
        assert cv2.imwrite(str(path), image)

    summary = sync_negative_views(
        curated_root=curated,
        library_root=library,
        confusers_root=confusers,
    )

    buds_auto = confusers / "Buds3" / "_auto"
    cup_auto = confusers / "Cup" / "_auto"
    assert (buds_auto / "registered" / "Cup" / "front.jpg").exists()
    assert (buds_auto / "library" / "Mouse" / "side.jpg").exists()
    assert not (buds_auto / "library" / "Buds3" / "wrong.jpg").exists()
    assert (cup_auto / "registered" / "Buds3" / "front.jpg").exists()
    assert (confusers / "Buds3" / "manual" / "Cup" / "manual.jpg").exists()
    assert summary.target_count == 2
    assert summary.total_managed_files >= 4
