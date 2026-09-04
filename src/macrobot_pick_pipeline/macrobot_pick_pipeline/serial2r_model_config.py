"""Construct the active serial-2R arm model from kinematics parameters."""

from __future__ import annotations

from typing import Any, Mapping, Tuple

from macrobot_arm_kinematics.model import ArmGeometry, JointLimits, MacRobotArmModel

Vec3 = Tuple[float, float, float]


def _vec3(params: Mapping[str, Any], name: str, default: Vec3) -> Vec3:
    raw = params.get(name, default)
    if not isinstance(raw, (list, tuple)) or len(raw) != 3:
        raise ValueError(f"{name} must contain exactly three numbers")
    values = tuple(float(value) for value in raw)
    return values  # type: ignore[return-value]


def build_arm_model(params: Mapping[str, Any]) -> MacRobotArmModel:
    geometry_default = ArmGeometry()
    limits_default = JointLimits()

    required_geometry_fields = {
        "shoulder_origin_xyz",
        "shoulder_origin_rpy",
        "shoulder_axis",
        "wrist_origin_xyz",
        "wrist_origin_rpy",
        "wrist_axis",
        "grasp_origin_xyz",
        "grasp_origin_rpy",
    }
    actual_fields = set(getattr(ArmGeometry, "__dataclass_fields__", {}))
    missing = sorted(required_geometry_fields - actual_fields)
    if missing:
        raise RuntimeError(
            "macrobot_arm_kinematics.model is still the legacy four-bar model; "
            f"missing ArmGeometry fields: {missing}"
        )

    geometry = ArmGeometry(
        shoulder_origin_xyz=_vec3(
            params, "shoulder_origin_xyz", geometry_default.shoulder_origin_xyz
        ),
        shoulder_origin_rpy=_vec3(
            params, "shoulder_origin_rpy", geometry_default.shoulder_origin_rpy
        ),
        shoulder_axis=_vec3(params, "shoulder_axis", geometry_default.shoulder_axis),
        wrist_origin_xyz=_vec3(
            params, "wrist_origin_xyz", geometry_default.wrist_origin_xyz
        ),
        wrist_origin_rpy=_vec3(
            params, "wrist_origin_rpy", geometry_default.wrist_origin_rpy
        ),
        wrist_axis=_vec3(params, "wrist_axis", geometry_default.wrist_axis),
        grasp_origin_xyz=_vec3(
            params, "grasp_origin_xyz", geometry_default.grasp_origin_xyz
        ),
        grasp_origin_rpy=_vec3(
            params, "grasp_origin_rpy", geometry_default.grasp_origin_rpy
        ),
        gripper_open_gap_m=float(
            params.get("gripper_open_gap_m", geometry_default.gripper_open_gap_m)
        ),
        gripper_closed_gap_m=float(
            params.get("gripper_closed_gap_m", geometry_default.gripper_closed_gap_m)
        ),
    )
    limits = JointLimits(
        arm_lift_min=float(params.get("arm_lift_min", limits_default.arm_lift_min)),
        arm_lift_max=float(params.get("arm_lift_max", limits_default.arm_lift_max)),
        wrist_pitch_min=float(
            params.get("wrist_pitch_min", limits_default.wrist_pitch_min)
        ),
        wrist_pitch_max=float(
            params.get("wrist_pitch_max", limits_default.wrist_pitch_max)
        ),
        gripper_min=float(params.get("gripper_min", limits_default.gripper_min)),
        gripper_max=float(params.get("gripper_max", limits_default.gripper_max)),
    )
    return MacRobotArmModel(
        geometry,
        limits,
        max_plane_error_m=float(params.get("max_plane_error_m", 0.030)),
    )
