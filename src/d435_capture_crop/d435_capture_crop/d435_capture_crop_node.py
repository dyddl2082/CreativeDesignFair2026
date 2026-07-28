"""ROS 2 node for D435 capture, browser crop review, and dataset saving."""

from __future__ import annotations

import json
import queue
import threading
import time
import uuid
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import rclpy
from ament_index_python.packages import get_package_share_directory
from cv_bridge import CvBridge, CvBridgeError
from rclpy.node import Node
from rclpy.qos import (
    DurabilityPolicy,
    HistoryPolicy,
    QoSProfile,
    ReliabilityPolicy,
)
from sensor_msgs.msg import CameraInfo, Image
from std_msgs.msg import String

from .capture_core import (
    DepthStats,
    Roi,
    atomic_write_bytes,
    atomic_write_json,
    compute_depth_stats,
    crop_array,
    depth_to_meters,
    encode_image,
    ensure_under_root,
    map_roi_between_sizes,
    normalize_roi,
    sanitize_component,
)
from .web_server import ApiError, guess_access_url, start_http_server


@dataclass(frozen=True)
class BufferedDepth:
    stamp_ns: int
    message: Image


@dataclass(frozen=True)
class CaptureSession:
    session_id: str
    object_name: str
    view_label: str
    created_monotonic: float
    created_local_iso: str
    filename_timestamp: str
    color_bgr: np.ndarray
    color_jpeg: bytes
    color_stamp_ns: int
    color_frame_id: str
    color_encoding: str
    depth_m: np.ndarray | None
    depth_raw_for_png: np.ndarray | None
    depth_stamp_ns: int | None
    depth_frame_id: str
    depth_encoding: str
    depth_sync_offset_sec: float | None
    camera_info: dict[str, Any] | None


