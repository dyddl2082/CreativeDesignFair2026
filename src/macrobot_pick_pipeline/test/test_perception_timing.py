from macrobot_pick_pipeline.perception_timing import (
    PerceptionTimingTracker,
    effective_observation_wait,
    extract_component_counters,
)


def status(*, processed=0, accepted=0, messages=0, heartbeats=0, active=0, confirmed=0, confirmations=0):
    return {
        "health": {
            "components": {
                "embedding": {
                    "processed": processed,
                    "accepted": accepted,
                },
                "temporal": {
                    "received_messages": messages,
                    "received_heartbeats": heartbeats,
                    "active_tracks": active,
                    "confirmed_tracks": confirmed,
                    "confirmation_events": confirmations,
                },
            }
        }
    }


def test_extract_component_counters():
    values = extract_component_counters(
        status(processed=4, accepted=2, messages=3, heartbeats=8, active=1, confirmed=1, confirmations=1)
    )
    assert values["embedding_processed"] == 4
    assert values["embedding_accepted"] == 2
    assert values["temporal_messages"] == 3
    assert values["temporal_heartbeats"] == 8
    assert values["temporal_active_tracks"] == 1
    assert values["temporal_confirmed_tracks"] == 1


def test_progress_distinguishes_pipeline_and_target_evidence():
    tracker = PerceptionTimingTracker()
    tracker.reset(10.0)
    tracker.baseline(status(processed=5, accepted=1, messages=5, heartbeats=10))

    pipeline = tracker.observe_status(
        status(processed=6, accepted=1, messages=6, heartbeats=11),
        11.0,
    )
    assert pipeline.pipeline_progress
    assert not pipeline.evidence_progress
    assert tracker.last_pipeline_progress_at == 11.0

    evidence = tracker.observe_status(
        status(processed=7, accepted=2, messages=7, heartbeats=12, active=1),
        12.0,
    )
    assert evidence.pipeline_progress
    assert evidence.evidence_progress
    assert tracker.last_evidence_progress_at == 12.0
    assert tracker.timestamps["first_target_evidence"] == 12.0


def test_counter_reset_is_not_false_progress():
    tracker = PerceptionTimingTracker()
    tracker.reset(1.0)
    tracker.baseline(status(processed=100, accepted=20, messages=80, active=2))
    reset = tracker.observe_status(status(processed=0, accepted=0, messages=0, active=0), 2.0)
    assert not reset.pipeline_progress
    assert not reset.evidence_progress
    after_reset = tracker.observe_status(status(processed=1, accepted=0, messages=1), 3.0)
    assert after_reset.pipeline_progress


def test_latency_payload_uses_first_occurrence():
    tracker = PerceptionTimingTracker()
    tracker.reset(100.0)
    tracker.mark("finder_target_ready", 102.0)
    tracker.mark("first_target_evidence", 103.5)
    tracker.mark("identity_confirmed", 105.0)
    tracker.mark_localized(106.0)
    tracker.mark("stable_object_acquired", 108.0)
    tracker.mark("stable_object_acquired", 120.0)

    payload = tracker.latency_payload()
    assert payload["target_ready_to_first_evidence_sec"] == 1.5
    assert payload["target_ready_to_object_found_sec"] == 3.0
    assert payload["object_found_to_first_localized_sec"] == 1.0
    assert payload["first_localized_to_stable_sec"] == 2.0
    assert payload["relative_sec"]["stable_object_acquired"] == 8.0


def test_effective_observation_wait_never_shortens_profile():
    assert effective_observation_wait(1.2, 3.0) == 3.0
    assert effective_observation_wait(4.0, 3.0) == 4.0
    assert effective_observation_wait(-1.0, 2.0) == 2.0
