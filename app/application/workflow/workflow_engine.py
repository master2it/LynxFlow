"""Orchestrate extraction, routing, composition, optional enhancement, and redaction."""

from __future__ import annotations

import asyncio
import time
from collections.abc import Awaitable, Callable

from app.ai.model_router import ModelRouter
from app.ai.ollama_client import OllamaClient, OllamaError
from app.application.prompt_composer.composer import PromptComposer
from app.application.schemas.generation import (
    ComposedPrompt,
    ExtractedContext,
    GenerationProgress,
    GenerationResult,
    IntentResult,
    ModelMetadata,
    UserRequest,
)
from app.application.task_router.router import load_strategy_for_task
from app.core.config import Settings
from app.intelligence.context_extraction.extractor import extract_context
from app.intelligence.intent_detection.detector import detect_intent
from app.intelligence.privacy.secret_scanner import scan_and_redact
from app.intelligence.prompt_scoring.scorer import score_prompt
from app.intelligence.repo_analyzer.analyzer import analyze_repository


async def _maybe_await(value: Awaitable[None] | None) -> None:
    if value is None:
        return
    if asyncio.iscoroutine(value):
        await value


class WorkflowEngine:
    """Thin coordinator between intelligence, templates, and Ollama."""

    def __init__(
        self,
        settings: Settings,
        ollama: OllamaClient,
        router: ModelRouter,
        composer: PromptComposer,
    ) -> None:
        self._settings = settings
        self._ollama = ollama
        self._router = router
        self._composer = composer

    async def _emit(
        self,
        cb: Callable[[GenerationProgress], Awaitable[None] | None] | None,
        stage: GenerationProgress,
    ) -> None:
        if cb is None:
            return
        await _maybe_await(cb(stage))

    async def run(
        self,
        request: UserRequest,
        *,
        cancel_event: asyncio.Event,
        on_progress: Callable[[GenerationProgress], Awaitable[None] | None] | None = None,
        on_chunk: Callable[[str], Awaitable[None] | None] | None = None,
    ) -> GenerationResult:
        warnings: list[str] = []

        await self._emit(on_progress, GenerationProgress.EXTRACTING)
        intent: IntentResult = detect_intent(request.raw_text)
        context: ExtractedContext = extract_context(request.raw_text, intent.task_type)

        await self._emit(on_progress, GenerationProgress.ANALYZING_REPO)
        repo_summary = analyze_repository(request.repository_path)
        if repo_summary:
            context = context.model_copy(update={"repository_summary": repo_summary})

        await self._emit(on_progress, GenerationProgress.ROUTING)
        strategy = load_strategy_for_task(intent.task_type)

        await self._emit(on_progress, GenerationProgress.COMPOSING)
        composed: ComposedPrompt = self._composer.compose(
            request=request,
            intent=intent,
            context=context,
            strategy=strategy,
        )
        score = score_prompt(composed, strategy)

        final_text = composed.body
        model_meta: ModelMetadata | None = None

        await self._emit(on_progress, GenerationProgress.ENHANCING)
        if self._settings.enhance_with_ollama and not cancel_event.is_set():
            model = self._router.model_for("generation")
            system = (
                "You are a senior prompt engineer. Improve clarity and specificity without "
                "removing headings or constraints. Do not add new requirements. "
                "Return only the improved prompt text."
            )
            try:
                await self._ollama.ensure_model_available(model)
                started = time.perf_counter()
                parts: list[str] = []
                async for chunk in self._ollama.generate_stream(
                    model=model,
                    prompt=composed.body,
                    system=system,
                    cancel_event=cancel_event,
                ):
                    parts.append(chunk)
                    if on_chunk:
                        await _maybe_await(on_chunk(chunk))
                enhanced = "".join(parts).strip()
                elapsed_ms = (time.perf_counter() - started) * 1000.0
                if enhanced:
                    final_text = enhanced
                model_meta = ModelMetadata(
                    model=model,
                    latency_ms=float(elapsed_ms),
                    done_reason="stream_end",
                )
            except OllamaError as exc:
                warnings.append(str(exc))
                model_meta = None

        await self._emit(on_progress, GenerationProgress.FINALIZING)
        scan = scan_and_redact(final_text)
        final_text = scan.text
        if scan.warnings:
            warnings.extend(scan.warnings)

        await self._emit(on_progress, GenerationProgress.DONE)

        return GenerationResult(
            final_prompt=final_text,
            composed_before_enhance=composed.body,
            sections_used=composed.sections_used,
            intent=intent,
            context=context,
            strategy=strategy,
            score=score,
            model_metadata=model_meta,
            warnings=warnings,
            redactions_applied=scan.redactions > 0,
        )
