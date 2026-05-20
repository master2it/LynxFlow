"""Bridge Qt signals to async prompt generation."""

from __future__ import annotations

import asyncio

from PySide6.QtCore import QObject, Signal
from qasync import asyncSlot

from app.application.schemas.generation import GenerationProgress, UserRequest
from app.application.use_cases.generate_prompt import GeneratePromptUseCase


class WorkflowController(QObject):
    """Runs `GeneratePromptUseCase` on the asyncio event loop integrated with Qt."""

    progress = Signal(str)
    chunk = Signal(str)
    finished = Signal(object)
    failed = Signal(str)

    def __init__(self, use_case: GeneratePromptUseCase) -> None:
        super().__init__()
        self._use_case = use_case
        self._cancel = asyncio.Event()

    def cancel(self) -> None:
        self._cancel.set()

    def reset_cancel(self) -> None:
        self._cancel = asyncio.Event()

    @asyncSlot(dict)
    async def generate(self, payload: dict) -> None:
        self.reset_cancel()
        request = UserRequest.model_validate(payload)

        async def on_progress(stage: GenerationProgress) -> None:
            self.progress.emit(stage.value)

        async def on_chunk(text: str) -> None:
            self.chunk.emit(text)

        try:
            result = await self._use_case.execute(
                request,
                cancel_event=self._cancel,
                on_progress=on_progress,
                on_chunk=on_chunk,
                save_history=True,
            )
        except Exception as exc:  # noqa: BLE001 - surface to UI
            self.failed.emit(str(exc))
            return

        self.finished.emit(result)
