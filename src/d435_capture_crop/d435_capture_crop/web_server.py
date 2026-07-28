"""Small dependency-free HTTP server for the D435 capture/crop browser UI."""

from __future__ import annotations

import json
import mimetypes
import socket
import threading
import urllib.parse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Protocol


class CaptureBackend(Protocol):
    """Methods exposed by the ROS node to the HTTP layer."""

    def api_status(self) -> dict[str, Any]: ...

    def api_capture(self, payload: dict[str, Any]) -> dict[str, Any]: ...

    def api_crop_stats(self, payload: dict[str, Any]) -> dict[str, Any]: ...

    def api_save(self, payload: dict[str, Any]) -> dict[str, Any]: ...

    def api_discard(self, payload: dict[str, Any]) -> dict[str, Any]: ...

    def get_capture_jpeg(self, session_id: str) -> bytes: ...

    def wait_for_preview(self, last_sequence: int, timeout_sec: float) -> tuple[int, bytes | None]: ...

    def is_http_running(self) -> bool: ...


class ApiError(RuntimeError):
    """HTTP-friendly application error."""

    def __init__(self, status: int, message: str, details: Any | None = None):
        super().__init__(message)
        self.status = int(status)
        self.message = str(message)
        self.details = details


class CaptureHttpServer(ThreadingHTTPServer):
    """Threaded server carrying references to the ROS backend and static root."""

    daemon_threads = True
    allow_reuse_address = True

    def __init__(
        self,
        address: tuple[str, int],
        backend: CaptureBackend,
        static_root: Path,
        max_json_bytes: int = 1_000_000,
    ):
        super().__init__(address, CaptureRequestHandler)
        self.backend = backend
        self.static_root = Path(static_root).resolve()
        self.max_json_bytes = int(max_json_bytes)


