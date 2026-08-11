from pathlib import Path

import yaml

from macrobot_pick_pipeline.teach_store import AtomicYamlStore


def test_store_preserves_existing_sections(tmp_path: Path):
    path = tmp_path / "report.yaml"
    path.write_text(
        yaml.safe_dump({"sections": {"pulse_zero_calibration": {"status": "completed"}}}),
        encoding="utf-8",
    )
    store = AtomicYamlStore(path)
    store.complete_section("primitives", {"primitives": {"HOME": {"target_q": [0, 0, 0]}}})

    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert loaded["sections"]["pulse_zero_calibration"]["status"] == "completed"
    assert loaded["sections"]["primitives"]["status"] == "completed"
    assert loaded["sections"]["primitives"]["primitives"]["HOME"]["target_q"] == [0, 0, 0]
