from __future__ import annotations

from dataclasses import asdict
import json
import secrets
import time
from typing import Any

from PySide6.QtCore import QObject, QThread, QTimer, Qt, Signal, Slot
from PySide6.QtGui import QColor, QFont, QSyntaxHighlighter, QTextCharFormat
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from .code_validator import GeneratedCodeValidator
from .config import AppConfig
from .models import (
    BackendState,
    ChatTurn,
    ParsedResponse,
    ResponseStatus,
    StoredTask,
    ValidationReport,
)
from .openai_service import ApiResponse, OpenAIChatService
from .prompt_repository import PromptRepository
from .response_parser import parse_response
from .ros_protocol import (
    HELD_RESET_REQUEST_SCHEMA,
    STOP_REQUEST_SCHEMA,
    make_task_request,
)
from .storage import TaskStorage
from .widgets import ChatTranscript, WrappingLabel


class ApiWorker(QObject):
    completed = Signal(object)
    failed = Signal(str)

    def __init__(self, service: OpenAIChatService, user_message: str) -> None:
        super().__init__()
        self._service = service
        self._user_message = user_message

    @Slot()
    def run(self) -> None:
        try:
            self.completed.emit(self._service.reply(self._user_message))
        except Exception as error:
            self.failed.emit(f"{type(error).__name__}: {error}")


class PythonHighlighter(QSyntaxHighlighter):
    _KEYWORDS = {
        "def",
        "if",
        "else",
        "elif",
        "for",
        "while",
        "return",
        "in",
        "not",
        "and",
        "or",
        "True",
        "False",
        "None",
        "match",
        "case",
        "break",
        "continue",
    }

    def __init__(self, document) -> None:
        super().__init__(document)
        self._keyword_format = QTextCharFormat()
        self._keyword_format.setForeground(QColor("#C792EA"))
        self._keyword_format.setFontWeight(QFont.Weight.DemiBold)
        self._comment_format = QTextCharFormat()
        self._comment_format.setForeground(QColor("#73808C"))
        self._string_format = QTextCharFormat()
        self._string_format.setForeground(QColor("#C3E88D"))

    def highlightBlock(self, text: str) -> None:  # noqa: N802
        comment_index = text.find("#")
        if comment_index >= 0:
            self.setFormat(
                comment_index,
                len(text) - comment_index,
                self._comment_format,
            )
        for keyword in self._KEYWORDS:
            start = 0
            while True:
                start = text.find(keyword, start)
                if start < 0:
                    break
                before = text[start - 1] if start else " "
                end = start + len(keyword)
                after = text[end] if end < len(text) else " "
                if not (before.isalnum() or before == "_") and not (
                    after.isalnum() or after == "_"
                ):
                    self.setFormat(start, len(keyword), self._keyword_format)
                start = end
        in_string = False
        quote = ""
        string_start = 0
        for index, char in enumerate(text):
            if char in {"'", '"'} and (index == 0 or text[index - 1] != "\\"):
                if not in_string:
                    in_string, quote, string_start = True, char, index
                elif char == quote:
                    self.setFormat(
                        string_start,
                        index - string_start + 1,
                        self._string_format,
                    )
                    in_string = False


class ChatPane(QWidget):
    send_requested = Signal(str)

    def __init__(self, max_input_chars: int) -> None:
        super().__init__()
        self.max_input_chars = int(max_input_chars)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        title = QLabel("작업 대화")
        title.setObjectName("panelTitle")
        subtitle = WrappingLabel(
            "명령을 구체화한 뒤 검증 가능한 Robot API 코드로 변환합니다."
        )
        subtitle.setObjectName("panelSubtitle")
        root.addWidget(title)
        root.addWidget(subtitle)

        self.transcript = ChatTranscript()
        root.addWidget(self.transcript, 1)

        composer = QFrame()
        composer.setObjectName("composer")
        composer_layout = QVBoxLayout(composer)
        composer_layout.setContentsMargins(12, 10, 10, 10)
        composer_layout.setSpacing(6)

        input_row = QHBoxLayout()
        input_row.setSpacing(10)
        self.input = QPlainTextEdit()
        self.input.setPlaceholderText(
            "예: 주변에서 지우개를 찾고, 정렬한 뒤 잡아서 들어 올려줘."
        )
        self.input.setMinimumHeight(145)
        self.input.setMaximumHeight(230)
        self.input.setObjectName("messageInput")
        # Keep standard Qt pre-edit/commit handling enabled for Korean IMEs.
        self.input.setAttribute(
            Qt.WidgetAttribute.WA_InputMethodEnabled,
            True,
        )
        self.input.setInputMethodHints(Qt.InputMethodHint.ImhNone)
        self.input.textChanged.connect(self._update_input_count)
        input_row.addWidget(self.input, 1)

        self.send_button = QPushButton("전송")
        self.send_button.setObjectName("primaryButton")
        self.send_button.setFixedWidth(90)
        self.send_button.clicked.connect(self._emit_message)
        input_row.addWidget(self.send_button, alignment=Qt.AlignmentFlag.AlignBottom)
        composer_layout.addLayout(input_row)

        self.char_count = QLabel(f"0 / {self.max_input_chars}자")
        self.char_count.setObjectName("charCount")
        composer_layout.addWidget(self.char_count, alignment=Qt.AlignmentFlag.AlignRight)
        root.addWidget(composer)

    def add_message(
        self,
        role: str,
        text: str,
        status: ResponseStatus | None = None,
    ) -> None:
        self.transcript.add_message(role, text, status)

    def clear_messages(self) -> None:
        self.transcript.clear_messages()

    def set_busy(self, busy: bool) -> None:
        self.input.setDisabled(busy)
        self.send_button.setDisabled(busy)
        self.send_button.setText("생성 중…" if busy else "전송")

    def _update_input_count(self) -> None:
        text = self.input.toPlainText()
        if len(text) > self.max_input_chars:
            cursor = self.input.textCursor()
            position = cursor.position()
            self.input.blockSignals(True)
            self.input.setPlainText(text[: self.max_input_chars])
            self.input.blockSignals(False)
            cursor.setPosition(min(position, self.max_input_chars))
            self.input.setTextCursor(cursor)
            text = self.input.toPlainText()
        self.char_count.setText(f"{len(text)} / {self.max_input_chars}자")

    def _emit_message(self) -> None:
        text = self.input.toPlainText().strip()
        if text:
            self.input.clear()
            self.send_requested.emit(text)


