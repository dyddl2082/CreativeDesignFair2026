from __future__ import annotations

from PySide6.QtCore import QRect, QSize, Qt, QTimer
from PySide6.QtGui import QFontMetrics
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLayout,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from .models import ResponseStatus


class WrappingLabel(QLabel):
    """A QLabel with an explicit and stable height-for-width contract."""

    def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.setTextFormat(Qt.TextFormat.PlainText)
        self.setWordWrap(True)
        policy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        policy.setHeightForWidth(True)
        self.setSizePolicy(policy)

    def hasHeightForWidth(self) -> bool:  # noqa: N802 - Qt virtual name
        return True

    def heightForWidth(self, width: int) -> int:  # noqa: N802 - Qt virtual name
        margins = self.contentsMargins()
        content_width = max(1, int(width) - margins.left() - margins.right())
        flags = (
            Qt.TextFlag.TextWordWrap
            | Qt.TextFlag.TextWrapAnywhere
            | Qt.TextFlag.TextExpandTabs
        )
        bounds = QFontMetrics(self.font()).boundingRect(
            QRect(0, 0, content_width, 1_000_000),
            flags,
            self.text(),
        )
        return max(
            QFontMetrics(self.font()).lineSpacing(),
            bounds.height(),
        ) + margins.top() + margins.bottom() + 2

    def sizeHint(self) -> QSize:  # noqa: N802 - Qt virtual name
        base = super().sizeHint()
        width = max(1, self.width() if self.width() > 1 else base.width())
        return QSize(base.width(), self.heightForWidth(width))

    def minimumSizeHint(self) -> QSize:  # noqa: N802 - Qt virtual name
        width = max(1, self.width())
        return QSize(0, self.heightForWidth(width))

    def setText(self, text: str) -> None:  # noqa: N802 - Qt virtual name
        super().setText(text)
        self.updateGeometry()


class MessageBubble(QFrame):
    MIN_WIDTH = 220
    MAX_WIDTH = 780
    HORIZONTAL_PADDING = 28

    def __init__(
        self,
        role: str,
        text: str,
        status: ResponseStatus | None = None,
    ) -> None:
        super().__init__()
        self._text = text
        self._is_user = role == "user"
        self.setObjectName("userBubble" if self._is_user else "assistantBubble")
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(14, 11, 14, 11)
        self._layout.setSpacing(6)

        self.header = QLabel("사용자" if self._is_user else "MacRobot 에이전트")
        self.header.setObjectName("bubbleHeader")
        self._layout.addWidget(self.header)

        self.badge: QLabel | None = None
        if status is not None:
            self.badge = QLabel(status.value)
            self.badge.setObjectName(f"badge_{status.value}")
            self.badge.setSizePolicy(
                QSizePolicy.Policy.Maximum,
                QSizePolicy.Policy.Fixed,
            )
            self._layout.addWidget(self.badge, alignment=Qt.AlignmentFlag.AlignLeft)

        self.body = WrappingLabel(text)
        self.body.setObjectName("bubbleText")
        self.body.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self._layout.addWidget(self.body)

    def reflow(self, viewport_width: int) -> None:
        available = max(140, int(viewport_width) - 12)
        maximum = min(self.MAX_WIDTH, max(140, int(available * 0.78)))
        minimum = min(self.MIN_WIDTH, maximum)

        body_metrics = QFontMetrics(self.body.font())
        header_metrics = QFontMetrics(self.header.font())
        natural = max(
            [header_metrics.horizontalAdvance(self.header.text())]
            + [
                body_metrics.horizontalAdvance(line)
                for line in self._text.splitlines() or [""]
            ]
        )
        if self.badge is not None:
            natural = max(
                natural,
                QFontMetrics(self.badge.font()).horizontalAdvance(self.badge.text()),
            )
        bubble_width = min(maximum, max(minimum, natural + self.HORIZONTAL_PADDING))
        content_width = max(1, bubble_width - self.HORIZONTAL_PADDING)

        self.setFixedWidth(bubble_width)
        self.body.setFixedWidth(content_width)
        self.body.setMinimumHeight(self.body.heightForWidth(content_width))
        self._layout.invalidate()
        self._layout.activate()
        self.setMinimumHeight(self._layout.sizeHint().height())
        self.updateGeometry()

    def text_is_fully_visible(self) -> bool:
        return self.body.height() >= self.body.heightForWidth(self.body.width())


class ChatTranscript(QScrollArea):
    """Scrollable chat transcript with stable row-owned bubble geometry."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)

        self._content = QWidget()
        self._content.setObjectName("chatContent")
        self._layout = QVBoxLayout(self._content)
        self._layout.setSizeConstraint(QLayout.SizeConstraint.SetMinAndMaxSize)
        self._layout.setContentsMargins(4, 4, 4, 4)
        self._layout.setSpacing(12)
        self._layout.addStretch(1)
        self.setWidget(self._content)

        self._bubbles: list[MessageBubble] = []
        self._rows: list[QWidget] = []

    @property
    def bubbles(self) -> tuple[MessageBubble, ...]:
        return tuple(self._bubbles)

    def add_message(
        self,
        role: str,
        text: str,
        status: ResponseStatus | None = None,
    ) -> MessageBubble:
        bubble = MessageBubble(role, text, status)
        row = QWidget(self._content)
        row.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(0)
        if role == "user":
            row_layout.addStretch(1)
            row_layout.addWidget(bubble)
        else:
            row_layout.addWidget(bubble)
            row_layout.addStretch(1)
        self._layout.insertWidget(self._layout.count() - 1, row)
        self._bubbles.append(bubble)
        self._rows.append(row)
        QTimer.singleShot(0, self.reflow)
        QTimer.singleShot(0, self.scroll_to_bottom)
        return bubble

    def clear_messages(self) -> None:
        for row in self._rows:
            row.deleteLater()
        self._rows.clear()
        self._bubbles.clear()
        while self._layout.count() > 1:
            self._layout.takeAt(0)
        self._layout.invalidate()
        self._content.updateGeometry()

    def resizeEvent(self, event) -> None:  # noqa: N802 - Qt virtual name
        super().resizeEvent(event)
        QTimer.singleShot(0, self.reflow)

    def reflow(self) -> None:
        width = self.viewport().width()
        if width <= 0:
            return
        for bubble in self._bubbles:
            bubble.reflow(width)
        for row in self._rows:
            row.updateGeometry()
        self._layout.invalidate()
        self._layout.activate()
        self._content.adjustSize()
        self._content.updateGeometry()

    def scroll_to_bottom(self) -> None:
        bar = self.verticalScrollBar()
        bar.setValue(bar.maximum())
