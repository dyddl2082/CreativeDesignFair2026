"""Small command-line client for ``macrobot_object_finder``."""

from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Optional

import rclpy
from rclpy.node import Node
from rclpy.utilities import remove_ros_args
from std_msgs.msg import String


class FinderCliNode(Node):
    def __init__(self) -> None:
        super().__init__("macrobot_object_finder_cli")
        self.goal_pub = self.create_publisher(String, "/object_finder/goal", 10)
        self.cancel_pub = self.create_publisher(String, "/object_finder/cancel", 10)
        self.last_result: Optional[str] = None
        self.last_status: Optional[str] = None
        self.create_subscription(String, "/object_finder/result", self._result, 10)
        self.create_subscription(String, "/object_finder/status", self._status, 10)

    def _result(self, msg: String) -> None:
        self.last_result = msg.data

    def _status(self, msg: String) -> None:
        self.last_status = msg.data


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="MacRobot object finder CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    find = sub.add_parser("find", help="start object search")
    find.add_argument("object_name")
    find.add_argument("--timeout", type=float, default=60.0)
    find.add_argument("--once", action="store_true")
    find.add_argument("--rebuild-banks", action="store_true")
    find.add_argument("--min-score", type=float, default=0.0)
    find.add_argument("--no-wait", action="store_true")
    cancel = sub.add_parser("cancel", help="cancel active search")
    cancel.add_argument("--reason", default="user_cancel")
    sub.add_parser("status", help="print one status message")
    sub.add_parser("watch", help="print result messages until Ctrl+C")
    return parser


def _publish_connected(node: FinderCliNode, publisher, message: String, timeout: float = 3.0) -> None:
    deadline = time.monotonic() + timeout
    while rclpy.ok() and time.monotonic() < deadline:
        if publisher.get_subscription_count() > 0:
            publisher.publish(message)
            return
        rclpy.spin_once(node, timeout_sec=0.1)
    publisher.publish(message)


def _wait(node: FinderCliNode, attribute: str, timeout: float) -> Optional[str]:
    deadline = time.monotonic() + timeout
    while rclpy.ok() and time.monotonic() < deadline:
        rclpy.spin_once(node, timeout_sec=0.1)
        value = getattr(node, attribute)
        if value is not None:
            return value
    return None


def main(args=None) -> None:
    cli_args = remove_ros_args(args=sys.argv if args is None else args)[1:]
    options = _parser().parse_args(cli_args)
    rclpy.init(args=args)
    node = FinderCliNode()
    try:
        if options.command == "find":
            payload = {
                "object_name": options.object_name,
                "timeout_sec": options.timeout,
                "continuous": not options.once,
                "rebuild_banks": options.rebuild_banks,
                "min_score": options.min_score,
            }
            msg = String()
            msg.data = json.dumps(payload, ensure_ascii=False)
            _publish_connected(node, node.goal_pub, msg)
            time.sleep(0.2)
            print(msg.data)
            if not options.no_wait:
                result = _wait(node, "last_result", options.timeout + 5.0)
                if result is None:
                    raise SystemExit("No finder result received before timeout")
                print(result)
        elif options.command == "cancel":
            msg = String()
            msg.data = options.reason
            _publish_connected(node, node.cancel_pub, msg)
            time.sleep(0.2)
        elif options.command == "status":
            status = _wait(node, "last_status", 5.0)
            if status is None:
                raise SystemExit("No /object_finder/status message received")
            print(status)
        elif options.command == "watch":
            previous = None
            while rclpy.ok():
                rclpy.spin_once(node, timeout_sec=0.2)
                if node.last_result is not None and node.last_result != previous:
                    print(node.last_result, flush=True)
                    previous = node.last_result
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
