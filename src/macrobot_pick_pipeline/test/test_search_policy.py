from macrobot_pick_pipeline.search_policy import (
    TranslationDominantSearchConfig,
    build_translation_dominant_search,
    total_motion_budget,
)


def test_search_observes_before_motion_and_reverses_same_corridor():
    actions = build_translation_dominant_search(
        TranslationDominantSearchConfig(
            forward_step_m=0.08,
            forward_steps=2,
            observation_sec=1.0,
            yaw_step_deg=10.0,
            yaw_levels=2,
        )
    )
    assert actions[0].kind == "observe"
    forward = [a.amount for a in actions if a.label.startswith("corridor_forward")]
    reverse = [a.amount for a in actions if a.label.startswith("corridor_reverse")]
    assert forward == [0.08, 0.08]
    assert reverse == [-0.08, -0.08]
    assert sum(forward) + sum(reverse) == 0.0


def test_search_uses_small_view_turns_not_one_large_geometric_turn():
    actions = build_translation_dominant_search(
        TranslationDominantSearchConfig(yaw_step_deg=10.0, yaw_levels=3)
    )
    turns = [abs(a.amount) for a in actions if a.kind == "turn"]
    assert turns
    assert max(turns) <= 10.0
    move_budget, turn_budget = total_motion_budget(actions)
    assert move_budget > 0.0
    assert turn_budget <= 100.0
