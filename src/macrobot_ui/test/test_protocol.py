from __future__ import annotations

import pytest

from macrobot_ui.ros_protocol import (
    ProtocolError,
    extract_last_json_object,
    make_task_request,
    parse_task_request,
)


CODE = """def main() -> TaskOutcome:\n    return TaskOutcome(status=TaskStatus.SUCCEEDED)\n"""


def test_request_hash_round_trip():
    payload = make_task_request(
        request_id="ui-validate-1",
        mode="validate",
        code=CODE,
        approved=False,
        metadata={"request": "test"},
    )
    request = parse_task_request(payload, max_code_bytes=10000)
    assert request.request_id == "ui-validate-1"
    assert request.mode == "validate"
    assert request.code.endswith("\n")
    assert request.source_sha256 == payload["source_sha256"]


def test_tampered_source_is_rejected():
    payload = make_task_request(
        request_id="ui-execute-1",
        mode="execute",
        code=CODE,
        approved=True,
    )
    payload["code"] += "# changed\n"
    with pytest.raises(ProtocolError, match="source_sha256"):
        parse_task_request(payload, max_code_bytes=10000)


def test_extract_final_runner_json():
    text = (
        'warning\n{"valid": true}\ntrailing\n'
        '{"ok": false, "result": {"message": "x", "detail": {"n": 1}}}\n'
    )
    assert extract_last_json_object(text) == {
        "ok": False,
        "result": {"message": "x", "detail": {"n": 1}},
    }
