from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import os
from pathlib import Path
import tempfile
import threading
from typing import Any, Dict, Mapping

import yaml


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _mapping(value: Any) -> Dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


class AtomicYamlStore:
    """Small atomic YAML store compatible with the commissioning report layout."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path).expanduser().resolve()
        self._lock = threading.RLock()
        self._data: Dict[str, Any] = {}
        self.reload()

    def reload(self) -> None:
        with self._lock:
            if self.path.exists():
                with self.path.open("r", encoding="utf-8") as stream:
                    loaded = yaml.safe_load(stream) or {}
                self._data = _mapping(loaded)
            else:
                self._data = {}
            metadata = _mapping(self._data.get("metadata"))
            metadata.setdefault("created_at", utc_now())
            metadata["updated_at"] = utc_now()
            metadata.setdefault("robot", "MacRobot")
            metadata.setdefault("schema", "macrobot.arm_commissioning/v2")
            self._data["metadata"] = metadata
            self._data.setdefault("sections", {})

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            return deepcopy(self._data)

    def section(self, name: str) -> Dict[str, Any]:
        with self._lock:
            sections = _mapping(self._data.get("sections"))
            return deepcopy(_mapping(sections.get(name)))

    def update_section(
        self,
        name: str,
        payload: Mapping[str, Any],
        *,
        status: str = "in_progress",
        merge: bool = True,
    ) -> Dict[str, Any]:
        with self._lock:
            sections = _mapping(self._data.get("sections"))
            previous = _mapping(sections.get(name)) if merge else {}
            merged = {**previous, **deepcopy(dict(payload))}
            merged.setdefault("started_at", previous.get("started_at", utc_now()))
            merged["updated_at"] = utc_now()
            merged["status"] = status
            sections[name] = merged
            self._data["sections"] = sections
            self._touch_metadata()
            self.save()
            return deepcopy(merged)

    def complete_section(
        self,
        name: str,
        payload: Mapping[str, Any],
        *,
        merge: bool = True,
    ) -> Dict[str, Any]:
        result = self.update_section(name, payload, status="completed", merge=merge)
        with self._lock:
            sections = _mapping(self._data.get("sections"))
            section = _mapping(sections.get(name))
            section["completed_at"] = utc_now()
            sections[name] = section
            self._data["sections"] = sections
            self._touch_metadata()
            self.save()
            return deepcopy(section)

    def _touch_metadata(self) -> None:
        metadata = _mapping(self._data.get("metadata"))
        metadata.setdefault("created_at", utc_now())
        metadata["updated_at"] = utc_now()
        metadata.setdefault("robot", "MacRobot")
        metadata.setdefault("schema", "macrobot.arm_commissioning/v2")
        self._data["metadata"] = metadata

    def save(self) -> None:
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._touch_metadata()
            fd, temp_name = tempfile.mkstemp(
                prefix=f".{self.path.name}.",
                suffix=".tmp",
                dir=str(self.path.parent),
                text=True,
            )
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as stream:
                    yaml.safe_dump(
                        self._data,
                        stream,
                        allow_unicode=True,
                        sort_keys=False,
                        default_flow_style=False,
                    )
                    stream.flush()
                    os.fsync(stream.fileno())
                os.replace(temp_name, self.path)
            finally:
                if os.path.exists(temp_name):
                    os.unlink(temp_name)
