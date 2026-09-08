"""Pure legacy-style 2D orientation alignment planner.

This controller intentionally does *not* use 3D face normals.  It keeps the
current camera/depth/localization stack, aligns position first, then treats the
2D image/patch orientation as a soft hint.  A bounded number of small
orientation turns is allowed; orientation can never block grasp forever.
"""

from __future__ import annotations

from dataclasses import dataclass
import math


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def wrap_deg_180(value: float) -> float:
    """Wrap a directed angle to [-180, 180)."""
    result = (float(value) + 180.0) % 360.0 - 180.0
    if result == 180.0:
        return -180.0
    return result


def axial_error_deg(current_deg: float, reference_deg: float) -> float:
    """Return the shortest signed error for a 180-degree symmetric axis.

    Positive means the object axis in base coordinates is CCW from the taught
    axis.  Because a positive robot yaw rotates the observed object axis by the
    negative of that yaw, the correct robot yaw command has the *same* sign as
    this error.
    """
    current = float(current_deg)
    reference = float(reference_deg)
    if not (math.isfinite(current) and math.isfinite(reference)):
        return math.nan
    return (current - reference + 90.0) % 180.0 - 90.0


@dataclass(frozen=True)
class Legacy2DPlan:
    stage: str
    reached: bool
    blocked: bool
    reason: str
    command_kind: str | None
    command_amount: float
    command_yaw_deg: float
    current_forward_m: float
    current_lateral_m: float
    reference_forward_m: float
    reference_lateral_m: float
    forward_error_m: float
    lateral_error_m: float
    bearing_error_deg: float
    orientation_error_deg: float
    orientation_quality: float
    orientation_corrections_used: int


