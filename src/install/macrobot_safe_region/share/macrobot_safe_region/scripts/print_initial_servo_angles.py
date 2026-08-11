#!/usr/bin/env python3
"""Print the physical zero/install angles for the corrected MacRobot arm."""

import math

q1_home = 0.0
q2_home = 0.0
q3_open = 0.0
q3_closed = math.pi / 2.0

left_home_deg = 90.0 + math.degrees(2.0 * q1_home)
right_home_deg = 90.0 - math.degrees(2.0 * (q1_home + q2_home))
gripper_open_deg = math.degrees(2.0 * q3_open)
gripper_closed_deg = math.degrees(2.0 * q3_closed)

print(f"Left MG996R (arm tilt) install: {left_home_deg:.3f} deg at q1=0")
print(f"Right MG996R (rear lift) install: {right_home_deg:.3f} deg at q1=q2=0")
print(f"MG90S gripper install open: {gripper_open_deg:.3f} deg at q3=0")
print(f"MG90S gripper expected closed: {gripper_closed_deg:.3f} deg at q3=pi/2")
print(f"Required gripper servo travel: {gripper_closed_deg - gripper_open_deg:.3f} deg CCW")
print("500/1500/2500 us nominal pulses: home/open = ARM_US 1500 1500 500")
