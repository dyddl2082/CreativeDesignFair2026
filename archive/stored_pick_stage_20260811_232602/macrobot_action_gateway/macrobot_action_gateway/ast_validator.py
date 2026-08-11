from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import Iterable

from .gateway_runtime import ASYNC_FUNCTIONS, PUBLIC_FUNCTIONS


ALLOWED_BUILTIN_CALLS = {
    "abs",
    "bool",
    "dict",
    "enumerate",
    "float",
    "int",
    "len",
    "list",
    "max",
    "min",
    "range",
    "round",
    "str",
    "sum",
    "tuple",
}

ALLOWED_CONSTRUCTORS = {"TaskOutcome"}
INJECTED_NAMES = {
    "robot",
    "TaskStatus",
    "TaskOutcome",
    "ActionState",
    "ActionHandle",
    "ActionResult",
    "OperationResult",
    "ResourceId",
    "ObjectId",
    "ObjectState",
    "ObjectStateResult",
    "EstimateState",
    "StateSource",
    "RobotSnapshotState",
    "RobotPosResult",
}


ENUM_MEMBERS = {
    "TaskStatus": {"SUCCEEDED", "PARTIALLY_SUCCEEDED", "FAILED", "CANCELED", "TIMED_OUT"},
    "ActionState": {"PENDING", "RUNNING", "CANCEL_REQUESTED", "SUCCEEDED", "FAILED", "CANCELED", "TIMED_OUT"},
    "ResourceId": {"BASE_MOTION", "ARM_MOTION", "GRIPPER_MOTION", "PICO_MOTION", "POSITION_STORE", "ARM_PRIMITIVE_STORE"},
    "ObjectId": {"BUDS3", "CUP"},
    "ObjectState": {"VISIBLE", "NOT_VISIBLE", "AMBIGUOUS", "STALE", "PERCEPTION_UNAVAILABLE", "UNKNOWN"},
    "EstimateState": {"VALID", "TRANSIENT", "UNRELIABLE", "UNAVAILABLE"},
    "StateSource": {"COMMAND_HISTORY", "COMMANDED_STATE", "MEASURED_STATE"},
    "RobotSnapshotState": {"COMPLETE", "PARTIAL", "UNAVAILABLE"},
}

READ_ONLY_RESULT_FIELDS = {
    "status", "message", "data",
    "action_id", "action_name", "run_id", "state", "error_code", "error_message",
    "started_at_unix_ms", "finished_at_unix_ms", "duration_ms",
    "function_name", "success",
    "object_id", "confidence", "observed_at_unix_ms", "checked_at_unix_ms",
    "snapshot_state", "captured_at_unix_ms",
    "x_m", "y_m", "yaw_deg", "base_state", "base_source", "base_updated_at_unix_ms",
    "arm_lift_deg", "wrist_pitch_deg", "arm_state", "arm_source", "arm_updated_at_unix_ms",
    "gripper_deg", "gripper_state", "gripper_source", "gripper_updated_at_unix_ms",
}

FORBIDDEN_NODES = (
    ast.Import,
    ast.ImportFrom,
    ast.ClassDef,
    ast.Lambda,
    ast.AsyncFunctionDef,
    ast.Await,
    ast.Try,
    ast.With,
    ast.AsyncWith,
    ast.Global,
    ast.Nonlocal,
    ast.Yield,
    ast.YieldFrom,
    ast.Raise,
    ast.Delete,
    ast.NamedExpr,
    ast.Assert,
    ast.ListComp,
    ast.SetComp,
    ast.DictComp,
    ast.GeneratorExp,
)


@dataclass(frozen=True)
class ValidationIssue:
    line: int
    column: int
    code: str
    message: str


@dataclass(frozen=True)
class ValidationReport:
    valid: bool
    issues: tuple[ValidationIssue, ...]
    function_names: tuple[str, ...]
    robot_calls: tuple[str, ...]

    def summary(self) -> str:
        if self.valid:
            return "validated"
        return "\n".join(
            f"L{issue.line}:{issue.column} {issue.code}: {issue.message}"
            for issue in self.issues
        )


