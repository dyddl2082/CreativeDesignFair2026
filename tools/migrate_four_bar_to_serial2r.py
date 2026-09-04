#!/usr/bin/env python3
"""Migrate the MacRobot arm stack from the legacy four-bar model to serial 2R.

The script intentionally keeps the public logical joint names:

    arm_lift_joint, wrist_pitch_joint, gripper_joint

It reads the *current* macrobot_description URDF, extracts the actual serial
chain, backs up affected packages, replaces the four-bar FK/IK implementation,
changes the second actuator input from q1+q2 to q2, removes four-bar-only safety
checks, updates the safe-region generator and commissioning tools, refreshes a
minimal conservative SRDF, and writes a migration report.  Gripper mimic values
(including the current +2 servo-gear ratio/direction) are copied from the active
URDF instead of being hard-coded.  The URDF itself is never edited.

Default mode is dry-run. Use --apply to write changes.
"""

from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence, Tuple
import xml.etree.ElementTree as ET

try:
    import yaml
except ImportError as exc:  # pragma: no cover - runtime guard
    raise SystemExit("PyYAML is required: sudo apt install python3-yaml") from exc


Vec3 = Tuple[float, float, float]
Mat3 = Tuple[Tuple[float, float, float], Tuple[float, float, float], Tuple[float, float, float]]

LEGACY_ARM_JOINTS = {
    "servo_left_gear_joint",
    "servo_right_gear_joint",
    "ratio_left_gear_joint",
    "ratio_right_gear_joint",
    "ratio_left_gear_back_link_joint",
    "back_link_top_link_joint",
}

CORE_PACKAGES = (
    "macrobot_description",
    "macrobot_arm_kinematics",
    "macrobot_arm_control",
    "macrobot_safe_region",
    "macrobot_arm_commissioning",
    "macrobot_moveit_config",
)

# These patterns intentionally match executable legacy behaviour, not comments,
# migration notes, compatibility aliases, or validators that merely mention an old
# name.  A broad search for the words "four bar" produced many false positives.
FORBIDDEN_RUNTIME_PATTERNS = (
    ("coupled_q1_q2_assignment", re.compile(r"\brear_lift_angle\s*=\s*q1\s*\+\s*q2\b")),
    ("coupled_servo_python", re.compile(r"model_angle_to_command_deg\(\s*q1\s*\+\s*q2\s*\)")),
    ("coupled_servo_cpp", re.compile(r"tilt_multiplier_\s*\*\s*\(\s*q1\s*\+\s*q2\s*\)")),
    ("legacy_moveit_joint_mapping", re.compile(
        r"setVariablePosition\(\s*[\"'](?:servo_left_gear_joint|servo_right_gear_joint|"
        r"ratio_left_gear_joint|ratio_right_gear_joint|ratio_left_gear_back_link_joint|"
        r"back_link_top_link_joint)[\"']"
    )),
    ("legacy_four_bar_margin", re.compile(r"\bfour_bar_margin_\b")),
    ("legacy_coupled_limit", re.compile(r"\btool_pitch_(?:min|max)_\b")),
    ("legacy_commissioning_check", re.compile(r"[\"']four_bar_parallelogram_maintained[\"']")),
    ("legacy_four_bar_enabled", re.compile(r"\bfour_bar_enabled\s*:\s*(?:true|True|1)\b")),
)


class MigrationError(RuntimeError):
    pass


@dataclass(frozen=True)
class JointSpec:
    name: str
    joint_type: str
    parent: str
    child: str
    origin_xyz: Vec3
    origin_rpy: Vec3
    axis: Vec3
    lower: float
    upper: float
    mimic_joint: Optional[str] = None
    mimic_multiplier: float = 1.0
    mimic_offset: float = 0.0


@dataclass(frozen=True)
class RobotSpec:
    robot_name: str
    model_revision: str
    urdf_path: Path
    links: Tuple[str, ...]
    shoulder: JointSpec
    wrist: JointSpec
    gripper: JointSpec
    grasp_joint: JointSpec
    mimics: Mapping[str, Tuple[str, float, float]]
    wheel_joints: Tuple[str, ...]
    zero_grasp_xyz: Vec3
    shoulder_axis_base: Vec3
    wrist_axis_base_zero: Vec3
    axis_alignment: float


@dataclass
class PlannedWrite:
    path: Path
    content: str
    reason: str


@dataclass
class PlannedMove:
    source: Path
    destination: Path
    reason: str


def parse_vec(text: Optional[str], default: Vec3 = (0.0, 0.0, 0.0)) -> Vec3:
    if not text:
        return default
    values = tuple(float(x) for x in text.split())
    if len(values) != 3:
        raise MigrationError(f"Expected three values, got {text!r}")
    return values  # type: ignore[return-value]


def mat_mul(a: Mat3, b: Mat3) -> Mat3:
    return tuple(
        tuple(sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3))
        for i in range(3)
    )  # type: ignore[return-value]


def mat_vec(a: Mat3, v: Vec3) -> Vec3:
    return tuple(sum(a[i][k] * v[k] for k in range(3)) for i in range(3))  # type: ignore[return-value]


def vec_add(a: Vec3, b: Vec3) -> Vec3:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def dot(a: Vec3, b: Vec3) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def norm(v: Vec3) -> float:
    return math.sqrt(dot(v, v))


def normalized(v: Vec3) -> Vec3:
    length = norm(v)
    if length <= 1e-12:
        raise MigrationError(f"Zero-length axis: {v}")
    return (v[0] / length, v[1] / length, v[2] / length)


def rpy_matrix(rpy: Vec3) -> Mat3:
    roll, pitch, yaw = rpy
    cr, sr = math.cos(roll), math.sin(roll)
    cp, sp = math.cos(pitch), math.sin(pitch)
    cy, sy = math.cos(yaw), math.sin(yaw)
    rx: Mat3 = ((1.0, 0.0, 0.0), (0.0, cr, -sr), (0.0, sr, cr))
    ry: Mat3 = ((cp, 0.0, sp), (0.0, 1.0, 0.0), (-sp, 0.0, cp))
    rz: Mat3 = ((cy, -sy, 0.0), (sy, cy, 0.0), (0.0, 0.0, 1.0))
    return mat_mul(mat_mul(rz, ry), rx)


def axis_angle_matrix(axis: Vec3, angle: float) -> Mat3:
    x, y, z = normalized(axis)
    c = math.cos(angle)
    s = math.sin(angle)
    t = 1.0 - c
    return (
        (t * x * x + c, t * x * y - s * z, t * x * z + s * y),
        (t * x * y + s * z, t * y * y + c, t * y * z - s * x),
        (t * x * z - s * y, t * y * z + s * x, t * z * z + c),
    )


def format_tuple(values: Sequence[float]) -> str:
    return "(" + ", ".join(f"{float(v):.12g}" for v in values) + ")"


def format_yaml_list(values: Sequence[float]) -> str:
    return "[" + ", ".join(f"{float(v):.12g}" for v in values) + "]"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run_command(command: Sequence[str], cwd: Optional[Path] = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        cwd=str(cwd) if cwd else None,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=check,
    )


def strip_namespace(root: ET.Element) -> None:
    for element in root.iter():
        if "}" in element.tag:
            element.tag = element.tag.split("}", 1)[1]


def expand_or_select_urdf(
    description_pkg: Path,
    explicit_urdf: Optional[Path] = None,
) -> Tuple[Path, Optional[tempfile.TemporaryDirectory[str]], Path]:
    """Return (parseable_urdf, temporary_owner, source_path).

    The launch stack normally consumes Xacro, so a usable Xacro is preferred
    over a possibly stale checked-in flat URDF.  The temporary directory is
    kept alive only while parse_robot_spec reads the expanded model.
    """

    def expand_xacro(
        xacro_file: Path,
    ) -> Tuple[Path, tempfile.TemporaryDirectory[str], Path]:
        if shutil.which("xacro") is None:
            raise MigrationError(
                f"Cannot expand {xacro_file}: xacro is unavailable. "
                "Run: sudo apt install ros-jazzy-xacro, or pass an explicit flat URDF."
            )
        temporary = tempfile.TemporaryDirectory(prefix="macrobot_serial2r_")
        output = Path(temporary.name) / "macrobot_expanded.urdf"
        try:
            result = run_command(["xacro", str(xacro_file)], cwd=description_pkg)
        except subprocess.CalledProcessError as exc:
            temporary.cleanup()
            raise MigrationError(
                f"Xacro expansion failed for {xacro_file}:\n{exc.stdout or exc}"
            ) from exc
        output.write_text(result.stdout, encoding="utf-8")
        return output, temporary, xacro_file

    if explicit_urdf is not None:
        selected = explicit_urdf.expanduser().resolve()
        if not selected.exists():
            raise MigrationError(f"Explicit URDF/Xacro does not exist: {selected}")
        if selected.suffix == ".xacro":
            return expand_xacro(selected)
        try:
            ET.parse(selected)
        except ET.ParseError as exc:
            raise MigrationError(f"Explicit URDF is not valid XML: {selected}: {exc}") from exc
        return selected, None, selected

    candidates = (
        description_pkg / "urdf" / "macrobot_full_visual.urdf.xacro",
        description_pkg / "urdf" / "macrobot_full_exact_gripper.urdf.xacro",
        description_pkg / "urdf" / "macrobot_arm_kinematic.urdf.xacro",
    )
    xacro_file = next((path for path in candidates if path.exists()), None)
    if xacro_file is not None and shutil.which("xacro") is not None:
        return expand_xacro(xacro_file)

    flat = description_pkg / "urdf" / "macrobot.urdf"
    if flat.exists():
        try:
            root = ET.parse(flat).getroot()
            strip_namespace(root)
            names = {joint.get("name") for joint in root.findall("joint")}
            if {"arm_lift_joint", "wrist_pitch_joint", "gripper_joint"}.issubset(names):
                return flat, None, flat
        except ET.ParseError:
            pass

    if xacro_file is not None:
        raise MigrationError(
            f"A serial-2R Xacro exists at {xacro_file}, but xacro is unavailable and "
            "no usable flat urdf/macrobot.urdf was found."
        )
    raise MigrationError("No usable flat URDF or serial-2R Xacro was found")


def load_model_revision(description_pkg: Path) -> str:
    revision_file = description_pkg / "config" / "collision_model_revision.txt"
    if revision_file.exists():
        value = revision_file.read_text(encoding="utf-8").strip()
        if value:
            return value
    kinematics = description_pkg / "config" / "kinematics.yaml"
    if kinematics.exists():
        raw = yaml.safe_load(kinematics.read_text(encoding="utf-8")) or {}
        params = extract_ros_parameters(raw)
        value = params.get("model_revision")
        if value:
            return str(value)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"macrobot-serial-2r-{stamp}"


def extract_joint(element: ET.Element, defaults: Tuple[float, float]) -> JointSpec:
    name = element.get("name") or ""
    joint_type = element.get("type") or ""
    parent_node = element.find("parent")
    child_node = element.find("child")
    if parent_node is None or child_node is None:
        raise MigrationError(f"Joint {name} lacks parent or child")
    origin = element.find("origin")
    axis = element.find("axis")
    limit = element.find("limit")
    mimic = element.find("mimic")
    lower = float(limit.get("lower", defaults[0])) if limit is not None else defaults[0]
    upper = float(limit.get("upper", defaults[1])) if limit is not None else defaults[1]
    return JointSpec(
        name=name,
        joint_type=joint_type,
        parent=parent_node.get("link") or "",
        child=child_node.get("link") or "",
        origin_xyz=parse_vec(origin.get("xyz") if origin is not None else None),
        origin_rpy=parse_vec(origin.get("rpy") if origin is not None else None),
        axis=parse_vec(axis.get("xyz") if axis is not None else None, (0.0, 0.0, 1.0)),
        lower=lower,
        upper=upper,
        mimic_joint=mimic.get("joint") if mimic is not None else None,
        mimic_multiplier=float(mimic.get("multiplier", "1")) if mimic is not None else 1.0,
        mimic_offset=float(mimic.get("offset", "0")) if mimic is not None else 0.0,
    )


def parse_robot_spec(description_pkg: Path, explicit_urdf: Optional[Path] = None) -> RobotSpec:
    parse_path, temporary, source_path = expand_or_select_urdf(description_pkg, explicit_urdf)
    try:
        root = ET.parse(parse_path).getroot()
        strip_namespace(root)
        robot_name = root.get("name") or "macrobot"
        joints_by_name = {element.get("name"): element for element in root.findall("joint")}
        missing = [name for name in ("arm_lift_joint", "wrist_pitch_joint", "gripper_joint") if name not in joints_by_name]
        if missing:
            raise MigrationError(f"Current description lacks logical joints: {missing}")
        legacy_present = sorted(name for name in LEGACY_ARM_JOINTS if name in joints_by_name)
        if legacy_present:
            raise MigrationError(
                "The selected description still contains the legacy four-bar arm joints: "
                + ", ".join(legacy_present)
            )
        shoulder = extract_joint(joints_by_name["arm_lift_joint"], (-1.0, 1.0))
        wrist = extract_joint(joints_by_name["wrist_pitch_joint"], (-1.3, 1.3))
        gripper = extract_joint(joints_by_name["gripper_joint"], (0.0, math.pi / 2.0))
        if shoulder.parent != "base_link":
            raise MigrationError(f"arm_lift_joint parent must be base_link, got {shoulder.parent}")
        if shoulder.child != wrist.parent:
            raise MigrationError(
                f"Serial chain is broken: shoulder child {shoulder.child} != wrist parent {wrist.parent}"
            )
        grasp_element = next(
            (
                element
                for element in root.findall("joint")
                if (element.find("child") is not None and element.find("child").get("link") in {"grasp_nominal", "grasp_frame"})
            ),
            None,
        )
        if grasp_element is None:
            raise MigrationError("No fixed joint to grasp_nominal or grasp_frame was found")
        grasp = extract_joint(grasp_element, (0.0, 0.0))
        if grasp.parent != wrist.child:
            raise MigrationError(
                f"Grasp frame parent must be {wrist.child}, got {grasp.parent}. "
                "Update the script or URDF before migrating."
            )
        mimics: Dict[str, Tuple[str, float, float]] = {}
        for name, element in joints_by_name.items():
            if name is None:
                continue
            mimic = element.find("mimic")
            if mimic is None:
                continue
            mimics[name] = (
                mimic.get("joint") or "",
                float(mimic.get("multiplier", "1")),
                float(mimic.get("offset", "0")),
            )
        wheels = tuple(
            name
            for name in (
                "front_left_wheel_joint",
                "back_left_wheel_joint",
                "front_right_wheel_joint",
                "back_right_wheel_joint",
            )
            if name in joints_by_name
        )

        r_shoulder = rpy_matrix(shoulder.origin_rpy)
        shoulder_axis_base = normalized(mat_vec(r_shoulder, shoulder.axis))
        r_wrist_zero = mat_mul(r_shoulder, rpy_matrix(wrist.origin_rpy))
        wrist_axis_base = normalized(mat_vec(r_wrist_zero, wrist.axis))
        alignment = dot(shoulder_axis_base, wrist_axis_base)
        if abs(alignment) < 0.999:
            raise MigrationError(
                "The two arm axes are not parallel enough for the serial planar 2R solver: "
                f"dot={alignment:.9f}"
            )

        wrist_point = vec_add(shoulder.origin_xyz, mat_vec(r_shoulder, wrist.origin_xyz))
        zero_grasp = vec_add(wrist_point, mat_vec(r_wrist_zero, grasp.origin_xyz))

        return RobotSpec(
            robot_name=robot_name,
            model_revision=load_model_revision(description_pkg),
            urdf_path=source_path,
            links=tuple(element.get("name") or "" for element in root.findall("link")),
            shoulder=shoulder,
            wrist=wrist,
            gripper=gripper,
            grasp_joint=grasp,
            mimics=mimics,
            wheel_joints=wheels,
            zero_grasp_xyz=zero_grasp,
            shoulder_axis_base=shoulder_axis_base,
            wrist_axis_base_zero=wrist_axis_base,
            axis_alignment=alignment,
        )
    finally:
        if temporary is not None:
            temporary.cleanup()


