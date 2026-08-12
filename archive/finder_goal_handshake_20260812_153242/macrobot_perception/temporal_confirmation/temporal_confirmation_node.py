"""ROS 2 temporal confirmation node for MacRobot embedding results."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import math
import threading
import time
from typing import Dict, Optional, Sequence, Tuple

from macrobot_interfaces.msg import (
    DepthCandidateArray,
    EmbeddingRetrievalResult,
    TemporalConfirmationResult,
)
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import RegionOfInterest
from std_msgs.msg import String
from std_srvs.srv import Trigger

from .temporal_core import (
    BoundingBox,
    Observation,
    TemporalConfig,
    TemporalTracker,
    TrackSnapshot,
)


@dataclass
class _PendingFrame:
    stamp_ns: int
    target_object: str
    messages: Dict[Tuple[int, int], EmbeddingRetrievalResult] = field(
        default_factory=dict
    )
    created_monotonic: float = field(default_factory=time.monotonic)
    last_update_monotonic: float = field(default_factory=time.monotonic)
    heartbeat_received: bool = False
    heartbeat_monotonic: float = 0.0


class TemporalConfirmationNode(Node):
    """Associate candidates across frames and apply K-of-N confirmation."""

    def __init__(self) -> None:
        super().__init__("temporal_confirmation")
        self._declare_parameters()
        self._validate_parameters()

        self._lock = threading.RLock()
        self._tracker = TemporalTracker(self._tracker_config())
        self._pending_frames: dict[int, _PendingFrame] = {}
        self._last_finalized_stamp_ns = -1
        self._frame_index = 0
        self._active_target = str(self.get_parameter("target_object").value).strip()

        self._received_messages = 0
        self._received_heartbeats = 0
        self._finalized_frames = 0
        self._empty_finalized_frames = 0
        self._invalid_observations = 0
        self._duplicate_messages = 0
        self._out_of_order_drops = 0
        self._late_result_drops = 0
        self._forced_pending_flushes = 0
        self._target_resets = 0
        self._last_event = "not_started"
        self._last_frame_candidate_count = 0
        self._last_confirmed_publish: dict[int, float] = {}
        self._legacy_found = False
        self._legacy_track_id: Optional[int] = None
        self._last_legacy_publish_monotonic = 0.0

        input_qos = QoSProfile(depth=50)
        input_qos.reliability = ReliabilityPolicy.RELIABLE
        result_qos = QoSProfile(depth=50)
        result_qos.reliability = ReliabilityPolicy.RELIABLE
        confirmed_qos = QoSProfile(depth=10)
        confirmed_qos.reliability = ReliabilityPolicy.RELIABLE
        status_qos = QoSProfile(depth=1)
        status_qos.reliability = ReliabilityPolicy.RELIABLE

        input_topic = str(self.get_parameter("input_topic").value)
        heartbeat_topic = str(self.get_parameter("frame_heartbeat_topic").value)
        result_topic = str(self.get_parameter("result_topic").value)
        confirmed_topic = str(self.get_parameter("confirmed_topic").value)
        status_topic = str(self.get_parameter("status_topic").value)
        legacy_topic = str(self.get_parameter("legacy_result_topic").value)
        target_topic = str(self.get_parameter("target_topic").value)

        self._result_publisher = self.create_publisher(
            TemporalConfirmationResult,
            result_topic,
            result_qos,
        )
        self._confirmed_publisher = self.create_publisher(
            TemporalConfirmationResult,
            confirmed_topic,
            confirmed_qos,
        )
        self._status_publisher = self.create_publisher(
            String,
            status_topic,
            status_qos,
        )
        self._legacy_publisher = self.create_publisher(
            String,
            legacy_topic,
            result_qos,
        )
        self._input_subscription = self.create_subscription(
            EmbeddingRetrievalResult,
            input_topic,
            self._input_callback,
            input_qos,
        )
        self._heartbeat_subscription = None
        if bool(self.get_parameter("use_frame_heartbeat").value):
            self._heartbeat_subscription = self.create_subscription(
                DepthCandidateArray,
                heartbeat_topic,
                self._heartbeat_callback,
                input_qos,
            )
        self._target_subscription = self.create_subscription(
            String,
            target_topic,
            self._target_callback,
            result_qos,
        )
        self._reset_service = self.create_service(
            Trigger,
            str(self.get_parameter("reset_service").value),
            self._reset_service_callback,
        )

        timer_period = max(float(self.get_parameter("timer_period_sec").value), 0.02)
        self._maintenance_timer = self.create_timer(
            timer_period,
            self._maintenance_callback,
        )
        status_period = max(float(self.get_parameter("status_period_sec").value), 0.5)
        self._status_timer = self.create_timer(status_period, self._publish_status)

        config = self._tracker.config
        self.get_logger().info(
            "Temporal confirmation ready: "
            f"input='{input_topic}', heartbeat='{heartbeat_topic}', "
            f"use_heartbeat={bool(self.get_parameter('use_frame_heartbeat').value)}, "
            f"result='{result_topic}', confirmed='{confirmed_topic}', "
            f"target='{self._active_target}', window={config.window_size}, "
            f"required_hits={config.required_hits}, "
            f"min_consecutive_hits={config.min_consecutive_hits}, "
            f"decision_source='{self.get_parameter('decision_source').value}'"
        )

    def _declare_parameters(self) -> None:
        defaults = {
            "input_topic": "/embedding_retrieval/results",
            # This small metadata topic provides every proposal-frame stamp, even
            # when no crop survives the filter/embedding stages.  It makes K-of-N
            # mean actual evaluated proposal frames rather than only positive ones.
            "use_frame_heartbeat": True,
            "frame_heartbeat_topic": "/depth_candidates/candidates",
            "frame_completion_delay_sec": 1.5,
            "frame_flush_timeout_sec": 3.0,
            "max_pending_frames": 32,
            "result_topic": "/temporal_confirmation/results",
            "confirmed_topic": "/temporal_confirmation/confirmed",
            "status_topic": "/temporal_confirmation/status",
            "legacy_result_topic": "/object_finder/result",
            "target_topic": "/embedding_retrieval/target",
            "reset_service": "/temporal_confirmation/reset",
            "target_object": "Buds3",
            "timer_period_sec": 0.05,
            # threshold_flags is recommended while embedding retrieval remains in
            # observation/pass-through mode.
            "decision_source": "threshold_flags",  # threshold_flags, accepted, custom
            "require_positive_bank_for_hit": True,
            "require_negative_bank_for_hit": True,
            "custom_min_positive_similarity": 0.45,
            "custom_min_margin": 0.05,
            "min_objectness_score": -1.0,
            # Temporal K-of-N confirmation and hysteresis.
            "window_size": 5,
            "required_hits": 3,
            "min_consecutive_hits": 2,
            "deconfirm_after_misses": 3,
            "retire_after_misses": 6,
            "track_timeout_sec": 2.5,
            "max_tracks": 12,
            "create_tracks_from_non_hits": False,
            # Spatial/depth data association. Candidate IDs are frame-local and
            # therefore deliberately not used as persistent IDs.
            "association_min_iou": 0.05,
            "association_max_center_distance_px": 120.0,
            "association_max_depth_difference_m": 0.18,
            "association_max_area_ratio": 3.0,
            "association_center_weight": 0.45,
            "association_iou_weight": 0.30,
            "association_depth_weight": 0.15,
            "association_area_weight": 0.10,
            # Reject confirmation when supposed hits jump too much spatially.
            "require_stability_for_confirm": True,
            "min_hit_observations_for_stability": 2,
            "max_center_std_px": 45.0,
            "max_depth_std_m": 0.12,
            # Human-readable temporal score. This is not a probability.
            "temporal_hit_weight": 0.55,
            "temporal_stability_weight": 0.25,
            "temporal_margin_weight": 0.20,
            "margin_reference_low": 0.05,
            "margin_reference_good": 0.20,
            # Image geometry and steering suggestion.
            # Patch-localization quality below this value falls back to the
            # original depth-candidate centre.
            "minimum_localization_quality": 0.25,
            "require_localization_for_confirm": False,
            # Output behavior.
            "publish_tentative_results": True,
            "publish_confirmed_updates": True,
            "confirmed_update_hz": 5.0,
            "publish_legacy_json": True,
            "publish_lost_legacy_event": True,
            "legacy_publish_hz": 5.0,
            "status_period_sec": 3.0,
        }
        for name, value in defaults.items():
            self.declare_parameter(name, value)

    def _validate_parameters(self) -> None:
        decision_source = str(self.get_parameter("decision_source").value).strip().lower()
        if decision_source not in {"threshold_flags", "accepted", "custom"}:
            raise ValueError(
                "decision_source must be threshold_flags, accepted, or custom"
            )
        for name in ("frame_completion_delay_sec", "frame_flush_timeout_sec"):
            if float(self.get_parameter(name).value) <= 0.0:
                raise ValueError(f"{name} must be positive")
        if int(self.get_parameter("max_pending_frames").value) <= 0:
            raise ValueError("max_pending_frames must be positive")
        self._tracker_config().validate()

    def _tracker_config(self) -> TemporalConfig:
        value = lambda name: self.get_parameter(name).value
        return TemporalConfig(
            window_size=int(value("window_size")),
            required_hits=int(value("required_hits")),
            min_consecutive_hits=int(value("min_consecutive_hits")),
            deconfirm_after_misses=int(value("deconfirm_after_misses")),
            retire_after_misses=int(value("retire_after_misses")),
            track_timeout_sec=float(value("track_timeout_sec")),
            max_tracks=int(value("max_tracks")),
            create_tracks_from_non_hits=bool(value("create_tracks_from_non_hits")),
            association_min_iou=float(value("association_min_iou")),
            association_max_center_distance_px=float(
                value("association_max_center_distance_px")
            ),
            association_max_depth_difference_m=float(
                value("association_max_depth_difference_m")
            ),
            association_max_area_ratio=float(value("association_max_area_ratio")),
            association_center_weight=float(value("association_center_weight")),
            association_iou_weight=float(value("association_iou_weight")),
            association_depth_weight=float(value("association_depth_weight")),
            association_area_weight=float(value("association_area_weight")),
            require_stability_for_confirm=bool(
                value("require_stability_for_confirm")
            ),
            min_hit_observations_for_stability=int(
                value("min_hit_observations_for_stability")
            ),
            max_center_std_px=float(value("max_center_std_px")),
            max_depth_std_m=float(value("max_depth_std_m")),
            temporal_hit_weight=float(value("temporal_hit_weight")),
            temporal_stability_weight=float(value("temporal_stability_weight")),
            temporal_margin_weight=float(value("temporal_margin_weight")),
            margin_reference_low=float(value("margin_reference_low")),
            margin_reference_good=float(value("margin_reference_good")),
        )

    @staticmethod
    def _stamp_to_ns(stamp: object) -> int:
        return int(stamp.sec) * 1_000_000_000 + int(stamp.nanosec)

    def _result_stamp_ns(self, message: EmbeddingRetrievalResult) -> int:
        value = self._stamp_to_ns(message.proposal_header.stamp)
        if value > 0:
            return value
        value = self._stamp_to_ns(message.image_header.stamp)
        if value > 0:
            return value
        return time.monotonic_ns()

    @staticmethod
    def _message_key(message: EmbeddingRetrievalResult) -> Tuple[int, int]:
        return int(message.candidate_id), int(message.crop_index)

    def _get_or_create_pending_locked(
        self,
        stamp_ns: int,
        target: str,
        now: float,
    ) -> _PendingFrame:
        pending = self._pending_frames.get(stamp_ns)
        if pending is None:
            pending = _PendingFrame(
                stamp_ns=stamp_ns,
                target_object=target,
                created_monotonic=now,
                last_update_monotonic=now,
            )
            self._pending_frames[stamp_ns] = pending
        return pending

    def _input_callback(self, message: EmbeddingRetrievalResult) -> None:
        now = time.monotonic()
        stamp_ns = self._result_stamp_ns(message)
        target = message.target_object.strip() or self._active_target

        with self._lock:
            self._received_messages += 1
            # The explicit target topic is authoritative.  A result can arrive
            # after an asynchronous DINO bank switch; letting that stale result
            # change the active target causes Eraser/Buds3 target flapping.
            if target:
                if self._active_target and target.casefold() != self._active_target.casefold():
                    self._late_result_drops += 1
                    self._last_event = (
                        f"dropped_stale_target_result result='{target}' "
                        f"active='{self._active_target}'"
                    )
                    return
                if not self._active_target:
                    self._switch_target_locked(target, reason="initial_result_target")
            if stamp_ns <= self._last_finalized_stamp_ns:
                self._late_result_drops += 1
                return

            pending = self._get_or_create_pending_locked(stamp_ns, target, now)
            key = self._message_key(message)
            if key in pending.messages:
                self._duplicate_messages += 1
            pending.messages[key] = message
            pending.last_update_monotonic = now

            if not bool(self.get_parameter("use_frame_heartbeat").value):
                self._finalize_older_frames_locked(stamp_ns, now)
            self._enforce_pending_limit_locked(now)

    def _heartbeat_callback(self, message: DepthCandidateArray) -> None:
        stamp_ns = self._stamp_to_ns(message.header.stamp)
        if stamp_ns <= 0:
            return
        now = time.monotonic()
        with self._lock:
            self._received_heartbeats += 1
            if stamp_ns <= self._last_finalized_stamp_ns:
                self._out_of_order_drops += 1
                return
            pending = self._get_or_create_pending_locked(
                stamp_ns,
                self._active_target,
                now,
            )
            pending.heartbeat_received = True
            pending.heartbeat_monotonic = now
            pending.last_update_monotonic = max(pending.last_update_monotonic, now)
            self._enforce_pending_limit_locked(now)

    def _target_callback(self, message: String) -> None:
        target = message.data.strip()
        if not target:
            return
        changed = False
        with self._lock:
            if target.casefold() != self._active_target.casefold():
                self._switch_target_locked(target, reason="target_topic_changed")
                changed = True
        if changed:
            # Finder waits for this acknowledgement before accepting detections.
            self._publish_status()

    def _switch_target_locked(self, target: str, *, reason: str) -> None:
        events = self._tracker.reset(frame_index=self._frame_index, event="expired")
        self._publish_events_locked(events)
        self._pending_frames.clear()
        self._last_finalized_stamp_ns = -1
        self._active_target = target
        self._target_resets += 1
        self._last_event = f"reset target='{target}' reason={reason}"
        self._publish_legacy_locked(best=None, force=True, lost_reason=reason)

    def _reset_service_callback(
        self,
        request: Trigger.Request,
        response: Trigger.Response,
    ) -> Trigger.Response:
        del request
        with self._lock:
            events = self._tracker.reset(
                frame_index=self._frame_index,
                event="expired",
            )
            self._publish_events_locked(events)
            self._pending_frames.clear()
            self._last_finalized_stamp_ns = -1
            self._publish_legacy_locked(
                best=None,
                force=True,
                lost_reason="manual_reset",
            )
            self._last_event = "manual_reset"
        response.success = True
        response.message = "Temporal tracks and pending frames were cleared"
        return response

    def _maintenance_callback(self) -> None:
        now = time.monotonic()
        with self._lock:
            self._finalize_ready_frames_locked(now)
            events = self._tracker.expire_stale(
                now_sec=now,
                frame_index=self._frame_index,
            )
            if events:
                self._publish_events_locked(events)
                best = self._tracker.best_confirmed(frame_index=self._frame_index)
                self._publish_legacy_locked(
                    best=best,
                    force=True,
                    lost_reason="track_timeout",
                )

    def _frame_ready_locked(self, pending: _PendingFrame, now: float) -> bool:
        if bool(self.get_parameter("use_frame_heartbeat").value):
            if pending.heartbeat_received:
                delay = float(self.get_parameter("frame_completion_delay_sec").value)
                return now - pending.heartbeat_monotonic >= delay
            timeout = float(self.get_parameter("frame_flush_timeout_sec").value)
            return now - pending.last_update_monotonic >= timeout
        timeout = float(self.get_parameter("frame_flush_timeout_sec").value)
        return now - pending.last_update_monotonic >= timeout

    def _finalize_ready_frames_locked(self, now: float) -> None:
        while self._pending_frames:
            oldest_stamp = min(self._pending_frames)
            pending = self._pending_frames[oldest_stamp]
            if not self._frame_ready_locked(pending, now):
                break
            self._finalize_stamp_locked(oldest_stamp, now)

    def _finalize_older_frames_locked(self, current_stamp: int, now: float) -> None:
        for stamp_ns in sorted(self._pending_frames):
            if stamp_ns >= current_stamp:
                break
            self._finalize_stamp_locked(stamp_ns, now)

    def _enforce_pending_limit_locked(self, now: float) -> None:
        maximum = int(self.get_parameter("max_pending_frames").value)
        while len(self._pending_frames) > maximum:
            oldest_stamp = min(self._pending_frames)
            self._forced_pending_flushes += 1
            self._finalize_stamp_locked(oldest_stamp, now)

    def _ensure_tracker_config_locked(self) -> None:
        new_config = self._tracker_config()
        new_config.validate()
        if new_config == self._tracker.config:
            return
        events = self._tracker.reset(frame_index=self._frame_index, event="expired")
        self._publish_events_locked(events)
        self._tracker = TemporalTracker(new_config)
        self._last_confirmed_publish.clear()
        self._publish_legacy_locked(
            best=None,
            force=True,
            lost_reason="temporal_parameters_changed",
        )
        self._last_event = "tracker_reconfigured"

    def _finalize_stamp_locked(self, stamp_ns: int, now: float) -> None:
        pending = self._pending_frames.pop(stamp_ns, None)
        if pending is None:
            return
        if stamp_ns <= self._last_finalized_stamp_ns:
            self._out_of_order_drops += 1
            return

        self._ensure_tracker_config_locked()
        self._last_finalized_stamp_ns = stamp_ns
        self._frame_index += 1
        self._finalized_frames += 1

        observations: list[Observation] = []
        ordered = sorted(
            pending.messages.values(),
            key=lambda item: (int(item.crop_index), int(item.candidate_id)),
        )
        for message in ordered:
            observation = self._to_observation(message, self._frame_index, stamp_ns)
            if observation is None:
                self._invalid_observations += 1
                continue
            observations.append(observation)

        if not observations:
            self._empty_finalized_frames += 1
        self._last_frame_candidate_count = len(observations)
        events = self._tracker.process_frame(
            frame_index=self._frame_index,
            observations=observations,
            now_sec=now,
        )
        self._publish_events_locked(events)
        best = self._tracker.best_confirmed(frame_index=self._frame_index)
        self._publish_legacy_locked(best=best, force=False, lost_reason="no_confirmed_track")

    def _to_observation(
        self,
        message: EmbeddingRetrievalResult,
        frame_index: int,
        stamp_ns: int,
    ) -> Optional[Observation]:
        localization_quality = float(getattr(message, "localization_quality", 0.0))
        localization_available = bool(getattr(message, "localization_available", False))
        localization_available = (
            localization_available
            and math.isfinite(localization_quality)
            and localization_quality
            >= float(self.get_parameter("minimum_localization_quality").value)
        )
        localized_roi = getattr(message, "localized_roi", None)
        candidate_roi = message.candidate.roi
        if (
            localization_available
            and localized_roi is not None
            and int(localized_roi.width) > 0
            and int(localized_roi.height) > 0
        ):
            roi = localized_roi
        elif int(candidate_roi.width) > 0 and int(candidate_roi.height) > 0:
            roi = candidate_roi
        else:
            roi = message.crop_roi
        bbox = BoundingBox(
            x=float(roi.x_offset),
            y=float(roi.y_offset),
            width=float(roi.width),
            height=float(roi.height),
        )
        if not bbox.valid():
            return None

        if localization_available:
            center_x = float(getattr(message, "localized_center_x", bbox.center_x))
            center_y = float(getattr(message, "localized_center_y", bbox.center_y))
        else:
            center_x = float(message.candidate.center_x)
            center_y = float(message.candidate.center_y)
        if not math.isfinite(center_x) or not math.isfinite(center_y):
            center_x = bbox.center_x
            center_y = bbox.center_y

        depth = float(message.candidate.median_depth_m)
        depth_m: Optional[float]
        if math.isfinite(depth) and depth > 0.0:
            depth_m = depth
        else:
            depth_m = None

        positive = (
            float(message.positive_similarity)
            if message.positive_bank_available
            and math.isfinite(float(message.positive_similarity))
            else None
        )
        negative = (
            float(message.negative_similarity)
            if message.negative_bank_available
            and math.isfinite(float(message.negative_similarity))
            else None
        )
        margin = (
            float(message.margin)
            if positive is not None
            and math.isfinite(float(message.margin))
            else None
        )
        objectness = float(message.objectness_score)
        objectness_score = (
            objectness if math.isfinite(objectness) and objectness >= 0.0 else None
        )

        return Observation(
            frame_index=frame_index,
            stamp_ns=stamp_ns,
            target_object=message.target_object.strip() or self._active_target,
            candidate_id=int(message.candidate_id),
            crop_index=int(message.crop_index),
            bbox=bbox,
            center_x=center_x,
            center_y=center_y,
            depth_m=depth_m,
            hit=self._is_hit(message, objectness_score),
            positive_similarity=positive,
            negative_similarity=negative,
            margin=margin,
            objectness_score=objectness_score,
            localization_method=(
                str(getattr(message, "localization_method", ""))
                if localization_available
                else "candidate_bbox"
            ),
            localization_quality=(localization_quality if localization_available else 0.0),
            orientation_deg=float(getattr(message, "orientation_deg", 0.0)),
            orientation_class=str(getattr(message, "orientation_class", "unknown")),
            orientation_quality=float(getattr(message, "orientation_quality", 0.0)),
            payload=message,
        )

    def _is_hit(
        self,
        message: EmbeddingRetrievalResult,
        objectness_score: Optional[float],
    ) -> bool:
        if bool(self.get_parameter("require_positive_bank_for_hit").value):
            if not message.positive_bank_available:
                return False
        if bool(self.get_parameter("require_negative_bank_for_hit").value):
            if not message.negative_bank_available:
                return False

        if bool(self.get_parameter("require_localization_for_confirm").value):
            if not bool(getattr(message, "localization_available", False)):
                return False
            if float(getattr(message, "localization_quality", 0.0)) < float(
                self.get_parameter("minimum_localization_quality").value
            ):
                return False

        minimum_objectness = float(self.get_parameter("min_objectness_score").value)
        if minimum_objectness >= 0.0:
            if objectness_score is None or objectness_score < minimum_objectness:
                return False

        source = str(self.get_parameter("decision_source").value).strip().lower()
        if source == "accepted":
            return bool(message.accepted)
        if source == "custom":
            return (
                message.positive_bank_available
                and float(message.positive_similarity)
                >= float(
                    self.get_parameter("custom_min_positive_similarity").value
                )
                and float(message.margin)
                >= float(self.get_parameter("custom_min_margin").value)
            )
        return bool(
            message.passed_positive_threshold
            and message.passed_margin_threshold
        )

    def _publish_events_locked(self, events: Sequence[TrackSnapshot]) -> None:
        now = time.monotonic()
        for snapshot in events:
            output = self._build_output(snapshot)
            should_publish_result = bool(
                self.get_parameter("publish_tentative_results").value
            ) or snapshot.state in {"confirmed", "lost"} or snapshot.event in {
                "confirmed",
                "deconfirmed",
                "expired",
            }
            if should_publish_result:
                self._result_publisher.publish(output)

            publish_confirmed = snapshot.event == "confirmed"
            if (
                snapshot.confirmed
                and snapshot.event == "update"
                and bool(self.get_parameter("publish_confirmed_updates").value)
            ):
                rate = max(
                    float(self.get_parameter("confirmed_update_hz").value),
                    0.01,
                )
                last = self._last_confirmed_publish.get(snapshot.track_id, 0.0)
                publish_confirmed = now - last >= 1.0 / rate
            if publish_confirmed:
                self._confirmed_publisher.publish(output)
                self._last_confirmed_publish[snapshot.track_id] = now

            if snapshot.event in {"expired", "deconfirmed"}:
                self._last_confirmed_publish.pop(snapshot.track_id, None)

            self._last_event = (
                f"{snapshot.event} track={snapshot.track_id} "
                f"hits={snapshot.hits_in_window}/{snapshot.samples_in_window} "
                f"score={snapshot.temporal_score:.3f}"
            )

    def _build_output(self, snapshot: TrackSnapshot) -> TemporalConfirmationResult:
        output = TemporalConfirmationResult()
        latest = snapshot.latest_observation.payload
        output.header = latest.proposal_header
        output.target_object = snapshot.target_object
        output.track_id = int(snapshot.track_id)
        output.frame_index = int(snapshot.frame_index)
        output.state = snapshot.state
        output.event = snapshot.event
        output.confirmed = bool(snapshot.confirmed)
        output.track_age_frames = int(snapshot.track_age_frames)
        output.window_size = int(snapshot.window_size)
        output.required_hits = int(snapshot.required_hits)
        output.samples_in_window = int(snapshot.samples_in_window)
        output.matched_frames_in_window = int(snapshot.matched_frames_in_window)
        output.hits_in_window = int(snapshot.hits_in_window)
        output.misses_in_window = int(snapshot.misses_in_window)
        output.consecutive_hits = int(snapshot.consecutive_hits)
        output.consecutive_misses = int(snapshot.consecutive_misses)
        output.hit_ratio = float(snapshot.hit_ratio)
        output.temporal_score = float(snapshot.temporal_score)
        output.stability_score = float(snapshot.stability_score)
        output.mean_positive_similarity = self._or_unavailable(
            snapshot.mean_positive_similarity
        )
        output.mean_negative_similarity = self._or_unavailable(
            snapshot.mean_negative_similarity
        )
        output.mean_margin = self._or_unavailable(snapshot.mean_margin)
        output.min_margin_in_window = self._or_unavailable(
            snapshot.min_margin_in_window
        )
        output.mean_objectness_score = self._or_unavailable(
            snapshot.mean_objectness_score
        )
        output.roi = self._roi_message(snapshot.bbox)
        output.center_x = float(snapshot.center_x)
        output.center_y = float(snapshot.center_y)
        output.depth_m = self._or_unavailable(snapshot.depth_m)
        output.center_std_px = float(snapshot.center_std_px)
        output.depth_std_m = float(snapshot.depth_std_m)
        output.localization_method = str(snapshot.localization_method)
        output.localization_quality = float(snapshot.localization_quality)
        output.orientation_deg = float(snapshot.orientation_deg)
        output.orientation_class = str(snapshot.orientation_class)
        output.orientation_quality = float(snapshot.orientation_quality)
        output.latest_result = latest
        return output

    @staticmethod
    def _or_unavailable(value: Optional[float]) -> float:
        return float(value) if value is not None and math.isfinite(value) else -1.0

    @staticmethod
    def _roi_message(bbox: BoundingBox) -> RegionOfInterest:
        roi = RegionOfInterest()
        roi.x_offset = max(0, int(round(bbox.x)))
        roi.y_offset = max(0, int(round(bbox.y)))
        roi.width = max(1, int(round(bbox.width)))
        roi.height = max(1, int(round(bbox.height)))
        roi.do_rectify = False
        return roi

    def _publish_legacy_locked(
        self,
        *,
        best: Optional[TrackSnapshot],
        force: bool,
        lost_reason: str,
    ) -> None:
        if not bool(self.get_parameter("publish_legacy_json").value):
            return
        now = time.monotonic()
        rate = max(float(self.get_parameter("legacy_publish_hz").value), 0.01)

        if best is None:
            if not self._legacy_found:
                return
            if not bool(self.get_parameter("publish_lost_legacy_event").value):
                self._legacy_found = False
                self._legacy_track_id = None
                return
            payload = {
                "found": False,
                "object_name": self._active_target,
                "reason": lost_reason,
                "previous_track_id": self._legacy_track_id,
                "frame_index": self._frame_index,
            }
            message = String()
            message.data = json.dumps(payload, ensure_ascii=False, sort_keys=True)
            self._legacy_publisher.publish(message)
            self._legacy_found = False
            self._legacy_track_id = None
            self._last_legacy_publish_monotonic = now
            return

        if not force and now - self._last_legacy_publish_monotonic < 1.0 / rate:
            return

        latest = best.latest_observation.payload
        payload = {
            "found": True,
            "object_name": best.target_object,
            "track_id": best.track_id,
            "frame_index": best.frame_index,
            "confidence": round(best.temporal_score, 6),
            "temporal_score": round(best.temporal_score, 6),
            "hit_ratio": round(best.hit_ratio, 6),
            "hits_in_window": best.hits_in_window,
            "window_size": best.window_size,
            "required_hits": best.required_hits,
            "consecutive_hits": best.consecutive_hits,
            "center_x": round(best.center_x, 3),
            "center_y": round(best.center_y, 3),
            "depth_m": (
                round(best.depth_m, 4) if best.depth_m is not None else None
            ),
            "bbox": {
                "x": int(round(best.bbox.x)),
                "y": int(round(best.bbox.y)),
                "width": int(round(best.bbox.width)),
                "height": int(round(best.bbox.height)),
            },
            "localization": {
                "method": best.localization_method,
                "quality": round(best.localization_quality, 6),
                "orientation_deg": round(best.orientation_deg, 3),
                "orientation_class": best.orientation_class,
                "orientation_quality": round(best.orientation_quality, 6),
            },
            "positive_similarity": round(
                best.mean_positive_similarity
                if best.mean_positive_similarity is not None
                else float(latest.positive_similarity),
                6,
            ),
            "negative_similarity": (
                round(best.mean_negative_similarity, 6)
                if best.mean_negative_similarity is not None
                else None
            ),
            "margin": (
                round(best.mean_margin, 6)
                if best.mean_margin is not None
                else None
            ),
            "stability": {
                "score": round(best.stability_score, 6),
                "center_std_px": round(best.center_std_px, 4),
                "depth_std_m": round(best.depth_std_m, 5),
            },
            "proposal_stamp": {
                "sec": int(latest.proposal_header.stamp.sec),
                "nanosec": int(latest.proposal_header.stamp.nanosec),
            },
        }
        message = String()
        message.data = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        self._legacy_publisher.publish(message)
        self._legacy_found = True
        self._legacy_track_id = best.track_id
        self._last_legacy_publish_monotonic = now

    def _publish_status(self) -> None:
        with self._lock:
            config = self._tracker.config
            payload = {
                "target_object": self._active_target,
                "decision_source": str(
                    self.get_parameter("decision_source").value
                ),
                "use_frame_heartbeat": bool(
                    self.get_parameter("use_frame_heartbeat").value
                ),
                "received_messages": self._received_messages,
                "received_heartbeats": self._received_heartbeats,
                "finalized_frames": self._finalized_frames,
                "empty_finalized_frames": self._empty_finalized_frames,
                "pending_frames": len(self._pending_frames),
                "last_frame_candidate_count": self._last_frame_candidate_count,
                "active_tracks": self._tracker.active_track_count,
                "confirmed_tracks": self._tracker.confirmed_track_count,
                "created_tracks": self._tracker.created_tracks,
                "retired_tracks": self._tracker.retired_tracks,
                "confirmation_events": self._tracker.confirmation_events,
                "deconfirmation_events": self._tracker.deconfirmation_events,
                "expiration_events": self._tracker.expiration_events,
                "invalid_observations": self._invalid_observations,
                "duplicate_messages": self._duplicate_messages,
                "out_of_order_drops": self._out_of_order_drops,
                "late_result_drops": self._late_result_drops,
                "forced_pending_flushes": self._forced_pending_flushes,
                "target_resets": self._target_resets,
                "window_size": config.window_size,
                "required_hits": config.required_hits,
                "min_consecutive_hits": config.min_consecutive_hits,
                "deconfirm_after_misses": config.deconfirm_after_misses,
                "track_timeout_sec": config.track_timeout_sec,
                "minimum_localization_quality": float(
                    self.get_parameter("minimum_localization_quality").value
                ),
                "require_localization_for_confirm": bool(
                    self.get_parameter("require_localization_for_confirm").value
                ),
                "frame_completion_delay_sec": float(
                    self.get_parameter("frame_completion_delay_sec").value
                ),
                "legacy_found": self._legacy_found,
                "legacy_track_id": self._legacy_track_id,
                "last_event": self._last_event,
            }
        message = String()
        message.data = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        self._status_publisher.publish(message)


def main(args: Optional[Sequence[str]] = None) -> None:
    rclpy.init(args=args)
    node: Optional[TemporalConfirmationNode] = None
    try:
        node = TemporalConfirmationNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
