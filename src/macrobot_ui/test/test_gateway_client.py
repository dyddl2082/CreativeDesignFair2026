from __future__ import annotations

import json
from pathlib import Path
import socketserver
import threading

from macrobot_ui.gateway_client import GatewaySocketClient


class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        request = json.loads(self.rfile.readline().decode("utf-8"))
        op = request["op"]
        if op == "status":
            result = {"real_motion_enabled": False, "spec_version": "0.2.0"}
        elif op == "open_run":
            result = {"run_id": request["run_id"]}
        elif op == "call":
            result = {"success": request["function"] == "STOP"}
        elif op == "close_run":
            result = {"closed": True}
        else:
            result = {}
        self.wfile.write((json.dumps({"ok": True, "result": result}) + "\n").encode())


class Server(socketserver.ThreadingUnixStreamServer):
    daemon_threads = True


def test_status_and_stop(tmp_path: Path):
    socket_path = tmp_path / "gateway.sock"
    server = Server(str(socket_path), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        client = GatewaySocketClient(str(socket_path))
        assert client.status()["spec_version"] == "0.2.0"
        result = client.stop_all()
        assert result["stop_result"]["success"] is True
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
