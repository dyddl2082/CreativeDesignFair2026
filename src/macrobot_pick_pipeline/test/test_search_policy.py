import math

from macrobot_pick_pipeline.search_policy import (
    RotationFirstSearchConfig,
    TranslationDominantSearchConfig,
    build_rotation_first_search,
    build_translation_dominant_search,
    total_motion_budget,
)


def test_rotation_first_search_observes_then_conditionally_backs_off_then_turns():
    actions = build_rotation_first_search(
        RotationFirstSearchConfig(
            initial_observation_sec=4.0,
            observation_sec=3.0,
            backoff_step_m=0.04,
            backoff_steps=2,
            yaw_step_deg=10.0,
        )
    )
    assert actions[0].kind == "observe"
    assert actions[0].label == "initial_view"
    backoffs = [
        action for action in actions if action.label.startswith("close_obstacle_backoff")
    ]
    assert [action.amount for action in backoffs] == [-0.04, -0.04]
    first_turn = next(index for index, action in enumerate(actions) if action.kind == "turn")
    assert all(action.kind != "turn" for action in actions[:first_turn])
    assert all(action.amount <= 0.0 for action in actions if action.kind == "move")


def test_rotation_first_search_covers_exactly_one_full_rotation():
    actions = build_rotation_first_search(
        RotationFirstSearchConfig(yaw_step_deg=10.0, full_rotation_deg=360.0)
    )
    turns = [action.amount for action in actions if action.kind == "turn"]
    assert len(turns) == 36
    assert max(abs(value) for value in turns) <= 10.0
    assert math.isclose(sum(abs(value) for value in turns), 360.0)
    assert all(value > 0.0 for value in turns)
    assert not [action for action in actions if action.kind == "move" and action.amount > 0.0]
    move_budget, turn_budget = total_motion_budget(actions)
    assert move_budget == 0.08
    assert math.isclose(turn_budget, 360.0)


def test_full_rotation_supports_opposite_monotonic_direction_and_remainder():
    actions = build_rotation_first_search(
        RotationFirstSearchConfig(
            yaw_step_deg=7.0,
            full_rotation_deg=360.0,
            turn_direction=-1,
            include_conditional_backoff=False,
        )
    )
    turns = [action.amount for action in actions if action.kind == "turn"]
    assert all(value < 0.0 for value in turns)
    assert math.isclose(sum(abs(value) for value in turns), 360.0)
    assert abs(turns[-1]) <= 7.0


def test_legacy_translation_config_cannot_reenable_forward_search():
    actions = build_translation_dominant_search(
        TranslationDominantSearchConfig(
            forward_step_m=0.08,
            forward_steps=2,
            observation_sec=2.0,
            yaw_step_deg=10.0,
            yaw_levels=1,
        )
    )
    assert all(action.amount <= 0.0 for action in actions if action.kind == "move")
    assert any(action.label.startswith("close_obstacle_backoff") for action in actions)
    assert math.isclose(
        sum(abs(action.amount) for action in actions if action.kind == "turn"),
        360.0,
    )


def test_legacy_oversized_probe_is_capped_to_small_backoff():
    actions = build_translation_dominant_search(
        TranslationDominantSearchConfig(
            forward_step_m=0.20,
            forward_steps=7,
            observation_sec=2.0,
            yaw_step_deg=25.0,
            yaw_levels=1,
        )
    )
    backoffs = [
        action.amount
        for action in actions
        if action.label.startswith("close_obstacle_backoff")
    ]
    turns = [abs(action.amount) for action in actions if action.kind == "turn"]
    assert backoffs == [-0.04, -0.04]
    assert max(turns) <= 10.0
