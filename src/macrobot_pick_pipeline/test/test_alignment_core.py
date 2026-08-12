from pathlib import Path

from macrobot_pick_pipeline.alignment_core import (
    AlignmentProfile,
    AlignmentProfileStore,
    alignment_errors,
    choose_alignment_action,
    pico_move_command_cm,
    pico_turn_command_deg,
)


def profile(point=(-0.30, 0.06, 0.10)):
    return AlignmentProfile(
        name="Buds3",
        object_name="Buds3",
        pick_profile="Buds3",
        reference_point_base=point,
        recorded_at="test",
        bearing_tolerance_deg=2.0,
        range_tolerance_m=0.01,
        height_tolerance_m=0.02,
        max_turn_step_deg=8.0,
        max_move_step_m=0.04,
    )


def test_same_recorded_pose_is_aligned():
    item = profile()
    errors = alignment_errors(
        item.reference_point_base,
        item.reference_point_base,
        forward_axis_sign=-1.0,
        lateral_axis_sign=1.0,
    )
    decision = choose_alignment_action(errors, item)
    assert decision.action == "aligned"


def test_object_more_left_requires_left_turn():
    item = profile(point=(-0.30, 0.00, 0.10))
    errors = alignment_errors(
        (-0.30, 0.10, 0.10),
        item.reference_point_base,
        forward_axis_sign=-1.0,
        lateral_axis_sign=1.0,
    )
    decision = choose_alignment_action(errors, item)
    assert decision.action == "turn"
    # Core convention: positive amount means physical left turn.
    assert decision.amount > 0.0
    assert decision.amount <= item.max_turn_step_deg


def test_farther_object_requires_forward_motion():
    item = profile(point=(-0.30, 0.00, 0.10))
    errors = alignment_errors(
        (-0.42, 0.00, 0.10),
        item.reference_point_base,
        forward_axis_sign=-1.0,
        lateral_axis_sign=1.0,
    )
    decision = choose_alignment_action(errors, item)
    assert decision.action == "move"
    assert decision.amount > 0.0
    assert decision.amount <= item.max_move_step_m


def test_height_error_is_rejected():
    item = profile()
    errors = alignment_errors(
        (-0.30, 0.06, 0.20),
        item.reference_point_base,
        forward_axis_sign=-1.0,
        lateral_axis_sign=1.0,
    )
    decision = choose_alignment_action(errors, item)
    assert decision.action == "reject"
    assert decision.reason == "height_error_not_correctable_by_planar_base"


def test_profile_store_roundtrip(tmp_path: Path):
    path = tmp_path / "alignment.yaml"
    store = AlignmentProfileStore(path)
    item = profile()
    store.upsert(item)

    loaded = AlignmentProfileStore(path)
    assert loaded.names() == ("Buds3",)
    assert loaded.get("Buds3").reference_point_base == item.reference_point_base
    assert loaded.get(object_name="Buds3").pick_profile == "Buds3"


def test_pico_command_sign_conventions():
    # Pico firmware uses positive TURN_DEG for right turn.
    assert pico_turn_command_deg(5.0, pico_positive_is_right=True) == -5.0
    assert pico_turn_command_deg(-5.0, pico_positive_is_right=True) == 5.0
    assert pico_move_command_cm(0.04, pico_positive_is_forward=True) == 4.0
    assert pico_move_command_cm(-0.04, pico_positive_is_forward=True) == -4.0


def test_iterative_turn_move_alignment_converges():
    import math

    item = profile(point=(-0.30, 0.06, 0.10))
    # Core planar coordinates: forward=-x, left=+y.
    forward = 0.48
    lateral = 0.18
    height = 0.10

    for _ in range(40):
        current = (-forward, lateral, height)
        errors = alignment_errors(
            current,
            item.reference_point_base,
            forward_axis_sign=-1.0,
            lateral_axis_sign=1.0,
        )
        decision = choose_alignment_action(errors, item)
        if decision.action == "aligned":
            break
        if decision.action == "turn":
            alpha = math.radians(decision.amount)  # physical left-positive yaw
            forward, lateral = (
                math.cos(alpha) * forward + math.sin(alpha) * lateral,
                -math.sin(alpha) * forward + math.cos(alpha) * lateral,
            )
        elif decision.action == "move":
            forward -= decision.amount
        else:
            raise AssertionError(decision)
    else:
        raise AssertionError("alignment did not converge")

    final_errors = alignment_errors(
        (-forward, lateral, height),
        item.reference_point_base,
        forward_axis_sign=-1.0,
        lateral_axis_sign=1.0,
    )
    assert abs(final_errors.bearing_error_deg) <= item.bearing_tolerance_deg
    assert abs(final_errors.range_error_m) <= item.range_tolerance_m


def test_observation_constraints_reject_low_quality_and_orientation_mismatch():
    from macrobot_pick_pipeline.alignment_core import observation_constraint_decision

    item = AlignmentProfile(
        name="Eraser",
        object_name="Eraser",
        pick_profile="Eraser",
        reference_point_base=(-0.30, 0.05, 0.10),
        recorded_at="test",
        minimum_localization_quality=0.4,
        maximum_depth_std_m=0.02,
        maximum_center_std_px=8.0,
        require_orientation_match=True,
        reference_orientation_deg=0.0,
        reference_orientation_class="horizontal",
        reference_orientation_quality=0.8,
        minimum_orientation_quality=0.5,
        orientation_tolerance_deg=15.0,
    )
    low = observation_constraint_decision(
        item,
        localization_quality=0.2,
        depth_std_m=0.01,
        center_std_px=3.0,
        orientation_deg=0.0,
        orientation_class="horizontal",
        orientation_quality=0.8,
    )
    assert low.action == "reject"
    assert low.reason == "localization_quality_below_threshold"

    mismatch = observation_constraint_decision(
        item,
        localization_quality=0.9,
        depth_std_m=0.01,
        center_std_px=3.0,
        orientation_deg=90.0,
        orientation_class="vertical",
        orientation_quality=0.8,
    )
    assert mismatch.action == "reject"
    assert mismatch.reason == "object_orientation_class_mismatch"
