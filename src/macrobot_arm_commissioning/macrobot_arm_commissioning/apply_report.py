from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import shutil
from typing import Any, Dict, Mapping, MutableMapping

import yaml


def _parameters_block(data: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
    if "/**" in data:
        block = data["/**"]
        if not isinstance(block, dict):
            block = {}
            data["/**"] = block
        parameters = block.get("ros__parameters")
        if not isinstance(parameters, dict):
            parameters = {}
            block["ros__parameters"] = parameters
        return parameters
    parameters = data.get("ros__parameters")
    if isinstance(parameters, dict):
        return parameters
    data["/**"] = {"ros__parameters": {}}
    return data["/**"]["ros__parameters"]


def _load(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        value = yaml.safe_load(stream) or {}
    if not isinstance(value, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return value


def _write(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as stream:
        yaml.safe_dump(
            dict(value),
            stream,
            allow_unicode=True,
            sort_keys=False,
        )


def _backup(path: Path) -> None:
    if not path.exists():
        return
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(path, path.with_name(path.name + f".bak_{stamp}"))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Apply calibration and grasp-frame recommendations from a commissioning report."
    )
    parser.add_argument("--report", required=True)
    parser.add_argument("--actuator-input", default="")
    parser.add_argument("--actuator-output", default="")
    parser.add_argument("--kinematics-input", default="")
    parser.add_argument("--kinematics-output", default="")
    parser.add_argument("--in-place", action="store_true")
    args = parser.parse_args()

    report_path = Path(args.report).expanduser().resolve()
    report = _load(report_path)
    sections = report.get("sections", {})

    source = report.get("source", {})
    actuator_source = (
        Path(args.actuator_input).expanduser().resolve()
        if args.actuator_input
        else Path(str(source.get("actuator_limits_file", ""))).expanduser().resolve()
    )
    if not actuator_source.exists():
        raise SystemExit(
            "Actuator input was not found. Pass --actuator-input explicitly."
        )

    calibration = sections.get("pulse_zero_calibration", {})
    suggested_actuator = calibration.get("suggested_actuator_parameters", {})
    if not isinstance(suggested_actuator, dict) or not suggested_actuator:
        raise SystemExit("No suggested_actuator_parameters in the report.")

    if args.in_place:
        actuator_output = actuator_source
    elif args.actuator_output:
        actuator_output = Path(args.actuator_output).expanduser().resolve()
    else:
        actuator_output = report_path.with_name("actuator_limits_calibrated.yaml")

    actuator_yaml = _load(actuator_source)
    actuator_parameters = _parameters_block(actuator_yaml)
    actuator_parameters.update(suggested_actuator)
    if args.in_place:
        _backup(actuator_output)
    _write(actuator_output, actuator_yaml)
    print(f"Wrote actuator calibration: {actuator_output}")

    grasp_section = sections.get("grasp_frame_calibration", {})
    recommended_geometry = grasp_section.get(
        "recommended_kinematics_parameters", {}
    )
    if isinstance(recommended_geometry, dict) and recommended_geometry:
        if args.kinematics_input:
            kinematics_source = Path(args.kinematics_input).expanduser().resolve()
        else:
            kinematics_source = Path()
        if not kinematics_source.exists():
            print(
                "Grasp-frame recommendations exist, but no kinematics input was found. "
                "Pass --kinematics-input to apply them."
            )
            return
        if args.in_place:
            kinematics_output = kinematics_source
        elif args.kinematics_output:
            kinematics_output = Path(args.kinematics_output).expanduser().resolve()
        else:
            kinematics_output = report_path.with_name("kinematics_calibrated.yaml")
        kinematics_yaml = _load(kinematics_source)
        kinematics_parameters = _parameters_block(kinematics_yaml)
        kinematics_parameters.update(recommended_geometry)
        if args.in_place:
            _backup(kinematics_output)
        _write(kinematics_output, kinematics_yaml)
        print(f"Wrote grasp-frame calibration: {kinematics_output}")


if __name__ == "__main__":
    main()
