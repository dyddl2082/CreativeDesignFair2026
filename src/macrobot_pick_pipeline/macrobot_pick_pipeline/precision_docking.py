"""Pure precision-docking helpers for MacRobot visual grasp alignment.

The stored grasp reference is a point in ``base_link``.  The old controller
matched bearing plus Euclidean planar range.  That is adequate for coarse
alignment, but the tracked chassis directly actuates forward translation; the
quantity that should drive ``MOVE_CM`` is therefore the forward-coordinate
error after bearing has been corrected.  Final readiness additionally checks
the lateral residual so a loose angular tolerance cannot hide a centimetre
scale miss at the gripper.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

from .alignment_core import AlignmentDecision, AlignmentErrors


@dataclass(frozen=True)
class PrecisionDockingErrors:
    bearing_error_deg: float
    forward_error_m: float
    lateral_error_m: float
    range_error_m: float
    planar_position_error_m: float


def precision_errors(errors: AlignmentErrors) -> PrecisionDockingErrors:
    forward_error = float(errors.current.forward_m - errors.reference.forward_m)
    lateral_error = float(errors.current.lateral_m - errors.reference.lateral_m)
    return PrecisionDockingErrors(
        bearing_error_deg=float(errors.bearing_error_deg),
        forward_error_m=forward_error,
        lateral_error_m=lateral_error,
        range_error_m=float(errors.range_error_m),
        planar_position_error_m=math.hypot(forward_error, lateral_error),
    )


def choose_precision_docking_action(
    errors: AlignmentErrors,
    *,
    bearing_tolerance_deg: float,
    forward_tolerance_m: float,
    lateral_tolerance_m: float,
    max_turn_step_deg: float,
    max_move_step_m: float,
) -> AlignmentDecision:
    """Choose one closed-loop docking action.

    Order is deliberately fixed:

    1. centre the object direction;
    2. move only along the base forward axis;
    3. verify the residual lateral displacement;
    4. declare aligned only when both Cartesian components are inside bounds.

    A positive move means the object is farther forward than the taught
    reference and the chassis should move forward.  Every physical command is
    followed by a fresh camera observation in the runtime node.
    """

    values = (
        bearing_tolerance_deg,
        forward_tolerance_m,
        lateral_tolerance_m,
        max_turn_step_deg,
        max_move_step_m,
    )
    if not all(math.isfinite(float(value)) and float(value) > 0.0 for value in values):
        raise ValueError("precision docking limits must be positive and finite")
    if errors.current.forward_m <= 0.0:
        return AlignmentDecision("reject", reason="object_not_in_front_half_plane")

    precise = precision_errors(errors)
    if abs(precise.bearing_error_deg) > float(bearing_tolerance_deg):
        amount = max(
            -float(max_turn_step_deg),
            min(float(max_turn_step_deg), precise.bearing_error_deg),
        )
        return AlignmentDecision("turn", amount=amount, reason="precision_bearing_error")

    if abs(precise.forward_error_m) > float(forward_tolerance_m):
        amount = max(
            -float(max_move_step_m),
            min(float(max_move_step_m), precise.forward_error_m),
        )
        return AlignmentDecision("move", amount=amount, reason="precision_forward_error")

    if abs(precise.lateral_error_m) > float(lateral_tolerance_m):
        # Once forward distance is correct, a residual y error is best removed
        # by a very small yaw correction and another visual re-observation.
        # The atan2 form naturally scales the command with target distance.
        denominator = max(abs(float(errors.current.forward_m)), 0.05)
        correction = math.degrees(math.atan2(precise.lateral_error_m, denominator))
        if abs(correction) < 0.25:
            correction = math.copysign(0.25, precise.lateral_error_m)
        amount = max(
            -float(max_turn_step_deg),
            min(float(max_turn_step_deg), correction),
        )
        return AlignmentDecision("turn", amount=amount, reason="precision_lateral_error")

    return AlignmentDecision("aligned", reason="within_precision_cartesian_tolerance")