class RobotStatusPane(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("robotStatusCard")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)

        title = QLabel("ROS 2 / 로봇 상태")
        title.setObjectName("cardTitle")
        layout.addWidget(title)

        self.backend = WrappingLabel("UI backend: 연결 대기")
        self.gateway = WrappingLabel("Action Gateway: 연결 대기")
        self.robot = WrappingLabel("로봇 작업: 상태 대기")
        self.last_event = WrappingLabel("최근 이벤트: 없음")
        for label in (self.backend, self.gateway, self.robot, self.last_event):
            label.setObjectName("statusLine")
            layout.addWidget(label)

    def set_backend(self, state: BackendState) -> None:
        self.backend.setText(
            "UI backend: 연결됨"
            if state.reachable
            else f"UI backend: 연결 안 됨 · {state.detail}"
        )
        if state.gateway_reachable:
            motion = "실제 구동" if state.gateway_real_motion_enabled else "DRY-RUN"
            permission = "실행 허용" if state.allow_execution else "실행 차단"
            self.gateway.setText(f"Action Gateway: {motion} · {permission}")
        else:
            self.gateway.setText("Action Gateway: socket 연결 안 됨")

    def set_task_status(self, payload: dict[str, Any]) -> None:
        event = str(payload.get("event", "unknown"))
        state = str(payload.get("state", ""))
        request_id = str(payload.get("request_id", ""))
        self.robot.setText(f"UI 작업: {state or event} · {request_id}")
        self.last_event.setText(f"최근 이벤트: {event}")

    def set_telemetry(self, label: str, payload: dict[str, Any]) -> None:
        event = str(payload.get("event", payload.get("state", "message")))
        object_name = str(payload.get("object_name", ""))
        suffix = f" · {object_name}" if object_name else ""
        self.last_event.setText(f"최근 로봇 이벤트: {label}/{event}{suffix}")
        if label == "stored_pick":
            action_state = payload.get("action_state", payload.get("state", ""))
            phase = payload.get("phase", "")
            self.robot.setText(f"로봇 작업: {action_state or event} · {phase}")


