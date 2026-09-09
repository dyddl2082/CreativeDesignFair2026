from pathlib import Path

from candidate_filter.reflection_gate import (
    ReflectionEvidence,
    ReflectionGateConfig,
    reflection_reject_reason,
)

ROOT = Path(__file__).resolve().parents[1]
NODE = ROOT / "candidate_filter" / "candidate_filter_node.py"
CONFIG = ROOT / "config" / "candidate_filter.yaml"


def _evidence(**overrides):
    values = dict(
        plane_found=True,
        foreground_height_valid=True,
        foreground_height_m=0.035,
        valid_depth_ratio=0.88,
        depth_std_m=0.018,
        foreground_mask_available=True,
        mask_fill_ratio=0.35,
    )
    values.update(overrides)
    return ReflectionEvidence(**values)


def test_physical_candidate_passes():
    config = ReflectionGateConfig()
    assert reflection_reject_reason(_evidence(), config) is None


def test_disabled_gate_is_passthrough():
    config = ReflectionGateConfig(enabled=False)
    evidence = _evidence(
        plane_found=False,
        foreground_height_valid=False,
        valid_depth_ratio=0.0,
        depth_std_m=1.0,
        foreground_mask_available=False,
    )
    assert reflection_reject_reason(evidence, config) is None


def test_fallback_candidate_without_plane_is_rejected():
    reason = reflection_reject_reason(
        _evidence(plane_found=False),
        ReflectionGateConfig(),
    )
    assert reason == "reflection_plane_unavailable"


def test_missing_plane_height_is_rejected():
    reason = reflection_reject_reason(
        _evidence(foreground_height_valid=False),
        ReflectionGateConfig(),
    )
    assert reason == "reflection_height_unavailable"


def test_too_low_foreground_is_rejected():
    reason = reflection_reject_reason(
        _evidence(foreground_height_m=0.003),
        ReflectionGateConfig(),
    )
    assert reason == "reflection_height_too_low"


def test_weak_depth_support_is_rejected():
    reason = reflection_reject_reason(
        _evidence(valid_depth_ratio=0.40),
        ReflectionGateConfig(),
    )
    assert reason == "reflection_depth_support_low"


def test_unstable_depth_is_rejected():
    reason = reflection_reject_reason(
        _evidence(depth_std_m=0.12),
        ReflectionGateConfig(),
    )
    assert reason == "reflection_depth_variation_high"


def test_missing_foreground_mask_is_rejected():
    reason = reflection_reject_reason(
        _evidence(foreground_mask_available=False),
        ReflectionGateConfig(),
    )
    assert reason == "reflection_mask_unavailable"


def test_implausible_mask_fill_is_rejected():
    low = reflection_reject_reason(
        _evidence(mask_fill_ratio=0.005),
        ReflectionGateConfig(),
    )
    high = reflection_reject_reason(
        _evidence(mask_fill_ratio=0.995),
        ReflectionGateConfig(),
    )
    assert low == "reflection_mask_fill_low"
    assert high == "reflection_mask_fill_high"


def test_node_runs_gate_before_jpeg_decode_and_dino_output():
    source = NODE.read_text(encoding="utf-8")
    callback = source.split("def _crop_callback", 1)[1].split(
        "def _base_result", 1
    )[0]
    assert "REFLECTION_REJECTION_V1" in callback
    assert callback.index("reflection_reject_reason(") < callback.index(
        "decode_compressed_image("
    )
    assert '"reflection_gate"' in callback


def test_config_enables_reflection_gate():
    text = CONFIG.read_text(encoding="utf-8")
    assert "enable_reflection_rejection: true" in text
    assert "reflection_require_plane: true" in text
    assert "reflection_require_foreground_height: true" in text
    assert "reflection_min_valid_depth_ratio: 0.60" in text
    assert "reflection_max_depth_std_m: 0.060" in text
