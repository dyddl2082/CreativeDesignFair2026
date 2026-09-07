from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_no_duplicate_executable_app_module():
    assert not (ROOT / "app.py").exists()
    assert (ROOT / "macrobot_ui" / "app.py").is_file()


def test_secret_env_is_not_packaged():
    assert not (ROOT / ".env").exists()
    assert (ROOT / ".env.example").is_file()


def test_layout_fix_has_no_padding_hack():
    widgets = (ROOT / "macrobot_ui" / "widgets.py").read_text(encoding="utf-8")
    assert "FORCED_BUBBLE_HEIGHT_PADDING" not in widgets
    assert "TextWrapAnywhere" in widgets
    assert "row_layout.addWidget(bubble)" in widgets
    assert "setFixedHeight" not in widgets


def test_frontend_and_backend_entrypoints_exist():
    setup = (ROOT / "setup.py").read_text(encoding="utf-8")
    assert "macrobot_ui = macrobot_ui.runtime_bootstrap:main" in setup
    assert "macrobot_ui_backend = macrobot_ui.backend_node:main" in setup
