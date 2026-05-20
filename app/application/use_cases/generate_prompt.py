"""Generate a structured prompt and optionally persist history."""

from __future__ import annotations

import asyncio

from sqlalchemy.engine import Engine

from app.application.schemas.generation import GenerationResult, UserRequest
from app.application.workflow.workflow_engine import WorkflowEngine
from app.core.config import Settings
from app.intelligence.privacy.secret_scanner import scan_and_redact, truncate_preview
from app.storage.repositories.history import PromptHistoryRepository


class GeneratePromptUseCase:
    def __init__(self, settings: Settings, engine: Engine, workflow: WorkflowEngine) -> None:
        self._settings = settings
        self._engine = engine
        self._workflow = workflow
        self._history = PromptHistoryRepository(engine)

    async def execute(
        self,
        request: UserRequest,
        *,
        cancel_event: asyncio.Event,
        on_progress=None,
        on_chunk=None,
        save_history: bool = True,
    ) -> GenerationResult:
        result = await self._workflow.run(
            request,
            cancel_event=cancel_event,
            on_progress=on_progress,
            on_chunk=on_chunk,
        )

        if save_history and self._settings.history_enabled:
            raw_scan = scan_and_redact(request.raw_text)
            preview = truncate_preview(raw_scan.text)
            task_type = result.intent.task_type if result.intent else "general"
            await self._history.add(
                target_ai=request.target_ai,
                task_type=task_type,
                mode=request.mode,
                raw_preview=preview,
                final_prompt=result.final_prompt,
                warnings=result.warnings,
            )
        return result
