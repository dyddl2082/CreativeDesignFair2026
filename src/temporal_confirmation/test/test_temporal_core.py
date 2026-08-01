from temporal_confirmation.temporal_core import (
    BoundingBox,
    Observation,
    TemporalConfig,
    TemporalTracker,
    bbox_iou,
)


def observation(
    frame_index: int,
    *,
    x: float = 100.0,
    y: float = 100.0,
    hit: bool = True,
    depth: float = 0.5,
    margin: float = 0.15,
) -> Observation:
    box = BoundingBox(x=x, y=y, width=80.0, height=60.0)
    return Observation(
        frame_index=frame_index,
        stamp_ns=frame_index * 1_000_000,
        target_object="Buds3",
        candidate_id=frame_index,
        crop_index=0,
        bbox=box,
        center_x=box.center_x,
        center_y=box.center_y,
        depth_m=depth,
        hit=hit,
        positive_similarity=0.80 if hit else 0.60,
        negative_similarity=0.60 if hit else 0.63,
        margin=margin if hit else -0.03,
        objectness_score=0.8,
        payload={"frame": frame_index},
    )


def test_bbox_iou() -> None:
    first = BoundingBox(0, 0, 10, 10)
    second = BoundingBox(5, 0, 10, 10)
    assert abs(bbox_iou(first, second) - (50.0 / 150.0)) < 1.0e-6


def test_confirms_after_three_of_five_with_two_consecutive_hits() -> None:
    tracker = TemporalTracker(
        TemporalConfig(
            window_size=5,
            required_hits=3,
            min_consecutive_hits=2,
            require_stability_for_confirm=True,
        )
    )
    events = []
    hits = [True, False, True, True]
    for index, hit in enumerate(hits, start=1):
        events = tracker.process_frame(
            frame_index=index,
            observations=[observation(index, x=100 + index, hit=hit)],
            now_sec=float(index),
        )
    assert tracker.confirmed_track_count == 1
    assert any(event.event == "confirmed" for event in events)
    confirmed = tracker.best_confirmed(frame_index=4)
    assert confirmed is not None
    assert confirmed.hits_in_window == 3
    assert confirmed.consecutive_hits == 2


def test_does_not_merge_distant_candidates() -> None:
    tracker = TemporalTracker(
        TemporalConfig(
            association_max_center_distance_px=50.0,
            association_min_iou=0.05,
            required_hits=2,
            min_consecutive_hits=2,
            require_stability_for_confirm=False,
        )
    )
    tracker.process_frame(
        frame_index=1,
        observations=[observation(1, x=50.0)],
        now_sec=1.0,
    )
    tracker.process_frame(
        frame_index=2,
        observations=[observation(2, x=400.0)],
        now_sec=2.0,
    )
    assert tracker.active_track_count == 2
    assert tracker.confirmed_track_count == 0


def test_confirmed_track_deconfirms_after_misses() -> None:
    tracker = TemporalTracker(
        TemporalConfig(
            window_size=5,
            required_hits=2,
            min_consecutive_hits=2,
            deconfirm_after_misses=2,
            retire_after_misses=4,
            require_stability_for_confirm=False,
        )
    )
    tracker.process_frame(
        frame_index=1,
        observations=[observation(1)],
        now_sec=1.0,
    )
    tracker.process_frame(
        frame_index=2,
        observations=[observation(2)],
        now_sec=2.0,
    )
    assert tracker.confirmed_track_count == 1
    tracker.process_frame(frame_index=3, observations=[], now_sec=3.0)
    events = tracker.process_frame(frame_index=4, observations=[], now_sec=4.0)
    assert tracker.confirmed_track_count == 0
    assert any(event.event == "deconfirmed" for event in events)


def test_track_expires_after_timeout() -> None:
    tracker = TemporalTracker(
        TemporalConfig(
            track_timeout_sec=1.0,
            required_hits=1,
            min_consecutive_hits=1,
            require_stability_for_confirm=False,
        )
    )
    tracker.process_frame(
        frame_index=1,
        observations=[observation(1)],
        now_sec=1.0,
    )
    events = tracker.expire_stale(now_sec=2.1, frame_index=2)
    assert tracker.active_track_count == 0
    assert len(events) == 1
    assert events[0].event == "expired"
    assert events[0].state == "lost"


def test_non_hit_does_not_create_track_by_default() -> None:
    tracker = TemporalTracker(TemporalConfig())
    tracker.process_frame(
        frame_index=1,
        observations=[observation(1, hit=False)],
        now_sec=1.0,
    )
    assert tracker.active_track_count == 0


def test_empty_frames_count_as_misses() -> None:
    tracker = TemporalTracker(
        TemporalConfig(
            window_size=5,
            required_hits=3,
            min_consecutive_hits=2,
            deconfirm_after_misses=2,
            retire_after_misses=5,
            require_stability_for_confirm=False,
        )
    )
    tracker.process_frame(
        frame_index=1,
        observations=[observation(1)],
        now_sec=1.0,
    )
    tracker.process_frame(frame_index=2, observations=[], now_sec=2.0)
    tracker.process_frame(
        frame_index=3,
        observations=[observation(3)],
        now_sec=3.0,
    )
    tracker.process_frame(frame_index=4, observations=[], now_sec=4.0)
    tracker.process_frame(
        frame_index=5,
        observations=[observation(5)],
        now_sec=5.0,
    )
    # There are three hits in five frames, but never two consecutive hits.
    assert tracker.confirmed_track_count == 0


def test_frame_local_candidate_id_is_not_used_for_association() -> None:
    tracker = TemporalTracker(
        TemporalConfig(
            required_hits=2,
            min_consecutive_hits=2,
            require_stability_for_confirm=False,
        )
    )
    first = observation(1)
    second = Observation(
        **{
            **first.__dict__,
            "frame_index": 2,
            "stamp_ns": 2_000_000,
            "candidate_id": 999,
            "bbox": BoundingBox(103.0, 101.0, 80.0, 60.0),
            "center_x": 143.0,
            "center_y": 131.0,
            "payload": {"frame": 2},
        }
    )
    tracker.process_frame(frame_index=1, observations=[first], now_sec=1.0)
    tracker.process_frame(frame_index=2, observations=[second], now_sec=2.0)
    assert tracker.active_track_count == 1
    assert tracker.confirmed_track_count == 1
