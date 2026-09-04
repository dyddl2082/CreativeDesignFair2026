#!/usr/bin/env python3
"""Patch macrobot_pick_pipeline from the legacy four-bar arm model to serial 2R.

Dry-run is the default. Pass --apply to write files. The script is deliberately
strict: if the expected legacy structure is not found, it aborts before making
partial changes.
"""

from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import shutil
import sys
from typing import Iterable, Sequence


class PatchError(RuntimeError):
    pass


@dataclass(frozen=True)
class Change:
    path: Path
    content: str
    reason: str


def target_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
        return f"{node.value.id}.{node.attr}"
    return None


def class_method(tree: ast.Module, class_name: str, method_name: str) -> ast.FunctionDef:
    for item in tree.body:
        if isinstance(item, ast.ClassDef) and item.name == class_name:
            for member in item.body:
                if isinstance(member, ast.FunctionDef) and member.name == method_name:
                    return member
    raise PatchError(f"{class_name}.{method_name} not found")


def replace_lines(source: str, start_line: int, end_line: int, replacement: str) -> str:
    lines = source.splitlines(keepends=True)
    if start_line < 1 or end_line < start_line or end_line > len(lines):
        raise PatchError(f"invalid replacement range {start_line}:{end_line}")
    if replacement and not replacement.endswith("\n"):
        replacement += "\n"
    return "".join(lines[: start_line - 1]) + replacement + "".join(lines[end_line:])


def replace_method(source: str, class_name: str, method_name: str, body: str) -> str:
    tree = ast.parse(source)
    method = class_method(tree, class_name, method_name)
    if method.end_lineno is None:
        raise PatchError(f"cannot determine end of {class_name}.{method_name}")
    return replace_lines(source, method.lineno, method.end_lineno, body)


def replace_init_assignments(
    source: str,
    class_name: str,
    first_target: str,
    last_target: str,
    replacement: str,
) -> str:
    tree = ast.parse(source)
    method = class_method(tree, class_name, "__init__")
    first: ast.Assign | ast.AnnAssign | None = None
    last: ast.Assign | ast.AnnAssign | None = None
    for stmt in method.body:
        if isinstance(stmt, ast.Assign):
            names = [target_name(target) for target in stmt.targets]
        elif isinstance(stmt, ast.AnnAssign):
            names = [target_name(stmt.target)]
        else:
            continue
        if first_target in names and first is None:
            first = stmt
        if last_target in names:
            last = stmt
    if first is None or last is None or first.lineno > last.lineno:
        raise PatchError(
            f"could not find ordered assignments {first_target} .. {last_target} "
            f"in {class_name}.__init__"
        )
    if last.end_lineno is None:
        raise PatchError(f"cannot determine end of assignment {last_target}")
    return replace_lines(source, first.lineno, last.end_lineno, replacement)


def replace_once(source: str, old: str, new: str, label: str) -> str:
    if old in source:
        return source.replace(old, new, 1)
    if new in source:
        return source
    raise PatchError(f"{label}: expected legacy or migrated text was not found")


def serial2r_model_config() -> str:
    return '''"""Construct the active serial-2R arm model from kinematics parameters."""

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
'''


def serial2r_grasp_frame_fit() -> str:
    return '''"""Fit the fixed ``gripper_link -> grasp_nominal`` frame for serial 2R."""

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
'''


def serial2r_grasp_frame_test() -> str:
    return '''import math

from macrobot_arm_kinematics.model import MacRobotArmModel
from macrobot_pick_pipeline.grasp_frame_fit import fit_grasp_frame


def _base_point(model, q1, q2, local):
    position, rotation = model.gripper_link_transform(q1, q2)
    rotated = tuple(
        sum(rotation[row][column] * local[column] for column in range(3))
        for row in range(3)
    )
    return tuple(position[index] + rotated[index] for index in range(3))


def test_fixed_grasp_frame_fit_recovers_model_offset():
    model = MacRobotArmModel()
    truth = model.geometry.grasp_origin_xyz
    samples = []
    for q1, q2, q3 in ((0.0, 0.0, 0.0), (0.20, -0.10, 0.6), (-0.18, 0.16, 1.2)):
        point = _base_point(model, q1, q2, truth)
        samples.append(
            {
                "q1": q1,
                "q2": q2,
                "q3": q3,
                "measurement_frame": "base_link",
                "measured_x": point[0],
                "measured_y": point[1],
                "measured_z": point[2],
            }
        )
    result = fit_grasp_frame(samples, model=model)
    assert math.dist(result["grasp_origin_xyz"], truth) < 1e-10
    assert result["max_error_m"] < 1e-10


def test_grasp_center_is_independent_of_q3():
    model = MacRobotArmModel()
    first = model.forward(0.15, -0.10, 0.0)
    second = model.forward(0.15, -0.10, model.limits.gripper_max)
    assert (first.x, first.y, first.z) == (second.x, second.y, second.z)
'''


