"""Depth-only camera alignment policy for MacRobot.

This module intentionally ignores object orientation during base alignment.
Only the current base_link forward depth is compared with the taught forward
reference.  Lateral and bearing values are optional *safety guards*; they are
never converted into a turn command.

Coordinate convention:
- +x: robot forward
- +y: robot left
- positive MOVE amount: robot forward

For a stationary object and a straight robot move ``d`` the next observed
forward depth is approximated by ``x_next = x_current - d``.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

PATCH_MARKER = "macrobot_depth_only_grasp_v7_1"


@dataclass(frozen=True)
class DepthOnlyPlan:
    reached: bool
    blocked: bool
    reason: str
    current_depth_m: float
    target_depth_m: float
    depth_error_m: float
    current_lateral_m: float
    reference_lateral_m: float
    lateral_delta_m: float
    bearing_deg: float
    progress: float
    command_m: float
    predicted_depth_m: float
    predicted_range_m: float


def _finite(value: float, name: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _positive(value: float, name: str, *, allow_zero: bool = False) -> float:
    result = _finite(value, name)
    if allow_zero:
        if result < 0.0:
            raise ValueError(f"{name} must be non-negative")
    elif result <= 0.0:
        raise ValueError(f"{name} must be positive")
    return result


def _blocked_plan(
    *,
    reason: str,
    current_depth_m: float,
    target_depth_m: float,
    current_lateral_m: float,
    reference_lateral_m: float,
) -> DepthOnlyPlan:
    depth_error = current_depth_m - target_depth_m
    lateral_delta = current_lateral_m - reference_lateral_m
    bearing = math.degrees(math.atan2(current_lateral_m, current_depth_m))
    return DepthOnlyPlan(
        reached=False,
        blocked=True,
        reason=reason,
        current_depth_m=current_depth_m,
        target_depth_m=target_depth_m,
        depth_error_m=depth_error,
        current_lateral_m=current_lateral_m,
        reference_lateral_m=reference_lateral_m,
        lateral_delta_m=lateral_delta,
        bearing_deg=bearing,
        progress=0.0,
        command_m=0.0,
        predicted_depth_m=current_depth_m,
        predicted_range_m=math.hypot(current_depth_m, current_lateral_m),
    )


def choose_depth_only_plan(
    current_depth_m: float,
    target_depth_m: float,
    *,
    current_lateral_m: float = 0.0,
    reference_lateral_m: float = 0.0,
    forward_tolerance_m: float = 0.008,
    coarse_progress: float = 0.90,
    near_progress: float = 0.65,
    near_error_m: float = 0.040,
    maximum_forward_step_m: float = 0.080,
    maximum_reverse_step_m: float = 0.040,
    minimum_move_m: float = 0.004,
    minimum_object_forward_m: float = 0.120,
    allow_reverse: bool = True,
    lateral_guard_enabled: bool = True,
    maximum_lateral_delta_m: float = 0.080,
    maximum_abs_bearing_deg: float = 28.0,
) -> DepthOnlyPlan:
    """Choose one bounded straight MOVE command.

    ``depth_error_m`` is ``current - target``.  A positive error therefore
    produces a positive forward move; a negative error requires reverse.
    Orientation is deliberately absent from the API.
    """

    current = _finite(current_depth_m, "current_depth_m")
    target = _finite(target_depth_m, "target_depth_m")
    lateral = _finite(current_lateral_m, "current_lateral_m")
    reference_lateral = _finite(reference_lateral_m, "reference_lateral_m")
    tolerance = _positive(forward_tolerance_m, "forward_tolerance_m")
    coarse = _positive(coarse_progress, "coarse_progress")
    near = _positive(near_progress, "near_progress")
    near_error = _positive(near_error_m, "near_error_m")
    max_forward = _positive(
        maximum_forward_step_m,
        "maximum_forward_step_m",
    )
    max_reverse = _positive(
        maximum_reverse_step_m,
        "maximum_reverse_step_m",
    )
    minimum_move = _positive(minimum_move_m, "minimum_move_m", allow_zero=True)
    minimum_forward = _positive(
        minimum_object_forward_m,
        "minimum_object_forward_m",
    )
    max_lateral_delta = _positive(
        maximum_lateral_delta_m,
        "maximum_lateral_delta_m",
        allow_zero=True,
    )
    max_bearing = _positive(
        maximum_abs_bearing_deg,
        "maximum_abs_bearing_deg",
    )

    if current <= 0.0:
        return _blocked_plan(
            reason="object_not_in_front_half_plane",
            current_depth_m=current,
            target_depth_m=target,
            current_lateral_m=lateral,
            reference_lateral_m=reference_lateral,
        )
    if target < minimum_forward:
        return _blocked_plan(
            reason="taught_target_depth_below_minimum_object_forward",
            current_depth_m=current,
            target_depth_m=target,
            current_lateral_m=lateral,
            reference_lateral_m=reference_lateral,
        )

    error = current - target
    lateral_delta = lateral - reference_lateral
    bearing = math.degrees(math.atan2(lateral, current))

    # These are guards only.  No turn/lateral correction is generated.
    if lateral_guard_enabled and abs(lateral_delta) > max_lateral_delta:
        return _blocked_plan(
            reason="lateral_delta_outside_depth_only_safety_guard",
            current_depth_m=current,
            target_depth_m=target,
            current_lateral_m=lateral,
            reference_lateral_m=reference_lateral,
        )
    if lateral_guard_enabled and abs(bearing) > max_bearing:
        return _blocked_plan(
            reason="bearing_outside_depth_only_safety_guard",
            current_depth_m=current,
            target_depth_m=target,
            current_lateral_m=lateral,
            reference_lateral_m=reference_lateral,
        )

    if abs(error) <= tolerance:
        return DepthOnlyPlan(
            reached=True,
            blocked=False,
            reason="forward_depth_within_tolerance",
            current_depth_m=current,
            target_depth_m=target,
            depth_error_m=error,
            current_lateral_m=lateral,
            reference_lateral_m=reference_lateral,
            lateral_delta_m=lateral_delta,
            bearing_deg=bearing,
            progress=0.0,
            command_m=0.0,
            predicted_depth_m=current,
            predicted_range_m=math.hypot(current, lateral),
        )

    if error < 0.0 and not bool(allow_reverse):
        return _blocked_plan(
            reason="reverse_required_but_disabled",
            current_depth_m=current,
            target_depth_m=target,
            current_lateral_m=lateral,
            reference_lateral_m=reference_lateral,
        )

    progress = near if abs(error) <= near_error else coarse
    raw_command = progress * error
    if raw_command >= 0.0:
        command = min(raw_command, max_forward)
    else:
        command = max(raw_command, -max_reverse)

    # A forward move must not predict an object depth below the hard limit.
    if command > 0.0:
        command = min(command, max(0.0, current - minimum_forward))

    if abs(command) <= 1e-12:
        return _blocked_plan(
            reason="no_safe_depth_only_motion_available",
            current_depth_m=current,
            target_depth_m=target,
            current_lateral_m=lateral,
            reference_lateral_m=reference_lateral,
        )

    if abs(command) < minimum_move:
        # The tolerance is normally larger than minimum_move.  If custom
        # parameters violate that relation, never overshoot the requested
        # residual merely to satisfy a minimum step.
        command = math.copysign(min(abs(error), minimum_move), command)
        if command > 0.0:
            command = min(command, max(0.0, current - minimum_forward))
        if abs(command) <= 1e-12:
            return _blocked_plan(
                reason="residual_smaller_than_safe_minimum_move",
                current_depth_m=current,
                target_depth_m=target,
                current_lateral_m=lateral,
                reference_lateral_m=reference_lateral,
            )

    predicted_depth = current - command
    predicted_range = math.hypot(predicted_depth, lateral)
    return DepthOnlyPlan(
        reached=False,
        blocked=False,
        reason=(
            "bounded_forward_depth_correction"
            if command > 0.0
            else "bounded_reverse_depth_correction"
        ),
        current_depth_m=current,
        target_depth_m=target,
        depth_error_m=error,
        current_lateral_m=lateral,
        reference_lateral_m=reference_lateral,
        lateral_delta_m=lateral_delta,
        bearing_deg=bearing,
        progress=progress,
        command_m=command,
        predicted_depth_m=predicted_depth,
        predicted_range_m=predicted_range,
    )


def simulate_depth_loop(
    current_depth_m: float,
    target_depth_m: float,
    *,
    move_scale: float = 1.0,
    maximum_steps: int = 20,
    planner_kwargs: dict | None = None,
) -> tuple[bool, int, float]:
    """Pure deterministic helper used by regression tests."""

    current = _finite(current_depth_m, "current_depth_m")
    scale = _positive(move_scale, "move_scale")
    kwargs = dict(planner_kwargs or {})
    for index in range(max(1, int(maximum_steps))):
        plan = choose_depth_only_plan(current, target_depth_m, **kwargs)
        if plan.reached:
            return True, index, current
        if plan.blocked or abs(plan.command_m) <= 1e-12:
            return False, index, current
        current -= plan.command_m * scale
    final = choose_depth_only_plan(current, target_depth_m, **kwargs)
    return final.reached, int(maximum_steps), current
