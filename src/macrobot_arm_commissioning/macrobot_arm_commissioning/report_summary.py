from __future__ import annotations

from pathlib import Path
import sys
import yaml


def main() -> None:
    path = (
        Path(sys.argv[1]).expanduser().resolve()
        if len(sys.argv) >= 2
        else Path.home()
        / "MacRobot"
        / "data"
        / "commissioning"
        / "arm_commissioning_report.yaml"
    )
    if not path.exists():
        raise SystemExit(f"Report not found: {path}")
    with path.open("r", encoding="utf-8") as stream:
        report = yaml.safe_load(stream) or {}
    print(f"report: {path}")
    print(f"robot: {report.get('robot_name')}")
    print(f"updated: {report.get('updated_at')}")
    sections = report.get("sections", {})
    if isinstance(sections, dict):
        for name, value in sections.items():
            status = value.get("status") if isinstance(value, dict) else "unknown"
            print(f"- {name}: {status}")
