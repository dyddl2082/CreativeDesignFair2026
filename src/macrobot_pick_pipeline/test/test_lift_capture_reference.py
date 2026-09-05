import math

import pytest

from macrobot_arm_kinematics.model import MacRobotArmModel
from macrobot_pick_pipeline.grasp_keyframe_core import (
    GraspKeyframeProfile,
    GraspKeyframeStage,
    capture_stage,
    recover_lift_capture_reference,
)


def test_lift_reference_is_recovered_from_grasp_open_without_live_detection():
    model = MacRobotArmModel()
    q = (0.0, 0.0, 0.0)
    pose = model.forward(*q)
    object_point = (float(pose.x) - 0.015, float(pose.y), float(pose.z) - 0.010)

    pre = capture_stage(
        stage_name="PRE_GRASP",
        current_q=q,
        object_point_base=object_point,
        model=model,
    )
    grasp = capture_stage(
        stage_name="GRASP_OPEN",
        current_q=q,
        object_point_base=object_point,
        model=model,
    )
    draft = GraspKeyframeProfile(
        name="Eraser_r4",
        object_name="Eraser",
        stages={"PRE_GRASP": pre, "GRASP_OPEN": grasp},
    )

    recovered, source = recover_lift_capture_reference(model, draft)

    assert source == "GRASP_OPEN"
    assert all(math.isclose(a, b, abs_tol=1e-9) for a, b in zip(recovered, object_point))


def test_lift_reference_rejects_inconsistent_recorded_object_points():
    model = MacRobotArmModel()
    q = (0.0, 0.0, 0.0)
    pose = model.forward(*q)
    object_point = (float(pose.x), float(pose.y), float(pose.z))

    pre = capture_stage(
        stage_name="PRE_GRASP",
        current_q=q,
        object_point_base=object_point,
        model=model,
    )
    grasp = GraspKeyframeStage(
        name="GRASP_OPEN",
        representation="object_relative_cartesian",
        q=q,
        object_offset=(0.10, 0.0, 0.0),
        seed_q=q,
        gripper_q=q[2],
    )
    draft = GraspKeyframeProfile(
        name="Eraser_r4",
        object_name="Eraser",
        stages={"PRE_GRASP": pre, "GRASP_OPEN": grasp},
    )

    with pytest.raises(ValueError, match="lift_reference_inconsistent"):
        recover_lift_capture_reference(
            model,
            draft,
            consistency_tolerance_m=0.030,
        )
