from __future__ import annotations

from collections import OrderedDict
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import threading
import time
from typing import Any

import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import String

from .gateway_client import GatewaySocketClient
from .ros_protocol import (
    BACKEND_STATUS_SCHEMA,
    HELD_RESET_REQUEST_SCHEMA,
    STOP_REQUEST_SCHEMA,
    TASK_RESULT_SCHEMA,
    TASK_STATUS_SCHEMA,
    ProtocolError,
    classify_runner_execution,
    compact_json,
    extract_last_json_object,
    parse_json_object,
    parse_task_request,
)


class MacRobotUiBackend(Node):
    """Pi-local bridge from ROS 2 UI requests to robot_code_runner."""

    def __init__(self) -> None:
        super().__init__("macrobot_ui_backend")
        defaults = {
            "request_topic": "/macrobot/ui/task/request",
            "status_topic": "/macrobot/ui/task/status",
            "result_topic": "/macrobot/ui/task/result",
            "stop_topic": "/macrobot/ui/stop",
            "held_reset_topic": "/macrobot/ui/held/reset",
            "stored_task_admin_topic": "/macrobot/stored_pick/admin",
            "stored_task_status_topic": "/macrobot/stored_pick/status",
            "backend_status_topic": "/macrobot/ui/backend/status",
            "gateway_socket": "/tmp/macrobot_action_gateway.sock",
            "allow_execution": False,
            "code_root": str(
                Path.home() / "MacRobot" / "data" / "ui" / "approved_tasks"
            ),
            "run_log_root": str(Path.home() / "MacRobot" / "data" / "llm_runs"),
            "runner_wall_timeout_s": 5000.0,
            "max_code_bytes": 200000,
            "request_cache_size": 64,
            "heartbeat_period_s": 1.0,
            "held_reset_timeout_s": 5.0,
        }
        for name, value in defaults.items():
            self.declare_parameter(name, value)

        self.allow_execution = bool(self.get_parameter("allow_execution").value)
        self.gateway_socket = str(self.get_parameter("gateway_socket").value)
        self.code_root = Path(str(self.get_parameter("code_root").value)).expanduser()
        self.run_log_root = Path(
            str(self.get_parameter("run_log_root").value)
        ).expanduser()
        self.runner_wall_timeout_s = float(
            self.get_parameter("runner_wall_timeout_s").value
        )
        self.held_reset_timeout_s = float(
            self.get_parameter("held_reset_timeout_s").value
        )
        self.max_code_bytes = int(self.get_parameter("max_code_bytes").value)
        self.request_cache_size = max(
            8, int(self.get_parameter("request_cache_size").value)
        )

        control_qos = QoSProfile(
            depth=20,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE,
        )
        result_qos = QoSProfile(
            depth=20,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )
        heartbeat_qos = QoSProfile(
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )
        self.status_pub = self.create_publisher(
            String, str(self.get_parameter("status_topic").value), control_qos
        )
        self.result_pub = self.create_publisher(
            String, str(self.get_parameter("result_topic").value), result_qos
        )
        self.backend_status_pub = self.create_publisher(
            String,
            str(self.get_parameter("backend_status_topic").value),
            heartbeat_qos,
        )
        self.stored_task_admin_pub = self.create_publisher(
            String,
            str(self.get_parameter("stored_task_admin_topic").value),
            control_qos,
        )
        self.create_subscription(
            String,
            str(self.get_parameter("request_topic").value),
            self._request_callback,
            control_qos,
        )
        self.create_subscription(
            String,
            str(self.get_parameter("stop_topic").value),
            self._stop_callback,
            control_qos,
        )
        self.create_subscription(
            String,
            str(self.get_parameter("held_reset_topic").value),
            self._held_reset_callback,
            control_qos,
        )
        self.create_subscription(
            String,
            str(self.get_parameter("stored_task_status_topic").value),
            self._stored_task_status_callback,
            control_qos,
        )

        self._gateway = GatewaySocketClient(self.gateway_socket, timeout_s=1.0)
        self._lock = threading.RLock()
        self._held_reset_cv = threading.Condition(self._lock)
        self._stored_task_status_seq = 0
        self._last_stored_task_status: dict[str, Any] = {}
        self._maintenance_request_id = ""
        self._active_request_id = ""
        self._active_source_hash = ""
        self._active_process: subprocess.Popen[str] | None = None
        self._cache: OrderedDict[str, dict[str, Any]] = OrderedDict()
        self._shutdown = False
        self._last_gateway_status: dict[str, Any] = {}
        self._last_gateway_error = ""

        period = max(0.5, float(self.get_parameter("heartbeat_period_s").value))
        self._heartbeat_timer = self.create_timer(period, self._publish_backend_status)
        self.get_logger().info(
            "MacRobot UI backend ready: "
            f"allow_execution={self.allow_execution}, socket={self.gateway_socket}"
        )


    @staticmethod
    def _active_gateway_actions(gateway: dict[str, Any]) -> list[dict[str, Any]]:
        snapshot = gateway.get("actions", {}) if isinstance(gateway, dict) else {}
        actions = snapshot.get("actions", {}) if isinstance(snapshot, dict) else {}
        terminal = {"succeeded", "failed", "canceled", "timed_out"}
        active: list[dict[str, Any]] = []
        if isinstance(actions, dict):
            for action_id, item in actions.items():
                if not isinstance(item, dict):
                    continue
                state = str(item.get("state", "")).strip().casefold()
                if state not in terminal:
                    active.append({"action_id": action_id, **item})
        return active

    @staticmethod
    def _stored_task_busy(payload: dict[str, Any]) -> bool:
        state = str(
            payload.get("action_state", payload.get("state", ""))
        ).strip().casefold()
        return bool(state) and state not in {
            "idle",
            "succeeded",
            "failed",
            "canceled",
            "timed_out",
        }

    def _stored_task_status_callback(self, message: String) -> None:
        payload = parse_json_object(message.data)
        if payload is None:
            return
        with self._held_reset_cv:
            self._last_stored_task_status = dict(payload)
            self._stored_task_status_seq += 1
            self._held_reset_cv.notify_all()

    def _held_reset_callback(self, message: String) -> None:
        payload = parse_json_object(message.data)
        request_id = str(payload.get("request_id", "")) if payload else ""
        if payload is None or payload.get("schema") != HELD_RESET_REQUEST_SCHEMA:
            self._publish_result(
                {
                    "schema": TASK_RESULT_SCHEMA,
                    "request_id": request_id,
                    "ok": False,
                    "event": "ui_held_state_clear_failed",
                    "error_code": "INVALID_HELD_RESET_REQUEST",
                    "message": "invalid held-state reset request",
                }
            )
            return
        if payload.get("operator_confirmed_empty") is not True:
            self._publish_result(
                {
                    "schema": TASK_RESULT_SCHEMA,
                    "request_id": request_id,
                    "ok": False,
                    "event": "ui_held_state_clear_failed",
                    "error_code": "PHYSICAL_EMPTY_CONFIRMATION_REQUIRED",
                    "message": "operator must confirm that the physical gripper is empty",
                }
            )
            return
        if not request_id:
            self._publish_result(
                {
                    "schema": TASK_RESULT_SCHEMA,
                    "request_id": "",
                    "ok": False,
                    "event": "ui_held_state_clear_failed",
                    "error_code": "REQUEST_ID_REQUIRED",
                    "message": "held-state reset request_id is required",
                }
            )
            return
        with self._lock:
            if self._active_request_id or self._maintenance_request_id:
                busy = self._active_request_id or self._maintenance_request_id
                self._publish_result(
                    {
                        "schema": TASK_RESULT_SCHEMA,
                        "request_id": request_id,
                        "ok": False,
                        "event": "ui_held_state_clear_failed",
                        "error_code": "BACKEND_BUSY",
                        "message": f"active request: {busy}",
                    }
                )
                return
            self._maintenance_request_id = request_id
            with self._held_reset_cv:
                before_seq = self._stored_task_status_seq
                stored_status = dict(self._last_stored_task_status)
        try:
            gateway = self._gateway.status(timeout_s=0.5)
        except Exception as exc:
            self._finish_held_reset(
                request_id,
                False,
                "GATEWAY_UNAVAILABLE",
                f"{type(exc).__name__}: {exc}",
            )
            return
        active_actions = self._active_gateway_actions(gateway)
        if active_actions:
            self._finish_held_reset(
                request_id,
                False,
                "ROBOT_ACTION_ACTIVE",
                "held state cannot be cleared while a Gateway action is active",
                active_actions=active_actions,
            )
            return
        if self._stored_task_busy(stored_status):
            self._finish_held_reset(
                request_id,
                False,
                "STORED_TASK_ACTIVE",
                "stored-object task node reports an active task",
                stored_task_status=stored_status,
            )
            return
        self._publish_status(
            {
                "schema": TASK_STATUS_SCHEMA,
                "request_id": request_id,
                "event": "ui_held_state_clear_started",
                "state": "MAINTENANCE",
            }
        )
        threading.Thread(
            target=self._perform_held_reset,
            args=(request_id, before_seq),
            name="macrobot-ui-held-reset",
            daemon=True,
        ).start()

    def _perform_held_reset(self, request_id: str, before_seq: int) -> None:
        deadline = time.monotonic() + max(1.0, self.held_reset_timeout_s)
        next_publish = 0.0
        source_payload: dict[str, Any] | None = None
        error_code = "HELD_RESET_TIMEOUT"
        message = "held_object_cleared acknowledgement was not observed"
        while time.monotonic() < deadline and not self._shutdown:
            now = time.monotonic()
            if now >= next_publish:
                self.stored_task_admin_pub.publish(
                    String(
                        data=compact_json(
                            {
                                "action": "clear_held",
                                "source": "macrobot_ui",
                                "request_id": request_id,
                            }
                        )
                    )
                )
                next_publish = now + 0.5
            with self._held_reset_cv:
                if self._stored_task_status_seq <= before_seq:
                    self._held_reset_cv.wait(timeout=0.1)
                seq = self._stored_task_status_seq
                payload = dict(self._last_stored_task_status)
            if seq <= before_seq:
                continue
            event = str(payload.get("event", ""))
            if event == "object_memory_admin_failed":
                source_payload = payload
                error_code = "HELD_RESET_SOURCE_FAILED"
                message = str(payload.get("error", "object memory admin failed"))
                break
            held = payload.get("held_object")
            held_state = (
                str(held.get("state", "")).strip().casefold()
                if isinstance(held, dict)
                else ""
            )
            if event == "held_object_cleared" and held_state == "empty":
                source_payload = payload
                error_code = ""
                message = ""
                break
            before_seq = seq
        if source_payload is None or error_code:
            self._finish_held_reset(
                request_id,
                False,
                error_code,
                message,
                stored_task_status=source_payload,
            )
            return
        sync_deadline = time.monotonic() + 2.0
        gateway_status: dict[str, Any] | None = None
        while time.monotonic() < sync_deadline:
            try:
                gateway_status = self._gateway.status(timeout_s=0.5)
            except Exception:
                gateway_status = None
            robot_state = (
                gateway_status.get("robot_state", {})
                if isinstance(gateway_status, dict)
                else {}
            )
            if (
                isinstance(robot_state, dict)
                and robot_state.get("held_object_known") is True
                and robot_state.get("held_object") is None
            ):
                self._finish_held_reset(
                    request_id,
                    True,
                    "",
                    "보유 상태를 empty로 초기화했고 Gateway 동기화까지 확인했습니다.",
                    stored_task_status=source_payload,
                    gateway_robot_state=robot_state,
                )
                return
            time.sleep(0.1)
        self._finish_held_reset(
            request_id,
            False,
            "GATEWAY_HELD_STATE_SYNC_TIMEOUT",
            "source memory is empty but Gateway did not confirm held_object_known=true/held_object=None",
            stored_task_status=source_payload,
            gateway_status=gateway_status,
        )

    def _finish_held_reset(
        self,
        request_id: str,
        ok: bool,
        error_code: str,
        message: str,
        **details: Any,
    ) -> None:
        with self._lock:
            if self._maintenance_request_id == request_id:
                self._maintenance_request_id = ""
        payload = {
            "schema": TASK_RESULT_SCHEMA,
            "request_id": request_id,
            "ok": bool(ok),
            "event": "ui_held_state_cleared" if ok else "ui_held_state_clear_failed",
            "message": message,
            **details,
        }
        if error_code:
            payload["error_code"] = error_code
        self._publish_result(payload)

    def _request_callback(self, message: String) -> None:
        payload = parse_json_object(message.data)
        if payload is None:
            self._publish_result(
                {
                    "schema": TASK_RESULT_SCHEMA,
                    "request_id": "",
                    "ok": False,
                    "event": "ui_task_rejected",
                    "error_code": "INVALID_JSON",
                    "message": "task request is not a JSON object",
                }
            )
            return
        try:
            request = parse_task_request(payload, max_code_bytes=self.max_code_bytes)
        except ProtocolError as exc:
            self._publish_result(
                {
                    "schema": TASK_RESULT_SCHEMA,
                    "request_id": str(payload.get("request_id", "")),
                    "ok": False,
                    "event": "ui_task_rejected",
                    "error_code": "INVALID_REQUEST",
                    "message": str(exc),
                }
            )
            return

        with self._lock:
            if self._maintenance_request_id:
                self._publish_result(
                    {
                        "schema": TASK_RESULT_SCHEMA,
                        "request_id": request.request_id,
                        "ok": False,
                        "event": "ui_task_rejected",
                        "error_code": "BACKEND_MAINTENANCE",
                        "message": f"maintenance request active: {self._maintenance_request_id}",
                        "source_sha256": request.source_sha256,
                    }
                )
                return
            cached = self._cache.get(request.request_id)
            if cached is not None:
                if cached.get("source_sha256") != request.source_sha256:
                    self._publish_result(
                        {
                            "schema": TASK_RESULT_SCHEMA,
                            "request_id": request.request_id,
                            "ok": False,
                            "event": "ui_task_rejected",
                            "error_code": "REQUEST_ID_HASH_CONFLICT",
                            "message": "same request_id was reused for different source",
                            "source_sha256": request.source_sha256,
                        }
                    )
                    return
                self._publish_status(
                    {
                        "schema": TASK_STATUS_SCHEMA,
                        "request_id": request.request_id,
                        "event": "ui_task_acknowledged",
                        "state": "DUPLICATE",
                        "duplicate": True,
                        "source_sha256": request.source_sha256,
                    }
                )
                final = cached.get("final_result")
                if isinstance(final, dict):
                    self._publish_result(final)
                return

            if self._active_request_id:
                if (
                    self._active_request_id == request.request_id
                    and self._active_source_hash == request.source_sha256
                ):
                    self._publish_status(
                        {
                            "schema": TASK_STATUS_SCHEMA,
                            "request_id": request.request_id,
                            "event": "ui_task_acknowledged",
                            "state": "RUNNING",
                            "duplicate": True,
                            "source_sha256": request.source_sha256,
                        }
                    )
                else:
                    self._publish_result(
                        {
                            "schema": TASK_RESULT_SCHEMA,
                            "request_id": request.request_id,
                            "ok": False,
                            "event": "ui_task_rejected",
                            "error_code": "BACKEND_BUSY",
                            "message": f"active request: {self._active_request_id}",
                            "source_sha256": request.source_sha256,
                        }
                    )
                return

            if request.mode == "execute" and not self.allow_execution:
                self._publish_result(
                    {
                        "schema": TASK_RESULT_SCHEMA,
                        "request_id": request.request_id,
                        "ok": False,
                        "event": "ui_task_rejected",
                        "error_code": "EXECUTION_DISABLED",
                        "message": (
                            "backend allow_execution is false; launch the backend with "
                            "allow_execution:=true after completing dry-run checks"
                        ),
                        "source_sha256": request.source_sha256,
                    }
                )
                return
            if request.mode == "execute" and not request.approved:
                self._publish_result(
                    {
                        "schema": TASK_RESULT_SCHEMA,
                        "request_id": request.request_id,
                        "ok": False,
                        "event": "ui_task_rejected",
                        "error_code": "APPROVAL_REQUIRED",
                        "message": "execute request requires approval for this exact source hash",
                        "source_sha256": request.source_sha256,
                    }
                )
                return

            self._active_request_id = request.request_id
            self._active_source_hash = request.source_sha256
            self._cache[request.request_id] = {
                "source_sha256": request.source_sha256,
                "final_result": None,
            }
            self._trim_cache_locked()

        self._publish_status(
            {
                "schema": TASK_STATUS_SCHEMA,
                "request_id": request.request_id,
                "event": "ui_task_acknowledged",
                "state": "VALIDATING" if request.mode == "validate" else "STARTING",
                "duplicate": False,
                "mode": request.mode,
                "source_sha256": request.source_sha256,
            }
        )
        thread = threading.Thread(
            target=self._run_request,
            args=(request,),
            name=f"macrobot-ui-task-{request.request_id}",
            daemon=True,
        )
        thread.start()

    def _run_request(self, request) -> None:
        started_ms = int(time.time() * 1000)
        try:
            code_path, metadata_path = self._persist_request(request)
            command = [
                sys.executable,
                "-m",
                "macrobot_action_gateway.code_runner",
                "--code",
                str(code_path),
                "--socket",
                self.gateway_socket,
                "--log-root",
                str(self.run_log_root),
            ]
            if request.mode == "execute":
                command.extend(
                    [
                        "--execute",
                        "--approved",
                        "--wall-timeout-s",
                        str(self.runner_wall_timeout_s),
                    ]
                )
            else:
                command.append("--validate-only")

            self._publish_status(
                {
                    "schema": TASK_STATUS_SCHEMA,
                    "request_id": request.request_id,
                    "event": "ui_task_runner_started",
                    "state": "RUNNING" if request.mode == "execute" else "VALIDATING",
                    "mode": request.mode,
                    "source_sha256": request.source_sha256,
                    "code_path": str(code_path),
                }
            )
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                start_new_session=True,
            )
            with self._lock:
                self._active_process = process
            try:
                stdout, stderr = process.communicate(
                    timeout=max(10.0, self.runner_wall_timeout_s + 30.0)
                )
                timed_out = False
            except subprocess.TimeoutExpired:
                timed_out = True
                try:
                    self._gateway.stop_all("ui_backend_runner_timeout")
                except Exception:
                    pass
                self._terminate_process(process)
                stdout, stderr = process.communicate(timeout=5.0)

            combined = "\n".join(part for part in (stdout, stderr) if part)
            runner_payload = extract_last_json_object(combined)
            if timed_out:
                result = {
                    "schema": TASK_RESULT_SCHEMA,
                    "request_id": request.request_id,
                    "ok": False,
                    "event": "ui_task_timed_out",
                    "error_code": "RUNNER_TIMEOUT",
                    "message": "robot_code_runner did not finish within the backend limit",
                }
            elif request.mode == "validate":
                valid = bool(runner_payload and runner_payload.get("valid"))
                result = {
                    "schema": TASK_RESULT_SCHEMA,
                    "request_id": request.request_id,
                    "ok": valid and process.returncode == 0,
                    "event": (
                        "ui_task_validated" if valid and process.returncode == 0
                        else "ui_task_validation_failed"
                    ),
                    "validation": runner_payload,
                }
            else:
                task_ok, task_event, task_status, task_message = (
                    classify_runner_execution(runner_payload, process.returncode)
                )
                result = {
                    "schema": TASK_RESULT_SCHEMA,
                    "request_id": request.request_id,
                    "ok": task_ok,
                    "event": task_event,
                    "task_status": task_status,
                    "task_message": task_message,
                    "runner_ok": bool(runner_payload and runner_payload.get("ok")),
                    "runner_result": runner_payload,
                }
            result.update(
                {
                    "mode": request.mode,
                    "source_sha256": request.source_sha256,
                    "runner_returncode": process.returncode,
                    "code_path": str(code_path),
                    "metadata_path": str(metadata_path),
                    "started_at_unix_ms": started_ms,
                    "finished_at_unix_ms": int(time.time() * 1000),
                }
            )
            if not result.get("ok") and runner_payload is None:
                result["runner_output"] = combined[-20000:]
            self._finish_request(request.request_id, result)
        except Exception as exc:
            result = {
                "schema": TASK_RESULT_SCHEMA,
                "request_id": request.request_id,
                "ok": False,
                "event": "ui_task_failed",
                "error_code": "BACKEND_EXCEPTION",
                "message": f"{type(exc).__name__}: {exc}",
                "mode": request.mode,
                "source_sha256": request.source_sha256,
                "started_at_unix_ms": started_ms,
                "finished_at_unix_ms": int(time.time() * 1000),
            }
            self._finish_request(request.request_id, result)

    def _persist_request(self, request) -> tuple[Path, Path]:
        directory = self.code_root / request.request_id
        directory.mkdir(parents=True, exist_ok=True)
        code_path = directory / "task.py"
        metadata_path = directory / "request.json"
        self._atomic_write(code_path, request.code, 0o600)
        self._atomic_write(
            metadata_path,
            json.dumps(
                {
                    "request_id": request.request_id,
                    "mode": request.mode,
                    "approved": request.approved,
                    "source_sha256": request.source_sha256,
                    "metadata": request.metadata,
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            0o600,
        )
        return code_path, metadata_path

    @staticmethod
    def _atomic_write(path: Path, text: str, mode: int) -> None:
        descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                stream.write(text)
                stream.flush()
                os.fsync(stream.fileno())
            os.chmod(temporary, mode)
            os.replace(temporary, path)
        except Exception:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass
            raise

    def _finish_request(self, request_id: str, result: dict[str, Any]) -> None:
        with self._lock:
            entry = self._cache.get(request_id)
            if entry is not None:
                entry["final_result"] = dict(result)
                self._cache.move_to_end(request_id)
            if self._active_request_id == request_id:
                self._active_request_id = ""
                self._active_source_hash = ""
                self._active_process = None
        self._publish_result(result)

    def _stop_callback(self, message: String) -> None:
        payload = parse_json_object(message.data) or {}
        if payload.get("schema") not in {None, STOP_REQUEST_SCHEMA}:
            return
        request_id = str(payload.get("request_id", "ui-stop"))
        reason = str(payload.get("reason", "operator_stop"))
        self._publish_status(
            {
                "schema": TASK_STATUS_SCHEMA,
                "request_id": request_id,
                "event": "ui_stop_acknowledged",
                "state": "STOPPING",
                "reason": reason,
            }
        )
        threading.Thread(
            target=self._perform_stop,
            args=(request_id, reason),
            name="macrobot-ui-stop",
            daemon=True,
        ).start()

    def _perform_stop(self, request_id: str, reason: str) -> None:
        try:
            gateway_result = self._gateway.stop_all(reason)
            ok = True
            error = ""
        except Exception as exc:
            gateway_result = None
            ok = False
            error = f"{type(exc).__name__}: {exc}"
        with self._lock:
            process = self._active_process
        if process is not None and process.poll() is None:
            try:
                process.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                self._terminate_process(process)
        self._publish_result(
            {
                "schema": TASK_RESULT_SCHEMA,
                "request_id": request_id,
                "ok": ok,
                "event": "ui_stop_completed" if ok else "ui_stop_failed",
                "reason": reason,
                "gateway_result": gateway_result,
                "message": error,
            }
        )

    @staticmethod
    def _terminate_process(process: subprocess.Popen[str]) -> None:
        if process.poll() is not None:
            return
        try:
            os.killpg(process.pid, signal.SIGTERM)
            process.wait(timeout=3.0)
        except Exception:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except Exception:
                process.kill()

    def _publish_backend_status(self) -> None:
        try:
            gateway = self._gateway.status()
            self._last_gateway_status = gateway
            self._last_gateway_error = ""
            gateway_reachable = True
        except Exception as exc:
            gateway = self._last_gateway_status
            self._last_gateway_error = f"{type(exc).__name__}: {exc}"
            gateway_reachable = False
        with self._lock:
            active = self._active_request_id
            maintenance = self._maintenance_request_id
        payload = {
            "schema": BACKEND_STATUS_SCHEMA,
            "event": "ui_backend_heartbeat",
            "stamp_unix_ms": int(time.time() * 1000),
            "allow_execution": self.allow_execution,
            "active_request_id": active,
            "maintenance_request_id": maintenance,
            "gateway_reachable": gateway_reachable,
            "gateway_socket": self.gateway_socket,
            "gateway_real_motion_enabled": bool(
                gateway.get("real_motion_enabled", False)
            )
            if isinstance(gateway, dict)
            else False,
            "gateway_spec_version": gateway.get("spec_version", "")
            if isinstance(gateway, dict)
            else "",
            "gateway_error": self._last_gateway_error,
        }
        self.backend_status_pub.publish(String(data=compact_json(payload)))

    def _publish_status(self, payload: dict[str, Any]) -> None:
        self.status_pub.publish(String(data=compact_json(payload)))

    def _publish_result(self, payload: dict[str, Any]) -> None:
        self.result_pub.publish(String(data=compact_json(payload)))

    def _trim_cache_locked(self) -> None:
        while len(self._cache) > self.request_cache_size:
            key, entry = next(iter(self._cache.items()))
            if key == self._active_request_id or entry.get("final_result") is None:
                self._cache.move_to_end(key)
                break
            self._cache.popitem(last=False)

    def destroy_node(self) -> bool:
        self._shutdown = True
        with self._lock:
            process = self._active_process
        if process is not None and process.poll() is None:
            try:
                self._gateway.stop_all("ui_backend_shutdown")
            except Exception:
                pass
            self._terminate_process(process)
        return super().destroy_node()


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node: MacRobotUiBackend | None = None
    try:
        node = MacRobotUiBackend()
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
