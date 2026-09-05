"""Timestamped Pico-odometry history for delayed perception compensation.

DINO inference and temporal confirmation can finish after the chassis has moved.
A point expressed in ``base_link`` at camera time must therefore be transformed
through the base pose at capture time before it is used at the current pose.
This module deliberately uses only the existing Pico odometry; it does not claim
that wheel odometry is a persistent global map.
"""

from __future__ import annotations

from dataclasses import dataclass
import bisect
import math
from typing import List, Optional, Tuple

from .stored_object_core import OdomPose, point_base_to_odom, point_odom_to_base, wrap_angle_deg


Vector3 = Tuple[float, float, float]


def _interpolate_angle_deg(first: float, second: float, ratio: float) -> float:
    delta = wrap_angle_deg(float(second) - float(first))
    return wrap_angle_deg(float(first) + float(ratio) * delta)


@dataclass(frozen=True)
class PoseSnapshot:
    wall_sec: float
    pose: OdomPose


@dataclass(frozen=True)
class MotionSegment:
    purpose: str
    start_wall_sec: float
    end_wall_sec: float
    start_pose: OdomPose
    end_pose: OdomPose
    commanded_amount: float = 0.0

    def contains(self, wall_sec: float) -> bool:
        return self.start_wall_sec <= wall_sec <= self.end_wall_sec

    def pose_at(self, wall_sec: float) -> OdomPose:
        duration = max(1e-9, self.end_wall_sec - self.start_wall_sec)
        ratio = min(1.0, max(0.0, (wall_sec - self.start_wall_sec) / duration))
        pico_time = None
        if self.start_pose.pico_time_ms is not None and self.end_pose.pico_time_ms is not None:
            pico_time = int(round(
                self.start_pose.pico_time_ms
                + ratio * (self.end_pose.pico_time_ms - self.start_pose.pico_time_ms)
            ))
        return OdomPose(
            x_m=self.start_pose.x_m + ratio * (self.end_pose.x_m - self.start_pose.x_m),
            y_m=self.start_pose.y_m + ratio * (self.end_pose.y_m - self.start_pose.y_m),
            yaw_deg=_interpolate_angle_deg(
                self.start_pose.yaw_deg, self.end_pose.yaw_deg, ratio
            ),
            reliable=self.start_pose.reliable and self.end_pose.reliable,
            pico_time_ms=pico_time,
        )


class PoseHistory:
    """Small bounded history of odometry samples and completed motion segments."""

    def __init__(
        self,
        *,
        max_snapshots: int = 256,
        max_segments: int = 128,
        nearest_tolerance_sec: float = 0.35,
    ) -> None:
        self.max_snapshots = max(4, int(max_snapshots))
        self.max_segments = max(2, int(max_segments))
        self.nearest_tolerance_sec = max(0.0, float(nearest_tolerance_sec))
        self._snapshots: List[PoseSnapshot] = []
        self._segments: List[MotionSegment] = []
        self._pending: Optional[tuple[str, float, OdomPose, float]] = None

    @property
    def pending(self) -> bool:
        return self._pending is not None

    @property
    def latest_pose(self) -> Optional[OdomPose]:
        return self._snapshots[-1].pose if self._snapshots else None

    @property
    def segments(self) -> Tuple[MotionSegment, ...]:
        return tuple(self._segments)

    def clear(self) -> None:
        self._snapshots.clear()
        self._segments.clear()
        self._pending = None

    def add_snapshot(self, wall_sec: float, pose: OdomPose) -> None:
        stamp = float(wall_sec)
        if not math.isfinite(stamp):
            raise ValueError("wall_sec must be finite")
        if self._snapshots and stamp < self._snapshots[-1].wall_sec:
            stamps = [item.wall_sec for item in self._snapshots]
            index = bisect.bisect_left(stamps, stamp)
            self._snapshots.insert(index, PoseSnapshot(stamp, pose))
        elif self._snapshots and abs(stamp - self._snapshots[-1].wall_sec) < 1e-9:
            self._snapshots[-1] = PoseSnapshot(stamp, pose)
        else:
            self._snapshots.append(PoseSnapshot(stamp, pose))
        if len(self._snapshots) > self.max_snapshots:
            del self._snapshots[: len(self._snapshots) - self.max_snapshots]

    def begin_motion(
        self,
        purpose: str,
        wall_sec: float,
        start_pose: OdomPose,
        commanded_amount: float = 0.0,
    ) -> None:
        if self._pending is not None:
            raise RuntimeError("a motion segment is already pending")
        self.add_snapshot(wall_sec, start_pose)
        self._pending = (
            str(purpose),
            float(wall_sec),
            start_pose,
            float(commanded_amount),
        )

    def abort_motion(self) -> None:
        self._pending = None

    def complete_motion(self, wall_sec: float, end_pose: OdomPose) -> MotionSegment:
        if self._pending is None:
            raise RuntimeError("no motion segment is pending")
        purpose, start_wall_sec, start_pose, amount = self._pending
        end_wall_sec = max(float(wall_sec), start_wall_sec + 1e-6)
        segment = MotionSegment(
            purpose=purpose,
            start_wall_sec=start_wall_sec,
            end_wall_sec=end_wall_sec,
            start_pose=start_pose,
            end_pose=end_pose,
            commanded_amount=amount,
        )
        self._pending = None
        self._segments.append(segment)
        if len(self._segments) > self.max_segments:
            del self._segments[: len(self._segments) - self.max_segments]
        self.add_snapshot(end_wall_sec, end_pose)
        return segment

    def pose_at(self, wall_sec: float) -> Optional[OdomPose]:
        stamp = float(wall_sec)
        if not math.isfinite(stamp):
            return None
        for segment in reversed(self._segments):
            if segment.contains(stamp):
                return segment.pose_at(stamp)
        if not self._snapshots:
            return None
        stamps = [item.wall_sec for item in self._snapshots]
        index = bisect.bisect_left(stamps, stamp)
        candidates: List[PoseSnapshot] = []
        if index < len(self._snapshots):
            candidates.append(self._snapshots[index])
        if index > 0:
            candidates.append(self._snapshots[index - 1])
        nearest = min(candidates, key=lambda item: abs(item.wall_sec - stamp))
        if abs(nearest.wall_sec - stamp) <= self.nearest_tolerance_sec:
            return nearest.pose
        return None

    def compensate_point(
        self,
        point_base_at_capture: Vector3,
        *,
        capture_wall_sec: float,
        current_pose: Optional[OdomPose] = None,
        forward_axis_sign: float = 1.0,
        lateral_axis_sign: float = 1.0,
    ) -> Optional[Vector3]:
        capture_pose = self.pose_at(capture_wall_sec)
        target_pose = current_pose or self.latest_pose
        if capture_pose is None or target_pose is None:
            return None
        point_odom = point_base_to_odom(
            point_base_at_capture,
            capture_pose,
            forward_axis_sign=forward_axis_sign,
            lateral_axis_sign=lateral_axis_sign,
        )
        return point_odom_to_base(
            point_odom,
            target_pose,
            forward_axis_sign=forward_axis_sign,
            lateral_axis_sign=lateral_axis_sign,
        )
