"""Pure helpers for active object-orientation recovery.

DINOv2 patch localization reports an *axial* image-plane orientation: 0 and
180 degrees describe the same axis.  The controller therefore works modulo
180 degrees and treats orientation as a visual feedback signal rather than as
wheel-odometry truth.

A non-holonomic base cannot independently change object bearing and viewpoint
with an in-place turn alone.  The runtime node uses these helpers to perform a
small turn, take a fresh observation, then make at most one short translation
before observing again.  The next probe direction is chosen by measured
improvement, so an initially wrong sign assumption self-corrects.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Optional, Sequence

from .orientation_domain import signed_axial_axis_error_deg


def signed_axial_error_deg(current_deg: float, reference_deg: float) -> float:
    """Return the signed shortest axial error in ``[-90, 90)`` degrees."""

    current = float(current_deg)
    reference = float(reference_deg)
    if not math.isfinite(current) or not math.isfinite(reference):
        raise ValueError("orientation angles must be finite")
    return ((current - reference + 90.0) % 180.0) - 90.0


@dataclass(frozen=True)
class OrientationAssessment:
    state: str  # aligned | quality_low | angle_mismatch
    signed_error_deg: float
    absolute_error_deg: float
    quality: float
    cost: float
    reason: str = ""
    comparison_mode: str = "scalar_axial_angle"

    @property
    def aligned(self) -> bool:
        return self.state == "aligned"


def assess_orientation(
    *,
    current_deg: float,
    current_quality: float,
    reference_deg: float,
    minimum_quality: float,
    tolerance_deg: float,
    current_axis_base: Optional[Sequence[float]] = None,
    reference_axis_base: Optional[Sequence[float]] = None,
    current_coordinate_frame: str = "",
    reference_coordinate_frame: str = "",
    current_semantics: str = "",
    reference_semantics: str = "",
) -> OrientationAssessment:
    """Classify one visual orientation observation and compute a hill-climb cost."""

    quality = float(current_quality)
    minimum = float(minimum_quality)
    tolerance = float(tolerance_deg)
    if not math.isfinite(quality):
        quality = 0.0
    if not 0.0 <= minimum <= 1.0:
        raise ValueError("minimum_quality must be within [0, 1]")
    if tolerance <= 0.0 or not math.isfinite(tolerance):
        raise ValueError("tolerance_deg must be positive and finite")

    current_frame = str(current_coordinate_frame).strip()
    reference_frame = str(reference_coordinate_frame).strip()
    current_kind = str(current_semantics).strip()
    reference_kind = str(reference_semantics).strip()
    domain_declared = bool(
        current_frame or current_kind or reference_frame or reference_kind
    )
    domain_compatible = (
        not domain_declared
        or (
            bool(current_frame)
            and bool(current_kind)
            and current_frame == reference_frame
            and current_kind == reference_kind
        )
    )
    if not domain_compatible:
        quality = 0.0
        error = 0.0
        absolute = 0.0
        cost = 2.0
        return OrientationAssessment(
            "quality_low",
            error,
            absolute,
            quality,
            cost,
            reason=(
                "orientation_domain_mismatch: "
                f"current={current_frame or '?'}:{current_kind or '?'}, "
                f"reference={reference_frame or '?'}:{reference_kind or '?'}"
            ),
            comparison_mode="incompatible",
        )

    use_axis = (
        current_axis_base is not None
        and reference_axis_base is not None
        and current_frame == reference_frame == "base_link"
        and current_kind == reference_kind == "axial_yaw"
    )
    if use_axis:
        try:
            error = signed_axial_axis_error_deg(
                current_axis_base or (), reference_axis_base or ()
            )
            comparison_mode = "base_link_axis_3d"
        except (TypeError, ValueError):
            quality = 0.0
            error = 0.0
            comparison_mode = "invalid_3d_axis"
    else:
        error = signed_axial_error_deg(current_deg, reference_deg)
        comparison_mode = "scalar_axial_angle"

    absolute = abs(error)
    quality = max(0.0, min(1.0, quality))
    quality_deficit = max(0.0, minimum - quality) / max(minimum, 1e-6)
    cost = absolute / tolerance + quality_deficit

    if quality < minimum:
        state = "quality_low"
    elif absolute > tolerance:
        state = "angle_mismatch"
    else:
        state = "aligned"
    return OrientationAssessment(
        state,
        error,
        absolute,
        quality,
        cost,
        reason="",
        comparison_mode=comparison_mode,
    )


def choose_probe_direction(
    assessment: OrientationAssessment,
    *,
    previous_direction: int = 0,
    previous_cost: float | None = None,
    minimum_improvement: float = 0.05,
) -> int:
    """Choose the next viewpoint-probe direction.

    On the first reliable angle mismatch, the signed axial error provides an
    initial guess.  After a probe, the direction is kept only if measured cost
    improved; otherwise it is reversed.  For low-quality observations without
    a useful angle, directions alternate.
    """

    direction = 1 if int(previous_direction) >= 0 else -1
    if previous_direction == 0:
        if assessment.state == "angle_mismatch" and abs(assessment.signed_error_deg) > 1e-6:
            return 1 if assessment.signed_error_deg > 0.0 else -1
        return 1

    if previous_cost is None or not math.isfinite(float(previous_cost)):
        return direction
    improvement = float(previous_cost) - assessment.cost
    if improvement >= max(0.0, float(minimum_improvement)):
        return direction
    return -direction


def choose_probe_translation_m(
    *,
    current_range_m: float,
    reference_range_m: float,
    step_m: float,
    forward_clearance_ok: bool,
    close_margin_m: float = 0.04,
) -> float:
    """Return a tiny translation for a viewpoint change.

    Near the target, reverse is preferred so the robot never crowds an
    unidentified/poorly oriented object.  Farther away, a forward diagonal
    step is allowed only when the depth-clearance gate authorizes it.
    """

    current = float(current_range_m)
    reference = float(reference_range_m)
    step = abs(float(step_m))
    if not all(math.isfinite(value) for value in (current, reference, step)):
        raise ValueError("probe translation inputs must be finite")
    if step <= 0.0:
        return 0.0
    if current <= reference + max(0.0, float(close_margin_m)):
        return -step
    return step if bool(forward_clearance_ok) else -step


def adaptive_probe_steps(
    assessment: OrientationAssessment,
    *,
    coarse_turn_deg: float,
    coarse_move_m: float,
    fine_turn_deg: float,
    fine_move_m: float,
) -> tuple[float, float]:
    """Return smaller viewpoint steps as orientation approaches the target.

    Large, low-confidence errors need a visible baseline change.  Near the
    desired axis, the former fixed 3-degree/2-centimetre probe was too coarse
    and could step across the optimum repeatedly.  This helper reduces both
    commands in the final band without ever increasing the configured limits.
    """

    coarse_turn = max(0.5, abs(float(coarse_turn_deg)))
    coarse_move = max(0.0, abs(float(coarse_move_m)))
    fine_turn = min(coarse_turn, max(0.5, abs(float(fine_turn_deg))))
    fine_move = min(coarse_move, max(0.0, abs(float(fine_move_m))))

    if assessment.state == "quality_low" or assessment.absolute_error_deg > 20.0:
        return coarse_turn, coarse_move
    if assessment.absolute_error_deg > 10.0:
        return max(fine_turn, 0.75 * coarse_turn), max(fine_move, 0.75 * coarse_move)
    return fine_turn, fine_move