class CodePane(QWidget):
    validate_requested = Signal()
    save_requested = Signal()
    copy_requested = Signal()
    backend_validate_requested = Signal()
    execute_requested = Signal()
    held_reset_requested = Signal()
    stop_requested = Signal()

    arm_home_requested = Signal()
    def __init__(self, code_font: QFont | None = None) -> None:
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        title_row = QHBoxLayout()
        title = QLabel("생성 코드")
        title.setObjectName("panelTitle")
        title_row.addWidget(title)
        title_row.addStretch(1)
        self.status_badge = QLabel("대화 대기")
        self.status_badge.setObjectName("statusBadge")
        title_row.addWidget(self.status_badge)
        root.addLayout(title_row)

        self.code_editor = QPlainTextEdit()
        self.code_editor.setObjectName("codeEditor")
        if code_font is not None:
            self.code_editor.setFont(QFont(code_font))
        self.code_editor.setReadOnly(True)
        self.code_editor.setPlaceholderText("CODE 응답이 생성되면 여기에 표시됩니다.")
        self.code_editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self._highlighter = PythonHighlighter(self.code_editor.document())
        root.addWidget(self.code_editor, 1)

        report_frame = QFrame()
        report_frame.setObjectName("validationCard")
        report_layout = QVBoxLayout(report_frame)
        report_layout.setContentsMargins(14, 12, 14, 12)
        report_label = QLabel("검증 결과")
        report_label.setObjectName("cardTitle")
        self.report = WrappingLabel("생성된 코드가 없습니다.")
        self.report.setObjectName("validationReport")
        report_layout.addWidget(report_label)
        report_layout.addWidget(self.report)
        root.addWidget(report_frame)

        first_row = QHBoxLayout()
        self.copy_button = self._button("복사", "secondaryButton", self.copy_requested)
        self.validate_button = self._button(
            "로컬 검증", "secondaryButton", self.validate_requested
        )
        self.save_button = self._button("저장", "secondaryButton", self.save_requested)
        self.backend_validate_button = self._button(
            "Pi 검증", "secondaryButton", self.backend_validate_requested
        )
        for button in (
            self.copy_button,
            self.validate_button,
            self.save_button,
            self.backend_validate_button,
        ):
            first_row.addWidget(button)
        root.addLayout(first_row)

        second_row = QHBoxLayout()
        self.execute_button = self._button(
            "승인 후 실행", "primaryButton", self.execute_requested
        )
        self.held_reset_button = self._button(
            "보유 상태 비우기", "secondaryButton", self.held_reset_requested
        )
        self.arm_home_button = self._button(
            "로봇팔 HOME", "secondaryButton", self.arm_home_requested
        )
        self.stop_button = self._button("긴급 STOP", "dangerButton", self.stop_requested)
        second_row.addWidget(self.execute_button, 2)
        second_row.addWidget(self.held_reset_button, 1)
        second_row.addWidget(self.arm_home_button, 1)
        second_row.addWidget(self.stop_button, 1)
        root.addLayout(second_row)
        self.set_code("")
        self.set_backend_availability(False, False, False)

    @staticmethod
    def _button(text: str, object_name: str, signal: Signal) -> QPushButton:
        button = QPushButton(text)
        button.setObjectName(object_name)
        button.clicked.connect(lambda _checked=False: signal.emit())
        return button

    def set_code(self, code: str) -> None:
        self.code_editor.setPlainText(code)
        has_code = bool(code.strip())
        self.copy_button.setEnabled(has_code)
        self.validate_button.setEnabled(has_code)
        self.save_button.setEnabled(False)
        self.backend_validate_button.setEnabled(False)
        self.execute_button.setEnabled(False)

    def set_status(self, label: str, kind: str = "neutral") -> None:
        self.status_badge.setText(label)
        self.status_badge.setProperty("kind", kind)
        self.status_badge.style().unpolish(self.status_badge)
        self.status_badge.style().polish(self.status_badge)

    def show_report(self, report: ValidationReport | None) -> None:
        if report is None:
            self.report.setText("생성된 코드가 없습니다.")
            self.save_button.setEnabled(False)
            return
        if report.is_valid:
            calls = ", ".join(report.robot_calls) if report.robot_calls else "분석됨"
            self.report.setText(f"{report.summary}\nRobot API: {calls}")
            self.save_button.setEnabled(True)
            return
        details = "\n".join(f"• {issue.display()}" for issue in report.issues)
        self.report.setText(f"{report.summary}\n{details}")
        self.save_button.setEnabled(False)

    def set_backend_availability(
        self,
        backend_reachable: bool,
        allow_execution: bool,
        local_valid: bool,
        request_pending: bool = False,
    ) -> None:
        has_code = bool(self.code_editor.toPlainText().strip())
        self.backend_validate_button.setEnabled(
            backend_reachable and has_code and local_valid and not request_pending
        )
        self.execute_button.setEnabled(
            backend_reachable
            and allow_execution
            and has_code
            and local_valid
            and not request_pending
        )
        self.held_reset_button.setEnabled(backend_reachable and not request_pending)
        self.arm_home_button.setEnabled(
            backend_reachable and allow_execution and not request_pending
        )
        self.stop_button.setEnabled(backend_reachable)


