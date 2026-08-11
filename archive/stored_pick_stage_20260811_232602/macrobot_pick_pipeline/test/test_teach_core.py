import pytest

from macrobot_pick_pipeline.teach_core import (
    ProfileDraft,
    RecordedStage,
    derive_pick_profile,
)


def stage(name, q, tool, target=(1.0, 2.0, 3.0)):
    return RecordedStage(
        name=name,
        q=q,
        tool_point_base=tool,
        target_point_base=target,
        captured_at="2026-08-10T00:00:00+00:00",
    )


def test_derive_camera_relative_profile():
    draft = ProfileDraft(
        object_name="Buds3",
        target_point_base=(1.0, 2.0, 3.0),
        started_at="now",
        speed_scale=0.4,
    )
    draft.capture(stage("PRE_GRASP", (0.1, 0.2, 0.0), (1.02, 2.0, 3.05)))
    draft.capture(stage("GRASP", (0.2, 0.3, 0.0), (1.01, 2.0, 3.01)))
    draft.capture(stage("CLOSE", (0.2, 0.3, 1.1), (1.005, 2.0, 3.002)))
    draft.capture(stage("LIFT", (0.0, 0.1, 1.1), (1.005, 2.0, 3.052)))

    profile = derive_pick_profile(draft)

    assert profile["open_q3"] == 0.0
    assert profile["close_q3"] == 1.1
    assert profile["grasp_offset_base"] == pytest.approx([0.005, 0.0, 0.002])
    assert profile["pregrasp_offset_base"] == pytest.approx([0.015, 0.0, 0.048])
    assert profile["lift_offset_base"] == pytest.approx([0.0, 0.0, 0.05])
    assert profile["pre_grasp_seed_q"] == [0.1, 0.2, 0.0]
    assert profile["grasp_seed_q"] == [0.2, 0.3, 0.0]
    assert profile["lift_seed_q"] == [0.0, 0.1, 1.1]


def test_missing_required_stage_is_rejected():
    draft = ProfileDraft(
        object_name="Buds3",
        target_point_base=(0.0, 0.0, 0.0),
        started_at="now",
    )
    draft.capture(stage("PRE_GRASP", (0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)))
    try:
        derive_pick_profile(draft)
    except ValueError as exc:
        assert "missing profile stages" in str(exc)
    else:
        raise AssertionError("missing stages must be rejected")
