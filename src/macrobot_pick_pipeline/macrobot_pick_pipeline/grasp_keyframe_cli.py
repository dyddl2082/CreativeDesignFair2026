"""CLI for semantic grasp keyframe capture and playback."""

from __future__ import annotations

import argparse
import json
import time
import uuid

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class Client(Node):
    def __init__(self, timeout: float) -> None:
        super().__init__("grasp_keyframe_cli")
        self.pub = self.create_publisher(String, "/macrobot/grasp_keyframes/command", 10)
        self.result = None
        self.create_subscription(
            String, "/macrobot/grasp_keyframes/result", self._callback, 10
        )
        self.timeout = timeout

    def _callback(self, message: String) -> None:
        try:
            self.result = json.loads(message.data)
        except Exception:
            self.result = {"ok": False, "event": "invalid_result", "raw": message.data}

    def call(self, payload: dict) -> dict:
        message = String()
        message.data = json.dumps(payload, ensure_ascii=False)
        for _ in range(3):
            self.pub.publish(message)
            rclpy.spin_once(self, timeout_sec=0.2)
        deadline = time.monotonic() + self.timeout
        while rclpy.ok() and self.result is None and time.monotonic() < deadline:
            rclpy.spin_once(self, timeout_sec=0.2)
        return self.result or {"ok": False, "event": "cli_timeout"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Semantic grasp keyframe CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    capture = sub.add_parser("capture")
    capture.add_argument("profile")
    capture.add_argument("object_name")
    capture.add_argument("stage", choices=["OPEN", "PRE_GRASP", "GRASP_OPEN", "CLOSE", "LIFT"])
    finalize = sub.add_parser("finalize")
    finalize.add_argument("profile")
    play = sub.add_parser("play")
    play.add_argument("profile")
    play.add_argument("--object-name", default="")
    preflight = sub.add_parser("preflight")
    preflight.add_argument("profile")
    preflight.add_argument("--object-name", default="")
    delete = sub.add_parser("delete")
    delete.add_argument("profile")
    sub.add_parser("list")
    sub.add_parser("cancel")
    parser.add_argument("--timeout", type=float, default=120.0)
    return parser


def main(argv=None) -> None:
    args = build_parser().parse_args(argv)
    payload = {"command_id": f"keyframe-cli-{uuid.uuid4().hex[:10]}"}
    if args.command == "capture":
        payload.update(
            {
                "action": "capture",
                "profile": args.profile,
                "object_name": args.object_name,
                "stage": args.stage,
            }
        )
    elif args.command in {"play", "preflight"}:
        payload.update(
            {
                "action": args.command,
                "profile": args.profile,
                "object_name": args.object_name,
            }
        )
    elif args.command in {"finalize", "delete"}:
        payload.update({"action": args.command, "profile": args.profile})
    else:
        payload["action"] = args.command
    rclpy.init()
    node = Client(args.timeout)
    try:
        result = node.call(payload)
    finally:
        node.destroy_node()
        rclpy.shutdown()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if bool(result.get("ok", False)) else 1)


if __name__ == "__main__":
    main()
