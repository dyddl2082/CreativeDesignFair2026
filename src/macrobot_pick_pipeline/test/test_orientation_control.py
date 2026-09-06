from macrobot_pick_pipeline.orientation_control import (
    assess_orientation,
    choose_probe_direction,
    choose_probe_translation_m,
    signed_axial_error_deg,
)


def test_signed_axial_error_wraps_modulo_180():
    assert signed_axial_error_deg(175.0, 5.0) == -10.0
    assert signed_axial_error_deg(5.0, 175.0) == 10.0


def test_assessment_distinguishes_quality_and_angle():
    low = assess_orientation(
        current_deg=90.0,
        current_quality=0.1,
        reference_deg=0.0,
        minimum_quality=0.25,
        tolerance_deg=20.0,
    )
    assert low.state == "quality_low"
    mismatch = assess_orientation(
        current_deg=60.0,
        current_quality=0.9,
        reference_deg=0.0,
        minimum_quality=0.25,
        tolerance_deg=20.0,
    )
    assert mismatch.state == "angle_mismatch"
    aligned = assess_orientation(
        current_deg=178.0,
        current_quality=0.9,
        reference_deg=2.0,
        minimum_quality=0.25,
        tolerance_deg=20.0,
    )
    assert aligned.aligned


def test_probe_direction_reverses_when_cost_did_not_improve():
    current = assess_orientation(
        current_deg=50.0,
        current_quality=0.8,
        reference_deg=0.0,
        minimum_quality=0.25,
        tolerance_deg=20.0,
    )
    assert choose_probe_direction(
        current,
        previous_direction=1,
        previous_cost=current.cost - 0.1,
        minimum_improvement=0.05,
    ) == -1
    assert choose_probe_direction(
        current,
        previous_direction=-1,
        previous_cost=current.cost + 0.2,
        minimum_improvement=0.05,
    ) == -1


def test_probe_translation_prefers_backoff_near_target():
    assert choose_probe_translation_m(
        current_range_m=0.28,
        reference_range_m=0.27,
        step_m=0.02,
        forward_clearance_ok=True,
    ) == -0.02
    assert choose_probe_translation_m(
        current_range_m=0.60,
        reference_range_m=0.27,
        step_m=0.02,
        forward_clearance_ok=True,
    ) == 0.02
    assert choose_probe_translation_m(
        current_range_m=0.60,
        reference_range_m=0.27,
        step_m=0.02,
        forward_clearance_ok=False,
    ) == -0.02


def test_adaptive_probe_steps_get_smaller_near_target():
    from macrobot_pick_pipeline.orientation_control import adaptive_probe_steps

    far = assess_orientation(
        current_deg=40.0,
        current_quality=0.8,
        reference_deg=90.0,
        minimum_quality=0.45,
        tolerance_deg=8.0,
    )
    near = assess_orientation(
        current_deg=84.0,
        current_quality=0.8,
        reference_deg=90.0,
        minimum_quality=0.45,
        tolerance_deg=8.0,
    )
    far_steps = adaptive_probe_steps(
        far,
        coarse_turn_deg=3.0,
        coarse_move_m=0.018,
        fine_turn_deg=1.0,
        fine_move_m=0.010,
    )
    near_steps = adaptive_probe_steps(
        near,
        coarse_turn_deg=3.0,
        coarse_move_m=0.018,
        fine_turn_deg=1.0,
        fine_move_m=0.010,
    )
    assert near_steps[0] < far_steps[0]
    assert near_steps[1] < far_steps[1]
