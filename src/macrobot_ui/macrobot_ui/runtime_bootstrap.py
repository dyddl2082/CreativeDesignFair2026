from __future__ import annotations

import importlib
import importlib.util
import os
from pathlib import Path
import sys
from typing import Iterable


ENV_PYTHON = "MACROBOT_UI_PYTHON"
ENV_VENV = "MACROBOT_UI_VENV"
ENV_WORKSPACE = "MACROBOT_WORKSPACE"
ENV_BOOTSTRAPPED = "MACROBOT_UI_BOOTSTRAPPED"
UI_REQUIRED_MODULES = ("PySide6", "openai", "rclpy", "yaml", "dotenv")
FONT_CHECK_REQUIRED_MODULES = ("PySide6",)


def _absolute(path: Path) -> Path:
    return Path(os.path.abspath(os.fspath(path.expanduser())))


def _workspace_roots() -> list[Path]:
    roots: list[Path] = []
    configured = os.environ.get(ENV_WORKSPACE, "").strip()
    if configured:
        roots.append(Path(configured))
    for variable in ("AMENT_PREFIX_PATH", "COLCON_PREFIX_PATH", "CMAKE_PREFIX_PATH"):
        for entry in os.environ.get(variable, "").split(os.pathsep):
            if not entry.strip():
                continue
            path = _absolute(Path(entry))
            for parent in (path, *path.parents):
                if parent.name == "install":
                    roots.append(parent.parent)
                    break
    roots.extend((Path.home() / "MacRobot", Path.home()))
    unique: list[Path] = []
    seen: set[str] = set()
    for root in roots:
        absolute = _absolute(root)
        key = os.fspath(absolute)
        if key not in seen:
            seen.add(key)
            unique.append(absolute)
    return unique


def candidate_pythons() -> list[Path]:
    values: list[Path] = []
    explicit = os.environ.get(ENV_PYTHON, "").strip()
    if explicit:
        values.append(Path(explicit))
    venv = os.environ.get(ENV_VENV, "").strip()
    if venv:
        values.append(Path(venv) / "bin" / "python")
    for root in _workspace_roots():
        values.append(root / ".venv-ui" / "bin" / "python")
    unique: list[Path] = []
    seen: set[str] = set()
    for value in values:
        absolute = _absolute(value)
        key = os.fspath(absolute)
        if key not in seen:
            seen.add(key)
            unique.append(absolute)
    return unique


def _missing_modules(required: Iterable[str]) -> list[str]:
    return [name for name in required if importlib.util.find_spec(name) is None]


def _bootstrap_and_run(
    *,
    module_name: str,
    callable_name: str,
    required_modules: tuple[str, ...],
) -> int:
    current = _absolute(Path(sys.executable))
    for candidate in candidate_pythons():
        if not candidate.is_file() or not os.access(candidate, os.X_OK):
            continue
        if candidate == current:
            break
        if os.environ.get(ENV_BOOTSTRAPPED) == "1":
            break
        env = os.environ.copy()
        env[ENV_BOOTSTRAPPED] = "1"
        env[ENV_PYTHON] = os.fspath(candidate)
        env.setdefault("PYTHONUNBUFFERED", "1")
        os.execve(
            os.fspath(candidate),
            [os.fspath(candidate), "-m", module_name, *sys.argv[1:]],
            env,
        )

    missing = _missing_modules(required_modules)
    if missing:
        candidates = "\n".join(f"  - {path}" for path in candidate_pythons())
        print(
            "MacRobot UI Python runtime is incomplete.\n"
            f"Missing modules: {', '.join(missing)}\n"
            "Create ~/MacRobot/.venv-ui with --system-site-packages and install "
            "requirements-ui.txt.\n"
            f"Candidates checked:\n{candidates}",
            file=sys.stderr,
        )
        return 2

    module = importlib.import_module(module_name)
    target = getattr(module, callable_name)
    return int(target())


def main() -> int:
    # Input-method environment must be selected before PySide6/Qt is imported.
    from .ime_support import prepare_input_method_environment

    preparation = prepare_input_method_environment(start_daemon=True)
    print(
        "[MacRobot UI IME] "
        f"backend={preparation.backend!r}, "
        f"platform={preparation.qpa_platform!r}, "
        f"QT_IM_MODULE={preparation.qt_im_module!r}, "
        f"daemon_ready={preparation.daemon_ready}, "
        f"engine={preparation.current_engine!r}",
        file=sys.stderr,
    )
    for warning in preparation.warnings:
        print(f"[MacRobot UI IME] WARNING: {warning}", file=sys.stderr)

    strict_ime = os.environ.get(
        "MACROBOT_UI_IME_STRICT",
        "false",
    ).strip().lower() in {"1", "true", "yes", "on"}
    if (
        preparation.is_wsl
        and preparation.backend == "ibus"
        and strict_ime
        and (
            not preparation.daemon_ready
            or not preparation.hangul_engine_available
        )
    ):
        print(
            "ERROR: Korean input is not ready. Run "
            "install_wsl_ui_ime.sh --install --activate-hangul, then "
            "ros2 run macrobot_ui macrobot_ui_ime_check.",
            file=sys.stderr,
        )
        return 4

    return _bootstrap_and_run(
        module_name="macrobot_ui.main",
        callable_name="main",
        required_modules=UI_REQUIRED_MODULES,
    )


def font_check_main() -> int:
    return _bootstrap_and_run(
        module_name="macrobot_ui.font_support",
        callable_name="diagnostic_main",
        required_modules=FONT_CHECK_REQUIRED_MODULES,
    )


def ime_check_main() -> int:
    from .ime_support import prepare_input_method_environment

    prepare_input_method_environment(start_daemon=True)
    return _bootstrap_and_run(
        module_name="macrobot_ui.ime_support",
        callable_name="diagnostic_main",
        required_modules=FONT_CHECK_REQUIRED_MODULES,
    )


if __name__ == "__main__":
    raise SystemExit(main())
