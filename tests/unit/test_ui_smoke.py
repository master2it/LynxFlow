from __future__ import annotations

import asyncio

from PySide6.QtWidgets import QApplication
from qasync import QEventLoop

from app.ai.model_router import ModelRouter
from app.ai.ollama_client import OllamaClient
from app.application.prompt_composer.composer import PromptComposer
from app.application.use_cases.generate_prompt import GeneratePromptUseCase
from app.application.workflow.workflow_engine import WorkflowEngine
from app.ui.windows.main_window import MainWindow


def test_main_window_construct(qtbot, settings, engine) -> None:
    qt = QApplication.instance() or QApplication([])
    loop = QEventLoop(qt)
    asyncio.set_event_loop(loop)

    settings.enhance_with_ollama = False
    ollama = OllamaClient(settings)
    router = ModelRouter(settings)
    composer = PromptComposer()
    workflow = WorkflowEngine(settings, ollama, router, composer)
    use_case = GeneratePromptUseCase(settings, engine, workflow)

    win = MainWindow(settings, use_case, engine)
    qtbot.addWidget(win)
    assert win.windowTitle() == "LynxFlow"