def extract_ros_parameters(raw: Mapping[str, Any]) -> MutableMapping[str, Any]:
    if "/**" in raw and isinstance(raw["/**"], Mapping):
        block = raw["/**"]
        if isinstance(block.get("ros__parameters"), MutableMapping):
            return block["ros__parameters"]  # type: ignore[return-value]
    for value in raw.values():
        if isinstance(value, Mapping) and isinstance(value.get("ros__parameters"), MutableMapping):
            return value["ros__parameters"]  # type: ignore[return-value]
    if isinstance(raw.get("ros__parameters"), MutableMapping):
        return raw["ros__parameters"]  # type: ignore[return-value]
    if isinstance(raw, MutableMapping):
        return raw
    raise MigrationError("YAML does not contain a mutable ROS parameter mapping")


def python_literal_mapping(mapping: Mapping[str, Tuple[str, float, float]]) -> str:
    lines = ["{"]
    for child, (master, multiplier, offset) in sorted(mapping.items()):
        lines.append(f"    {child!r}: ({master!r}, {multiplier:.12g}, {offset:.12g}),")
    lines.append("}")
    return "\n".join(lines)


def render_model_py(spec: RobotSpec) -> str:
    template = r'''"""Serial two-axis MacRobot arm kinematics.

Generated by migrate_four_bar_to_serial2r.py from the active URDF.
The public logical names remain arm_lift_joint, wrist_pitch_joint and
 gripper_joint, but q2 is now an independent wrist coordinate. No arm
four-bar closure or q1+q2 actuator coupling is used.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import List, Optional, Sequence, Tuple

Vec3 = Tuple[float, float, float]
Mat3 = Tuple[Tuple[float, float, float], Tuple[float, float, float], Tuple[float, float, float]]


def normalize_angle(angle: float) -> float:
    return math.atan2(math.sin(angle), math.cos(angle))


def _dot(a: Vec3, b: Vec3) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _add(a: Vec3, b: Vec3) -> Vec3:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _sub(a: Vec3, b: Vec3) -> Vec3:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _scale(v: Vec3, scale: float) -> Vec3:
    return (v[0] * scale, v[1] * scale, v[2] * scale)


def _cross(a: Vec3, b: Vec3) -> Vec3:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _norm(v: Vec3) -> float:
    return math.sqrt(_dot(v, v))


def _normalized(v: Vec3) -> Vec3:
    length = _norm(v)
    if length <= 1e-12:
        raise ValueError(f"Zero-length vector: {v}")
    return _scale(v, 1.0 / length)


def _mat_mul(a: Mat3, b: Mat3) -> Mat3:
    return tuple(
        tuple(sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3))
        for i in range(3)
    )  # type: ignore[return-value]


def _mat_vec(matrix: Mat3, vector: Vec3) -> Vec3:
    return tuple(
        sum(matrix[i][k] * vector[k] for k in range(3)) for i in range(3)
    )  # type: ignore[return-value]


def _rpy_matrix(rpy: Vec3) -> Mat3:
    roll, pitch, yaw = rpy
    cr, sr = math.cos(roll), math.sin(roll)
    cp, sp = math.cos(pitch), math.sin(pitch)
    cy, sy = math.cos(yaw), math.sin(yaw)
    rx: Mat3 = ((1.0, 0.0, 0.0), (0.0, cr, -sr), (0.0, sr, cr))
    ry: Mat3 = ((cp, 0.0, sp), (0.0, 1.0, 0.0), (-sp, 0.0, cp))
    rz: Mat3 = ((cy, -sy, 0.0), (sy, cy, 0.0), (0.0, 0.0, 1.0))
    return _mat_mul(_mat_mul(rz, ry), rx)


def _axis_angle(axis: Vec3, angle: float) -> Mat3:
    x, y, z = _normalized(axis)
    c, s, t = math.cos(angle), math.sin(angle), 1.0 - math.cos(angle)
    return (
        (t * x * x + c, t * x * y - s * z, t * x * z + s * y),
        (t * x * y + s * z, t * y * y + c, t * y * z - s * x),
        (t * x * z - s * y, t * y * z + s * x, t * z * z + c),
    )


def _matrix_to_quaternion(matrix: Mat3) -> Tuple[float, float, float, float]:
    trace = matrix[0][0] + matrix[1][1] + matrix[2][2]
    if trace > 0.0:
        scale = math.sqrt(trace + 1.0) * 2.0
        qw = 0.25 * scale
        qx = (matrix[2][1] - matrix[1][2]) / scale
        qy = (matrix[0][2] - matrix[2][0]) / scale
        qz = (matrix[1][0] - matrix[0][1]) / scale
    elif matrix[0][0] > matrix[1][1] and matrix[0][0] > matrix[2][2]:
        scale = math.sqrt(1.0 + matrix[0][0] - matrix[1][1] - matrix[2][2]) * 2.0
        qw = (matrix[2][1] - matrix[1][2]) / scale
        qx = 0.25 * scale
        qy = (matrix[0][1] + matrix[1][0]) / scale
        qz = (matrix[0][2] + matrix[2][0]) / scale
    elif matrix[1][1] > matrix[2][2]:
        scale = math.sqrt(1.0 + matrix[1][1] - matrix[0][0] - matrix[2][2]) * 2.0
        qw = (matrix[0][2] - matrix[2][0]) / scale
        qx = (matrix[0][1] + matrix[1][0]) / scale
        qy = 0.25 * scale
        qz = (matrix[1][2] + matrix[2][1]) / scale
    else:
        scale = math.sqrt(1.0 + matrix[2][2] - matrix[0][0] - matrix[1][1]) * 2.0
        qw = (matrix[1][0] - matrix[0][1]) / scale
        qx = (matrix[0][2] + matrix[2][0]) / scale
        qy = (matrix[1][2] + matrix[2][1]) / scale
        qz = 0.25 * scale
    length = math.sqrt(qx * qx + qy * qy + qz * qz + qw * qw)
    return (qx / length, qy / length, qz / length, qw / length)


def _matrix_to_rpy(matrix: Mat3) -> Vec3:
    sin_pitch = max(-1.0, min(1.0, -matrix[2][0]))
    pitch = math.asin(sin_pitch)
    if abs(math.cos(pitch)) > 1e-9:
        roll = math.atan2(matrix[2][1], matrix[2][2])
        yaw = math.atan2(matrix[1][0], matrix[0][0])
    else:
        roll = math.atan2(-matrix[1][2], matrix[1][1])
        yaw = 0.0
    return (roll, pitch, yaw)


def _wrapped_values(angle: float, lower: float, upper: float) -> List[float]:
    output: List[float] = []
    for turns in range(-2, 3):
        candidate = angle + 2.0 * math.pi * turns
        if lower - 1e-9 <= candidate <= upper + 1e-9:
            output.append(candidate)
    return output


@dataclass(frozen=True)
class ArmGeometry:
    shoulder_origin_xyz: Vec3 = @@SHOULDER_XYZ@@
    shoulder_origin_rpy: Vec3 = @@SHOULDER_RPY@@
    shoulder_axis: Vec3 = @@SHOULDER_AXIS@@
    wrist_origin_xyz: Vec3 = @@WRIST_XYZ@@
    wrist_origin_rpy: Vec3 = @@WRIST_RPY@@
    wrist_axis: Vec3 = @@WRIST_AXIS@@
    grasp_origin_xyz: Vec3 = @@GRASP_XYZ@@
    grasp_origin_rpy: Vec3 = @@GRASP_RPY@@
    gripper_open_gap_m: float = 0.070
    gripper_closed_gap_m: float = 0.010


@dataclass(frozen=True)
class JointLimits:
    arm_lift_min: float = @@Q1_MIN@@
    arm_lift_max: float = @@Q1_MAX@@
    wrist_pitch_min: float = @@Q2_MIN@@
    wrist_pitch_max: float = @@Q2_MAX@@
    gripper_min: float = @@Q3_MIN@@
    gripper_max: float = @@Q3_MAX@@

    def contains(self, q1: float, q2: float, q3: float = 0.0) -> bool:
        return (
            self.arm_lift_min <= q1 <= self.arm_lift_max
            and self.wrist_pitch_min <= q2 <= self.wrist_pitch_max
            and self.gripper_min <= q3 <= self.gripper_max
        )


@dataclass(frozen=True)
class ToolPose2D:
    """Backward-compatible name for the full 3D tool pose."""

    x: float
    y: float
    z: float
    roll: float
    pitch: float
    yaw: float
    qx: float
    qy: float
    qz: float
    qw: float


@dataclass(frozen=True)
class IKSolution:
    q1: float
    q2: float
    position_error: float
    seed_distance: float
    plane_error_m: float = 0.0
    in_plane_error_m: float = 0.0


class MacRobotArmModel:
    """Exact URDF-based planar serial 2R kinematics."""

    def __init__(
        self,
        geometry: ArmGeometry = ArmGeometry(),
        limits: JointLimits = JointLimits(),
        max_plane_error_m: float = 0.030,
        ik_tolerance_m: float = 1e-5,
    ) -> None:
        self.geometry = geometry
        self.limits = limits
        self.max_plane_error_m = max(0.0, float(max_plane_error_m))
        self.ik_tolerance_m = max(1e-8, float(ik_tolerance_m))

        g = geometry
        self._r_shoulder_origin = _rpy_matrix(g.shoulder_origin_rpy)
        self._r_wrist_origin = _rpy_matrix(g.wrist_origin_rpy)
        self._r_grasp_origin = _rpy_matrix(g.grasp_origin_rpy)
        self._normal = _normalized(_mat_vec(self._r_shoulder_origin, g.shoulder_axis))

        r_wrist_zero = _mat_mul(self._r_shoulder_origin, self._r_wrist_origin)
        wrist_axis_base = _normalized(_mat_vec(r_wrist_zero, g.wrist_axis))
        alignment = _dot(self._normal, wrist_axis_base)
        if abs(alignment) < 0.999:
            raise ValueError(
                "Serial 2R solver requires parallel arm axes; "
                f"axis dot product is {alignment:.9f}"
            )
        self._wrist_axis_sign = 1.0 if alignment >= 0.0 else -1.0

        v1 = _mat_vec(self._r_shoulder_origin, g.wrist_origin_xyz)
        v2 = _mat_vec(r_wrist_zero, g.grasp_origin_xyz)
        self._normal_offset = _dot(v1, self._normal) + _dot(v2, self._normal)
        v1_planar = _sub(v1, _scale(self._normal, _dot(v1, self._normal)))
        v2_planar = _sub(v2, _scale(self._normal, _dot(v2, self._normal)))
        self._l1 = _norm(v1_planar)
        self._l2 = _norm(v2_planar)
        if self._l1 <= 1e-8 or self._l2 <= 1e-8:
            raise ValueError("Degenerate serial 2R link geometry")
        self._e1 = _scale(v1_planar, 1.0 / self._l1)
        self._e2 = _normalized(_cross(self._normal, self._e1))
        self._beta = math.atan2(_dot(v2_planar, self._e2), _dot(v2_planar, self._e1))
        self._nominal_y = self.forward(0.0, 0.0, 0.0).y

    @property
    def arm_plane_normal(self) -> Vec3:
        return self._normal

    @property
    def wrist_axis_sign(self) -> float:
        return self._wrist_axis_sign

    def gripper_link_transform(self, q1: float, q2: float) -> Tuple[Vec3, Mat3]:
        g = self.geometry
        r1 = _mat_mul(self._r_shoulder_origin, _axis_angle(g.shoulder_axis, q1))
        wrist_position = _add(g.shoulder_origin_xyz, _mat_vec(r1, g.wrist_origin_xyz))
        r2 = _mat_mul(
            _mat_mul(r1, self._r_wrist_origin),
            _axis_angle(g.wrist_axis, q2),
        )
        return wrist_position, r2

    def forward(self, q1: float, q2: float, q3: float = 0.0) -> ToolPose2D:
        del q3  # grasp_nominal is fixed to gripper_link in the active URDF.
        position, rotation = self.gripper_link_transform(q1, q2)
        position = _add(position, _mat_vec(rotation, self.geometry.grasp_origin_xyz))
        rotation = _mat_mul(rotation, self._r_grasp_origin)
        roll, pitch, yaw = _matrix_to_rpy(rotation)
        qx, qy, qz, qw = _matrix_to_quaternion(rotation)
        return ToolPose2D(position[0], position[1], position[2], roll, pitch, yaw, qx, qy, qz, qw)

    def inverse_xyz(
        self,
        x: float,
        y: float,
        z: float,
        seed: Optional[Tuple[float, float]] = None,
        seed_weight: float = 0.001,
        gripper_q: float = 0.0,
        max_plane_error_m: Optional[float] = None,
    ) -> List[IKSolution]:
        if not self.limits.gripper_min <= gripper_q <= self.limits.gripper_max:
            return []
        rel = _sub((float(x), float(y), float(z)), self.geometry.shoulder_origin_xyz)
        normal_component = _dot(rel, self._normal)
        plane_error = normal_component - self._normal_offset
        allowed_plane_error = self.max_plane_error_m if max_plane_error_m is None else max(0.0, float(max_plane_error_m))
        if abs(plane_error) > allowed_plane_error:
            return []

        target_u = _dot(rel, self._e1)
        target_v = _dot(rel, self._e2)
        radius_sq = target_u * target_u + target_v * target_v
        cosine_delta = (radius_sq - self._l1 * self._l1 - self._l2 * self._l2) / (2.0 * self._l1 * self._l2)
        if cosine_delta < -1.0 - 1e-9 or cosine_delta > 1.0 + 1e-9:
            return []
        cosine_delta = max(-1.0, min(1.0, cosine_delta))
        delta_abs = math.acos(cosine_delta)

        solutions: List[IKSolution] = []
        seen = set()
        for delta in (delta_abs, -delta_abs):
            q1_base = math.atan2(target_v, target_u) - math.atan2(
                self._l2 * math.sin(delta),
                self._l1 + self._l2 * math.cos(delta),
            )
            q2_base = (delta - self._beta) / self._wrist_axis_sign
            for q1 in _wrapped_values(q1_base, self.limits.arm_lift_min, self.limits.arm_lift_max):
                for q2 in _wrapped_values(q2_base, self.limits.wrist_pitch_min, self.limits.wrist_pitch_max):
                    if not self.limits.contains(q1, q2, gripper_q):
                        continue
                    key = (round(q1, 10), round(q2, 10))
                    if key in seen:
                        continue
                    seen.add(key)
                    pose = self.forward(q1, q2, gripper_q)
                    error_vector = (pose.x - x, pose.y - y, pose.z - z)
                    in_plane_error = math.hypot(_dot(error_vector, self._e1), _dot(error_vector, self._e2))
                    if in_plane_error > max(1e-4, self.ik_tolerance_m * 10.0):
                        continue
                    position_error = _norm(error_vector)
                    seed_distance = 0.0 if seed is None else math.hypot(
                        normalize_angle(q1 - seed[0]),
                        normalize_angle(q2 - seed[1]),
                    )
                    solutions.append(
                        IKSolution(
                            q1=q1,
                            q2=q2,
                            position_error=position_error,
                            seed_distance=seed_distance,
                            plane_error_m=plane_error,
                            in_plane_error_m=in_plane_error,
                        )
                    )
        solutions.sort(
            key=lambda item: (
                item.in_plane_error_m + seed_weight * item.seed_distance,
                abs(item.plane_error_m),
                item.seed_distance,
            )
        )
        return solutions

    def inverse(
        self,
        x: float,
        z: float,
        seed: Optional[Tuple[float, float]] = None,
        seed_weight: float = 0.001,
        gripper_q: float = 0.0,
    ) -> List[IKSolution]:
        """Compatibility wrapper for callers that still provide only X/Z."""
        return self.inverse_xyz(x, self._nominal_y, z, seed, seed_weight, gripper_q)

    def gripper_gap(self, q3: float) -> float:
        limits = self.limits
        if limits.gripper_max <= limits.gripper_min:
            return self.geometry.gripper_open_gap_m
        ratio = (q3 - limits.gripper_min) / (limits.gripper_max - limits.gripper_min)
        ratio = min(1.0, max(0.0, ratio))
        blend = math.cos(0.5 * math.pi * ratio)
        return self.geometry.gripper_closed_gap_m + (
            self.geometry.gripper_open_gap_m - self.geometry.gripper_closed_gap_m
        ) * blend

    @staticmethod
    def full_visual_joint_positions(
        q1: float,
        q2: float,
        q3: float = 0.0,
        lift_servo_multiplier: float = 1.0,
        tilt_servo_multiplier: float = 1.0,
        gripper_servo_multiplier: float = 2.0,
    ) -> dict[str, float]:
        """Compatibility mapping with independent q2; no arm passive joints."""
        return {
            "arm_lift_joint": q1,
            "wrist_pitch_joint": q2,
            "gripper_joint": q3,
            "lift_servo": lift_servo_multiplier * q1,
            "tilt_servo": tilt_servo_multiplier * q2,
            "gripper_servo": gripper_servo_multiplier * q3,
            "gripper_left_gear": -q3,
            "gripper_right_gear": q3,
            "gripper_left_addition": -q3,
            "gripper_right_addition": q3,
            "gripper_left_clamp": q3,
            "gripper_right_clamp": -q3,
        }
'''
    replacements = {
        "@@SHOULDER_XYZ@@": format_tuple(spec.shoulder.origin_xyz),
        "@@SHOULDER_RPY@@": format_tuple(spec.shoulder.origin_rpy),
        "@@SHOULDER_AXIS@@": format_tuple(spec.shoulder.axis),
        "@@WRIST_XYZ@@": format_tuple(spec.wrist.origin_xyz),
        "@@WRIST_RPY@@": format_tuple(spec.wrist.origin_rpy),
        "@@WRIST_AXIS@@": format_tuple(spec.wrist.axis),
        "@@GRASP_XYZ@@": format_tuple(spec.grasp_joint.origin_xyz),
        "@@GRASP_RPY@@": format_tuple(spec.grasp_joint.origin_rpy),
        "@@Q1_MIN@@": f"{spec.shoulder.lower:.12g}",
        "@@Q1_MAX@@": f"{spec.shoulder.upper:.12g}",
        "@@Q2_MIN@@": f"{spec.wrist.lower:.12g}",
        "@@Q2_MAX@@": f"{spec.wrist.upper:.12g}",
        "@@Q3_MIN@@": f"{spec.gripper.lower:.12g}",
        "@@Q3_MAX@@": f"{spec.gripper.upper:.12g}",
    }
    for key, value in replacements.items():
        template = template.replace(key, value)
    return template


