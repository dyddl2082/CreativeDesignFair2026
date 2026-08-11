from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Any, Dict, Optional

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class _Client(Node):
    def __init__(self) -> None:
        super().__init__("stored_object_pick_cli")
        self.goal_pub = self.create_publisher(String, "/macrobot/stored_pick/goal", 10)
        self.record_pub = self.create_publisher(String, "/macrobot/stored_pick/record", 10)
        self.admin_pub = self.create_publisher(String, "/macrobot/stored_pick/admin", 10)
        self.cancel_pub = self.create_publisher(String, "/macrobot/stored_pick/cancel", 10)
        self.visible_goal_pub = self.create_publisher(String, "/macrobot/visible_pick_test/goal", 10)
        self.visible_cancel_pub = self.create_publisher(String, "/macrobot/visible_pick_test/cancel", 10)
        self.result: Optional[Dict[str, Any]] = None
        self.request_id = ""
        self.create_subscription(String, "/macrobot/stored_pick/result", self._result_cb, 20)
        self.create_subscription(String, "/macrobot/visible_pick_test/result", self._result_cb, 20)
        self.create_subscription(String, "/macrobot/stored_pick/status", self._status_cb, 20)

    def _result_cb(self, msg: String) -> None:
        try:
            payload = json.loads(msg.data)
        except Exception:
            return
        if not isinstance(payload, dict):
            return
        if self.request_id and str(payload.get("request_id", "")) != self.request_id:
            return
        self.result = payload

    def _status_cb(self, msg: String) -> None:
        try:
            payload = json.loads(msg.data)
        except Exception:
            return
        if not isinstance(payload, dict):
            return
        if self.request_id and str(payload.get("request_id", "")) != self.request_id:
            return
        print(json.dumps(payload, ensure_ascii=False), flush=True)
        if not self.request_id and str(payload.get("event", "")) in {
            "stored_object_profiles",
            "stored_object_profiles_reloaded",
            "stored_object_profile_deleted",
            "stored_object_profile_not_found",
            "stored_object_admin_failed",
        }:
            self.result = payload

    @staticmethod
    def _publish(pub, payload: object) -> None:
        msg = String()
        msg.data = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False)
        pub.publish(msg)

    def wait(self, timeout: float) -> Optional[Dict[str, Any]]:
        deadline = time.monotonic() + timeout
        while rclpy.ok() and time.monotonic() < deadline:
            rclpy.spin_once(self, timeout_sec=0.1)
            if self.result is not None:
                return self.result
        return None


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Record, test, or run stored-object picking")
    sub = parser.add_subparsers(dest="command", required=True)

    record = sub.add_parser("record", help="Record current graspable camera/base pose")
    record.add_argument("object_name")
    record.add_argument("--profile", default="")
    record.add_argument("--grasp-trajectory", required=True)
    record.add_argument("--pick-profile", default="")
    record.add_argument("--no-finder", action="store_true")
    record.add_argument("--timeout", type=float, default=40.0)

    visible = sub.add_parser("visible-test", help="Assume object is already localized; align and grasp")
    visible.add_argument("object_name")
    visible.add_argument("--profile", default="")
    visible.add_argument("--align-only", action="store_true")
    visible.add_argument("--timeout", type=float, default=120.0)

    run = sub.add_parser("run", help="Return near stored pose, find, align, and grasp")
    run.add_argument("object_name")
    run.add_argument("--profile", default="")
    run.add_argument("--align-only", action="store_true")
    run.add_argument("--timeout", type=float, default=180.0)

    sub.add_parser("list", help="List stored runtime profiles")
    delete = sub.add_parser("delete", help="Delete a stored profile")
    delete.add_argument("profile")
    sub.add_parser("reload", help="Reload the profile file")
    sub.add_parser("cancel", help="Cancel active search/alignment/grasp")
    return parser


def main(argv=None) -> None:
    args = _parser().parse_args(argv)
    rclpy.init()
    node = _Client()
    try:
        request_id = f"cli-{args.command}-{int(time.time() * 1000)}"
        node.request_id = request_id
        timeout = float(getattr(args, "timeout", 10.0))

        if args.command == "record":
            node._publish(
                node.record_pub,
                {
                    "request_id": request_id,
                    "object_name": args.object_name,
                    "profile": args.profile or args.object_name,
                    "grasp_trajectory": args.grasp_trajectory,
                    "pick_profile": args.pick_profile or args.object_name,
                    "start_finder": not args.no_finder,
                },
            )
        elif args.command == "visible-test":
            node._publish(
                node.visible_goal_pub,
                {
                    "request_id": request_id,
                    "object_name": args.object_name,
                    "profile": args.profile or args.object_name,
                    "execute_pick": not args.align_only,
                    "timeout_sec": timeout,
                },
            )
        elif args.command == "run":
            node._publish(
                node.goal_pub,
                {
                    "request_id": request_id,
                    "object_name": args.object_name,
                    "profile": args.profile or args.object_name,
                    "mode": "full",
                    "start_finder": True,
                    "execute_pick": not args.align_only,
                    "timeout_sec": timeout,
                },
            )
        elif args.command == "list":
            node.request_id = ""
            node._publish(node.admin_pub, {"action": "list"})
            timeout = 2.0
        elif args.command == "delete":
            node.request_id = ""
            node._publish(node.admin_pub, {"action": "delete", "profile": args.profile})
            timeout = 2.0
        elif args.command == "reload":
            node.request_id = ""
            node._publish(node.admin_pub, {"action": "reload"})
            timeout = 2.0
        else:
            node.request_id = ""
            node._publish(node.cancel_pub, "user_cancel")
            node._publish(node.visible_cancel_pub, "user_cancel")
            timeout = 5.0

        result = node.wait(timeout)
        if result is None:
            print("No terminal result received before timeout", file=sys.stderr)
            raise SystemExit(2)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        raise SystemExit(0 if result.get("ok") is True else 1)
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
