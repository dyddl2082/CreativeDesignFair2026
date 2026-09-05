#!/usr/bin/env python3
"""Wait for one ROS 2 message without relying on `timeout ros2 topic echo`.

This helper is intended for MacRobot diagnostics.  It creates and shuts down its
own rclpy context cleanly, so a timeout cannot leave `ros2 topic echo` in an
invalid-context shutdown race.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from typing import Any

import rclpy
from rclpy.node import Node
from rclpy.qos import (
    DurabilityPolicy,
    HistoryPolicy,
    QoSProfile,
    ReliabilityPolicy,
)
from rosidl_runtime_py.convert import message_to_ordereddict
from rosidl_runtime_py.utilities import get_message


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("topic")
    parser.add_argument("--field", default="")
    parser.add_argument("--timeout", type=float, default=7.0)
    parser.add_argument(
        "--reliability",
        choices=("best_effort", "reliable"),
        default="best_effort",
    )
    return parser.parse_args()


def field_value(message: Any, field_path: str) -> Any:
    value = message
    if field_path:
        for part in field_path.split("."):
            if not hasattr(value, part):
                raise AttributeError(
                    f"field {field_path!r} is unavailable at component {part!r}"
                )
            value = getattr(value, part)
    return value


def printable(value: Any) -> str:
    if hasattr(value, "get_fields_and_field_types"):
        return json.dumps(
            message_to_ordereddict(value),
            ensure_ascii=False,
            sort_keys=False,
        )
    if isinstance(value, (str, int, float, bool)) or value is None:
        return str(value)
    if isinstance(value, (list, tuple, dict)):
        return json.dumps(value, ensure_ascii=False, default=str)
    return str(value)


def main() -> int:
    args = parse_args()
    timeout_sec = max(0.1, float(args.timeout))
    deadline = time.monotonic() + timeout_sec

    rclpy.init(args=[])
    node = Node(f"macrobot_topic_probe_{os.getpid()}")
    subscription = None

    try:
        topic_types: list[str] = []
        while time.monotonic() < deadline:
            names_and_types = dict(node.get_topic_names_and_types())
            topic_types = list(names_and_types.get(args.topic, []))
            if topic_types:
                break
            rclpy.spin_once(node, timeout_sec=0.1)

        if not topic_types:
            print(f"topic not discovered: {args.topic}", file=sys.stderr)
            return 2

        try:
            message_type = get_message(topic_types[0])
        except (AttributeError, ImportError, ValueError) as exc:
            print(
                f"cannot import topic type {topic_types[0]!r}: {exc}",
                file=sys.stderr,
            )
            return 3

        qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
            reliability=(
                ReliabilityPolicy.BEST_EFFORT
                if args.reliability == "best_effort"
                else ReliabilityPolicy.RELIABLE
            ),
            durability=DurabilityPolicy.VOLATILE,
        )

        received: list[Any] = []

        def callback(message: Any) -> None:
            if not received:
                received.append(message)

        subscription = node.create_subscription(
            message_type,
            args.topic,
            callback,
            qos,
        )

        while time.monotonic() < deadline and not received:
            remaining = max(0.0, deadline - time.monotonic())
            rclpy.spin_once(node, timeout_sec=min(0.2, remaining))

        if not received:
            print(f"no sample within {timeout_sec:.1f}s: {args.topic}", file=sys.stderr)
            return 4

        try:
            value = field_value(received[0], args.field)
        except AttributeError as exc:
            print(str(exc), file=sys.stderr)
            return 5

        print(printable(value))
        return 0
    finally:
        if subscription is not None:
            node.destroy_subscription(subscription)
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