def geometry_parameter_declarations(spec: RobotSpec, indent: str = "        ") -> str:
    rows = (
        ("shoulder_origin_xyz", spec.shoulder.origin_xyz),
        ("shoulder_origin_rpy", spec.shoulder.origin_rpy),
        ("shoulder_axis", spec.shoulder.axis),
        ("wrist_origin_xyz", spec.wrist.origin_xyz),
        ("wrist_origin_rpy", spec.wrist.origin_rpy),
        ("wrist_axis", spec.wrist.axis),
        ("grasp_origin_xyz", spec.grasp_joint.origin_xyz),
        ("grasp_origin_rpy", spec.grasp_joint.origin_rpy),
    )
    return "\n".join(
        f"{indent}self.declare_parameter({name!r}, {list(values)!r})" for name, values in rows
    )


def render_linkage_state_node(spec: RobotSpec) -> str:
    mimic_literal = python_literal_mapping(spec.mimics)
    wheel_literal = repr(list(spec.wheel_joints))
    declarations = geometry_parameter_declarations(spec)
    template = r'''from __future__ import annotations

import math
from typing import Dict, Tuple

import rclpy
from geometry_msgs.msg import PoseStamped, TransformStamped
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64
from tf2_ros import TransformBroadcaster

from .model import ArmGeometry, JointLimits, MacRobotArmModel

MIMIC_MAP = @@MIMIC_MAP@@
WHEEL_JOINTS = @@WHEEL_JOINTS@@


def _vector_parameter(node: Node, name: str) -> Tuple[float, float, float]:
    values = tuple(float(value) for value in node.get_parameter(name).value)
    if len(values) != 3:
        raise ValueError(f"{name} must contain three numbers")
    return values  # type: ignore[return-value]


class LinkageStateNode(Node):
    """Publish serial-2R logical state, exact tool pose, and gripper mimics."""

    def __init__(self) -> None:
        super().__init__("macrobot_linkage_state_node")
        self.declare_parameter("model_revision", @@MODEL_REVISION@@)
        self.declare_parameter("base_frame", "base_link")
        self.declare_parameter("tool_frame", "grasp_frame")
        self.declare_parameter("logical_state_topic", "/macrobot/arm/logical_joint_states")
        self.declare_parameter("full_joint_state_topic", "/joint_states")
        self.declare_parameter("tool_pose_topic", "/macrobot/arm/tool_pose")
        self.declare_parameter("gripper_gap_topic", "/macrobot/gripper/gap")
        self.declare_parameter("publish_full_joint_states", True)
        self.declare_parameter("publish_mimic_joint_states", True)
        self.declare_parameter("publish_rate", 30.0)
@@GEOMETRY_DECLARATIONS@@
        self.declare_parameter("arm_lift_min", @@Q1_MIN@@)
        self.declare_parameter("arm_lift_max", @@Q1_MAX@@)
        self.declare_parameter("wrist_pitch_min", @@Q2_MIN@@)
        self.declare_parameter("wrist_pitch_max", @@Q2_MAX@@)
        self.declare_parameter("gripper_min", @@Q3_MIN@@)
        self.declare_parameter("gripper_max", @@Q3_MAX@@)
        self.declare_parameter("gripper_open_gap_m", 0.070)
        self.declare_parameter("gripper_closed_gap_m", 0.010)
        self.declare_parameter("max_plane_error_m", 0.030)

        geometry = ArmGeometry(
            shoulder_origin_xyz=_vector_parameter(self, "shoulder_origin_xyz"),
            shoulder_origin_rpy=_vector_parameter(self, "shoulder_origin_rpy"),
            shoulder_axis=_vector_parameter(self, "shoulder_axis"),
            wrist_origin_xyz=_vector_parameter(self, "wrist_origin_xyz"),
            wrist_origin_rpy=_vector_parameter(self, "wrist_origin_rpy"),
            wrist_axis=_vector_parameter(self, "wrist_axis"),
            grasp_origin_xyz=_vector_parameter(self, "grasp_origin_xyz"),
            grasp_origin_rpy=_vector_parameter(self, "grasp_origin_rpy"),
            gripper_open_gap_m=float(self.get_parameter("gripper_open_gap_m").value),
            gripper_closed_gap_m=float(self.get_parameter("gripper_closed_gap_m").value),
        )
        limits = JointLimits(
            arm_lift_min=float(self.get_parameter("arm_lift_min").value),
            arm_lift_max=float(self.get_parameter("arm_lift_max").value),
            wrist_pitch_min=float(self.get_parameter("wrist_pitch_min").value),
            wrist_pitch_max=float(self.get_parameter("wrist_pitch_max").value),
            gripper_min=float(self.get_parameter("gripper_min").value),
            gripper_max=float(self.get_parameter("gripper_max").value),
        )
        self.model = MacRobotArmModel(
            geometry,
            limits,
            max_plane_error_m=float(self.get_parameter("max_plane_error_m").value),
        )
        self.base_frame = str(self.get_parameter("base_frame").value)
        self.tool_frame = str(self.get_parameter("tool_frame").value)
        self.publish_full = bool(self.get_parameter("publish_full_joint_states").value)
        self.publish_mimics = bool(self.get_parameter("publish_mimic_joint_states").value)
        self.q1 = 0.0
        self.q2 = 0.0
        self.q3 = 0.0

        logical_topic = str(self.get_parameter("logical_state_topic").value)
        full_topic = str(self.get_parameter("full_joint_state_topic").value)
        self.create_subscription(JointState, logical_topic, self.logical_callback, 10)
        self.joint_pub = self.create_publisher(JointState, full_topic, 10) if self.publish_full else None
        self.tool_pub = self.create_publisher(
            PoseStamped, str(self.get_parameter("tool_pose_topic").value), 10
        )
        self.gap_pub = self.create_publisher(
            Float64, str(self.get_parameter("gripper_gap_topic").value), 10
        )
        self.tf_broadcaster = TransformBroadcaster(self)
        rate = max(1.0, float(self.get_parameter("publish_rate").value))
        self.create_timer(1.0 / rate, self.publish_state)
        self.get_logger().info(
            f"Serial-2R state publisher ready; revision={self.get_parameter('model_revision').value}"
        )

    def logical_callback(self, msg: JointState) -> None:
        values: Dict[str, float] = dict(zip(msg.name, msg.position))
        candidate = (
            float(values.get("arm_lift_joint", self.q1)),
            float(values.get("wrist_pitch_joint", self.q2)),
            float(values.get("gripper_joint", self.q3)),
        )
        if not all(math.isfinite(value) for value in candidate):
            self.get_logger().warning("Rejected non-finite logical joint state")
            return
        if not self.model.limits.contains(*candidate):
            self.get_logger().warning(
                f"Rejected logical state outside limits: q={candidate}"
            )
            return
        self.q1, self.q2, self.q3 = candidate

    @staticmethod
    def _resolved_joint_positions(q1: float, q2: float, q3: float) -> Dict[str, float]:
        resolved: Dict[str, float] = {
            "arm_lift_joint": q1,
            "wrist_pitch_joint": q2,
            "gripper_joint": q3,
        }
        pending = dict(MIMIC_MAP)
        while pending:
            progressed = False
            for child, (master, multiplier, offset) in list(pending.items()):
                if master not in resolved:
                    continue
                resolved[child] = multiplier * resolved[master] + offset
                del pending[child]
                progressed = True
            if not progressed:
                break
        return resolved

    def publish_state(self) -> None:
        now = self.get_clock().now().to_msg()
        if self.joint_pub is not None:
            positions = self._resolved_joint_positions(self.q1, self.q2, self.q3)
            names = ["arm_lift_joint", "wrist_pitch_joint", "gripper_joint"]
            if self.publish_mimics:
                names.extend(name for name in sorted(MIMIC_MAP) if name not in names)
            names.extend(name for name in WHEEL_JOINTS if name not in names)
            msg = JointState()
            msg.header.stamp = now
            msg.name = names
            msg.position = [positions.get(name, 0.0) for name in names]
            self.joint_pub.publish(msg)

        pose = self.model.forward(self.q1, self.q2, self.q3)
        pmsg = PoseStamped()
        pmsg.header.stamp = now
        pmsg.header.frame_id = self.base_frame
        pmsg.pose.position.x = pose.x
        pmsg.pose.position.y = pose.y
        pmsg.pose.position.z = pose.z
        pmsg.pose.orientation.x = pose.qx
        pmsg.pose.orientation.y = pose.qy
        pmsg.pose.orientation.z = pose.qz
        pmsg.pose.orientation.w = pose.qw
        self.tool_pub.publish(pmsg)

        transform = TransformStamped()
        transform.header.stamp = now
        transform.header.frame_id = self.base_frame
        transform.child_frame_id = self.tool_frame
        transform.transform.translation.x = pose.x
        transform.transform.translation.y = pose.y
        transform.transform.translation.z = pose.z
        transform.transform.rotation = pmsg.pose.orientation
        self.tf_broadcaster.sendTransform(transform)

        gap = Float64()
        gap.data = self.model.gripper_gap(self.q3)
        self.gap_pub.publish(gap)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = LinkageStateNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
'''
    replacements = {
        "@@MIMIC_MAP@@": mimic_literal,
        "@@WHEEL_JOINTS@@": wheel_literal,
        "@@MODEL_REVISION@@": repr(spec.model_revision),
        "@@GEOMETRY_DECLARATIONS@@": declarations,
        "@@Q1_MIN@@": f"{spec.shoulder.lower:.12g}",
        "@@Q1_MAX@@": f"{spec.shoulder.upper:.12g}",
        "@@Q2_MIN@@": f"{spec.wrist.lower:.12g}",
        "@@Q2_MAX@@": f"{spec.wrist.upper:.12g}",
        "@@Q3_MIN@@": f"{spec.gripper.lower:.12g}",
        "@@Q3_MAX@@": f"{spec.gripper.upper:.12g}",
    }
    for key, value in replacements.items():
        template = template.replace(key, value)
    return template


