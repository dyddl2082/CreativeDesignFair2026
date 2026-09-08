from __future__ import annotations

import hashlib
import json
import re
import time
from dataclasses import dataclass
from typing import Any, Mapping


TASK_REQUEST_SCHEMA = "macrobot.ui.task_request/v1"
TASK_STATUS_SCHEMA = "macrobot.ui.task_status/v1"
TASK_RESULT_SCHEMA = "macrobot.ui.task_result/v1"
STOP_REQUEST_SCHEMA = "macrobot.ui.stop_request/v1"
BACKEND_STATUS_SCHEMA = "macrobot.ui.backend_status/v1"
HELD_RESET_REQUEST_SCHEMA = "macrobot.ui.held_reset_request/v1"

REQUEST_ID_PATTERN = re.compile(r"^[0-9A-Za-z_.:-]{1,128}$")
TERMINAL_EVENTS = {
    "ui_task_validated",
    "ui_task_validation_failed",
    "ui_task_completed",
    "ui_task_partially_succeeded",
    "ui_task_canceled",
    "ui_task_failed",
    "ui_task_rejected",
    "ui_task_timed_out",
    "ui_held_state_cleared",
    "ui_held_state_clear_failed",
}


class ProtocolError(ValueError):
    pass



def extract_runner_task_outcome(
    payload: Mapping[str, Any] | None,
) -> tuple[str, str]:
    """Return TaskOutcome status/message from either v4.5 fields or legacy wire data."""
    if not isinstance(payload, Mapping):
        return "", ""
    status = str(payload.get("task_status", "")).strip().casefold()
    message = str(payload.get("task_message", "")).strip()
    outcome = payload.get("outcome")
    if isinstance(outcome, Mapping):
        if not status:
            raw_status = outcome.get("status")
            if isinstance(raw_status, Mapping):
                status = str(raw_status.get("value", "")).strip().casefold()
            elif isinstance(raw_status, str):
                status = raw_status.strip().casefold()
        if not message:
            raw_message = outcome.get("message", "")
            if raw_message is not None:
                message = str(raw_message).strip()
    return status, message


def classify_runner_execution(
    payload: Mapping[str, Any] | None,
    returncode: int,
) -> tuple[bool, str, str, str]:
    """Separate runner success from the generated task's TaskOutcome."""
    status, message = extract_runner_task_outcome(payload)
    runner_ok = bool(isinstance(payload, Mapping) and payload.get("ok"))
    if not runner_ok or int(returncode) != 0:
        return False, "ui_task_failed", status, message
    events = {
        "succeeded": "ui_task_completed",
        "partially_succeeded": "ui_task_partially_succeeded",
        "failed": "ui_task_failed",
        "canceled": "ui_task_canceled",
        "timed_out": "ui_task_timed_out",
    }
    event = events.get(status)
    if event is None:
        return (
            False,
            "ui_task_failed",
            status,
            message or "runner finished without a recognized TaskOutcome status",
        )
    return status == "succeeded", event, status, message

@dataclass(frozen=True)
class TaskRequest:
    request_id: str
    mode: str
    code: str
    source_sha256: str
    approved: bool
    metadata: dict[str, Any]


def normalized_source(source: str) -> str:
    return source.rstrip() + "\n"


def source_sha256(source: str) -> str:
    return hashlib.sha256(normalized_source(source).encode("utf-8")).hexdigest()


def make_task_request(
    *,
    request_id: str,
    mode: str,
    code: str,
    approved: bool,
    metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    normalized = normalized_source(code)
    return {
        "schema": TASK_REQUEST_SCHEMA,
        "request_id": request_id,
        "mode": mode,
        "code": normalized,
        "source_sha256": hashlib.sha256(normalized.encode("utf-8")).hexdigest(),
        "approved": bool(approved),
        "metadata": dict(metadata or {}),
        "created_at_unix_ms": int(time.time() * 1000),
    }


def parse_task_request(payload: Mapping[str, Any], *, max_code_bytes: int) -> TaskRequest:
    if payload.get("schema") != TASK_REQUEST_SCHEMA:
        raise ProtocolError("unsupported task request schema")
    request_id = str(payload.get("request_id", "")).strip()
    if not REQUEST_ID_PATTERN.fullmatch(request_id):
        raise ProtocolError("invalid request_id")
    mode = str(payload.get("mode", "")).strip().lower()
    if mode not in {"validate", "execute"}:
        raise ProtocolError("mode must be validate or execute")
    code = payload.get("code")
    if not isinstance(code, str) or not code.strip():
        raise ProtocolError("code is required")
    normalized = normalized_source(code)
    if len(normalized.encode("utf-8")) > int(max_code_bytes):
        raise ProtocolError("code exceeds max_code_bytes")
    expected_hash = source_sha256(normalized)
    supplied_hash = str(payload.get("source_sha256", "")).strip().lower()
    if supplied_hash != expected_hash:
        raise ProtocolError("source_sha256 mismatch")
    metadata = payload.get("metadata", {})
    if not isinstance(metadata, dict):
        raise ProtocolError("metadata must be an object")
    return TaskRequest(
        request_id=request_id,
        mode=mode,
        code=normalized,
        source_sha256=expected_hash,
        approved=bool(payload.get("approved", False)),
        metadata=dict(metadata),
    )


def parse_json_object(raw: str) -> dict[str, Any] | None:
    try:
        value = json.loads(raw)
    except (TypeError, ValueError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def compact_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(dict(payload), ensure_ascii=False, separators=(",", ":"))


def extract_last_json_object(text: str) -> dict[str, Any] | None:
    """Extract the final top-level JSON object from runner output.

    ``robot_code_runner`` prints indented JSON.  Scanning every opening brace and
    returning the last decodable value would accidentally return the deepest
    nested dictionary, so candidates are ranked by their absolute end position
    and then by the earliest start at that end position.
    """
    stripped = text.strip()
    if not stripped:
        return None
    try:
        direct = json.loads(stripped)
    except json.JSONDecodeError:
        direct = None
    if isinstance(direct, dict):
        return direct

    decoder = json.JSONDecoder()
    candidates: list[tuple[int, int, dict[str, Any]]] = []
    for index, char in enumerate(text):
        if char != "{":
            continue
        try:
            value, relative_end = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            candidates.append((index + relative_end, index, value))
    if not candidates:
        return None
    final_end = max(item[0] for item in candidates)
    finalists = [item for item in candidates if item[0] == final_end]
    return min(finalists, key=lambda item: item[1])[2]


def is_terminal_event(payload: Mapping[str, Any]) -> bool:
    return str(payload.get("event", "")) in TERMINAL_EVENTS
