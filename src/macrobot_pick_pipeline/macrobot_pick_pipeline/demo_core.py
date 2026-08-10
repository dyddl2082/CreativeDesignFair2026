from __future__ import annotations

from dataclasses import dataclass, field
import math
import re
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


Q = Tuple[float, float, float]
JOINT_NAMES = ("arm_lift_joint", "wrist_pitch_joint", "gripper_joint")


def q3(value: Any, *, name: str = "q") -> Q:
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        raise ValueError(f"{name} must contain exactly three numbers")
    result = tuple(float(item) for item in value)
    if not all(math.isfinite(item) for item in result):
        raise ValueError(f"{name} contains a non-finite value")
    return result  # type: ignore[return-value]


def max_joint_delta(a: Q, b: Q) -> float:
    return max(abs(a[index] - b[index]) for index in range(3))


def safe_name(value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip())
    normalized = normalized.strip("._")
    if not normalized:
        raise ValueError("name must contain at least one letter or number")
    return normalized[:96]


@dataclass(frozen=True)
class Waypoint:
    t_sec: float
    q: Q

    def as_dict(self) -> Dict[str, Any]:
        return {"t_sec": float(self.t_sec), "q": list(self.q)}

    @staticmethod
    def from_mapping(data: Mapping[str, Any]) -> "Waypoint":
        return Waypoint(
            t_sec=max(0.0, float(data.get("t_sec", 0.0))),
            q=q3(data.get("q"), name="waypoint.q"),
        )


@dataclass
class DemoRecording:
    name: str
    kind: str
    recorded_at: str
    waypoints: List[Waypoint]
    speed_scale: float = 0.5
    notes: str = ""
    marks: List[Dict[str, Any]] = field(default_factory=list)
    source_state: str = "commanded_logical_state"

    @property
    def duration_sec(self) -> float:
        return self.waypoints[-1].t_sec if self.waypoints else 0.0

    @property
    def final_q(self) -> Q:
        if not self.waypoints:
            return (0.0, 0.0, 0.0)
        return self.waypoints[-1].q

    def as_dict(self) -> Dict[str, Any]:
        return {
            "schema": "macrobot.arm_primitive/v2",
            "name": self.name,
            "kind": self.kind,
            "recorded_at": self.recorded_at,
            "joint_names": list(JOINT_NAMES),
            "source_state": self.source_state,
            "warning": (
                "logical_joint_states are command-derived unless external joint encoders are added"
            ),
            "speed_scale": float(self.speed_scale),
            "notes": self.notes,
            "duration_sec": float(self.duration_sec),
            "waypoint_count": len(self.waypoints),
            "final_q": list(self.final_q),
            "marks": list(self.marks),
            "waypoints": [waypoint.as_dict() for waypoint in self.waypoints],
        }

    @staticmethod
    def from_mapping(data: Mapping[str, Any]) -> "DemoRecording":
        raw_waypoints = data.get("waypoints", [])
        if not isinstance(raw_waypoints, Sequence):
            raise ValueError("primitive.waypoints must be a sequence")
        waypoints = [
            Waypoint.from_mapping(item)
            for item in raw_waypoints
            if isinstance(item, Mapping)
        ]
        if not waypoints:
            final_q = data.get("final_q") or data.get("target_q")
            if final_q is not None:
                waypoints = [Waypoint(0.0, q3(final_q, name="primitive.final_q"))]
        if not waypoints:
            raise ValueError("primitive contains no waypoints")
        return DemoRecording(
            name=safe_name(str(data.get("name", "primitive"))),
            kind=str(data.get("kind", "trajectory")),
            recorded_at=str(data.get("recorded_at", "")),
            waypoints=waypoints,
            speed_scale=max(0.05, min(1.0, float(data.get("speed_scale", 0.5)))),
            notes=str(data.get("notes", "")),
            marks=[dict(item) for item in data.get("marks", []) if isinstance(item, Mapping)],
            source_state=str(data.get("source_state", "commanded_logical_state")),
        )


