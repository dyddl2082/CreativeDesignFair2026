#!/usr/bin/env python3
import math

q3_closed = -1.25
travel_deg = abs(math.degrees(2.0 * q3_closed))
open_deg = 90.0 + travel_deg / 2.0
closed_deg = 90.0 - travel_deg / 2.0
print(f"MG996R lift install: 90.000 deg at q1=0")
print(f"MG996R tilt install: 90.000 deg at q1=q2=0")
print(f"MG90S gripper install open: {open_deg:.4f} deg")
print(f"MG90S gripper expected closed: {closed_deg:.4f} deg")
print(f"Required gripper servo travel: {travel_deg:.4f} deg")
