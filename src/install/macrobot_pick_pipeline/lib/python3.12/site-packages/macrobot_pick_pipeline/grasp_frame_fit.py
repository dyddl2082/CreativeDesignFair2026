from __future__ import annotations

from dataclasses import dataclass
import math
from statistics import mean
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


@dataclass(frozen=True)
class GeometryReference:
    pivot_x: float
    pivot_z: float
    main_link_length: float


def base_point_to_wrist_offset(
    q1: float,
    q2: float,
    measured_x: float,
    measured_z: float,
    reference: GeometryReference,
) -> Tuple[float, float]:
    """Transform a measured base_link X/Z point into the wrist frame."""
    rear_lift_angle = q1 + q2
    wrist_x = reference.pivot_x - reference.main_link_length * math.sin(q1)
    wrist_z = reference.pivot_z + reference.main_link_length * math.cos(q1)
    dx = measured_x - wrist_x
    dz = measured_z - wrist_z
    # Inverse of the corrected local-to-base rotation:
    # x = ox*cos(h) - oz*sin(h), z = ox*sin(h) + oz*cos(h).
    offset_x = dx * math.cos(rear_lift_angle) + dz * math.sin(rear_lift_angle)
    offset_z = -dx * math.sin(rear_lift_angle) + dz * math.cos(rear_lift_angle)
    return offset_x, offset_z


def _linear_fit(x: Sequence[float], y: Sequence[float]) -> Tuple[float, float]:
    if len(x) != len(y) or len(x) < 2:
        raise ValueError("At least two paired samples are required")
    x_mean = mean(x)
    y_mean = mean(y)
    denominator = sum((value - x_mean) ** 2 for value in x)
    if denominator <= 1e-14:
        raise ValueError("The q3 samples do not provide enough variation")
    slope = sum(
        (x_value - x_mean) * (y_value - y_mean)
        for x_value, y_value in zip(x, y)
    ) / denominator
    intercept = y_mean - slope * x_mean
    return intercept, slope


def fit_grasp_frame(
    samples: Sequence[Dict[str, float]],
    reference: GeometryReference,
) -> Dict[str, object]:
    """Fit the parameters used by MacRobotArmModel.effective_tool_offset().

    Expected sample keys:
      q1, q2, q3, measured_x, measured_z, measurement_frame

    ``measurement_frame`` is either ``base_link`` or ``wrist``.  Optional
    ``measured_gap`` values fit ``gripper_base_separation``.
    """
    if len(samples) < 3:
        raise ValueError("Three or more grasp-frame samples are recommended")

    transformed: List[Dict[str, float]] = []
    for raw in samples:
        q1 = float(raw["q1"])
        q2 = float(raw["q2"])
        q3 = float(raw["q3"])
        frame = str(raw.get("measurement_frame", "base_link"))
        measured_x = float(raw["measured_x"])
        measured_z = float(raw["measured_z"])
        if frame == "base_link":
            offset_x, offset_z = base_point_to_wrist_offset(
                q1, q2, measured_x, measured_z, reference
            )
        elif frame == "wrist":
            offset_x, offset_z = measured_x, measured_z
        else:
            raise ValueError(f"Unknown measurement_frame: {frame}")
        transformed.append(
            {
                "q1": q1,
                "q2": q2,
                "q3": q3,
                "offset_x": offset_x,
                "offset_z": offset_z,
                **(
                    {"measured_gap": float(raw["measured_gap"])}
                    if "measured_gap" in raw and raw["measured_gap"] is not None
                    else {}
                ),
            }
        )

    predictor = [math.sin(item["q3"]) for item in transformed]
    observed_x = [item["offset_x"] for item in transformed]
    tool_offset_x, gripper_link_length = _linear_fit(predictor, observed_x)
    tool_offset_z = mean(item["offset_z"] for item in transformed)

    residuals = []
    for item in transformed:
        predicted_x = tool_offset_x + gripper_link_length * math.sin(item["q3"])
        predicted_z = tool_offset_z
        residuals.append(
            {
                "q3": item["q3"],
                "offset_x": item["offset_x"],
                "offset_z": item["offset_z"],
                "predicted_x": predicted_x,
                "predicted_z": predicted_z,
                "error_m": math.hypot(
                    item["offset_x"] - predicted_x,
                    item["offset_z"] - predicted_z,
                ),
            }
        )

    fitted: Dict[str, object] = {
        "tool_offset_x": tool_offset_x,
        "tool_offset_z": tool_offset_z,
        "gripper_link_length": gripper_link_length,
        "rms_error_m": math.sqrt(
            mean(item["error_m"] ** 2 for item in residuals)
        ),
        "max_error_m": max(item["error_m"] for item in residuals),
        "transformed_samples": transformed,
        "residuals": residuals,
    }

    gap_items = [
        item for item in transformed if "measured_gap" in item
    ]
    if gap_items:
        base_values = [
            item["measured_gap"]
            - 2.0 * gripper_link_length * math.cos(item["q3"])
            for item in gap_items
        ]
        fitted["gripper_base_separation"] = mean(base_values)
    return fitted
