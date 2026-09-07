from __future__ import annotations

from pathlib import Path

from macrobot_pick_pipeline.grasp_keyframe_core import GraspKeyframeStage
from macrobot_pick_pipeline.grasp_keyframe_store import GraspKeyframeStore


def test_keyframe_store_round_trips_3d_orientation_metadata(tmp_path: Path):
    path = tmp_path / "profiles.yaml"
    store = GraspKeyframeStore(path)
    stage = GraspKeyframeStage(
        name="OPEN",
        representation="gripper_only",
        q=(0.1, 0.2, 0.0),
        gripper_q=0.0,
    )
    store.upsert_stage(
        profile_name="Eraser_r4",
        object_name="Eraser",
        stage=stage,
        orientation_deg=24.0,
        orientation_class="diagonal",
        orientation_quality=0.8,
        orientation_source="depth_axis_3d",
        orientation_frame="base_link",
        orientation_semantics="axial_yaw",
        orientation_axis_base=(0.9, 0.4, 0.05),
    )

    loaded = GraspKeyframeStore(path).get("Eraser_r4")
    assert loaded.reference_orientation_source == "depth_axis_3d"
    assert loaded.reference_orientation_frame == "base_link"
    assert loaded.reference_orientation_semantics == "axial_yaw"
    assert loaded.reference_orientation_axis_base is not None
