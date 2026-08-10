"""Pure temporal tracking and K-of-N confirmation logic for MacRobot.

The module intentionally has no ROS imports so it can be unit-tested without a
ROS installation.  A spatial track receives at most one evidence item per
finalized proposal frame.  A matched embedding result can be a hit or a miss;
an unmatched active track receives a miss for that frame.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from collections import deque
import math
import statistics
from typing import Any, Deque, Iterable, Optional, Sequence


_EPSILON = 1.0e-9


@dataclass(frozen=True)
class BoundingBox:
    """Axis-aligned image bounding box in pixels."""

    x: float
    y: float
    width: float
    height: float

    @property
    def x2(self) -> float:
        return self.x + max(self.width, 0.0)

    @property
    def y2(self) -> float:
        return self.y + max(self.height, 0.0)

    @property
    def area(self) -> float:
        return max(self.width, 0.0) * max(self.height, 0.0)

    @property
    def center_x(self) -> float:
        return self.x + max(self.width, 0.0) * 0.5

    @property
    def center_y(self) -> float:
        return self.y + max(self.height, 0.0) * 0.5

    def valid(self) -> bool:
        return (
            math.isfinite(self.x)
            and math.isfinite(self.y)
            and math.isfinite(self.width)
            and math.isfinite(self.height)
            and self.width > 0.0
            and self.height > 0.0
        )


def bbox_iou(first: BoundingBox, second: BoundingBox) -> float:
    """Return intersection-over-union in ``[0, 1]``."""

    intersection_width = max(0.0, min(first.x2, second.x2) - max(first.x, second.x))
    intersection_height = max(0.0, min(first.y2, second.y2) - max(first.y, second.y))
    intersection = intersection_width * intersection_height
    union = first.area + second.area - intersection
    if union <= _EPSILON:
        return 0.0
    return float(max(0.0, min(1.0, intersection / union)))


def center_distance(first: BoundingBox, second: BoundingBox) -> float:
    return math.hypot(first.center_x - second.center_x, first.center_y - second.center_y)


def area_ratio(first: BoundingBox, second: BoundingBox) -> float:
    smaller = min(first.area, second.area)
    larger = max(first.area, second.area)
    if smaller <= _EPSILON:
        return math.inf
    return larger / smaller


@dataclass(frozen=True)
class TemporalConfig:
    """Configuration for spatial association and temporal confirmation."""

    window_size: int = 5
    required_hits: int = 3
    min_consecutive_hits: int = 2
    deconfirm_after_misses: int = 3
    retire_after_misses: int = 6
    track_timeout_sec: float = 2.0
    max_tracks: int = 12
    create_tracks_from_non_hits: bool = False

    association_min_iou: float = 0.05
    association_max_center_distance_px: float = 120.0
    association_max_depth_difference_m: float = 0.18
    association_max_area_ratio: float = 3.0
    association_center_weight: float = 0.45
    association_iou_weight: float = 0.30
    association_depth_weight: float = 0.15
    association_area_weight: float = 0.10

    require_stability_for_confirm: bool = True
    min_hit_observations_for_stability: int = 2
    max_center_std_px: float = 45.0
    max_depth_std_m: float = 0.12

    temporal_hit_weight: float = 0.55
    temporal_stability_weight: float = 0.25
    temporal_margin_weight: float = 0.20
    margin_reference_low: float = 0.05
    margin_reference_good: float = 0.20

    def validate(self) -> None:
        if self.window_size <= 0:
            raise ValueError("window_size must be positive")
        if self.required_hits <= 0 or self.required_hits > self.window_size:
            raise ValueError("required_hits must be in [1, window_size]")
        if self.min_consecutive_hits <= 0:
            raise ValueError("min_consecutive_hits must be positive")
        if self.deconfirm_after_misses <= 0:
            raise ValueError("deconfirm_after_misses must be positive")
        if self.retire_after_misses < self.deconfirm_after_misses:
            raise ValueError("retire_after_misses must be >= deconfirm_after_misses")
        if self.track_timeout_sec <= 0.0:
            raise ValueError("track_timeout_sec must be positive")
        if self.max_tracks <= 0:
            raise ValueError("max_tracks must be positive")
        if self.association_max_center_distance_px <= 0.0:
            raise ValueError("association_max_center_distance_px must be positive")
        if self.association_max_depth_difference_m <= 0.0:
            raise ValueError("association_max_depth_difference_m must be positive")
        if self.association_max_area_ratio < 1.0:
            raise ValueError("association_max_area_ratio must be >= 1")
        if self.max_center_std_px <= 0.0:
            raise ValueError("max_center_std_px must be positive")
        if self.max_depth_std_m <= 0.0:
            raise ValueError("max_depth_std_m must be positive")
        if self.margin_reference_good <= self.margin_reference_low:
            raise ValueError("margin_reference_good must exceed margin_reference_low")
        weight_sum = (
            self.temporal_hit_weight
            + self.temporal_stability_weight
            + self.temporal_margin_weight
        )
        if weight_sum <= 0.0:
            raise ValueError("temporal score weights must have a positive sum")


@dataclass(frozen=True)
class Observation:
    """One embedding-retrieval observation in a finalized proposal frame."""

    frame_index: int
    stamp_ns: int
    target_object: str
    candidate_id: int
    crop_index: int
    bbox: BoundingBox
    center_x: float
    center_y: float
    depth_m: Optional[float]
    hit: bool
    positive_similarity: Optional[float]
    negative_similarity: Optional[float]
    margin: Optional[float]
    objectness_score: Optional[float]
    payload: Any = None


@dataclass(frozen=True)
class Evidence:
    frame_index: int
    matched: bool
    hit: bool
    observation: Optional[Observation]


@dataclass(frozen=True)
class TrackSnapshot:
    """Immutable summary used by the ROS wrapper and tests."""

    track_id: int
    target_object: str
    frame_index: int
    state: str
    event: str
    confirmed: bool
    track_age_frames: int
    window_size: int
    required_hits: int
    samples_in_window: int
    matched_frames_in_window: int
    hits_in_window: int
    misses_in_window: int
    consecutive_hits: int
    consecutive_misses: int
    hit_ratio: float
    temporal_score: float
    stability_score: float
    mean_positive_similarity: Optional[float]
    mean_negative_similarity: Optional[float]
    mean_margin: Optional[float]
    min_margin_in_window: Optional[float]
    mean_objectness_score: Optional[float]
    bbox: BoundingBox
    center_x: float
    center_y: float
    depth_m: Optional[float]
    center_std_px: float
    depth_std_m: float
    last_seen_monotonic: float
    latest_observation: Observation


@dataclass
class _Track:
    track_id: int
    target_object: str
    created_frame_index: int
    history: Deque[Evidence]
    latest_observation: Observation
    last_seen_monotonic: float
    confirmed: bool = False
    consecutive_hits: int = 0
    consecutive_misses: int = 0
    track_age_frames: int = 0

    def append_observation(self, observation: Observation, now_sec: float) -> None:
        self.latest_observation = observation
        self.last_seen_monotonic = now_sec
        self.track_age_frames += 1
        self.history.append(
            Evidence(
                frame_index=observation.frame_index,
                matched=True,
                hit=observation.hit,
                observation=observation,
            )
        )
        if observation.hit:
            self.consecutive_hits += 1
            self.consecutive_misses = 0
        else:
            self.consecutive_hits = 0
            self.consecutive_misses += 1

    def append_miss(self, frame_index: int) -> None:
        self.track_age_frames += 1
        self.history.append(
            Evidence(
                frame_index=frame_index,
                matched=False,
                hit=False,
                observation=None,
            )
        )
        self.consecutive_hits = 0
        self.consecutive_misses += 1


class TemporalTracker:
    """Greedy multi-object tracker with K-of-N temporal confirmation."""

    def __init__(self, config: TemporalConfig) -> None:
        config.validate()
        self.config = config
        self._tracks: dict[int, _Track] = {}
        self._next_track_id = 1
        self.created_tracks = 0
        self.retired_tracks = 0
        self.confirmation_events = 0
        self.deconfirmation_events = 0
        self.expiration_events = 0

    @property
    def active_track_count(self) -> int:
        return len(self._tracks)

    @property
    def confirmed_track_count(self) -> int:
        return sum(1 for track in self._tracks.values() if track.confirmed)

    def reset(self, *, frame_index: int = 0, event: str = "expired") -> list[TrackSnapshot]:
        snapshots = [
            self._snapshot(track, frame_index=frame_index, event=event, force_state="lost")
            for track in self._tracks.values()
        ]
        self.retired_tracks += len(self._tracks)
        self.expiration_events += len(self._tracks)
        self._tracks.clear()
        return snapshots

    def _association_cost(self, track: _Track, observation: Observation) -> Optional[float]:
        if track.target_object != observation.target_object:
            return None

        previous = track.latest_observation
        iou = bbox_iou(previous.bbox, observation.bbox)
        distance = center_distance(previous.bbox, observation.bbox)
        if iou < self.config.association_min_iou and (
            distance > self.config.association_max_center_distance_px
        ):
            return None

        ratio = area_ratio(previous.bbox, observation.bbox)
        if ratio > self.config.association_max_area_ratio:
            return None

        depth_cost = 0.0
        if previous.depth_m is not None and observation.depth_m is not None:
            depth_difference = abs(previous.depth_m - observation.depth_m)
            if depth_difference > self.config.association_max_depth_difference_m:
                return None
            depth_cost = min(
                depth_difference / self.config.association_max_depth_difference_m,
                1.0,
            )

        center_cost = min(
            distance / self.config.association_max_center_distance_px,
            1.0,
        )
        iou_cost = 1.0 - iou
        if ratio <= 1.0:
            area_cost = 0.0
        else:
            area_cost = min(
                math.log(ratio) / math.log(self.config.association_max_area_ratio),
                1.0,
            )

        weighted = (
            self.config.association_center_weight * center_cost
            + self.config.association_iou_weight * iou_cost
            + self.config.association_depth_weight * depth_cost
            + self.config.association_area_weight * area_cost
        )
        weight_sum = (
            self.config.association_center_weight
            + self.config.association_iou_weight
            + self.config.association_depth_weight
            + self.config.association_area_weight
        )
        if weight_sum <= _EPSILON:
            return center_cost
        return weighted / weight_sum

    def process_frame(
        self,
        *,
        frame_index: int,
        observations: Sequence[Observation],
        now_sec: float,
    ) -> list[TrackSnapshot]:
        """Associate one finalized proposal frame and return track events/updates."""

        valid_observations = [
            observation
            for observation in observations
            if observation.bbox.valid() and observation.target_object
        ]

        pairs: list[tuple[float, int, int]] = []
        track_ids = list(self._tracks.keys())
        for track_id in track_ids:
            track = self._tracks[track_id]
            for observation_index, observation in enumerate(valid_observations):
                cost = self._association_cost(track, observation)
                if cost is not None:
                    pairs.append((cost, track_id, observation_index))
        pairs.sort(key=lambda item: item[0])

        assigned_tracks: set[int] = set()
        assigned_observations: set[int] = set()
        assignments: dict[int, int] = {}
        for _, track_id, observation_index in pairs:
            if track_id in assigned_tracks or observation_index in assigned_observations:
                continue
            assigned_tracks.add(track_id)
            assigned_observations.add(observation_index)
            assignments[track_id] = observation_index

        events: list[TrackSnapshot] = []
        for track_id in list(self._tracks.keys()):
            track = self._tracks[track_id]
            previous_confirmed = track.confirmed
            if track_id in assignments:
                track.append_observation(
                    valid_observations[assignments[track_id]],
                    now_sec,
                )
            else:
                track.append_miss(frame_index)

            transition_event = self._update_confirmation_state(track)
            if transition_event == "confirmed":
                self.confirmation_events += 1
            elif transition_event == "deconfirmed":
                self.deconfirmation_events += 1

            if track.consecutive_misses >= self.config.retire_after_misses:
                events.append(
                    self._snapshot(
                        track,
                        frame_index=frame_index,
                        event="expired",
                        force_state="lost",
                    )
                )
                del self._tracks[track_id]
                self.retired_tracks += 1
                self.expiration_events += 1
                continue

            event = transition_event or "update"
            if previous_confirmed and not track.confirmed and event == "update":
                event = "deconfirmed"
            events.append(self._snapshot(track, frame_index=frame_index, event=event))

        for observation_index, observation in enumerate(valid_observations):
            if observation_index in assigned_observations:
                continue
            if not observation.hit and not self.config.create_tracks_from_non_hits:
                continue
            track = _Track(
                track_id=self._next_track_id,
                target_object=observation.target_object,
                created_frame_index=frame_index,
                history=deque(maxlen=self.config.window_size),
                latest_observation=observation,
                last_seen_monotonic=now_sec,
            )
            self._next_track_id += 1
            self.created_tracks += 1
            track.append_observation(observation, now_sec)
            transition_event = self._update_confirmation_state(track)
            if transition_event == "confirmed":
                self.confirmation_events += 1
            self._tracks[track.track_id] = track
            events.append(
                self._snapshot(
                    track,
                    frame_index=frame_index,
                    event=transition_event or "update",
                )
            )

        events.extend(self._enforce_track_limit(frame_index))
        return sorted(events, key=lambda item: item.track_id)

    def expire_stale(self, *, now_sec: float, frame_index: int) -> list[TrackSnapshot]:
        events: list[TrackSnapshot] = []
        for track_id in list(self._tracks.keys()):
            track = self._tracks[track_id]
            if now_sec - track.last_seen_monotonic <= self.config.track_timeout_sec:
                continue
            events.append(
                self._snapshot(
                    track,
                    frame_index=frame_index,
                    event="expired",
                    force_state="lost",
                )
            )
            del self._tracks[track_id]
            self.retired_tracks += 1
            self.expiration_events += 1
        return events

    def snapshots(self, *, frame_index: int, event: str = "update") -> list[TrackSnapshot]:
        return [
            self._snapshot(track, frame_index=frame_index, event=event)
            for track in sorted(self._tracks.values(), key=lambda item: item.track_id)
        ]

    def best_confirmed(self, *, frame_index: int) -> Optional[TrackSnapshot]:
        candidates = [
            self._snapshot(track, frame_index=frame_index, event="update")
            for track in self._tracks.values()
            if track.confirmed
        ]
        if not candidates:
            return None
        return max(
            candidates,
            key=lambda item: (
                item.temporal_score,
                item.hit_ratio,
                item.mean_margin if item.mean_margin is not None else -math.inf,
                -item.track_id,
            ),
        )

    def _update_confirmation_state(self, track: _Track) -> Optional[str]:
        metrics = self._metrics(track)
        can_confirm = (
            metrics["hits_in_window"] >= self.config.required_hits
            and track.consecutive_hits >= self.config.min_consecutive_hits
        )
        if self.config.require_stability_for_confirm:
            can_confirm = can_confirm and bool(metrics["stable"])

        if not track.confirmed and can_confirm:
            track.confirmed = True
            return "confirmed"
        if track.confirmed and (
            track.consecutive_misses >= self.config.deconfirm_after_misses
        ):
            track.confirmed = False
            return "deconfirmed"
        return None

    def _enforce_track_limit(self, frame_index: int) -> list[TrackSnapshot]:
        if len(self._tracks) <= self.config.max_tracks:
            return []
        ordered = sorted(
            self._tracks.values(),
            key=lambda track: (
                track.confirmed,
                self._snapshot(
                    track,
                    frame_index=frame_index,
                    event="update",
                ).temporal_score,
                track.last_seen_monotonic,
            ),
        )
        remove_count = len(self._tracks) - self.config.max_tracks
        events: list[TrackSnapshot] = []
        for track in ordered[:remove_count]:
            events.append(
                self._snapshot(
                    track,
                    frame_index=frame_index,
                    event="expired",
                    force_state="lost",
                )
            )
            del self._tracks[track.track_id]
            self.retired_tracks += 1
            self.expiration_events += 1
        return events

    def _metrics(self, track: _Track) -> dict[str, Any]:
        evidence = list(track.history)
        matched = [item for item in evidence if item.matched and item.observation is not None]
        hits = [item.observation for item in evidence if item.hit and item.observation is not None]
        position_observations = hits or [item.observation for item in matched]
        if not position_observations:
            position_observations = [track.latest_observation]

        samples = len(evidence)
        hit_count = len(hits)
        hit_ratio = hit_count / float(max(samples, 1))

        center_x_values = [item.center_x for item in position_observations]
        center_y_values = [item.center_y for item in position_observations]
        center_x_value = float(statistics.median(center_x_values))
        center_y_value = float(statistics.median(center_y_values))
        if len(position_observations) >= 2:
            center_std = math.sqrt(
                statistics.pvariance(center_x_values)
                + statistics.pvariance(center_y_values)
            )
        else:
            center_std = 0.0

        depth_values = [
            item.depth_m
            for item in position_observations
            if item.depth_m is not None and math.isfinite(item.depth_m)
        ]
        depth_value = (
            float(statistics.median(depth_values)) if depth_values else None
        )
        depth_std = (
            float(statistics.pstdev(depth_values)) if len(depth_values) >= 2 else 0.0
        )

        boxes = [item.bbox for item in position_observations]
        bbox = BoundingBox(
            x=float(statistics.median([item.x for item in boxes])),
            y=float(statistics.median([item.y for item in boxes])),
            width=float(statistics.median([item.width for item in boxes])),
            height=float(statistics.median([item.height for item in boxes])),
        )

        positive_values = self._available_values(
            item.positive_similarity for item in hits
        )
        negative_values = self._available_values(
            item.negative_similarity for item in hits
        )
        margin_values = self._available_values(item.margin for item in hits)
        objectness_values = self._available_values(
            item.objectness_score for item in hits
        )

        center_stability = max(
            0.0,
            min(1.0, 1.0 - center_std / self.config.max_center_std_px),
        )
        if len(depth_values) >= 2:
            depth_stability = max(
                0.0,
                min(1.0, 1.0 - depth_std / self.config.max_depth_std_m),
            )
            stability_score = 0.5 * (center_stability + depth_stability)
        else:
            stability_score = center_stability

        enough_stability_observations = (
            len(position_observations)
            >= self.config.min_hit_observations_for_stability
        )
        stable = (
            enough_stability_observations
            and center_std <= self.config.max_center_std_px
            and (
                len(depth_values) < 2
                or depth_std <= self.config.max_depth_std_m
            )
        )

        mean_margin = self._mean_or_none(margin_values)
        if mean_margin is None:
            margin_score = 0.0
        else:
            margin_score = max(
                0.0,
                min(
                    1.0,
                    (mean_margin - self.config.margin_reference_low)
                    / (
                        self.config.margin_reference_good
                        - self.config.margin_reference_low
                    ),
                ),
            )

        score_weight_sum = (
            self.config.temporal_hit_weight
            + self.config.temporal_stability_weight
            + self.config.temporal_margin_weight
        )
        temporal_score = (
            self.config.temporal_hit_weight * hit_ratio
            + self.config.temporal_stability_weight * stability_score
            + self.config.temporal_margin_weight * margin_score
        ) / score_weight_sum

        return {
            "samples_in_window": samples,
            "matched_frames_in_window": len(matched),
            "hits_in_window": hit_count,
            "misses_in_window": samples - hit_count,
            "hit_ratio": hit_ratio,
            "temporal_score": temporal_score,
            "stability_score": stability_score,
            "stable": stable,
            "mean_positive_similarity": self._mean_or_none(positive_values),
            "mean_negative_similarity": self._mean_or_none(negative_values),
            "mean_margin": mean_margin,
            "min_margin_in_window": min(margin_values) if margin_values else None,
            "mean_objectness_score": self._mean_or_none(objectness_values),
            "bbox": bbox,
            "center_x": center_x_value,
            "center_y": center_y_value,
            "depth_m": depth_value,
            "center_std_px": center_std,
            "depth_std_m": depth_std,
        }

    def _snapshot(
        self,
        track: _Track,
        *,
        frame_index: int,
        event: str,
        force_state: Optional[str] = None,
    ) -> TrackSnapshot:
        metrics = self._metrics(track)
        state = force_state or ("confirmed" if track.confirmed else "tentative")
        return TrackSnapshot(
            track_id=track.track_id,
            target_object=track.target_object,
            frame_index=frame_index,
            state=state,
            event=event,
            confirmed=track.confirmed if force_state is None else False,
            track_age_frames=track.track_age_frames,
            window_size=self.config.window_size,
            required_hits=self.config.required_hits,
            samples_in_window=metrics["samples_in_window"],
            matched_frames_in_window=metrics["matched_frames_in_window"],
            hits_in_window=metrics["hits_in_window"],
            misses_in_window=metrics["misses_in_window"],
            consecutive_hits=track.consecutive_hits,
            consecutive_misses=track.consecutive_misses,
            hit_ratio=metrics["hit_ratio"],
            temporal_score=metrics["temporal_score"],
            stability_score=metrics["stability_score"],
            mean_positive_similarity=metrics["mean_positive_similarity"],
            mean_negative_similarity=metrics["mean_negative_similarity"],
            mean_margin=metrics["mean_margin"],
            min_margin_in_window=metrics["min_margin_in_window"],
            mean_objectness_score=metrics["mean_objectness_score"],
            bbox=metrics["bbox"],
            center_x=metrics["center_x"],
            center_y=metrics["center_y"],
            depth_m=metrics["depth_m"],
            center_std_px=metrics["center_std_px"],
            depth_std_m=metrics["depth_std_m"],
            last_seen_monotonic=track.last_seen_monotonic,
            latest_observation=track.latest_observation,
        )

    @staticmethod
    def _available_values(values: Iterable[Optional[float]]) -> list[float]:
        return [
            float(value)
            for value in values
            if value is not None and math.isfinite(float(value))
        ]

    @staticmethod
    def _mean_or_none(values: Sequence[float]) -> Optional[float]:
        if not values:
            return None
        return float(statistics.fmean(values))
