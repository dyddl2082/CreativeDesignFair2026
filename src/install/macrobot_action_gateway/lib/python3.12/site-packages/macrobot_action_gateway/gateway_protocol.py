from __future__ import annotations

import json
import os
from pathlib import Path
import socket
import socketserver
import threading
from typing import Any

from .api_types import from_wire, to_wire
from .gateway_runtime import GatewayRuntime


class GatewayProtocolError(RuntimeError):
    pass


class _RequestHandler(socketserver.StreamRequestHandler):
    def handle(self) -> None:
        server: "GatewayUnixServer" = self.server  # type: ignore[assignment]
        raw = self.rfile.readline(server.max_request_bytes + 1)
        if len(raw) > server.max_request_bytes:
            self._write({"ok": False, "error": "REQUEST_TOO_LARGE"})
            return
        try:
            request = json.loads(raw.decode("utf-8"))
            if not isinstance(request, dict):
                raise ValueError("request must be a JSON object")
            response = server.dispatch(request)
        except Exception as exc:
            response = {
                "ok": False,
                "error": "PROTOCOL_ERROR",
                "message": f"{type(exc).__name__}: {exc}",
            }
        self._write(response)

    def _write(self, payload: dict[str, Any]) -> None:
        encoded = (json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8")
        self.wfile.write(encoded)
        self.wfile.flush()


class GatewayUnixServer(socketserver.ThreadingUnixStreamServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(
        self,
        socket_path: str,
        runtime: GatewayRuntime,
        *,
        max_request_bytes: int = 1_000_000,
    ) -> None:
        self.socket_path = str(Path(socket_path).expanduser())
        self.runtime = runtime
        self.max_request_bytes = int(max_request_bytes)
        path = Path(self.socket_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() or path.is_socket():
            path.unlink()
        super().__init__(self.socket_path, _RequestHandler)
        os.chmod(self.socket_path, 0o600)

    def dispatch(self, request: dict[str, Any]) -> dict[str, Any]:
        op = str(request.get("op", "")).strip()
        if op == "open_run":
            result = self.runtime.open_run(str(request.get("run_id", "")))
        elif op == "close_run":
            result = self.runtime.close_run(str(request.get("run_id", "")))
        elif op == "abort_run":
            result = self.runtime.abort_run(
                str(request.get("run_id", "")),
                str(request.get("reason", "worker_aborted")),
            )
        elif op == "call":
            args = from_wire(request.get("args", {}))
            if not isinstance(args, dict):
                raise ValueError("args must decode to a mapping")
            result = self.runtime.call(
                str(request.get("run_id", "")),
                str(request.get("function", "")),
                args,
            )
        elif op == "status":
            result = self.runtime.status()
        else:
            raise ValueError(f"unsupported op: {op}")
        return {"ok": True, "result": to_wire(result)}

    def shutdown_and_cleanup(self) -> None:
        self.shutdown()
        self.server_close()
        try:
            Path(self.socket_path).unlink()
        except FileNotFoundError:
            pass


class GatewayServerThread:
    def __init__(self, server: GatewayUnixServer) -> None:
        self.server = server
        self.thread = threading.Thread(
            target=server.serve_forever,
            name="macrobot-gateway-rpc",
            daemon=True,
        )

    def start(self) -> None:
        self.thread.start()

    def close(self) -> None:
        self.server.shutdown_and_cleanup()
        self.thread.join(timeout=2.0)


class GatewayRpcClient:
    def __init__(self, socket_path: str, *, timeout_s: float = 190.0) -> None:
        self.socket_path = str(Path(socket_path).expanduser())
        self.timeout_s = float(timeout_s)

    def request(self, payload: dict[str, Any], *, timeout_s: float | None = None) -> Any:
        timeout = self.timeout_s if timeout_s is None else float(timeout_s)
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.settimeout(timeout)
            try:
                client.connect(self.socket_path)
            except OSError as exc:
                raise GatewayProtocolError(
                    f"Robot Action Gateway socket 연결 실패: {self.socket_path}: {exc}"
                ) from exc
            encoded = (json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8")
            client.sendall(encoded)
            buffer = bytearray()
            while True:
                chunk = client.recv(65536)
                if not chunk:
                    break
                buffer.extend(chunk)
                if b"\n" in buffer:
                    break
        if not buffer:
            raise GatewayProtocolError("Gateway가 응답을 반환하지 않았습니다.")
        line = bytes(buffer).split(b"\n", 1)[0]
        response = json.loads(line.decode("utf-8"))
        if not isinstance(response, dict) or not response.get("ok"):
            raise GatewayProtocolError(
                str(response.get("message", response.get("error", "unknown gateway error")))
                if isinstance(response, dict)
                else "invalid gateway response"
            )
        return from_wire(response.get("result"))

    def open_run(self, run_id: str) -> dict[str, Any]:
        return self.request({"op": "open_run", "run_id": run_id})

    def close_run(self, run_id: str) -> dict[str, Any]:
        return self.request({"op": "close_run", "run_id": run_id})

    def abort_run(self, run_id: str, reason: str) -> dict[str, Any]:
        return self.request({"op": "abort_run", "run_id": run_id, "reason": reason})

    def call(
        self,
        run_id: str,
        function: str,
        args: dict[str, Any],
        *,
        timeout_s: float | None = None,
    ) -> Any:
        return self.request(
            {
                "op": "call",
                "run_id": run_id,
                "function": function,
                "args": to_wire(args),
            },
            timeout_s=timeout_s,
        )

    def status(self) -> dict[str, Any]:
        return self.request({"op": "status"}, timeout_s=5.0)
