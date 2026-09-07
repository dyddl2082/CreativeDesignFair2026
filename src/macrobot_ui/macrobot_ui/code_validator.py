from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

import yaml

from .models import ValidationIssue, ValidationReport


class GeneratedCodeValidator:
    """Use the installed Action Gateway validator, with a source-only fallback."""

    def __init__(self, bundle_path: Path) -> None:
        self._fallback = _BundleValidator(bundle_path)

    def validate(self, code: str) -> ValidationReport:
        try:
            from macrobot_action_gateway.ast_validator import validate_source
        except Exception:
            return self._fallback.validate(code)

        try:
            _tree, report = validate_source(code)
        except Exception as exc:
            return ValidationReport(
                issues=(
                    ValidationIssue(
                        message=f"Action Gateway validator 호출 실패: {type(exc).__name__}: {exc}",
                        code="VALIDATOR_ERROR",
                    ),
                ),
                validator_name="gateway",
            )

        converted: list[ValidationIssue] = []
        for issue in getattr(report, "issues", ()):
            converted.append(
                ValidationIssue(
                    message=str(getattr(issue, "message", issue)),
                    line=_optional_int(getattr(issue, "line", None)),
                    column=_optional_int(getattr(issue, "column", None)),
                    code=str(getattr(issue, "code", "")),
                    severity=str(getattr(issue, "severity", "error")),
                )
            )
        robot_calls = tuple(str(item) for item in getattr(report, "robot_calls", ()))
        return ValidationReport(
            issues=tuple(converted),
            validator_name="gateway",
            robot_calls=robot_calls,
        )


def _optional_int(value: Any) -> int | None:
    try:
        return None if value is None else int(value)
    except (TypeError, ValueError):
        return None


class _BundleValidator(ast.NodeVisitor):
    """Conservative fallback for a UI machine without action_gateway imports."""

    _FORBIDDEN_NODES = (
        ast.Import,
        ast.ImportFrom,
        ast.Try,
        ast.AsyncFunctionDef,
        ast.AsyncFor,
        ast.Await,
        ast.ClassDef,
        ast.Lambda,
        ast.With,
        ast.AsyncWith,
        ast.Global,
        ast.Nonlocal,
        ast.Raise,
        ast.Yield,
        ast.YieldFrom,
        ast.Delete,
        ast.Assert,
    )

    def __init__(self, bundle_path: Path) -> None:
        bundle = yaml.safe_load(Path(bundle_path).read_text(encoding="utf-8")) or {}
        self._allowed_robot_functions = set((bundle.get("functions") or {}).keys())
        contract = bundle.get("code_contract") or {}
        self._allowed_builtins = set(contract.get("allowed_builtins") or [])
        self._forbidden_names = set(contract.get("forbidden_names") or [])
        self._enum_members = {
            enum_name: set((spec or {}).get("values", {}).keys())
            for enum_name, spec in (bundle.get("enums") or {}).items()
        }
        self._allowed_result_fields = {
            field_name
            for spec in (bundle.get("types") or {}).values()
            for field_name in (spec or {}).get("fields", {}).keys()
        }
        self._issues: list[ValidationIssue] = []
        self._defined_functions: set[str] = set()
        self._function_stack: list[str] = []

    def validate(self, code: str) -> ValidationReport:
        self._issues = []
        self._defined_functions = set()
        self._function_stack = []
        try:
            tree = ast.parse(code)
        except SyntaxError as error:
            return ValidationReport(
                issues=(
                    ValidationIssue(
                        message=error.msg,
                        line=error.lineno,
                        column=error.offset,
                        code="SYNTAX_ERROR",
                    ),
                ),
                validator_name="bundled",
            )

        self._defined_functions = {
            node.name for node in tree.body if isinstance(node, ast.FunctionDef)
        }
        mains = [
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "main"
        ]
        if len(mains) != 1:
            self._error("main 함수는 정확히 하나여야 합니다.", code="MAIN_CONTRACT")
        elif mains[0].args.args or mains[0].args.kwonlyargs:
            self._error(
                "main 함수는 인자를 받으면 안 됩니다.",
                mains[0],
                code="MAIN_CONTRACT",
            )
        elif not _is_task_outcome_annotation(mains[0].returns):
            self._error(
                "main의 반환 형식은 TaskOutcome이어야 합니다.",
                mains[0],
                code="MAIN_CONTRACT",
            )

        for node in tree.body:
            if not isinstance(node, ast.FunctionDef):
                self._error(
                    "최상위에는 함수 정의만 둘 수 있습니다.",
                    node,
                    code="TOP_LEVEL_CODE",
                )

        self.visit(tree)
        return ValidationReport(
            issues=tuple(self._issues),
            validator_name="bundled",
        )

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if node.decorator_list:
            self._error("데코레이터는 사용할 수 없습니다.", node)
        self._function_stack.append(node.name)
        self.generic_visit(node)
        self._function_stack.pop()

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name):
            name = node.func.id
            if name in self._forbidden_names:
                self._error(f"{name} 호출은 허용되지 않습니다.", node)
            elif name not in self._allowed_builtins | self._defined_functions | {
                "TaskOutcome"
            }:
                self._error(f"허용되지 않은 함수 호출입니다: {name}", node)
        elif isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id == "robot":
                if node.func.attr not in self._allowed_robot_functions:
                    self._error(
                        f"등록되지 않은 Robot API입니다: robot.{node.func.attr}",
                        node,
                    )
            else:
                self._error("robot facade 이외의 객체 메서드 호출은 허용되지 않습니다.", node)
        else:
            self._error("허용되지 않은 호출 형식입니다.", node)
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr.startswith("_"):
            self._error("private/dunder 속성 접근은 허용되지 않습니다.", node)
        elif isinstance(node.value, ast.Name):
            owner = node.value.id
            if owner == "robot" and node.attr not in self._allowed_robot_functions:
                self._error(f"등록되지 않은 Robot API입니다: robot.{node.attr}", node)
            elif owner in self._enum_members and node.attr not in self._enum_members[owner]:
                self._error(f"등록되지 않은 enum 값입니다: {owner}.{node.attr}", node)
            elif (
                owner not in {"robot"} | set(self._enum_members)
                and node.attr not in self._allowed_result_fields
            ):
                self._error(f"허용되지 않은 필드 접근입니다: .{node.attr}", node)
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        if node.id in self._forbidden_names:
            self._error(f"{node.id} 사용은 허용되지 않습니다.", node)

    def visit_Return(self, node: ast.Return) -> None:
        if self._function_stack and self._function_stack[-1] == "main":
            valid = (
                isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Name)
                and node.value.func.id == "TaskOutcome"
            )
            if not valid:
                self._error("main의 return은 TaskOutcome(...)이어야 합니다.", node)
        self.generic_visit(node)

    def generic_visit(self, node: ast.AST) -> None:
        if isinstance(node, self._FORBIDDEN_NODES):
            self._error(f"허용되지 않은 구문입니다: {type(node).__name__}", node)
        super().generic_visit(node)

    def _error(
        self,
        message: str,
        node: ast.AST | None = None,
        *,
        code: str = "UI_CONTRACT",
    ) -> None:
        self._issues.append(
            ValidationIssue(
                message=message,
                line=getattr(node, "lineno", None) if node else None,
                column=getattr(node, "col_offset", None) if node else None,
                code=code,
            )
        )


def _is_task_outcome_annotation(annotation: ast.expr | None) -> bool:
    return isinstance(annotation, ast.Name) and annotation.id == "TaskOutcome"
