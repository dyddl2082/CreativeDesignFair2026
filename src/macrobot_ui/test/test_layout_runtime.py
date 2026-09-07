from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication

from macrobot_ui.models import ResponseStatus
from macrobot_ui.widgets import MessageBubble


def test_long_korean_message_is_not_clipped():
    app = QApplication.instance() or QApplication([])
    text = (
        "물체를 찾은 다음 카메라로 위치와 방향을 다시 확인하고, "
        "검증된 작업만 실행해 주세요. " * 30
    )
    bubble = MessageBubble("assistant", text, ResponseStatus.CODE)
    bubble.reflow(440)
    bubble.show()
    app.processEvents()
    assert bubble.text_is_fully_visible()
    assert bubble.height() >= bubble.minimumSizeHint().height()
