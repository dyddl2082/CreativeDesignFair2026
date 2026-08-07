"""Reduced MacRobot arm and gripper kinematics.

The physical arm contains a geared four-bar linkage.  It is represented by two
logical arm coordinates plus one logical gripper coordinate:

* q1: ``arm_lift_joint``
* q2: ``wrist_pitch_joint`` (relative; absolute wrist pitch is q1 + q2)
* q3: ``gripper_joint`` (0 rad is fully open; negative closes)

The full Fusion visual joints are generated from these logical coordinates.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import List, Optional, Tuple


def normalize_angle(angle: float) -> float:
    return math.atan2(math.sin(angle), math.cos(angle))


@dataclass(frozen=True)
class ArmGeometry:
    # Main four-bar pivot in base_link.
    pivot_x: float = 0.02095
    pivot_y: float = 0.06340
    pivot_z: float = 0.064595

    # Main parallel link length.
    main_link_length: float = 0.10000

    # Nominal open-gripper grasp center, expressed in the wrist frame at q3=0.
    # Recovered from the midpoint of the two clamp collision centroids.
    tool_offset_x: float = -0.184756
    tool_offset_z: float = -0.006000
    tool_y: float = 0.064500

    # Each gripper four-bar side link is 30 mm.  Closing shifts the jaw-center
    # slightly along the local tool X direction.
    gripper_link_length: float = 0.03000
    gripper_base_separation: float = 0.01000


@dataclass(frozen=True)
class JointLimits:
    arm_lift_min: float = -1.0
    arm_lift_max: float = 1.0
    wrist_pitch_min: float = -1.30
    wrist_pitch_max: float = 1.30
    tool_pitch_min: float = -2.0
    tool_pitch_max: float = 2.0
    four_bar_margin: float = math.radians(10.0)
    gripper_min: float = -1.25
    gripper_max: float = 0.0

    def contains(self, q1: float, q2: float, q3: float = 0.0) -> bool:
        tool_pitch = q1 + q2
        return (
            self.arm_lift_min <= q1 <= self.arm_lift_max
            and self.wrist_pitch_min <= q2 <= self.wrist_pitch_max
            and self.tool_pitch_min <= tool_pitch <= self.tool_pitch_max
            and abs(q2) <= (math.pi / 2.0 - self.four_bar_margin)
            and self.gripper_min <= q3 <= self.gripper_max
        )


@dataclass(frozen=True)
class ToolPose2D:
    x: float
    y: float
    z: float
    pitch: float


@dataclass(frozen=True)
class IKSolution:
    q1: float
    q2: float
    position_error: float
    seed_distance: float


class MacRobotArmModel:
    """Kinematics for the reduced arm and the full visual linkage mapping."""

    def __init__(
        self,
        geometry: ArmGeometry = ArmGeometry(),
        limits: JointLimits = JointLimits(),
    ) -> None:
        self.geometry = geometry
        self.limits = limits

    def effective_tool_offset(self, q3: float = 0.0) -> Tuple[float, float]:
        """Return the grasp-center X/Z offset in the wrist frame.

        The jaw-center moves toward the robot by ``-L*sin(q3)`` as the
        symmetric gripper closes with negative q3.  The nominal CAD/Fusion pose corresponds to q3=0.
        """
        g = self.geometry
        return (
            g.tool_offset_x - g.gripper_link_length * math.sin(q3),
            g.tool_offset_z,
        )

    def forward(self, q1: float, q2: float, q3: float = 0.0) -> ToolPose2D:
        g = self.geometry
        pitch = q1 + q2
        offset_x, offset_z = self.effective_tool_offset(q3)

        x = (
            g.pivot_x
            + g.main_link_length * math.sin(q1)
            + offset_x * math.cos(pitch)
            + offset_z * math.sin(pitch)
        )
        z = (
            g.pivot_z
            + g.main_link_length * math.cos(q1)
            - offset_x * math.sin(pitch)
            + offset_z * math.cos(pitch)
        )
        return ToolPose2D(x=x, y=g.tool_y, z=z, pitch=pitch)

    def inverse(
        self,
        x: float,
        z: float,
        seed: Optional[Tuple[float, float]] = None,
        seed_weight: float = 0.001,
        gripper_q: float = 0.0,
    ) -> List[IKSolution]:
        """Return all bounded planar IK branches.

        The fixed wrist-to-grasp vector may have both X and Z components.  It is
        represented as an equivalent second link with a constant angular offset.
        """
        g = self.geometry
        px = x - g.pivot_x
        pz = z - g.pivot_z
        l1 = g.main_link_length
        offset_x, offset_z = self.effective_tool_offset(gripper_q)
        l2 = math.hypot(offset_x, offset_z)
        if l2 <= 1e-12:
            return []
        gamma = math.atan2(offset_z, offset_x)

        radius_sq = px * px + pz * pz
        cosine_delta = (radius_sq - l1 * l1 - l2 * l2) / (2.0 * l1 * l2)
        tolerance = 1e-9
        if cosine_delta < -1.0 - tolerance or cosine_delta > 1.0 + tolerance:
            return []
        cosine_delta = max(-1.0, min(1.0, cosine_delta))
        delta_abs = math.acos(cosine_delta)

        solutions: List[IKSolution] = []
        for delta in (delta_abs, -delta_abs):
            alpha = math.atan2(pz, px) - math.atan2(
                l2 * math.sin(delta), l1 + l2 * math.cos(delta)
            )
            q1 = normalize_angle(math.pi / 2.0 - alpha)
            q2 = normalize_angle(gamma - math.pi / 2.0 - delta)
            if not self.limits.contains(q1, q2, gripper_q):
                continue

            pose = self.forward(q1, q2, gripper_q)
            error = math.hypot(pose.x - x, pose.z - z)
            if seed is None:
                seed_distance = 0.0
            else:
                seed_distance = math.hypot(
                    normalize_angle(q1 - seed[0]),
                    normalize_angle(q2 - seed[1]),
                )
            solutions.append(
                IKSolution(
                    q1=q1,
                    q2=q2,
                    position_error=error,
                    seed_distance=seed_distance,
                )
            )

        solutions.sort(
            key=lambda s: (
                s.position_error + seed_weight * s.seed_distance,
                s.seed_distance,
            )
        )
        return solutions

    def gripper_gap(self, q3: float) -> float:
        """Approximate inner jaw-frame separation in metres."""
        g = self.geometry
        return g.gripper_base_separation + 2.0 * g.gripper_link_length * math.cos(q3)

    @staticmethod
    def full_visual_joint_positions(
        q1: float,
        q2: float,
        q3: float = 0.0,
        lift_servo_multiplier: float = -2.0,
        tilt_servo_multiplier: float = 2.0,
        gripper_servo_multiplier: float = 2.0,
    ) -> dict[str, float]:
        """Map logical joints to the Fusion-exported tree joint coordinates.

        Arm:
          * 20:40 external gear pairs -> servo magnitude is 2x driven gear.
          * passive joints preserve the parallelogram four-bar.

        Gripper:
          * q3 is the left driven-gear angle (q3=0 is the CAD open pose).
          * the right gear counter-rotates 1:1.
          * the two side links follow their driven gears.
          * clamp passive joints counter-rotate, preserving parallel jaws.
        """
        tool_pitch = q1 + q2
        return {
            'lift_servo': lift_servo_multiplier * q1,
            'tilt_servo': tilt_servo_multiplier * tool_pitch,
            'lift_ratio': q1,
            'tilt_ratio': -tool_pitch,
            'rear_passive': -q2,
            'top_passive': -q2,
            'gripper_servo': gripper_servo_multiplier * q3,
            'gripper_left_gear': q3,
            'gripper_right_gear': -q3,
            'gripper_left_addition': q3,
            'gripper_right_addition': -q3,
            'gripper_left_clamp': -q3,
            'gripper_right_clamp': q3,
        }
