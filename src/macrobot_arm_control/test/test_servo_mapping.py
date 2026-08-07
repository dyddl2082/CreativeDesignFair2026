import csv
import math
from pathlib import Path

from macrobot_arm_control.safety import SafeRegionGrid, SafetyValidator
from macrobot_arm_control.servo_mapping import load_servo_mapping


def _actuator_file() -> Path:
    return (
        Path(__file__).resolve().parents[2]
        / 'macrobot_safe_region'
        / 'config'
        / 'actuator_limits.yaml'
    )


def test_home_servo_commands():
    mapping = load_servo_mapping(_actuator_file())
    commands = mapping.servo_commands_deg(0.0, 0.0, 0.0)
    assert commands['lift'] == 90.0
    assert commands['tilt'] == 90.0
    assert abs(commands['gripper'] - 161.619724) < 1e-6


def test_closed_gripper_servo_command():
    mapping = load_servo_mapping(_actuator_file())
    command = mapping.servo_commands_deg(0.0, 0.0, -1.25)['gripper']
    assert abs(command - 18.3802757) < 1e-5


def test_analytic_rejects_servo_limit():
    mapping = load_servo_mapping(_actuator_file())
    validator = SafetyValidator(mapping)
    result = validator.validate_point((1.0, 0.0, 0.0))
    assert not result.ok
    assert result.reason == 'lift_servo_limit'


def test_path_validation():
    mapping = load_servo_mapping(_actuator_file())
    validator = SafetyValidator(mapping)
    result = validator.validate_path((0.0, 0.0, 0.0), (0.2, -0.1, -0.4), math.radians(1.0))
    assert result.ok
    assert result.details['path_samples'] > 2


def test_safe_grid_cell(tmp_path):
    csv_path = tmp_path / 'safe_connected_samples.csv'
    with csv_path.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.writer(stream)
        writer.writerow([
            'q1_rad', 'q2_rad', 'q3_rad', 'lift_servo_deg', 'tilt_servo_deg',
            'gripper_servo_deg', 'safe', 'connected', 'reason', 'contacts'
        ])
        for q1 in (0.0, 0.1):
            for q2 in (0.0, 0.1):
                for q3 in (-0.1, 0.0):
                    writer.writerow([q1, q2, q3, 90, 90, 90, 1, 1, 'safe', ''])

    grid = SafeRegionGrid(csv_path)
    assert grid.validate((0.05, 0.05, -0.05), 'cell').ok
    assert not grid.validate((0.15, 0.05, -0.05), 'cell').ok
