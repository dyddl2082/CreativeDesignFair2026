from __future__ import annotations

import json
import math
import time
from typing import Dict, Optional, Tuple

import rclpy
from geometry_msgs.msg import PointStamped
from rclpy.duration import Duration
from rclpy.node import Node
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

    # v' = v + 2*w*(q_xyz x v) + 2*(q_xyz x (q_xyz x v))
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


class DetectionLocalizerNode(Node):
    """Convert the existing object_finder JSON result into a base_link point.

    Expected legacy detection fields include ``center_px`` and ``depth_m``.
    A future detector may bypass pixel projection by including ``point_base``.
    """

    def __init__(self) -> None:
        super().__init__("macrobot_detection_localizer")

        self.declare_parameter("finder_result_topic", "/object_finder/result")
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

        self.create_subscription(
            String,
            str(self.get_parameter("finder_result_topic").value),
            self._result_callback,
            20,
        )
        self.create_subscription(
            CameraInfo,
            str(self.get_parameter("camera_info_topic").value),
            self._camera_info_callback,
            10,
        )
        self.create_subscription(
            String,
            str(self.get_parameter("active_target_topic").value),
            self._target_callback,
            10,
        )

        self.get_logger().info(
            "Detection localizer ready: object_finder result -> base_link PointStamped"
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
            "stamp_sec": time.time(),
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

    def _result_callback(self, msg: String) -> None:
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
        if not object_name:
            return
        if self.active_target and object_name.casefold() != self.active_target.casefold():
            return
        score = float(payload.get("score", 0.0))
        if not math.isfinite(score) or score < self.minimum_score:
            return

        direct_point = parse_point_mapping(payload.get("point_base"))
        if direct_point is not None:
            self._publish_localized(
                object_name=object_name,
                score=score,
                point_base=direct_point,
                source="finder_point_base",
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
        if not all(math.isfinite(item) for item in (u, v, depth_m)):
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

        # ROS optical frame convention: X right, Y down, Z forward.
        point_optical: Vector3 = (
            (u - cx) * depth_m / fx,
            (v - cy) * depth_m / fy,
            depth_m,
        )
        source_frame = self.optical_frame_override or self.camera_info.header.frame_id
        if not source_frame:
            self._publish_status(False, "camera_info_frame_empty")
            return
        try:
            point_base = self._transform_to_base(point_optical, source_frame)
        except TransformException as exc:
            self._publish_status(
                False,
                "tf_unavailable",
                source_frame=source_frame,
                target_frame=self.base_frame,
                error=str(exc),
            )
            return

        self._publish_localized(
            object_name=object_name,
            score=score,
            point_base=point_base,
            source="pixel_depth_projection",
            details={
                "pixel": {"u": u, "v": v},
                "depth_m": depth_m,
                "optical_frame": source_frame,
                "point_optical": {
                    "x": point_optical[0],
                    "y": point_optical[1],
                    "z": point_optical[2],
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
