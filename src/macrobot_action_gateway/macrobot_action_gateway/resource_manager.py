from __future__ import annotations

import threading
import time
from collections.abc import Callable, Iterable

from .api_types import ResourceId


class ResourceManager:
    """Thread-safe atomic resource manager.

    Resources are acquired as one set.  The implementation deliberately does
    not provide an acquire-after-check path, matching the v0.2 contract.
    """

    def __init__(self) -> None:
        self._condition = threading.Condition()
        self._owners: dict[ResourceId, str] = {}

    def acquire(self, owner_id: str, resources: Iterable[ResourceId]) -> bool:
        requested = tuple(sorted(set(resources), key=lambda item: item.value))
        with self._condition:
            if any(resource in self._owners for resource in requested):
                return False
            for resource in requested:
                self._owners[resource] = owner_id
            self._condition.notify_all()
            return True

    def release(self, owner_id: str) -> None:
        with self._condition:
            released = [
                resource
                for resource, current_owner in self._owners.items()
                if current_owner == owner_id
            ]
            for resource in released:
                del self._owners[resource]
            self._condition.notify_all()

    def owner(self, resource: ResourceId) -> str | None:
        with self._condition:
            return self._owners.get(resource)

    def is_idle(self, resource: ResourceId) -> bool:
        return self.owner(resource) is None

    def wait_idle(
        self,
        resource: ResourceId,
        timeout_s: float,
        interrupted: Callable[[], bool] | None = None,
    ) -> bool:
        deadline = time.monotonic() + timeout_s
        with self._condition:
            while resource in self._owners:
                if interrupted is not None and interrupted():
                    return False
                remaining = deadline - time.monotonic()
                if remaining <= 0.0:
                    return False
                self._condition.wait(timeout=min(remaining, 0.1))
            return True

    def snapshot(self) -> dict[str, str]:
        with self._condition:
            return {
                resource.value: owner
                for resource, owner in sorted(
                    self._owners.items(), key=lambda item: item[0].value
                )
            }
