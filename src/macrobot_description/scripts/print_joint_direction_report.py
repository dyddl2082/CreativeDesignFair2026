#!/usr/bin/env python3
from pathlib import Path
import csv

package = Path(__file__).resolve().parents[1]
print('model_revision: macrobot-serial-2axis-2026-09-04-r4')
print('source_archive: macrobot_description(4).zip')
print('shoulder_axis_base: 0.000000020 1.000000000 0.000000022')
print('wrist_axis_base_zero: 0.000000020 1.000000000 -0.000000305')
print('axis_alignment: 1.000000000000')
print('zero_grasp_xyz: -0.181900056 0.063000003 0.226997937')
print('gripper_servo_mimic: +2.0')
print()
print('Kinematic samples:')
with (package/'validation/KINEMATIC_SANITY_SAMPLES.csv').open() as f:
    for row in csv.DictReader(f):
        print(row)
print()
print('Gripper samples:')
with (package/'validation/GRIPPER_DIRECTION_SAMPLES.csv').open() as f:
    for row in csv.DictReader(f):
        print(row)
