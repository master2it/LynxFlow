from __future__ import annotations

import asyncio

import pytest

from app.ai.model_router import ModelRouter
from app.ai.ollama_client import OllamaClient
from app.application.prompt_composer.composer import PromptComposer
from app.application.schemas.generation import UserRequest
from app.application.use_cases.generate_prompt import GeneratePromptUseCase
from app.application.workflow.workflow_engine import WorkflowEngine


@pytest.mark.asyncio
async def test_workflow_without_ollama_enhancement(settings, engine) -> None:
    settings.enhance_with_ollama = False

    ollama = OllamaClient(settings)
    router = ModelRouter(settings)
    composer = PromptComposer()
    workflow = WorkflowEngine(settings, ollama, router, composer)
    use_case = GeneratePromptUseCase(settings, engine, workflow)

    req = UserRequest(
        raw_text="Refactor the payment module in `src/pay.py` for clarity.",
        target_ai="cursor",
        repository_path=None,
        mode="production_ready",
    )

    cancel = asyncio.Event()
    result = await use_case.execute(req, cancel_event=cancel)
    assert "Refactor" in result.final_prompt or "payment" in result.final_prompt.lower()
    assert result.intent is not None
    assert result.strategy is not None
