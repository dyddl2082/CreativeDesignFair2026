"""Reduced MacRobot arm and gripper kinematics.

The current physical conventions are intentionally explicit:

* ``q1`` / legacy ROS name ``arm_lift_joint`` is the **left-servo arm-tilt**
  coordinate.  Positive ``q1`` tilts the arm toward the robot front.
* ``q2`` / legacy ROS name ``wrist_pitch_joint`` is the relative coordinate
  used by the right rear-height mechanism.  The right driven-gear angle is
  ``rear_lift_angle = q1 + q2``.  Positive values lift the rear linkage.
* ``q3`` / ``gripper_joint`` is 0 rad when open and increases while closing.
  A 1:2 external gear pair means q3=pi/2 corresponds to 180 degrees at the
  gripper servo shaft.

The old ROS joint names are retained to avoid breaking launch files and saved
profiles.  Their physical meanings above are the authoritative definitions.
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

    # Nominal open-gripper grasp center, expressed in the rear-link/tool frame
    # at q3=0.
    tool_offset_x: float = -0.184756
    tool_offset_z: float = -0.006000
    tool_y: float = 0.064500

    # Each gripper four-bar side link is 30 mm. Closing shifts the nominal
    # jaw-center slightly along local tool X.
    gripper_link_length: float = 0.03000
    gripper_base_separation: float = 0.01000


@dataclass(frozen=True)
class JointLimits:
    # Legacy field names are retained for configuration compatibility.
    # arm_lift_* constrains q1 = forward arm tilt.
    arm_lift_min: float = -1.0
    arm_lift_max: float = 1.0

    # wrist_pitch_* constrains q2 = relative rear-lift coordinate.
    wrist_pitch_min: float = -1.30
    wrist_pitch_max: float = 1.30

    # tool_pitch_* constrains the absolute right driven/rear-lift angle q1+q2.
    tool_pitch_min: float = -2.0
    tool_pitch_max: float = 2.0

    four_bar_margin: float = math.radians(10.0)

    # q3=0 open; q3=pi/2 closed for a 180-degree servo through 1:2 gearing.
    gripper_min: float = 0.0
    gripper_max: float = math.pi / 2.0

    def contains(self, q1: float, q2: float, q3: float = 0.0) -> bool:
        rear_lift_angle = q1 + q2
        return (
            self.arm_lift_min <= q1 <= self.arm_lift_max
            and self.wrist_pitch_min <= q2 <= self.wrist_pitch_max
            and self.tool_pitch_min <= rear_lift_angle <= self.tool_pitch_max
            and abs(q2) <= (math.pi / 2.0 - self.four_bar_margin)
            and self.gripper_min <= q3 <= self.gripper_max
        )


@dataclass(frozen=True)
class ToolPose2D:
    x: float
    y: float
    z: float
    # Rotation about the URDF +Y axis. Since positive logical rear-lift is
    # defined about -Y, the published +Y pitch is negative rear_lift_angle.
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
        """Return the grasp-center X/Z offset in the rear/tool frame.

        Positive q3 closes the gripper. This is the sign-inverted form of the
        previous model, where negative q3 represented closing.
        """
        g = self.geometry
        return (
            g.tool_offset_x + g.gripper_link_length * math.sin(q3),
            g.tool_offset_z,
        )

    def forward(self, q1: float, q2: float, q3: float = 0.0) -> ToolPose2D:
        """Compute the nominal grasp center from the three logical joints.

        Positive q1 rotates the main arm toward robot front (-X). Positive
        rear_lift_angle=q1+q2 raises the right/rear linkage. Both logical arm
        rotations are therefore represented about the physical -Y direction.
        """
        g = self.geometry
        rear_lift_angle = q1 + q2
        offset_x, offset_z = self.effective_tool_offset(q3)

        x = (
            g.pivot_x
            - g.main_link_length * math.sin(q1)
            + offset_x * math.cos(rear_lift_angle)
            - offset_z * math.sin(rear_lift_angle)
        )
        z = (
            g.pivot_z
            + g.main_link_length * math.cos(q1)
            + offset_x * math.sin(rear_lift_angle)
            + offset_z * math.cos(rear_lift_angle)
        )
        return ToolPose2D(
            x=x,
            y=g.tool_y,
            z=z,
            pitch=-rear_lift_angle,
        )

    def inverse(
        self,
        x: float,
        z: float,
        seed: Optional[Tuple[float, float]] = None,
        seed_weight: float = 0.001,
        gripper_q: float = 0.0,
    ) -> List[IKSolution]:
        """Return all bounded planar IK branches for the corrected signs."""
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
            # Standard x-z plane angles:
            # a1 = pi/2 + q1
            # a2 = gamma + rear_lift_angle
            a1 = math.atan2(pz, px) - math.atan2(
                l2 * math.sin(delta), l1 + l2 * math.cos(delta)
            )
            q1 = normalize_angle(a1 - math.pi / 2.0)
            rear_lift_angle = normalize_angle(a1 + delta - gamma)
            q2 = normalize_angle(rear_lift_angle - q1)

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
        lift_servo_multiplier: float = 2.0,
        tilt_servo_multiplier: float = -2.0,
        gripper_servo_multiplier: float = -2.0,
    ) -> dict[str, float]:
        """Map logical coordinates to Fusion-exported tree joints.

        Arm conventions:
          * left servo CCW => positive q1 => arm tilts forward;
          * right servo CW => positive (q1+q2) => rear linkage rises;
          * external 1:2 gear pairs reverse physical direction.

        Gripper convention:
          * q3=0 open and positive q3 closes;
          * the servo turns CCW by 2*q3, while the driven gear counter-rotates.
          * ``gripper_servo_joint`` uses a -Z URDF axis, hence its joint
            coordinate is -2*q3 although the physical servo rotation is CCW.
        """
        rear_lift_angle = q1 + q2
        return {
            'lift_servo': lift_servo_multiplier * q1,
            'tilt_servo': tilt_servo_multiplier * rear_lift_angle,
            'lift_ratio': q1,
            'tilt_ratio': rear_lift_angle,
            'rear_passive': q2,
            'top_passive': q2,
            'gripper_servo': gripper_servo_multiplier * q3,
            'gripper_left_gear': -q3,
            'gripper_right_gear': q3,
            'gripper_left_addition': -q3,
            'gripper_right_addition': q3,
            'gripper_left_clamp': q3,
            'gripper_right_clamp': -q3,
        }
