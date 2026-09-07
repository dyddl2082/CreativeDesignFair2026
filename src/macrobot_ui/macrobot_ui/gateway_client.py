from __future__ import annotations

import json
from pathlib import Path
import secrets
import socket
import time
from typing import Any, Mapping


class GatewayClientError(RuntimeError):
    pass


class GatewaySocketClient:
    """Small stdlib-only client for the existing Action Gateway Unix socket."""

    def __init__(self, socket_path: str, *, timeout_s: float = 5.0) -> None:
        self.socket_path = str(Path(socket_path).expanduser())
        self.timeout_s = float(timeout_s)

    def request(
        self,
        payload: Mapping[str, Any],
        *,
        timeout_s: float | None = None,
    ) -> Any:
        timeout = self.timeout_s if timeout_s is None else float(timeout_s)
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.settimeout(timeout)
            try:
                client.connect(self.socket_path)
            except OSError as exc:
                raise GatewayClientError(
                    f"Action Gateway socket 연결 실패: {self.socket_path}: {exc}"
                ) from exc
            encoded = (
                json.dumps(dict(payload), ensure_ascii=False, separators=(",", ":"))
                + "\n"
            ).encode("utf-8")
            client.sendall(encoded)
            buffer = bytearray()
            while b"\n" not in buffer:
                chunk = client.recv(65536)
                if not chunk:
                    break
                buffer.extend(chunk)
        if not buffer:
            raise GatewayClientError("Action Gateway가 응답하지 않았습니다.")
        line = bytes(buffer).split(b"\n", 1)[0]
        try:
            response = json.loads(line.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise GatewayClientError("Action Gateway 응답이 유효한 JSON이 아닙니다.") from exc
        if not isinstance(response, dict) or not bool(response.get("ok")):
            detail = response.get("message", response.get("error", "unknown error"))
            raise GatewayClientError(str(detail))
        return response.get("result")

    def status(self, *, timeout_s: float = 0.25) -> dict[str, Any]:
        result = self.request({"op": "status"}, timeout_s=timeout_s)
        return result if isinstance(result, dict) else {"raw": result}

    def stop_all(self, reason: str = "ui_stop") -> dict[str, Any]:
        run_id = f"ui-stop-{int(time.time() * 1000)}-{secrets.token_hex(3)}"
        opened = self.request({"op": "open_run", "run_id": run_id})
        try:
            stop_result = self.request(
                {
                    "op": "call",
                    "run_id": run_id,
                    "function": "STOP",
                    "args": {},
                },
                timeout_s=10.0,
            )
        finally:
            try:
                closed = self.request({"op": "close_run", "run_id": run_id})
            except Exception as exc:
                closed = {"close_error": f"{type(exc).__name__}: {exc}"}
        return {
            "run_id": run_id,
            "reason": reason,
            "open_result": opened,
            "stop_result": stop_result,
            "close_result": closed,
        }
