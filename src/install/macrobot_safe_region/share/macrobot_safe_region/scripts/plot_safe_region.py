#!/usr/bin/env python3
"""Plot a q1-q2 projection of the connected safe region for selected q3 slices."""
from pathlib import Path
import argparse
import csv


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('csv_path', type=Path)
    parser.add_argument('--output', type=Path, default=Path('safe_region.png'))
    parser.add_argument('--q3', type=float, default=0.0, help='Desired gripper q3 slice in radians')
    args = parser.parse_args()

    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise SystemExit('Install matplotlib: sudo apt install python3-matplotlib') from exc

    rows = []
    with args.csv_path.open(newline='') as f:
        for row in csv.DictReader(f):
            rows.append({k: float(v) if k.endswith('_rad') else v for k, v in row.items()})
    if not rows:
        raise SystemExit('CSV has no samples')
    q3_available = sorted({row['q3_rad'] for row in rows})
    q3 = min(q3_available, key=lambda value: abs(value - args.q3))
    selected = [row for row in rows if abs(row['q3_rad'] - q3) < 1e-9]

    plt.figure(figsize=(8, 6))
    plt.scatter([r['q1_rad'] for r in selected], [r['q2_rad'] for r in selected], s=12)
    plt.xlabel('q1 arm forward tilt (legacy arm_lift_joint) [rad]')
    plt.ylabel('q2 relative rear lift (legacy wrist_pitch_joint) [rad]')
    plt.title(f'MacRobot connected safe region, q3={q3:.3f} rad')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(args.output, dpi=160)
    print(args.output)

if __name__ == '__main__':
    main()
