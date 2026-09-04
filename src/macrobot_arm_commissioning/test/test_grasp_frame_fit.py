import math

from macrobot_arm_commissioning.grasp_frame_fit import fit_grasp_frame
from macrobot_arm_kinematics.model import MacRobotArmModel


def _base_point(model, q1, q2, local):
    position, rotation = model.gripper_link_transform(q1, q2)
    rotated = tuple(
        sum(rotation[row][column] * local[column] for column in range(3))
        for row in range(3)
    )
    return tuple(position[index] + rotated[index] for index in range(3))


def test_fixed_grasp_frame_fit_recovers_urdf_offset():
    model = MacRobotArmModel()
    truth = (0.013, 0.218151, -0.008098)
    samples = []
    for q1, q2, q3 in ((0.0, 0.0, 0.0), (0.20, -0.10, 0.6), (-0.18, 0.16, 1.2)):
        point = _base_point(model, q1, q2, truth)
        samples.append({
            "q1": q1,
            "q2": q2,
            "q3": q3,
            "measurement_frame": "base_link",
            "measured_x": point[0],
            "measured_y": point[1],
            "measured_z": point[2],
        })
    result = fit_grasp_frame(samples, model=model)
    assert math.dist(result["grasp_origin_xyz"], truth) < 1e-10
    assert result["max_error_m"] < 1e-10


def test_grasp_center_is_independent_of_q3():
    model = MacRobotArmModel()
    first = model.forward(0.15, -0.10, 0.0)
    second = model.forward(0.15, -0.10, model.limits.gripper_max)
    assert (first.x, first.y, first.z) == (second.x, second.y, second.z)