class CaptureRequestHandler(BaseHTTPRequestHandler):
    """Serve the local web application, JSON API, and MJPEG preview."""

    server: CaptureHttpServer
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt: str, *args: Any) -> None:
        # ROS logs already provide higher-level status. Avoid noisy per-frame HTTP logs.
        return

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)
        try:
            if path in {"/", "/index.html"}:
                self._serve_static("index.html")
            elif path.startswith("/static/"):
                self._serve_static(path.removeprefix("/static/"))
            elif path == "/api/status":
                self._send_json(HTTPStatus.OK, self.server.backend.api_status())
            elif path == "/api/capture.jpg":
                session_id = (query.get("session_id") or [""])[0]
                if not session_id:
                    raise ApiError(HTTPStatus.BAD_REQUEST, "session_id is required")
                jpeg = self.server.backend.get_capture_jpeg(session_id)
                self._send_bytes(HTTPStatus.OK, jpeg, "image/jpeg", cache=False)
            elif path == "/stream.mjpg":
                self._serve_mjpeg()
            elif path == "/healthz":
                self._send_json(HTTPStatus.OK, {"ok": True})
            else:
                raise ApiError(HTTPStatus.NOT_FOUND, "Not found")
        except ApiError as exc:
            self._send_json(exc.status, {"ok": False, "error": exc.message, "details": exc.details})
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            return
        except Exception as exc:  # pragma: no cover - defensive HTTP boundary
            self._send_json(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                {"ok": False, "error": "Internal server error", "details": str(exc)},
            )

    def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        parsed = urllib.parse.urlparse(self.path)
        try:
            payload = self._read_json()
            if parsed.path == "/api/capture":
                result = self.server.backend.api_capture(payload)
            elif parsed.path == "/api/crop_stats":
                result = self.server.backend.api_crop_stats(payload)
            elif parsed.path == "/api/save":
                result = self.server.backend.api_save(payload)
            elif parsed.path == "/api/discard":
                result = self.server.backend.api_discard(payload)
            else:
                raise ApiError(HTTPStatus.NOT_FOUND, "Not found")
            self._send_json(HTTPStatus.OK, {"ok": True, **result})
        except ApiError as exc:
            self._send_json(exc.status, {"ok": False, "error": exc.message, "details": exc.details})
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            return
        except Exception as exc:  # pragma: no cover - defensive HTTP boundary
            self._send_json(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                {"ok": False, "error": "Internal server error", "details": str(exc)},
            )

    def _read_json(self) -> dict[str, Any]:
        content_type = self.headers.get("Content-Type", "")
        if "application/json" not in content_type:
            raise ApiError(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, "Content-Type must be application/json")
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError as exc:
            raise ApiError(HTTPStatus.BAD_REQUEST, "Invalid Content-Length") from exc
        if content_length < 0 or content_length > self.server.max_json_bytes:
            raise ApiError(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, "JSON request is too large")
        raw = self.rfile.read(content_length)
        try:
            decoded = json.loads(raw.decode("utf-8") or "{}")
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ApiError(HTTPStatus.BAD_REQUEST, "Invalid JSON body") from exc
        if not isinstance(decoded, dict):
            raise ApiError(HTTPStatus.BAD_REQUEST, "JSON body must be an object")
        return decoded

    def _serve_static(self, relative_path: str) -> None:
        relative = Path(relative_path)
        if relative.is_absolute() or ".." in relative.parts:
            raise ApiError(HTTPStatus.BAD_REQUEST, "Invalid static path")
        path = (self.server.static_root / relative).resolve()
        if self.server.static_root not in path.parents and path != self.server.static_root:
            raise ApiError(HTTPStatus.BAD_REQUEST, "Invalid static path")
        if not path.is_file():
            raise ApiError(HTTPStatus.NOT_FOUND, "Static file not found")
        mime_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        self._send_bytes(HTTPStatus.OK, path.read_bytes(), mime_type, cache=False)

    def _serve_mjpeg(self) -> None:
        boundary = "macrobot-frame"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", f"multipart/x-mixed-replace; boundary={boundary}")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Connection", "close")
        self.end_headers()

        last_sequence = -1
        while self.server.backend.is_http_running():
            sequence, jpeg = self.server.backend.wait_for_preview(last_sequence, timeout_sec=2.0)
            if jpeg is None or sequence == last_sequence:
                continue
            last_sequence = sequence
            header = (
                f"--{boundary}\r\n"
                "Content-Type: image/jpeg\r\n"
                f"Content-Length: {len(jpeg)}\r\n"
                "Cache-Control: no-cache\r\n\r\n"
            ).encode("ascii")
            self.wfile.write(header)
            self.wfile.write(jpeg)
            self.wfile.write(b"\r\n")
            self.wfile.flush()

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        data = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self._send_bytes(status, data, "application/json; charset=utf-8", cache=False)

    def _send_bytes(
        self,
        status: int,
        data: bytes,
        content_type: str,
        *,
        cache: bool,
    ) -> None:
        self.send_response(int(status))
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Content-Type-Options", "nosniff")
        if cache:
            self.send_header("Cache-Control", "public, max-age=3600")
        else:
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
            self.send_header("Pragma", "no-cache")
        self.end_headers()
        self.wfile.write(data)


def start_http_server(
    backend: CaptureBackend,
    host: str,
    port: int,
    static_root: Path,
) -> tuple[CaptureHttpServer, threading.Thread]:
    """Start the HTTP server in a daemon thread."""

    try:
        server = CaptureHttpServer((host, int(port)), backend, static_root)
    except OSError as exc:
        if exc.errno in {98, 48, 10048}:
            raise RuntimeError(f"HTTP port {port} is already in use") from exc
        raise
    thread = threading.Thread(
        target=server.serve_forever,
        name="d435-capture-http",
        daemon=True,
    )
    thread.start()
    return server, thread


def guess_access_url(host: str, port: int) -> str:
    """Return a useful log URL without making network configuration assumptions."""

    display_host = host
    if host in {"0.0.0.0", "::", ""}:
        try:
            display_host = socket.gethostbyname(socket.gethostname())
        except OSError:
            display_host = "<PI_IP>"
    return f"http://{display_host}:{int(port)}"
