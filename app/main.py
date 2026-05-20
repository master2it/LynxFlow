"""Application entrypoint."""

from __future__ import annotations

import asyncio
import sys

from PySide6.QtWidgets import QApplication
from qasync import QEventLoop

from app.ai.model_router import ModelRouter
from app.ai.ollama_client import OllamaClient
from app.application.prompt_composer.composer import PromptComposer
from app.application.use_cases.generate_prompt import GeneratePromptUseCase
from app.application.workflow.workflow_engine import WorkflowEngine
from app.core.config import Settings
from app.core.lifecycle import background_ollama_probe, ensure_data_dir
from app.core.logging import setup_logging
from app.storage.db.engine import get_engine
from app.storage.migrate import upgrade_head
from app.ui.windows.main_window import MainWindow


def main() -> int:
    setup_logging()
    settings = Settings()
    ensure_data_dir(settings)
    upgrade_head()

    engine = get_engine(settings)

    qt = QApplication(sys.argv)
    loop = QEventLoop(qt)
    asyncio.set_event_loop(loop)
    asyncio.ensure_future(background_ollama_probe(settings))

    ollama = OllamaClient(settings)
    router = ModelRouter(settings)
    composer = PromptComposer()
    workflow = WorkflowEngine(settings, ollama, router, composer)
    use_case = GeneratePromptUseCase(settings, engine, workflow)

    window = MainWindow(settings, use_case, engine)
    window.show()
    return qt.exec()


if __name__ == "__main__":
    raise SystemExit(main())
