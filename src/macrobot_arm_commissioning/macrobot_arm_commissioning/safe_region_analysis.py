from __future__ import annotations

from collections import Counter, deque
import csv
from dataclasses import dataclass
import math
from pathlib import Path
from statistics import median
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


Q = Tuple[float, float, float]


@dataclass(frozen=True)
class SafeSample:
    q1: float
    q2: float
    q3: float
    safe: bool = True
    connected: bool = True
    reason: str = "safe"
    contacts: str = ""

    @property
    def q(self) -> Q:
        return (self.q1, self.q2, self.q3)

    @property
    def rear_lift_angle(self) -> float:
        """Absolute angle of the right driven/rear-lift gear."""
        return self.q1 + self.q2

    @property
    def tool_pitch(self) -> float:
        """Backward-compatible alias for rear_lift_angle."""
        return self.rear_lift_angle


def _read_bool(value: object, default: bool = False) -> bool:
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def _median_step(values: Sequence[float]) -> float:
    differences = [
        b - a for a, b in zip(values[:-1], values[1:]) if b - a > 1e-10
    ]
    return median(differences) if differences else math.inf


class SafeRegionDataset:
    """Read MoveIt safe-region CSV files and choose physical test poses."""

    def __init__(
        self,
        connected_csv: str | Path,
        all_samples_csv: str | Path | None = None,
    ) -> None:
        self.connected_path = Path(connected_csv).expanduser().resolve()
        if not self.connected_path.exists():
            raise FileNotFoundError(self.connected_path)
        self.connected = self._read_csv(self.connected_path, connected_only=True)
        if not self.connected:
            raise ValueError(f"No connected samples: {self.connected_path}")

        inferred = self.connected_path.with_name("safe_samples.csv")
        if all_samples_csv:
            self.all_samples_path = Path(all_samples_csv).expanduser().resolve()
        elif inferred.exists():
            self.all_samples_path = inferred
        else:
            self.all_samples_path = None
        self.all_samples = (
            self._read_csv(self.all_samples_path, connected_only=False)
            if self.all_samples_path and self.all_samples_path.exists()
            else []
        )

        self.q1_values = sorted({item.q1 for item in self.connected})
        self.q2_values = sorted({item.q2 for item in self.connected})
        self.q3_values = sorted({item.q3 for item in self.connected})
        self.steps = (
            _median_step(self.q1_values),
            _median_step(self.q2_values),
            _median_step(self.q3_values),
        )
        self._q1_index = {round(value, 9): index for index, value in enumerate(self.q1_values)}
        self._q2_index = {round(value, 9): index for index, value in enumerate(self.q2_values)}
        self._q3_index = {round(value, 9): index for index, value in enumerate(self.q3_values)}
        self._sample_by_index = {}
        for item in self.connected:
            index = (
                self._q1_index[round(item.q1, 9)],
                self._q2_index[round(item.q2, 9)],
                self._q3_index[round(item.q3, 9)],
            )
            self._sample_by_index[index] = item

    @staticmethod
    def _read_csv(path: Path, connected_only: bool) -> List[SafeSample]:
        rows: List[SafeSample] = []
        with path.open("r", encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream)
            required = {"q1_rad", "q2_rad", "q3_rad"}
            if not required.issubset(set(reader.fieldnames or [])):
                raise ValueError(f"Missing columns {sorted(required)} in {path}")
            for row in reader:
                connected = _read_bool(row.get("connected"), default=True)
                safe = _read_bool(row.get("safe"), default=connected)
                if connected_only and not connected:
                    continue
                rows.append(
                    SafeSample(
                        q1=float(row["q1_rad"]),
                        q2=float(row["q2_rad"]),
                        q3=float(row["q3_rad"]),
                        safe=safe,
                        connected=connected,
                        reason=str(row.get("reason", "")),
                        contacts=str(row.get("contacts", "")),
                    )
                )
        return rows

    def metadata(self) -> Dict[str, object]:
        return {
            "connected_csv": str(self.connected_path),
            "all_samples_csv": (
                str(self.all_samples_path) if self.all_samples_path else None
            ),
            "connected_sample_count": len(self.connected),
            "all_sample_count": len(self.all_samples),
            "bounds_rad": {
                "q1": [self.q1_values[0], self.q1_values[-1]],
                "q2": [self.q2_values[0], self.q2_values[-1]],
                "q3": [self.q3_values[0], self.q3_values[-1]],
            },
            "grid_step_rad": {
                "q1": self.steps[0],
                "q2": self.steps[1],
                "q3": self.steps[2],
            },
        }

    def nearest(self, target: Q, samples: Optional[Sequence[SafeSample]] = None) -> SafeSample:
        candidates = samples or self.connected
        scales = tuple(1.0 if math.isinf(step) else max(step, 1e-9) for step in self.steps)
        return min(
            candidates,
            key=lambda item: sum(
                ((item.q[index] - target[index]) / scales[index]) ** 2
                for index in range(3)
            ),
        )

    def nearest_home(self) -> SafeSample:
        return self.nearest((0.0, 0.0, 0.0))

    @staticmethod
    def _second_inset(values: Sequence[float], high: bool) -> float:
        if len(values) <= 2:
            return values[-1] if high else values[0]
        return values[-2] if high else values[1]

    def _at_axis_value(self, axis: int, value: float) -> List[SafeSample]:
        return [item for item in self.connected if abs(item.q[axis] - value) < 1e-8]

    def _case(
        self,
        name: str,
        category: str,
        sample: SafeSample,
        rationale: str,
    ) -> Dict[str, object]:
        return {
            "name": name,
            "category": category,
            "q": [sample.q1, sample.q2, sample.q3],
            "rear_lift_angle": sample.rear_lift_angle,
            "tool_pitch": sample.tool_pitch,  # legacy report key
            "rationale": rationale,
        }

    def representative_cases(self, max_collision_cases: int = 3) -> List[Dict[str, object]]:
        cases: List[Dict[str, object]] = []
        home = self.nearest_home()
        cases.append(self._case("home", "home", home, "Connected sample nearest q=[0,0,0]."))

        axis_names = ("q1", "q2")
        values_by_axis = (self.q1_values, self.q2_values)
        for axis, axis_name in enumerate(axis_names):
            for high in (False, True):
                target_value = self._second_inset(values_by_axis[axis], high)
                candidates = self._at_axis_value(axis, target_value)
                sample = self.nearest(home.q, candidates)
                side = "max_inside" if high else "min_inside"
                cases.append(
                    self._case(
                        f"{axis_name}_{side}",
                        "joint_boundary",
                        sample,
                        f"One sampled grid level inside the {axis_name} {'maximum' if high else 'minimum'}.",
                    )
                )

        open_candidates = self._at_axis_value(2, self.q3_values[0])
        open_sample = self.nearest(home.q, open_candidates)
        cases.append(
            self._case(
                "gripper_open",
                "gripper",
                open_sample,
                "Connected sample at the most open sampled q3 value.",
            )
        )

        q3_mid = 0.5 * (self.q3_values[0] + self.q3_values[-1])
        half_sample = min(
            self.connected,
            key=lambda item: (
                abs(item.q3 - q3_mid) / max(self.steps[2], 1e-9),
                abs(item.q1) + abs(item.q2),
            ),
        )
        cases.append(
            self._case(
                "gripper_half",
                "gripper",
                half_sample,
                "Safe connected sample nearest half of the sampled gripper range.",
            )
        )

        near_close_value = self._second_inset(self.q3_values, high=True)
        near_close_candidates = self._at_axis_value(2, near_close_value)
        near_close_sample = self.nearest(home.q, near_close_candidates)
        cases.append(
            self._case(
                "gripper_near_close",
                "gripper",
                near_close_sample,
                "One sampled grid level inside the most closed connected q3 boundary.",
            )
        )

        pitches = sorted({round(item.rear_lift_angle, 10) for item in self.connected})
        for high in (False, True):
            target_pitch = self._second_inset(pitches, high)
            candidates = [
                item
                for item in self.connected
                if abs(item.rear_lift_angle - target_pitch) < 1e-7
            ]
            if not candidates:
                candidates = sorted(
                    self.connected,
                    key=lambda item: abs(item.rear_lift_angle - target_pitch),
                )[: max(1, min(100, len(self.connected)))]
            sample = self.nearest(home.q, candidates)
            side = "max_inside" if high else "min_inside"
            cases.append(
                self._case(
                    f"rear_lift_angle_{side}",
                    "coupled_boundary",
                    sample,
                    "One sampled level inside the q1+q2 rear-lift boundary.",
                )
            )

        cases.extend(self._collision_near_cases(max_collision_cases))

        deduplicated: List[Dict[str, object]] = []
        seen = set()
        for case in cases:
            key = tuple(round(float(value), 8) for value in case["q"])  # type: ignore[index]
            if key in seen:
                continue
            seen.add(key)
            deduplicated.append(case)
        return deduplicated

    def _collision_near_cases(self, count: int) -> List[Dict[str, object]]:
        if count <= 0 or not self.all_samples:
            return []
        collision_rows = [
            item
            for item in self.all_samples
            if item.reason == "collision" and item.contacts
        ]
        pair_counts: Counter[str] = Counter()
        for item in collision_rows:
            for pair in item.contacts.split(";"):
                pair = pair.strip()
                if pair:
                    pair_counts[pair] += 1

        output: List[Dict[str, object]] = []
        for index, (pair, frequency) in enumerate(pair_counts.most_common(count), start=1):
            matching = [
                item for item in collision_rows if pair in item.contacts.split(";")
            ]
            if not matching:
                continue
            unsafe = min(
                matching,
                key=lambda item: item.q1 * item.q1 + item.q2 * item.q2 + item.q3 * item.q3,
            )
            safe = self.nearest(unsafe.q)
            output.append(
                self._case(
                    f"collision_margin_{index}",
                    "collision_boundary",
                    safe,
                    f"Connected safe sample nearest frequent collision pair {pair} "
                    f"(observed {frequency} rejected samples).",
                )
            )
            output[-1]["collision_pair"] = pair
            output[-1]["collision_frequency"] = frequency
            output[-1]["nearest_rejected_q"] = list(unsafe.q)
        return output

    def grid_path(self, start: Q, goal: Q) -> List[Q]:
        """Return a 6-neighbour path through the home-connected sample grid.

        The safe-region generator uses the same neighbour topology when it marks
        the component connected to home.  Each returned segment therefore stays
        on an edge that was accepted during generation.
        """
        start_sample = self.nearest(start)
        goal_sample = self.nearest(goal)
        start_index = (
            self._q1_index[round(start_sample.q1, 9)],
            self._q2_index[round(start_sample.q2, 9)],
            self._q3_index[round(start_sample.q3, 9)],
        )
        goal_index = (
            self._q1_index[round(goal_sample.q1, 9)],
            self._q2_index[round(goal_sample.q2, 9)],
            self._q3_index[round(goal_sample.q3, 9)],
        )
        if start_index == goal_index:
            return [start_sample.q]

        queue = deque([start_index])
        parent = {start_index: None}
        directions = (
            (1, 0, 0),
            (-1, 0, 0),
            (0, 1, 0),
            (0, -1, 0),
            (0, 0, 1),
            (0, 0, -1),
        )
        while queue:
            current = queue.popleft()
            if current == goal_index:
                break
            for direction in directions:
                neighbour = (
                    current[0] + direction[0],
                    current[1] + direction[1],
                    current[2] + direction[2],
                )
                if neighbour not in self._sample_by_index or neighbour in parent:
                    continue
                parent[neighbour] = current
                queue.append(neighbour)

        if goal_index not in parent:
            raise RuntimeError(
                f"No connected grid path from {start_sample.q} to {goal_sample.q}"
            )

        indices = []
        cursor = goal_index
        while cursor is not None:
            indices.append(cursor)
            cursor = parent[cursor]
        indices.reverse()
        return [self._sample_by_index[index].q for index in indices]

    def safe_close_q3(self, inset_levels: int = 1) -> float:
        if len(self.q3_values) <= inset_levels:
            return self.q3_values[-1]
        return self.q3_values[max(0, len(self.q3_values) - 1 - inset_levels)]
