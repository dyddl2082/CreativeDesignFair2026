from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import math
import statistics
import time
from typing import Deque, Iterable, List, Optional, Sequence, Tuple

from macrobot_arm_kinematics.model import IKSolution, MacRobotArmModel

from .profiles import PickProfile, Q, Vector3


@dataclass(frozen=True)
class DetectionSample:
    stamp_sec: float
    object_name: str
    score: float
    point_base: Vector3
    source: str = ""


@dataclass(frozen=True)
class StableDetection:
    object_name: str
    score: float
    point_base: Vector3
    sample_count: int
    radius_m: float


class StablePointFilter:
    def __init__(self) -> None:
        self.samples: Deque[DetectionSample] = deque()

    def clear(self) -> None:
        self.samples.clear()

    def add(self, sample: DetectionSample) -> None:
        self.samples.append(sample)

    def stable(
        self,
        *,
        now_sec: float,
        object_name: str,
        minimum_score: float,
        minimum_count: int,
        window_sec: float,
        radius_m: float,
    ) -> Optional[StableDetection]:
        cutoff = now_sec - window_sec
        while self.samples and self.samples[0].stamp_sec < cutoff:
            self.samples.popleft()

        target_key = object_name.strip().casefold()
        eligible = [
            item
            for item in self.samples
            if item.object_name.strip().casefold() == target_key
            and item.score >= minimum_score
        ]
        if len(eligible) < minimum_count:
            return None

        # Use the newest requested number of observations so an older cluster
        # does not mask motion of the object.
        eligible = eligible[-minimum_count:]
        coordinates = list(zip(*(item.point_base for item in eligible)))
        median_point: Vector3 = tuple(
            float(statistics.median(axis)) for axis in coordinates
        )  # type: ignore[assignment]
        distances = [
            math.dist(item.point_base, median_point)
            for item in eligible
        ]
        cluster_radius = max(distances, default=0.0)
        if cluster_radius > radius_m:
            return None
        return StableDetection(
            object_name=object_name,
            score=float(statistics.median(item.score for item in eligible)),
            point_base=median_point,
            sample_count=len(eligible),
            radius_m=cluster_radius,
        )


@dataclass(frozen=True)
class PlannedStep:
    name: str
    q: Q
    target_point_base: Optional[Vector3] = None


@dataclass(frozen=True)
class PickPlan:
    object_name: str
    object_point_base: Vector3
    grasp_point_base: Vector3
    pregrasp_point_base: Vector3
    lift_point_base: Vector3
    steps: Tuple[PlannedStep, ...]


def add3(a: Vector3, b: Vector3) -> Vector3:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def solve_nearest(
    model: MacRobotArmModel,
    point: Vector3,
    *,
    seed_q: Q,
    gripper_q: float,
) -> Optional[IKSolution]:
    solutions = model.inverse(
        point[0],
        point[2],
        seed=(seed_q[0], seed_q[1]),
        gripper_q=gripper_q,
    )
    return solutions[0] if solutions else None


def build_pick_plan(
    model: MacRobotArmModel,
    profile: PickProfile,
    object_name: str,
    object_point_base: Vector3,
    current_q: Q,
) -> PickPlan:
    grasp_point = add3(object_point_base, profile.grasp_offset_base)
    pregrasp_point = add3(grasp_point, profile.pregrasp_offset_base)
    lift_point = add3(grasp_point, profile.lift_offset_base)

    pre_seed = profile.pre_grasp_seed_q or current_q
    pre_solution = solve_nearest(
        model,
        pregrasp_point,
        seed_q=pre_seed,
        gripper_q=profile.open_q3,
    )
    if pre_solution is None:
        raise ValueError("pregrasp_unreachable")

    # Solve the final grasp point using the closed gripper geometry. The arm
    # approaches with q3 open but, after closing at the same q1/q2, the dynamic
    # grasp_frame is centred on the object.
    grasp_seed = profile.grasp_seed_q or (
        pre_solution.q1,
        pre_solution.q2,
        profile.open_q3,
    )
    grasp_solution = solve_nearest(
        model,
        grasp_point,
        seed_q=grasp_seed,
        gripper_q=profile.close_q3,
    )
    if grasp_solution is None:
        raise ValueError("grasp_unreachable")

    lift_seed = profile.lift_seed_q or (
        grasp_solution.q1,
        grasp_solution.q2,
        profile.close_q3,
    )
    lift_solution = solve_nearest(
        model,
        lift_point,
        seed_q=lift_seed,
        gripper_q=profile.close_q3,
    )
    if lift_solution is None:
        raise ValueError("lift_unreachable")

    open_current: Q = (current_q[0], current_q[1], profile.open_q3)
    pre_q: Q = (pre_solution.q1, pre_solution.q2, profile.open_q3)
    approach_q: Q = (
        grasp_solution.q1,
        grasp_solution.q2,
        profile.open_q3,
    )
    close_q: Q = (
        grasp_solution.q1,
        grasp_solution.q2,
        profile.close_q3,
    )
    lift_q: Q = (
        lift_solution.q1,
        lift_solution.q2,
        profile.close_q3,
    )

    return PickPlan(
        object_name=object_name,
        object_point_base=object_point_base,
        grasp_point_base=grasp_point,
        pregrasp_point_base=pregrasp_point,
        lift_point_base=lift_point,
        steps=(
            PlannedStep("OPEN", open_current),
            PlannedStep("PRE_GRASP", pre_q, pregrasp_point),
            PlannedStep("APPROACH", approach_q, grasp_point),
            PlannedStep("CLOSE", close_q, grasp_point),
            PlannedStep("LIFT", lift_q, lift_point),
        ),
    )
