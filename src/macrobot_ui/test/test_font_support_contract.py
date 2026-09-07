from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_no_font_binary_is_bundled():
    forbidden = {".ttf", ".otf", ".ttc", ".woff", ".woff2"}
    bundled = [path for path in ROOT.rglob("*") if path.suffix.lower() in forbidden]
    assert bundled == []


def test_font_resolver_checks_real_hangul_glyphs():
    source = (ROOT / "macrobot_ui" / "font_support.py").read_text(
        encoding="utf-8"
    )
    assert "QRawFont" in source
    assert "supportsCharacter" in source
    assert "Noto Sans CJK KR" in source
    assert "Noto Sans Mono CJK KR" in source
    assert "MACROBOT_UI_FONT_FAMILY" in source
    assert "MACROBOT_CODE_FONT_FAMILY" in source
    assert "/mnt/c/Windows/Fonts/malgun.ttf" in source


def test_qss_does_not_override_resolved_font_family():
    source = (ROOT / "macrobot_ui" / "app.py").read_text(encoding="utf-8")
    assert "font-family:" not in source
    assert "self.code_editor.setFont" in source


def test_main_applies_font_selection_before_window_creation():
    source = (ROOT / "macrobot_ui" / "main.py").read_text(encoding="utf-8")
    configure_at = source.index("configure_application_fonts(app)")
    window_at = source.index("MainWindow(config, bridge")
    assert configure_at < window_at


def test_font_check_entrypoint_exists():
    setup = (ROOT / "setup.py").read_text(encoding="utf-8")
    assert (
        "macrobot_ui_font_check = "
        "macrobot_ui.runtime_bootstrap:font_check_main"
    ) in setup
