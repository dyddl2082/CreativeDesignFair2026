from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class ResponseStatus(str, Enum):
    CODE = "CODE"
    NEED_CLARIFICATION = "NEED_CLARIFICATION"
    UNSUPPORTED = "UNSUPPORTED"
    GENERATION_ERROR = "GENERATION_ERROR"

    @classmethod
    def from_text(cls, value: str | None) -> "ResponseStatus":
        normalized = str(value or "").strip().upper()
        for status in cls:
            if status.value == normalized:
                return status
        return cls.GENERATION_ERROR


@dataclass(frozen=True)
class ChatTurn:
    role: str
    text: str


@dataclass(frozen=True)
class ParsedResponse:
    status: ResponseStatus
    raw_text: str
    object_bindings: str = ""
    assumptions: str = ""
    code: str = ""
    question_or_reason: str = ""
    format_error: str | None = None

    @property
    def is_code(self) -> bool:
        return self.status == ResponseStatus.CODE and bool(self.code.strip())


@dataclass(frozen=True)
class ValidationIssue:
    message: str
    line: int | None = None
    column: int | None = None
    code: str = ""
    severity: str = "error"

    def display(self) -> str:
        location = ""
        if self.line is not None:
            location = f"{self.line}행"
            if self.column is not None:
                location += f" {self.column}열"
            location += ": "
        prefix = f"[{self.code}] " if self.code else ""
        return f"{location}{prefix}{self.message}"


@dataclass(frozen=True)
class ValidationReport:
    issues: tuple[ValidationIssue, ...] = field(default_factory=tuple)
    validator_name: str = "bundled"
    robot_calls: tuple[str, ...] = field(default_factory=tuple)

    @property
    def is_valid(self) -> bool:
        return not any(issue.severity == "error" for issue in self.issues)

    @property
    def summary(self) -> str:
        source = (
            "Action Gateway validator"
            if self.validator_name == "gateway"
            else "UI bundled validator"
        )
        if self.is_valid:
            return (
                f"{source} 검증을 통과했습니다. "
                "실행 시 Pi 백엔드와 Action Gateway가 같은 소스를 다시 검증합니다."
            )
        return f"{source}에서 수정이 필요한 항목을 찾았습니다."


@dataclass(frozen=True)
class StoredTask:
    code_path: Path
    metadata_path: Path
    source_sha256: str


@dataclass(frozen=True)
class BackendState:
    reachable: bool = False
    allow_execution: bool = False
    gateway_reachable: bool = False
    gateway_real_motion_enabled: bool = False
    active_request_id: str = ""
    detail: str = "백엔드 대기"
    raw: dict[str, Any] = field(default_factory=dict)
