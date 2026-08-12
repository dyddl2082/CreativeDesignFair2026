"""Runtime bootstrap for the DINOv2 ROS node.

The ROS workspace may be built with the system Python.  The generated
``embedding_retrieval_node`` console script therefore may also use the system
Python, while torch / transformers live in a dedicated virtual environment.

This module is deliberately stdlib-only.  It locates the configured embedding
Python and re-executes the real node under that interpreter before importing any
ML or ROS dependency.
"""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import sys
from typing import Iterable, Optional


ENV_PYTHON = "MACROBOT_EMBEDDING_PYTHON"
ENV_VENV = "MACROBOT_EMBEDDING_VENV"
ENV_WORKSPACE = "MACROBOT_WORKSPACE"
ENV_BOOTSTRAPPED = "MACROBOT_EMBEDDING_BOOTSTRAPPED"

_CHILD_NODE = "--macrobot-bootstrap-child=node"
_CHILD_CHECK = "--macrobot-bootstrap-child=check"

_REQUIRED_MODULES = (
    "rclpy",
    "torch",
    "transformers",
    "safetensors",
    "PIL",
)


def _absolute(path: Path) -> Path:
    """Return an absolute path without resolving a venv Python symlink."""

    return Path(os.path.abspath(os.fspath(path.expanduser())))


def _deduplicate(paths: Iterable[Path]) -> list[Path]:
    result: list[Path] = []
    seen: set[str] = set()
    for path in paths:
        absolute = _absolute(path)
        key = os.fspath(absolute)
        if key in seen:
            continue
        seen.add(key)
        result.append(absolute)
    return result


def _workspace_roots() -> list[Path]:
    roots: list[Path] = []

    configured = os.environ.get(ENV_WORKSPACE, "").strip()
    if configured:
        roots.append(Path(configured))

    for variable in ("AMENT_PREFIX_PATH", "COLCON_PREFIX_PATH", "CMAKE_PREFIX_PATH"):
        for raw_entry in os.environ.get(variable, "").split(os.pathsep):
            entry = raw_entry.strip()
            if not entry:
                continue
            path = _absolute(Path(entry))
            for parent in (path, *path.parents):
                if parent.name == "install":
                    roots.append(parent.parent)
                    break

    for probe in (_absolute(Path(__file__)), _absolute(Path.cwd())):
        for parent in (probe, *probe.parents):
            if parent.name in {"src", "install"}:
                roots.append(parent.parent)
                break

    roots.append(Path.home() / "MacRobot")
    return _deduplicate(roots)


def candidate_runtime_pythons() -> list[Path]:
    """Return runtime Python candidates in priority order."""

    candidates: list[Path] = []

    explicit_python = os.environ.get(ENV_PYTHON, "").strip()
    if explicit_python:
        candidates.append(Path(explicit_python))

    explicit_venv = os.environ.get(ENV_VENV, "").strip()
    if explicit_venv:
        candidates.append(Path(explicit_venv) / "bin" / "python")

    for root in _workspace_roots():
        candidates.append(root / ".venv-embedding" / "bin" / "python")

    return _deduplicate(candidates)


def select_runtime_python() -> Optional[Path]:
    for candidate in candidate_runtime_pythons():
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate
    return None


def _current_interpreter_matches(target: Path) -> bool:
    current_executable = _absolute(Path(sys.executable))
    target = _absolute(target)
    if current_executable == target:
        return True

    # A virtualenv often exposes python, python3 and python3.X names.  They can
    # all point to the system binary, so realpath/samefile cannot distinguish
    # whether the virtualenv is active.  sys.prefix can.
    target_venv = target.parent.parent
    current_prefix = _absolute(Path(sys.prefix))
    return current_prefix == target_venv


def _missing_modules() -> list[str]:
    return [name for name in _REQUIRED_MODULES if importlib.util.find_spec(name) is None]


def _runtime_error_message(target: Optional[Path], missing: Iterable[str] = ()) -> str:
    target_text = os.fspath(target) if target is not None else "<not found>"
    missing_text = ", ".join(missing) if missing else "unknown"
    return (
        "MacRobot embedding runtime is not ready.\n"
        f"Selected Python: {target_text}\n"
        f"Missing modules: {missing_text}\n\n"
        "Expected default runtime:\n"
        "  ~/MacRobot/.venv-embedding/bin/python\n\n"
        "Override it with either:\n"
        "  export MACROBOT_EMBEDDING_PYTHON=/absolute/path/to/python\n"
        "or:\n"
        "  export MACROBOT_EMBEDDING_VENV=/absolute/path/to/venv\n\n"
        "The venv must be created from the ROS system Python with "
        "--system-site-packages so that rclpy remains importable."
    )


def _exec_child(target: Path, mode: str) -> None:
    env = os.environ.copy()
    env[ENV_BOOTSTRAPPED] = "1"
    env[ENV_PYTHON] = os.fspath(target)
    env.setdefault("PYTHONUNBUFFERED", "1")

    marker = _CHILD_NODE if mode == "node" else _CHILD_CHECK
    argv = [
        os.fspath(target),
        "-m",
        "embedding_retrieval.runtime_bootstrap",
        marker,
        *sys.argv[1:],
    ]
    os.execve(os.fspath(target), argv, env)


def _prepare_runtime(mode: str) -> None:
    target = select_runtime_python()

    if target is not None and not _current_interpreter_matches(target):
        if os.environ.get(ENV_BOOTSTRAPPED) == "1":
            raise SystemExit(
                "Embedding runtime bootstrap recursion was detected.\n"
                + _runtime_error_message(target)
            )
        _exec_child(target, mode)

    # No dedicated runtime was found.  A system-wide installation is allowed
    # only when it already provides all required modules.
    missing = _missing_modules()
    if missing:
        raise SystemExit(_runtime_error_message(target, missing))


def _run_node_local() -> None:
    _prepare_runtime("node")
    from .embedding_retrieval_node import main as real_main

    real_main()


def _run_check_local() -> None:
    _prepare_runtime("check")

    import rclpy
    import safetensors
    import torch
    import transformers
    from PIL import Image

    del Image
    payload = {
        "ok": True,
        "python": sys.executable,
        "prefix": sys.prefix,
        "rclpy": getattr(rclpy, "__file__", None),
        "torch_version": getattr(torch, "__version__", None),
        "xpu_available": bool(
            hasattr(torch, "xpu") and torch.xpu.is_available()
        ),
        "transformers_version": getattr(transformers, "__version__", None),
        "safetensors_version": getattr(safetensors, "__version__", None),
        "selected_runtime": os.environ.get(ENV_PYTHON),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def main() -> None:
    """Console entry point for the real embedding node."""

    _run_node_local()


def check_main() -> None:
    """Console entry point that verifies the selected runtime and exits."""

    _run_check_local()


def _module_dispatch() -> None:
    if len(sys.argv) >= 2 and sys.argv[1] in {_CHILD_NODE, _CHILD_CHECK}:
        marker = sys.argv.pop(1)
        if marker == _CHILD_NODE:
            _run_node_local()
        else:
            _run_check_local()
        return

    # Running this module directly is a diagnostic operation.
    _run_check_local()


if __name__ == "__main__":
    _module_dispatch()
