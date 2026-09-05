from macrobot_pick_pipeline.runtime_epoch import RuntimeEpoch, epoch_compatibility


def test_host_restart_invalidates_odom_memory():
    recorded = RuntimeEpoch("boot-a", "pico-a", 50_000)
    current = RuntimeEpoch("boot-b", "pico-a", 60_000)
    assert epoch_compatibility(recorded, current) == (False, "host_restarted")


def test_pico_uptime_regression_invalidates_same_host_memory():
    recorded = RuntimeEpoch("boot-a", "", 50_000)
    current = RuntimeEpoch("boot-a", "", 100)
    assert epoch_compatibility(recorded, current, pico_time_tolerance_ms=1000) == (
        False,
        "pico_uptime_regressed",
    )


def test_same_epoch_accepts_location_hint():
    recorded = RuntimeEpoch("boot-a", "pico-a", 50_000)
    current = RuntimeEpoch("boot-a", "pico-a", 60_000)
    compatible, reason = epoch_compatibility(recorded, current)
    assert compatible
    assert reason == "same_host_and_pico_boot"
