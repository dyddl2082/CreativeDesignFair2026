from __future__ import annotations

import re

from .models import ParsedResponse, ResponseStatus


_STATUS_PATTERN = re.compile(
    r"^STATUS:\s*(CODE|NEED_CLARIFICATION|UNSUPPORTED|GENERATION_ERROR)\s*$",
    re.MULTILINE,
)


def parse_response(raw_text: str) -> ParsedResponse:
    match = _STATUS_PATTERN.search(raw_text)
    if not match:
        return ParsedResponse(
            status=ResponseStatus.GENERATION_ERROR,
            raw_text=raw_text,
            question_or_reason="응답 첫 줄에서 유효한 STATUS를 찾지 못했습니다.",
            format_error="유효한 STATUS 형식이 아닙니다.",
        )

    status = ResponseStatus.from_text(match.group(1))
    if status == ResponseStatus.CODE:
        bindings = _section(raw_text, "OBJECT_BINDINGS", ("ASSUMPTIONS", "CODE"))
        assumptions = _section(raw_text, "ASSUMPTIONS", ("CODE",))
        code = _extract_code(raw_text)
        if not code:
            return ParsedResponse(
                status=ResponseStatus.GENERATION_ERROR,
                raw_text=raw_text,
                object_bindings=bindings,
                assumptions=assumptions,
                question_or_reason="CODE 응답에 Python 코드 블록이 없습니다.",
                format_error="CODE 섹션의 Python 코드 블록을 찾지 못했습니다.",
            )
        return ParsedResponse(
            status=status,
            raw_text=raw_text,
            object_bindings=bindings,
            assumptions=assumptions,
            code=code,
        )

    label = "QUESTION" if status == ResponseStatus.NEED_CLARIFICATION else "REASON"
    return ParsedResponse(
        status=status,
        raw_text=raw_text,
        question_or_reason=_section(raw_text, label, tuple()),
    )


def _section(text: str, label: str, next_labels: tuple[str, ...]) -> str:
    boundary = "|".join(re.escape(item) for item in next_labels)
    if boundary:
        pattern = rf"(?ms)^{re.escape(label)}:\s*\n(.*?)(?=^(?:{boundary}):|\Z)"
    else:
        pattern = rf"(?ms)^{re.escape(label)}:\s*\n(.*?)(?=^\w[\w_ ]*:\s*\n|\Z)"
    match = re.search(pattern, text)
    return match.group(1).strip() if match else ""


def _extract_code(text: str) -> str:
    match = re.search(
        r"(?ms)^CODE:\s*\n.*?^```python\s*\n(.*?)^```\s*$",
        text,
    )
    return match.group(1).strip() if match else ""
