from macrobot_ui.models import ResponseStatus
from macrobot_ui.response_parser import parse_response


def test_parse_code_response():
    parsed = parse_response(
        """STATUS: CODE

OBJECT_BINDINGS:
- 지우개 -> ObjectId.ERASER

ASSUMPTIONS:
- 없음

CODE:

```python
def main() -> TaskOutcome:
    return TaskOutcome(status=TaskStatus.SUCCEEDED)
```
"""
    )
    assert parsed.status == ResponseStatus.CODE
    assert "def main" in parsed.code
    assert "ObjectId.ERASER" in parsed.object_bindings


def test_missing_status_fails_closed():
    parsed = parse_response("hello")
    assert parsed.status == ResponseStatus.GENERATION_ERROR
    assert parsed.format_error
