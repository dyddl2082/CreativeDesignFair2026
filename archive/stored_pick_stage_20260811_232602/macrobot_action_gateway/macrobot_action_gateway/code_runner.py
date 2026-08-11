from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing as mp
from pathlib import Path
import resource
import secrets
import sys
import time
import traceback
from typing import Any

from .api_types import (
    ActionHandle,
    ActionResult,
    ActionState,
    EstimateState,
    ObjectId,
    ObjectState,
    ObjectStateResult,
    OperationResult,
    ResourceId,
    RobotPosResult,
    RobotSnapshotState,
    StateSource,
    TaskOutcome,
    TaskStatus,
    to_wire,
)
from .ast_validator import compile_validated_source, validate_source
from .gateway_protocol import GatewayRpcClient
from .robot_facade import RobotFacade


SAFE_BUILTINS = {
    "abs": abs,
    "bool": bool,
    "dict": dict,
    "enumerate": enumerate,
    "float": float,
    "int": int,
    "len": len,
    "list": list,
    "max": max,
    "min": min,
    "range": range,
    "round": round,
    "str": str,
    "sum": sum,
    "tuple": tuple,
}


class LoopBudgetExceeded(RuntimeError):
    pass


def _apply_resource_limits(cpu_seconds: int, memory_mb: int, max_output_bytes: int) -> None:
    try:
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds + 1))
    except Exception:
        pass
    try:
        limit = memory_mb * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
    except Exception:
        pass
    try:
        resource.setrlimit(resource.RLIMIT_FSIZE, (max_output_bytes, max_output_bytes))
    except Exception:
        pass
    try:
        resource.setrlimit(resource.RLIMIT_NOFILE, (32, 32))
    except Exception:
        pass


def _worker_entry(
    connection,
    source: str,
    socket_path: str,
    run_id: str,
    loop_budget: int,
    cpu_seconds: int,
    memory_mb: int,
    max_output_bytes: int,
) -> None:
    _apply_resource_limits(cpu_seconds, memory_mb, max_output_bytes)
    client: GatewayRpcClient | None = None
    try:
        code, _ = compile_validated_source(source)
        remaining = int(loop_budget)

        def loop_guard() -> None:
            nonlocal remaining
            remaining -= 1
            if remaining < 0:
                raise LoopBudgetExceeded("반복문 실행 budget을 초과했습니다.")

        client = GatewayRpcClient(socket_path, timeout_s=190.0)
        client.open_run(run_id)
        robot = RobotFacade(client, run_id)
        environment: dict[str, Any] = {
            "__builtins__": SAFE_BUILTINS,
            "__loop_guard": loop_guard,
            "robot": robot,
            "TaskStatus": TaskStatus,
            "TaskOutcome": TaskOutcome,
            "ActionState": ActionState,
            "ActionHandle": ActionHandle,
            "ActionResult": ActionResult,
            "OperationResult": OperationResult,
            "ResourceId": ResourceId,
            "ObjectId": ObjectId,
            "ObjectState": ObjectState,
            "ObjectStateResult": ObjectStateResult,
            "EstimateState": EstimateState,
            "StateSource": StateSource,
            "RobotSnapshotState": RobotSnapshotState,
            "RobotPosResult": RobotPosResult,
        }
        exec(code, environment, environment)
        outcome = environment["main"]()
        if not isinstance(outcome, TaskOutcome):
            raise TypeError("main()은 TaskOutcome을 반환해야 합니다.")

        close_result = client.close_run(run_id)
        if bool(close_result.get("had_active_actions")):
            raise RuntimeError(
                "main()이 비동기 액션이 종료되기 전에 반환했습니다. "
                "모든 의존 액션에 WAIT_ACTION을 사용해야 합니다."
            )
        if not bool(close_result.get("clean_shutdown", False)):
            raise RuntimeError("run 종료 시 로봇 액션의 안전한 정리를 확인하지 못했습니다.")

        connection.send(
            {
                "ok": True,
                "outcome": to_wire(outcome),
                "loop_iterations_used": loop_budget - remaining,
                "close_result": close_result,
            }
        )
    except BaseException as exc:
        abort_result: dict[str, Any] | None = None
        if client is not None:
            try:
                abort_result = client.abort_run(run_id, f"worker_error:{type(exc).__name__}")
            except BaseException as abort_exc:
                abort_result = {
                    "stop_success": False,
                    "abort_error": f"{type(abort_exc).__name__}: {abort_exc}",
                }
        # Stack trace is retained only in the supervisor log, not propagated as a
        # hardware/API error string to generated code.
        connection.send(
            {
                "ok": False,
                "error_type": type(exc).__name__,
                "message": str(exc),
                "traceback": traceback.format_exc(limit=20),
                "abort_result": abort_result,
            }
        )
    finally:
        connection.close()


