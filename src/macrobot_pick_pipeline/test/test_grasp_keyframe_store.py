from pathlib import Path

from macrobot_pick_pipeline.grasp_keyframe_core import GraspKeyframeStage
from macrobot_pick_pipeline.grasp_keyframe_store import GraspKeyframeStore


def test_first_localized_stage_sets_orientation_after_open(tmp_path: Path):
    store = GraspKeyframeStore(tmp_path / "profiles.yaml")
    open_stage = GraspKeyframeStage("OPEN", "gripper_only", (0.0, 0.0, 0.0), gripper_q=0.0)
    store.upsert_stage(profile_name="Eraser", object_name="Eraser", stage=open_stage)
    pre = GraspKeyframeStage(
        "PRE_GRASP", "object_relative_cartesian", (0.1, 0.0, 0.0),
        object_offset=(0.0, 0.0, 0.03), seed_q=(0.1, 0.0, 0.0), gripper_q=0.0,
    )
    profile = store.upsert_stage(
        profile_name="Eraser", object_name="Eraser", stage=pre,
        orientation_deg=7.0, orientation_class="horizontal", orientation_quality=0.8,
    )
    assert profile.reference_orientation_class == "horizontal"
    assert profile.reference_orientation_quality == 0.8
