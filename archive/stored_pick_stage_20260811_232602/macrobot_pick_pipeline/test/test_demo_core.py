from macrobot_pick_pipeline.demo_core import (
    DemoRecording,
    TrajectorySampler,
    Waypoint,
    playback_keyframes,
    safe_name,
)


def test_sampler_records_change_and_final_state():
    sampler = TrajectorySampler(
        min_joint_delta_rad=0.01,
        max_sample_interval_sec=1.0,
        max_duration_sec=10.0,
    )
    sampler.start(100.0, (0.0, 0.0, 0.0))
    assert not sampler.add(100.1, (0.001, 0.0, 0.0))
    assert sampler.add(100.2, (0.02, 0.0, 0.0))
    waypoints, marks = sampler.finish(100.3, (0.03, 0.0, 0.0))
    assert len(waypoints) == 3
    assert waypoints[-1].q == (0.03, 0.0, 0.0)
    assert marks == []


def test_sampler_pause_excludes_paused_time():
    sampler = TrajectorySampler()
    sampler.start(10.0, (0.0, 0.0, 0.0))
    sampler.pause(11.0)
    sampler.resume(21.0)
    assert 0.99 <= sampler.elapsed(21.0) <= 1.01


def test_playback_keyframes_keeps_endpoints():
    raw = [
        Waypoint(0.0, (0.0, 0.0, 0.0)),
        Waypoint(0.1, (0.001, 0.0, 0.0)),
        Waypoint(0.2, (0.020, 0.0, 0.0)),
        Waypoint(0.3, (0.021, 0.0, 0.0)),
    ]
    result = playback_keyframes(raw, min_joint_delta_rad=0.01)
    assert result[0] == raw[0]
    assert result[-1] == raw[-1]
    assert len(result) == 3


def test_recording_round_trip():
    recording = DemoRecording(
        name="PICK_DEMO",
        kind="trajectory",
        recorded_at="now",
        waypoints=[
            Waypoint(0.0, (0.0, 0.0, 0.0)),
            Waypoint(1.0, (0.1, 0.2, 0.3)),
        ],
    )
    loaded = DemoRecording.from_mapping(recording.as_dict())
    assert loaded.name == "PICK_DEMO"
    assert loaded.final_q == (0.1, 0.2, 0.3)


def test_safe_name():
    assert safe_name("My demo 1") == "My_demo_1"