def choose_legacy_2d_plan(
    current_point: tuple[float, float],
    reference_point: tuple[float, float],
    *,
    current_orientation_deg: float | None,
    reference_orientation_deg: float | None,
    orientation_quality: float,
    orientation_corrections_used: int,
    bearing_tolerance_deg: float = 6.0,
    forward_tolerance_m: float = 0.010,
    lateral_tolerance_m: float = 0.015,
    position_turn_max_deg: float = 10.0,
    position_move_max_m: float = 0.050,
    position_progress: float = 0.85,
    allow_reverse: bool = True,
    reverse_max_m: float = 0.020,
    orientation_enabled: bool = True,
    orientation_trigger_deg: float = 18.0,
    orientation_turn_max_deg: float = 7.0,
    orientation_min_quality: float = 0.35,
    orientation_max_corrections: int = 2,
) -> Legacy2DPlan:
    cx, cy = map(float, current_point)
    rx, ry = map(float, reference_point)
    values = (cx, cy, rx, ry)
    if not all(math.isfinite(value) for value in values):
        raise ValueError("current/reference points must be finite")
    if cx <= 0.0 or rx <= 0.0:
        return Legacy2DPlan(
            "blocked", False, True, "object_not_in_front_half_plane", None, 0.0, 0.0,
            cx, cy, rx, ry, cx-rx, cy-ry, math.nan, math.nan,
            float(orientation_quality), int(orientation_corrections_used),
        )

    current_bearing = math.degrees(math.atan2(cy, cx))
    reference_bearing = math.degrees(math.atan2(ry, rx))
    bearing_error = wrap_deg_180(current_bearing - reference_bearing)
    forward_error = cx - rx
    lateral_error = cy - ry

    orientation_error = math.nan
    if current_orientation_deg is not None and reference_orientation_deg is not None:
        orientation_error = axial_error_deg(current_orientation_deg, reference_orientation_deg)

    common = dict(
        current_forward_m=cx,
        current_lateral_m=cy,
        reference_forward_m=rx,
        reference_lateral_m=ry,
        forward_error_m=forward_error,
        lateral_error_m=lateral_error,
        bearing_error_deg=bearing_error,
        orientation_error_deg=orientation_error,
        orientation_quality=float(orientation_quality),
        orientation_corrections_used=int(orientation_corrections_used),
    )

    # Old-style priority: put the object back near the taught image ray first.
    if abs(bearing_error) > float(bearing_tolerance_deg):
        yaw = clamp(bearing_error, -abs(position_turn_max_deg), abs(position_turn_max_deg))
        return Legacy2DPlan(
            stage="position_bearing",
            reached=False,
            blocked=False,
            reason="bearing_outside_tolerance",
            command_kind="turn",
            command_amount=0.0,
            command_yaw_deg=yaw,
            **common,
        )

    # Then recover the taught forward depth/range.  Do not chase encoder-perfect
    # distance; every move is followed by a fresh RGB-D observation.
    if abs(forward_error) > float(forward_tolerance_m):
        command = float(position_progress) * forward_error
        if command >= 0.0:
            command = min(command, abs(float(position_move_max_m)))
        else:
            if not allow_reverse:
                return Legacy2DPlan(
                    stage="blocked",
                    reached=False,
                    blocked=True,
                    reason="reverse_required_but_disabled",
                    command_kind=None,
                    command_amount=0.0,
                    command_yaw_deg=0.0,
                    **common,
                )
            command = max(command, -abs(float(reverse_max_m)))
        return Legacy2DPlan(
            stage="position_range",
            reached=False,
            blocked=False,
            reason="forward_depth_outside_tolerance",
            command_kind="move",
            command_amount=command,
            command_yaw_deg=0.0,
            **common,
        )

    # A small residual lateral error is tolerated if bearing and depth are good.
    # A larger one is not corrected with an invented sideways motion; the robot
    # simply reports blocked so the operator can reposition if needed.
    if abs(lateral_error) > float(lateral_tolerance_m):
        return Legacy2DPlan(
            stage="blocked",
            reached=False,
            blocked=True,
            reason="lateral_error_not_correctable_without_large_pose_motion",
            command_kind=None,
            command_amount=0.0,
            command_yaw_deg=0.0,
            **common,
        )

    # Legacy behavior: orientation is advisory.  Ignore low-quality/unavailable
    # orientation, and never spend more than a tiny fixed correction budget.
    if not orientation_enabled:
        return Legacy2DPlan(
            stage="reached", reached=True, blocked=False,
            reason="position_reached_orientation_disabled", command_kind=None,
            command_amount=0.0, command_yaw_deg=0.0, **common,
        )
    if not math.isfinite(orientation_error):
        return Legacy2DPlan(
            stage="reached", reached=True, blocked=False,
            reason="position_reached_orientation_unavailable_soft_accept", command_kind=None,
            command_amount=0.0, command_yaw_deg=0.0, **common,
        )
    if float(orientation_quality) < float(orientation_min_quality):
        return Legacy2DPlan(
            stage="reached", reached=True, blocked=False,
            reason="position_reached_orientation_quality_low_soft_accept", command_kind=None,
            command_amount=0.0, command_yaw_deg=0.0, **common,
        )
    if abs(orientation_error) <= float(orientation_trigger_deg):
        return Legacy2DPlan(
            stage="reached", reached=True, blocked=False,
            reason="position_reached_2d_orientation_inside_soft_band", command_kind=None,
            command_amount=0.0, command_yaw_deg=0.0, **common,
        )
    if int(orientation_corrections_used) >= max(0, int(orientation_max_corrections)):
        return Legacy2DPlan(
            stage="reached", reached=True, blocked=False,
            reason="position_reached_2d_orientation_budget_exhausted_soft_accept", command_kind=None,
            command_amount=0.0, command_yaw_deg=0.0, **common,
        )

    yaw = clamp(orientation_error, -abs(orientation_turn_max_deg), abs(orientation_turn_max_deg))
    return Legacy2DPlan(
        stage="orientation_soft",
        reached=False,
        blocked=False,
        reason="2d_orientation_large_apply_small_bounded_turn",
        command_kind="turn",
        command_amount=0.0,
        command_yaw_deg=yaw,
        **common,
    )
