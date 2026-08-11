from pathlib import Path

import yaml

from macrobot_pick_pipeline.profiles import PickProfileRepository


def test_camera_recorded_offsets_override_static_profile(tmp_path: Path):
    config = tmp_path / "profiles.yaml"
    report = tmp_path / "report.yaml"
    config.write_text(
        yaml.safe_dump(
            {
                "defaults": {"close_q3": 1.0},
                "objects": {"Buds3": {"grasp_offset_base": [0.0, 0.0, 0.0]}},
            }
        ),
        encoding="utf-8",
    )
    report.write_text(
        yaml.safe_dump(
            {
                "sections": {
                    "grasp_profiles": {
                        "profiles": {
                            "Buds3": {
                                "open_q3": 0.1,
                                "close_q3": 1.2,
                                "grasp_offset_base": [0.01, 0.0, -0.002],
                                "pregrasp_offset_base": [0.0, 0.0, 0.04],
                                "lift_offset_base": [0.0, 0.0, 0.06],
                                "pre_grasp_q": [0.1, 0.2, 0.1],
                                "grasp_q": [0.2, 0.3, 0.1],
                                "lift_q": [0.0, 0.1, 1.2],
                            }
                        }
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    repo = PickProfileRepository(config, report)
    profile = repo.get("Buds3")

    assert profile.open_q3 == 0.1
    assert profile.close_q3 == 1.2
    assert profile.grasp_offset_base == (0.01, 0.0, -0.002)
    assert profile.pregrasp_offset_base == (0.0, 0.0, 0.04)
    assert profile.lift_offset_base == (0.0, 0.0, 0.06)
    assert profile.pre_grasp_seed_q == (0.1, 0.2, 0.1)
