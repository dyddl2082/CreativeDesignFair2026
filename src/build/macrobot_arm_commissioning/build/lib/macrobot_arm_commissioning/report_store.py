from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import os
from pathlib import Path
import threading
import uuid
from typing import Any, Dict, Iterable, MutableMapping, Sequence

import yaml


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class ReportStore:
    """Atomic, resumable YAML report store.

    The commissioning wizard writes every completed operator input and automatic
    observation immediately.  If the process is interrupted, the same report can
    be reopened and continued.
    """

    def __init__(self, path: str | Path, robot_name: str = "MacRobot") -> None:
        self.path = Path(path).expanduser().resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        if self.path.exists():
            with self.path.open("r", encoding="utf-8") as stream:
                loaded = yaml.safe_load(stream) or {}
            if not isinstance(loaded, dict):
                raise ValueError(f"Report root must be a mapping: {self.path}")
            self.data: Dict[str, Any] = loaded
            self.data.setdefault("schema_version", 1)
            self.data.setdefault("robot_name", robot_name)
            self.data.setdefault("report_id", str(uuid.uuid4()))
            self.data.setdefault("created_at", utc_now())
            self.data.setdefault("sections", {})
        else:
            self.data = {
                "schema_version": 1,
                "robot_name": robot_name,
                "report_id": str(uuid.uuid4()),
                "created_at": utc_now(),
                "updated_at": utc_now(),
                "sections": {},
            }
            self.save()

    def save(self) -> None:
        with self._lock:
            self.data["updated_at"] = utc_now()
            temp_path = self.path.with_name(self.path.name + ".tmp")
            with temp_path.open("w", encoding="utf-8") as stream:
                yaml.safe_dump(
                    self.data,
                    stream,
                    allow_unicode=True,
                    sort_keys=False,
                    default_flow_style=False,
                )
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp_path, self.path)

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            return deepcopy(self.data)

    def set_path(self, keys: Sequence[str], value: Any) -> None:
        if not keys:
            raise ValueError("keys must not be empty")
        with self._lock:
            cursor: MutableMapping[str, Any] = self.data
            for key in keys[:-1]:
                next_value = cursor.get(key)
                if not isinstance(next_value, dict):
                    next_value = {}
                    cursor[key] = next_value
                cursor = next_value
            cursor[keys[-1]] = value
            self.save()

    def merge_path(self, keys: Sequence[str], values: Dict[str, Any]) -> None:
        if not keys:
            raise ValueError("keys must not be empty")
        with self._lock:
            cursor: MutableMapping[str, Any] = self.data
            for key in keys:
                next_value = cursor.get(key)
                if not isinstance(next_value, dict):
                    next_value = {}
                    cursor[key] = next_value
                cursor = next_value
            cursor.update(values)
            self.save()

    def append_path(self, keys: Sequence[str], value: Any) -> None:
        if not keys:
            raise ValueError("keys must not be empty")
        with self._lock:
            cursor: MutableMapping[str, Any] = self.data
            for key in keys[:-1]:
                next_value = cursor.get(key)
                if not isinstance(next_value, dict):
                    next_value = {}
                    cursor[key] = next_value
                cursor = next_value
            target = cursor.get(keys[-1])
            if target is None:
                target = []
                cursor[keys[-1]] = target
            if not isinstance(target, list):
                raise ValueError(f"Report path is not a list: {'.'.join(keys)}")
            target.append(value)
            self.save()

    def begin_section(self, name: str, metadata: Dict[str, Any] | None = None) -> None:
        payload: Dict[str, Any] = {
            "status": "in_progress",
            "started_at": utc_now(),
        }
        if metadata:
            payload.update(metadata)
        self.set_path(("sections", name), payload)

    def complete_section(self, name: str, payload: Dict[str, Any]) -> None:
        result = dict(payload)
        result["status"] = "completed"
        result["completed_at"] = utc_now()
        existing = self.data.get("sections", {}).get(name, {})
        if isinstance(existing, dict) and "started_at" in existing:
            result.setdefault("started_at", existing["started_at"])
        self.set_path(("sections", name), result)

    def mark_section(self, name: str, status: str, details: Dict[str, Any] | None = None) -> None:
        payload: Dict[str, Any] = {"status": status, "updated_at": utc_now()}
        if details:
            payload.update(details)
        self.merge_path(("sections", name), payload)

    def section_statuses(self) -> Dict[str, str]:
        sections = self.data.get("sections", {})
        if not isinstance(sections, dict):
            return {}
        output: Dict[str, str] = {}
        for name, value in sections.items():
            if isinstance(value, dict):
                output[str(name)] = str(value.get("status", "unknown"))
        return output
