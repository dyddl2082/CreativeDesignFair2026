from pathlib import Path
import yaml

from macrobot_arm_commissioning.report_store import ReportStore


def test_report_store_atomic(tmp_path: Path):
    path = tmp_path / "report.yaml"
    store = ReportStore(path)
    store.begin_section("example")
    store.complete_section("example", {"value": 3})
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert loaded["sections"]["example"]["status"] == "completed"
    assert loaded["sections"]["example"]["value"] == 3
