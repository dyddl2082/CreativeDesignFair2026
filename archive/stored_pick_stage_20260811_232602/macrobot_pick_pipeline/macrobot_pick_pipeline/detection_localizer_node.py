from __future__ import annotations

import json
import math
import time
from typing import Dict, Optional, Tuple

import rclpy
from geometry_msgs.msg import PointStamped
from macrobot_interfaces.msg import TemporalConfirmationResult
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from rclpy.time import Time
from sensor_msgs.msg import CameraInfo
from std_msgs.msg import String
from tf2_ros import Buffer, TransformException, TransformListener


Vector3 = Tuple[float, float, float]


def rotate_vector_by_quaternion(vector: Vector3, quaternion) -> Vector3:
    """Rotate a vector by geometry_msgs/Quaternion without external helpers."""
    vx, vy, vz = vector
    qx = float(quaternion.x)
    qy = float(quaternion.y)
    qz = float(quaternion.z)
    qw = float(quaternion.w)

    tx = 2.0 * (qy * vz - qz * vy)
    ty = 2.0 * (qz * vx - qx * vz)
    tz = 2.0 * (qx * vy - qy * vx)
    return (
        vx + qw * tx + (qy * tz - qz * ty),
        vy + qw * ty + (qz * tx - qx * tz),
        vz + qw * tz + (qx * ty - qy * tx),
    )


def parse_point_mapping(value) -> Optional[Vector3]:
    if not isinstance(value, dict):
        return None
    try:
        point = (float(value["x"]), float(value["y"]), float(value["z"]))
    except (KeyError, TypeError, ValueError):
        return None
    return point if all(math.isfinite(item) for item in point) else None


def stamp_to_sec(stamp) -> float:
    return float(stamp.sec) + float(stamp.nanosec) * 1e-9