def render_ik_node(spec: RobotSpec) -> str:
    declarations = geometry_parameter_declarations(spec)
    template = r'''from __future__ import annotations

import json
import math
from typing import Optional, Tuple

import rclpy
from geometry_msgs.msg import PointStamped
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import String

from .model import ArmGeometry, JointLimits, MacRobotArmModel


def _vector_parameter(node: Node, name: str) -> Tuple[float, float, float]:
    values = tuple(float(value) for value in node.get_parameter(name).value)
    if len(values) != 3:
        raise ValueError(f"{name} must contain three numbers")
    return values  # type: ignore[return-value]


class IKNode(Node):
    def __init__(self) -> None:
        super().__init__("macrobot_arm_ik_node")
        self.declare_parameter("model_revision", @@MODEL_REVISION@@)
        self.declare_parameter("base_frame", "base_link")
        self.declare_parameter("logical_state_topic", "/macrobot/arm/logical_joint_states")
        self.declare_parameter("target_topic", "/macrobot/arm/target_point")
        self.declare_parameter("solution_topic", "/macrobot/arm/ik_solution")
        self.declare_parameter("status_topic", "/macrobot/arm/ik_status")
        self.declare_parameter("auto_apply_ik", False)
        self.declare_parameter("seed_weight", 0.001)
        self.declare_parameter("max_plane_error_m", 0.030)
@@GEOMETRY_DECLARATIONS@@
        self.declare_parameter("arm_lift_min", @@Q1_MIN@@)
        self.declare_parameter("arm_lift_max", @@Q1_MAX@@)
        self.declare_parameter("wrist_pitch_min", @@Q2_MIN@@)
        self.declare_parameter("wrist_pitch_max", @@Q2_MAX@@)
        self.declare_parameter("gripper_min", @@Q3_MIN@@)
        self.declare_parameter("gripper_max", @@Q3_MAX@@)

        geometry = ArmGeometry(
            shoulder_origin_xyz=_vector_parameter(self, "shoulder_origin_xyz"),
            shoulder_origin_rpy=_vector_parameter(self, "shoulder_origin_rpy"),
            shoulder_axis=_vector_parameter(self, "shoulder_axis"),
            wrist_origin_xyz=_vector_parameter(self, "wrist_origin_xyz"),
            wrist_origin_rpy=_vector_parameter(self, "wrist_origin_rpy"),
            wrist_axis=_vector_parameter(self, "wrist_axis"),
            grasp_origin_xyz=_vector_parameter(self, "grasp_origin_xyz"),
            grasp_origin_rpy=_vector_parameter(self, "grasp_origin_rpy"),
        )
        limits = JointLimits(
            arm_lift_min=float(self.get_parameter("arm_lift_min").value),
            arm_lift_max=float(self.get_parameter("arm_lift_max").value),
            wrist_pitch_min=float(self.get_parameter("wrist_pitch_min").value),
            wrist_pitch_max=float(self.get_parameter("wrist_pitch_max").value),
            gripper_min=float(self.get_parameter("gripper_min").value),
            gripper_max=float(self.get_parameter("gripper_max").value),
        )
        self.model = MacRobotArmModel(
            geometry,
            limits,
            max_plane_error_m=float(self.get_parameter("max_plane_error_m").value),
        )
        self.base_frame = str(self.get_parameter("base_frame").value)
        self.auto_apply = bool(self.get_parameter("auto_apply_ik").value)
        self.seed_weight = float(self.get_parameter("seed_weight").value)
        self.seed: Optional[Tuple[float, float]] = (0.0, 0.0)
        self.gripper_q = 0.0

        logical_topic = str(self.get_parameter("logical_state_topic").value)
        self.create_subscription(JointState, logical_topic, self.state_callback, 10)
        self.create_subscription(
            PointStamped,
            str(self.get_parameter("target_topic").value),
            self.target_callback,
            10,
        )
        self.solution_pub = self.create_publisher(
            JointState, str(self.get_parameter("solution_topic").value), 10
        )
        self.apply_pub = self.create_publisher(JointState, logical_topic, 10)
        self.status_pub = self.create_publisher(
            String, str(self.get_parameter("status_topic").value), 10
        )

    def state_callback(self, msg: JointState) -> None:
        values = dict(zip(msg.name, msg.position))
        if "arm_lift_joint" in values and "wrist_pitch_joint" in values:
            self.seed = (float(values["arm_lift_joint"]), float(values["wrist_pitch_joint"]))
        if "gripper_joint" in values:
            self.gripper_q = float(values["gripper_joint"])

    def target_callback(self, msg: PointStamped) -> None:
        if msg.header.frame_id and msg.header.frame_id != self.base_frame:
            self.publish_status(False, "frame_mismatch", {
                "expected_frame": self.base_frame,
                "received_frame": msg.header.frame_id,
            })
            return
        target = (float(msg.point.x), float(msg.point.y), float(msg.point.z))
        if not all(math.isfinite(value) for value in target):
            self.publish_status(False, "non_finite_target", {"target": list(target)})
            return
        solutions = self.model.inverse_xyz(
            *target,
            seed=self.seed,
            seed_weight=self.seed_weight,
            gripper_q=self.gripper_q,
        )
        if not solutions:
            self.publish_status(False, "unreachable_or_out_of_plane", {
                "target_x": target[0],
                "target_y": target[1],
                "target_z": target[2],
                "gripper_joint": self.gripper_q,
            })
            return

        best = solutions[0]
        result = JointState()
        result.header.stamp = self.get_clock().now().to_msg()
        result.name = ["arm_lift_joint", "wrist_pitch_joint", "gripper_joint"]
        result.position = [best.q1, best.q2, self.gripper_q]
        self.solution_pub.publish(result)
        if self.auto_apply:
            self.apply_pub.publish(result)
        self.seed = (best.q1, best.q2)

        pose = self.model.forward(best.q1, best.q2, self.gripper_q)
        self.publish_status(True, "solution", {
            "model_type": "serial_2r",
            "model_revision": self.get_parameter("model_revision").value,
            "q1": best.q1,
            "q2": best.q2,
            "gripper_joint": self.gripper_q,
            "gripper_gap_m": self.model.gripper_gap(self.gripper_q),
            "plane_error_m": best.plane_error_m,
            "in_plane_error_m": best.in_plane_error_m,
            "position_error_m": best.position_error,
            "seed_distance": best.seed_distance,
            "target_x": target[0],
            "target_y": target[1],
            "target_z": target[2],
            "solution_x": pose.x,
            "solution_y": pose.y,
            "solution_z": pose.z,
            "solution_rpy": [pose.roll, pose.pitch, pose.yaw],
        })

    def publish_status(self, ok: bool, event: str, details: dict) -> None:
        message = String()
        message.data = json.dumps({"ok": ok, "event": event, **details}, ensure_ascii=False)
        self.status_pub.publish(message)
        logger = self.get_logger()
        if ok:
            logger.info(message.data)
        else:
            logger.warning(message.data)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = IKNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
'''
    replacements = {
        "@@MODEL_REVISION@@": repr(spec.model_revision),
        "@@GEOMETRY_DECLARATIONS@@": declarations,
        "@@Q1_MIN@@": f"{spec.shoulder.lower:.12g}",
        "@@Q1_MAX@@": f"{spec.shoulder.upper:.12g}",
        "@@Q2_MIN@@": f"{spec.wrist.lower:.12g}",
        "@@Q2_MAX@@": f"{spec.wrist.upper:.12g}",
        "@@Q3_MIN@@": f"{spec.gripper.lower:.12g}",
        "@@Q3_MAX@@": f"{spec.gripper.upper:.12g}",
    }
    for key, value in replacements.items():
        template = template.replace(key, value)
    return template


def render_servo_mapping_py() -> str:
    return r'''"""MacRobot serial-2R logical joints to physical servo commands."""

from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
from typing import Dict, Mapping, Tuple

import yaml

JOINT_NAMES = ("arm_lift_joint", "wrist_pitch_joint", "gripper_joint")


@dataclass(frozen=True)
class ServoAxis:
    name: str
    channel: int
    zero_deg: float
    sign: float
    model_multiplier: float
    command_min_deg: float
    command_max_deg: float
    pulse_min_us: float = 500.0
    pulse_center_us: float = 1500.0
    pulse_max_us: float = 2500.0

    def model_angle_to_command_deg(self, model_angle_rad: float) -> float:
        return self.zero_deg + self.sign * math.degrees(self.model_multiplier * model_angle_rad)

    def within_command_limit(self, command_deg: float, tolerance_deg: float = 1e-6) -> bool:
        return self.command_min_deg - tolerance_deg <= command_deg <= self.command_max_deg + tolerance_deg

    def command_deg_to_pulse_us(self, command_deg: float) -> float:
        command_deg = min(180.0, max(0.0, float(command_deg)))
        if command_deg <= 90.0:
            ratio = command_deg / 90.0
            return self.pulse_min_us + ratio * (self.pulse_center_us - self.pulse_min_us)
        ratio = (command_deg - 90.0) / 90.0
        return self.pulse_center_us + ratio * (self.pulse_max_us - self.pulse_center_us)


@dataclass(frozen=True)
class LogicalLimits:
    q1_min: float
    q1_max: float
    q2_min: float
    q2_max: float
    q3_min: float
    q3_max: float
    home_q1: float = 0.0
    home_q2: float = 0.0
    home_q3: float = 0.0
    model_type: str = "serial_2r"
    model_revision: str = "unknown"

    @property
    def home(self) -> Tuple[float, float, float]:
        return (self.home_q1, self.home_q2, self.home_q3)

    @property
    def tool_pitch_min(self) -> float:
        """Deprecated compatibility alias; q2 is independent in serial 2R."""
        return self.q2_min

    @property
    def tool_pitch_max(self) -> float:
        return self.q2_max

    @property
    def four_bar_margin_rad(self) -> float:
        return 0.0


@dataclass(frozen=True)
class ServoMapping:
    logical_limits: LogicalLimits
    lift: ServoAxis
    tilt: ServoAxis
    gripper: ServoAxis

    def servo_commands_deg(self, q1: float, q2: float, q3: float) -> Dict[str, float]:
        return {
            "lift": self.lift.model_angle_to_command_deg(q1),
            "tilt": self.tilt.model_angle_to_command_deg(q2),
            "gripper": self.gripper.model_angle_to_command_deg(q3),
        }

    def servo_pulses_us(self, q1: float, q2: float, q3: float) -> Dict[str, float]:
        commands = self.servo_commands_deg(q1, q2, q3)
        return {
            "lift": self.lift.command_deg_to_pulse_us(commands["lift"]),
            "tilt": self.tilt.command_deg_to_pulse_us(commands["tilt"]),
            "gripper": self.gripper.command_deg_to_pulse_us(commands["gripper"]),
        }

    def command_limits_ok(self, q1: float, q2: float, q3: float) -> Tuple[bool, str]:
        commands = self.servo_commands_deg(q1, q2, q3)
        for key, axis in (("lift", self.lift), ("tilt", self.tilt), ("gripper", self.gripper)):
            if not axis.within_command_limit(commands[key]):
                return False, f"{key}_servo_limit"
        return True, "safe"


def _extract_ros_parameters(data: Mapping) -> Mapping:
    if "/**" in data:
        block = data["/**"]
        if isinstance(block, Mapping) and "ros__parameters" in block:
            return block["ros__parameters"]
    for block in data.values():
        if isinstance(block, Mapping) and "ros__parameters" in block:
            return block["ros__parameters"]
    if "ros__parameters" in data:
        return data["ros__parameters"]
    return data


def load_servo_mapping(path: str | Path) -> ServoMapping:
    config_path = Path(path).expanduser().resolve()
    if not config_path.exists():
        raise FileNotFoundError(f"Actuator configuration not found: {config_path}")
    with config_path.open("r", encoding="utf-8") as stream:
        raw = yaml.safe_load(stream) or {}
    p = _extract_ros_parameters(raw)
    limits = LogicalLimits(
        q1_min=float(p["q1_min"]), q1_max=float(p["q1_max"]),
        q2_min=float(p["q2_min"]), q2_max=float(p["q2_max"]),
        q3_min=float(p["q3_min"]), q3_max=float(p["q3_max"]),
        home_q1=float(p.get("home_q1", 0.0)),
        home_q2=float(p.get("home_q2", 0.0)),
        home_q3=float(p.get("home_q3", 0.0)),
        model_type=str(p.get("model_type", "serial_2r")),
        model_revision=str(p.get("model_revision", "unknown")),
    )

    def axis(prefix: str, default_channel: int, default_name: str) -> ServoAxis:
        return ServoAxis(
            name=default_name,
            channel=int(p.get(f"{prefix}_channel", default_channel)),
            zero_deg=float(p[f"{prefix}_zero_deg"]),
            sign=float(p[f"{prefix}_sign"]),
            model_multiplier=float(p[f"{prefix}_model_multiplier"]),
            command_min_deg=float(p[f"{prefix}_command_min_deg"]),
            command_max_deg=float(p[f"{prefix}_command_max_deg"]),
            pulse_min_us=float(p.get(f"{prefix}_pulse_min_us", 500.0)),
            pulse_center_us=float(p.get(f"{prefix}_pulse_center_us", 1500.0)),
            pulse_max_us=float(p.get(f"{prefix}_pulse_max_us", 2500.0)),
        )

    return ServoMapping(
        limits,
        axis("lift", 0, "left_mg996r_arm_lift"),
        axis("tilt", 1, "right_mg996r_wrist_pitch"),
        axis("gripper", 2, "gripper_mg90s"),
    )
'''


def replace_python_class(source: str, class_name: str, replacement: str) -> str:
    tree = ast.parse(source)
    node = next((item for item in tree.body if isinstance(item, ast.ClassDef) and item.name == class_name), None)
    if node is None or node.end_lineno is None:
        raise MigrationError(f"Class {class_name} was not found")
    lines = source.splitlines(keepends=True)
    start = node.lineno - 1
    end = node.end_lineno
    replacement_text = replacement.rstrip() + "\n\n"
    return "".join(lines[:start]) + replacement_text + "".join(lines[end:])


def serial2r_analytic_validator_class() -> str:
    return r'''class AnalyticValidator:
    def __init__(self, mapping: ServoMapping) -> None:
        self.mapping = mapping

    def validate(self, q: Q) -> ValidationResult:
        q1, q2, q3 = (float(value) for value in q)
        if not all(math.isfinite(value) for value in (q1, q2, q3)):
            return ValidationResult(False, "non_finite_joint_value")
        limits = self.mapping.logical_limits
        if not (limits.q1_min <= q1 <= limits.q1_max):
            return ValidationResult(False, "q1_logical_limit", {"q1": q1})
        if not (limits.q2_min <= q2 <= limits.q2_max):
            return ValidationResult(False, "q2_logical_limit", {"q2": q2})
        if not (limits.q3_min <= q3 <= limits.q3_max):
            return ValidationResult(False, "q3_logical_limit", {"q3": q3})

        servo_ok, servo_reason = self.mapping.command_limits_ok(q1, q2, q3)
        commands = self.mapping.servo_commands_deg(q1, q2, q3)
        if not servo_ok:
            return ValidationResult(False, servo_reason, {"servo_deg": commands})
        return ValidationResult(
            True,
            "safe",
            {
                "model_type": "serial_2r",
                "wrist_joint": q2,
                "servo_deg": commands,
                "servo_pulse_us": self.mapping.servo_pulses_us(q1, q2, q3),
            },
        )'''


