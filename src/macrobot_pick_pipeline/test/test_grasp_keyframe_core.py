import numpy as np

from macrobot_arm_kinematics.model import MacRobotArmModel
from macrobot_pick_pipeline.grasp_keyframe_core import (
    GraspKeyframeProfile,
    SafeRegionLookup,
    build_semantic_grasp_plan,
    build_semantic_place_plan,
    capture_stage,
)


def test_semantic_keyframes_recompute_ik_for_shifted_object():
    model = MacRobotArmModel()
    reference_q = (0.0, 0.0, 0.0)
    pose = model.forward(*reference_q)
    object_point = (pose.x, pose.y, pose.z)
    stages = {
        "OPEN": capture_stage(stage_name="OPEN", current_q=reference_q, object_point_base=None, model=model),
        "PRE_GRASP": capture_stage(stage_name="PRE_GRASP", current_q=reference_q, object_point_base=object_point, model=model),
        "GRASP_OPEN": capture_stage(stage_name="GRASP_OPEN", current_q=reference_q, object_point_base=object_point, model=model),
        "CLOSE": capture_stage(stage_name="CLOSE", current_q=(0.0, 0.0, 0.5), object_point_base=None, model=model),
        "LIFT": capture_stage(stage_name="LIFT", current_q=reference_q, object_point_base=object_point, model=model),
    }
    profile = GraspKeyframeProfile("Eraser", "Eraser", stages)
    plan = build_semantic_grasp_plan(model, profile, object_point, reference_q)
    assert [step.name for step in plan.steps] == ["OPEN", "PRE_GRASP", "GRASP_OPEN", "CLOSE", "LIFT"]
    assert plan.steps[3].q[2] == 0.5


def test_safe_region_preflight_checks_interpolation():
    samples = np.array([[x, 0.0, 0.0] for x in np.linspace(0.0, 0.4, 21)])
    lookup = SafeRegionLookup(samples, max_distance_rad=0.03)
    ok, point, distance = lookup.validate_path((0.0, 0.0, 0.0), (0.4, 0.0, 0.0))
    assert ok
    assert point is None
    assert distance == 0.0


def test_semantic_plan_rejects_lateral_misalignment():
    model = MacRobotArmModel()
    q = (0.0, 0.0, 0.0)
    pose = model.forward(*q)
    reference = (pose.x, pose.y, pose.z)
    stages = {
        "OPEN": capture_stage(stage_name="OPEN", current_q=q, object_point_base=None, model=model),
        "PRE_GRASP": capture_stage(stage_name="PRE_GRASP", current_q=q, object_point_base=reference, model=model),
        "GRASP_OPEN": capture_stage(stage_name="GRASP_OPEN", current_q=q, object_point_base=reference, model=model),
        "CLOSE": capture_stage(stage_name="CLOSE", current_q=(0.0, 0.0, 0.5), object_point_base=None, model=model),
        "LIFT": capture_stage(stage_name="LIFT", current_q=q, object_point_base=reference, model=model),
    }
    profile = GraspKeyframeProfile("Eraser", "Eraser", stages)
    shifted = (reference[0], reference[1] + 0.05, reference[2])
    import pytest
    with pytest.raises(ValueError, match="lateral_alignment_failed"):
        build_semantic_grasp_plan(model, profile, shifted, q, lateral_tolerance_m=0.02)


def test_place_plan_is_cartesian_reverse_of_pick_semantics():
    model = MacRobotArmModel()
    q_open = (0.0, 0.0, 0.0)
    q_closed = (0.0, 0.0, 0.5)
    pose = model.forward(*q_open)
    point = (pose.x, pose.y, pose.z)
    stages = {
        "OPEN": capture_stage(stage_name="OPEN", current_q=q_open, object_point_base=None, model=model),
        "PRE_GRASP": capture_stage(stage_name="PRE_GRASP", current_q=q_open, object_point_base=point, model=model),
        "GRASP_OPEN": capture_stage(stage_name="GRASP_OPEN", current_q=q_open, object_point_base=point, model=model),
        "CLOSE": capture_stage(stage_name="CLOSE", current_q=q_closed, object_point_base=None, model=model),
        "LIFT": capture_stage(stage_name="LIFT", current_q=q_open, object_point_base=point, model=model),
    }
    profile = GraspKeyframeProfile("Eraser", "Eraser", stages)
    plan = build_semantic_place_plan(model, profile, point, q_closed)
    assert plan.operation == "place"
    assert [step.name for step in plan.steps] == [
        "PLACE_ABOVE",
        "PLACE_DESCEND",
        "PLACE_RELEASE",
        "PLACE_RETREAT",
    ]
    assert plan.steps[0].q[2] == 0.5
    assert plan.steps[1].q[2] == 0.5
    assert plan.steps[2].q[2] == 0.0
    assert plan.steps[3].q[2] == 0.0