class TrajectorySampler:
    """Record a compact logical-joint trajectory from a live state stream."""

    def __init__(
        self,
        *,
        min_joint_delta_rad: float = 0.003,
        max_sample_interval_sec: float = 0.25,
        max_duration_sec: float = 180.0,
    ) -> None:
        self.min_joint_delta_rad = max(0.0, float(min_joint_delta_rad))
        self.max_sample_interval_sec = max(0.02, float(max_sample_interval_sec))
        self.max_duration_sec = max(1.0, float(max_duration_sec))
        self.started_at_monotonic: Optional[float] = None
        self.paused_at_monotonic: Optional[float] = None
        self.paused_total_sec = 0.0
        self.waypoints: List[Waypoint] = []
        self.marks: List[Dict[str, Any]] = []

    @property
    def active(self) -> bool:
        return self.started_at_monotonic is not None

    @property
    def paused(self) -> bool:
        return self.paused_at_monotonic is not None

    def start(self, now: float, q: Q) -> None:
        self.started_at_monotonic = float(now)
        self.paused_at_monotonic = None
        self.paused_total_sec = 0.0
        self.waypoints = [Waypoint(0.0, q)]
        self.marks = []

    def pause(self, now: float) -> None:
        if self.active and not self.paused:
            self.paused_at_monotonic = float(now)

    def resume(self, now: float) -> None:
        if self.active and self.paused_at_monotonic is not None:
            self.paused_total_sec += max(0.0, float(now) - self.paused_at_monotonic)
            self.paused_at_monotonic = None

    def elapsed(self, now: float) -> float:
        if self.started_at_monotonic is None:
            return 0.0
        effective_now = self.paused_at_monotonic if self.paused_at_monotonic is not None else float(now)
        return max(0.0, effective_now - self.started_at_monotonic - self.paused_total_sec)

    def add(self, now: float, q: Q, *, force: bool = False) -> bool:
        if not self.active or self.paused:
            return False
        elapsed = self.elapsed(now)
        if elapsed > self.max_duration_sec:
            return False
        if not self.waypoints:
            self.waypoints.append(Waypoint(elapsed, q))
            return True
        previous = self.waypoints[-1]
        changed = max_joint_delta(previous.q, q) >= self.min_joint_delta_rad
        stale = elapsed - previous.t_sec >= self.max_sample_interval_sec
        if force or changed or stale:
            self.waypoints.append(Waypoint(elapsed, q))
            return True
        return False

    def mark(self, now: float, label: str) -> None:
        if not self.active:
            raise ValueError("no active recording")
        self.marks.append({"t_sec": self.elapsed(now), "label": str(label)})

    def finish(self, now: float, q: Q) -> Tuple[List[Waypoint], List[Dict[str, Any]]]:
        if not self.active:
            raise ValueError("no active recording")
        if self.paused:
            self.resume(now)
        self.add(now, q, force=True)
        result = list(self.waypoints)
        marks = list(self.marks)
        self.started_at_monotonic = None
        self.paused_at_monotonic = None
        return result, marks


def playback_keyframes(
    waypoints: Iterable[Waypoint],
    *,
    min_joint_delta_rad: float = 0.01,
    max_interval_sec: float = 1.0,
) -> List[Waypoint]:
    """Reduce a recorded path to safe, meaningful playback keyframes."""
    values = list(waypoints)
    if len(values) <= 2:
        return values
    result = [values[0]]
    for item in values[1:-1]:
        previous = result[-1]
        if (
            max_joint_delta(previous.q, item.q) >= min_joint_delta_rad
            or item.t_sec - previous.t_sec >= max_interval_sec
        ):
            result.append(item)
    if max_joint_delta(result[-1].q, values[-1].q) > 1e-9:
        result.append(values[-1])
    elif result[-1].t_sec != values[-1].t_sec:
        result[-1] = values[-1]
    return result
