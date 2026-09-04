#!/usr/bin/env python3

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shutil
import sys


workspace = Path.home() / "MacRobot"
src = workspace / "src"
report_path = workspace / "four_bar_to_serial2r_report.json"

if not src.is_dir():
    raise SystemExit(f"ERROR: source directory not found: {src}")

if not report_path.is_file():
    raise SystemExit(f"ERROR: migration report not found: {report_path}")


patterns = (
    (
        "coupled_q1_q2_assignment",
        re.compile(r"\brear_lift_angle\s*=\s*q1\s*\+\s*q2\b"),
    ),
    (
        "coupled_servo_python",
        re.compile(
            r"model_angle_to_command_deg\(\s*q1\s*\+\s*q2\s*\)"
        ),
    ),
    (
        "coupled_servo_cpp",
        re.compile(
            r"tilt_multiplier_\s*\*\s*\(\s*q1\s*\+\s*q2\s*\)"
        ),
    ),
    (
        "legacy_moveit_joint_mapping",
        re.compile(
            r"setVariablePosition\(\s*[\"']"
            r"(?:servo_left_gear_joint|servo_right_gear_joint|"
            r"ratio_left_gear_joint|ratio_right_gear_joint|"
            r"ratio_left_gear_back_link_joint|"
            r"back_link_top_link_joint)"
            r"[\"']"
        ),
    ),
    (
        "legacy_four_bar_margin",
        re.compile(r"\bfour_bar_margin_\b"),
    ),
    (
        "legacy_coupled_limit",
        re.compile(r"\btool_pitch_(?:min|max)_\b"),
    ),
    (
        "legacy_commissioning_check",
        re.compile(
            r"[\"']four_bar_parallelogram_maintained[\"']"
        ),
    ),
    (
        "legacy_four_bar_enabled",
        re.compile(
            r"\bfour_bar_enabled\s*:\s*(?:true|True|1)\b"
        ),
    ),
)

allowed_suffixes = {
    ".py",
    ".cpp",
    ".hpp",
    ".h",
    ".yaml",
    ".yml",
    ".xml",
}

ignored_directories = {
    "docs",
    "urdf",
    "original",
    "backup",
    "build",
    "install",
    "log",
    "__pycache__",
}


findings: list[dict[str, object]] = []

for path in sorted(src.rglob("*")):
    if not path.is_file():
        continue

    if path.suffix not in allowed_suffixes:
        continue

    if any(part in ignored_directories for part in path.parts):
        continue

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        continue

    for line_number, line in enumerate(lines, start=1):
        for kind, pattern in patterns:
            if pattern.search(line):
                findings.append(
                    {
                        "kind": kind,
                        "path": str(path),
                        "line": line_number,
                        "text": line.strip(),
                    }
                )
                break


if findings:
    print("ERROR: active legacy runtime references still remain.")
    print()

    for item in findings:
        print(
            f"{item['kind']}: "
            f"{item['path']}:{item['line']}: "
            f"{item['text']}"
        )

    print()
    print("The migration report was not modified.")
    raise SystemExit(2)


timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
backup_path = report_path.with_name(
    f"{report_path.stem}.before_refresh_{timestamp}.json"
)

shutil.copy2(report_path, backup_path)

report = json.loads(report_path.read_text(encoding="utf-8"))
old_items = report.get("unresolved_legacy_runtime_references", [])

report["unresolved_legacy_runtime_references"] = []
report["legacy_runtime_scan"] = {
    "refreshed_at_utc": datetime.now(timezone.utc).isoformat(),
    "source_root": str(src),
    "active_finding_count": 0,
    "previous_report_finding_count": len(old_items),
    "result": "passed",
    "note": (
        "Refreshed after applying the serial-2R pick-pipeline patch. "
        "The active source tree was rescanned before clearing the "
        "historical findings."
    ),
}

report_path.write_text(
    json.dumps(report, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8",
)

print("Current source scan passed.")
print(f"Previous report findings: {len(old_items)}")
print(f"Backup: {backup_path}")
print(f"Updated report: {report_path}")