def camera_fit_method() -> str:
    return '''    def _action_fit_grasp_frame(
        self, command_id: str, _: Mapping[str, Any]
    ) -> None:
        if len(self.grasp_samples) < 3:
            raise ValueError("at least three camera-aligned samples are required")
        fit_samples = [
            {key: value for key, value in sample.items() if value is not None}
            for sample in self.grasp_samples
        ]
        fitted = fit_grasp_frame(fit_samples, model=self.arm_model)
        recommended = {"grasp_origin_xyz": fitted["grasp_origin_xyz"]}
        for key in ("gripper_open_gap_m", "gripper_closed_gap_m"):
            if key in fitted:
                recommended[key] = fitted[key]

        self.report.complete_section(
            "grasp_frame_calibration",
            {
                "source": "camera_arm_teach",
                "model_type": "serial_2r",
                "measurement_method": "camera_locked_calibration_target",
                "samples": list(self.grasp_samples),
                "fit": fitted,
                "recommended_description_parameters": recommended,
                "recommended_kinematics_parameters": recommended,
                "warning": (
                    "This fit includes camera extrinsic and object-centre error. "
                    "Apply grasp_origin_xyz to the URDF and kinematics.yaml together, "
                    "then regenerate MoveIt collision data and safe-region outputs."
                ),
            },
        )
        recommendation_file = self.report.path.parent / "grasp_frame_recommendation.yaml"
        recommendation_file.parent.mkdir(parents=True, exist_ok=True)
        with recommendation_file.open("w", encoding="utf-8") as stream:
            yaml.safe_dump(
                {
                    "model_type": "serial_2r",
                    "recommended_description_parameters": recommended,
                    "recommended_kinematics_parameters": recommended,
                    "fit": fitted,
                },
                stream,
                allow_unicode=True,
                sort_keys=False,
            )
        self._result(
            command_id,
            "grasp_frame_fit_completed",
            recommended_description_parameters=recommended,
            recommended_kinematics_parameters=recommended,
            fit=fitted,
            recommendation_file=str(recommendation_file),
        )'''


