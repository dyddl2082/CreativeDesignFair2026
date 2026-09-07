from __future__ import annotations

from pathlib import Path

from macrobot_ui.ime_support import (
    load_ime_environment_file,
    plan_input_method_environment,
)


PACKAGE_ROOT = Path(__file__).resolve().parents[1]


def test_wsl_ibus_plan_forces_xcb_without_overwriting_explicit_values():
    planned = plan_input_method_environment({}, wsl=True)
    assert planned["QT_QPA_PLATFORM"] == "xcb"
    assert planned["QT_IM_MODULE"] == "ibus"
    assert planned["QT_IM_MODULES"] == "ibus;compose"
    assert planned["GTK_IM_MODULE"] == "ibus"
    assert planned["XMODIFIERS"] == "@im=ibus"

    explicit = plan_input_method_environment(
        {
            "QT_QPA_PLATFORM": "wayland",
            "QT_IM_MODULE": "custom",
            "MACROBOT_UI_IME_FORCE_XCB": "false",
        },
        wsl=True,
    )
    assert explicit["QT_QPA_PLATFORM"] == "wayland"
    assert explicit["QT_IM_MODULE"] == "custom"


def test_ime_env_file_loads_only_whitelisted_values(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "OPENAI_API_KEY=must-not-be-loaded\n"
        "MACROBOT_UI_IME_BACKEND=ibus\n"
        "QT_IM_MODULE=ibus\n"
        "XMODIFIERS='@im=ibus'\n",
        encoding="utf-8",
    )
    values: dict[str, str] = {}
    load_ime_environment_file(values, env_file)
    assert values == {
        "MACROBOT_UI_IME_BACKEND": "ibus",
        "QT_IM_MODULE": "ibus",
        "XMODIFIERS": "@im=ibus",
    }


def test_qt_input_method_is_prepared_before_ui_import():
    bootstrap = (
        PACKAGE_ROOT / "macrobot_ui" / "runtime_bootstrap.py"
    ).read_text(encoding="utf-8")
    app = (PACKAGE_ROOT / "macrobot_ui" / "app.py").read_text(
        encoding="utf-8"
    )
    setup = (PACKAGE_ROOT / "setup.py").read_text(encoding="utf-8")

    assert "prepare_input_method_environment(start_daemon=True)" in bootstrap
    assert "macrobot_ui_ime_check" in setup
    assert "WA_InputMethodEnabled" in app
    assert "setInputMethodHints" in app
    assert "keyPressEvent" not in app
    assert "eventFilter" not in app
