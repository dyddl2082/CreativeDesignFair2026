"""Fast camera-authoritative docking policy for MacRobot.

The legacy precision controller re-centred to a one-degree bearing tolerance
before every short translation and evaluated orientation before range.  That is
accurate but slow on a tracked base.  This module implements coarse-to-fine
hysteresis:

* far from the taught grasp point: tolerate small bearing error and translate;
* re-turn only for a large error or after a bounded translation streak;
* near the target: use the existing strict precision controller;
* engage object orientation only inside the final Cartesian band.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

from .alignment_core import AlignmentDecision, AlignmentErrors
from .precision_docking import choose_precision_docking_action, precision_errors


@dataclass(frozen=True)
class FastDockingResult:
    decision: AlignmentDecision
    phase: str  # coarse | final


def _positive(value: float, name: str) -> float:
    result = float(value)
    if not math.isfinite(result) or result <= 0.0:
        raise ValueError(f"{name} must be positive and finite")
    return result


def choose_fast_camera_docking_action(
    errors: AlignmentErrors,
    *,
    translation_streak: int,
    final_bearing_tolerance_deg: float,
    final_forward_tolerance_m: float,
    final_lateral_tolerance_m: float,
    final_turn_step_deg: float,
    final_move_step_m: float,
    coarse_bearing_tolerance_deg: float,
    emergency_bearing_tolerance_deg: float,
    coarse_lateral_tolerance_m: float,
    coarse_turn_step_deg: float,
    coarse_move_step_m: float,
    final_forward_band_m: float,
    max_translation_streak: int,
) -> FastDockingResult:
    """Select a coarse translation or strict final docking action."""

    final_bearing = _positive(final_bearing_tolerance_deg, "final bearing tolerance")
    final_forward = _positive(final_forward_tolerance_m, "final forward tolerance")
    final_lateral = _positive(final_lateral_tolerance_m, "final lateral tolerance")
    final_turn = _positive(final_turn_step_deg, "final turn step")
    final_move = _positive(final_move_step_m, "final move step")
    coarse_bearing = max(
        final_bearing,
        _positive(coarse_bearing_tolerance_deg, "coarse bearing tolerance"),
    )
    emergency_bearing = max(
        coarse_bearing,
        _positive(emergency_bearing_tolerance_deg, "emergency bearing tolerance"),
    )
    coarse_lateral = max(
        final_lateral,
        _positive(coarse_lateral_tolerance_m, "coarse lateral tolerance"),
    )
    coarse_turn = max(
        final_turn,
        _positive(coarse_turn_step_deg, "coarse turn step"),
    )
    coarse_move = max(
        final_move,
        _positive(coarse_move_step_m, "coarse move step"),
    )
    final_band = max(
        final_forward,
        _positive(final_forward_band_m, "final forward band"),
    )
    streak_limit = max(1, int(max_translation_streak))

    precise = precision_errors(errors)
    if errors.current.forward_m <= 0.0:
        return FastDockingResult(
            AlignmentDecision("reject", reason="object_not_in_front_half_plane"),
            "final",
        )

    coarse_phase = abs(precise.forward_error_m) > final_band
    if not coarse_phase:
        return FastDockingResult(
            choose_precision_docking_action(
                errors,
                bearing_tolerance_deg=final_bearing,
                forward_tolerance_m=final_forward,
                lateral_tolerance_m=final_lateral,
                max_turn_step_deg=final_turn,
                max_move_step_m=final_move,
            ),
            "final",
        )

    bearing = float(precise.bearing_error_deg)
    lateral = float(precise.lateral_error_m)
    streak = max(0, int(translation_streak))

    must_turn = abs(bearing) > emergency_bearing
    scheduled_turn = (
        streak >= streak_limit
        and (
            abs(bearing) > coarse_bearing
            or abs(lateral) > coarse_lateral
        )
    )
    if must_turn or scheduled_turn:
        amount = max(-coarse_turn, min(coarse_turn, bearing))
        return FastDockingResult(
            AlignmentDecision(
                "turn",
                amount=amount,
                reason=(
                    "fast_emergency_bearing_realign"
                    if must_turn
                    else "fast_periodic_heading_realign"
                ),
            ),
            "coarse",
        )

    amount = max(
        -coarse_move,
        min(coarse_move, float(precise.forward_error_m)),
    )
    return FastDockingResult(
        AlignmentDecision(
            "move",
            amount=amount,
            reason="fast_coarse_camera_translation",
        ),
        "coarse",
    )


def orientation_engagement_ready(
    errors: AlignmentErrors,
    *,
    maximum_forward_error_m: float,
    maximum_lateral_error_m: float,
    maximum_bearing_error_deg: float,
) -> bool:
    precise = precision_errors(errors)
    return (
        abs(precise.forward_error_m) <= abs(float(maximum_forward_error_m))
        and abs(precise.lateral_error_m) <= abs(float(maximum_lateral_error_m))
        and abs(precise.bearing_error_deg) <= abs(float(maximum_bearing_error_deg))
    )


def direct_axis_turn_deg(
    signed_axis_error_deg: float,
    *,
    gain: float = 1.0,
    maximum_step_deg: float = 6.0,
    minimum_step_deg: float = 0.75,
) -> float:
    """Map a base-frame axial yaw error directly to one bounded base turn."""

    error = float(signed_axis_error_deg)
    if not math.isfinite(error):
        raise ValueError("axis error must be finite")
    maximum = _positive(maximum_step_deg, "maximum axis turn")
    minimum = min(maximum, _positive(minimum_step_deg, "minimum axis turn"))
    command = error * float(gain)
    command = max(-maximum, min(maximum, command))
    if abs(command) < minimum and abs(error) > 1e-9:
        command = math.copysign(minimum, command if command != 0.0 else error)
    return command