def render_model_test(spec: RobotSpec) -> str:
    zero = format_tuple(spec.zero_grasp_xyz)
    return f'''import math

from macrobot_arm_kinematics.model import JointLimits, MacRobotArmModel


def test_zero_pose_matches_active_urdf():
    pose = MacRobotArmModel().forward(0.0, 0.0, 0.0)
    expected = {zero}
    actual = (pose.x, pose.y, pose.z)
    assert max(abs(a - b) for a, b in zip(actual, expected)) < 2e-6


def test_fk_ik_round_trip_serial_2r():
    model = MacRobotArmModel()
    for q1, q2 in ((0.0, 0.0), (0.20, -0.10), (-0.20, 0.15)):
        pose = model.forward(q1, q2, 0.0)
        solutions = model.inverse_xyz(pose.x, pose.y, pose.z, seed=(q1, q2))
        assert solutions
        best = solutions[0]
        reconstructed = model.forward(best.q1, best.q2, 0.0)
        assert math.dist(
            (pose.x, pose.y, pose.z),
            (reconstructed.x, reconstructed.y, reconstructed.z),
        ) < 1e-5


def test_q2_is_independent_and_four_bar_guard_is_removed():
    model = MacRobotArmModel()
    assert model.limits.contains(0.8, -1.0, 0.0)
    mapped_a = model.full_visual_joint_positions(0.25, 0.10, 0.0, 2.0, -2.0, 2.0)
    mapped_b = model.full_visual_joint_positions(-0.25, 0.10, 0.0, 2.0, -2.0, 2.0)
    assert mapped_a["tilt_servo"] == mapped_b["tilt_servo"] == -0.20


def test_joint_limits_are_independent():
    limits = JointLimits()
    assert not limits.contains(limits.arm_lift_max + 0.01, 0.0, 0.0)
    assert not limits.contains(0.0, limits.wrist_pitch_max + 0.01, 0.0)
    assert not limits.contains(0.0, 0.0, limits.gripper_max + 0.01)
'''


def render_servo_test() -> str:
    return r'''from macrobot_arm_control.servo_mapping import LogicalLimits, ServoAxis, ServoMapping


def _mapping() -> ServoMapping:
    limits = LogicalLimits(-1.0, 1.0, -1.3, 1.3, 0.0, 1.57)
    axis = lambda name, channel: ServoAxis(name, channel, 90.0, 1.0, 1.0, 0.0, 180.0)
    return ServoMapping(limits, axis("lift", 0), axis("wrist", 1), axis("gripper", 2))


def test_wrist_servo_uses_q2_only():
    mapping = _mapping()
    first = mapping.servo_commands_deg(0.5, 0.2, 0.0)["tilt"]
    second = mapping.servo_commands_deg(-0.5, 0.2, 0.0)["tilt"]
    assert first == second


def test_joint_outputs_remain_three_axis():
    commands = _mapping().servo_commands_deg(0.1, -0.2, 0.3)
    assert set(commands) == {"lift", "tilt", "gripper"}
'''


def render_serial_grasp_frame_fit() -> str:
    return r'''"""Fit a fixed grasp frame for the serial-2R arm.

The previous implementation inferred a q3-dependent endpoint with the arm
four-bar relation.  In the current model ``grasp_nominal`` is a rigid child of
``gripper_link``.  Calibration therefore estimates one constant XYZ offset in
the gripper-link frame from measurements collected at several q1/q2 poses.
"""

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
    """Deprecated compatibility container.

    Old callers may still construct this object.  Its planar four-bar values
    are intentionally ignored; the current URDF-derived MacRobotArmModel is the
    source of truth.
    """

    pivot_x: float = 0.0
    pivot_z: float = 0.0
    main_link_length: float = 0.0


def _transpose_multiply(rotation: Mat3, vector: Vec3) -> Vec3:
    return tuple(
        sum(rotation[row][column] * vector[row] for row in range(3))
        for column in range(3)
    )  # type: ignore[return-value]


def _transform_point(position: Vec3, rotation: Mat3, local: Vec3) -> Vec3:
    rotated = tuple(
        sum(rotation[row][column] * local[column] for column in range(3))
        for row in range(3)
    )
    return (
        position[0] + rotated[0],
        position[1] + rotated[1],
        position[2] + rotated[2],
    )


def base_point_to_gripper_offset(
    q1: float,
    q2: float,
    measured_x: float,
    measured_y: float,
    measured_z: float,
    model: Optional[MacRobotArmModel] = None,
) -> Vec3:
    """Convert a measured base_link point to the gripper_link frame."""
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
    """Estimate the fixed ``gripper_link -> grasp_nominal`` translation.

    Required sample keys are ``q1``, ``q2``, ``measured_x``, ``measured_y``
    and ``measured_z``.  ``measurement_frame`` may be ``base_link`` or
    ``gripper_link``; the legacy word ``wrist`` is accepted as an alias for
    ``gripper_link``.  q3 is recorded only for optional jaw-gap fitting and
    never changes the grasp-frame origin.
    """
    del reference  # retained only so old callers fail safely rather than at import time
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
        measured_z = float(raw["measured_z"])
        if "measured_y" not in raw:
            raise ValueError(
                "measured_y is required for the serial-2R 3D grasp-frame fit"
            )
        measured_y = float(raw["measured_y"])

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
            (item["local_x"], item["local_y"], item["local_z"]),
            origin,
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
'''


def render_serial_grasp_frame_test(spec: RobotSpec) -> str:
    truth = spec.grasp_joint.origin_xyz
    return f'''import math

from macrobot_arm_commissioning.grasp_frame_fit import fit_grasp_frame
from macrobot_arm_kinematics.model import MacRobotArmModel


def _base_point(model, q1, q2, local):
    position, rotation = model.gripper_link_transform(q1, q2)
    rotated = tuple(
        sum(rotation[row][column] * local[column] for column in range(3))
        for row in range(3)
    )
    return tuple(position[index] + rotated[index] for index in range(3))


def test_fixed_grasp_frame_fit_recovers_urdf_offset():
    model = MacRobotArmModel()
    truth = {format_tuple(truth)}
    samples = []
    for q1, q2, q3 in ((0.0, 0.0, 0.0), (0.20, -0.10, 0.6), (-0.18, 0.16, 1.2)):
        point = _base_point(model, q1, q2, truth)
        samples.append({{
            "q1": q1,
            "q2": q2,
            "q3": q3,
            "measurement_frame": "base_link",
            "measured_x": point[0],
            "measured_y": point[1],
            "measured_z": point[2],
        }})
    result = fit_grasp_frame(samples, model=model)
    assert math.dist(result["grasp_origin_xyz"], truth) < 1e-10
    assert result["max_error_m"] < 1e-10


def test_grasp_center_is_independent_of_q3():
    model = MacRobotArmModel()
    first = model.forward(0.15, -0.10, 0.0)
    second = model.forward(0.15, -0.10, model.limits.gripper_max)
    assert (first.x, first.y, first.z) == (second.x, second.y, second.z)
'''


def replace_python_method(
    source: str,
    class_name: str,
    method_name: str,
    replacement: str,
) -> str:
    tree = ast.parse(source)
    class_node = next(
        (item for item in tree.body if isinstance(item, ast.ClassDef) and item.name == class_name),
        None,
    )
    if class_node is None:
        raise MigrationError(f"Class {class_name} was not found")
    method = next(
        (
            item
            for item in class_node.body
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
            and item.name == method_name
        ),
        None,
    )
    if method is None or method.end_lineno is None:
        raise MigrationError(f"Method {class_name}.{method_name} was not found")
    lines = source.splitlines(keepends=True)
    indent_match = re.match(r"\s*", lines[method.lineno - 1])
    indent = indent_match.group(0) if indent_match else "    "
    body = textwrap.dedent(replacement).strip("\n")
    rendered = textwrap.indent(body, indent) + "\n\n"
    return "".join(lines[: method.lineno - 1]) + rendered + "".join(lines[method.end_lineno :])


def serial2r_grasp_frame_calibration_method() -> str:
    return r'''def grasp_frame_calibration(self) -> None:
    if not self._require_motion():
        return
    self.report.begin_section("grasp_frame_calibration_serial_2r")
    limits = self.node.mapping.logical_limits
    current = self.node.current_q

    def clamp(value: float, lower: float, upper: float) -> float:
        return min(upper, max(lower, value))

    defaults = [
        current,
        (
            clamp(current[0] + 0.15, limits.q1_min, limits.q1_max),
            clamp(current[1] - 0.10, limits.q2_min, limits.q2_max),
            current[2],
        ),
        (
            clamp(current[0] - 0.15, limits.q1_min, limits.q1_max),
            clamp(current[1] + 0.10, limits.q2_min, limits.q2_max),
            current[2],
        ),
    ]
    pose_count = max(3, ask_int("측정 자세 수", 3))
    frame = ask_text(
        "측정 좌표계(base_link 또는 gripper_link)",
        "base_link",
    )
    if frame not in {"base_link", "gripper_link"}:
        raise ValueError("measurement frame must be base_link or gripper_link")

    samples = []
    for index in range(pose_count):
        default_q = defaults[index] if index < len(defaults) else current
        q = ask_q(f"측정 자세 {{index + 1}}/{{pose_count}}", default_q)
        automatic = self._execute_and_review(q, f"serial grasp-frame sample {{index + 1}}")
        print(
            "두 clamp 사이의 실제 파지 중심을 3차원으로 측정하세요. "
            "입력 단위는 mm이며 보고서에는 m로 저장됩니다."
        )
        measured_x_mm = ask_float("측정 X", allow_blank=False)
        measured_y_mm = ask_float("측정 Y", allow_blank=False)
        measured_z_mm = ask_float("측정 Z", allow_blank=False)
        gap_mm = optional_measurement("실제 clamp 간격", "mm")
        samples.append(
            {
                "q1": q[0],
                "q2": q[1],
                "q3": q[2],
                "measurement_frame": frame,
                "measured_x": float(measured_x_mm) / 1000.0,
                "measured_y": float(measured_y_mm) / 1000.0,
                "measured_z": float(measured_z_mm) / 1000.0,
                "measured_gap": (
                    float(gap_mm) / 1000.0 if gap_mm is not None else None
                ),
                "model_tool_pose": automatic.get("tool_pose"),
                "automatic": automatic,
                "notes": ask_text("메모", "", True),
            }
        )

    fit_samples = [
        {key: value for key, value in sample.items() if value is not None}
        for sample in samples
    ]
    fitted = fit_grasp_frame(fit_samples)
    print("\\n추천 gripper_link -> grasp_nominal 고정 offset:")
    print(f"  grasp_origin_xyz: {{fitted['grasp_origin_xyz']}}")
    print(f"  rms_error_m: {{fitted['rms_error_m']}}")
    print(f"  max_error_m: {{fitted['max_error_m']}}")
    for key in ("gripper_open_gap_m", "gripper_closed_gap_m", "gap_fit_warning"):
        if key in fitted:
            print(f"  {{key}}: {{fitted[key]}}")
    print(
        "이 값은 URDF의 grasp_nominal_fixed_joint와 kinematics.yaml에 함께 반영한 뒤 "
        "MoveIt/safe-region/PICK·PLACE 경로를 다시 검증해야 합니다."
    )
    self.report.complete_section(
        "grasp_frame_calibration_serial_2r",
        {
            "samples": samples,
            "fit": fitted,
            "recommended_description_parameters": {
                "grasp_origin_xyz": fitted["grasp_origin_xyz"],
                **(
                    {"gripper_open_gap_m": fitted["gripper_open_gap_m"]}
                    if "gripper_open_gap_m" in fitted
                    else {}
                ),
                **(
                    {"gripper_closed_gap_m": fitted["gripper_closed_gap_m"]}
                    if "gripper_closed_gap_m" in fitted
                    else {}
                ),
            },
            "requires_moveit_and_safe_region_regeneration": True,
            "requires_pick_place_revalidation": True,
        },
    )'''


def patch_commissioning_cli(source: str) -> str:
    text = source.replace(
        "from .grasp_frame_fit import GeometryReference, fit_grasp_frame",
        "from .grasp_frame_fit import fit_grasp_frame",
    )
    old = '''"four_bar_parallelogram_maintained": ask_yes_no(\n                    "팔 4-bar가 평행사변형을 유지하나요?", True\n                ),'''
    new = '''"serial_2r_joint_alignment_verified": ask_yes_no(\n                    "두 직렬 관절이 의도한 평면에서 독립적으로 움직이나요?", True\n                ),'''
    if old in text:
        text = text.replace(old, new, 1)
    elif "serial_2r_joint_alignment_verified" not in text:
        raise MigrationError("Neither the legacy nor serial-2R direction-test prompt was found")
    return replace_python_method(
        text,
        "CommissioningWizard",
        "grasp_frame_calibration",
        serial2r_grasp_frame_calibration_method(),
    )


