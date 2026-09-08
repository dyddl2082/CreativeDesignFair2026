from macrobot_ui.ros_protocol import (
    HELD_RESET_REQUEST_SCHEMA,
    classify_runner_execution,
    extract_runner_task_outcome,
)


def test_v45_failed_task_is_not_runner_success():
    payload = {
        "ok": True,
        "task_status": "failed",
        "task_message": "already holding object",
    }
    ok, event, status, message = classify_runner_execution(payload, 0)
    assert ok is False
    assert event == "ui_task_failed"
    assert status == "failed"
    assert message == "already holding object"


def test_v45_legacy_wire_outcome_is_understood():
    payload = {
        "ok": True,
        "outcome": {
            "status": {"__enum__": "TaskStatus", "value": "partially_succeeded"},
            "message": "pick succeeded, place failed",
        },
    }
    assert extract_runner_task_outcome(payload) == (
        "partially_succeeded",
        "pick succeeded, place failed",
    )
    ok, event, status, _ = classify_runner_execution(payload, 0)
    assert ok is False
    assert event == "ui_task_partially_succeeded"
    assert status == "partially_succeeded"


def test_v45_success_is_success():
    payload = {"ok": True, "task_status": "succeeded", "task_message": "done"}
    assert classify_runner_execution(payload, 0)[:3] == (
        True,
        "ui_task_completed",
        "succeeded",
    )


def test_v45_held_reset_schema_is_versioned():
    assert HELD_RESET_REQUEST_SCHEMA == "macrobot.ui.held_reset_request/v1"
