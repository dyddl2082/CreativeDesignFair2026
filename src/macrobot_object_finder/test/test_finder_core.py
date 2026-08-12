from types import SimpleNamespace

import pytest

from macrobot_object_finder.finder_core import (
    FinderSession,
    parse_goal_text,
    temporal_message_is_usable,
    temporal_to_result_payload,
)


def message(**overrides):
    data = dict(
        confirmed=True,
        target_object="Buds3",
        state="confirmed",
        event="confirmed",
        center_x=321.0,
        center_y=239.0,
        depth_m=0.42,
        temporal_score=0.82,
        stability_score=0.9,
        track_id=7,
        center_std_px=2.0,
        depth_std_m=0.01,
        localization_method="dinov2_patch_margin",
        localization_quality=0.91,
        orientation_deg=8.0,
        orientation_class="horizontal",
        orientation_quality=0.84,
        mean_positive_similarity=0.76,
        mean_negative_similarity=0.55,
        mean_margin=0.21,
        header=SimpleNamespace(
            frame_id="camera_color_optical_frame",
            stamp=SimpleNamespace(sec=10, nanosec=500_000_000),
        ),
        roi=SimpleNamespace(x_offset=10, y_offset=20, width=30, height=40),
    )
    data.update(overrides)
    return SimpleNamespace(**data)


def test_parse_plain_goal():
    goal = parse_goal_text("Buds3")
    assert goal.object_name == "Buds3"
    assert goal.continuous is True
    assert goal.request_id


def test_parse_json_goal():
    goal = parse_goal_text(
        '{"object_name":"Cup","timeout_sec":12,"continuous":false,"min_score":0.6}'
    )
    assert goal.object_name == "Cup"
    assert goal.timeout_sec == 12
    assert goal.continuous is False
    assert goal.min_score == 0.6


def test_unsafe_target_rejected():
    with pytest.raises(ValueError):
        parse_goal_text("../Buds3")


def test_temporal_result_contract():
    goal = parse_goal_text('{"object_name":"Buds3","min_score":0.5}')
    msg = message()
    assert temporal_message_is_usable(
        msg, goal, minimum_depth_m=0.08, maximum_depth_m=2.0
    )
    result = temporal_to_result_payload(
        msg, goal, default_frame_id="fallback"
    )
    assert result["found"] is True
    assert result["center_px"] == {"x": 321.0, "y": 239.0}
    assert result["depth_m"] == 0.42
    assert result["bbox"]["width"] == 30


def test_wrong_target_rejected():
    goal = parse_goal_text("Buds3")
    assert not temporal_message_is_usable(
        message(target_object="Cup"),
        goal,
        minimum_depth_m=0.08,
        maximum_depth_m=2.0,
    )


def test_session_timeout_and_found():
    goal = parse_goal_text('{"object_name":"Buds3","timeout_sec":2,"continuous":true}')
    session = FinderSession()
    session.start(goal, 10.0)
    assert not session.timeout_due(11.9)
    assert session.timeout_due(12.0)
    session.accept_found(4, 11.0)
    assert session.state == "TRACKING"
    assert session.track_id == 4