def render_arm_pipeline_launch() -> str:
    """Launch the current description without the obsolete four-bar GUI mapper."""
    return r'''from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    description_pkg = Path(get_package_share_directory("macrobot_description"))
    safe_pkg = Path(get_package_share_directory("macrobot_safe_region"))
    control_pkg = Path(get_package_share_directory("macrobot_arm_control"))

    dry_run = LaunchConfiguration("dry_run")
    require_safe_region = LaunchConfiguration("require_safe_region")
    safe_region_csv = LaunchConfiguration("safe_region_csv")
    command_home_on_start = LaunchConfiguration("command_home_on_start")
    use_sim_time = LaunchConfiguration("use_sim_time")
    start_rviz = LaunchConfiguration("start_rviz")

    actuator_file = safe_pkg / "config" / "actuator_limits.yaml"
    control_defaults = control_pkg / "config" / "control_defaults.yaml"
    kinematics_file = description_pkg / "config" / "kinematics.yaml"

    return LaunchDescription([
        DeclareLaunchArgument("dry_run", default_value="true"),
        DeclareLaunchArgument("require_safe_region", default_value="true"),
        DeclareLaunchArgument("safe_region_csv", default_value=""),
        DeclareLaunchArgument("command_home_on_start", default_value="false"),
        DeclareLaunchArgument("use_sim_time", default_value="false"),
        DeclareLaunchArgument("start_rviz", default_value="false"),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                str(description_pkg / "launch" / "runtime_description.launch.py")
            ),
            launch_arguments={"use_sim_time": use_sim_time}.items(),
        ),
        Node(
            package="macrobot_arm_kinematics",
            executable="linkage_state_node",
            name="macrobot_serial2r_state_node",
            output="screen",
            parameters=[str(kinematics_file), {"use_sim_time": use_sim_time}],
        ),
        Node(
            package="rviz2",
            executable="rviz2",
            name="rviz2",
            arguments=["-d", str(description_pkg / "rviz" / "display.rviz")],
            condition=IfCondition(start_rviz),
            output="screen",
        ),
        Node(
            package="macrobot_arm_control",
            executable="ik_validator_node",
            name="macrobot_ik_validator",
            output="screen",
            parameters=[
                str(control_defaults),
                {
                    "actuator_limits_file": str(actuator_file),
                    "safe_region_csv": safe_region_csv,
                    "require_safe_region": ParameterValue(
                        require_safe_region, value_type=bool
                    ),
                },
            ],
        ),
        Node(
            package="macrobot_arm_control",
            executable="servo_bridge_node",
            name="macrobot_arm_servo_bridge",
            output="screen",
            parameters=[
                str(control_defaults),
                {
                    "actuator_limits_file": str(actuator_file),
                    "safe_region_csv": safe_region_csv,
                    "require_safe_region": ParameterValue(
                        require_safe_region, value_type=bool
                    ),
                    "dry_run": ParameterValue(dry_run, value_type=bool),
                    "command_home_on_start": ParameterValue(
                        command_home_on_start, value_type=bool
                    ),
                },
            ],
        ),
    ])
'''


def render_commissioning_pipeline_launch() -> str:
    return r'''from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    description_pkg = Path(get_package_share_directory("macrobot_description"))
    safe_pkg = Path(get_package_share_directory("macrobot_safe_region"))
    control_pkg = Path(get_package_share_directory("macrobot_arm_control"))

    dry_run = LaunchConfiguration("dry_run")
    require_safe_region = LaunchConfiguration("require_safe_region")
    safe_region_csv = LaunchConfiguration("safe_region_csv")
    actuator_limits_file = LaunchConfiguration("actuator_limits_file")
    start_rviz = LaunchConfiguration("start_rviz")
    start_pico_debug = LaunchConfiguration("start_pico_debug")
    serial_port = LaunchConfiguration("serial_port")

    default_actuator_file = safe_pkg / "config" / "actuator_limits.yaml"
    control_defaults = control_pkg / "config" / "control_defaults.yaml"

    return LaunchDescription([
        DeclareLaunchArgument("dry_run", default_value="true"),
        DeclareLaunchArgument("require_safe_region", default_value="true"),
        DeclareLaunchArgument("safe_region_csv", default_value=""),
        DeclareLaunchArgument(
            "actuator_limits_file", default_value=str(default_actuator_file)
        ),
        DeclareLaunchArgument("start_rviz", default_value="false"),
        DeclareLaunchArgument("start_pico_debug", default_value="false"),
        DeclareLaunchArgument("serial_port", default_value="/dev/ttyACM0"),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                str(description_pkg / "launch" / "runtime_description.launch.py")
            ),
            launch_arguments={"use_sim_time": "false"}.items(),
        ),
        Node(
            package="macrobot_arm_kinematics",
            executable="linkage_state_node",
            name="macrobot_serial2r_state_node",
            output="screen",
            parameters=[str(description_pkg / "config" / "kinematics.yaml")],
        ),
        Node(
            package="rviz2",
            executable="rviz2",
            name="rviz2",
            arguments=["-d", str(description_pkg / "rviz" / "display.rviz")],
            condition=IfCondition(start_rviz),
            output="screen",
        ),
        Node(
            package="pico_debug",
            executable="pico_debug_node",
            name="pico_debug_node",
            output="screen",
            condition=IfCondition(start_pico_debug),
            parameters=[{
                "serial_port": serial_port,
                "interactive": False,
                "auto_reconnect": True,
                "send_stop_on_shutdown": True,
            }],
        ),
        Node(
            package="macrobot_arm_control",
            executable="ik_validator_node",
            name="macrobot_ik_validator",
            output="screen",
            parameters=[
                str(control_defaults),
                {
                    "actuator_limits_file": actuator_limits_file,
                    "safe_region_csv": safe_region_csv,
                    "require_safe_region": ParameterValue(
                        require_safe_region, value_type=bool
                    ),
                    "path_step_rad": 0.00872664626,
                },
            ],
        ),
        Node(
            package="macrobot_arm_control",
            executable="servo_bridge_node",
            name="macrobot_arm_servo_bridge",
            output="screen",
            parameters=[
                str(control_defaults),
                {
                    "actuator_limits_file": actuator_limits_file,
                    "safe_region_csv": safe_region_csv,
                    "require_safe_region": ParameterValue(
                        require_safe_region, value_type=bool
                    ),
                    "dry_run": ParameterValue(dry_run, value_type=bool),
                    "command_home_on_start": False,
                    "update_rate_hz": 20.0,
                    "q1_max_velocity": 0.08,
                    "q2_max_velocity": 0.08,
                    "q3_max_velocity": 0.12,
                    "minimum_duration_sec": 0.5,
                    "preempt_active_goal": False,
                },
            ],
        ),
    ])
'''


def ensure_exec_dependency(package_xml: str, dependency: str) -> str:
    if re.search(rf"<(?:depend|exec_depend)>\s*{re.escape(dependency)}\s*</", package_xml):
        return package_xml
    marker = "  <export>"
    if marker not in package_xml:
        raise MigrationError("package.xml has no <export> marker")
    return package_xml.replace(
        marker,
        f"  <exec_depend>{dependency}</exec_depend>\n\n{marker}",
        1,
    )

def render_kinematics_yaml(spec: RobotSpec) -> str:
    return f'''/**:
  ros__parameters:
    model_revision: {spec.model_revision}
    model_type: serial_2r
    base_frame: base_link
    tool_frame: grasp_frame
    nominal_tool_frame: {spec.grasp_joint.child}
    shoulder_joint: arm_lift_joint
    wrist_joint: wrist_pitch_joint
    gripper_joint: gripper_joint
    logical_state_topic: /macrobot/arm/logical_joint_states
    full_joint_state_topic: /joint_states
    target_topic: /macrobot/arm/target_point
    solution_topic: /macrobot/arm/ik_solution
    status_topic: /macrobot/arm/ik_status
    tool_pose_topic: /macrobot/arm/tool_pose
    gripper_gap_topic: /macrobot/gripper/gap
    shoulder_origin_xyz: {format_yaml_list(spec.shoulder.origin_xyz)}
    shoulder_origin_rpy: {format_yaml_list(spec.shoulder.origin_rpy)}
    shoulder_axis: {format_yaml_list(spec.shoulder.axis)}
    wrist_origin_xyz: {format_yaml_list(spec.wrist.origin_xyz)}
    wrist_origin_rpy: {format_yaml_list(spec.wrist.origin_rpy)}
    wrist_axis: {format_yaml_list(spec.wrist.axis)}
    grasp_origin_xyz: {format_yaml_list(spec.grasp_joint.origin_xyz)}
    grasp_origin_rpy: {format_yaml_list(spec.grasp_joint.origin_rpy)}
    # Compatibility aliases used by the current description/validator.
    nominal_grasp_xyz_in_gripper_link: {format_yaml_list(spec.grasp_joint.origin_xyz)}
    nominal_grasp_rpy_in_gripper_link: {format_yaml_list(spec.grasp_joint.origin_rpy)}
    arm_lift_min: {spec.shoulder.lower:.12g}
    arm_lift_max: {spec.shoulder.upper:.12g}
    wrist_pitch_min: {spec.wrist.lower:.12g}
    wrist_pitch_max: {spec.wrist.upper:.12g}
    gripper_min: {spec.gripper.lower:.12g}
    gripper_max: {spec.gripper.upper:.12g}
    max_plane_error_m: 0.030
    gripper_open_gap_m: 0.070
    gripper_closed_gap_m: 0.010
    publish_full_joint_states: true
    publish_mimic_joint_states: true
    publish_rate: 30.0
    auto_apply_ik: false
    seed_weight: 0.001
    four_bar_enabled: false
    wrist_actuator_uses_absolute_angle: false
    wrist_actuator_coordinate: q2
'''


def render_arm_semantics_yaml(spec: RobotSpec) -> str:
    mimic_lines = "\n".join(
        f"      {child}: [{multiplier:.12g}, {offset:.12g}]"
        for child, (master, multiplier, offset) in sorted(spec.mimics.items())
        if master == "gripper_joint"
    )
    return f'''model_revision: {spec.model_revision}
model_type: serial_2r
source_urdf: {spec.urdf_path.name}
logical_joints:
  arm_lift_joint:
    meaning: First serial arm joint; positive direction follows the active URDF.
    parent: {spec.shoulder.parent}
    child: {spec.shoulder.child}
    fixed_origin_xyz_m: {format_yaml_list(spec.shoulder.origin_xyz)}
    fixed_origin_rpy_rad: {format_yaml_list(spec.shoulder.origin_rpy)}
    axis_in_joint_frame: {format_yaml_list(spec.shoulder.axis)}
    range_rad: [{spec.shoulder.lower:.12g}, {spec.shoulder.upper:.12g}]
  wrist_pitch_joint:
    meaning: Independent second serial arm joint; the actuator input is q2, never q1+q2.
    parent: {spec.wrist.parent}
    child: {spec.wrist.child}
    fixed_origin_xyz_m: {format_yaml_list(spec.wrist.origin_xyz)}
    fixed_origin_rpy_rad: {format_yaml_list(spec.wrist.origin_rpy)}
    axis_in_joint_frame: {format_yaml_list(spec.wrist.axis)}
    range_rad: [{spec.wrist.lower:.12g}, {spec.wrist.upper:.12g}]
  gripper_joint:
    meaning: Logical symmetric closure coordinate; zero is open and positive closes.
    range_rad: [{spec.gripper.lower:.12g}, {spec.gripper.upper:.12g}]
    mimic_mapping:
{mimic_lines if mimic_lines else '      {}'}
removed_constraints:
  - arm four-bar closure
  - rear passive-joint mapping
  - q1+q2 wrist actuator coupling
  - four-bar toggle-margin check
derived:
  shoulder_axis_base: {format_yaml_list(spec.shoulder_axis_base)}
  wrist_axis_base_at_zero: {format_yaml_list(spec.wrist_axis_base_zero)}
  arm_axis_dot_product: {spec.axis_alignment:.12g}
  zero_pose_grasp_xyz_base_m: {format_yaml_list(spec.zero_grasp_xyz)}
'''


def patch_description_validator(source: str, spec: RobotSpec) -> str:
    """Synchronize the repository's reviewed-model validator with active URDF facts."""
    text, count = re.subn(
        r"(?m)^REVISION\s*=\s*['\"][^'\"]+['\"]\s*$",
        f"REVISION = {spec.model_revision!r}",
        source,
        count=1,
    )
    if count != 1:
        raise MigrationError("validate_description.py: REVISION assignment was not found")

    def replace_joint_check(
        current: str,
        name: str,
        xyz: Vec3,
        rpy: Vec3,
        axis: Optional[Vec3],
    ) -> str:
        pattern = re.compile(
            rf"(?ms)^[ \t]*check_joint\(\s*['\"]{re.escape(name)}['\"]\s*,.*?\)\s*$"
        )
        args = f"{name!r}, {format_tuple(xyz)},\n                {format_tuple(rpy)}"
        if axis is not None:
            args += f", {format_tuple(axis)}"
        replacement = f"    check_joint({args})"
        updated, replacements = pattern.subn(replacement, current, count=1)
        if replacements != 1:
            raise MigrationError(
                f"validate_description.py: check_joint({name!r}) was not found or was ambiguous"
            )
        return updated

    text = replace_joint_check(
        text,
        spec.shoulder.name,
        spec.shoulder.origin_xyz,
        spec.shoulder.origin_rpy,
        spec.shoulder.axis,
    )
    text = replace_joint_check(
        text,
        spec.wrist.name,
        spec.wrist.origin_xyz,
        spec.wrist.origin_rpy,
        spec.wrist.axis,
    )
    text = replace_joint_check(
        text,
        spec.grasp_joint.name,
        spec.grasp_joint.origin_xyz,
        spec.grasp_joint.origin_rpy,
        None,
    )

    mimic_lines = ["    expected_mimics = {"]
    for child, (master, multiplier, _offset) in sorted(spec.mimics.items()):
        mimic_lines.append(
            f"        {child!r}: ({master!r}, {float(multiplier):.12g}),"
        )
    mimic_lines.append("    }")
    mimic_block = "\n".join(mimic_lines)
    text, count = re.subn(
        r"(?ms)^    expected_mimics\s*=\s*\{\n.*?^    \}\s*$",
        mimic_block,
        text,
        count=1,
    )
    if count != 1:
        raise MigrationError("validate_description.py: expected_mimics block was not found")

    text, count = re.subn(
        r"(?m)^(\s*)expected_zero\s*=\s*\([^\n]+\)\s*$",
        lambda match: f"{match.group(1)}expected_zero = {format_tuple(spec.zero_grasp_xyz)}",
        text,
        count=1,
    )
    if count != 1:
        raise MigrationError("validate_description.py: expected_zero assignment was not found")
    return text


def patch_revision_yaml(path: Path, model_revision: str) -> str:
    source = path.read_text(encoding="utf-8") if path.exists() else ""
    if re.search(r"(?m)^model_revision\s*:", source):
        return re.sub(
            r"(?m)^model_revision\s*:\s*.*$",
            f"model_revision: {model_revision}",
            source,
            count=1,
        )
    return f"model_revision: {model_revision}\n" + source

def patch_actuator_yaml(path: Path, spec: RobotSpec) -> str:
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {"/**": {"ros__parameters": {}}}
    params = extract_ros_parameters(raw)
    for key in ("tool_pitch_min", "tool_pitch_max", "four_bar_margin_rad", "four_bar_margin"):
        params.pop(key, None)
    params["model_type"] = "serial_2r"
    params["model_revision"] = spec.model_revision
    params["wrist_actuator_coordinate"] = "q2"
    params["q1_min"] = float(params.get("q1_min", spec.shoulder.lower))
    params["q1_max"] = float(params.get("q1_max", spec.shoulder.upper))
    params["q2_min"] = float(params.get("q2_min", spec.wrist.lower))
    params["q2_max"] = float(params.get("q2_max", spec.wrist.upper))
    params["q3_min"] = float(params.get("q3_min", spec.gripper.lower))
    params["q3_max"] = float(params.get("q3_max", spec.gripper.upper))
    return "# Serial-2R actuator calibration. Reconfirm zero/sign/range on hardware.\n" + yaml.safe_dump(
        raw, sort_keys=False, allow_unicode=True
    )


