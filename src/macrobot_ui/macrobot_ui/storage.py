from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

from .models import StoredTask


class TaskStorage:
    def __init__(self, tasks_dir: Path, result_dir: Path) -> None:
        self._tasks_dir = Path(tasks_dir)
        self._result_dir = Path(result_dir)

    def save(
        self,
        request_text: str,
        code: str,
        metadata: dict[str, Any],
    ) -> StoredTask:
        self._tasks_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        normalized_code = code.rstrip() + "\n"
        source_hash = hashlib.sha256(normalized_code.encode("utf-8")).hexdigest()
        stem = f"{timestamp}_{_safe_stem(request_text)}_{source_hash[:10]}"
        code_path = self._tasks_dir / f"{stem}.py"
        metadata_path = self._tasks_dir / f"{stem}.json"
        payload = dict(metadata)
        payload.update(
            {
                "source_sha256": source_hash,
                "code_path": str(code_path),
                "saved_at": datetime.now().astimezone().isoformat(),
            }
        )
        _atomic_write_text(code_path, normalized_code, mode=0o600)
        _atomic_write_text(
            metadata_path,
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            mode=0o600,
        )
        return StoredTask(
            code_path=code_path,
            metadata_path=metadata_path,
            source_sha256=source_hash,
        )

    def save_backend_result(self, request_id: str, payload: dict[str, Any]) -> Path:
        self._result_dir.mkdir(parents=True, exist_ok=True)
        safe_id = re.sub(r"[^0-9A-Za-z_.-]", "_", request_id)[:96] or "unknown"
        path = self._result_dir / f"{safe_id}.json"
        _atomic_write_text(
            path,
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            mode=0o600,
        )
        return path


def _safe_stem(text: str) -> str:
    compact = re.sub(r"\s+", "_", text.strip())
    compact = re.sub(r"[^0-9A-Za-z가-힣_-]", "", compact)
    return (compact[:32] or "task").strip("_") or "task"


def _atomic_write_text(path: Path, text: str, *, mode: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise
