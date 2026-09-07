from macrobot_pick_pipeline.alignment_core import (
    AlignmentErrors,
    PlanarObservation,
)
from macrobot_pick_pipeline.fast_visual_docking import (
    choose_fast_camera_docking_action,
    direct_axis_turn_deg,
    orientation_engagement_ready,
)


def errors(*, current_forward, current_lateral, ref_forward=0.25, ref_lateral=0.0):
    current = PlanarObservation(
        current_forward,
        current_lateral,
        (current_forward ** 2 + current_lateral ** 2) ** 0.5,
        __import__("math").atan2(current_lateral, current_forward),
        0.0,
    )
    reference = PlanarObservation(
        ref_forward,
        ref_lateral,
        (ref_forward ** 2 + ref_lateral ** 2) ** 0.5,
        __import__("math").atan2(ref_lateral, ref_forward),
        0.0,
    )
    return AlignmentErrors(
        current=current,
        reference=reference,
        bearing_error_rad=current.bearing_rad - reference.bearing_rad,
        range_error_m=current.range_m - reference.range_m,
        height_error_m=0.0,
    )


def choose(value, streak=0):
    return choose_fast_camera_docking_action(
        value,
        translation_streak=streak,
        final_bearing_tolerance_deg=1.0,
        final_forward_tolerance_m=0.008,
        final_lateral_tolerance_m=0.008,
        final_turn_step_deg=1.5,
        final_move_step_m=0.012,
        coarse_bearing_tolerance_deg=4.0,
        emergency_bearing_tolerance_deg=7.0,
        coarse_lateral_tolerance_m=0.025,
        coarse_turn_step_deg=6.0,
        coarse_move_step_m=0.03,
        final_forward_band_m=0.035,
        max_translation_streak=3,
    )


def test_far_small_bearing_moves_without_micro_turn():
    result = choose(errors(current_forward=0.36, current_lateral=0.012))
    assert result.phase == "coarse"
    assert result.decision.action == "move"
    assert result.decision.amount == 0.03


def test_large_bearing_turns_immediately_with_coarse_step():
    result = choose(errors(current_forward=0.36, current_lateral=0.08))
    assert result.phase == "coarse"
    assert result.decision.action == "turn"
    assert result.decision.reason == "fast_emergency_bearing_realign"
    assert abs(result.decision.amount) == 6.0


def test_periodic_heading_realign_after_translation_streak():
    result = choose(errors(current_forward=0.36, current_lateral=0.03), streak=3)
    assert result.decision.action == "turn"
    assert result.decision.reason == "fast_periodic_heading_realign"


def test_near_target_uses_strict_final_controller():
    result = choose(errors(current_forward=0.27, current_lateral=0.012))
    assert result.phase == "final"
    assert result.decision.action in {"turn", "move"}


def test_orientation_is_deferred_until_final_band():
    assert not orientation_engagement_ready(
        errors(current_forward=0.34, current_lateral=0.0),
        maximum_forward_error_m=0.025,
        maximum_lateral_error_m=0.015,
        maximum_bearing_error_deg=3.0,
    )
    assert orientation_engagement_ready(
        errors(current_forward=0.26, current_lateral=0.004),
        maximum_forward_error_m=0.025,
        maximum_lateral_error_m=0.015,
        maximum_bearing_error_deg=3.0,
    )


def test_direct_3d_axis_turn_is_bounded():
    assert direct_axis_turn_deg(12.0, maximum_step_deg=6.0) == 6.0
    assert direct_axis_turn_deg(-4.0, maximum_step_deg=6.0) == -4.0