class MainWindow(QMainWindow):
    def __init__(
        self,
        config: AppConfig,
        ros_bridge,
        code_font: QFont | None = None,
    ) -> None:
        super().__init__()
        self._config = config
        self._ros = ros_bridge
        self._code_font = QFont(code_font) if code_font is not None else None
        self._instructions = PromptRepository(config.knowledge_dir).build_instructions()
        self._service = OpenAIChatService(config, self._instructions)
        self._validator = GeneratedCodeValidator(config.knowledge_dir / "llm_bundle.yaml")
        self._storage = TaskStorage(config.tasks_dir, config.run_result_dir)

        self._history: list[ChatTurn] = []
        self._last_user_request = ""
        self._current_response: ParsedResponse | None = None
        self._current_report: ValidationReport | None = None
        self._stored_task: StoredTask | None = None
        self._api_thread: QThread | None = None
        self._api_worker: ApiWorker | None = None

        self._backend_state = BackendState()
        self._backend_last_seen = 0.0
        self._pending_payload: dict[str, Any] | None = None
        self._pending_request_id = ""
        self._held_reset_pending_id = ""
        self._pending_acknowledged = False
        self._pending_started = 0.0
        self._request_timer = QTimer(self)
        self._request_timer.setInterval(config.request_retry_period_ms)
        self._request_timer.timeout.connect(self._retry_pending_request)
        self._backend_watchdog = QTimer(self)
        self._backend_watchdog.setInterval(1000)
        self._backend_watchdog.timeout.connect(self._check_backend_staleness)
        self._backend_watchdog.start()

        self.setWindowTitle("MacRobot ROS 2 제어 콘솔")
        self.resize(1480, 900)
        self.setMinimumSize(1080, 700)
        self._build_ui()
        self._connect_ros()
        self._start_new_chat()

    def _build_ui(self) -> None:
        central = QWidget()
        central.setObjectName("central")
        outer = QVBoxLayout(central)
        outer.setContentsMargins(24, 18, 24, 20)
        outer.setSpacing(14)

        top_bar = QHBoxLayout()
        mark = QLabel("●")
        mark.setObjectName("robotMark")
        top_bar.addWidget(mark)
        title_group = QVBoxLayout()
        title = QLabel("MacRobot ROS 2 제어 콘솔")
        title.setObjectName("appTitle")
        subtitle = WrappingLabel(
            "자연어 → 제한 Python → Pi 실행 백엔드 → Robot Action Gateway"
        )
        subtitle.setObjectName("appSubtitle")
        title_group.addWidget(title)
        title_group.addWidget(subtitle)
        top_bar.addLayout(title_group)
        top_bar.addStretch(1)
        self.api_state = QLabel(
            "API 키 필요" if not self._config.api_ready else f"모델: {self._config.model}"
        )
        self.api_state.setObjectName("apiState")
        top_bar.addWidget(self.api_state)
        new_chat = QPushButton("새 대화")
        new_chat.setObjectName("ghostButton")
        new_chat.clicked.connect(self._start_new_chat)
        top_bar.addWidget(new_chat)
        outer.addLayout(top_bar)

        self.robot_status = RobotStatusPane()
        outer.addWidget(self.robot_status)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.chat_pane = ChatPane(self._config.max_input_chars)
        self.code_pane = CodePane(self._code_font)
        splitter.addWidget(self.chat_pane)
        splitter.addWidget(self.code_pane)
        splitter.setSizes([790, 650])
        splitter.setHandleWidth(16)
        splitter.setChildrenCollapsible(False)
        outer.addWidget(splitter, 1)

        footer = WrappingLabel(
            "실행은 UI가 로봇 토픽을 직접 구동하지 않고, Pi backend가 승인된 코드 해시를 "
            "재검증한 뒤 robot_code_runner와 Action Gateway에 위임합니다."
        )
        footer.setObjectName("footer")
        outer.addWidget(footer)
        self.setCentralWidget(central)

        self.chat_pane.send_requested.connect(self._send_message)
        self.code_pane.copy_requested.connect(self._copy_code)
        self.code_pane.validate_requested.connect(self._validate_code)
        self.code_pane.save_requested.connect(self._save_code)
        self.code_pane.backend_validate_requested.connect(self._backend_validate)
        self.code_pane.execute_requested.connect(self._execute_code)
        self.code_pane.arm_home_requested.connect(
            self._request_arm_home
        )
        self.code_pane.held_reset_requested.connect(self._request_held_reset)
        self.code_pane.stop_requested.connect(self._request_stop)

    def _connect_ros(self) -> None:
        signals = self._ros.signals
        signals.backend_status.connect(self._on_backend_status)
        signals.task_status.connect(self._on_task_status)
        signals.task_result.connect(self._on_task_result)
        signals.telemetry.connect(self._on_telemetry)
        signals.ros_error.connect(self._on_ros_error)

    def _start_new_chat(self) -> None:
        if self._api_thread and self._api_thread.isRunning():
            return
        self._history.clear()
        self._service.reset_conversation()
        self._last_user_request = ""
        self._current_response = None
        self._current_report = None
        self._stored_task = None
        self.chat_pane.clear_messages()
        self.chat_pane.add_message(
            "assistant",
            "작업을 말씀해 주세요. 코드를 생성한 뒤 로컬 검증, Pi 검증, 정확한 코드 해시 승인 순서로 실행할 수 있습니다.",
        )
        self.code_pane.set_code("")
        self.code_pane.set_status("대화 대기")
        self.code_pane.show_report(None)
        self._refresh_action_buttons()

    def _send_message(self, text: str) -> None:
        if self._api_thread and self._api_thread.isRunning():
            return
        self._last_user_request = text
        self._history.append(ChatTurn(role="user", text=text))
        self.chat_pane.add_message("user", text)
        self.chat_pane.set_busy(True)
        self.code_pane.set_status("응답 생성 중", "pending")

        self._api_thread = QThread(self)
        self._api_worker = ApiWorker(self._service, text)
        self._api_worker.moveToThread(self._api_thread)
        self._api_thread.started.connect(self._api_worker.run)
        self._api_worker.completed.connect(self._handle_api_response)
        self._api_worker.failed.connect(self._handle_api_error)
        self._api_worker.completed.connect(self._api_thread.quit)
        self._api_worker.failed.connect(self._api_thread.quit)
        self._api_thread.finished.connect(self._api_worker.deleteLater)
        self._api_thread.finished.connect(self._api_thread.deleteLater)
        self._api_thread.finished.connect(self._clear_api_worker)
        self._api_thread.start()

    @Slot(object)
    def _handle_api_response(self, api_response: ApiResponse) -> None:
        parsed = parse_response(api_response.text)
        self._history.append(ChatTurn(role="assistant", text=api_response.text))
        self._current_response = parsed
        self._current_report = None
        self._stored_task = None
        self.chat_pane.add_message("assistant", _assistant_summary(parsed), parsed.status)
        if parsed.is_code:
            self.code_pane.set_code(parsed.code)
            self._validate_code()
            return
        self.code_pane.set_code("")
        self.code_pane.show_report(None)
        self.code_pane.set_status(
            _status_label(parsed.status),
            _status_kind(parsed.status),
        )
        self._refresh_action_buttons()

    @Slot(str)
    def _handle_api_error(self, message: str) -> None:
        self.chat_pane.add_message(
            "assistant",
            f"API 요청을 완료하지 못했습니다.\n{message}",
            ResponseStatus.GENERATION_ERROR,
        )
        self.code_pane.set_status("API 연결 실패", "error")

    @Slot()
    def _clear_api_worker(self) -> None:
        self.chat_pane.set_busy(False)
        self._api_worker = None
        self._api_thread = None

    def _validate_code(self) -> None:
        code = self.code_pane.code_editor.toPlainText().strip()
        if not code:
            self.code_pane.show_report(None)
            self._current_report = None
            self._refresh_action_buttons()
            return
        report = self._validator.validate(code)
        self._current_report = report
        self._stored_task = None
        self.code_pane.show_report(report)
        self.code_pane.set_status(
            "검증 완료" if report.is_valid else "검증 실패",
            "success" if report.is_valid else "error",
        )
        self._refresh_action_buttons()

    def _copy_code(self) -> None:
        code = self.code_pane.code_editor.toPlainText().strip()
        if code:
            QApplication.clipboard().setText(code)
            self.code_pane.set_status("코드 복사됨", "success")

    def _metadata(self) -> dict[str, Any]:
        response = self._current_response
        report = self._current_report
        return {
            "request": self._last_user_request,
            "status": response.status.value if response else "",
            "object_bindings": response.object_bindings if response else "",
            "assumptions": response.assumptions if response else "",
            "raw_response": response.raw_text if response else "",
            "validation": [asdict(issue) for issue in report.issues] if report else [],
            "validator": report.validator_name if report else "",
            "conversation": [asdict(turn) for turn in self._history],
        }

    def _ensure_saved_task(self) -> StoredTask | None:
        if not self._current_report or not self._current_report.is_valid:
            QMessageBox.warning(
                self,
                "저장할 수 없음",
                "검증을 통과한 CODE 응답만 저장하거나 전송할 수 있습니다.",
            )
            return None
        code = self.code_pane.code_editor.toPlainText()
        if self._stored_task is None:
            self._stored_task = self._storage.save(
                self._last_user_request,
                code,
                self._metadata(),
            )
        return self._stored_task

    def _save_code(self) -> None:
        stored = self._ensure_saved_task()
        if stored is None:
            return
        self.code_pane.set_status("저장 완료", "success")
        QMessageBox.information(
            self,
            "저장 완료",
            f"코드와 메타데이터를 저장했습니다.\n\n{stored.code_path}\n{stored.metadata_path}",
        )

    def _backend_validate(self) -> None:
        stored = self._ensure_saved_task()
        if stored is None:
            return
        self._submit_backend("validate", approved=False, stored=stored)

    def _execute_code(self) -> None:
        stored = self._ensure_saved_task()
        if stored is None:
            return
        motion = (
            "실제 구동 모드"
            if self._backend_state.gateway_real_motion_enabled
            else "Gateway DRY-RUN 모드"
        )
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Warning)
        box.setWindowTitle("정확한 코드 실행 승인")
        box.setText(
            f"현재 Gateway는 {motion}입니다.\n"
            "아래 SHA-256의 정확한 코드를 실행하도록 승인하시겠습니까?"
        )
        box.setInformativeText(stored.source_sha256)
        box.setDetailedText(self.code_pane.code_editor.toPlainText())
        box.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        box.setDefaultButton(QMessageBox.StandardButton.No)
        if box.exec() != QMessageBox.StandardButton.Yes:
            return
        self._submit_backend("execute", approved=True, stored=stored)

    def _request_arm_home(self) -> None:
        # Move the arm to HOME through the validated/approved Robot API path.
        if self._pending_payload is not None:
            QMessageBox.warning(
                self,
                "요청 진행 중",
                "이전 Pi 요청이 아직 진행 중입니다.",
            )
            return
        if not self._backend_state.reachable or not self._backend_state.allow_execution:
            QMessageBox.warning(
                self,
                "HOME 실행 불가",
                "Pi backend 연결 및 실행 허용 상태를 확인하세요.",
            )
            return

        code = (
            "def main() -> TaskOutcome:\n"
            "    action = robot.SET_ARM_JOINTS(\n"
            "        arm_lift_deg=0.0,\n"
            "        wrist_pitch_deg=0.0,\n"
            "    )\n"
            "    result = robot.WAIT_ACTION(\n"
            "        action,\n"
            "        timeout_s=25.0,\n"
            "    )\n"
            "    if result.state != ActionState.SUCCEEDED:\n"
            "        return TaskOutcome(\n"
            "            status=TaskStatus.FAILED,\n"
            "            message=result.error_message or \"로봇팔 HOME 이동에 실패했습니다.\",\n"
            "        )\n"
            "    return TaskOutcome(\n"
            "        status=TaskStatus.SUCCEEDED,\n"
            "        message=\"로봇팔을 HOME 위치로 이동했습니다.\",\n"
            "    )\n"
        )
        self._last_user_request = "UI quick action: robot arm HOME"
        self._current_response = None
        self._current_report = None
        self._stored_task = None
        self.code_pane.set_code(code)
        self._validate_code()
        if self._current_report is None or not self._current_report.is_valid:
            QMessageBox.critical(
                self,
                "HOME 코드 검증 실패",
                "SET_ARM_JOINTS 기반 HOME 코드가 로컬 검증을 통과하지 못했습니다.",
            )
            return

        self._execute_code()

    def _submit_backend(
        self,
        mode: str,
        *,
        approved: bool,
        stored: StoredTask,
    ) -> None:
        if self._pending_payload is not None:
            QMessageBox.warning(self, "요청 진행 중", "이전 Pi 요청이 아직 진행 중입니다.")
            return
        request_id = (
            f"ui-{mode}-{int(time.time() * 1000)}-{secrets.token_hex(3)}"
        )
        metadata = self._metadata()
        metadata.update(
            {
                "frontend_code_path": str(stored.code_path),
                "frontend_metadata_path": str(stored.metadata_path),
            }
        )
        payload = make_task_request(
            request_id=request_id,
            mode=mode,
            code=self.code_pane.code_editor.toPlainText(),
            approved=approved,
            metadata=metadata,
        )
        if payload["source_sha256"] != stored.source_sha256:
            QMessageBox.critical(
                self,
                "해시 불일치",
                "저장된 코드와 화면 코드가 달라 전송을 중단했습니다.",
            )
            return
        self._pending_payload = payload
        self._pending_request_id = request_id
        self._pending_acknowledged = False
        self._pending_started = time.monotonic()
        self._ros.publish_task(payload)
        self._request_timer.start()
        self._refresh_action_buttons()
        self.code_pane.set_status(
            "Pi 승인 대기" if mode == "execute" else "Pi 검증 요청",
            "pending",
        )

    def _retry_pending_request(self) -> None:
        if self._pending_payload is None or self._pending_acknowledged:
            self._request_timer.stop()
            return
        elapsed_ms = int((time.monotonic() - self._pending_started) * 1000)
        if elapsed_ms >= self._config.request_ack_timeout_ms:
            self._request_timer.stop()
            request_id = self._pending_request_id
            self._clear_pending_request()
            self.code_pane.set_status("Pi 응답 없음", "error")
            QMessageBox.warning(
                self,
                "Pi backend 응답 없음",
                f"{request_id} 요청의 acknowledgement를 받지 못했습니다.",
            )
            return
        self._ros.publish_task(self._pending_payload)

    def _request_held_reset(self) -> None:
        if not self._backend_state.reachable:
            QMessageBox.warning(self, "UI backend 연결 필요", "Pi UI backend가 연결되어 있지 않습니다.")
            return
        if self._pending_payload is not None or self._held_reset_pending_id:
            return
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Warning)
        box.setWindowTitle("보유 상태 초기화")
        box.setText("실제 그리퍼가 비어 있습니까?")
        box.setInformativeText(
            "확인을 누르면 stored-pick source-of-truth의 held-object 상태를 empty로 바꿉니다. "
            "실제로 물체를 잡고 있는 상태에서는 사용하지 마세요."
        )
        box.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        box.setDefaultButton(QMessageBox.StandardButton.No)
        if box.exec() != QMessageBox.StandardButton.Yes:
            return
        request_id = f"ui-held-clear-{int(time.time() * 1000)}-{secrets.token_hex(3)}"
        self._held_reset_pending_id = request_id
        self._ros.publish_held_reset(
            {
                "schema": HELD_RESET_REQUEST_SCHEMA,
                "request_id": request_id,
                "operator_confirmed_empty": True,
                "created_at_unix_ms": int(time.time() * 1000),
            }
        )
        self.code_pane.set_status("보유 상태 초기화 요청", "pending")
        self._refresh_action_buttons()

    def _request_stop(self) -> None:
        request_id = f"ui-stop-{int(time.time() * 1000)}-{secrets.token_hex(3)}"
        self._ros.publish_stop(
            {
                "schema": STOP_REQUEST_SCHEMA,
                "request_id": request_id,
                "reason": "operator_pressed_ui_stop",
                "created_at_unix_ms": int(time.time() * 1000),
            }
        )
        self.code_pane.set_status("STOP 요청 전송", "error")

    @Slot(object)
    def _on_backend_status(self, payload: dict[str, Any]) -> None:
        self._backend_last_seen = time.monotonic()
        self._backend_state = BackendState(
            reachable=True,
            allow_execution=bool(payload.get("allow_execution", False)),
            gateway_reachable=bool(payload.get("gateway_reachable", False)),
            gateway_real_motion_enabled=bool(
                payload.get("gateway_real_motion_enabled", False)
            ),
            active_request_id=str(payload.get("active_request_id", "")),
            detail=str(payload.get("gateway_error", "")),
            raw=dict(payload),
        )
        self.robot_status.set_backend(self._backend_state)
        self._refresh_action_buttons()

    @Slot(object)
    def _on_task_status(self, payload: dict[str, Any]) -> None:
        self.robot_status.set_task_status(payload)
        request_id = str(payload.get("request_id", ""))
        if request_id == self._pending_request_id and payload.get("event") == "ui_task_acknowledged":
            self._pending_acknowledged = True
            self._request_timer.stop()
            self.code_pane.set_status("Pi가 요청 수락", "pending")

    @Slot(object)
    def _on_task_result(self, payload: dict[str, Any]) -> None:
        request_id = str(payload.get("request_id", ""))
        try:
            path = self._storage.save_backend_result(request_id, payload)
        except Exception:
            path = None
        event = str(payload.get("event", "ui_task_result"))
        if request_id == self._held_reset_pending_id:
            ok = bool(payload.get("ok", False))
            self._held_reset_pending_id = ""
            self.code_pane.set_status(
                "보유 상태 비움" if ok else "보유 상태 초기화 실패",
                "success" if ok else "error",
            )
            self._refresh_action_buttons()
            details = json.dumps(payload, ensure_ascii=False, indent=2)
            if path is not None:
                details += f"\n\n저장 결과: {path}"
            box = QMessageBox(self)
            box.setIcon(
                QMessageBox.Icon.Information if ok else QMessageBox.Icon.Critical
            )
            box.setWindowTitle(event)
            box.setText(
                str(payload.get("message", ""))
                or ("보유 상태가 empty로 동기화되었습니다." if ok else "보유 상태 초기화에 실패했습니다.")
            )
            box.setDetailedText(details)
            box.exec()
            return
        if request_id == self._pending_request_id:
            task_status = str(payload.get("task_status", "")).strip().casefold()
            task_message = str(
                payload.get("task_message", payload.get("message", ""))
            ).strip()
            if event == "ui_task_validated":
                label, kind = "Pi 검증 완료", "success"
                icon = QMessageBox.Icon.Information
                summary = "Pi 검증을 통과했습니다."
            elif event == "ui_task_validation_failed":
                label, kind = "Pi 검증 실패", "error"
                icon = QMessageBox.Icon.Critical
                summary = "Pi 검증에 실패했습니다."
            elif task_status == "succeeded":
                label, kind = "Pi 작업 성공", "success"
                icon = QMessageBox.Icon.Information
                summary = task_message or "로봇 작업이 성공했습니다."
            elif task_status == "partially_succeeded":
                label, kind = "Pi 작업 부분 성공", "error"
                icon = QMessageBox.Icon.Warning
                summary = task_message or "로봇 작업이 부분 성공으로 종료되었습니다."
            elif task_status == "canceled":
                label, kind = "Pi 작업 취소", "error"
                icon = QMessageBox.Icon.Warning
                summary = task_message or "로봇 작업이 취소되었습니다."
            elif task_status == "timed_out" or event == "ui_task_timed_out":
                label, kind = "Pi 작업 시간 초과", "error"
                icon = QMessageBox.Icon.Critical
                summary = task_message or "로봇 작업이 제한시간을 초과했습니다."
            elif task_status == "failed":
                label, kind = "Pi 작업 실패", "error"
                icon = QMessageBox.Icon.Critical
                summary = task_message or "로봇 작업이 실패했습니다."
            else:
                ok = bool(payload.get("ok", False))
                label = "Pi 작업 완료" if ok else "Pi 작업 실패"
                kind = "success" if ok else "error"
                icon = QMessageBox.Icon.Information if ok else QMessageBox.Icon.Critical
                summary = str(payload.get("message", "")).strip() or (
                    "작업이 완료되었습니다." if ok else "작업이 실패했습니다."
                )
            self.code_pane.set_status(label, kind)
            self._clear_pending_request()
            details = json.dumps(payload, ensure_ascii=False, indent=2)
            if path is not None:
                details += f"\n\n저장 결과: {path}"
            box = QMessageBox(self)
            box.setIcon(icon)
            box.setWindowTitle(event)
            box.setText(summary)
            box.setDetailedText(details)
            box.exec()
        elif event.startswith("ui_stop_"):
            self.robot_status.set_task_status(payload)

    @Slot(str, object)
    def _on_telemetry(self, label: str, payload: dict[str, Any]) -> None:
        self.robot_status.set_telemetry(label, payload)

    @Slot(str)
    def _on_ros_error(self, message: str) -> None:
        self.robot_status.last_event.setText(f"ROS 오류: {message}")

    def _check_backend_staleness(self) -> None:
        if self._backend_last_seen <= 0.0:
            return
        if time.monotonic() - self._backend_last_seen <= 3.0:
            return
        self._backend_state = BackendState(
            detail="3초 이상 heartbeat 없음",
        )
        self.robot_status.set_backend(self._backend_state)
        self._refresh_action_buttons()

    def _refresh_action_buttons(self) -> None:
        local_valid = bool(self._current_report and self._current_report.is_valid)
        self.code_pane.set_backend_availability(
            self._backend_state.reachable,
            self._backend_state.allow_execution
            and self._backend_state.gateway_reachable
            and self._config.execution_controls_enabled,
            local_valid,
            request_pending=(
                self._pending_payload is not None
                or bool(self._held_reset_pending_id)
            ),
        )

    def _clear_pending_request(self) -> None:
        self._request_timer.stop()
        self._pending_payload = None
        self._pending_request_id = ""
        self._pending_acknowledged = False
        self._pending_started = 0.0
        self._refresh_action_buttons()


