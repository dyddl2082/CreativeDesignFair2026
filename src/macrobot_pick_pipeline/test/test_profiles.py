from pathlib import Path

from macrobot_pick_pipeline.profiles import PickProfileRepository


def test_profile_loading():
    config = Path(__file__).parents[1] / "config" / "pick_profiles.yaml"
    repository = PickProfileRepository(config)
    buds = repository.get("Buds3")
    assert buds.name == "Buds3"
    assert buds.open_q3 == 0.0
    assert buds.close_q3 > 0.0
    assert len(buds.pregrasp_offset_base) == 3


def test_unknown_object_uses_defaults():
    config = Path(__file__).parents[1] / "config" / "pick_profiles.yaml"
    repository = PickProfileRepository(config)
    unknown = repository.get("random_object")
    assert unknown.name == "random_object"
    assert unknown.stability_count >= 1
