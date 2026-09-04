#!/usr/bin/env python3
"""Normalize MacRobot ROS 2 vector parameters to homogeneous double arrays.

ROS 2's rcl YAML parameter parser requires every item in a parameter array to
have one scalar type.  This script rewrites only the known 3-vector parameters
in macrobot_description/config/kinematics.yaml, preserving the rest of the
file and creating a timestamped backup.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import re
import shutil
import sys

VECTOR_KEYS = {
    "shoulder_origin_xyz",
    "shoulder_origin_rpy",
    "shoulder_axis",
    "wrist_origin_xyz",
    "wrist_origin_rpy",
    "wrist_axis",
    "grasp_origin_xyz",
    "grasp_origin_rpy",
    "nominal_grasp_xyz_in_gripper_link",
    "nominal_grasp_rpy_in_gripper_link",
    "arm_axis_base_xy",
    "positive_tilt_direction_base_xy",
}

LINE_RE = re.compile(
    r"^(?P<indent>\s*)(?P<key>[A-Za-z_][A-Za-z0-9_]*):\s*"
    r"\[(?P<body>[^\]]*)\](?P<suffix>\s*(?:#.*)?)$"
)


def float_text(value: float) -> str:
    text = f"{value:.12g}"
    if "." not in text and "e" not in text.lower():
        text += ".0"
    return text


def normalize(path: Path) -> tuple[int, list[str]]:
    original = path.read_text(encoding="utf-8")
    output: list[str] = []
    changed: list[str] = []
    seen: set[str] = set()

    for line_number, line in enumerate(original.splitlines(), start=1):
        match = LINE_RE.match(line)
        if not match or match.group("key") not in VECTOR_KEYS:
            output.append(line)
            continue

        key = match.group("key")
        seen.add(key)
        raw_items = [item.strip() for item in match.group("body").split(",")]
        if not raw_items or any(not item for item in raw_items):
            raise ValueError(f"{path}:{line_number}: malformed vector for {key}")

        try:
            values = [float(item) for item in raw_items]
        except ValueError as exc:
            raise ValueError(
                f"{path}:{line_number}: {key} contains a non-numeric item"
            ) from exc

        if key not in {"arm_axis_base_xy", "positive_tilt_direction_base_xy"} and len(values) != 3:
            raise ValueError(
                f"{path}:{line_number}: {key} must contain exactly three values"
            )
        if key in {"arm_axis_base_xy", "positive_tilt_direction_base_xy"} and len(values) != 2:
            raise ValueError(
                f"{path}:{line_number}: {key} must contain exactly two values"
            )

        normalized = (
            f"{match.group('indent')}{key}: "
            f"[{', '.join(float_text(value) for value in values)}]"
            f"{match.group('suffix')}"
        )
        output.append(normalized)
        if normalized != line:
            changed.append(f"line {line_number}: {key}")

    required = {
        "shoulder_origin_xyz",
        "shoulder_origin_rpy",
        "shoulder_axis",
        "wrist_origin_xyz",
        "wrist_origin_rpy",
        "wrist_axis",
        "grasp_origin_xyz",
        "grasp_origin_rpy",
    }
    missing = sorted(required - seen)
    if missing:
        raise ValueError(f"missing required vector parameters: {', '.join(missing)}")

    if not changed:
        return 0, []

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = path.with_name(f"{path.name}.before_numeric_fix_{stamp}")
    shutil.copy2(path, backup)
    path.write_text("\n".join(output) + "\n", encoding="utf-8")
    return len(changed), [str(backup), *changed]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, default=Path.home() / "MacRobot")
    parser.add_argument("--file", type=Path, default=None)
    args = parser.parse_args()

    path = args.file or (
        args.workspace.expanduser()
        / "src/macrobot_description/config/kinematics.yaml"
    )
    path = path.expanduser().resolve()
    if not path.is_file():
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        return 2

    try:
        count, details = normalize(path)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(f"file: {path}")
    print(f"changed vectors: {count}")
    if details:
        print(f"backup: {details[0]}")
        for item in details[1:]:
            print(f"  {item}")
    else:
        print("No rewrite was needed; all known vectors already use double syntax.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
