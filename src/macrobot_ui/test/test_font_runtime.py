from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication

from macrobot_ui.font_support import (
    configure_application_fonts,
    family_supports_text,
)


def test_selected_fonts_render_korean_when_system_fonts_exist():
    app = QApplication.instance() or QApplication([])
    selection = configure_application_fonts(app)
    assert family_supports_text(selection.ui_family)
    assert family_supports_text(selection.code_family)
    assert app.font().family() == selection.ui_family
