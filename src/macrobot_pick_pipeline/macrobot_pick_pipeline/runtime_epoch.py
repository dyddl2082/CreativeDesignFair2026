"""Runtime epoch helpers for odometry-scoped memories.

Wheel odometry has no globally persistent origin.  A location recorded in one
Linux/Pico boot therefore must not be treated as an absolute coordinate after a
restart.  This module gives each observation an epoch token and provides a
conservative compatibility check.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Optional
import uuid


_DEFAULT_BOOT_ID_PATH = Path("/proc/sys/kernel/random/boot_id")


def read_host_boot_id(path: Path = _DEFAULT_BOOT_ID_PATH) -> str:
    """Return the current Linux boot ID, or a process-local fallback."""

    try:
        value = path.read_text(encoding="utf-8").strip()
        if value:
            return value
    except OSError:
        pass
    return f"fallback-{uuid.uuid4()}"


def _optional_int(value: Any) -> Optional[int]:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


@dataclass(frozen=True)
class RuntimeEpoch:
    """Identity of the host/Pico odometry session used by an observation."""

    host_boot_id: str
    pico_boot_id: str = ""
    pico_time_ms: Optional[int] = None

    @classmethod
    def current(
        cls,
        payload: Optional[Mapping[str, Any]] = None,
        *,
        host_boot_id: Optional[str] = None,
    ) -> "RuntimeEpoch":
        payload = payload or {}
        odometry = payload.get("odometry")
        if not isinstance(odometry, Mapping):
            odometry = payload.get("odom")
        if not isinstance(odometry, Mapping):
            odometry = {}

        pico_boot = ""
        for key in ("pico_boot_id", "boot_id", "odom_epoch", "epoch_id"):
            raw = payload.get(key)
            if raw in (None, ""):
                raw = odometry.get(key)
            if raw not in (None, ""):
                pico_boot = str(raw).strip()
                break

        pico_time = None
        for key in ("pico_time_ms", "time_ms", "uptime_ms"):
            pico_time = _optional_int(odometry.get(key))
            if pico_time is None:
                pico_time = _optional_int(payload.get(key))
            if pico_time is not None:
                break

        return cls(
            host_boot_id=(host_boot_id or read_host_boot_id()).strip(),
            pico_boot_id=pico_boot,
            pico_time_ms=pico_time,
        )

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "RuntimeEpoch":
        return cls(
            host_boot_id=str(value.get("host_boot_id", "")).strip(),
            pico_boot_id=str(value.get("pico_boot_id", "")).strip(),
            pico_time_ms=_optional_int(value.get("pico_time_ms")),
        )

    def to_mapping(self) -> dict[str, Any]:
        return {
            "host_boot_id": self.host_boot_id,
            "pico_boot_id": self.pico_boot_id or None,
            "pico_time_ms": self.pico_time_ms,
        }


def epoch_compatibility(
    recorded: RuntimeEpoch,
    current: RuntimeEpoch,
    *,
    pico_time_tolerance_ms: int = 2000,
) -> tuple[bool, str]:
    """Return whether an odometry-frame memory can be reused safely.

    Host boot mismatch is always stale.  A Pico boot identifier, when present on
    both sides, is authoritative.  Otherwise a large Pico uptime regression is
    treated as a reset.  Missing historical epoch metadata is deliberately
    considered stale rather than guessed compatible.
    """

    if not recorded.host_boot_id:
        return False, "recorded_epoch_missing"
    if not current.host_boot_id:
        return False, "current_epoch_missing"
    if recorded.host_boot_id != current.host_boot_id:
        return False, "host_restarted"

    if recorded.pico_boot_id and current.pico_boot_id:
        if recorded.pico_boot_id != current.pico_boot_id:
            return False, "pico_restarted"
        return True, "same_host_and_pico_boot"

    if recorded.pico_time_ms is not None and current.pico_time_ms is not None:
        tolerance = max(0, int(pico_time_tolerance_ms))
        if current.pico_time_ms + tolerance < recorded.pico_time_ms:
            return False, "pico_uptime_regressed"
        return True, "same_host_no_pico_regression"

    return True, "same_host_pico_epoch_unknown"
