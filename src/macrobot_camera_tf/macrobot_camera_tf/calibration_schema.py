from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import math
from typing import Any, Iterable

import yaml


@dataclass(frozen=True)
class TransformSpec:
    parent: str
    child: str
    xyz: tuple[float, float, float]
    quaternion_xyzw: tuple[float, float, float, float]


def quaternion_from_rpy(roll: float, pitch: float, yaw: float) -> tuple[float, float, float, float]:
    """Return an x-y-z-w quaternion for fixed-axis roll/pitch/yaw."""
    cr = math.cos(roll * 0.5)
    sr = math.sin(roll * 0.5)
    cp = math.cos(pitch * 0.5)
    sp = math.sin(pitch * 0.5)
    cy = math.cos(yaw * 0.5)
    sy = math.sin(yaw * 0.5)
    return (
        sr * cp * cy - cr * sp * sy,
        cr * sp * cy + sr * cp * sy,
        cr * cp * sy - sr * sp * cy,
        cr * cp * cy + sr * sp * sy,
    )


def rotate_vector(
    quaternion_xyzw: tuple[float, float, float, float],
    vector: tuple[float, float, float],
) -> tuple[float, float, float]:
    """Rotate a vector by a unit quaternion without external dependencies."""
    qx, qy, qz, qw = quaternion_xyzw
    vx, vy, vz = vector
    tx = 2.0 * (qy * vz - qz * vy)
    ty = 2.0 * (qz * vx - qx * vz)
    tz = 2.0 * (qx * vy - qy * vx)
    return (
        vx + qw * tx + (qy * tz - qz * ty),
        vy + qw * ty + (qz * tx - qx * tz),
        vz + qw * tz + (qx * ty - qy * tx),
    )


def multiply_quaternions(
    first_xyzw: tuple[float, float, float, float],
    second_xyzw: tuple[float, float, float, float],
) -> tuple[float, float, float, float]:
    """Compose rotations: result applies ``second`` and then ``first``."""
    ax, ay, az, aw = first_xyzw
    bx, by, bz, bw = second_xyzw
    return (
        aw * bx + ax * bw + ay * bz - az * by,
        aw * by - ax * bz + ay * bw + az * bx,
        aw * bz + ax * by - ay * bx + az * bw,
        aw * bw - ax * bx - ay * by - az * bz,
    )


def compose_transforms(
    first: TransformSpec,
    second: TransformSpec,
    *,
    parent: str,
    child: str,
) -> TransformSpec:
    """Compose parent->middle and middle->child transforms."""
    rotated = rotate_vector(first.quaternion_xyzw, second.xyz)
    xyz = tuple(first.xyz[index] + rotated[index] for index in range(3))
    quaternion = multiply_quaternions(
        first.quaternion_xyzw, second.quaternion_xyzw
    )
    return TransformSpec(
        parent=parent,
        child=child,
        xyz=(xyz[0], xyz[1], xyz[2]),
        quaternion_xyzw=quaternion,
    )


def _float_tuple(value: Any, size: int, field: str) -> tuple[float, ...]:
    if not isinstance(value, (list, tuple)) or len(value) != size:
        raise ValueError(f"{field} must contain exactly {size} numbers")
    result = tuple(float(item) for item in value)
    return result


def load_calibration(path: Path) -> tuple[dict[str, Any], list[TransformSpec]]:
    root = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(root, dict):
        raise ValueError("calibration root must be a mapping")
    if int(root.get("schema_version", 0)) != 1:
        raise ValueError("unsupported camera TF calibration schema_version")

    raw_transforms = root.get("transforms")
    if not isinstance(raw_transforms, list) or not raw_transforms:
        raise ValueError("calibration must contain a non-empty transforms list")

    transforms: list[TransformSpec] = []
    seen_children: set[str] = set()
    for index, raw in enumerate(raw_transforms):
        if not isinstance(raw, dict):
            raise ValueError(f"transforms[{index}] must be a mapping")
        parent = str(raw.get("parent", "")).strip()
        child = str(raw.get("child", "")).strip()
        if not parent or not child:
            raise ValueError(f"transforms[{index}] has an empty parent or child")
        if parent == child:
            raise ValueError(f"transforms[{index}] is a self transform: {parent}")
        if child in seen_children:
            raise ValueError(f"duplicate TF child frame in calibration: {child}")
        seen_children.add(child)
        xyz = _float_tuple(raw.get("xyz"), 3, f"transforms[{index}].xyz")
        quat = _float_tuple(
            raw.get("quaternion_xyzw"), 4, f"transforms[{index}].quaternion_xyzw"
        )
        norm2 = sum(item * item for item in quat)
        if norm2 <= 1e-12:
            raise ValueError(f"transforms[{index}] has a zero quaternion")
        norm = norm2 ** 0.5
        quat = tuple(item / norm for item in quat)
        transforms.append(
            TransformSpec(
                parent=parent,
                child=child,
                xyz=(xyz[0], xyz[1], xyz[2]),
                quaternion_xyzw=(quat[0], quat[1], quat[2], quat[3]),
            )
        )

    return root, transforms


def as_yaml_mapping(
    *,
    metadata: dict[str, Any],
    transforms: Iterable[TransformSpec],
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "metadata": metadata,
        "transforms": [
            {
                "parent": item.parent,
                "child": item.child,
                "xyz": [float(value) for value in item.xyz],
                "quaternion_xyzw": [float(value) for value in item.quaternion_xyzw],
            }
            for item in transforms
        ],
    }
