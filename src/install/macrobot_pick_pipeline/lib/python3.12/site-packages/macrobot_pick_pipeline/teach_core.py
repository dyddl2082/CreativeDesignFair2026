from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Any, Dict, Mapping, MutableMapping, Optional, Tuple


Vector3 = Tuple[float, float, float]
Q = Tuple[float, float, float]


PROFILE_REQUIRED_STAGES = ("PRE_GRASP", "GRASP", "CLOSE", "LIFT")
PROFILE_OPTIONAL_STAGES = ("PLACE",)
PROFILE_STAGES = PROFILE_REQUIRED_STAGES + PROFILE_OPTIONAL_STAGES


def vector3(value: Any, *, name: str = "vector") -> Vector3:
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        raise ValueError(f"{name} must contain exactly three numbers")
    result = tuple(float(item) for item in value)
    if not all(math.isfinite(item) for item in result):
        raise ValueError(f"{name} contains a non-finite value")
    return result  # type: ignore[return-value]


def q3(value: Any, *, name: str = "q") -> Q:
    return vector3(value, name=name)


def add3(a: Vector3, b: Vector3) -> Vector3:
    return tuple(a[index] + b[index] for index in range(3))  # type: ignore[return-value]


def sub3(a: Vector3, b: Vector3) -> Vector3:
    return tuple(a[index] - b[index] for index in range(3))  # type: ignore[return-value]


def distance3(a: Vector3, b: Vector3) -> float:
    return math.sqrt(sum((a[index] - b[index]) ** 2 for index in range(3)))


@dataclass
class RecordedStage:
    name: str
    q: Q
    tool_point_base: Vector3
    target_point_base: Vector3
    captured_at: str
    notes: str = ""
    score: Optional[float] = None
    gripper_gap_m: Optional[float] = None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "q": list(self.q),
            "tool_point_base": list(self.tool_point_base),
            "target_point_base": list(self.target_point_base),
            "captured_at": self.captured_at,
            "notes": self.notes,
            "score": self.score,
            "gripper_gap_m": self.gripper_gap_m,
        }

    @staticmethod
    def from_mapping(data: Mapping[str, Any]) -> "RecordedStage":
        return RecordedStage(
            name=str(data.get("name", "")).upper(),
            q=q3(data.get("q"), name="stage.q"),
            tool_point_base=vector3(
                data.get("tool_point_base"), name="stage.tool_point_base"
            ),
            target_point_base=vector3(
                data.get("target_point_base"), name="stage.target_point_base"
            ),
            captured_at=str(data.get("captured_at", "")),
            notes=str(data.get("notes", "")),
            score=(float(data["score"]) if data.get("score") is not None else None),
            gripper_gap_m=(
                float(data["gripper_gap_m"])
                if data.get("gripper_gap_m") is not None
                else None
            ),
        )


@dataclass
class ProfileDraft:
    object_name: str
    target_point_base: Vector3
    started_at: str
    speed_scale: float = 0.5
    notes: str = ""
    stages: MutableMapping[str, RecordedStage] = field(default_factory=dict)

    def capture(self, stage: RecordedStage) -> None:
        normalized = stage.name.upper()
        if normalized not in PROFILE_STAGES:
            raise ValueError(f"unsupported profile stage: {normalized}")
        self.stages[normalized] = stage

    def as_dict(self) -> Dict[str, Any]:
        return {
            "object_name": self.object_name,
            "target_point_base": list(self.target_point_base),
            "started_at": self.started_at,
            "speed_scale": self.speed_scale,
            "notes": self.notes,
            "stages": {
                name: stage.as_dict() for name, stage in self.stages.items()
            },
        }

    @staticmethod
    def from_mapping(data: Mapping[str, Any]) -> "ProfileDraft":
        stages: Dict[str, RecordedStage] = {}
        raw_stages = data.get("stages", {})
        if isinstance(raw_stages, Mapping):
            for name, raw in raw_stages.items():
                if isinstance(raw, Mapping):
                    stage = RecordedStage.from_mapping(raw)
                    stages[str(name).upper()] = stage
        return ProfileDraft(
            object_name=str(data.get("object_name", "")),
            target_point_base=vector3(
                data.get("target_point_base"), name="draft.target_point_base"
            ),
            started_at=str(data.get("started_at", "")),
            speed_scale=max(0.05, min(1.0, float(data.get("speed_scale", 0.5)))),
            notes=str(data.get("notes", "")),
            stages=stages,
        )


def derive_pick_profile(draft: ProfileDraft) -> Dict[str, Any]:
    missing = [name for name in PROFILE_REQUIRED_STAGES if name not in draft.stages]
    if missing:
        raise ValueError("missing profile stages: " + ", ".join(missing))

    pre = draft.stages["PRE_GRASP"]
    grasp = draft.stages["GRASP"]
    close = draft.stages["CLOSE"]
    lift = draft.stages["LIFT"]
    place = draft.stages.get("PLACE")

    if close.q[2] <= grasp.q[2] + 1e-6:
        raise ValueError(
            "CLOSE q3 must be greater than GRASP/open q3 under the current physical convention"
        )
    if abs(lift.q[2] - close.q[2]) > 0.15:
        raise ValueError(
            "LIFT must keep approximately the same closed-gripper q3 as CLOSE"
        )

    # The closed grasp_frame is the physically relevant contact centre.  The
    # camera target is locked before the jaws occlude it, so the same reference
    # point is used for all later stages.
    grasp_offset = sub3(close.tool_point_base, draft.target_point_base)
    pregrasp_offset = sub3(pre.tool_point_base, close.tool_point_base)
    lift_offset = sub3(lift.tool_point_base, close.tool_point_base)

    profile: Dict[str, Any] = {
        "object_name": draft.object_name,
        "open_q3": float(grasp.q[2]),
        "close_q3": float(close.q[2]),
        "pre_grasp_q": list(pre.q),
        "grasp_q": list(grasp.q),
        "lift_q": list(lift.q),
        "place_q": list(place.q) if place is not None else list(lift.q),
        "pre_grasp_seed_q": list(pre.q),
        "grasp_seed_q": list(grasp.q),
        "lift_seed_q": list(lift.q),
        "grasp_offset_base": list(grasp_offset),
        "pregrasp_offset_base": list(pregrasp_offset),
        "lift_offset_base": list(lift_offset),
        "sequence": ["OPEN", "PRE_GRASP", "GRASP", "CLOSE", "LIFT"],
        "speed_scale": draft.speed_scale,
        "notes": draft.notes,
        "camera_reference": {
            "target_point_base": list(draft.target_point_base),
            "pre_grasp_tool_point_base": list(pre.tool_point_base),
            "grasp_open_tool_point_base": list(grasp.tool_point_base),
            "grasp_closed_tool_point_base": list(close.tool_point_base),
            "lift_tool_point_base": list(lift.tool_point_base),
            "profile_reference_distance_m": distance3(
                draft.target_point_base, close.tool_point_base
            ),
        },
        "stages": {
            name: stage.as_dict() for name, stage in draft.stages.items()
        },
    }
    return profile


def pick_profile_overlay(profile: Mapping[str, Any]) -> Dict[str, Any]:
    """Convert a report profile to the object entry used by pick_profiles.yaml."""
    keys = (
        "open_q3",
        "close_q3",
        "grasp_offset_base",
        "pregrasp_offset_base",
        "lift_offset_base",
        "pre_grasp_seed_q",
        "grasp_seed_q",
        "lift_seed_q",
        "speed_scale",
        "notes",
    )
    return {key: profile[key] for key in keys if key in profile}
