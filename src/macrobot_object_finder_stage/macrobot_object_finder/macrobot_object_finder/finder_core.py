"""Pure-Python core helpers for the MacRobot object finder.

This module intentionally has no ROS imports so its protocol and state logic can
be unit tested without a ROS installation.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import math
import time
import uuid
from typing import Any, Mapping, Optional


VALID_STATES = {
    "IDLE",
    "SEARCHING",
    "TRACKING",
    "FOUND",
    "LOST",
    "TIMED_OUT",
    "CANCELLED",
    "ERROR",
}


def _as_bool(value: Any, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "on"}:
        return True
    if text in {"0", "false", "no", "off"}:
        return False
    return default


def validate_target_name(name: str) -> str:
    target = str(name).strip()
    if not target:
        raise ValueError("empty_object_name")
    if target in {".", ".."} or "/" in target or "\\" in target:
        raise ValueError("unsafe_object_name")
    if len(target) > 80:
        raise ValueError("object_name_too_long")
    return target


@dataclass(frozen=True)
class FinderGoal:
    object_name: str
    timeout_sec: float = 60.0
    continuous: bool = True
    request_id: str = ""
    rebuild_banks: bool = False
    min_score: float = 0.0

    def validate(self) -> "FinderGoal":
        validate_target_name(self.object_name)
        if not math.isfinite(self.timeout_sec) or self.timeout_sec <= 0.0:
            raise ValueError("timeout_sec_must_be_positive")
        if not math.isfinite(self.min_score) or not 0.0 <= self.min_score <= 1.0:
            raise ValueError("min_score_must_be_between_0_and_1")
        return self


def parse_goal_text(
    text: str,
    *,
    default_timeout_sec: float = 60.0,
    default_continuous: bool = True,
    default_min_score: float = 0.0,
) -> FinderGoal:
    raw = str(text).strip()
    if not raw:
        raise ValueError("empty_goal")
    if raw.startswith("{"):
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError("goal_json_must_be_object")
        object_name = validate_target_name(
            str(data.get("object_name", data.get("name", "")))
        )
        request_id = str(data.get("request_id", "")).strip()
        goal = FinderGoal(
            object_name=object_name,
            timeout_sec=float(data.get("timeout_sec", default_timeout_sec)),
            continuous=_as_bool(data.get("continuous"), default_continuous),
            request_id=request_id or f"find-{uuid.uuid4().hex[:12]}",
            rebuild_banks=_as_bool(data.get("rebuild_banks"), False),
            min_score=float(data.get("min_score", default_min_score)),
        )
    else:
        goal = FinderGoal(
            object_name=validate_target_name(raw),
            timeout_sec=float(default_timeout_sec),
            continuous=bool(default_continuous),
            request_id=f"find-{uuid.uuid4().hex[:12]}",
            min_score=float(default_min_score),
        )
    return goal.validate()


def stamp_to_seconds(stamp: Any) -> float:
    try:
        return float(stamp.sec) + float(stamp.nanosec) * 1e-9
    except Exception:
        return time.time()


def temporal_message_is_usable(
    message: Any,
    goal: FinderGoal,
    *,
    minimum_depth_m: float,
    maximum_depth_m: float,
) -> bool:
    if not bool(getattr(message, "confirmed", False)):
        return False
    object_name = str(getattr(message, "target_object", "")).strip()
    if object_name.casefold() != goal.object_name.casefold():
        return False
    state = str(getattr(message, "state", "")).strip().lower()
    event = str(getattr(message, "event", "")).strip().lower()
    if state and state not in {"confirmed", "tentative"}:
        return False
    if event and event not in {"confirmed", "update"}:
        return False
    values = (
        float(getattr(message, "center_x", float("nan"))),
        float(getattr(message, "center_y", float("nan"))),
        float(getattr(message, "depth_m", float("nan"))),
        float(getattr(message, "temporal_score", float("nan"))),
    )
    if not all(math.isfinite(value) for value in values):
        return False
    if values[3] < goal.min_score:
        return False
    return minimum_depth_m <= values[2] <= maximum_depth_m


def temporal_to_result_payload(
    message: Any,
    goal: FinderGoal,
    *,
    default_frame_id: str,
) -> dict[str, Any]:
    header = getattr(message, "header", None)
    stamp = getattr(header, "stamp", None)
    frame_id = str(getattr(header, "frame_id", "")).strip() or default_frame_id
    roi = getattr(message, "roi", None)
    payload: dict[str, Any] = {
        "event": "object_found",
        "found": True,
        "object_name": goal.object_name,
        "request_id": goal.request_id,
        "score": float(getattr(message, "temporal_score", 0.0)),
        "confidence": float(getattr(message, "temporal_score", 0.0)),
        "temporal_score": float(getattr(message, "temporal_score", 0.0)),
        "stability_score": float(getattr(message, "stability_score", 0.0)),
        "track_id": int(getattr(message, "track_id", 0)),
        "center_px": {
            "x": float(getattr(message, "center_x", 0.0)),
            "y": float(getattr(message, "center_y", 0.0)),
        },
        "depth_m": float(getattr(message, "depth_m", 0.0)),
        "frame_id": frame_id,
        "stamp_sec": stamp_to_seconds(stamp),
        "horizontal_error_norm": float(
            getattr(message, "horizontal_error_norm", 0.0)
        ),
        "suggested_turn": str(getattr(message, "suggested_turn", "")),
        "center_std_px": float(getattr(message, "center_std_px", 0.0)),
        "depth_std_m": float(getattr(message, "depth_std_m", 0.0)),
        "similarity": {
            "positive": float(getattr(message, "mean_positive_similarity", -1.0)),
            "negative": float(getattr(message, "mean_negative_similarity", -1.0)),
            "margin": float(getattr(message, "mean_margin", -1.0)),
        },
    }
    if roi is not None:
        payload["bbox"] = {
            "x": int(getattr(roi, "x_offset", 0)),
            "y": int(getattr(roi, "y_offset", 0)),
            "width": int(getattr(roi, "width", 0)),
            "height": int(getattr(roi, "height", 0)),
        }
    return payload


def not_found_payload(
    *,
    goal: Optional[FinderGoal],
    reason: str,
    event: str = "object_not_found",
    details: Optional[Mapping[str, Any]] = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "event": event,
        "found": False,
        "object_name": goal.object_name if goal else "",
        "request_id": goal.request_id if goal else "",
        "reason": str(reason),
        "stamp_sec": time.time(),
    }
    if details:
        payload.update(dict(details))
    return payload


class FinderSession:
    """Small deterministic session state machine."""

    def __init__(self) -> None:
        self.state = "IDLE"
        self.goal: Optional[FinderGoal] = None
        self.started_monotonic = 0.0
        self.last_result_monotonic = 0.0
        self.track_id: Optional[int] = None
        self.found_count = 0

    def start(self, goal: FinderGoal, now: float) -> None:
        self.goal = goal.validate()
        self.state = "SEARCHING"
        self.started_monotonic = float(now)
        self.last_result_monotonic = 0.0
        self.track_id = None
        self.found_count = 0

    def cancel(self) -> None:
        self.state = "CANCELLED"

    def timeout_due(self, now: float) -> bool:
        return (
            self.goal is not None
            and self.state in {"SEARCHING", "TRACKING"}
            and float(now) - self.started_monotonic >= self.goal.timeout_sec
        )

    def accept_found(self, track_id: int, now: float) -> None:
        if self.goal is None:
            return
        self.track_id = int(track_id)
        self.last_result_monotonic = float(now)
        self.found_count += 1
        self.state = "TRACKING" if self.goal.continuous else "FOUND"

    def mark_lost(self) -> None:
        if self.goal is None:
            self.state = "IDLE"
            return
        self.track_id = None
        self.state = "SEARCHING" if self.goal.continuous else "LOST"

    def mark_timeout(self) -> None:
        self.state = "TIMED_OUT"

    def snapshot(self) -> dict[str, Any]:
        return {
            "state": self.state,
            "object_name": self.goal.object_name if self.goal else "",
            "request_id": self.goal.request_id if self.goal else "",
            "continuous": self.goal.continuous if self.goal else False,
            "timeout_sec": self.goal.timeout_sec if self.goal else 0.0,
            "track_id": self.track_id,
            "found_count": self.found_count,
        }