def patch_moveit_joint_limits(path: Path, spec: RobotSpec) -> str:
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    limits = raw.setdefault("joint_limits", {})
    for name, lower, upper in (
        ("arm_lift_joint", spec.shoulder.lower, spec.shoulder.upper),
        ("wrist_pitch_joint", spec.wrist.lower, spec.wrist.upper),
        ("gripper_joint", spec.gripper.lower, spec.gripper.upper),
    ):
        entry = limits.setdefault(name, {})
        entry["has_position_limits"] = True
        entry["min_position"] = float(lower)
        entry["max_position"] = float(upper)
    return yaml.safe_dump(raw, sort_keys=False, allow_unicode=True)


def find_matching_brace(text: str, opening: int) -> int:
    depth = 0
    in_string: Optional[str] = None
    escaped = False
    in_line_comment = False
    in_block_comment = False
    i = opening
    while i < len(text):
        ch = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""
        if in_line_comment:
            if ch == "\n":
                in_line_comment = False
            i += 1
            continue
        if in_block_comment:
            if ch == "*" and nxt == "/":
                in_block_comment = False
                i += 2
                continue
            i += 1
            continue
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == in_string:
                in_string = None
            i += 1
            continue
        if ch == "/" and nxt == "/":
            in_line_comment = True
            i += 2
            continue
        if ch == "/" and nxt == "*":
            in_block_comment = True
            i += 2
            continue
        if ch in ('"', "'"):
            in_string = ch
            i += 1
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    raise MigrationError("Unbalanced braces while patching C++")


def replace_cpp_function(text: str, marker: str, replacement: str) -> str:
    start = text.find(marker)
    if start < 0:
        raise MigrationError(f"C++ function marker not found: {marker}")
    opening = text.find("{", start)
    if opening < 0:
        raise MigrationError(f"Opening brace not found after {marker}")
    closing = find_matching_brace(text, opening)
    return text[:start] + replacement.rstrip() + text[closing + 1 :]


def patch_safe_region_cpp(source: str) -> str:
    text = source
    text = re.sub(r'\n\s*declare_parameter<double>\("tool_pitch_min"[^\n]*\);', '', text)
    text = re.sub(r'\n\s*declare_parameter<double>\("tool_pitch_max"[^\n]*\);', '', text)
    text = re.sub(r'\n\s*declare_parameter<double>\("four_bar_margin_rad"[^\n]*\);', '', text)
    text = re.sub(r'\n\s*tool_pitch_min_\s*=.*?;\s*tool_pitch_max_\s*=.*?;', '', text)
    text = re.sub(r'\n\s*four_bar_margin_\s*=.*?;', '', text)
    text = text.replace(
        'if (robot_model_mode_ != "reduced" && robot_model_mode_ != "full_mapped")\n      throw std::invalid_argument("robot_model_mode must be reduced or full_mapped");',
        'if (robot_model_mode_ != "serial_2r" && robot_model_mode_ != "reduced" && robot_model_mode_ != "full_mapped")\n      throw std::invalid_argument("robot_model_mode must be serial_2r, reduced, or full_mapped");',
    )
    text = replace_cpp_function(
        text,
        "std::vector<std::string> requiredVariables() const",
        '''std::vector<std::string> requiredVariables() const
  {
    return { "arm_lift_joint", "wrist_pitch_joint", "gripper_joint" };
  }''',
    )
    text = replace_cpp_function(
        text,
        "void setStateFromLogical(",
        '''void setStateFromLogical(
    moveit::core::RobotState& state, const double q1, const double q2, const double q3) const
  {
    state.setToDefaultValues();
    state.setVariablePosition("arm_lift_joint", q1);
    state.setVariablePosition("wrist_pitch_joint", q2);
    state.setVariablePosition("gripper_joint", q3);
  }''',
    )
    old_tilt = 'out.tilt_cmd = tilt_zero_ + tilt_sign_ * radToDeg(tilt_multiplier_ * (q1 + q2));'
    new_tilt = 'out.tilt_cmd = tilt_zero_ + tilt_sign_ * radToDeg(tilt_multiplier_ * q2);'
    if old_tilt in text:
        text = text.replace(old_tilt, new_tilt, 1)
    elif new_tilt not in text:
        raise MigrationError("Safe-region wrist actuator formula was not found")
    coupled_block = re.compile(
        r'\n\s*const double rear_lift_angle = q1 \+ q2;\n'
        r'\s*if \(rear_lift_angle < tool_pitch_min_ \|\| rear_lift_angle > tool_pitch_max_\)\n'
        r'\s*\{\n\s*out\.reason = "rear_lift_angle_limit";\n\s*return out;\n\s*\}\n'
        r'\s*if \(std::abs\(q2\) > kPi / 2\.0 - four_bar_margin_\)\n'
        r'\s*\{\n\s*out\.reason = "four_bar_toggle_margin";\n\s*return out;\n\s*\}\n'
    )
    text, count = coupled_block.subn("\n", text, count=1)
    if count == 0 and ("rear_lift_angle_limit" in text or "four_bar_toggle_margin" in text):
        raise MigrationError(
            "Legacy coupled safety checks remain but did not match the expected source layout"
        )
    text = text.replace(
        'left_tilt_servo_deg,right_lift_servo_deg',
        'shoulder_servo_deg,wrist_servo_deg',
    )
    text = text.replace(
        'rear_lift_angle_from_right_servo',
        'q2_from_wrist_servo',
    )
    text = re.sub(
        r'\n\s*double tool_pitch_min_, tool_pitch_max_, four_bar_margin_;',
        '',
        text,
    )
    text = text.replace("right_lift_mg996r", "right_wrist_mg996r")
    text = text.replace("left_tilt_mg996r", "left_shoulder_mg996r")
    return text


def patch_safe_region_analysis(source: str) -> str:
    text = source.replace(
        'def rear_lift_angle(self) -> float:\n        """Absolute angle of the right driven/rear-lift gear."""\n        return self.q1 + self.q2',
        'def wrist_angle(self) -> float:\n        """Independent serial wrist coordinate."""\n        return self.q2\n\n    @property\n    def rear_lift_angle(self) -> float:\n        """Deprecated report alias; returns q2 in the serial-2R model."""\n        return self.q2',
    )
    text = text.replace(
        '"""Backward-compatible alias for rear_lift_angle."""\n        return self.rear_lift_angle',
        '"""Backward-compatible alias for the independent wrist angle."""\n        return self.q2',
    )
    text = text.replace('"rear_lift_angle": sample.rear_lift_angle,', '"wrist_angle": sample.q2,')
    text = text.replace('item.rear_lift_angle', 'item.q2')
    text = text.replace('rear_lift_angle_', 'wrist_angle_')
    text = text.replace('q1+q2 rear-lift boundary', 'independent q2 wrist boundary')
    text = text.replace('"coupled_boundary"', '"wrist_boundary"')
    return text


def patch_pico_direction_helper(source: str) -> str:
    text = source.replace('"right_mg996r_rear_lift"', '"right_mg996r_wrist_pitch"')
    text = text.replace('2.0 * (q1 + q2)', '2.0 * q2')
    text = text.replace('(q1 + q2)', 'q2')
    return text


def patch_pico_smoke_test(source: str) -> str:
    text = source
    text = text.replace(
        "CH1 right MG996R: CW -> rear linkage rises",
        "CH1 right MG996R: CW -> independent second arm joint moves",
    )
    text = text.replace(
        "# q1=+0.15: left servo CCW (+17.19deg), rear absolute angle also +0.15\n# so right servo turns CW (-17.19deg).",
        "# q1=+0.15: only the first arm servo moves; q2 remains zero.",
    )
    text = text.replace(
        'send_command "ARM_US 1691 1309 500" 2.0',
        'send_command "ARM_US 1691 1500 500" 2.0',
    )
    text = text.replace(
        "# q2=+0.15 with q1=0: pure relative rear lift; right servo CW.",
        "# q2=+0.15 with q1=0: the independent second servo turns CW.",
    )
    text = text.replace(
        'read -r -p "q2 +0.15: 뒤쪽 높이 상승 시험을 하려면 Enter: "',
        'read -r -p "q2 +0.15: 두 번째 직렬 관절 시험을 하려면 Enter: "',
    )
    return text


def render_srdf(robot_name: str, spec: RobotSpec, links: Sequence[str]) -> str:
    link_set = set(links)
    pairs: List[Tuple[str, str, str]] = []
    for parent, child in (
        (spec.shoulder.parent, spec.shoulder.child),
        (spec.wrist.parent, spec.wrist.child),
        (spec.gripper.parent, spec.gripper.child),
        ("base_link", "camera_link"),
        ("base_link", "front_left_wheel"),
        ("base_link", "back_left_wheel"),
        ("base_link", "front_right_wheel"),
        ("base_link", "back_right_wheel"),
        ("gripper_link", "gripper_servo_gear"),
        ("gripper_link", "gripper_left_gear"),
        ("gripper_link", "gripper_right_gear"),
        ("gripper_link", "gripper_left_addition"),
        ("gripper_link", "gripper_right_addition"),
        ("gripper_left_addition", "gripper_clamp_left"),
        ("gripper_right_addition", "gripper_clamp_right"),
        ("gripper_left_gear", "gripper_clamp_left"),
        ("gripper_right_gear", "gripper_clamp_right"),
        ("gripper_link", "tool0"),
        ("gripper_link", spec.grasp_joint.child),
        ("gripper_servo_gear", "gripper_left_gear"),
        ("gripper_left_gear", "gripper_right_gear"),
    ):
        if parent in link_set and child in link_set:
            reason = "GearMesh" if "gear" in parent and "gear" in child else "Adjacent"
            pairs.append((parent, child, reason))
    collision_lines = "\n".join(
        f'  <disable_collisions link1="{a}" link2="{b}" reason="{reason}"/>'
        for a, b, reason in pairs
    )
    return f'''<?xml version="1.0"?>
<robot name="{robot_name}">
  <virtual_joint name="world_joint" type="fixed" parent_frame="world" child_link="base_link"/>
  <group name="arm">
    <joint name="arm_lift_joint"/>
    <joint name="wrist_pitch_joint"/>
  </group>
  <group name="gripper">
    <joint name="gripper_joint"/>
  </group>
  <group name="arm_with_gripper">
    <group name="arm"/>
    <group name="gripper"/>
  </group>
  <end_effector name="macrobot_gripper" parent_link="gripper_link" group="gripper" parent_group="arm"/>
  <group_state name="home" group="arm_with_gripper">
    <joint name="arm_lift_joint" value="0"/>
    <joint name="wrist_pitch_joint" value="0"/>
    <joint name="gripper_joint" value="0"/>
  </group_state>
  <group_state name="gripper_open" group="gripper">
    <joint name="gripper_joint" value="{spec.gripper.lower:.12g}"/>
  </group_state>
  <group_state name="gripper_closed" group="gripper">
    <joint name="gripper_joint" value="{spec.gripper.upper:.12g}"/>
  </group_state>
{collision_lines}
</robot>
'''


def update_launch_text(source: str, model_revision: str) -> str:
    text = source.replace("'robot_model_mode': 'full_mapped'", "'robot_model_mode': 'serial_2r'")
    text = text.replace('"robot_model_mode": "full_mapped"', '"robot_model_mode": "serial_2r"')
    text = re.sub(
        r"(['\"]model_revision['\"]\s*:\s*)['\"][^'\"]+['\"]",
        lambda match: f"{match.group(1)}{model_revision!r}",
        text,
    )
    return text


def collect_links(urdf_path: Path) -> List[str]:
    root = ET.parse(urdf_path).getroot()
    strip_namespace(root)
    return [element.get("name") or "" for element in root.findall("link")]


