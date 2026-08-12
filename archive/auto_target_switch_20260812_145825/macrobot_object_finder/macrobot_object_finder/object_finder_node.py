"""Commandable object-finder manager for the existing MacRobot D435 pipeline."""

from __future__ import annotations

import json
import math
from pathlib import Path
import time
from typing import Any, Optional

from geometry_msgs.msg import PointStamped
from macrobot_interfaces.msg import TemporalConfirmationResult
import rclpy
from rclpy.node import Node
from rclpy.qos import (
    DurabilityPolicy,
    HistoryPolicy,
    QoSProfile,
    ReliabilityPolicy,
    qos_profile_sensor_data,
)
from sensor_msgs.msg import CameraInfo
from std_msgs.msg import String
from std_srvs.srv import Trigger

from .finder_core import (
    FinderGoal,
    FinderSession,
    not_found_payload,
    parse_goal_text,
    temporal_message_is_usable,
    temporal_to_result_payload,
)


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


class ObjectFinderNode(Node):
    """Turn the candidate/filter/embedding/temporal chain into a finder API.

    The node never subscribes to RGB or depth images.  It consumes only compact
    metadata and the typed temporal-confirmation output, then publishes the
    canonical JSON contract used by ``macrobot_pick_pipeline``.
    """

    def __init__(self) -> None:
        super().__init__("macrobot_object_finder")
        self._declare_parameters()

        self.session = FinderSession()
        self.camera_info: Optional[CameraInfo] = None
        self.last_camera_info = 0.0
        self.last_filter_status = 0.0
        self.last_embedding_status = 0.0
        self.last_temporal_status = 0.0
        self.status_payloads: dict[str, dict[str, Any]] = {}
        self.target_repeat_remaining = 0
        self.last_target_publish = 0.0
        self.last_found_publish = 0.0

        reliable = QoSProfile(depth=20)
        reliable.reliability = ReliabilityPolicy.RELIABLE
        target_qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )

        self.result_pub = self.create_publisher(
            String, str(self.get_parameter("result_topic").value), reliable
        )
        self.status_pub = self.create_publisher(
            String, str(self.get_parameter("status_topic").value), 10
        )
        self.active_target_pub = self.create_publisher(
            String, str(self.get_parameter("active_target_topic").value), target_qos
        )
        self.candidate_target_pub = self.create_publisher(
            String, str(self.get_parameter("candidate_target_topic").value), target_qos
        )
        self.embedding_target_pub = self.create_publisher(
            String, str(self.get_parameter("embedding_target_topic").value), target_qos
        )
        self.point_camera_pub = self.create_publisher(
            PointStamped, str(self.get_parameter("point_camera_topic").value), 10
        )

        self.create_subscription(
            String,
            str(self.get_parameter("goal_topic").value),
            self._goal_callback,
            reliable,
        )
        self.create_subscription(
            String,
            str(self.get_parameter("cancel_topic").value),
            self._cancel_callback,
            reliable,
        )
        self.create_subscription(
            TemporalConfirmationResult,
            str(self.get_parameter("confirmed_topic").value),
            self._confirmed_callback,
            reliable,
        )
        self.create_subscription(
            TemporalConfirmationResult,
            str(self.get_parameter("temporal_events_topic").value),
            self._temporal_event_callback,
            reliable,
        )
        self.create_subscription(
            CameraInfo,
            str(self.get_parameter("camera_info_topic").value),
            self._camera_info_callback,
            qos_profile_sensor_data,
        )
        for key, topic_param in (
            ("filter", "filter_status_topic"),
            ("embedding", "embedding_status_topic"),
            ("temporal", "temporal_status_topic"),
        ):
            self.create_subscription(
                String,
                str(self.get_parameter(topic_param).value),
                lambda msg, source=key: self._component_status_callback(source, msg),
                10,
            )

        self.temporal_reset_client = self.create_client(
            Trigger, str(self.get_parameter("temporal_reset_service").value)
        )
        self.candidate_reload_client = self.create_client(
            Trigger, str(self.get_parameter("candidate_reload_service").value)
        )
        self.embedding_reload_client = self.create_client(
            Trigger, str(self.get_parameter("embedding_reload_service").value)
        )
        self.embedding_rebuild_client = self.create_client(
            Trigger, str(self.get_parameter("embedding_rebuild_service").value)
        )

        timer_hz = max(float(self.get_parameter("timer_hz").value), 1.0)
        self.timer = self.create_timer(1.0 / timer_hz, self._timer_callback)
        self.get_logger().info(
            "Object finder ready: /object_finder/goal -> typed temporal confirmation "
            "-> canonical /object_finder/result (no full-image subscription)"
        )

    def _declare_parameters(self) -> None:
        defaults = {
            "goal_topic": "/object_finder/goal",
            "cancel_topic": "/object_finder/cancel",
            "result_topic": "/object_finder/result",
            "status_topic": "/object_finder/status",
            "active_target_topic": "/macrobot/pick/active_target",
            "candidate_target_topic": "/candidate_filter/target",
            "embedding_target_topic": "/embedding_retrieval/target",
            "confirmed_topic": "/temporal_confirmation/confirmed",
            "temporal_events_topic": "/temporal_confirmation/results",
            "camera_info_topic": "/camera/camera/color/camera_info",
            "filter_status_topic": "/candidate_filter/status",
            "embedding_status_topic": "/embedding_retrieval/status",
            "temporal_status_topic": "/temporal_confirmation/status",
            "point_camera_topic": "/object_finder/point_camera",
            "temporal_reset_service": "/temporal_confirmation/reset",
            "candidate_reload_service": "/candidate_filter/reload_profile",
            "embedding_reload_service": "/embedding_retrieval/reload_banks",
            "embedding_rebuild_service": "/embedding_retrieval/rebuild_banks",
            "default_timeout_sec": 60.0,
            "default_continuous": True,
            "default_min_score": 0.0,
            "minimum_depth_m": 0.08,
            "maximum_depth_m": 2.0,
            "result_publish_hz": 5.0,
            "health_timeout_sec": 7.0,
            "status_period_sec": 1.0,
            "target_repeat_count": 4,
            "target_repeat_period_sec": 0.5,
            "default_camera_frame": "camera_color_optical_frame",
            "positive_root_template": "~/MacRobot/data/curated/objects/{target}",
            "require_positive_bank_files": True,
            "minimum_positive_images": 1,
            "reset_temporal_on_goal": True,
            "reload_candidate_on_goal": False,
            "reload_embedding_on_goal": False,
            "timeout_after_first_found": False,
            "timer_hz": 10.0,
        }
        for name, value in defaults.items():
            self.declare_parameter(name, value)

    def _now(self) -> float:
        return time.monotonic()

    def _publish_json(self, publisher, payload: dict[str, Any]) -> None:
        msg = String()
        msg.data = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        publisher.publish(msg)

    def _publish_result(self, payload: dict[str, Any]) -> None:
        self._publish_json(self.result_pub, payload)

    def _profile_image_count(self, target: str) -> int:
        template = str(self.get_parameter("positive_root_template").value)
        directory = Path(template.format(target=target)).expanduser()
        if not directory.is_dir():
            return 0
        return sum(
            1
            for path in directory.rglob("*")
            if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
        )

    def _goal_callback(self, msg: String) -> None:
        try:
            goal = parse_goal_text(
                msg.data,
                default_timeout_sec=float(
                    self.get_parameter("default_timeout_sec").value
                ),
                default_continuous=bool(
                    self.get_parameter("default_continuous").value
                ),
                default_min_score=float(
                    self.get_parameter("default_min_score").value
                ),
            )
        except Exception as exc:
            self._publish_result(
                not_found_payload(goal=None, reason=str(exc), event="invalid_goal")
            )
            return

        image_count = self._profile_image_count(goal.object_name)
        minimum_images = int(self.get_parameter("minimum_positive_images").value)
        if bool(self.get_parameter("require_positive_bank_files").value) and image_count < minimum_images:
            self._publish_result(
                not_found_payload(
                    goal=goal,
                    reason="positive_bank_unavailable",
                    event="finder_configuration_error",
                    details={"positive_image_count": image_count},
                )
            )
            return

        self.session.start(goal, self._now())
        self.target_repeat_remaining = max(
            1, int(self.get_parameter("target_repeat_count").value)
        )
        self.last_target_publish = 0.0
        self._publish_targets(force=True)

        if bool(self.get_parameter("reset_temporal_on_goal").value):
            self._call_trigger(self.temporal_reset_client, "temporal_reset")
        if bool(self.get_parameter("reload_candidate_on_goal").value):
            self._call_trigger(self.candidate_reload_client, "candidate_reload")
        if goal.rebuild_banks:
            self._call_trigger(self.embedding_rebuild_client, "embedding_rebuild")
        elif bool(self.get_parameter("reload_embedding_on_goal").value):
            self._call_trigger(self.embedding_reload_client, "embedding_reload")

        self._publish_status("search_started", positive_image_count=image_count)

    def _cancel_callback(self, msg: String) -> None:
        reason = msg.data.strip() or "user_cancel"
        goal = self.session.goal
        if goal is None:
            self._publish_status("cancel_ignored", reason="no_active_goal")
            return
        self.session.cancel()
        self.target_repeat_remaining = 0
        self._clear_active_target()
        self._call_trigger(self.temporal_reset_client, "temporal_reset")
        self._publish_result(
            not_found_payload(
                goal=goal, reason=reason, event="search_cancelled"
            )
        )
        self._publish_status("search_cancelled", reason=reason)

    def _publish_targets(self, *, force: bool = False) -> None:
        goal = self.session.goal
        if goal is None:
            return
        now = self._now()
        period = max(float(self.get_parameter("target_repeat_period_sec").value), 0.1)
        if not force and now - self.last_target_publish < period:
            return
        target = String()
        target.data = goal.object_name
        self.active_target_pub.publish(target)
        self.candidate_target_pub.publish(target)
        self.embedding_target_pub.publish(target)
        self.last_target_publish = now
        if self.target_repeat_remaining > 0:
            self.target_repeat_remaining -= 1

    def _clear_active_target(self) -> None:
        msg = String()
        msg.data = ""
        self.active_target_pub.publish(msg)

    def _call_trigger(self, client, label: str) -> None:
        if not client.service_is_ready():
            self.get_logger().warning(f"Service not ready: {label}")
            return
        future = client.call_async(Trigger.Request())
        future.add_done_callback(
            lambda done, name=label: self._trigger_done(name, done)
        )

    def _trigger_done(self, label: str, future) -> None:
        try:
            response = future.result()
        except Exception as exc:
            self.get_logger().warning(f"{label} failed: {exc}")
            return
        if not bool(response.success):
            self.get_logger().warning(f"{label} rejected: {response.message}")

    def _camera_info_callback(self, msg: CameraInfo) -> None:
        if len(msg.k) >= 9 and msg.k[0] > 0.0 and msg.k[4] > 0.0:
            self.camera_info = msg
            self.last_camera_info = self._now()

    def _component_status_callback(self, source: str, msg: String) -> None:
        now = self._now()
        try:
            payload = json.loads(msg.data)
            if not isinstance(payload, dict):
                payload = {"raw": msg.data}
        except Exception:
            payload = {"raw": msg.data}
        self.status_payloads[source] = payload
        if source == "filter":
            self.last_filter_status = now
        elif source == "embedding":
            self.last_embedding_status = now
        elif source == "temporal":
            self.last_temporal_status = now

    def _confirmed_callback(self, msg: TemporalConfirmationResult) -> None:
        goal = self.session.goal
        if goal is None or self.session.state not in {"SEARCHING", "TRACKING", "FOUND"}:
            return
        if not temporal_message_is_usable(
            msg,
            goal,
            minimum_depth_m=float(self.get_parameter("minimum_depth_m").value),
            maximum_depth_m=float(self.get_parameter("maximum_depth_m").value),
        ):
            return

        now = self._now()
        rate = max(float(self.get_parameter("result_publish_hz").value), 0.1)
        if goal.continuous and now - self.last_found_publish < 1.0 / rate:
            return
        if not goal.continuous and self.session.found_count > 0:
            return

        payload = temporal_to_result_payload(
            msg,
            goal,
            default_frame_id=str(self.get_parameter("default_camera_frame").value),
        )
        self._publish_result(payload)
        self._publish_camera_point(payload)
        self.session.accept_found(int(payload.get("track_id", 0)), now)
        self.last_found_publish = now
        if not goal.continuous:
            self.target_repeat_remaining = 0
            self._clear_active_target()
        self._publish_status("object_found", track_id=payload.get("track_id"))

    def _temporal_event_callback(self, msg: TemporalConfirmationResult) -> None:
        goal = self.session.goal
        if goal is None or not goal.continuous:
            return
        if str(msg.target_object).strip().casefold() != goal.object_name.casefold():
            return
        event = str(msg.event).strip().lower()
        if event not in {"deconfirmed", "expired"}:
            return
        if self.session.track_id is not None and int(msg.track_id) != self.session.track_id:
            return
        self.session.mark_lost()
        if not goal.continuous:
            self._clear_active_target()
        self._publish_result(
            not_found_payload(
                goal=goal,
                reason=event,
                event="object_lost",
                details={"track_id": int(msg.track_id)},
            )
        )
        self._publish_status("object_lost", reason=event)

    def _publish_camera_point(self, payload: dict[str, Any]) -> None:
        info = self.camera_info
        center = payload.get("center_px")
        if info is None or not isinstance(center, dict):
            return
        try:
            u = float(center["x"])
            v = float(center["y"])
            depth = float(payload["depth_m"])
            fx = float(info.k[0])
            fy = float(info.k[4])
            cx = float(info.k[2])
            cy = float(info.k[5])
        except (KeyError, TypeError, ValueError, IndexError):
            return
        if not all(math.isfinite(value) for value in (u, v, depth, fx, fy, cx, cy)):
            return
        if fx <= 0.0 or fy <= 0.0:
            return
        point = PointStamped()
        point.header.stamp = self.get_clock().now().to_msg()
        point.header.frame_id = str(payload.get("frame_id", "")).strip() or info.header.frame_id
        point.point.x = (u - cx) * depth / fx
        point.point.y = (v - cy) * depth / fy
        point.point.z = depth
        self.point_camera_pub.publish(point)

    def _age(self, value: float, now: float) -> Optional[float]:
        return None if value <= 0.0 else max(0.0, now - value)

    def _health_snapshot(self) -> dict[str, Any]:
        now = self._now()
        timeout = max(float(self.get_parameter("health_timeout_sec").value), 0.1)
        ages = {
            "camera_info": self._age(self.last_camera_info, now),
            "filter_status": self._age(self.last_filter_status, now),
            "embedding_status": self._age(self.last_embedding_status, now),
            "temporal_status": self._age(self.last_temporal_status, now),
        }
        checks = {
            key: age is not None and age <= timeout for key, age in ages.items()
        }
        temporal_payload = self.status_payloads.get("temporal", {})
        received_heartbeats = int(temporal_payload.get("received_heartbeats", 0) or 0)
        checks["candidate_stream_seen_by_temporal"] = received_heartbeats > 0
        return {
            "ready": all(checks.values()),
            "checks": checks,
            "ages_sec": ages,
            "received_candidate_heartbeats": received_heartbeats,
            "components": self.status_payloads,
        }

    def _publish_status(self, event: str, **details: Any) -> None:
        payload = {
            "ok": True,
            "event": event,
            **self.session.snapshot(),
            "health": self._health_snapshot(),
            **details,
        }
        self._publish_json(self.status_pub, payload)

    def _timer_callback(self) -> None:
        if self.target_repeat_remaining > 0:
            self._publish_targets()
        timeout_after_found = bool(
            self.get_parameter("timeout_after_first_found").value
        )
        if self.session.timeout_due(self._now()) and (
            self.session.found_count == 0 or timeout_after_found
        ):
            goal = self.session.goal
            self.session.mark_timeout()
            self.target_repeat_remaining = 0
            self._clear_active_target()
            self._call_trigger(self.temporal_reset_client, "temporal_reset")
            self._publish_result(
                not_found_payload(goal=goal, reason="timeout")
            )
            self._publish_status("search_timeout")

        period = max(float(self.get_parameter("status_period_sec").value), 0.2)
        now = self._now()
        last = getattr(self, "_last_status_time", 0.0)
        if now - last >= period:
            self._last_status_time = now
            self._publish_status("status")


def main(args=None) -> None:
    rclpy.init(args=args)
    node = ObjectFinderNode()
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