class DetectionLocalizerNode(Node):
    """Convert object-finder outputs into a ``base_link`` 3D point.

    Two input contracts are supported:

    * ``legacy``: JSON on ``/object_finder/result``.  This remains the default
      for compatibility with the existing perception pipeline.
    * ``typed``: ``macrobot_interfaces/TemporalConfirmationResult`` on
      ``/temporal_confirmation/confirmed``.

    The detector may bypass pixel projection by including ``point_base`` in the
    JSON result.  Otherwise ``center_px`` + ``depth_m`` are projected with the
    color ``CameraInfo`` and transformed through TF.
    """

    def __init__(self) -> None:
        super().__init__("macrobot_detection_localizer")

        self.declare_parameter("input_mode", "legacy")  # legacy, typed, both
        self.declare_parameter("finder_result_topic", "/object_finder/result")
        self.declare_parameter(
            "typed_confirmation_topic", "/temporal_confirmation/confirmed"
        )
        self.declare_parameter("camera_info_topic", "/camera/camera/color/camera_info")
        self.declare_parameter("active_target_topic", "/macrobot/pick/active_target")
        self.declare_parameter(
            "localized_detection_topic", "/macrobot/perception/localized_detection"
        )
        self.declare_parameter("point_topic", "/macrobot/perception/object_point")
        self.declare_parameter("status_topic", "/macrobot/perception/localizer_status")
        self.declare_parameter("base_frame", "base_link")
        self.declare_parameter("optical_frame_override", "")
        self.declare_parameter("minimum_score", 0.0)
        self.declare_parameter("minimum_depth_m", 0.08)
        self.declare_parameter("maximum_depth_m", 2.0)
        self.declare_parameter("tf_timeout_sec", 0.20)

        self.input_mode = str(self.get_parameter("input_mode").value).strip().lower()
        if self.input_mode not in {"legacy", "typed", "both"}:
            raise ValueError("input_mode must be legacy, typed or both")
        self.base_frame = str(self.get_parameter("base_frame").value)
        self.optical_frame_override = str(
            self.get_parameter("optical_frame_override").value
        ).strip()
        self.minimum_score = float(self.get_parameter("minimum_score").value)
        self.minimum_depth = float(self.get_parameter("minimum_depth_m").value)
        self.maximum_depth = float(self.get_parameter("maximum_depth_m").value)
        self.tf_timeout = float(self.get_parameter("tf_timeout_sec").value)

        self.active_target = ""
        self.camera_info: Optional[CameraInfo] = None
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        self.detection_pub = self.create_publisher(
            String,
            str(self.get_parameter("localized_detection_topic").value),
            20,
        )
        self.point_pub = self.create_publisher(
            PointStamped,
            str(self.get_parameter("point_topic").value),
            20,
        )
        self.status_pub = self.create_publisher(
            String,
            str(self.get_parameter("status_topic").value),
            20,
        )

        if self.input_mode in {"legacy", "both"}:
            self.create_subscription(
                String,
                str(self.get_parameter("finder_result_topic").value),
                self._legacy_result_callback,
                20,
            )
        if self.input_mode in {"typed", "both"}:
            self.create_subscription(
                TemporalConfirmationResult,
                str(self.get_parameter("typed_confirmation_topic").value),
                self._typed_result_callback,
                20,
            )
        self.create_subscription(
            CameraInfo,
            str(self.get_parameter("camera_info_topic").value),
            self._camera_info_callback,
            qos_profile_sensor_data,
        )
        self.create_subscription(
            String,
            str(self.get_parameter("active_target_topic").value),
            self._target_callback,
            10,
        )

        self.get_logger().info(
            "Detection localizer ready: "
            f"input_mode={self.input_mode}, detection -> base_link PointStamped"
        )

    def _target_callback(self, msg: String) -> None:
        self.active_target = msg.data.strip()

    def _camera_info_callback(self, msg: CameraInfo) -> None:
        if msg.k[0] > 0.0 and msg.k[4] > 0.0:
            self.camera_info = msg

    def _publish_status(self, ok: bool, event: str, **details: object) -> None:
        message = String()
        message.data = json.dumps(
            {"ok": ok, "event": event, **details},
            ensure_ascii=False,
        )
        self.status_pub.publish(message)
        if not ok:
            self.get_logger().warning(message.data)

    def _publish_localized(
        self,
        *,
        object_name: str,
        score: float,
        point_base: Vector3,
        source: str,
        measurement_stamp_sec: Optional[float] = None,
        details: Optional[Dict[str, object]] = None,
    ) -> None:
        now = self.get_clock().now()
        point_msg = PointStamped()
        point_msg.header.stamp = now.to_msg()
        point_msg.header.frame_id = self.base_frame
        point_msg.point.x, point_msg.point.y, point_msg.point.z = point_base
        self.point_pub.publish(point_msg)

        payload: Dict[str, object] = {
            "ok": True,
            "event": "localized_object",
            "object_name": object_name,
            "score": score,
            "frame_id": self.base_frame,
            "point_base": {
                "x": point_base[0],
                "y": point_base[1],
                "z": point_base[2],
            },
            "stamp_sec": (
                float(measurement_stamp_sec)
                if measurement_stamp_sec is not None
                else time.time()
            ),
            "published_at_sec": time.time(),
            "source": source,
        }
        if details:
            payload.update(details)
        message = String()
        message.data = json.dumps(payload, ensure_ascii=False)
        self.detection_pub.publish(message)

    def _transform_to_base(self, point: Vector3, source_frame: str) -> Vector3:
        transform = self.tf_buffer.lookup_transform(
            self.base_frame,
            source_frame,
            Time(),
            timeout=Duration(seconds=self.tf_timeout),
        )
        rotated = rotate_vector_by_quaternion(
            point,
            transform.transform.rotation,
        )
        translation = transform.transform.translation
        return (
            rotated[0] + float(translation.x),
            rotated[1] + float(translation.y),
            rotated[2] + float(translation.z),
        )

    def _target_matches(self, object_name: str) -> bool:
        return not self.active_target or object_name.casefold() == self.active_target.casefold()

    def _localize_pixel_depth(
        self,
        *,
        object_name: str,
        score: float,
        u: float,
        v: float,
        depth_m: float,
        source_frame: str,
        source: str,
        measurement_stamp_sec: Optional[float],
        details: Optional[Dict[str, object]] = None,
    ) -> None:
        if not all(math.isfinite(item) for item in (u, v, depth_m, score)):
            return
        if score < self.minimum_score:
            return
        if not (self.minimum_depth <= depth_m <= self.maximum_depth):
            return
        if self.camera_info is None:
            self._publish_status(False, "waiting_for_camera_info", object_name=object_name)
            return

        fx = float(self.camera_info.k[0])
        fy = float(self.camera_info.k[4])
        cx = float(self.camera_info.k[2])
        cy = float(self.camera_info.k[5])
        if fx <= 0.0 or fy <= 0.0:
            self._publish_status(False, "invalid_camera_intrinsics")
            return

        point_optical: Vector3 = (
            (u - cx) * depth_m / fx,
            (v - cy) * depth_m / fy,
            depth_m,
        )
        frame = self.optical_frame_override or source_frame or self.camera_info.header.frame_id
        if not frame:
            self._publish_status(False, "camera_frame_empty")
            return
        try:
            point_base = self._transform_to_base(point_optical, frame)
        except TransformException as exc:
            self._publish_status(
                False,
                "tf_unavailable",
                source_frame=frame,
                target_frame=self.base_frame,
                error=str(exc),
            )
            return

        output_details: Dict[str, object] = {
            "pixel": {"u": u, "v": v},
            "depth_m": depth_m,
            "optical_frame": frame,
            "point_optical": {
                "x": point_optical[0],
                "y": point_optical[1],
                "z": point_optical[2],
            },
        }
        if details:
            output_details.update(details)
        self._publish_localized(
            object_name=object_name,
            score=score,
            point_base=point_base,
            source=source,
            measurement_stamp_sec=measurement_stamp_sec,
            details=output_details,
        )

    def _legacy_result_callback(self, msg: String) -> None:
        try:
            payload = json.loads(msg.data)
        except Exception:
            return
        if not isinstance(payload, dict):
            return
        if payload.get("found") is False:
            return
        if payload.get("event") not in (None, "object_found", "detection"):
            return

        object_name = str(payload.get("object_name", "")).strip()
        if not object_name or not self._target_matches(object_name):
            return
        score = float(payload.get("score", 0.0))
        if not math.isfinite(score) or score < self.minimum_score:
            return
        measurement_stamp = payload.get("stamp_sec")
        try:
            measurement_stamp_sec = float(measurement_stamp)
        except (TypeError, ValueError):
            measurement_stamp_sec = time.time()

        direct_point = parse_point_mapping(payload.get("point_base"))
        if direct_point is not None:
            self._publish_localized(
                object_name=object_name,
                score=score,
                point_base=direct_point,
                source="finder_point_base",
                measurement_stamp_sec=measurement_stamp_sec,
                details={"finder_payload_frame": payload.get("frame_id", self.base_frame)},
            )
            return

        center = payload.get("center_px")
        if not isinstance(center, dict):
            return
        try:
            u = float(center["x"])
            v = float(center["y"])
            depth_m = float(payload["depth_m"])
        except (KeyError, TypeError, ValueError):
            return
        source_frame = str(payload.get("frame_id", "")).strip()
        self._localize_pixel_depth(
            object_name=object_name,
            score=score,
            u=u,
            v=v,
            depth_m=depth_m,
            source_frame=source_frame,
            source="legacy_pixel_depth_projection",
            measurement_stamp_sec=measurement_stamp_sec,
            details={"legacy_event": payload.get("event")},
        )

    def _typed_result_callback(self, msg: TemporalConfirmationResult) -> None:
        if not bool(msg.confirmed):
            return
        if msg.state and msg.state not in {"confirmed", "tentative"}:
            return
        if msg.event and msg.event not in {"confirmed", "update"}:
            return
        object_name = str(msg.target_object).strip()
        if not object_name or not self._target_matches(object_name):
            return
        self._localize_pixel_depth(
            object_name=object_name,
            score=float(msg.temporal_score),
            u=float(msg.center_x),
            v=float(msg.center_y),
            depth_m=float(msg.depth_m),
            source_frame=str(msg.header.frame_id),
            source="typed_temporal_confirmation",
            measurement_stamp_sec=stamp_to_sec(msg.header.stamp),
            details={
                "track_id": int(msg.track_id),
                "temporal_score": float(msg.temporal_score),
                "stability_score": float(msg.stability_score),
                "horizontal_error_norm": float(msg.horizontal_error_norm),
                "suggested_turn": str(msg.suggested_turn),
                "roi": {
                    "x_offset": int(msg.roi.x_offset),
                    "y_offset": int(msg.roi.y_offset),
                    "width": int(msg.roi.width),
                    "height": int(msg.roi.height),
                },
            },
        )


def main(args=None) -> None:
    rclpy.init(args=args)
    node = DetectionLocalizerNode()
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
