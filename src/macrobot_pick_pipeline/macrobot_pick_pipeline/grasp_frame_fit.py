"""Fit the fixed ``gripper_link -> grasp_nominal`` frame for serial 2R."""

from __future__ import annotations

from dataclasses import dataclass
import math
from statistics import mean
from typing import Dict, List, Optional, Sequence, Tuple

from macrobot_arm_kinematics.model import MacRobotArmModel

Vec3 = Tuple[float, float, float]
Mat3 = Tuple[Tuple[float, float, float], Tuple[float, float, float], Tuple[float, float, float]]


@dataclass(frozen=True)
class GeometryReference:
    """Legacy compatibility container; values are intentionally ignored."""

    pivot_x: float = 0.0
    pivot_z: float = 0.0
    main_link_length: float = 0.0


def _transpose_multiply(rotation: Mat3, vector: Vec3) -> Vec3:
    return tuple(
        sum(rotation[row][column] * vector[row] for row in range(3))
        for column in range(3)
    )  # type: ignore[return-value]


def base_point_to_gripper_offset(
    q1: float,
    q2: float,
    measured_x: float,
    measured_y: float,
    measured_z: float,
    model: Optional[MacRobotArmModel] = None,
) -> Vec3:
    """Convert a measured base_link point to the current gripper_link frame."""
    active_model = model or MacRobotArmModel()
    position, rotation = active_model.gripper_link_transform(float(q1), float(q2))
    delta = (
        float(measured_x) - position[0],
        float(measured_y) - position[1],
        float(measured_z) - position[2],
    )
    return _transpose_multiply(rotation, delta)


def _linear_fit(x: Sequence[float], y: Sequence[float]) -> Tuple[float, float]:
    if len(x) != len(y) or len(x) < 2:
        raise ValueError("At least two paired samples are required")
    x_mean = mean(x)
    y_mean = mean(y)
    denominator = sum((value - x_mean) ** 2 for value in x)
    if denominator <= 1e-14:
        raise ValueError("Samples do not provide enough q3 variation")
    slope = sum(
        (x_value - x_mean) * (y_value - y_mean)
        for x_value, y_value in zip(x, y)
    ) / denominator
    return y_mean - slope * x_mean, slope


def fit_grasp_frame(
    samples: Sequence[Dict[str, float]],
    reference: Optional[GeometryReference] = None,
    model: Optional[MacRobotArmModel] = None,
) -> Dict[str, object]:
    """Estimate one q3-independent grasp-frame translation in gripper_link.

    Each sample requires q1, q2, measured_x, measured_y and measured_z. The
    measurement frame may be ``base_link`` or ``gripper_link``; ``wrist`` is
    accepted as a legacy alias for ``gripper_link``.
    """
    del reference
    if len(samples) < 3:
        raise ValueError("Three or more serial-2R grasp-frame samples are required")
    active_model = model or MacRobotArmModel()

    transformed: List[Dict[str, float]] = []
    for raw in samples:
        q1 = float(raw["q1"])
        q2 = float(raw["q2"])
        q3 = float(raw.get("q3", 0.0))
        frame = str(raw.get("measurement_frame", "base_link"))
        measured_x = float(raw["measured_x"])
        measured_y = float(raw["measured_y"])
        measured_z = float(raw["measured_z"])

        if frame == "base_link":
            local = base_point_to_gripper_offset(
                q1, q2, measured_x, measured_y, measured_z, active_model
            )
        elif frame in {"gripper_link", "wrist"}:
            local = (measured_x, measured_y, measured_z)
        else:
            raise ValueError(f"Unknown measurement_frame: {frame}")

        transformed.append(
            {
                "q1": q1,
                "q2": q2,
                "q3": q3,
                "local_x": local[0],
                "local_y": local[1],
                "local_z": local[2],
                **(
                    {"measured_gap": float(raw["measured_gap"])}
                    if raw.get("measured_gap") is not None
                    else {}
                ),
            }
        )

    origin: Vec3 = (
        mean(item["local_x"] for item in transformed),
        mean(item["local_y"] for item in transformed),
        mean(item["local_z"] for item in transformed),
    )
    residuals: List[Dict[str, float]] = []
    for item in transformed:
        error = math.dist(
            (item["local_x"], item["local_y"], item["local_z"]), origin
        )
        residuals.append(
            {
                "q1": item["q1"],
                "q2": item["q2"],
                "q3": item["q3"],
                "error_m": error,
            }
        )

    output: Dict[str, object] = {
        "grasp_origin_xyz": list(origin),
        "grasp_origin_x": origin[0],
        "grasp_origin_y": origin[1],
        "grasp_origin_z": origin[2],
        "rms_error_m": math.sqrt(mean(item["error_m"] ** 2 for item in residuals)),
        "max_error_m": max(item["error_m"] for item in residuals),
        "transformed_samples": transformed,
        "residuals": residuals,
        "model_note": "fixed grasp_nominal under gripper_link; q3-independent center",
    }

    gap_items = [item for item in transformed if "measured_gap" in item]
    if len(gap_items) >= 2:
        q3_min = active_model.limits.gripper_min
        q3_max = active_model.limits.gripper_max
        span = q3_max - q3_min
        if span > 1e-12:
            predictors = []
            observed = []
            for item in gap_items:
                ratio = min(1.0, max(0.0, (item["q3"] - q3_min) / span))
                predictors.append(math.cos(0.5 * math.pi * ratio))
                observed.append(item["measured_gap"])
            try:
                closed_gap, open_minus_closed = _linear_fit(predictors, observed)
                output["gripper_closed_gap_m"] = closed_gap
                output["gripper_open_gap_m"] = closed_gap + open_minus_closed
            except ValueError:
                output["gap_fit_warning"] = "q3 samples do not span enough range"
    return output
