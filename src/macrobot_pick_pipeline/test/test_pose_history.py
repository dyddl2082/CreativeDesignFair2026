import pytest

from macrobot_pick_pipeline.pose_history import PoseHistory
from macrobot_pick_pipeline.stored_object_core import OdomPose


def test_delayed_detection_is_compensated_after_forward_motion():
    history = PoseHistory(nearest_tolerance_sec=0.2)
    start = OdomPose(0.0, 0.0, 0.0, True, 1000)
    end = OdomPose(0.10, 0.0, 0.0, True, 2000)
    history.begin_motion("move", 10.0, start, 0.10)
    history.complete_motion(12.0, end)

    # With MacRobot's configured forward axis sign +1, an object at x=0.50 m
    # at capture time should be 0.40 m away after the chassis moves 0.10 m.
    compensated = history.compensate_point(
        (0.50, 0.0, 0.0),
        capture_wall_sec=10.0,
        current_pose=end,
        forward_axis_sign=1.0,
        lateral_axis_sign=1.0,
    )
    assert compensated is not None
    assert compensated[0] == pytest.approx(0.40, abs=1e-6)
    assert compensated[1] == pytest.approx(0.0, abs=1e-6)


def test_pose_history_interpolates_motion_timestamp():
    history = PoseHistory()
    history.begin_motion("turn", 10.0, OdomPose(0.0, 0.0, 0.0), 20.0)
    history.complete_motion(12.0, OdomPose(0.0, 0.0, 20.0))
    pose = history.pose_at(11.0)
    assert pose is not None
    assert pose.yaw_deg == pytest.approx(10.0)
