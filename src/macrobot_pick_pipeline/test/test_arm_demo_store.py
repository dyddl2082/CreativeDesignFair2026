from pathlib import Path

from macrobot_pick_pipeline.arm_demo_store import ArmDemoRepository
from macrobot_pick_pipeline.demo_core import DemoRecording, Waypoint
from macrobot_pick_pipeline.teach_store import AtomicYamlStore


def test_repository_save_load_and_report(tmp_path: Path):
    report = AtomicYamlStore(tmp_path / "report.yaml")
    repository = ArmDemoRepository(tmp_path / "recordings", report)
    recording = DemoRecording(
        name="HOME_DEMO",
        kind="trajectory",
        recorded_at="now",
        waypoints=[
            Waypoint(0.0, (0.0, 0.0, 0.0)),
            Waypoint(0.5, (0.1, 0.0, 0.0)),
        ],
    )
    path = repository.save(recording)
    assert path.exists()
    loaded = repository.load("HOME_DEMO")
    assert loaded.final_q == (0.1, 0.0, 0.0)
    section = report.section("primitives")
    assert section["primitives"]["HOME_DEMO"]["trajectory_file"] == str(path)
    assert repository.list()[0]["name"] == "HOME_DEMO"
