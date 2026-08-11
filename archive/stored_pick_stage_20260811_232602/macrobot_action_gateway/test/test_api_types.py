from macrobot_action_gateway.api_types import (
    ActionHandle,
    ActionResult,
    ActionState,
    ObjectId,
    ObjectState,
    ObjectStateResult,
    from_wire,
    to_wire,
)


def test_wire_round_trip_nested_types():
    result = ObjectStateResult(
        run_id="run-1",
        object_id=ObjectId.BUDS3,
        state=ObjectState.VISIBLE,
        confidence=0.8,
        observed_at_unix_ms=10,
        checked_at_unix_ms=11,
        error_code=None,
        error_message=None,
    )
    restored = from_wire(to_wire(result))
    assert restored == result


def test_action_result_round_trip():
    value = ActionResult(
        action_id="a",
        action_name="MOVE_BASE",
        run_id="r",
        state=ActionState.SUCCEEDED,
        error_code=None,
        error_message=None,
        started_at_unix_ms=1,
        finished_at_unix_ms=2,
        duration_ms=1,
    )
    assert from_wire(to_wire(value)) == value
