import math

from macrobot_arm_commissioning.grasp_frame_fit import (
    GeometryReference,
    fit_grasp_frame,
)


def test_fit_grasp_frame_synthetic():
    reference = GeometryReference(0.02, 0.06, 0.1)
    a = -0.18
    z = -0.006
    length = 0.03
    samples = []
    for q3 in (0.0, -0.6, -1.1):
        samples.append(
            {
                "q1": 0.0,
                "q2": 0.0,
                "q3": q3,
                "measurement_frame": "wrist",
                "measured_x": a - length * math.sin(q3),
                "measured_z": z,
            }
        )
    result = fit_grasp_frame(samples, reference)
    assert abs(result["tool_offset_x"] - a) < 1e-10
    assert abs(result["tool_offset_z"] - z) < 1e-10
    assert abs(result["gripper_link_length"] - length) < 1e-10
