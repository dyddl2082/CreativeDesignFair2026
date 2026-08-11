from __future__ import annotations

from dataclasses import dataclass, field
import threading
import time
import uuid
from collections.abc import Callable, Iterable
from typing import Any

from .api_types import ActionHandle, ActionResult, ActionState, ResourceId
from .resource_manager import ResourceManager
from .state_store import unix_ms


@dataclass
class RunRecord:
    run_id: str
    created_monotonic: float
    max_wall_time_s: float
    max_internal_motion_steps: int
    internal_motion_steps: int = 0
    canceled: bool = False
    stopped: bool = False
    closed: bool = False
    lock: threading.RLock = field(default_factory=threading.RLock, repr=False)

    def interrupted(self) -> bool:
        with self.lock:
            return self.canceled or self.stopped or self.closed or self.wall_timed_out()

    def wall_timed_out(self) -> bool:
        return time.monotonic() - self.created_monotonic > self.max_wall_time_s

    def remaining_motion_steps(self) -> int:
        with self.lock:
            return self.max_internal_motion_steps - self.internal_motion_steps

    def consume_motion_steps(self, count: int = 1) -> bool:
        if count < 0:
            raise ValueError("count must be non-negative")
        with self.lock:
            if self.internal_motion_steps + count > self.max_internal_motion_steps:
                return False
            self.internal_motion_steps += count
            return True


@dataclass
class ActionRecord:
    handle: ActionHandle
    resources: tuple[ResourceId, ...]
    state: ActionState = ActionState.PENDING
    error_code: str | None = None
    error_message: str | None = None
    started_at_unix_ms: int | None = None
    finished_at_unix_ms: int | None = None
    started_monotonic: float | None = None
    finished_monotonic: float | None = None
    cancel_event: threading.Event = field(default_factory=threading.Event, repr=False)
    done_event: threading.Event = field(default_factory=threading.Event, repr=False)
    lock: threading.RLock = field(default_factory=threading.RLock, repr=False)

    def result(self) -> ActionResult:
        with self.lock:
            duration_ms: int | None = None
            if self.started_monotonic is not None and self.finished_monotonic is not None:
                duration_ms = int(
                    max(0.0, self.finished_monotonic - self.started_monotonic) * 1000
                )
            return ActionResult(
                action_id=self.handle.action_id,
                action_name=self.handle.action_name,
                run_id=self.handle.run_id,
                state=self.state,
                error_code=self.error_code,
                error_message=self.error_message,
                started_at_unix_ms=self.started_at_unix_ms,
                finished_at_unix_ms=self.finished_at_unix_ms,
                duration_ms=duration_ms,
            )


Executor = Callable[[ActionRecord, RunRecord], tuple[ActionState, str | None, str | None]]


