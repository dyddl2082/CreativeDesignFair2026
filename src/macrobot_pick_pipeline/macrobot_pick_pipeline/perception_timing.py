"""Progress-aware perception timing helpers for stored-object search.

The helpers are ROS-independent so timeout behavior can be unit-tested without a
running graph.  The tracker distinguishes three concepts:

* pipeline progress: candidate/embedding/temporal messages are still flowing;
* target evidence: a crop passed the target gate or a temporal track exists;
* identity confirmation: object_finder emitted ``object_found``.

A large action hard timeout is still allowed, but the camera/search phase can
fail early when the pipeline is stalled and can stop consuming its search
budget once identity has been confirmed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


_COUNTER_PATHS = {
    "embedding_processed": ("embedding", "processed"),
    "embedding_accepted": ("embedding", "accepted"),
    "temporal_messages": ("temporal", "received_messages"),
    "temporal_heartbeats": ("temporal", "received_heartbeats"),
    "temporal_active_tracks": ("temporal", "active_tracks"),
    "temporal_confirmed_tracks": ("temporal", "confirmed_tracks"),
    "temporal_confirmation_events": ("temporal", "confirmation_events"),
}

_PIPELINE_COUNTERS = {
    "embedding_processed",
    "temporal_messages",
    "temporal_heartbeats",
}

_EVIDENCE_COUNTERS = {
    "embedding_accepted",
    "temporal_active_tracks",
    "temporal_confirmed_tracks",
    "temporal_confirmation_events",
}


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _counter(value: Any) -> int:
    try:
        return max(0, int(value or 0))
    except (TypeError, ValueError):
        return 0


def extract_component_counters(finder_status: Mapping[str, Any]) -> dict[str, int]:
    """Extract monotonic component counters from object_finder status JSON."""

    health = _mapping(finder_status.get("health"))
    components = _mapping(health.get("components"))
    result: dict[str, int] = {}
    for name, (component_name, field_name) in _COUNTER_PATHS.items():
        component = _mapping(components.get(component_name))
        result[name] = _counter(component.get(field_name))
    return result


@dataclass
class ProgressObservation:
    pipeline_progress: bool = False
    evidence_progress: bool = False
    counters: dict[str, int] = field(default_factory=dict)


@dataclass
class PerceptionTimingTracker:
    """Track phase timestamps and progress counters for one finder request."""

    started_at: float = 0.0
    timestamps: dict[str, float] = field(default_factory=dict)
    counters: dict[str, int] = field(default_factory=dict)
    last_pipeline_progress_at: float = 0.0
    last_evidence_progress_at: float = 0.0
    last_localized_progress_at: float = 0.0
    scan_turn_count: int = 0
    scan_view_count: int = 0

    def reset(self, now: float) -> None:
        self.started_at = float(now)
        self.timestamps = {"finder_goal_started": float(now)}
        self.counters = {}
        self.last_pipeline_progress_at = float(now)
        self.last_evidence_progress_at = 0.0
        self.last_localized_progress_at = 0.0
        self.scan_turn_count = 0
        self.scan_view_count = 0

    def mark(self, name: str, now: float) -> bool:
        """Record the first occurrence of a timestamp; return True if new."""

        if name in self.timestamps:
            return False
        self.timestamps[str(name)] = float(now)
        return True

    def baseline(self, finder_status: Mapping[str, Any]) -> None:
        self.counters = extract_component_counters(finder_status)

    def observe_status(
        self,
        finder_status: Mapping[str, Any],
        now: float,
    ) -> ProgressObservation:
        current = extract_component_counters(finder_status)
        if not self.counters:
            self.counters = current
            return ProgressObservation(counters=current)

        pipeline = any(
            current.get(name, 0) > self.counters.get(name, 0)
            for name in _PIPELINE_COUNTERS
        )
        evidence = any(
            current.get(name, 0) > self.counters.get(name, 0)
            for name in _EVIDENCE_COUNTERS
        )

        # Counters can reset when the target changes.  Store the current values
        # instead of taking maxima so the next increment is observed correctly.
        self.counters = current
        if pipeline:
            self.last_pipeline_progress_at = float(now)
            self.mark("first_pipeline_progress", now)
        if evidence:
            self.last_evidence_progress_at = float(now)
            self.mark("first_target_evidence", now)
        return ProgressObservation(
            pipeline_progress=pipeline,
            evidence_progress=evidence,
            counters=current,
        )

    def mark_localized(self, now: float) -> None:
        self.last_localized_progress_at = float(now)
        self.mark("first_localized_object", now)

    def relative_times(self) -> dict[str, float]:
        if self.started_at <= 0.0:
            return {}
        return {
            name: max(0.0, stamp - self.started_at)
            for name, stamp in sorted(self.timestamps.items())
        }

    def duration(self, start_name: str, end_name: str) -> float | None:
        start = self.timestamps.get(start_name)
        end = self.timestamps.get(end_name)
        if start is None or end is None:
            return None
        return max(0.0, end - start)

    def latency_payload(self) -> dict[str, Any]:
        return {
            "relative_sec": self.relative_times(),
            "target_ready_to_first_evidence_sec": self.duration(
                "finder_target_ready", "first_target_evidence"
            ),
            "target_ready_to_object_found_sec": self.duration(
                "finder_target_ready", "identity_confirmed"
            ),
            "object_found_to_first_localized_sec": self.duration(
                "identity_confirmed", "first_localized_object"
            ),
            "first_localized_to_stable_sec": self.duration(
                "first_localized_object", "stable_object_acquired"
            ),
            "target_ready_to_stable_sec": self.duration(
                "finder_target_ready", "stable_object_acquired"
            ),
            "scan_turn_count": self.scan_turn_count,
            "scan_view_count": self.scan_view_count,
            "last_counters": dict(self.counters),
        }


def effective_observation_wait(
    profile_dwell_sec: float,
    configured_wait_sec: float,
) -> float:
    """Use at least the configured post-turn wait without shortening profiles."""

    return max(0.0, float(profile_dwell_sec), float(configured_wait_sec))
