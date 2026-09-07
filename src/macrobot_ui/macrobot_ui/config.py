from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

try:
    from ament_index_python.packages import get_package_share_directory
except ImportError:  # Allows source-only parser/validator tests.
    get_package_share_directory = None  # type: ignore[assignment]


PACKAGE_NAME = "macrobot_ui"


def package_share_dir() -> Path:
    if get_package_share_directory is not None:
        try:
            return Path(get_package_share_directory(PACKAGE_NAME))
        except Exception:
            pass
    return Path(__file__).resolve().parents[1]


def _as_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _expanded(value: str | Path) -> Path:
    return Path(value).expanduser().resolve()


@dataclass(frozen=True)
class AppConfig:
    api_key: str | None
    model: str
    store_responses: bool
    knowledge_dir: Path
    tasks_dir: Path
    run_result_dir: Path
    max_input_chars: int
    execution_controls_enabled: bool
    request_retry_period_ms: int
    request_ack_timeout_ms: int

    @property
    def api_ready(self) -> bool:
        return bool(self.api_key)

    @classmethod
    def from_node(cls, node) -> "AppConfig":
        share = package_share_dir()
        defaults = {
            "env_file": str(Path.home() / ".config" / "macrobot_ui" / ".env"),
            "knowledge_dir": str(share / "knowledge"),
            "tasks_dir": str(
                Path.home() / "MacRobot" / "data" / "ui" / "generated_tasks"
            ),
            "run_result_dir": str(
                Path.home() / "MacRobot" / "data" / "ui" / "frontend_results"
            ),
            "model": "gpt-5.6",
            "store_responses": False,
            "max_input_chars": 500,
            "execution_controls_enabled": True,
            "request_retry_period_ms": 750,
            "request_ack_timeout_ms": 12000,
        }
        for name, value in defaults.items():
            node.declare_parameter(name, value)

        env_file = _expanded(str(node.get_parameter("env_file").value))
        if env_file.is_file():
            load_dotenv(env_file, override=False)

        model_from_param = str(node.get_parameter("model").value).strip()
        model = os.getenv("MACROBOT_MODEL", model_from_param).strip()
        store_responses = _as_bool(
            os.getenv("MACROBOT_STORE_RESPONSES"),
            bool(node.get_parameter("store_responses").value),
        )
        return cls(
            api_key=os.getenv("OPENAI_API_KEY"),
            model=model,
            store_responses=store_responses,
            knowledge_dir=_expanded(str(node.get_parameter("knowledge_dir").value)),
            tasks_dir=_expanded(str(node.get_parameter("tasks_dir").value)),
            run_result_dir=_expanded(
                str(node.get_parameter("run_result_dir").value)
            ),
            max_input_chars=max(100, int(node.get_parameter("max_input_chars").value)),
            execution_controls_enabled=bool(
                node.get_parameter("execution_controls_enabled").value
            ),
            request_retry_period_ms=max(
                200, int(node.get_parameter("request_retry_period_ms").value)
            ),
            request_ack_timeout_ms=max(
                1000, int(node.get_parameter("request_ack_timeout_ms").value)
            ),
        )
