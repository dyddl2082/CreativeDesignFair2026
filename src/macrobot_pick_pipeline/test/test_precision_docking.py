import math

from macrobot_pick_pipeline.alignment_core import alignment_errors
from macrobot_pick_pipeline.precision_docking import (
    choose_precision_docking_action,
    precision_errors,
)


def _choose(current, reference=(0.24, 0.06, 0.08)):
    errors = alignment_errors(current, reference)
    return errors, choose_precision_docking_action(
        errors,
        bearing_tolerance_deg=1.0,
        forward_tolerance_m=0.008,
        lateral_tolerance_m=0.008,
        max_turn_step_deg=1.5,
        max_move_step_m=0.012,
    )


def test_forward_coordinate_not_planar_range_drives_translation():
    # Keep y at the taught arm plane and place the object 3 cm too far in x.
    errors, action = _choose((0.27, 0.06, 0.08))
    precise = precision_errors(errors)
    assert math.isclose(precise.forward_error_m, 0.03, abs_tol=1e-9)
    # Bearing is corrected first, then a bounded move is requested.
    assert action.action in {"turn", "move"}
    if action.action == "move":
        assert math.isclose(action.amount, 0.012, abs_tol=1e-9)


def test_aligned_requires_both_cartesian_components():
    errors, action = _choose((0.244, 0.065, 0.08))
    precise = precision_errors(errors)
    assert abs(precise.forward_error_m) < 0.008
    assert abs(precise.lateral_error_m) < 0.008
    assert action.action == "aligned"


def test_lateral_residual_is_not_hidden_by_range_tolerance():
    reference = (0.24, 0.06, 0.08)
    current = (0.24, 0.075, 0.08)
    errors = alignment_errors(current, reference)
    action = choose_precision_docking_action(
        errors,
        bearing_tolerance_deg=10.0,  # isolate direct lateral gate
        forward_tolerance_m=0.008,
        lateral_tolerance_m=0.008,
        max_turn_step_deg=1.5,
        max_move_step_m=0.012,
    )
    assert action.action == "turn"
    assert action.reason == "precision_lateral_error"


def test_move_is_bounded_for_encoder_error_reobservation():
    errors = alignment_errors((0.50, 0.06, 0.08), (0.24, 0.06, 0.08))
    action = choose_precision_docking_action(
        errors,
        bearing_tolerance_deg=20.0,
        forward_tolerance_m=0.008,
        lateral_tolerance_m=0.008,
        max_turn_step_deg=1.5,
        max_move_step_m=0.012,
    )
    assert action.action == "move"
    assert action.amount == 0.012
