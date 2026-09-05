"""Semantic grasp keyframes and conservative safe-region preflight."""

from __future__ import annotations

from dataclasses import dataclass
import csv
import math
from pathlib import Path
from typing import Dict, Iterable, Mapping, Optional, Sequence, Tuple

import numpy as np

from macrobot_arm_kinematics.model import MacRobotArmModel

from .planner import Q, Vector3, add3, solve_nearest


REQUIRED_STAGES = ("OPEN", "PRE_GRASP", "GRASP_OPEN", "CLOSE", "LIFT")


@dataclass(frozen=True)
class GraspKeyframeStage:
    name: str
    representation: str
    q: Q
    object_offset: Optional[Vector3] = None
    seed_q: Optional[Q] = None
    gripper_q: Optional[float] = None
    settle_sec: float = 0.10

    def validate(self) -> None:
        if self.name not in REQUIRED_STAGES:
            raise ValueError(f"unsupported grasp stage: {self.name}")
        if self.representation not in {
            "gripper_only",
            "object_relative_cartesian",
            "joint_fallback",
        }:
            raise ValueError(f"unsupported stage representation: {self.representation}")
        if len(self.q) != 3 or not all(math.isfinite(float(value)) for value in self.q):
            raise ValueError("stage q must contain three finite values")
        if self.object_offset is not None and (
            len(self.object_offset) != 3
            or not all(math.isfinite(float(value)) for value in self.object_offset)
        ):
            raise ValueError("object_offset must contain three finite values")
        if self.settle_sec < 0.0:
            raise ValueError("settle_sec must be non-negative")


@dataclass(frozen=True)
class GraspKeyframeProfile:
    name: str
    object_name: str
    stages: Mapping[str, GraspKeyframeStage]
    reference_orientation_deg: float = 0.0
    reference_orientation_class: str = "unknown"
    reference_orientation_quality: float = 0.0
    recorded_at: str = ""

    def validate(self) -> None:
        if not self.name.strip() or not self.object_name.strip():
            raise ValueError("profile and object names must be non-empty")
        missing = [name for name in REQUIRED_STAGES if name not in self.stages]
        if missing:
            raise ValueError("missing required grasp stages: " + ", ".join(missing))
        for name in REQUIRED_STAGES:
            stage = self.stages[name]
            stage.validate()
            if stage.name != name:
                raise ValueError(f"stage mapping mismatch: {name} != {stage.name}")


@dataclass(frozen=True)
class SemanticPlanStep:
    name: str
    q: Q
    target_point_base: Optional[Vector3] = None
    settle_sec: float = 0.10


@dataclass(frozen=True)
class SemanticGraspPlan:
    profile_name: str
    object_name: str
    object_point_base: Vector3
    steps: Tuple[SemanticPlanStep, ...]
    operation: str = "pick"


def capture_stage(
    *,
    stage_name: str,
    current_q: Q,
    object_point_base: Optional[Vector3],
    model: MacRobotArmModel,
    settle_sec: float = 0.10,
) -> GraspKeyframeStage:
    name = str(stage_name).strip().upper()
    if name not in REQUIRED_STAGES:
        raise ValueError(f"stage must be one of {REQUIRED_STAGES}")
    q = tuple(float(value) for value in current_q)  # type: ignore[assignment]
    if name in {"OPEN", "CLOSE"}:
        return GraspKeyframeStage(
            name=name,
            representation="gripper_only",
            q=q,
            gripper_q=q[2],
            settle_sec=settle_sec,
        )
    if object_point_base is None:
        raise ValueError(f"{name} capture requires a current localized object point")
    pose = model.forward(*q)
    tool_point = (float(pose.x), float(pose.y), float(pose.z))
    offset = tuple(
        tool_point[index] - float(object_point_base[index]) for index in range(3)
    )
    return GraspKeyframeStage(
        name=name,
        representation="object_relative_cartesian",
        q=q,
        object_offset=offset,  # type: ignore[arg-type]
        seed_q=q,
        gripper_q=q[2],
        settle_sec=settle_sec,
    )


