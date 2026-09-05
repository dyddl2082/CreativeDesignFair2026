from macrobot_pick_pipeline.object_memory import (
    ObjectMemoryStore,
    ObjectObservationMemory,
)
from macrobot_pick_pipeline.runtime_epoch import RuntimeEpoch
from macrobot_pick_pipeline.stored_object_core import OdomPose


def test_location_hint_is_stale_after_restart_but_file_survives(tmp_path):
    path = tmp_path / "memory.yaml"
    store = ObjectMemoryStore(path)
    epoch = RuntimeEpoch("boot-a", "pico-a", 1000)
    store.remember(
        ObjectObservationMemory(
            object_name="Buds3",
            object_point_odom=(1.0, 2.0, 0.1),
            observer_pose_odom=OdomPose(0.0, 0.0, 0.0, True, 1000),
            source_stamp_sec=100.0,
            recorded_at="2026-09-01T00:00:00Z",
            epoch=epoch,
            score=0.8,
            localization_quality=0.9,
            confidence=0.85,
        )
    )
    reloaded = ObjectMemoryStore(path)
    state, reason, record = reloaded.classify(
        "Buds3",
        RuntimeEpoch("boot-b", "pico-b", 10),
        current_wall_sec=101.0,
    )
    assert state == "stale"
    assert reason == "host_restarted"
    assert record is not None
    assert record.object_name == "Buds3"


def test_holding_becomes_unknown_after_restart(tmp_path):
    store = ObjectMemoryStore(tmp_path / "memory.yaml")
    store.set_holding(
        "Eraser",
        "eraser_grasp",
        RuntimeEpoch("boot-a", "pico-a", 5000),
    )
    held = store.held_for_epoch(RuntimeEpoch("boot-b", "pico-b", 10))
    assert held.state == "unknown"
    assert held.object_name == "Eraser"
    assert held.grasp_profile == "eraser_grasp"