class _Validator(ast.NodeVisitor):
    def __init__(self, *, max_source_chars: int, max_ast_nodes: int) -> None:
        self.max_source_chars = max_source_chars
        self.max_ast_nodes = max_ast_nodes
        self.issues: list[ValidationIssue] = []
        self.function_names: set[str] = set()
        self.robot_calls: list[str] = []
        self.call_graph: dict[str, set[str]] = {}
        self.current_function: str | None = None
        self.node_count = 0
        self._registered_async_calls: set[int] = set()
        self._async_handles: dict[str, dict[str, ast.AST]] = {}
        self._managed_async_handles: dict[str, set[str]] = {}

    def issue(self, node: ast.AST, code: str, message: str) -> None:
        self.issues.append(
            ValidationIssue(
                line=int(getattr(node, "lineno", 0) or 0),
                column=int(getattr(node, "col_offset", 0) or 0),
                code=code,
                message=message,
            )
        )

    def generic_visit(self, node: ast.AST) -> None:
        self.node_count += 1
        if self.node_count > self.max_ast_nodes:
            self.issue(node, "AST_TOO_LARGE", "코드 AST가 허용 크기를 초과했습니다.")
            return
        if isinstance(node, FORBIDDEN_NODES):
            self.issue(node, "FORBIDDEN_SYNTAX", f"{type(node).__name__} 구문은 허용되지 않습니다.")
            return
        super().generic_visit(node)

    def visit_Module(self, node: ast.Module) -> None:
        main_count = 0
        for index, statement in enumerate(node.body):
            if isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Constant) and isinstance(statement.value.value, str):
                if index != 0:
                    self.issue(statement, "TOP_LEVEL_CODE", "모듈 docstring은 첫 문장에만 허용됩니다.")
                continue
            if not isinstance(statement, ast.FunctionDef):
                self.issue(statement, "TOP_LEVEL_CODE", "모듈 최상위에는 함수 정의만 허용됩니다.")
                continue
            self.function_names.add(statement.name)
            if statement.name == "main":
                main_count += 1
        if main_count != 1:
            self.issue(node, "MAIN_CONTRACT", "def main() -> TaskOutcome 진입점이 정확히 하나 필요합니다.")
        for statement in node.body:
            if isinstance(statement, ast.FunctionDef):
                self.visit(statement)
        self._check_recursion(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if node.decorator_list:
            self.issue(node, "DECORATOR_FORBIDDEN", "함수 decorator는 허용되지 않습니다.")
        if node.args.defaults or any(item is not None for item in node.args.kw_defaults):
            self.issue(node, "DEFAULT_ARGUMENT_FORBIDDEN", "함수 default argument는 모듈 로드 시 실행될 수 있어 허용되지 않습니다.")
        if node.name.startswith("__"):
            self.issue(node, "DUNDER_FORBIDDEN", "dunder 함수 이름은 허용되지 않습니다.")
        if node.name == "main":
            if node.args.args or node.args.posonlyargs or node.args.kwonlyargs or node.args.vararg or node.args.kwarg:
                self.issue(node, "MAIN_CONTRACT", "main은 인자를 받을 수 없습니다.")
            annotation = node.returns
            if not isinstance(annotation, ast.Name) or annotation.id != "TaskOutcome":
                self.issue(node, "MAIN_CONTRACT", "main 반환 annotation은 TaskOutcome이어야 합니다.")
        previous = self.current_function
        self.current_function = node.name
        self.call_graph.setdefault(node.name, set())
        for statement in node.body:
            self.visit(statement)
        handles = self._async_handles.get(node.name, {})
        managed = self._managed_async_handles.get(node.name, set())
        for handle_name, handle_node in handles.items():
            if handle_name not in managed:
                self.issue(
                    handle_node,
                    "ASYNC_ACTION_UNMANAGED",
                    f"비동기 액션 handle '{handle_name}'은 WAIT_ACTION, CANCEL_ACTION, CANCEL_ALL 또는 STOP으로 종료를 관리해야 합니다.",
                )
        self.current_function = previous

    @staticmethod
    def _robot_call_name(node: ast.AST) -> str | None:
        if not isinstance(node, ast.Call):
            return None
        target = node.func
        if (
            isinstance(target, ast.Attribute)
            and isinstance(target.value, ast.Name)
            and target.value.id == "robot"
        ):
            return target.attr
        return None

    def visit_Assign(self, node: ast.Assign) -> None:
        call_name = self._robot_call_name(node.value)
        if call_name in ASYNC_FUNCTIONS:
            if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
                self.issue(node, "ASYNC_HANDLE_REQUIRED", "비동기 Robot API 반환값은 하나의 단순 변수에 저장해야 합니다.")
            else:
                variable = node.targets[0].id
                function = self.current_function or "<module>"
                self._registered_async_calls.add(id(node.value))
                self._async_handles.setdefault(function, {})[variable] = node
        for target in node.targets:
            self.visit(target)
        self.visit(node.value)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        call_name = self._robot_call_name(node.value) if node.value is not None else None
        if call_name in ASYNC_FUNCTIONS:
            if not isinstance(node.target, ast.Name):
                self.issue(node, "ASYNC_HANDLE_REQUIRED", "비동기 Robot API 반환값은 하나의 단순 변수에 저장해야 합니다.")
            else:
                variable = node.target.id
                function = self.current_function or "<module>"
                self._registered_async_calls.add(id(node.value))
                self._async_handles.setdefault(function, {})[variable] = node
        self.visit(node.target)
        if node.annotation is not None:
            self.visit(node.annotation)
        if node.value is not None:
            self.visit(node.value)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr.startswith("_") or "__" in node.attr:
            self.issue(node, "PRIVATE_ATTRIBUTE_FORBIDDEN", "private/dunder attribute 접근은 허용되지 않습니다.")
            return
        if isinstance(node.value, ast.Name) and node.value.id == "robot":
            # ``robot.<API>(...)`` is handled by visit_Call.  Merely reading a
            # facade method or internal facade attribute is not part of the
            # generated-code contract.
            self.issue(node, "ROBOT_ATTRIBUTE_FORBIDDEN", "robot facade는 공개 API 호출 형태로만 사용할 수 있습니다.")
            return
        if isinstance(node.value, ast.Name) and node.value.id in ENUM_MEMBERS:
            if node.attr not in ENUM_MEMBERS[node.value.id]:
                self.issue(node, "ENUM_MEMBER_FORBIDDEN", f"허용되지 않은 enum member입니다: {node.value.id}.{node.attr}")
            return
        if node.attr not in READ_ONLY_RESULT_FIELDS:
            self.issue(node, "ATTRIBUTE_FORBIDDEN", f"허용되지 않은 read-only field입니다: {node.attr}")
            return
        self.visit(node.value)

    def visit_Call(self, node: ast.Call) -> None:
        target = node.func
        if isinstance(target, ast.Attribute):
            if isinstance(target.value, ast.Name) and target.value.id == "robot":
                if target.attr not in PUBLIC_FUNCTIONS:
                    self.issue(node, "UNKNOWN_ROBOT_API", f"지원하지 않는 robot API입니다: {target.attr}")
                else:
                    self.robot_calls.append(target.attr)
                    if target.attr in ASYNC_FUNCTIONS and id(node) not in self._registered_async_calls:
                        self.issue(node, "ASYNC_HANDLE_REQUIRED", "비동기 Robot API 반환값은 ActionHandle 변수에 저장해야 합니다.")
                    function = self.current_function or "<module>"
                    if target.attr in {"WAIT_ACTION", "CANCEL_ACTION"} and node.args:
                        first = node.args[0]
                        if isinstance(first, ast.Name):
                            self._managed_async_handles.setdefault(function, set()).add(first.id)
                    elif target.attr in {"CANCEL_ALL", "STOP"}:
                        self._managed_async_handles.setdefault(function, set()).update(
                            self._async_handles.get(function, {}).keys()
                        )
            else:
                self.issue(node, "METHOD_CALL_FORBIDDEN", "robot facade 이외 객체의 메서드 호출은 허용되지 않습니다.")
        elif isinstance(target, ast.Name):
            name = target.id
            if name in self.function_names:
                if self.current_function is not None:
                    self.call_graph.setdefault(self.current_function, set()).add(name)
            elif name not in ALLOWED_BUILTIN_CALLS and name not in ALLOWED_CONSTRUCTORS:
                self.issue(node, "CALL_FORBIDDEN", f"허용되지 않은 함수 호출입니다: {name}")
        else:
            self.issue(node, "CALL_FORBIDDEN", "동적 callable 호출은 허용되지 않습니다.")
        for argument in node.args:
            if isinstance(argument, ast.Starred):
                self.issue(argument, "STAR_ARGS_FORBIDDEN", "*args 호출은 허용되지 않습니다.")
            self.visit(argument)
        for keyword in node.keywords:
            if keyword.arg is None:
                self.issue(keyword, "STAR_ARGS_FORBIDDEN", "**kwargs 호출은 허용되지 않습니다.")
            self.visit(keyword.value)

    def visit_Name(self, node: ast.Name) -> None:
        if node.id.startswith("__") and node.id != "__loop_guard":
            self.issue(node, "DUNDER_FORBIDDEN", "dunder 이름 접근은 허용되지 않습니다.")

    def visit_Constant(self, node: ast.Constant) -> None:
        if isinstance(node.value, (bytes, complex)):
            self.issue(node, "CONSTANT_FORBIDDEN", f"{type(node.value).__name__} literal은 허용되지 않습니다.")
        if isinstance(node.value, str) and len(node.value) > 4096:
            self.issue(node, "STRING_TOO_LARGE", "문자열 literal이 너무 큽니다.")

    def _check_recursion(self, node: ast.AST) -> None:
        visiting: set[str] = set()
        visited: set[str] = set()

        def dfs(name: str) -> bool:
            if name in visiting:
                return True
            if name in visited:
                return False
            visiting.add(name)
            for child in self.call_graph.get(name, set()):
                if child in self.call_graph and dfs(child):
                    return True
            visiting.remove(name)
            visited.add(name)
            return False

        for name in self.call_graph:
            if dfs(name):
                self.issue(node, "RECURSION_FORBIDDEN", "직접 또는 간접 recursion은 허용되지 않습니다.")
                break


class _LoopGuardInjector(ast.NodeTransformer):
    def _guard(self, node: ast.AST) -> ast.Expr:
        guard = ast.Expr(
            value=ast.Call(
                func=ast.Name(id="__loop_guard", ctx=ast.Load()),
                args=[],
                keywords=[],
            )
        )
        return ast.copy_location(guard, node)

    def visit_For(self, node: ast.For):
        self.generic_visit(node)
        node.body.insert(0, self._guard(node))
        return node

    def visit_While(self, node: ast.While):
        self.generic_visit(node)
        node.body.insert(0, self._guard(node))
        return node


def validate_source(
    source: str,
    *,
    max_source_chars: int = 50_000,
    max_ast_nodes: int = 5_000,
) -> tuple[ast.Module | None, ValidationReport]:
    if len(source) > max_source_chars:
        issue = ValidationIssue(0, 0, "SOURCE_TOO_LARGE", "소스 코드가 허용 크기를 초과했습니다.")
        return None, ValidationReport(False, (issue,), (), ())
    try:
        tree = ast.parse(source, mode="exec")
    except SyntaxError as exc:
        issue = ValidationIssue(
            int(exc.lineno or 0),
            int(exc.offset or 0),
            "SYNTAX_ERROR",
            str(exc.msg),
        )
        return None, ValidationReport(False, (issue,), (), ())
    validator = _Validator(
        max_source_chars=max_source_chars,
        max_ast_nodes=max_ast_nodes,
    )
    validator.visit(tree)
    report = ValidationReport(
        valid=not validator.issues,
        issues=tuple(validator.issues),
        function_names=tuple(sorted(validator.function_names)),
        robot_calls=tuple(validator.robot_calls),
    )
    return tree, report


def compile_validated_source(source: str, filename: str = "<approved_robot_code>"):
    tree, report = validate_source(source)
    if tree is None or not report.valid:
        raise ValueError(report.summary())
    transformed = _LoopGuardInjector().visit(tree)
    ast.fix_missing_locations(transformed)
    return compile(transformed, filename, "exec"), report