def _assistant_summary(response: ParsedResponse) -> str:
    if response.format_error:
        return (
            "에이전트 응답 형식을 해석하지 못했습니다.\n\n"
            "원본 응답:\n"
            f"{response.raw_text}"
        )
    if response.status == ResponseStatus.CODE:
        bindings = response.object_bindings or "없음"
        assumptions = response.assumptions or "없음"
        return (
            "작업 코드를 생성했습니다. 오른쪽에서 검증하고, Pi 검증 또는 승인 후 실행을 선택하세요.\n\n"
            f"물체 매핑:\n{bindings}\n\n가정:\n{assumptions}"
        )
    return response.question_or_reason or "응답 형식을 해석하지 못했습니다."


def _status_label(status: ResponseStatus) -> str:
    return {
        ResponseStatus.NEED_CLARIFICATION: "추가 정보 필요",
        ResponseStatus.UNSUPPORTED: "지원하지 않는 작업",
        ResponseStatus.GENERATION_ERROR: "생성 오류",
    }.get(status, "코드 생성됨")


def _status_kind(status: ResponseStatus) -> str:
    return {
        ResponseStatus.NEED_CLARIFICATION: "pending",
        ResponseStatus.UNSUPPORTED: "error",
        ResponseStatus.GENERATION_ERROR: "error",
    }.get(status, "success")


