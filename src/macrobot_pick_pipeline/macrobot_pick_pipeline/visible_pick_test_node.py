from __future__ import annotations

import json
import math
import time
from typing import Any, Dict, Mapping, Optional

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class VisiblePickTestNode(Node):
    """Reliable visible-object client for the formal stored-object task node.

    The old implementation required a localized result to have arrived within a
    very short window *before* the command was accepted.  That is brittle when
    DINOv2 and temporal confirmation run on WSL2.  This node now acknowledges
    the operator request immediately, asks the formal task node to start the
    finder in ``visible_test`` mode, and retries the same request ID until the
    stored-object node acknowledges it.  The formal node remains responsible
    for perception, bounded search, alignment, safety validation and grasping.
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
        self.declare_parameter("detection_max_age_sec", 8.0)
        self.declare_parameter("default_timeout_sec", 120.0)
        self.declare_parameter("start_finder", True)
        self.declare_parameter("stored_goal_retry_period_sec", 0.75)
        self.declare_parameter("stored_goal_ack_timeout_sec", 12.0)

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
        self.create_timer(0.10, self._timer_callback)

        self.latest_by_object: Dict[str, Dict[str, Any]] = {}
        self.active_request_id = ""
        self.active_object = ""
        self.stored_goal_payload: Dict[str, Any] = {}
        self.stored_goal_started_monotonic = 0.0
        self.stored_goal_last_publish_monotonic = 0.0
        self.stored_goal_publish_count = 0
        self.stored_goal_acknowledged = False
        self.get_logger().info(
            "Visible pick test ready: request-id handshake -> finder-backed visible_test"
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

    def _recent_detection_summary(self, object_name: str) -> Dict[str, Any]:
        latest = self.latest_by_object.get(object_name.casefold())
        if latest is None:
            return {
                "recent_detection_available": False,
                "recent_detection_age_sec": None,
            }
        age = max(0.0, time.monotonic() - float(latest["received_monotonic"]))
        maximum = max(0.0, float(self.get_parameter("detection_max_age_sec").value))
        return {
            "recent_detection_available": age <= maximum,
            "recent_detection_age_sec": age,
            "recent_detection_max_age_sec": maximum,
        }

    def _goal_callback(self, msg: String) -> None:
        request: Dict[str, Any] = {}
        request_id = f"visible-test-{int(time.time() * 1000)}"
        object_name = ""
        try:
            request = (
                json.loads(msg.data)
                if msg.data.strip().startswith("{")
                else {"object_name": msg.data.strip()}
            )
            if not isinstance(request, dict):
                raise ValueError("goal must be a JSON object")
            request_id = str(request.get("request_id", request_id)).strip() or request_id
            object_name = str(request.get("object_name", "")).strip()
            if not object_name:
                raise ValueError("object_name is required")
            profile = str(request.get("profile", object_name)).strip() or object_name
            execute_pick = bool(request.get("execute_pick", True))
            timeout = float(
                request.get(
                    "timeout_sec", self.get_parameter("default_timeout_sec").value
                )
            )
            if not math.isfinite(timeout) or timeout <= 0.0:
                raise ValueError("timeout_sec must be positive and finite")
            start_finder = bool(
                request.get("start_finder", self.get_parameter("start_finder").value)
            )
            rebuild_banks = bool(request.get("rebuild_banks", False))

            if self.active_request_id:
                if request_id == self.active_request_id:
                    self._publish(
                        self.status_pub,
                        {
                            "ok": True,
                            "event": "visible_pick_test_command_acknowledged",
                            "request_id": request_id,
                            "object_name": self.active_object,
                            "duplicate": True,
                            "stored_goal_acknowledged": self.stored_goal_acknowledged,
                        },
                    )
                    self._publish_stored_goal(force=True)
                    return
                raise RuntimeError("another visible-test request is active")
        except Exception as exc:
            self._publish(
                self.result_pub,
                {
                    "ok": False,
                    "event": "visible_pick_test_rejected",
                    "request_id": request_id,
                    "object_name": object_name,
                    "error_code": (
                        "RESOURCE_BUSY" if isinstance(exc, RuntimeError) else "INVALID_ARGUMENT"
                    ),
                    "error": str(exc),
                },
            )
            return

        self.active_request_id = request_id
        self.active_object = object_name
        self.stored_goal_payload = {
            "request_id": request_id,
            "object_name": object_name,
            "profile": profile,
            "mode": "visible_test",
            "start_finder": start_finder,
            "execute_pick": execute_pick,
            "rebuild_banks": rebuild_banks,
            "timeout_sec": timeout,
        }
        self.stored_goal_started_monotonic = time.monotonic()
        self.stored_goal_last_publish_monotonic = 0.0
        self.stored_goal_publish_count = 0
        self.stored_goal_acknowledged = False
        self._publish(
            self.status_pub,
            {
                "ok": True,
                "event": "visible_pick_test_command_acknowledged",
                "request_id": request_id,
                "object_name": object_name,
                "profile": profile,
                "execute_pick": execute_pick,
                "start_finder": start_finder,
                "duplicate": False,
                "preexisting_detection_is_not_required": True,
                **self._recent_detection_summary(object_name),
            },
        )
        self._publish_stored_goal(force=True)

    def _publish_stored_goal(self, *, force: bool = False) -> None:
        if (
            not self.active_request_id
            or self.stored_goal_acknowledged
            or not self.stored_goal_payload
        ):
            return
        now = time.monotonic()
        period = max(
            0.1, float(self.get_parameter("stored_goal_retry_period_sec").value)
        )
        if not force and now - self.stored_goal_last_publish_monotonic < period:
            return
        self._publish(self.stored_goal_pub, self.stored_goal_payload)
        self.stored_goal_last_publish_monotonic = now
        self.stored_goal_publish_count += 1
        if self.stored_goal_publish_count == 1 or self.stored_goal_publish_count % 4 == 0:
            self._publish(
                self.status_pub,
                {
                    "ok": True,
                    "event": "visible_pick_test_forwarded",
                    "request_id": self.active_request_id,
                    "object_name": self.active_object,
                    "stored_goal_publish_count": self.stored_goal_publish_count,
                    "stored_goal_subscribers": self.stored_goal_pub.get_subscription_count(),
                    "waiting_for_stored_ack": True,
                },
            )

    def _timer_callback(self) -> None:
        if not self.active_request_id or self.stored_goal_acknowledged:
            return
        self._publish_stored_goal()
        timeout = max(
            1.0, float(self.get_parameter("stored_goal_ack_timeout_sec").value)
        )
        if time.monotonic() - self.stored_goal_started_monotonic < timeout:
            return
        subscribers = self.stored_goal_pub.get_subscription_count()
        error = (
            "no /macrobot/stored_pick/goal subscriber discovered"
            if subscribers <= 0
            else "stored-object node did not acknowledge the visible-test request_id"
        )
        self._publish(
            self.result_pub,
            {
                "ok": False,
                "event": "visible_pick_test_delivery_failed",
                "request_id": self.active_request_id,
                "object_name": self.active_object,
                "error_code": "CONTROL_UNAVAILABLE",
                "error": error,
                "stored_goal_publish_count": self.stored_goal_publish_count,
                "stored_goal_subscribers": subscribers,
            },
        )
        self._clear_active()

    def _cancel_callback(self, msg: String) -> None:
        reason = msg.data.strip() or "visible_test_cancel"
        outgoing = String()
        outgoing.data = reason
        self.stored_cancel_pub.publish(outgoing)
        if self.active_request_id:
            self._publish(
                self.status_pub,
                {
                    "ok": True,
                    "event": "visible_pick_test_cancel_forwarded",
                    "request_id": self.active_request_id,
                    "object_name": self.active_object,
                    "reason": reason,
                },
            )

    def _stored_status_callback(self, msg: String) -> None:
        payload = self._matching_payload(msg.data)
        if payload is None:
            return
        self.stored_goal_acknowledged = True
        forwarded = dict(payload)
        forwarded["source"] = "stored_object_pick"
        self._publish(self.status_pub, forwarded)

    def _stored_result_callback(self, msg: String) -> None:
        payload = self._matching_payload(msg.data)
        if payload is None:
            return
        self.stored_goal_acknowledged = True
        forwarded = dict(payload)
        forwarded["source"] = "stored_object_pick"
        self._publish(self.result_pub, forwarded)
        self._clear_active()

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

    def _clear_active(self) -> None:
        self.active_request_id = ""
        self.active_object = ""
        self.stored_goal_payload = {}
        self.stored_goal_started_monotonic = 0.0
        self.stored_goal_last_publish_monotonic = 0.0
        self.stored_goal_publish_count = 0
        self.stored_goal_acknowledged = False


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
