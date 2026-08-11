from __future__ import annotations

import json
import math
import time
from typing import Any, Dict, Mapping, Optional

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class VisiblePickTestNode(Node):
    """Thin integration-test client for an already-found, currently visible object.

    It does not implement perception, alignment, or arm control.  It verifies
    that a recent localized detection exists, then asks the formal stored-object
    pick node to run in ``visible_test`` mode.  The formal node still performs
    visual alignment and executes the recorded grasp through the validated arm
    path.
    """

    def __init__(self) -> None:
        super().__init__("macrobot_visible_pick_test")
        self.declare_parameter("goal_topic", "/macrobot/visible_pick_test/goal")
        self.declare_parameter("cancel_topic", "/macrobot/visible_pick_test/cancel")
        self.declare_parameter("status_topic", "/macrobot/visible_pick_test/status")
        self.declare_parameter("result_topic", "/macrobot/visible_pick_test/result")
        self.declare_parameter("stored_goal_topic", "/macrobot/stored_pick/goal")
        self.declare_parameter("stored_cancel_topic", "/macrobot/stored_pick/cancel")
        self.declare_parameter("stored_status_topic", "/macrobot/stored_pick/status")
        self.declare_parameter("stored_result_topic", "/macrobot/stored_pick/result")
        self.declare_parameter(
            "localized_detection_topic", "/macrobot/perception/localized_detection"
        )
        self.declare_parameter("detection_max_age_sec", 1.5)
        self.declare_parameter("default_timeout_sec", 90.0)

        self.status_pub = self.create_publisher(
            String, str(self.get_parameter("status_topic").value), 10
        )
        self.result_pub = self.create_publisher(
            String, str(self.get_parameter("result_topic").value), 10
        )
        self.stored_goal_pub = self.create_publisher(
            String, str(self.get_parameter("stored_goal_topic").value), 10
        )
        self.stored_cancel_pub = self.create_publisher(
            String, str(self.get_parameter("stored_cancel_topic").value), 10
        )

        self.create_subscription(
            String,
            str(self.get_parameter("goal_topic").value),
            self._goal_callback,
            10,
        )
        self.create_subscription(
            String,
            str(self.get_parameter("cancel_topic").value),
            self._cancel_callback,
            10,
        )
        self.create_subscription(
            String,
            str(self.get_parameter("localized_detection_topic").value),
            self._detection_callback,
            50,
        )
        self.create_subscription(
            String,
            str(self.get_parameter("stored_status_topic").value),
            self._stored_status_callback,
            20,
        )
        self.create_subscription(
            String,
            str(self.get_parameter("stored_result_topic").value),
            self._stored_result_callback,
            20,
        )

        self.latest_by_object: Dict[str, Dict[str, Any]] = {}
        self.active_request_id = ""
        self.active_object = ""
        self.get_logger().info(
            "Visible pick test ready: recent localized object -> visible_test align/grasp"
        )

    def _publish(self, publisher, payload: Mapping[str, Any]) -> None:
        msg = String()
        msg.data = json.dumps(dict(payload), ensure_ascii=False)
        publisher.publish(msg)

    def _detection_callback(self, msg: String) -> None:
        try:
            payload = json.loads(msg.data)
        except Exception:
            return
        if not isinstance(payload, dict) or payload.get("event") != "localized_object":
            return
        name = str(payload.get("object_name", "")).strip()
        point = payload.get("point_base")
        if not name or not isinstance(point, dict):
            return
        try:
            values = (float(point["x"]), float(point["y"]), float(point["z"]))
        except (KeyError, TypeError, ValueError):
            return
        if not all(math.isfinite(item) for item in values):
            return
        self.latest_by_object[name.casefold()] = {
            "received_monotonic": time.monotonic(),
            "payload": payload,
        }

    def _goal_callback(self, msg: String) -> None:
        try:
            request = json.loads(msg.data) if msg.data.strip().startswith("{") else {"object_name": msg.data.strip()}
            if not isinstance(request, dict):
                raise ValueError("goal must be a JSON object")
            object_name = str(request.get("object_name", "")).strip()
            if not object_name:
                raise ValueError("object_name is required")
            profile = str(request.get("profile", object_name)).strip()
            execute_pick = bool(request.get("execute_pick", True))
            latest = self.latest_by_object.get(object_name.casefold())
            if latest is None:
                raise ValueError("no localized detection has been received for the object")
            age = time.monotonic() - float(latest["received_monotonic"])
            maximum = float(self.get_parameter("detection_max_age_sec").value)
            if age > maximum:
                raise ValueError(f"localized detection is stale: age={age:.3f}s")
            request_id = str(request.get("request_id", f"visible-test-{int(time.time() * 1000)}"))
            timeout = float(request.get("timeout_sec", self.get_parameter("default_timeout_sec").value))
        except Exception as exc:
            self._publish(
                self.result_pub,
                {
                    "ok": False,
                    "event": "visible_pick_test_rejected",
                    "error": str(exc),
                },
            )
            return

        self.active_request_id = request_id
        self.active_object = object_name
        self._publish(
            self.stored_goal_pub,
            {
                "request_id": request_id,
                "object_name": object_name,
                "profile": profile,
                "mode": "visible_test",
                "start_finder": False,
                "execute_pick": execute_pick,
                "timeout_sec": timeout,
            },
        )
        self._publish(
            self.status_pub,
            {
                "ok": True,
                "event": "visible_pick_test_started",
                "request_id": request_id,
                "object_name": object_name,
                "profile": profile,
                "execute_pick": execute_pick,
            },
        )

    def _cancel_callback(self, msg: String) -> None:
        reason = msg.data.strip() or "visible_test_cancel"
        outgoing = String()
        outgoing.data = reason
        self.stored_cancel_pub.publish(outgoing)

    def _stored_status_callback(self, msg: String) -> None:
        payload = self._matching_payload(msg.data)
        if payload is None:
            return
        forwarded = dict(payload)
        forwarded["source"] = "stored_object_pick"
        self._publish(self.status_pub, forwarded)

    def _stored_result_callback(self, msg: String) -> None:
        payload = self._matching_payload(msg.data)
        if payload is None:
            return
        forwarded = dict(payload)
        forwarded["source"] = "stored_object_pick"
        self._publish(self.result_pub, forwarded)
        self.active_request_id = ""
        self.active_object = ""

    def _matching_payload(self, text: str) -> Optional[Dict[str, Any]]:
        if not self.active_request_id:
            return None
        try:
            payload = json.loads(text)
        except Exception:
            return None
        if not isinstance(payload, dict):
            return None
        if str(payload.get("request_id", "")) != self.active_request_id:
            return None
        return payload


def main(args=None) -> None:
    rclpy.init(args=args)
    node = VisiblePickTestNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
