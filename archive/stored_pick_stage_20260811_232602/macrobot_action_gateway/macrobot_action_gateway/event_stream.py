from __future__ import annotations

from collections import deque
from collections.abc import Callable
import threading
import time
from typing import Any


class EventStream:
    """Small condition-backed event history used by ROS callbacks and action threads."""

    def __init__(self, maxlen: int = 256) -> None:
        self._condition = threading.Condition()
        self._events: deque[tuple[int, float, dict[str, Any]]] = deque(maxlen=maxlen)
        self._sequence = 0

    def append(self, payload: dict[str, Any]) -> int:
        with self._condition:
            self._sequence += 1
            sequence = self._sequence
            self._events.append((sequence, time.monotonic(), payload))
            self._condition.notify_all()
            return sequence

    def last_sequence(self) -> int:
        with self._condition:
            return self._sequence

    def latest(self) -> tuple[int, float, dict[str, Any]] | None:
        with self._condition:
            return None if not self._events else self._events[-1]

    def wait_for(
        self,
        predicate: Callable[[dict[str, Any]], bool],
        *,
        after_sequence: int,
        timeout_s: float,
        interrupted: Callable[[], bool] | None = None,
    ) -> dict[str, Any] | None:
        deadline = time.monotonic() + timeout_s
        cursor = after_sequence
        with self._condition:
            while True:
                for sequence, _, payload in self._events:
                    if sequence <= cursor:
                        continue
                    cursor = max(cursor, sequence)
                    if predicate(payload):
                        return payload
                if interrupted is not None and interrupted():
                    return None
                remaining = deadline - time.monotonic()
                if remaining <= 0.0:
                    return None
                self._condition.wait(timeout=min(remaining, 0.1))