def stylesheet() -> str:
    return """
    /* Font families are resolved by font_support.py after checking actual
       Hangul glyph coverage. Do not override them with a QSS-only fallback. */
    QMainWindow, QWidget#central { background: #F7F8FA; color: #14213D; }
    QLabel#appTitle { font-size: 22px; font-weight: 700; color: #10234D; }
    QLabel#appSubtitle, QLabel#panelSubtitle, QLabel#footer { color: #697386; font-size: 12px; }
    QLabel#robotMark { color: #16A4B5; font-size: 30px; padding-right: 3px; }
    QLabel#apiState, QLabel#statusBadge {
        background: #E8F5F6; color: #087B88; border-radius: 12px;
        padding: 6px 10px; font-size: 12px; font-weight: 700;
    }
    QLabel#statusBadge[kind='success'] { background: #E8F6EE; color: #167846; }
    QLabel#statusBadge[kind='pending'] { background: #FFF3DE; color: #A45B00; }
    QLabel#statusBadge[kind='error'] { background: #FCEBED; color: #B42335; }
    QLabel#panelTitle { font-size: 17px; font-weight: 700; color: #10234D; }
    QFrame#composer, QFrame#validationCard, QFrame#robotStatusCard {
        background: white; border: 1px solid #E5E8EE; border-radius: 14px;
    }
    QPlainTextEdit#messageInput { border: none; background: transparent; padding: 5px; font-size: 14px; }
    QPlainTextEdit#codeEditor {
        background: #18212B; color: #EDF2F7; border: 1px solid #293747;
        border-radius: 12px; padding: 14px;
        font-size: 13px;
    }
    QFrame#userBubble { background: #DFF2F6; border: 1px solid #C8E6EB; border-radius: 15px; }
    QFrame#assistantBubble { background: white; border: 1px solid #E5E8EE; border-radius: 15px; }
    QLabel#bubbleHeader { color: #5B6576; font-size: 11px; font-weight: 700; }
    QLabel#bubbleText { background: transparent; color: #1A2539; border: none; padding: 0; font-size: 14px; }
    QLabel#charCount { color: #697386; font-size: 11px; padding-right: 4px; }
    QLabel#statusLine, QLabel#validationReport { color: #526072; font-size: 12px; }
    QLabel#badge_CODE, QLabel#badge_NEED_CLARIFICATION, QLabel#badge_UNSUPPORTED, QLabel#badge_GENERATION_ERROR {
        border-radius: 9px; padding: 3px 7px; font-size: 10px; font-weight: 700;
    }
    QLabel#badge_CODE { background: #E8F6EE; color: #167846; }
    QLabel#badge_NEED_CLARIFICATION { background: #FFF3DE; color: #A45B00; }
    QLabel#badge_UNSUPPORTED, QLabel#badge_GENERATION_ERROR { background: #FCEBED; color: #B42335; }
    QLabel#cardTitle { font-size: 13px; font-weight: 700; color: #334155; }
    QPushButton { border-radius: 9px; padding: 9px 12px; font-weight: 700; }
    QPushButton#primaryButton { background: #159DAC; color: white; border: none; }
    QPushButton#primaryButton:hover { background: #0D8492; }
    QPushButton#secondaryButton { background: white; color: #087B88; border: 1px solid #14A2B0; }
    QPushButton#secondaryButton:hover { background: #E8F5F6; }
    QPushButton#ghostButton { background: transparent; color: #536174; border: 1px solid #D8DEE8; }
    QPushButton#dangerButton { background: #B42335; color: white; border: none; }
    QPushButton#dangerButton:hover { background: #8F1728; }
    QPushButton:disabled { background: #E5E7EB; color: #9CA3AF; border-color: #E5E7EB; }
    QScrollArea { background: transparent; }
    QWidget#chatContent { background: transparent; }
    QSplitter::handle { background: transparent; width: 16px; }
    """
