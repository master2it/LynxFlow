"""Primary application window."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QTextCursor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from sqlalchemy.engine import Engine

from app.application.schemas.generation import GenerationResult, UserRequest
from app.application.use_cases.generate_prompt import GeneratePromptUseCase
from app.core.config import Settings
from app.core.constants import TARGET_AI_OPTIONS
from app.storage.repositories.history import PromptHistoryRepository
from app.ui.workflow_controller import WorkflowController


class MainWindow(QMainWindow):
    def __init__(self, settings: Settings, use_case: GeneratePromptUseCase, engine: Engine) -> None:
        super().__init__()
        self._settings = settings
        self._use_case = use_case
        self._engine = engine
        self._history_repo = PromptHistoryRepository(engine)

        self.setWindowTitle("LynxFlow")
        self.resize(1200, 820)

        self._controller = WorkflowController(use_case)
        self._controller.progress.connect(self._on_progress)
        self._controller.chunk.connect(self._on_chunk)
        self._controller.finished.connect(self._on_finished)
        self._controller.failed.connect(self._on_failed)

        root = QWidget()
        layout = QHBoxLayout(root)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # Sidebar
        side = QWidget()
        side_l = QVBoxLayout(side)
        self._history_list = QListWidget()
        self._history_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._history_list.itemActivated.connect(self._on_history_activated)
        side_l.addWidget(QLabel("History"))
        side_l.addWidget(self._history_list)

        tpl_btn = QPushButton("Reload history")
        tpl_btn.clicked.connect(self._reload_history)
        side_l.addWidget(tpl_btn)

        settings_btn = QPushButton("Settings…")
        settings_btn.clicked.connect(self._open_settings)
        side_l.addWidget(settings_btn)
        side_l.addStretch(1)
        splitter.addWidget(side)

        # Main column
        center = QWidget()
        c_l = QVBoxLayout(center)

        self._status = QLabel("Ready")
        self._status.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        c_l.addWidget(self._status)

        c_l.addWidget(QLabel("Request"))
        self._input = QTextEdit()
        self._input.setPlaceholderText("Describe what you want the AI to help with…")
        self._input.setMinimumHeight(120)
        c_l.addWidget(self._input)

        row = QHBoxLayout()
        row.addWidget(QLabel("Target AI"))
        self._target = QComboBox()
        self._target.addItems(list(TARGET_AI_OPTIONS))
        self._target.setCurrentText("cursor")
        row.addWidget(self._target)

        row.addWidget(QLabel("Mode"))
        self._mode = QComboBox()
        self._mode.addItems(["production_ready", "exploratory", "strict_review"])
        row.addWidget(self._mode)
        row.addStretch(1)
        c_l.addLayout(row)

        repo_row = QHBoxLayout()
        repo_row.addWidget(QLabel("Repository (optional)"))
        self._repo = QTextEdit()
        self._repo.setMaximumHeight(36)
        self._repo.setPlaceholderText("Path to project root")
        repo_row.addWidget(self._repo, stretch=1)
        browse = QPushButton("Browse…")
        browse.clicked.connect(self._browse_repo)
        repo_row.addWidget(browse)
        c_l.addLayout(repo_row)

        c_l.addWidget(QLabel("Structured context (preview)"))
        self._context_preview = QTextEdit()
        self._context_preview.setReadOnly(True)
        self._context_preview.setMinimumHeight(120)
        c_l.addWidget(self._context_preview)

        out_row = QHBoxLayout()
        self._generate = QPushButton("Generate")
        self._generate.clicked.connect(self._start_generate)
        self._cancel = QPushButton("Cancel")
        self._cancel.setEnabled(False)
        self._cancel.clicked.connect(self._controller.cancel)
        out_row.addWidget(self._generate)
        out_row.addWidget(self._cancel)
        out_row.addStretch(1)

        self._copy = QPushButton("Copy")
        self._copy.clicked.connect(self._copy_output)
        self._export = QPushButton("Export Markdown…")
        self._export.clicked.connect(self._export_md)
        out_row.addWidget(self._copy)
        out_row.addWidget(self._export)
        c_l.addLayout(out_row)

        c_l.addWidget(QLabel("Generated prompt"))
        self._output = QTextEdit()
        self._output.setReadOnly(True)
        self._output.setMinimumHeight(260)
        c_l.addWidget(self._output)

        splitter.addWidget(center)
        splitter.setStretchFactor(1, 1)

        self.setCentralWidget(root)

        menu = self.menuBar().addMenu("&File")
        quit_a = QAction("Quit", self)
        quit_a.triggered.connect(self.close)
        menu.addAction(quit_a)

        self._reload_history()

    def _browse_repo(self) -> None:
        d = QFileDialog.getExistingDirectory(self, "Select repository root")
        if d:
            self._repo.setPlainText(d)

    def _reload_history(self) -> None:
        self._history_list.clear()

        async def _go() -> None:
            rows = await self._history_repo.list_recent(50)
            self._history_list.clear()
            for row in reversed(rows):
                label = f"[{row.target_ai}] {row.task_type} — {row.raw_preview[:80]}"
                item = QListWidgetItem(label)
                item.setData(Qt.ItemDataRole.UserRole, row.id)
                self._history_list.addItem(item)

        import asyncio

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return
        loop.create_task(_go())

    def _on_history_activated(self, item: QListWidgetItem) -> None:
        # MVP: show stored prompt in output when double-clicked
        _ = item

    def _open_settings(self) -> None:
        msg = QMessageBox(self)
        msg.setWindowTitle("Settings")
        msg.setText(
            f"Data directory:\n{self._settings.data_dir}\n\n"
            f"Ollama URL:\n{self._settings.ollama_base_url}\n\n"
            f"Generation model:\n{self._settings.model_generation}\n\n"
            "Toggle enhance with Ollama for this session?",
        )
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if msg.exec() == QMessageBox.StandardButton.Yes:
            self._settings.enhance_with_ollama = not self._settings.enhance_with_ollama
        self._status.setText(f"enhance_with_ollama={self._settings.enhance_with_ollama}")

    def _start_generate(self) -> None:
        text = self._input.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "LynxFlow", "Please enter a request.")
            return
        repo = self._repo.toPlainText().strip() or None
        payload = {
            "raw_text": text,
            "target_ai": self._target.currentText(),
            "repository_path": repo,
            "mode": self._mode.currentText(),
        }
        try:
            preview = UserRequest.model_validate(payload)
        except Exception as exc:  # noqa: BLE001
            QMessageBox.warning(self, "Validation", str(exc))
            return

        self._output.clear()
        self._context_preview.setPlainText("Working…")
        self._generate.setEnabled(False)
        self._cancel.setEnabled(True)

        # lightweight preview of structured fields (filled after generation for MVP speed)
        self._context_preview.setPlainText(
            f"target_ai={preview.target_ai}\nmode={preview.mode}\nrepo={preview.repository_path}",
        )

        self._controller.generate(payload)

    def _on_progress(self, stage: str) -> None:
        self._status.setText(f"Stage: {stage}")

    def _on_chunk(self, text: str) -> None:
        self._output.moveCursor(QTextCursor.MoveOperation.End)
        self._output.insertPlainText(text)
        self._output.moveCursor(QTextCursor.MoveOperation.End)

    def _on_finished(self, result_obj: object) -> None:
        self._generate.setEnabled(True)
        self._cancel.setEnabled(False)
        if not isinstance(result_obj, GenerationResult):
            return
        result: GenerationResult = result_obj
        self._output.setPlainText(result.final_prompt)
        ctx = result.context
        intent = result.intent
        lines = []
        if intent:
            lines.append(f"task_type: {intent.task_type} (confidence={intent.confidence:.2f})")
            lines.append(f"framework: {intent.framework}")
            lines.append(f"domain: {intent.domain}")
        if ctx:
            lines.append(f"frameworks: {', '.join(ctx.frameworks)}")
            lines.append(f"languages: {', '.join(ctx.languages)}")
            lines.append(f"files: {', '.join(ctx.files)}")
            lines.append(f"constraints: {', '.join(ctx.constraints)}")
        self._context_preview.setPlainText("\n".join(lines))
        if result.warnings:
            self._status.setText("Done — warnings: " + "; ".join(result.warnings))
        else:
            self._status.setText("Done")
        self._reload_history()

    def _on_failed(self, message: str) -> None:
        self._generate.setEnabled(True)
        self._cancel.setEnabled(False)
        QMessageBox.critical(self, "LynxFlow", message)

    def _copy_output(self) -> None:
        self._output.selectAll()
        self._output.copy()

    def _export_md(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Markdown", str(Path.home() / "lynxflow-prompt.md"), "*.md"
        )
        if not path:
            return
        Path(path).write_text(self._output.toPlainText(), encoding="utf-8")