def build_semantic_grasp_plan(
    model: MacRobotArmModel,
    profile: GraspKeyframeProfile,
    object_point_base: Vector3,
    current_q: Q,
    *,
    lateral_tolerance_m: float = 0.020,
) -> SemanticGraspPlan:
    profile.validate()
    resolved: Dict[str, SemanticPlanStep] = {}
    previous_q: Q = tuple(float(value) for value in current_q)  # type: ignore[assignment]
    for name in REQUIRED_STAGES:
        stage = profile.stages[name]
        if stage.representation == "gripper_only":
            gripper_q = float(stage.gripper_q if stage.gripper_q is not None else stage.q[2])
            q: Q = (previous_q[0], previous_q[1], gripper_q)
            target = None
        elif stage.representation == "object_relative_cartesian" and stage.object_offset is not None:
            target = add3(object_point_base, stage.object_offset)
            if abs(float(target[1]) - float(model.geometry.tool_y)) > float(lateral_tolerance_m):
                raise ValueError(f"{name.lower()}_lateral_alignment_failed")
            gripper_q = float(stage.gripper_q if stage.gripper_q is not None else stage.q[2])
            seed = stage.seed_q or stage.q or previous_q
            solution = solve_nearest(
                model,
                target,
                seed_q=seed,
                gripper_q=gripper_q,
            )
            if solution is None:
                raise ValueError(f"{name.lower()}_ik_failed")
            q = (solution.q1, solution.q2, gripper_q)
        else:
            q = stage.q
            target = None
        if not model.limits.contains(*q):
            raise ValueError(f"{name.lower()}_joint_limits_failed")
        resolved[name] = SemanticPlanStep(name, q, target, stage.settle_sec)
        previous_q = q
    return SemanticGraspPlan(
        profile_name=profile.name,
        object_name=profile.object_name,
        object_point_base=object_point_base,
        steps=tuple(resolved[name] for name in REQUIRED_STAGES),
        operation="pick",
    )


def _resolve_cartesian_stage(
    model: MacRobotArmModel,
    stage: GraspKeyframeStage,
    object_point_base: Vector3,
    *,
    gripper_q: float,
    fallback_q: Q,
    lateral_tolerance_m: float,
    output_name: str,
) -> SemanticPlanStep:
    if stage.representation == "object_relative_cartesian" and stage.object_offset is not None:
        target = add3(object_point_base, stage.object_offset)
        if abs(float(target[1]) - float(model.geometry.tool_y)) > float(lateral_tolerance_m):
            raise ValueError(f"{output_name.lower()}_lateral_alignment_failed")
        solution = solve_nearest(
            model,
            target,
            seed_q=stage.seed_q or stage.q or fallback_q,
            gripper_q=gripper_q,
        )
        if solution is None:
            raise ValueError(f"{output_name.lower()}_ik_failed")
        q: Q = (solution.q1, solution.q2, gripper_q)
    else:
        # Older profiles may contain a joint fallback.  Preserve the arm pose
        # while explicitly overriding the gripper state required by PLACE.
        q = (stage.q[0], stage.q[1], gripper_q)
        target = None
    if not model.limits.contains(*q):
        raise ValueError(f"{output_name.lower()}_joint_limits_failed")
    return SemanticPlanStep(output_name, q, target, stage.settle_sec)


def build_semantic_place_plan(
    model: MacRobotArmModel,
    profile: GraspKeyframeProfile,
    placement_point_base: Vector3,
    current_q: Q,
    *,
    lateral_tolerance_m: float = 0.020,
) -> SemanticGraspPlan:
    """Build the safe reverse of the semantic pick sequence.

    The held object approaches the target with the gripper closed, descends to
    the recorded GRASP_OPEN relative pose, opens, and retreats to PRE_GRASP.
    The plan intentionally does not assume that simply replaying joint angles in
    reverse is valid; Cartesian keyframes are re-solved at the new placement
    point before safe-region preflight.
    """

    profile.validate()
    open_stage = profile.stages["OPEN"]
    close_stage = profile.stages["CLOSE"]
    open_q = float(
        open_stage.gripper_q if open_stage.gripper_q is not None else open_stage.q[2]
    )
    close_q = float(
        close_stage.gripper_q if close_stage.gripper_q is not None else close_stage.q[2]
    )
    previous: Q = tuple(float(value) for value in current_q)  # type: ignore[assignment]
    above = _resolve_cartesian_stage(
        model,
        profile.stages["LIFT"],
        placement_point_base,
        gripper_q=close_q,
        fallback_q=previous,
        lateral_tolerance_m=lateral_tolerance_m,
        output_name="PLACE_ABOVE",
    )
    descend = _resolve_cartesian_stage(
        model,
        profile.stages["GRASP_OPEN"],
        placement_point_base,
        gripper_q=close_q,
        fallback_q=above.q,
        lateral_tolerance_m=lateral_tolerance_m,
        output_name="PLACE_DESCEND",
    )
    release_q: Q = (descend.q[0], descend.q[1], open_q)
    if not model.limits.contains(*release_q):
        raise ValueError("place_release_joint_limits_failed")
    release = SemanticPlanStep(
        "PLACE_RELEASE", release_q, descend.target_point_base, open_stage.settle_sec
    )
    retreat = _resolve_cartesian_stage(
        model,
        profile.stages["PRE_GRASP"],
        placement_point_base,
        gripper_q=open_q,
        fallback_q=release.q,
        lateral_tolerance_m=lateral_tolerance_m,
        output_name="PLACE_RETREAT",
    )
    return SemanticGraspPlan(
        profile_name=profile.name,
        object_name=profile.object_name,
        object_point_base=placement_point_base,
        steps=(above, descend, release, retreat),
        operation="place",
    )