def plan_changes(workspace: Path) -> list[Change]:
    package = workspace / "src" / "macrobot_pick_pipeline"
    module = package / "macrobot_pick_pipeline"
    test_dir = package / "test"
    if not package.is_dir():
        raise PatchError(f"package not found: {package}")

    required = [
        module / "grasp_frame_fit.py",
        module / "camera_teach_node.py",
        module / "pick_coordinator_node.py",
        module / "grasp_keyframe_node.py",
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise PatchError("missing required files: " + ", ".join(missing))

    changes: list[Change] = []
    changes.append(Change(module / "serial2r_model_config.py", serial2r_model_config(), "add serial-2R model loader"))
    changes.append(Change(module / "grasp_frame_fit.py", serial2r_grasp_frame_fit(), "replace legacy four-bar grasp fit"))
    changes.append(Change(test_dir / "test_grasp_frame_fit.py", serial2r_grasp_frame_test(), "replace legacy grasp-frame test"))

    camera_path = module / "camera_teach_node.py"
    camera = camera_path.read_text(encoding="utf-8")
    camera = replace_once(
        camera,
        "from macrobot_arm_kinematics.model import ArmGeometry\n\nfrom .grasp_frame_fit import GeometryReference, fit_grasp_frame",
        "from .grasp_frame_fit import fit_grasp_frame\nfrom .serial2r_model_config import build_arm_model",
        "camera-teach imports",
    )
    if "self.arm_model = build_arm_model(params)" not in camera:
        camera = replace_init_assignments(
            camera,
            "CameraTeachNode",
            "params",
            "self.geometry",
            '''        params = _ros_params(
            Path(str(self.get_parameter("kinematics_file").value))
            .expanduser()
            .resolve()
        )
        self.arm_model = build_arm_model(params)''',
        )
    camera = replace_method(camera, "CameraTeachNode", "_action_fit_grasp_frame", camera_fit_method())
    changes.append(Change(camera_path, camera, "use fixed 3D serial-2R grasp fitting"))

    coordinator_path = module / "pick_coordinator_node.py"
    coordinator = coordinator_path.read_text(encoding="utf-8")
    coordinator = replace_once(
        coordinator,
        "from macrobot_arm_kinematics.model import ArmGeometry, JointLimits, MacRobotArmModel\n\nfrom .planner",
        "from .serial2r_model_config import build_arm_model\n\nfrom .planner",
        "pick-coordinator imports",
    )
    if "self.model = build_arm_model(params)" not in coordinator:
        coordinator = replace_init_assignments(
            coordinator,
            "PickCoordinatorNode",
            "geometry",
            "self.model",
            '''        self.model = build_arm_model(params)
        # The active arm is planar after the corrected shoulder transform.
        self.arm_plane_y = self.model.forward(0.0, 0.0, 0.0).y''',
        )
    coordinator = coordinator.replace("self.model.geometry.tool_y", "self.arm_plane_y")
    changes.append(Change(coordinator_path, coordinator, "load serial-2R geometry and remove legacy tool_y field"))

    keyframe_path = module / "grasp_keyframe_node.py"
    keyframe = keyframe_path.read_text(encoding="utf-8")
    keyframe = replace_once(
        keyframe,
        "from macrobot_arm_kinematics.model import ArmGeometry, JointLimits, MacRobotArmModel\n",
        "from .serial2r_model_config import build_arm_model\n",
        "keyframe imports",
    )
    if "self.model = build_arm_model(parameters)" not in keyframe:
        keyframe = replace_init_assignments(
            keyframe,
            "GraspKeyframeNode",
            "geometry",
            "self.model",
            "        self.model = build_arm_model(parameters)",
        )
    changes.append(Change(keyframe_path, keyframe, "load current serial-2R model"))

    return changes


def validate_contents(changes: Sequence[Change]) -> None:
    for item in changes:
        if item.path.suffix == ".py":
            try:
                compile(item.content, str(item.path), "exec")
            except SyntaxError as exc:
                raise PatchError(f"generated Python is invalid for {item.path}: {exc}") from exc

    combined = "\n".join(item.content for item in changes)
    forbidden = [
        "rear_lift_angle = q1 + q2",
        "four_bar_margin=",
        "tool_pitch_min=",
        "tool_pitch_max=",
        "self.model.geometry.tool_y",
        "GeometryReference(\n            pivot_x=self.geometry.pivot_x",
    ]
    found = [token for token in forbidden if token in combined]
    if found:
        raise PatchError(f"legacy runtime tokens remain in planned outputs: {found}")


def backup_and_write(workspace: Path, changes: Sequence[Change]) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = workspace / "backup" / f"pick_pipeline_serial2r_{stamp}"
    for item in changes:
        if item.path.exists():
            relative = item.path.relative_to(workspace)
            destination = backup / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item.path, destination)
    for item in changes:
        item.path.parent.mkdir(parents=True, exist_ok=True)
        item.path.write_text(item.content, encoding="utf-8")
    return backup


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, default=Path.home() / "MacRobot")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    workspace = args.workspace.expanduser().resolve()

    try:
        changes = plan_changes(workspace)
        validate_contents(changes)
    except (PatchError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print("Planned macrobot_pick_pipeline serial-2R changes:")
    for item in changes:
        state = "update" if item.path.exists() else "create"
        print(f"  [{state}] {item.path}: {item.reason}")

    if not args.apply:
        print("\nDry-run only. Re-run with --apply after reviewing the list.")
        return 0

    try:
        backup = backup_and_write(workspace, changes)
    except OSError as exc:
        print(f"ERROR while writing files: {exc}", file=sys.stderr)
        return 3
    print(f"\nApplied successfully. Backup: {backup}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
