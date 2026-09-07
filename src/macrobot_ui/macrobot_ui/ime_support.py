"""WSLg/Qt input-method preparation and diagnostics for MacRobot UI.

This module is intentionally standard-library only until ``diagnostic_main``
imports PySide6.  It is called by the console bootstrap before Qt is imported,
because Qt selects its platform and input-context plugins during application
startup.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import importlib.util
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import time
from typing import Mapping, MutableMapping


IME_ENV_KEYS = {
    "MACROBOT_UI_IME_BACKEND",
    "MACROBOT_UI_IME_AUTOSTART",
    "MACROBOT_UI_IME_FORCE_XCB",
    "MACROBOT_UI_IME_STRICT",
    "MACROBOT_UI_IME_ENGINE",
    "MACROBOT_UI_IME_AUTO_ACTIVATE",
    "QT_QPA_PLATFORM",
    "QT_IM_MODULE",
    "QT_IM_MODULES",
    "GTK_IM_MODULE",
    "XMODIFIERS",
}


@dataclass(frozen=True)
class ImePreparation:
    backend: str
    is_wsl: bool
    qpa_platform: str
    qt_im_module: str
    gtk_im_module: str
    xmodifiers: str
    daemon_ready: bool
    hangul_engine_available: bool
    current_engine: str
    warnings: tuple[str, ...]


def _truthy(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _strip_env_value(value: str) -> str:
    value = value.strip()
    if not value:
        return ""
    try:
        tokens = shlex.split(value, comments=False, posix=True)
    except ValueError:
        return value.strip('"\'')
    return tokens[0] if len(tokens) == 1 else value.strip('"\'')


def load_ime_environment_file(
    environ: MutableMapping[str, str] | None = None,
    path: Path | None = None,
) -> None:
    """Load only IME-related keys from the user's MacRobot ``.env`` file.

    ``python-dotenv`` cannot be assumed to be available before the UI virtual
    environment is selected, so this small parser handles only simple
    ``KEY=value`` entries used by the IME bootstrap.
    """

    target = os.environ if environ is None else environ
    env_path = path or (Path.home() / ".config" / "macrobot_ui" / ".env")
    if not env_path.is_file():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key not in IME_ENV_KEYS or key in target:
            continue
        target[key] = _strip_env_value(value)


def is_wsl_environment(environ: Mapping[str, str] | None = None) -> bool:
    values = os.environ if environ is None else environ
    if values.get("WSL_INTEROP") or values.get("WSL_DISTRO_NAME"):
        return True
    try:
        release = Path("/proc/sys/kernel/osrelease").read_text(
            encoding="utf-8"
        )
    except OSError:
        return False
    return "microsoft" in release.casefold() or "wsl" in release.casefold()


def plan_input_method_environment(
    current: Mapping[str, str],
    *,
    wsl: bool,
) -> dict[str, str]:
    """Return environment defaults without overwriting explicit user values."""

    result = dict(current)
    backend = result.get("MACROBOT_UI_IME_BACKEND", "ibus").strip().lower()
    if backend in {"", "none", "off", "disabled"}:
        return result
    if backend != "ibus":
        return result

    # WSLg uses Weston and exposes both Wayland and XWayland.  The PySide6 pip
    # wheel bundles its own Qt runtime, so the most portable path is its bundled
    # IBus input-context plugin on XWayland rather than mixing a distribution
    # fcitx Qt plugin with a different bundled Qt ABI.
    force_xcb = _truthy(result.get("MACROBOT_UI_IME_FORCE_XCB"), True)
    if wsl and force_xcb:
        result.setdefault("QT_QPA_PLATFORM", "xcb")
    result.setdefault("QT_IM_MODULE", "ibus")
    result.setdefault("QT_IM_MODULES", "ibus;compose")
    result.setdefault("GTK_IM_MODULE", "ibus")
    result.setdefault("XMODIFIERS", "@im=ibus")
    return result


def _run(
    command: list[str],
    *,
    timeout: float = 3.0,
    environ: Mapping[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout,
        env=dict(os.environ if environ is None else environ),
    )


def _ibus_engine(environ: Mapping[str, str]) -> tuple[bool, str]:
    if shutil.which("ibus") is None:
        return False, ""
    try:
        result = _run(["ibus", "engine"], environ=environ)
    except (OSError, subprocess.TimeoutExpired):
        return False, ""
    return result.returncode == 0, result.stdout.strip()


def _hangul_engine_available(environ: Mapping[str, str]) -> bool:
    if shutil.which("ibus") is None:
        return False
    try:
        result = _run(["ibus", "list-engine"], timeout=5.0, environ=environ)
    except (OSError, subprocess.TimeoutExpired):
        return False
    text = (result.stdout + "\n" + result.stderr).casefold()
    return result.returncode == 0 and "hangul" in text


def _ensure_ibus_daemon(
    environ: Mapping[str, str],
    *,
    autostart: bool,
) -> tuple[bool, str, list[str]]:
    warnings: list[str] = []
    ready, engine = _ibus_engine(environ)
    if ready:
        return True, engine, warnings

    if shutil.which("ibus-daemon") is None:
        warnings.append(
            "ibus-daemon is not installed; install packages ibus and ibus-hangul."
        )
        return False, "", warnings
    if not autostart:
        warnings.append("IBus is not reachable and automatic startup is disabled.")
        return False, "", warnings

    try:
        start = _run(
            ["ibus-daemon", "--daemonize", "--replace", "--xim"],
            timeout=8.0,
            environ=environ,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        warnings.append(f"Failed to start ibus-daemon: {error}")
        return False, "", warnings
    if start.returncode != 0:
        detail = (start.stderr or start.stdout).strip()
        warnings.append(
            "ibus-daemon startup failed"
            + (f": {detail}" if detail else ".")
        )
        return False, "", warnings

    for _ in range(30):
        time.sleep(0.1)
        ready, engine = _ibus_engine(environ)
        if ready:
            return True, engine, warnings
    warnings.append("ibus-daemon started but did not become reachable in 3 seconds.")
    return False, "", warnings


def _activate_engine(
    environ: Mapping[str, str],
    engine: str,
) -> tuple[bool, str]:
    if not engine or shutil.which("ibus") is None:
        return False, ""
    try:
        result = _run(["ibus", "engine", engine], environ=environ)
    except (OSError, subprocess.TimeoutExpired):
        return False, ""
    return result.returncode == 0, (result.stderr or result.stdout).strip()


def prepare_input_method_environment(
    *,
    start_daemon: bool = True,
    environ: MutableMapping[str, str] | None = None,
) -> ImePreparation:
    """Prepare a Korean-capable IBus/Qt environment before importing Qt."""

    target = os.environ if environ is None else environ
    load_ime_environment_file(target)
    wsl = is_wsl_environment(target)
    planned = plan_input_method_environment(target, wsl=wsl)
    target.update(planned)

    backend = target.get("MACROBOT_UI_IME_BACKEND", "ibus").strip().lower()
    warnings: list[str] = []
    ready = False
    current_engine = ""
    hangul_available = False
    if backend == "ibus":
        autostart = start_daemon and _truthy(
            target.get("MACROBOT_UI_IME_AUTOSTART"), True
        )
        ready, current_engine, daemon_warnings = _ensure_ibus_daemon(
            target,
            autostart=autostart,
        )
        warnings.extend(daemon_warnings)
        hangul_available = _hangul_engine_available(target) if ready else False
        if ready and not hangul_available:
            warnings.append(
                "The IBus Hangul engine is not installed or not visible; install ibus-hangul."
            )
        auto_activate = _truthy(
            target.get("MACROBOT_UI_IME_AUTO_ACTIVATE"), True
        )
        requested_engine = target.get("MACROBOT_UI_IME_ENGINE", "hangul").strip()
        if ready and hangul_available and auto_activate and requested_engine:
            activated, detail = _activate_engine(target, requested_engine)
            if not activated:
                warnings.append(
                    f"Could not activate IBus engine {requested_engine!r}"
                    + (f": {detail}" if detail else ".")
                )
            else:
                _, current_engine = _ibus_engine(target)
    elif backend not in {"", "none", "off", "disabled"}:
        warnings.append(
            f"Unsupported MACROBOT_UI_IME_BACKEND={backend!r}; supported: ibus, none."
        )

    return ImePreparation(
        backend=backend,
        is_wsl=wsl,
        qpa_platform=target.get("QT_QPA_PLATFORM", ""),
        qt_im_module=target.get("QT_IM_MODULE", ""),
        gtk_im_module=target.get("GTK_IM_MODULE", ""),
        xmodifiers=target.get("XMODIFIERS", ""),
        daemon_ready=ready,
        hangul_engine_available=hangul_available,
        current_engine=current_engine,
        warnings=tuple(warnings),
    )


def _pyside_input_plugins() -> tuple[str, list[str]]:
    spec = importlib.util.find_spec("PySide6")
    if spec is None or not spec.submodule_search_locations:
        return "", []
    root = Path(next(iter(spec.submodule_search_locations)))
    plugin_dir = root / "Qt" / "plugins" / "platforminputcontexts"
    if not plugin_dir.is_dir():
        return str(plugin_dir), []
    return str(plugin_dir), sorted(path.name for path in plugin_dir.glob("*"))


def diagnostic_main() -> int:
    preparation = prepare_input_method_environment(start_daemon=True)
    plugin_dir, plugins = _pyside_input_plugins()
    errors: list[str] = []

    if preparation.backend == "ibus":
        if not preparation.daemon_ready:
            errors.append("IBus daemon is not reachable")
        if not preparation.hangul_engine_available:
            errors.append("IBus Hangul engine is unavailable")
        if preparation.qt_im_module != "ibus":
            errors.append("QT_IM_MODULE is not ibus")
        if preparation.is_wsl and preparation.qpa_platform != "xcb":
            errors.append("WSLg Qt platform is not forced to xcb")
        if not any("ibus" in name.casefold() for name in plugins):
            errors.append(
                "PySide6's platforminputcontexts directory has no IBus plugin"
            )

    qt: dict[str, object] = {}
    try:
        from PySide6.QtCore import QLibraryInfo, Qt
        from PySide6.QtGui import QGuiApplication
        from PySide6.QtWidgets import QApplication, QPlainTextEdit

        app = QApplication.instance() or QApplication(["macrobot-ui-ime-check"])
        editor = QPlainTextEdit()
        editor.setAttribute(Qt.WidgetAttribute.WA_InputMethodEnabled, True)
        qt = {
            "platform_name": QGuiApplication.platformName(),
            "plugins_path": QLibraryInfo.path(
                QLibraryInfo.LibraryPath.PluginsPath
            ),
            "input_method_enabled": editor.testAttribute(
                Qt.WidgetAttribute.WA_InputMethodEnabled
            ),
            "input_method_locale": QGuiApplication.inputMethod().locale().name(),
        }
        if not qt["input_method_enabled"]:
            errors.append("QPlainTextEdit does not have WA_InputMethodEnabled")
        editor.deleteLater()
        del app
    except Exception as error:  # pragma: no cover - runtime diagnostic
        errors.append(f"Qt input-method diagnostic failed: {error}")

    payload = {
        "ok": not errors,
        "preparation": asdict(preparation),
        "environment": {
            key: os.environ.get(key, "")
            for key in (
                "DISPLAY",
                "WAYLAND_DISPLAY",
                "QT_QPA_PLATFORM",
                "QT_IM_MODULE",
                "QT_IM_MODULES",
                "GTK_IM_MODULE",
                "XMODIFIERS",
                "DBUS_SESSION_BUS_ADDRESS",
            )
        },
        "pyside_platforminputcontexts": {
            "directory": plugin_dir,
            "plugins": plugins,
        },
        "qt": qt,
        "errors": errors,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(diagnostic_main())
