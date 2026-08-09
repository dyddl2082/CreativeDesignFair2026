from pathlib import Path

import cv2
import numpy as np

from candidate_filter.filter_core import (
    CandidateMeasurements,
    FilterConfig,
    color_similarity_to_profile,
    compute_image_features,
    decode_compressed_image,
    evaluate_candidate,
    load_reference_profile,
)


def _patterned_image(color, width=160, height=120):
    image = np.full((height, width, 3), color, dtype=np.uint8)
    cv2.rectangle(image, (25, 22), (width - 25, height - 22), (35, 35, 35), 3)
    cv2.line(image, (40, height // 2), (width - 40, height // 2), (120, 120, 120), 2)
    return image


def _measurements(**overrides):
    values = dict(
        encoded_width=160,
        encoded_height=120,
        bbox_width_px=130,
        bbox_height_px=95,
        median_depth_m=0.55,
        depth_std_m=0.025,
        valid_depth_ratio=0.90,
        fill_ratio=0.65,
        foreground_height_m=0.055,
        proposal_score=0.80,
        touches_border=False,
        sync_offset_abs_sec=0.012,
        size_limit_met=True,
        estimated_width_m=0.07,
        estimated_height_m=0.05,
    )
    values.update(overrides)
    return CandidateMeasurements(**values)


def test_jpeg_decode_round_trip():
    image = _patterned_image((220, 220, 220))
    success, encoded = cv2.imencode(".jpg", image)
    assert success
    decoded = decode_compressed_image(encoded.tobytes())
    assert decoded.shape == image.shape


def test_reference_color_prefers_similar_view(tmp_path: Path):
    config = FilterConfig(min_sharpness=0.0)
    target_dir = tmp_path / "Buds3"
    target_dir.mkdir()
    assert cv2.imwrite(str(target_dir / "view_01.jpg"), _patterned_image((235, 235, 235)))
    assert cv2.imwrite(str(target_dir / "view_02.jpg"), _patterned_image((210, 220, 225)))

    profile = load_reference_profile("Buds3", target_dir, config)
    assert profile.available
    white_features = compute_image_features(_patterned_image((230, 230, 230)), config)
    red_features = compute_image_features(_patterned_image((30, 30, 220)), config)
    white_score = color_similarity_to_profile(white_features.color_histogram, profile, 2)
    red_score = color_similarity_to_profile(red_features.color_histogram, profile, 2)
    assert white_score is not None and red_score is not None
    assert white_score > red_score
    assert white_score > 0.70


def test_depth_hard_filter_rejects_far_candidate():
    config = FilterConfig(min_sharpness=0.0)
    features = compute_image_features(_patterned_image((220, 220, 220)), config)
    result = evaluate_candidate(
        _measurements(median_depth_m=2.0),
        features,
        profile=None,
        config=config,
    )
    assert not result.accepted
    assert result.reject_stage == "hard"
    assert result.reject_reason == "depth_too_far"


def test_safe_mode_accepts_valid_candidate_without_profile():
    config = FilterConfig(min_sharpness=0.0, enforce_soft_score=False)
    features = compute_image_features(_patterned_image((220, 220, 220)), config)
    result = evaluate_candidate(_measurements(), features, profile=None, config=config)
    assert result.accepted
    assert result.color_score is None
    assert 0.0 <= result.filter_score <= 1.0


def test_soft_filter_can_reject_by_threshold():
    config = FilterConfig(
        min_sharpness=0.0,
        enforce_soft_score=True,
        min_filter_score=0.99,
    )
    features = compute_image_features(_patterned_image((220, 220, 220)), config)
    result = evaluate_candidate(_measurements(), features, profile=None, config=config)
    assert not result.accepted
    assert result.reject_stage == "soft"
    assert result.reject_reason == "filter_score_below_threshold"


def test_physical_size_filter_rejects_large_bbox():
    config = FilterConfig(min_sharpness=0.0, enable_physical_size_filter=True)
    features = compute_image_features(_patterned_image((220, 220, 220)), config)
    result = evaluate_candidate(
        _measurements(estimated_width_m=0.40, estimated_height_m=0.30),
        features,
        profile=None,
        config=config,
    )
    assert not result.accepted
    assert result.reject_reason in {
        "physical_short_side_too_large",
        "physical_long_side_too_large",
    }
