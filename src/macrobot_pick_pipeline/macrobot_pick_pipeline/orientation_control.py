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

    error = signed_axial_error_deg(current_deg, reference_deg)
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
    return OrientationAssessment(state, error, absolute, quality, cost)


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
