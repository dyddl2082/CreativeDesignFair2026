from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Mapping

import yaml

from .demo_core import DemoRecording, safe_name
from .teach_store import AtomicYamlStore, utc_now


class ArmDemoRepository:
    def __init__(self, root: str | Path, report: AtomicYamlStore) -> None:
        self.root = Path(root).expanduser().resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.report = report

    def path_for(self, name: str) -> Path:
        return self.root / f"{safe_name(name)}.yaml"

    def save(self, recording: DemoRecording) -> Path:
        path = self.path_for(recording.name)
        payload = recording.as_dict()
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        with temporary.open("w", encoding="utf-8") as stream:
            yaml.safe_dump(payload, stream, allow_unicode=True, sort_keys=False)
        temporary.replace(path)
        self._mirror_to_report(recording, path)
        return path

    def load(self, name: str) -> DemoRecording:
        path = self.path_for(name)
        if not path.exists():
            raise FileNotFoundError(f"arm primitive not found: {name}")
        with path.open("r", encoding="utf-8") as stream:
            payload = yaml.safe_load(stream) or {}
        if not isinstance(payload, Mapping):
            raise ValueError(f"invalid arm primitive: {path}")
        return DemoRecording.from_mapping(payload)

    def delete(self, name: str) -> bool:
        path = self.path_for(name)
        existed = path.exists()
        if existed:
            path.unlink()
        section = self.report.section("primitives")
        primitives = section.get("primitives", {})
        if isinstance(primitives, Mapping):
            updated = dict(primitives)
            updated.pop(str(name).upper(), None)
            updated.pop(safe_name(name), None)
            self.report.update_section(
                "primitives",
                {
                    "source": "arm_demo_recorder",
                    "primitives": updated,
                    "last_deleted": str(name),
                },
                status="completed" if updated else "in_progress",
            )
        return existed

    def list(self) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for path in sorted(self.root.glob("*.yaml")):
            try:
                with path.open("r", encoding="utf-8") as stream:
                    payload = yaml.safe_load(stream) or {}
                if not isinstance(payload, Mapping):
                    continue
                results.append(
                    {
                        "name": str(payload.get("name", path.stem)),
                        "kind": str(payload.get("kind", "trajectory")),
                        "duration_sec": float(payload.get("duration_sec", 0.0)),
                        "waypoint_count": int(payload.get("waypoint_count", 0)),
                        "recorded_at": str(payload.get("recorded_at", "")),
                        "path": str(path),
                    }
                )
            except Exception:
                continue
        return results

    def _mirror_to_report(self, recording: DemoRecording, path: Path) -> None:
        section = self.report.section("primitives")
        existing = section.get("primitives", {})
        primitives = dict(existing) if isinstance(existing, Mapping) else {}
        key = recording.name.upper()
        primitives[key] = {
            "kind": recording.kind,
            "target_q": list(recording.final_q),
            "trajectory_file": str(path),
            "duration_sec": recording.duration_sec,
            "waypoint_count": len(recording.waypoints),
            "speed_scale": recording.speed_scale,
            "operator_pass": True,
            "notes": recording.notes,
            "recorded_at": recording.recorded_at,
            "recorded_by": "arm_demo_recorder",
            "source_state": recording.source_state,
            "marks": list(recording.marks),
        }
        self.report.complete_section(
            "primitives",
            {
                "source": "arm_demo_recorder",
                "primitives": primitives,
                "last_recorded": key,
                "updated_at": utc_now(),
            },
        )
