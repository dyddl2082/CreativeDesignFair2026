#!/usr/bin/env python3

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import re
import shutil


workspace = Path.home() / "MacRobot"

parameter_names = (
    "arm_lift_min",
    "arm_lift_max",
    "wrist_pitch_min",
    "wrist_pitch_max",
    "gripper_min",
    "gripper_max",
)

targets = [
    workspace
    / "src"
    / "macrobot_arm_kinematics"
    / "macrobot_arm_kinematics"
    / "linkage_state_node.py",

    workspace
    / "src"
    / "macrobot_arm_kinematics"
    / "macrobot_arm_kinematics"
    / "ik_node.py",

    workspace
    / "tools"
    / "migrate_four_bar_to_serial2r.py",

    workspace
    / "tools"
    / "migrate_four_bar_to_serial2r_yamlfix.py",
]

stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
total_changes = 0

for path in targets:
    if not path.is_file():
        print(f"skip, not found: {path}")
        continue

    original = path.read_text(encoding="utf-8")
    lines = original.splitlines(keepends=True)
    file_changes = 0

    for index, line in enumerate(lines):
        for name in parameter_names:
            pattern = re.compile(
                rf'^(\s*self\.declare_parameter\(\s*["\']'
                rf'{re.escape(name)}'
                rf'["\']\s*,\s*)'
                rf'(.+?)'
                rf'(\)\s*)'
                rf'(\r?\n)?$'
            )

            match = pattern.match(line)
            if match is None:
                continue

            expression = match.group(2).strip()

            # Already explicitly declared as a Python float.
            if expression.startswith("float("):
                break

            newline = match.group(4) or ""

            lines[index] = (
                f"{match.group(1)}"
                f"float({expression})"
                f"{match.group(3)}"
                f"{newline}"
            )

            file_changes += 1
            break

    if file_changes == 0:
        print(f"no change needed: {path}")
        continue

    backup = path.with_name(
        f"{path.name}.before_double_parameter_fix_{stamp}"
    )
    shutil.copy2(path, backup)

    path.write_text("".join(lines), encoding="utf-8")

    print(f"updated: {path}")
    print(f"backup : {backup}")
    print(f"changes: {file_changes}")

    total_changes += file_changes

print()
print(f"total changes: {total_changes}")

if total_changes == 0:
    print(
        "No declarations were changed. "
        "They may already be wrapped with float()."
    )
