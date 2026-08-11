from macrobot_action_gateway.ast_validator import compile_validated_source, validate_source


GOOD = '''
def helper(distance):
    action = robot.MOVE_BASE(distance_m=distance)
    return robot.WAIT_ACTION(action, timeout_s=10.0)

def main() -> TaskOutcome:
    result = helper(0.2)
    if result.state != ActionState.SUCCEEDED:
        return TaskOutcome(TaskStatus.FAILED, result.error_message or "failed")
    return TaskOutcome(TaskStatus.SUCCEEDED, "done")
'''


def test_valid_program():
    _, report = validate_source(GOOD)
    assert report.valid, report.summary()
    assert "MOVE_BASE" in report.robot_calls
    compile_validated_source(GOOD)


def test_import_is_rejected():
    _, report = validate_source("import os\n\ndef main() -> TaskOutcome:\n    return TaskOutcome(TaskStatus.SUCCEEDED, 'x')\n")
    assert not report.valid
    assert any(issue.code == "TOP_LEVEL_CODE" or issue.code == "FORBIDDEN_SYNTAX" for issue in report.issues)


def test_non_robot_method_is_rejected():
    _, report = validate_source("def main() -> TaskOutcome:\n    x = 'abc'.upper()\n    return TaskOutcome(TaskStatus.SUCCEEDED, x)\n")
    assert not report.valid
    assert any(issue.code == "METHOD_CALL_FORBIDDEN" for issue in report.issues)


def test_recursion_is_rejected():
    source = '''
def f():
    return f()

def main() -> TaskOutcome:
    f()
    return TaskOutcome(TaskStatus.SUCCEEDED, "x")
'''
    _, report = validate_source(source)
    assert not report.valid
    assert any(issue.code == "RECURSION_FORBIDDEN" for issue in report.issues)


def test_robot_private_attribute_is_rejected():
    source = '''
def main() -> TaskOutcome:
    value = robot._client
    return TaskOutcome(TaskStatus.SUCCEEDED, str(value))
'''
    _, report = validate_source(source)
    assert not report.valid
    assert any(issue.code in {"PRIVATE_ATTRIBUTE_FORBIDDEN", "ROBOT_ATTRIBUTE_FORBIDDEN"} for issue in report.issues)


def test_result_fields_and_enum_members_are_allowed():
    source = '''
def main() -> TaskOutcome:
    action = robot.MOVE_BASE(distance_m=0.1)
    result = robot.WAIT_ACTION(action, timeout_s=5.0)
    if result.state != ActionState.SUCCEEDED:
        return TaskOutcome(TaskStatus.FAILED, result.error_message or "failed")
    return TaskOutcome(TaskStatus.SUCCEEDED, "done")
'''
    _, report = validate_source(source)
    assert report.valid, report.summary()


def test_discarded_async_handle_is_rejected():
    source = '''
def main() -> TaskOutcome:
    robot.MOVE_BASE(distance_m=0.1)
    return TaskOutcome(TaskStatus.SUCCEEDED, "bad")
'''
    _, report = validate_source(source)
    assert not report.valid
    assert any(issue.code == "ASYNC_HANDLE_REQUIRED" for issue in report.issues)


def test_assigned_but_unmanaged_async_handle_is_rejected():
    source = '''
def main() -> TaskOutcome:
    action = robot.MOVE_BASE(distance_m=0.1)
    return TaskOutcome(TaskStatus.SUCCEEDED, "bad")
'''
    _, report = validate_source(source)
    assert not report.valid
    assert any(issue.code == "ASYNC_ACTION_UNMANAGED" for issue in report.issues)
