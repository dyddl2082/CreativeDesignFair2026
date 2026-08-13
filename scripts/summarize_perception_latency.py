#!/usr/bin/env python3
"""Summarize MacRobot finder latency JSONL and recommend tighter timeouts."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import statistics
from typing import Iterable


def percentile(values: list[float], q: float) -> float | None:
    clean = sorted(v for v in values if math.isfinite(v) and v >= 0.0)
    if not clean:
        return None
    if len(clean) == 1:
        return clean[0]
    position = (len(clean) - 1) * q
    lower = int(math.floor(position))
    upper = int(math.ceil(position))
    if lower == upper:
        return clean[lower]
    weight = position - lower
    return clean[lower] * (1.0 - weight) + clean[upper] * weight


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def load_records(path: Path, object_name: str) -> list[dict]:
    records: list[dict] = []
    if not path.is_file():
        return records
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            print(f"warning: skipped malformed line {line_number}")
            continue
        if not isinstance(item, dict):
            continue
        if object_name and str(item.get("object_name", "")).casefold() != object_name.casefold():
            continue
        records.append(item)
    return records


def metric(records: Iterable[dict], name: str) -> list[float]:
    result: list[float] = []
    for item in records:
        latency = item.get("latency")
        if not isinstance(latency, dict):
            continue
        value = latency.get(name)
        try:
            number = float(value)
        except (TypeError, ValueError):
            continue
        if math.isfinite(number) and number >= 0.0:
            result.append(number)
    return result


def relative_delta(records: Iterable[dict], start: str, end: str) -> list[float]:
    result: list[float] = []
    for item in records:
        latency = item.get("latency")
        if not isinstance(latency, dict):
            continue
        relative = latency.get("relative_sec")
        if not isinstance(relative, dict):
            continue
        try:
            value = float(relative[end]) - float(relative[start])
        except (KeyError, TypeError, ValueError):
            continue
        if math.isfinite(value) and value >= 0.0:
            result.append(value)
    return result


def describe(name: str, values: list[float]) -> None:
    if not values:
        print(f"{name:42s} n=0")
        return
    p50 = percentile(values, 0.50)
    p90 = percentile(values, 0.90)
    p95 = percentile(values, 0.95)
    print(
        f"{name:42s} n={len(values):3d} "
        f"mean={statistics.fmean(values):6.3f}s "
        f"p50={p50:6.3f}s p90={p90:6.3f}s p95={p95:6.3f}s "
        f"max={max(values):6.3f}s"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--file",
        default=str(Path.home() / "MacRobot/data/perception/finder_latency.jsonl"),
    )
    parser.add_argument("--object", default="")
    args = parser.parse_args()

    path = Path(args.file).expanduser()
    records = load_records(path, args.object)
    acquired = [
        item for item in records
        if str(item.get("outcome", "")) in {"acquired", "record_acquired"}
    ]

    print(f"file: {path}")
    print(f"records: {len(records)}, acquired: {len(acquired)}")
    if args.object:
        print(f"object: {args.object}")
    print()

    pipeline = relative_delta(acquired, "finder_target_ready", "first_pipeline_progress")
    evidence = metric(acquired, "target_ready_to_first_evidence_sec")
    found = metric(acquired, "target_ready_to_object_found_sec")
    found_to_localized = metric(acquired, "object_found_to_first_localized_sec")
    localized_to_stable = metric(acquired, "first_localized_to_stable_sec")
    ready_to_stable = metric(acquired, "target_ready_to_stable_sec")
    evidence_to_found = relative_delta(acquired, "first_target_evidence", "identity_confirmed")

    describe("target_ready -> pipeline progress", pipeline)
    describe("target_ready -> first target evidence", evidence)
    describe("first evidence -> object_found", evidence_to_found)
    describe("target_ready -> object_found", found)
    describe("object_found -> first localized", found_to_localized)
    describe("first localized -> stable point", localized_to_stable)
    describe("target_ready -> stable point", ready_to_stable)

    if not acquired:
        print("\nNot enough successful records for recommendations.")
        return 1

    p95_pipeline = percentile(pipeline, 0.95) or 1.0
    p90_found = percentile(found, 0.90) or percentile(evidence, 0.90) or 2.0
    p95_evidence_to_found = percentile(evidence_to_found, 0.95) or 1.0
    p95_found_to_localized = percentile(found_to_localized, 0.95) or 1.5
    p95_localized_to_stable = percentile(localized_to_stable, 0.95) or 2.0

    suggestions = {
        "finder_initial_detection_wait_sec": round(clamp(p90_found + 0.5, 1.5, 8.0), 2),
        "perception_pipeline_stall_timeout_sec": round(clamp(p95_pipeline + 2.0, 4.0, 12.0), 2),
        "perception_evidence_grace_sec": round(clamp(p95_evidence_to_found + 0.5, 1.0, 5.0), 2),
        "localization_idle_timeout_sec": round(clamp(p95_found_to_localized + 1.0, 2.0, 8.0), 2),
        "localization_stability_timeout_sec": round(
            clamp(p95_found_to_localized + p95_localized_to_stable + 1.5, 4.0, 15.0), 2
        ),
    }

    print("\nSuggested starting values (review with real failures before applying):")
    for name, value in suggestions.items():
        print(f"  {name}: {value}")

    print("\nRuntime commands:")
    for name, value in suggestions.items():
        print(
            "ros2 param set /macrobot_stored_object_pick "
            f"{name} {value}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