def _write_run_log(
    root: Path,
    run_id: str,
    payload: dict[str, Any],
) -> Path:
    directory = root.expanduser() / run_id
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "run.json"
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate and execute approved MacRobot LLM code through Robot Action Gateway."
    )
    parser.add_argument("--code", required=True, help="Approved Python source file")
    parser.add_argument("--socket", default="/tmp/macrobot_action_gateway.sock")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument(
        "--approved",
        action="store_true",
        help="Explicit confirmation that the user approved this exact source",
    )
    parser.add_argument("--wall-timeout-s", type=float, default=300.0)
    parser.add_argument("--cpu-seconds", type=int, default=30)
    parser.add_argument("--memory-mb", type=int, default=256)
    parser.add_argument("--loop-budget", type=int, default=1000)
    parser.add_argument("--max-output-bytes", type=int, default=1_000_000)
    parser.add_argument(
        "--log-root",
        default=str(Path.home() / "MacRobot" / "data" / "llm_runs"),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    path = Path(args.code).expanduser().resolve()
    try:
        source = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: source read failed: {exc}", file=sys.stderr)
        return 2

    _, report = validate_source(source)
    validation_payload = {
        "valid": report.valid,
        "issues": [issue.__dict__ for issue in report.issues],
        "function_names": list(report.function_names),
        "robot_calls": list(report.robot_calls),
    }
    if args.validate_only or not args.execute:
        print(json.dumps(validation_payload, ensure_ascii=False, indent=2))
        return 0 if report.valid else 3
    if not report.valid:
        print(json.dumps(validation_payload, ensure_ascii=False, indent=2), file=sys.stderr)
        return 3
    if not args.approved:
        print(
            "ERROR: 실행에는 --approved가 필요합니다. 검토/승인되지 않은 코드는 실행하지 않습니다.",
            file=sys.stderr,
        )
        return 4

    run_id = f"run-{int(time.time() * 1000)}-{secrets.token_hex(4)}"
    source_hash = hashlib.sha256(source.encode("utf-8")).hexdigest()
    started_ms = int(time.time() * 1000)
    client = GatewayRpcClient(args.socket, timeout_s=10.0)
    try:
        client.open_run(run_id)
    except Exception as exc:
        print(f"ERROR: gateway unavailable: {exc}", file=sys.stderr)
        return 5

    parent, child = mp.Pipe(duplex=False)
    process = mp.Process(
        target=_worker_entry,
        args=(
            child,
            source,
            args.socket,
            run_id,
            args.loop_budget,
            args.cpu_seconds,
            args.memory_mb,
            args.max_output_bytes,
        ),
        name=f"macrobot-code-worker-{run_id}",
        daemon=True,
    )
    process.start()
    child.close()

    result: dict[str, Any]
    if parent.poll(timeout=max(0.1, float(args.wall_timeout_s))):
        try:
            result = parent.recv()
        except EOFError:
            result = {
                "ok": False,
                "error_type": "WORKER_EOF",
                "message": "Code Worker가 결과 없이 종료되었습니다.",
            }
        process.join(timeout=2.0)
    else:
        try:
            abort = client.abort_run(run_id, "worker_wall_timeout")
        except Exception as exc:
            abort = {"stop_success": False, "abort_error": str(exc)}
        process.terminate()
        process.join(timeout=2.0)
        result = {
            "ok": False,
            "error_type": "RUN_WALL_TIMEOUT",
            "message": "Code Worker wall-clock timeout",
            "abort_result": abort,
        }

    if not result.get("ok"):
        try:
            supervisor_abort = client.abort_run(run_id, "worker_failed")
        except Exception as exc:
            supervisor_abort = {
                "stop_success": False,
                "abort_error": f"{type(exc).__name__}: {exc}",
            }
        result.setdefault("supervisor_abort_result", supervisor_abort)

    finished_ms = int(time.time() * 1000)
    log_payload = {
        "run_id": run_id,
        "source_path": str(path),
        "source_sha256": source_hash,
        "started_at_unix_ms": started_ms,
        "finished_at_unix_ms": finished_ms,
        "duration_ms": finished_ms - started_ms,
        "validation": validation_payload,
        "result": result,
    }
    log_path = _write_run_log(Path(args.log_root), run_id, log_payload)
    public_result = dict(result)
    public_result.pop("traceback", None)
    public_result["run_id"] = run_id
    public_result["log_path"] = str(log_path)
    print(json.dumps(public_result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 6


if __name__ == "__main__":
    raise SystemExit(main())
