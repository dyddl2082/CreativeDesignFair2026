#!/usr/bin/env python3
"""Wait for one TF and optionally validate its translation."""

from __future__ import annotations

import argparse
import math
import os
import sys
import time
import uuid

import rclpy
from rclpy.time import Time
from tf2_ros import Buffer, TransformListener


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target")
    parser.add_argument("source")
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--expect-x", type=float)
    parser.add_argument("--expect-y", type=float)
    parser.add_argument("--expect-z", type=float)
    parser.add_argument("--translation-tolerance", type=float, default=0.002)
    args = parser.parse_args()

    expected_values = (args.expect_x, args.expect_y, args.expect_z)
    if any(value is not None for value in expected_values) and not all(
        value is not None for value in expected_values
    ):
        parser.error("--expect-x, --expect-y and --expect-z must be used together")

    rclpy.init(args=None)
    node = rclpy.create_node(
        f"macrobot_tf_wait_{os.getpid()}_{uuid.uuid4().hex[:6]}"
    )
    buffer = Buffer()
    listener = TransformListener(buffer, node, spin_thread=False)
    del listener

    deadline = time.monotonic() + max(args.timeout, 0.1)
    last_error = "no transform received"

    try:
        while rclpy.ok() and time.monotonic() < deadline:
            rclpy.spin_once(node, timeout_sec=0.1)
            try:
                transform = buffer.lookup_transform(
                    args.target,
                    args.source,
                    Time(),
                )
            except Exception as exc:  # tf2 exception classes vary by distro
                last_error = str(exc)
                continue

            translation = transform.transform.translation
            rotation = transform.transform.rotation

            if all(value is not None for value in expected_values):
                expected = (
                    float(args.expect_x),
                    float(args.expect_y),
                    float(args.expect_z),
                )
                actual = (translation.x, translation.y, translation.z)
                error = math.sqrt(
                    sum((actual[index] - expected[index]) ** 2 for index in range(3))
                )
                if error > max(args.translation_tolerance, 0.0):
                    last_error = (
                        "transform exists but translation does not match the r4 "
                        f"camera anchor: actual={actual}, expected={expected}, "
                        f"error={error:.6f} m"
                    )
                    continue

            print(f"TF ready: {args.target} <- {args.source}")
            print(
                "translation: "
                f"[{translation.x:.9f}, {translation.y:.9f}, {translation.z:.9f}]"
            )
            print(
                "quaternion_xyzw: "
                f"[{rotation.x:.9f}, {rotation.y:.9f}, "
                f"{rotation.z:.9f}, {rotation.w:.9f}]"
            )
            return 0

        print(
            f"ERROR: TF unavailable after {args.timeout:.1f}s: "
            f"{args.target} <- {args.source}\nlast_error: {last_error}",
            file=sys.stderr,
        )
        return 2
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
