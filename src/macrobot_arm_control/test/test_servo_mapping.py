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


def test_home_servo_commands_and_pulses():
    mapping = load_servo_mapping(_actuator_file())
    commands = mapping.servo_commands_deg(0.0, 0.0, 0.0)
    pulses = mapping.servo_pulses_us(0.0, 0.0, 0.0)
    assert commands['lift'] == 90.0
    assert commands['tilt'] == 90.0
    assert commands['gripper'] == 0.0
    assert pulses['lift'] == 1500.0
    assert pulses['tilt'] == 1500.0
    assert pulses['gripper'] == 500.0


def test_positive_directions_match_physical_description():
    mapping = load_servo_mapping(_actuator_file())

    q1 = mapping.servo_commands_deg(0.15, 0.0, 0.0)
    assert q1['lift'] > 90.0       # left servo CCW
    assert q1['tilt'] < 90.0       # right servo CW because rear angle also rises

    q2 = mapping.servo_commands_deg(0.0, 0.15, 0.0)
    assert q2['lift'] == 90.0
    assert q2['tilt'] < 90.0       # pure rear lift: right servo CW

    q3 = mapping.servo_commands_deg(0.0, 0.0, math.pi / 2.0)
    assert abs(q3['gripper'] - 180.0) < 1e-9


def test_analytic_rejects_servo_limit():
    mapping = load_servo_mapping(_actuator_file())
    validator = SafetyValidator(mapping)
    result = validator.validate_point((1.0, 0.0, 0.0))
    assert not result.ok
    assert result.reason == 'lift_servo_limit'


def test_path_validation():
    mapping = load_servo_mapping(_actuator_file())
    validator = SafetyValidator(mapping)
    result = validator.validate_path((0.0, 0.0, 0.0), (0.2, -0.1, 0.4), math.radians(1.0))
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
                for q3 in (0.0, 0.1):
                    writer.writerow([q1, q2, q3, 90, 90, 0, 1, 1, 'safe', ''])

    grid = SafeRegionGrid(csv_path)
    assert grid.validate((0.05, 0.05, 0.05), 'cell').ok
    assert not grid.validate((0.15, 0.05, 0.05), 'cell').ok