def plan_migration(workspace: Path, spec: RobotSpec) -> Tuple[List[PlannedWrite], List[PlannedMove], List[str]]:
    src = workspace / "src"
    description = src / "macrobot_description"
    writes: List[PlannedWrite] = []
    moves: List[PlannedMove] = []
    warnings: List[str] = []

    kinematics_pkg = src / "macrobot_arm_kinematics"
    if kinematics_pkg.exists():
        writes.extend([
            PlannedWrite(
                kinematics_pkg / "macrobot_arm_kinematics" / "model.py",
                render_model_py(spec),
                "replace four-bar FK/IK with URDF-derived serial 2R",
            ),
            PlannedWrite(
                kinematics_pkg / "macrobot_arm_kinematics" / "linkage_state_node.py",
                render_linkage_state_node(spec),
                "publish direct q1/q2/q3 and current gripper mimics",
            ),
            PlannedWrite(
                kinematics_pkg / "macrobot_arm_kinematics" / "ik_node.py",
                render_ik_node(spec),
                "solve full XYZ target with serial 2R geometry",
            ),
            PlannedWrite(
                kinematics_pkg / "test" / "test_model.py",
                render_model_test(spec),
                "replace legacy four-bar unit tests",
            ),
        ])
    else:
        warnings.append("macrobot_arm_kinematics package not found")

    control_pkg = src / "macrobot_arm_control"
    if control_pkg.exists():
        writes.append(PlannedWrite(
            control_pkg / "macrobot_arm_control" / "servo_mapping.py",
            render_servo_mapping_py(),
            "make wrist servo depend on q2 only",
        ))
        safety_path = control_pkg / "macrobot_arm_control" / "safety.py"
        if safety_path.exists():
            patched = replace_python_class(
                safety_path.read_text(encoding="utf-8"),
                "AnalyticValidator",
                serial2r_analytic_validator_class(),
            )
            writes.append(PlannedWrite(safety_path, patched, "remove four-bar-only analytic guards"))
        writes.append(PlannedWrite(
            control_pkg / "test" / "test_servo_mapping.py",
            render_servo_test(),
            "verify q2-only wrist servo mapping",
        ))
        control_launch = control_pkg / "launch" / "arm_pipeline.launch.py"
        if control_launch.exists():
            writes.append(PlannedWrite(
                control_launch,
                render_arm_pipeline_launch(),
                "launch runtime_description and the serial-2R state node",
            ))
        control_package_xml = control_pkg / "package.xml"
        if control_package_xml.exists():
            writes.append(PlannedWrite(
                control_package_xml,
                ensure_exec_dependency(
                    ensure_exec_dependency(
                        control_package_xml.read_text(encoding="utf-8"),
                        "rviz2",
                    ),
                    "macrobot_arm_kinematics",
                ),
                "declare serial-2R launch dependencies",
            ))
    else:
        warnings.append("macrobot_arm_control package not found")

    writes.extend([
        PlannedWrite(description / "config" / "kinematics.yaml", render_kinematics_yaml(spec), "synchronize kinematics parameters with current URDF"),
        PlannedWrite(description / "config" / "arm_semantics.yaml", render_arm_semantics_yaml(spec), "document serial 2R semantics"),
    ])
    downstream_revision = description / "config" / "downstream_migration.yaml"
    if downstream_revision.exists():
        writes.append(PlannedWrite(
            downstream_revision,
            patch_revision_yaml(downstream_revision, spec.model_revision),
            "synchronize downstream migration revision",
        ))
    description_validator = description / "scripts" / "validate_description.py"
    if description_validator.exists():
        writes.append(PlannedWrite(
            description_validator,
            patch_description_validator(
                description_validator.read_text(encoding="utf-8"),
                spec,
            ),
            "synchronize reviewed-model validator with the active serial-2R URDF",
        ))

    for path in src.rglob("actuator_limits.yaml"):
        if any(part in {"build", "install", "log", "backup"} for part in path.parts):
            continue
        writes.append(PlannedWrite(path, patch_actuator_yaml(path, spec), "remove coupled wrist and four-bar limits"))

    safe_pkg = src / "macrobot_safe_region"
    if safe_pkg.exists():
        cpp = safe_pkg / "src" / "safe_region_generator.cpp"
        if cpp.exists():
            writes.append(PlannedWrite(cpp, patch_safe_region_cpp(cpp.read_text(encoding="utf-8")), "set MoveIt state directly from q1/q2/q3"))
        for launch in (safe_pkg / "launch").glob("*.py") if (safe_pkg / "launch").exists() else []:
            updated = update_launch_text(launch.read_text(encoding="utf-8"), spec.model_revision)
            writes.append(PlannedWrite(launch, updated, "select serial_2r safe-region mode and revision"))
    else:
        warnings.append("macrobot_safe_region package not found")

    commission_pkg = src / "macrobot_arm_commissioning"
    if commission_pkg.exists():
        analysis_path = commission_pkg / "macrobot_arm_commissioning" / "safe_region_analysis.py"
        if analysis_path.exists():
            writes.append(PlannedWrite(
                analysis_path,
                patch_safe_region_analysis(analysis_path.read_text(encoding="utf-8")),
                "change coupled boundary reports to independent wrist reports",
            ))
        grasp_fit = commission_pkg / "macrobot_arm_commissioning" / "grasp_frame_fit.py"
        if grasp_fit.exists():
            writes.append(PlannedWrite(
                grasp_fit,
                render_serial_grasp_frame_fit(),
                "replace q3-dependent four-bar endpoint fit with a fixed serial-2R grasp-frame fit",
            ))
        grasp_fit_test = commission_pkg / "test" / "test_grasp_frame_fit.py"
        writes.append(PlannedWrite(
            grasp_fit_test,
            render_serial_grasp_frame_test(spec),
            "verify fixed serial-2R grasp-frame fitting",
        ))
        commissioning_cli = commission_pkg / "macrobot_arm_commissioning" / "commissioning_cli.py"
        if commissioning_cli.exists():
            writes.append(PlannedWrite(
                commissioning_cli,
                patch_commissioning_cli(commissioning_cli.read_text(encoding="utf-8")),
                "replace four-bar operator checks and grasp calibration workflow",
            ))
        commissioning_launch = commission_pkg / "launch" / "commissioning_pipeline.launch.py"
        if commissioning_launch.exists():
            writes.append(PlannedWrite(
                commissioning_launch,
                render_commissioning_pipeline_launch(),
                "launch the current description and serial-2R state node",
            ))
        commissioning_package_xml = commission_pkg / "package.xml"
        if commissioning_package_xml.exists():
            writes.append(PlannedWrite(
                commissioning_package_xml,
                ensure_exec_dependency(
                    commissioning_package_xml.read_text(encoding="utf-8"),
                    "rviz2",
                ),
                "declare optional RViz launch dependency",
            ))
    else:
        warnings.append("macrobot_arm_commissioning package not found")

    for pico_helper in (
        src / "pico" / "servo_direction_config.py",
        workspace / "pico" / "servo_direction_config.py",
    ):
        if pico_helper.exists():
            writes.append(PlannedWrite(
                pico_helper,
                patch_pico_direction_helper(pico_helper.read_text(encoding="utf-8")),
                "change reference wrist formula from q1+q2 to q2",
            ))
    for smoke_test in (
        workspace / "scripts" / "test_pico_arm.sh",
        src / "scripts" / "test_pico_arm.sh",
    ):
        if smoke_test.exists():
            writes.append(PlannedWrite(
                smoke_test,
                patch_pico_smoke_test(smoke_test.read_text(encoding="utf-8")),
                "make the q1 smoke test leave the independent q2 servo at zero",
            ))

    moveit_pkg = src / "macrobot_moveit_config"
    if moveit_pkg.exists():
        links = list(spec.links)
        config = moveit_pkg / "config"
        joint_limits = config / "joint_limits.yaml"
        if joint_limits.exists():
            writes.append(PlannedWrite(
                joint_limits,
                patch_moveit_joint_limits(joint_limits, spec),
                "synchronize MoveIt position limits with the active URDF",
            ))
        for filename, robot_name in (
            ("macrobot.srdf", "macrobot_arm_kinematic"),
            ("macrobot_full_collision.srdf", "macrobot_full_collision"),
            ("macrobot_full_exact_gripper.srdf", "macrobot_full_exact_gripper"),
        ):
            writes.append(PlannedWrite(
                config / filename,
                render_srdf(robot_name, spec, links),
                "remove legacy four-bar links and create a conservative serial-2R SRDF",
            ))
    else:
        warnings.append("macrobot_moveit_config package not found")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    invalid_root = workspace / "backup" / f"invalid_four_bar_generated_{stamp}"
    # Generated scan outputs belong under workspace/data.  Never move files from
    # src/, because packages may contain test fixtures or templates with the
    # same names.
    generated_roots = [path for path in (workspace / "data", workspace / "outputs") if path.exists()]
    for pattern in ("safe_samples.csv", "safe_connected_samples.csv", "safe_region_summary.yaml", "safe_q2_intervals_by_q1_q3.csv"):
        for generated_root in generated_roots:
            for path in generated_root.rglob(pattern):
                if any(part in {"backup", "build", "install", "log"} for part in path.parts):
                    continue
                relative = path.relative_to(workspace)
                moves.append(
                    PlannedMove(
                        path,
                        invalid_root / relative,
                        "old collision/safe-region result is invalid after model change",
                    )
                )

    marker = workspace / "SERIAL2R_REVALIDATION_REQUIRED.md"
    marker_text = f'''# Serial 2R migration requires revalidation

Model revision: `{spec.model_revision}`

The code no longer uses the arm four-bar model. Before hardware motion, redo:

1. Physical q1/q2/q3 zero, sign, multiplier, and hard-limit calibration.
2. MoveIt self-collision matrix review using the current URDF.
3. Coarse and fine safe-region generation.
4. Camera extrinsic and final base-alignment validation.
5. PICK and PLACE keyframe/path validation.

The migration script does not certify physical safety.
'''
    writes.append(PlannedWrite(marker, marker_text, "create mandatory revalidation marker"))
    return writes, moves, warnings


def unique_planned_writes(writes: Sequence[PlannedWrite]) -> List[PlannedWrite]:
    latest: Dict[Path, PlannedWrite] = {}
    for item in writes:
        latest[item.path] = item
    return list(latest.values())


def backup_paths(paths: Iterable[Path], workspace: Path, backup_root: Path) -> None:
    for path in sorted(set(paths)):
        if not path.exists():
            continue
        try:
            relative = path.relative_to(workspace)
        except ValueError:
            relative = Path("external") / path.name
        destination = backup_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if path.is_dir():
            shutil.copytree(path, destination, dirs_exist_ok=True)
        else:
            shutil.copy2(path, destination)


def apply_plan(
    writes: Sequence[PlannedWrite],
    moves: Sequence[PlannedMove],
    workspace: Path,
    backup_root: Path,
) -> None:
    backup_paths([item.path for item in writes] + [item.source for item in moves], workspace, backup_root)
    for item in writes:
        item.path.parent.mkdir(parents=True, exist_ok=True)
        item.path.write_text(item.content.rstrip() + "\n", encoding="utf-8")
    for item in moves:
        if not item.source.exists():
            continue
        item.destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(item.source), str(item.destination))


def scan_unresolved(src: Path) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    suffixes = {".py", ".cpp", ".hpp", ".h", ".yaml", ".yml", ".xml"}
    for path in src.rglob("*"):
        if not path.is_file() or path.suffix not in suffixes:
            continue
        if any(part in {"docs", "urdf", "backup", "build", "install", "log", "original"} for part in path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            for kind, pattern in FORBIDDEN_RUNTIME_PATTERNS:
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
    return findings


def static_validate(paths: Sequence[Path]) -> List[str]:
    errors: List[str] = []
    for path in paths:
        if not path.exists():
            errors.append(f"missing: {path}")
            continue
        try:
            if path.suffix == ".py":
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            elif path.suffix in {".yaml", ".yml"}:
                yaml.safe_load(path.read_text(encoding="utf-8"))
            elif path.suffix in {".xml", ".srdf", ".urdf"}:
                ET.parse(path)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{path}: {exc}")
    return errors


def print_plan(writes: Sequence[PlannedWrite], moves: Sequence[PlannedMove], warnings: Sequence[str]) -> None:
    print("\nPlanned writes:")
    for item in sorted(writes, key=lambda x: str(x.path)):
        print(f"  WRITE {item.path} -- {item.reason}")
    print("\nGenerated artifacts to invalidate:")
    if moves:
        for item in sorted(moves, key=lambda x: str(x.source)):
            print(f"  MOVE  {item.source} -> {item.destination}")
    else:
        print("  (none found)")
    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"  - {warning}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path.home() / "MacRobot")
    parser.add_argument(
        "--urdf",
        type=Path,
        default=None,
        help="explicit active .urdf or .urdf.xacro; otherwise the description package is inspected",
    )
    parser.add_argument("--apply", action="store_true", help="write changes; default is dry-run")
    parser.add_argument("--allow-unresolved", action="store_true", help="do not fail when legacy runtime references remain")
    parser.add_argument("--build", action="store_true", help="run colcon build after migration")
    parser.add_argument("--test", action="store_true", help="run colcon test after migration")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    workspace = args.workspace.expanduser().resolve()
    src = workspace / "src"
    description = src / "macrobot_description"
    if not description.exists():
        raise MigrationError(f"Description package not found: {description}")

    spec = parse_robot_spec(description, args.urdf)
    writes, moves, warnings = plan_migration(workspace, spec)
    writes = unique_planned_writes(writes)
    print(f"Workspace: {workspace}")
    print(f"URDF: {spec.urdf_path}")
    print(f"Model revision: {spec.model_revision}")
    print(f"Axis alignment: {spec.axis_alignment:.9f}")
    print(f"Zero grasp point: {spec.zero_grasp_xyz}")
    print_plan(writes, moves, warnings)

    report: Dict[str, Any] = {
        "workspace": str(workspace),
        "applied": bool(args.apply),
        "model_revision": spec.model_revision,
        "source_urdf": str(spec.urdf_path),
        "axis_alignment": spec.axis_alignment,
        "zero_grasp_xyz": list(spec.zero_grasp_xyz),
        "serial_chain": {
            "shoulder": {
                "name": spec.shoulder.name,
                "parent": spec.shoulder.parent,
                "child": spec.shoulder.child,
                "origin_xyz": list(spec.shoulder.origin_xyz),
                "origin_rpy": list(spec.shoulder.origin_rpy),
                "axis": list(spec.shoulder.axis),
                "limits": [spec.shoulder.lower, spec.shoulder.upper],
            },
            "wrist": {
                "name": spec.wrist.name,
                "parent": spec.wrist.parent,
                "child": spec.wrist.child,
                "origin_xyz": list(spec.wrist.origin_xyz),
                "origin_rpy": list(spec.wrist.origin_rpy),
                "axis": list(spec.wrist.axis),
                "limits": [spec.wrist.lower, spec.wrist.upper],
            },
            "gripper": {
                "name": spec.gripper.name,
                "limits": [spec.gripper.lower, spec.gripper.upper],
            },
            "grasp_joint": {
                "name": spec.grasp_joint.name,
                "parent": spec.grasp_joint.parent,
                "child": spec.grasp_joint.child,
                "origin_xyz": list(spec.grasp_joint.origin_xyz),
                "origin_rpy": list(spec.grasp_joint.origin_rpy),
            },
        },
        "gripper_mimics": {
            child: {"master": master, "multiplier": multiplier, "offset": offset}
            for child, (master, multiplier, offset) in spec.mimics.items()
        },
        "writes": [{"path": str(item.path), "reason": item.reason} for item in writes],
        "invalidated": [{"source": str(item.source), "destination": str(item.destination)} for item in moves],
        "warnings": list(warnings),
    }

    if not args.apply:
        print("\nDry-run only. Re-run with --apply after reviewing the plan.")
        return 0

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_root = workspace / "backup" / f"four_bar_to_serial2r_{stamp}"
    apply_plan(writes, moves, workspace, backup_root)
    report["backup_root"] = str(backup_root)

    static_errors = static_validate([item.path for item in writes if item.path.suffix in {".py", ".yaml", ".yml", ".xml", ".srdf", ".urdf"}])
    report["static_errors"] = static_errors
    if static_errors:
        report_path = workspace / "four_bar_to_serial2r_report.json"
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        raise MigrationError("Static validation failed:\n" + "\n".join(static_errors))

    description_validator = description / "scripts" / "validate_description.py"
    if description_validator.exists():
        validation = run_command(
            [sys.executable, str(description_validator), str(description)],
            cwd=workspace,
            check=False,
        )
        report["description_validator_returncode"] = validation.returncode
        report["description_validator_output"] = validation.stdout
        if validation.returncode != 0:
            report_path = workspace / "four_bar_to_serial2r_report.json"
            report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            print(validation.stdout)
            raise MigrationError(
                "macrobot_description validator failed after migration; see the report above"
            )

    unresolved = scan_unresolved(src)
    report["unresolved_legacy_runtime_references"] = unresolved
    report_path = workspace / "four_bar_to_serial2r_report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if unresolved and not args.allow_unresolved:
        print("\nLegacy runtime references remain:")
        for finding in unresolved[:80]:
            print(f"  {finding['path']}:{finding['line']}: {finding['text']}")
        print(f"\nFull report: {report_path}")
        return 2

    packages = [name for name in CORE_PACKAGES if (src / name).exists()]
    if args.build:
        command = ["colcon", "build", "--symlink-install", "--packages-select", *packages]
        result = run_command(command, cwd=workspace, check=False)
        print(result.stdout)
        report["build_returncode"] = result.returncode
        if result.returncode != 0:
            report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            return result.returncode
    if args.test:
        command = ["colcon", "test", "--packages-select", *packages]
        result = run_command(command, cwd=workspace, check=False)
        print(result.stdout)
        report["test_returncode"] = result.returncode
        if result.returncode != 0:
            report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            return result.returncode

    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nMigration applied. Backup: {backup_root}")
    print(f"Report: {report_path}")
    print("Do not run hardware motion until MoveIt/safe-region and servo calibration are redone.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except MigrationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