class D435CaptureCropNode(Node):
    """Subscribe to D435 topics and expose a capture-before-save browser workflow."""

    def __init__(self) -> None:
        super().__init__("d435_capture_crop")
        self._declare_parameters()

        self._bridge = CvBridge()
        self._frame_lock = threading.RLock()
        self._session_lock = threading.RLock()
        self._preview_condition = threading.Condition()
        self._shutdown_event = threading.Event()
        self._event_queue: queue.SimpleQueue[dict[str, Any]] = queue.SimpleQueue()

        self._latest_color_msg: Image | None = None
        self._latest_color_received_monotonic = 0.0
        self._depth_buffer: deque[BufferedDepth] = deque(
            maxlen=max(1, int(self.get_parameter("depth_buffer_size").value))
        )
        self._latest_camera_info: CameraInfo | None = None
        self._active_session: CaptureSession | None = None
        self._saved_count = 0
        self._last_error = ""
        self._preview_jpeg: bytes | None = None
        self._preview_sequence = 0
        self._preview_stamp_ns = 0
        self._preview_dimensions = (0, 0)

        sensor_qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
        )
        command_qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE,
        )
        result_qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE,
        )

        color_topic = str(self.get_parameter("color_topic").value)
        depth_topic = str(self.get_parameter("depth_topic").value)
        camera_info_topic = str(self.get_parameter("camera_info_topic").value)
        command_topic = str(self.get_parameter("capture_command_topic").value)

        self._color_subscription = self.create_subscription(
            Image,
            color_topic,
            self._on_color,
            sensor_qos,
        )
        self._depth_subscription = self.create_subscription(
            Image,
            depth_topic,
            self._on_depth,
            sensor_qos,
        )
        self._camera_info_subscription = self.create_subscription(
            CameraInfo,
            camera_info_topic,
            self._on_camera_info,
            sensor_qos,
        )
        self._capture_command_subscription = self.create_subscription(
            String,
            command_topic,
            self._on_capture_command,
            command_qos,
        )

        self._status_publisher = self.create_publisher(
            String,
            str(self.get_parameter("status_topic").value),
            result_qos,
        )
        self._result_publisher = self.create_publisher(
            String,
            str(self.get_parameter("result_topic").value),
            result_qos,
        )

        self._status_timer = self.create_timer(1.0, self._on_status_timer)

        package_share = Path(get_package_share_directory("d435_capture_crop"))
        static_root = package_share / "web"
        host = str(self.get_parameter("host").value)
        port = int(self.get_parameter("port").value)
        self._http_server, self._http_thread = start_http_server(
            backend=self,
            host=host,
            port=port,
            static_root=static_root,
        )

        self._preview_thread = threading.Thread(
            target=self._preview_worker,
            name="d435-preview-worker",
            daemon=True,
        )
        self._preview_thread.start()

        self.get_logger().info(
            "D435 capture/crop node ready: "
            f"color='{color_topic}', depth='{depth_topic}', "
            f"web='{guess_access_url(host, port)}'"
        )
        self.get_logger().info(
            "Workflow: open the web UI, capture a frame, drag a crop, inspect depth, then save."
        )

    def _declare_parameters(self) -> None:
        defaults: dict[str, Any] = {
            "color_topic": "/camera/camera/color/image_raw",
            "depth_topic": "/camera/camera/aligned_depth_to_color/image_raw",
            "camera_info_topic": "/camera/camera/color/camera_info",
            "capture_command_topic": "/capture_object_name",
            "status_topic": "/object_camera_capture/status",
            "result_topic": "/object_camera_capture/result",
            "base_dir": "~/MacRobot/data",
            "original_subdir": "objects",
            "curated_subdir": "curated/objects",
            "depth_subdir": "curated/depth",
            "metadata_subdir": "curated/metadata",
            "host": "0.0.0.0",
            "port": 8090,
            "default_object_name": "Buds3",
            "preview_hz": 5.0,
            "preview_max_width": 640,
            "preview_jpeg_quality": 70,
            "capture_jpeg_quality": 90,
            "save_jpeg_quality": 95,
            "depth_buffer_size": 30,
            "depth_sync_tolerance_sec": 0.120,
            "depth_scale_m": 0.001,
            "depth_min_m": 0.05,
            "depth_max_m": 10.0,
            "session_timeout_sec": 600.0,
            "min_crop_width_px": 24,
            "min_crop_height_px": 24,
            "save_original_default": True,
            "save_depth_default": True,
            "clear_session_after_save": True,
        }
        for name, value in defaults.items():
            self.declare_parameter(name, value)

    @staticmethod
    def _stamp_to_ns(message: Image | CameraInfo) -> int:
        return int(message.header.stamp.sec) * 1_000_000_000 + int(
            message.header.stamp.nanosec
        )

    def _on_color(self, message: Image) -> None:
        with self._frame_lock:
            self._latest_color_msg = message
            self._latest_color_received_monotonic = time.monotonic()

    def _on_depth(self, message: Image) -> None:
        buffered = BufferedDepth(stamp_ns=self._stamp_to_ns(message), message=message)
        with self._frame_lock:
            self._depth_buffer.append(buffered)

    def _on_camera_info(self, message: CameraInfo) -> None:
        with self._frame_lock:
            self._latest_camera_info = message

    def _on_capture_command(self, message: String) -> None:
        text = str(message.data or "").strip()
        object_name = text
        view_label = ""
        if text.startswith("{"):
            try:
                payload = json.loads(text)
                object_name = str(payload.get("object_name", ""))
                view_label = str(payload.get("view_label", ""))
            except json.JSONDecodeError as exc:
                self.get_logger().warning(f"Ignoring invalid capture JSON: {exc}")
                return
        try:
            result = self.api_capture(
                {"object_name": object_name, "view_label": view_label, "source": "ros_topic"}
            )
            self.get_logger().info(
                "Frame frozen from capture topic. Complete cropping in the browser: "
                f"session={result['session_id']}"
            )
        except ApiError as exc:
            self.get_logger().warning(f"Capture command failed: {exc.message}")

    def _preview_worker(self) -> None:
        error_last_logged = 0.0
        while not self._shutdown_event.is_set():
            started = time.monotonic()
            preview_hz = max(0.2, float(self.get_parameter("preview_hz").value))
            interval = 1.0 / preview_hz
            with self._frame_lock:
                message = self._latest_color_msg
            if message is not None:
                try:
                    frame = self._bridge.imgmsg_to_cv2(message, desired_encoding="bgr8")
                    frame = np.asarray(frame)
                    max_width = max(64, int(self.get_parameter("preview_max_width").value))
                    if frame.shape[1] > max_width:
                        scale = max_width / frame.shape[1]
                        frame = cv2.resize(
                            frame,
                            (max_width, max(1, int(round(frame.shape[0] * scale)))),
                            interpolation=cv2.INTER_AREA,
                        )
                    preview = frame.copy()
                    cv2.putText(
                        preview,
                        "D435 LIVE",
                        (12, 28),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 0),
                        2,
                        cv2.LINE_AA,
                    )
                    quality = int(np.clip(self.get_parameter("preview_jpeg_quality").value, 25, 95))
                    jpeg = encode_image(preview, ".jpg", quality=quality)
                    with self._preview_condition:
                        self._preview_jpeg = jpeg
                        self._preview_sequence += 1
                        self._preview_stamp_ns = self._stamp_to_ns(message)
                        self._preview_dimensions = (int(frame.shape[1]), int(frame.shape[0]))
                        self._preview_condition.notify_all()
                except (CvBridgeError, ValueError, RuntimeError, cv2.error) as exc:
                    now = time.monotonic()
                    self._last_error = f"Preview conversion failed: {exc}"
                    if now - error_last_logged > 5.0:
                        self.get_logger().warning(self._last_error)
                        error_last_logged = now
            elapsed = time.monotonic() - started
            self._shutdown_event.wait(max(0.005, interval - elapsed))

    def _on_status_timer(self) -> None:
        self._expire_session_if_needed()
        while True:
            try:
                event = self._event_queue.get_nowait()
            except queue.Empty:
                break
            message = String()
            message.data = json.dumps(event, ensure_ascii=False)
            self._result_publisher.publish(message)

        status = String()
        status.data = json.dumps(self.api_status(), ensure_ascii=False)
        self._status_publisher.publish(status)

    def _expire_session_if_needed(self) -> None:
        timeout = max(0.0, float(self.get_parameter("session_timeout_sec").value))
        if timeout <= 0:
            return
        with self._session_lock:
            session = self._active_session
            if session and time.monotonic() - session.created_monotonic > timeout:
                self._active_session = None
                self.get_logger().info(f"Expired capture session {session.session_id}")

    def _camera_info_to_dict(self, message: CameraInfo | None) -> dict[str, Any] | None:
        if message is None:
            return None
        return {
            "header": {
                "stamp_ns": self._stamp_to_ns(message),
                "frame_id": message.header.frame_id,
            },
            "height": int(message.height),
            "width": int(message.width),
            "distortion_model": message.distortion_model,
            "d": [float(value) for value in message.d],
            "k": [float(value) for value in message.k],
            "r": [float(value) for value in message.r],
            "p": [float(value) for value in message.p],
            "binning_x": int(message.binning_x),
            "binning_y": int(message.binning_y),
            "roi": {
                "x_offset": int(message.roi.x_offset),
                "y_offset": int(message.roi.y_offset),
                "height": int(message.roi.height),
                "width": int(message.roi.width),
                "do_rectify": bool(message.roi.do_rectify),
            },
        }

    def _find_nearest_depth(self, color_stamp_ns: int) -> BufferedDepth | None:
        with self._frame_lock:
            items = list(self._depth_buffer)
        if not items:
            return None
        nearest = min(items, key=lambda item: abs(item.stamp_ns - color_stamp_ns))
        tolerance_ns = int(
            max(0.0, float(self.get_parameter("depth_sync_tolerance_sec").value))
            * 1_000_000_000
        )
        if tolerance_ns > 0 and abs(nearest.stamp_ns - color_stamp_ns) > tolerance_ns:
            return None
        return nearest

    def _make_session(self, object_name: str, view_label: str) -> CaptureSession:
        with self._frame_lock:
            color_message = self._latest_color_msg
            camera_info = self._latest_camera_info
        if color_message is None:
            raise ApiError(503, "No D435 color frame has been received yet")

        try:
            color_bgr = self._bridge.imgmsg_to_cv2(color_message, desired_encoding="bgr8")
            color_bgr = np.asarray(color_bgr).copy()
        except (CvBridgeError, cv2.error) as exc:
            raise ApiError(500, "Failed to decode the D435 color frame", str(exc)) from exc
        if color_bgr.ndim != 3 or color_bgr.shape[2] != 3:
            raise ApiError(500, f"Unexpected color frame shape: {color_bgr.shape}")

        color_stamp_ns = self._stamp_to_ns(color_message)
        depth_item = self._find_nearest_depth(color_stamp_ns)
        depth_m: np.ndarray | None = None
        depth_raw_for_png: np.ndarray | None = None
        depth_stamp_ns: int | None = None
        depth_frame_id = ""
        depth_encoding = ""
        depth_sync_offset_sec: float | None = None

        if depth_item is not None:
            try:
                depth_raw = self._bridge.imgmsg_to_cv2(
                    depth_item.message,
                    desired_encoding="passthrough",
                )
                depth_raw = np.asarray(depth_raw).copy()
                depth_encoding = str(depth_item.message.encoding)
                depth_m = depth_to_meters(
                    depth_raw,
                    depth_encoding,
                    float(self.get_parameter("depth_scale_m").value),
                )
                # Persist depth crops in a stable, explicit millimeter unit even
                # when the incoming image uses a non-default integer scale or 32FC1.
                depth_raw_for_png = np.clip(
                    np.rint(depth_m * 1000.0), 0, 65535
                ).astype(np.uint16)
                depth_stamp_ns = depth_item.stamp_ns
                depth_frame_id = depth_item.message.header.frame_id
                depth_sync_offset_sec = (depth_item.stamp_ns - color_stamp_ns) / 1e9
            except (CvBridgeError, ValueError, cv2.error) as exc:
                self.get_logger().warning(f"Depth snapshot unavailable for this capture: {exc}")
                depth_m = None
                depth_raw_for_png = None
                depth_stamp_ns = None
                depth_frame_id = ""
                depth_encoding = ""
                depth_sync_offset_sec = None

        now = datetime.now().astimezone()
        session_id = uuid.uuid4().hex[:16]
        quality = int(np.clip(self.get_parameter("capture_jpeg_quality").value, 40, 100))
        color_jpeg = encode_image(color_bgr, ".jpg", quality=quality)
        return CaptureSession(
            session_id=session_id,
            object_name=sanitize_component(object_name, fallback="object"),
            view_label=sanitize_component(view_label, fallback="view"),
            created_monotonic=time.monotonic(),
            created_local_iso=now.isoformat(timespec="milliseconds"),
            filename_timestamp=now.strftime("%Y%m%d_%H%M%S_%f")[:-3],
            color_bgr=color_bgr,
            color_jpeg=color_jpeg,
            color_stamp_ns=color_stamp_ns,
            color_frame_id=color_message.header.frame_id,
            color_encoding=str(color_message.encoding),
            depth_m=depth_m,
            depth_raw_for_png=depth_raw_for_png,
            depth_stamp_ns=depth_stamp_ns,
            depth_frame_id=depth_frame_id,
            depth_encoding=depth_encoding,
            depth_sync_offset_sec=depth_sync_offset_sec,
            camera_info=self._camera_info_to_dict(camera_info),
        )

    def _get_session(self, session_id: str) -> CaptureSession:
        self._expire_session_if_needed()
        with self._session_lock:
            session = self._active_session
        if session is None:
            raise ApiError(404, "There is no active capture session")
        if session_id and session.session_id != session_id:
            raise ApiError(409, "The capture session is stale; capture the frame again")
        return session

    def _depth_roi_for_color_roi(self, session: CaptureSession, color_roi: Roi) -> Roi | None:
        if session.depth_m is None:
            return None
        color_height, color_width = session.color_bgr.shape[:2]
        depth_height, depth_width = session.depth_m.shape[:2]
        return map_roi_between_sizes(
            color_roi,
            color_width,
            color_height,
            depth_width,
            depth_height,
        )

    def _depth_stats_for_roi(self, session: CaptureSession, color_roi: Roi) -> DepthStats:
        depth_roi = self._depth_roi_for_color_roi(session, color_roi)
        if depth_roi is None:
            return DepthStats(available=False)
        return compute_depth_stats(
            session.depth_m,
            depth_roi,
            min_depth_m=float(self.get_parameter("depth_min_m").value),
            max_depth_m=float(self.get_parameter("depth_max_m").value),
        )

    # HTTP backend interface -------------------------------------------------

    def is_http_running(self) -> bool:
        return not self._shutdown_event.is_set()

    def wait_for_preview(self, last_sequence: int, timeout_sec: float) -> tuple[int, bytes | None]:
        with self._preview_condition:
            if self._preview_sequence == last_sequence and not self._shutdown_event.is_set():
                self._preview_condition.wait(timeout=max(0.05, timeout_sec))
            return self._preview_sequence, self._preview_jpeg

    def api_status(self) -> dict[str, Any]:
        with self._frame_lock:
            color_available = self._latest_color_msg is not None
            color_age = (
                time.monotonic() - self._latest_color_received_monotonic
                if color_available
                else None
            )
            depth_buffer_count = len(self._depth_buffer)
            camera_info_available = self._latest_camera_info is not None
        with self._session_lock:
            session = self._active_session
        return {
            "ok": True,
            "node": self.get_name(),
            "color_available": color_available,
            "color_age_sec": color_age,
            "depth_available": depth_buffer_count > 0,
            "depth_buffer_count": depth_buffer_count,
            "camera_info_available": camera_info_available,
            "preview_available": self._preview_jpeg is not None,
            "preview_width": self._preview_dimensions[0],
            "preview_height": self._preview_dimensions[1],
            "active_session": (
                {
                    "session_id": session.session_id,
                    "object_name": session.object_name,
                    "view_label": session.view_label,
                    "created_local_iso": session.created_local_iso,
                    "width": int(session.color_bgr.shape[1]),
                    "height": int(session.color_bgr.shape[0]),
                    "depth_available": session.depth_m is not None,
                    "depth_sync_offset_sec": session.depth_sync_offset_sec,
                }
                if session
                else None
            ),
            "default_object_name": str(self.get_parameter("default_object_name").value),
            "save_original_default": bool(self.get_parameter("save_original_default").value),
            "save_depth_default": bool(self.get_parameter("save_depth_default").value),
            "saved_count": self._saved_count,
            "last_error": self._last_error,
        }

    def api_capture(self, payload: dict[str, Any]) -> dict[str, Any]:
        object_name = str(
            payload.get("object_name")
            or self.get_parameter("default_object_name").value
            or "object"
        )
        view_label = str(payload.get("view_label") or "view")
        session = self._make_session(object_name, view_label)
        with self._session_lock:
            self._active_session = session
        full_roi = Roi(0, 0, session.color_bgr.shape[1], session.color_bgr.shape[0])
        stats = self._depth_stats_for_roi(session, full_roi)
        self.get_logger().info(
            f"Captured frame for '{session.object_name}' "
            f"({session.color_bgr.shape[1]}x{session.color_bgr.shape[0]}, "
            f"depth={'yes' if session.depth_m is not None else 'no'})"
        )
        return {
            "session_id": session.session_id,
            "object_name": session.object_name,
            "view_label": session.view_label,
            "width": int(session.color_bgr.shape[1]),
            "height": int(session.color_bgr.shape[0]),
            "image_url": f"/api/capture.jpg?session_id={session.session_id}",
            "depth_available": session.depth_m is not None,
            "depth_sync_offset_sec": session.depth_sync_offset_sec,
            "full_frame_depth": stats.as_dict(),
        }

    def get_capture_jpeg(self, session_id: str) -> bytes:
        return self._get_session(session_id).color_jpeg

    def api_crop_stats(self, payload: dict[str, Any]) -> dict[str, Any]:
        session = self._get_session(str(payload.get("session_id", "")))
        height, width = session.color_bgr.shape[:2]
        try:
            roi = normalize_roi(
                payload.get("roi", {}),
                width,
                height,
                min_width=int(self.get_parameter("min_crop_width_px").value),
                min_height=int(self.get_parameter("min_crop_height_px").value),
            )
        except ValueError as exc:
            raise ApiError(400, str(exc)) from exc
        stats = self._depth_stats_for_roi(session, roi)
        return {
            "session_id": session.session_id,
            "roi": roi.as_dict(),
            "depth": stats.as_dict(),
        }

    def _storage_roots(self) -> dict[str, Path]:
        base = Path(str(self.get_parameter("base_dir").value)).expanduser().resolve()
        base.mkdir(parents=True, exist_ok=True)
        roots = {
            "base": base,
            "original": ensure_under_root(
                base,
                base / str(self.get_parameter("original_subdir").value),
            ),
            "curated": ensure_under_root(
                base,
                base / str(self.get_parameter("curated_subdir").value),
            ),
            "depth": ensure_under_root(
                base,
                base / str(self.get_parameter("depth_subdir").value),
            ),
            "metadata": ensure_under_root(
                base,
                base / str(self.get_parameter("metadata_subdir").value),
            ),
        }
        return roots

    def api_save(self, payload: dict[str, Any]) -> dict[str, Any]:
        session = self._get_session(str(payload.get("session_id", "")))
        color_height, color_width = session.color_bgr.shape[:2]
        try:
            roi = normalize_roi(
                payload.get("roi", {}),
                color_width,
                color_height,
                min_width=int(self.get_parameter("min_crop_width_px").value),
                min_height=int(self.get_parameter("min_crop_height_px").value),
            )
        except ValueError as exc:
            raise ApiError(400, str(exc)) from exc

        object_name = sanitize_component(
            str(payload.get("object_name") or session.object_name),
            fallback=session.object_name,
        )
        view_label = sanitize_component(
            str(payload.get("view_label") or session.view_label),
            fallback="view",
        )
        notes = str(payload.get("notes") or "").strip()[:2000]
        save_original = bool(
            payload.get(
                "save_original",
                bool(self.get_parameter("save_original_default").value),
            )
        )
        save_depth = bool(
            payload.get(
                "save_depth",
                bool(self.get_parameter("save_depth_default").value),
            )
        )

        crop = crop_array(session.color_bgr, roi)
        quality = int(np.clip(self.get_parameter("save_jpeg_quality").value, 50, 100))
        roots = self._storage_roots()
        suffix = f"{session.filename_timestamp}_{view_label}_{session.session_id[:6]}"
        original_path = roots["original"] / object_name / f"{suffix}_original.jpg"
        crop_path = roots["curated"] / object_name / f"{suffix}.jpg"
        depth_path = roots["depth"] / object_name / f"{suffix}_depth.png"
        metadata_path = roots["metadata"] / object_name / f"{suffix}.json"

        depth_roi = self._depth_roi_for_color_roi(session, roi)
        depth_stats = self._depth_stats_for_roi(session, roi)
        depth_saved = False

        try:
            if save_original:
                atomic_write_bytes(
                    original_path,
                    encode_image(session.color_bgr, ".jpg", quality=quality),
                )
            atomic_write_bytes(crop_path, encode_image(crop, ".jpg", quality=quality))
            if (
                save_depth
                and session.depth_raw_for_png is not None
                and depth_roi is not None
            ):
                depth_crop = crop_array(session.depth_raw_for_png, depth_roi)
                atomic_write_bytes(depth_path, encode_image(depth_crop, ".png"))
                depth_saved = True

            metadata: dict[str, Any] = {
                "schema_version": 1,
                "object_name": object_name,
                "view_label": view_label,
                "notes": notes,
                "session_id": session.session_id,
                "captured_local_iso": session.created_local_iso,
                "saved_local_iso": datetime.now().astimezone().isoformat(timespec="milliseconds"),
                "source": {
                    "camera_family": "Intel RealSense D435/D435f",
                    "color_topic": str(self.get_parameter("color_topic").value),
                    "depth_topic": str(self.get_parameter("depth_topic").value),
                    "color_stamp_ns": session.color_stamp_ns,
                    "color_frame_id": session.color_frame_id,
                    "color_encoding": session.color_encoding,
                    "depth_stamp_ns": session.depth_stamp_ns,
                    "depth_frame_id": session.depth_frame_id,
                    "depth_encoding": session.depth_encoding,
                    "depth_sync_offset_sec": session.depth_sync_offset_sec,
                },
                "image": {
                    "original_width": color_width,
                    "original_height": color_height,
                    "crop_width": int(crop.shape[1]),
                    "crop_height": int(crop.shape[0]),
                    "crop_roi": roi.as_dict(),
                    "jpeg_quality": quality,
                },
                "depth": {
                    **depth_stats.as_dict(),
                    "saved": depth_saved,
                    "saved_unit": "millimeter_uint16_png" if depth_saved else None,
                    "depth_roi": depth_roi.as_dict() if depth_roi else None,
                },
                "camera_info": session.camera_info,
                "files": {
                    "original": str(original_path) if save_original else None,
                    "crop": str(crop_path),
                    "depth_crop": str(depth_path) if depth_saved else None,
                    "metadata": str(metadata_path),
                },
            }
            atomic_write_json(metadata_path, metadata)
        except (OSError, ValueError, RuntimeError, cv2.error) as exc:
            self._last_error = f"Save failed: {exc}"
            raise ApiError(500, "Failed to save capture files", str(exc)) from exc

        self._saved_count += 1
        result = {
            "event": "capture_saved",
            "object_name": object_name,
            "view_label": view_label,
            "session_id": session.session_id,
            "crop_roi": roi.as_dict(),
            "depth": depth_stats.as_dict(),
            "paths": {
                "original": str(original_path) if save_original else None,
                "crop": str(crop_path),
                "depth_crop": str(depth_path) if depth_saved else None,
                "metadata": str(metadata_path),
            },
        }
        self._event_queue.put(result)
        self.get_logger().info(
            f"Saved '{object_name}' crop {crop.shape[1]}x{crop.shape[0]} to {crop_path}"
        )

        clear_after = bool(self.get_parameter("clear_session_after_save").value)
        if clear_after:
            with self._session_lock:
                if self._active_session and self._active_session.session_id == session.session_id:
                    self._active_session = None
        return {
            "session_cleared": clear_after,
            **result,
        }

    def api_discard(self, payload: dict[str, Any]) -> dict[str, Any]:
        requested_id = str(payload.get("session_id", ""))
        with self._session_lock:
            session = self._active_session
            if session is None:
                return {"discarded": False}
            if requested_id and requested_id != session.session_id:
                raise ApiError(409, "The capture session is stale")
            self._active_session = None
        self.get_logger().info(f"Discarded capture session {session.session_id}")
        return {"discarded": True, "session_id": session.session_id}

    def destroy_node(self) -> bool:
        self._shutdown_event.set()
        with self._preview_condition:
            self._preview_condition.notify_all()
        try:
            self._http_server.shutdown()
            self._http_server.server_close()
        except Exception:
            pass
        if self._preview_thread.is_alive():
            self._preview_thread.join(timeout=2.0)
        if self._http_thread.is_alive():
            self._http_thread.join(timeout=2.0)
        return super().destroy_node()


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node: D435CaptureCropNode | None = None
    try:
        node = D435CaptureCropNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