class ActionManager:
    def __init__(self, resources: ResourceManager) -> None:
        self.resources = resources
        self._lock = threading.RLock()
        self._runs: dict[str, RunRecord] = {}
        self._actions: dict[str, ActionRecord] = {}

    # ------------------------------------------------------------------
    # Runs
    # ------------------------------------------------------------------
    def open_run(
        self,
        run_id: str,
        *,
        max_wall_time_s: float,
        max_internal_motion_steps: int,
    ) -> RunRecord:
        if not run_id:
            raise ValueError("run_id is required")
        with self._lock:
            existing = self._runs.get(run_id)
            if existing is not None and not existing.closed:
                return existing
            record = RunRecord(
                run_id=run_id,
                created_monotonic=time.monotonic(),
                max_wall_time_s=max_wall_time_s,
                max_internal_motion_steps=max_internal_motion_steps,
            )
            self._runs[run_id] = record
            return record

    def get_run(self, run_id: str) -> RunRecord | None:
        with self._lock:
            return self._runs.get(run_id)

    def close_run(self, run_id: str) -> None:
        run = self.get_run(run_id)
        if run is None:
            return
        with run.lock:
            run.closed = True

    def mark_run_canceled(self, run_id: str) -> None:
        run = self.get_run(run_id)
        if run is not None:
            with run.lock:
                run.canceled = True

    def mark_run_stopped(self, run_id: str) -> None:
        run = self.get_run(run_id)
        if run is not None:
            with run.lock:
                run.stopped = True

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def create(
        self,
        run_id: str,
        action_name: str,
        resources: Iterable[ResourceId],
        executor: Executor,
    ) -> ActionHandle:
        handle = ActionHandle(
            action_id=uuid.uuid4().hex,
            action_name=action_name,
            run_id=run_id,
        )
        record = ActionRecord(handle=handle, resources=tuple(resources))
        with self._lock:
            self._actions[handle.action_id] = record
        thread = threading.Thread(
            target=self._execute,
            args=(record, executor),
            name=f"macrobot-action-{action_name}-{handle.action_id[:8]}",
            daemon=True,
        )
        thread.start()
        return handle

    def immediate_failure(
        self,
        run_id: str,
        action_name: str,
        error_code: str,
        error_message: str,
    ) -> ActionHandle:
        def executor(record: ActionRecord, run: RunRecord):
            del record, run
            return ActionState.FAILED, error_code, error_message

        return self.create(run_id, action_name, (), executor)

    def _execute(self, record: ActionRecord, executor: Executor) -> None:
        run = self.get_run(record.handle.run_id)
        if run is None:
            self._finish(
                record,
                ActionState.FAILED,
                "INTERNAL_ERROR",
                "run registry에서 현재 run을 찾을 수 없습니다.",
            )
            return

        with run.lock:
            if run.closed:
                self._finish(record, ActionState.FAILED, "RUN_CANCELED", "run이 종료되었습니다.")
                return
            if run.stopped:
                self._finish(record, ActionState.FAILED, "RUN_STOPPED", "STOP 이후 동일 run에서는 새 motion을 시작할 수 없습니다.")
                return
            if run.canceled:
                self._finish(record, ActionState.CANCELED, "RUN_CANCELED", "run이 취소되었습니다.")
                return
            if run.wall_timed_out():
                self._finish(record, ActionState.TIMED_OUT, "RUN_WALL_TIMEOUT", "run wall-clock 제한을 초과했습니다.")
                return

        if record.resources and not self.resources.acquire(
            record.handle.action_id, record.resources
        ):
            self._finish(
                record,
                ActionState.FAILED,
                "RESOURCE_BUSY",
                "필요한 로봇 자원이 다른 액션에서 사용 중입니다.",
            )
            return

        try:
            with record.lock:
                record.state = ActionState.RUNNING
                record.started_at_unix_ms = unix_ms()
                record.started_monotonic = time.monotonic()
            try:
                state, error_code, error_message = executor(record, run)
            except Exception as exc:  # Gateway implementation boundary, not generated code.
                state = ActionState.FAILED
                error_code = "INTERNAL_ERROR"
                error_message = f"Gateway action executor 오류: {type(exc).__name__}: {exc}"
            self._finish(record, state, error_code, error_message)
        finally:
            self.resources.release(record.handle.action_id)

    def _finish(
        self,
        record: ActionRecord,
        state: ActionState,
        error_code: str | None,
        error_message: str | None,
    ) -> None:
        with record.lock:
            if record.state.terminal:
                return
            record.state = state
            record.error_code = error_code
            record.error_message = error_message
            record.finished_at_unix_ms = unix_ms()
            record.finished_monotonic = time.monotonic()
            record.done_event.set()

    def get_record(self, action_id: str) -> ActionRecord | None:
        with self._lock:
            return self._actions.get(action_id)

    def check(self, handle: ActionHandle, run_id: str) -> ActionResult:
        record = self.get_record(handle.action_id)
        if record is None:
            return ActionResult(
                action_id=handle.action_id,
                action_name=handle.action_name,
                run_id=handle.run_id,
                state=ActionState.FAILED,
                error_code="ACTION_NOT_FOUND",
                error_message="등록되지 않은 action ID입니다.",
                started_at_unix_ms=None,
                finished_at_unix_ms=unix_ms(),
                duration_ms=None,
            )
        if record.handle.run_id != run_id or handle.run_id != run_id:
            return ActionResult(
                action_id=handle.action_id,
                action_name=handle.action_name,
                run_id=handle.run_id,
                state=ActionState.FAILED,
                error_code="ACTION_OWNERSHIP_MISMATCH",
                error_message="현재 run이 소유하지 않은 액션입니다.",
                started_at_unix_ms=None,
                finished_at_unix_ms=unix_ms(),
                duration_ms=None,
            )
        return record.result()

    def wait(
        self,
        handle: ActionHandle,
        run_id: str,
        timeout_s: float,
        *,
        cancel_on_timeout: bool = True,
    ) -> ActionResult:
        record = self.get_record(handle.action_id)
        if record is None or record.handle.run_id != run_id or handle.run_id != run_id:
            return self.check(handle, run_id)
        if record.done_event.wait(timeout=timeout_s):
            return record.result()
        if cancel_on_timeout:
            record.cancel_event.set()
            with record.lock:
                if not record.state.terminal:
                    record.state = ActionState.CANCEL_REQUESTED
            # Give the executor a bounded chance to perform a hardware stop.
            record.done_event.wait(timeout=min(3.0, max(0.2, timeout_s * 0.25)))
            if not record.done_event.is_set():
                self._finish(
                    record,
                    ActionState.TIMED_OUT,
                    "WAIT_TIMEOUT",
                    "WAIT_ACTION timeout 후 액션 취소/정지 확인이 완료되지 않았습니다.",
                )
            elif record.result().state == ActionState.CANCELED:
                # The public contract calls timeout-triggered cancellation TIMED_OUT.
                with record.lock:
                    record.state = ActionState.TIMED_OUT
                    record.error_code = "WAIT_TIMEOUT"
                    record.error_message = "WAIT_ACTION 제한시간을 초과하여 액션을 취소했습니다."
            return record.result()
        return record.result()

    def request_cancel(self, handle: ActionHandle, run_id: str) -> ActionResult:
        record = self.get_record(handle.action_id)
        if record is None or record.handle.run_id != run_id or handle.run_id != run_id:
            return self.check(handle, run_id)
        with record.lock:
            if record.state.terminal:
                return record.result()
            record.state = ActionState.CANCEL_REQUESTED
            record.cancel_event.set()
        record.done_event.wait(timeout=3.0)
        if not record.done_event.is_set():
            self._finish(
                record,
                ActionState.FAILED,
                "SAFE_STOP_UNCONFIRMED",
                "액션 취소 후 안전한 종료를 확인하지 못했습니다.",
            )
        return record.result()

    def cancel_all(self, run_id: str, timeout_s: float) -> bool:
        with self._lock:
            records = [
                record
                for record in self._actions.values()
                if record.handle.run_id == run_id and not record.result().state.terminal
            ]
        for record in records:
            with record.lock:
                if not record.state.terminal:
                    record.state = ActionState.CANCEL_REQUESTED
                    record.cancel_event.set()
        deadline = time.monotonic() + timeout_s
        for record in records:
            remaining = max(0.0, deadline - time.monotonic())
            record.done_event.wait(timeout=remaining)
        return all(record.done_event.is_set() for record in records)

    def active_records(self, run_id: str | None = None) -> list[ActionRecord]:
        with self._lock:
            values = list(self._actions.values())
        return [
            record
            for record in values
            if (run_id is None or record.handle.run_id == run_id)
            and not record.result().state.terminal
        ]

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            runs = {
                run_id: {
                    "canceled": run.canceled,
                    "stopped": run.stopped,
                    "closed": run.closed,
                    "internal_motion_steps": run.internal_motion_steps,
                    "max_internal_motion_steps": run.max_internal_motion_steps,
                    "wall_timed_out": run.wall_timed_out(),
                }
                for run_id, run in self._runs.items()
            }
            actions = {
                action_id: {
                    "action_name": record.handle.action_name,
                    "run_id": record.handle.run_id,
                    "state": record.result().state.value,
                    "error_code": record.result().error_code,
                }
                for action_id, record in self._actions.items()
            }
        return {"runs": runs, "actions": actions}