class SafeRegionLookup:
    """Nearest-sample validator for the generated connected safe-region CSV.

    This does not replace the runtime IK validator.  It is an early preflight so
    a multi-stage grasp can be rejected before the first physical motion.  The
    endpoint and every interpolated point are still validated again by the
    normal ROS validator and servo bridge during execution.
    """

    def __init__(self, samples: np.ndarray, *, max_distance_rad: float = 0.06) -> None:
        array = np.asarray(samples, dtype=np.float64)
        if array.ndim != 2 or array.shape[1] != 3 or array.shape[0] == 0:
            raise ValueError("safe-region samples must have shape [N, 3]")
        if not np.all(np.isfinite(array)):
            raise ValueError("safe-region samples contain non-finite values")
        self.samples = array
        self.max_distance_rad = float(max_distance_rad)

    @classmethod
    def from_csv(cls, path: str | Path, *, max_distance_rad: float = 0.06) -> "SafeRegionLookup":
        csv_path = Path(path).expanduser().resolve()
        if not csv_path.is_file():
            raise FileNotFoundError(csv_path)
        rows: list[tuple[float, float, float]] = []
        with csv_path.open(newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream)
            names = reader.fieldnames or []
            lowered = {name.casefold(): name for name in names}
            def find(*candidates: str) -> str:
                for candidate in candidates:
                    if candidate.casefold() in lowered:
                        return lowered[candidate.casefold()]
                raise ValueError(f"safe-region CSV missing one of {candidates}")
            q1_key = find("q1_rad", "q1", "arm_lift_joint")
            q2_key = find("q2_rad", "q2", "wrist_pitch_joint")
            q3_key = find("q3_rad", "q3", "gripper_joint")
            safe_key = lowered.get("safe")
            connected_key = lowered.get("connected")
            for row in reader:
                if safe_key and str(row.get(safe_key, "1")).strip().lower() in {"0", "false", "no"}:
                    continue
                if connected_key and str(row.get(connected_key, "1")).strip().lower() in {"0", "false", "no"}:
                    continue
                rows.append((float(row[q1_key]), float(row[q2_key]), float(row[q3_key])))
        return cls(np.asarray(rows, dtype=np.float64), max_distance_rad=max_distance_rad)

    def nearest_distance(self, q: Q) -> float:
        value = np.asarray(q, dtype=np.float64).reshape(1, 3)
        return float(np.min(np.linalg.norm(self.samples - value, axis=1)))

    def contains(self, q: Q) -> bool:
        return self.nearest_distance(q) <= self.max_distance_rad

    def validate_path(
        self,
        start: Q,
        goal: Q,
        *,
        interpolation_step_rad: float = 0.025,
    ) -> tuple[bool, Optional[Q], float]:
        delta = np.asarray(goal, dtype=np.float64) - np.asarray(start, dtype=np.float64)
        steps = max(1, int(math.ceil(float(np.max(np.abs(delta))) / max(interpolation_step_rad, 1e-6))))
        for index in range(steps + 1):
            ratio = index / float(steps)
            point = tuple((np.asarray(start) + ratio * delta).tolist())  # type: ignore[assignment]
            distance = self.nearest_distance(point)
            if distance > self.max_distance_rad:
                return False, point, distance
        return True, None, 0.0

    def validate_plan(
        self,
        current_q: Q,
        plan: SemanticGraspPlan,
        *,
        interpolation_step_rad: float = 0.025,
    ) -> tuple[bool, str, Optional[Q], float]:
        previous = current_q
        for step in plan.steps:
            ok, point, distance = self.validate_path(
                previous,
                step.q,
                interpolation_step_rad=interpolation_step_rad,
            )
            if not ok:
                return False, step.name, point, distance
            previous = step.q
        return True, "", None, 0.0
