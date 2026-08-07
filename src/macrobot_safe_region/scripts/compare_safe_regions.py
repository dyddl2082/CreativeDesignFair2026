#!/usr/bin/env python3
"""Compare two safe_connected_samples.csv files."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def load(path: Path):
    with path.open('r', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    points = {
        (
            round(float(r['q1_rad']), 9),
            round(float(r['q2_rad']), 9),
            round(float(r['q3_rad']), 9),
        )
        for r in rows
    }
    return rows, points


def bounds(rows):
    result = {}
    for key in ('q1_rad', 'q2_rad', 'q3_rad'):
        values = [float(r[key]) for r in rows]
        result[key] = (min(values), max(values)) if values else (None, None)
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('first', type=Path)
    ap.add_argument('second', type=Path)
    args = ap.parse_args()

    rows_a, a = load(args.first)
    rows_b, b = load(args.second)

    print('A:', args.first)
    print('  rows:', len(rows_a), 'bounds:', bounds(rows_a))
    print('B:', args.second)
    print('  rows:', len(rows_b), 'bounds:', bounds(rows_b))
    print('common:', len(a & b))
    print('only A:', len(a - b))
    print('only B:', len(b - a))


if __name__ == '__main__':
    main()
