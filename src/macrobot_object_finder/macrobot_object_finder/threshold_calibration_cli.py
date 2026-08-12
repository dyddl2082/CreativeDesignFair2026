"""Small CLI for explicit field-threshold calibration."""

from __future__ import annotations

import argparse
import json
import sys
import time
import uuid

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class CalibrationClient(Node):
    def __init__(self, timeout_sec: float) -> None:
        super().__init__("threshold_calibration_cli")
        self.publisher = self.create_publisher(
            String, "/object_finder/calibration/command", 10
        )
        self.result = None
        self.create_subscription(
            String,
            "/object_finder/calibration/result",
            self._result_callback,
            10,
        )
        self.timeout_sec = timeout_sec

    def _result_callback(self, message: String) -> None:
        try:
            self.result = json.loads(message.data)
        except Exception:
            self.result = {"ok": False, "event": "invalid_result", "raw": message.data}

    def send(self, payload: dict) -> dict:
        message = String()
        message.data = json.dumps(payload, ensure_ascii=False)
        deadline = time.monotonic() + self.timeout_sec
        # Transient startup discovery can otherwise drop a one-shot command.
        for _ in range(3):
            self.publisher.publish(message)
            rclpy.spin_once(self, timeout_sec=0.25)
        while rclpy.ok() and self.result is None and time.monotonic() < deadline:
            rclpy.spin_once(self, timeout_sec=0.2)
        return self.result or {
            "ok": False,
            "event": "calibration_cli_timeout",
            "reason": "no result before CLI timeout",
        }


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="MacRobot threshold calibration CLI")
    sub = root.add_subparsers(dest="command", required=True)
    calibrate = sub.add_parser("calibrate")
    calibrate.add_argument("object_name")
    calibrate.add_argument("--environment", default="default")
    calibrate.add_argument("--duration", type=float, default=8.0)
    calibrate.add_argument("--no-apply", action="store_true")
    calibrate.add_argument("--confirm-visible", action="store_true")
    apply_cmd = sub.add_parser("apply")
    apply_cmd.add_argument("object_name")
    apply_cmd.add_argument("--environment", default="default")
    sub.add_parser("list")
    sub.add_parser("cancel")
    root.add_argument("--timeout", type=float, default=40.0)
    return root


def main(argv=None) -> None:
    args = parser().parse_args(argv)
    if args.command == "calibrate" and not args.confirm_visible:
        print(
            "Refusing calibration: place the requested object clearly in view and add "
            "--confirm-visible. Normal search must never auto-lower thresholds.",
            file=sys.stderr,
        )
        raise SystemExit(2)
    payload = {"request_id": f"threshold-cli-{uuid.uuid4().hex[:10]}"}
    if args.command == "calibrate":
        payload.update(
            {
                "action": "start",
                "object_name": args.object_name,
                "environment_id": args.environment,
                "duration_sec": args.duration,
                "apply": not args.no_apply,
                "operator_confirms_visible": True,
            }
        )
    elif args.command == "apply":
        payload.update(
            {
                "action": "apply",
                "object_name": args.object_name,
                "environment_id": args.environment,
            }
        )
    else:
        payload["action"] = args.command

    rclpy.init()
    node = CalibrationClient(args.timeout)
    try:
        result = node.send(payload)
    finally:
        node.destroy_node()
        rclpy.shutdown()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if bool(result.get("ok", False)) else 1)


if __name__ == "__main__":
    main()
