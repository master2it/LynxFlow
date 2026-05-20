"""Compose layered prompts from Jinja templates."""

from __future__ import annotations

from jinja2 import Environment, PackageLoader, StrictUndefined, TemplateNotFound

from app.application.schemas.generation import (
    ComposedPrompt,
    ExtractedContext,
    IntentResult,
    StrategySpec,
    UserRequest,
)
from app.core.constants import TARGET_AI_OPTIONS


class PromptComposer:
    """Render target profile + strategy template with shared blocks."""

    def __init__(self) -> None:
        self._env = Environment(
            loader=PackageLoader("app", "templates"),
            autoescape=False,
            undefined=StrictUndefined,
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def _normalize_target(self, target_ai: str) -> str:
        t = target_ai.strip().lower()
        return t if t in TARGET_AI_OPTIONS else "cursor"

    def _build_context(
        self,
        request: UserRequest,
        intent: IntentResult,
        context: ExtractedContext,
        strategy: StrategySpec,
    ) -> dict[str, str]:
        frameworks = list(context.frameworks)
        if intent.framework and intent.framework not in frameworks:
            frameworks.insert(0, intent.framework)
        languages = list(context.languages)
        return {
            "user_goal": request.raw_text.strip(),
            "task_type": intent.task_type,
            "target_ai": self._normalize_target(request.target_ai),
            "frameworks": ", ".join(frameworks) if frameworks else "not specified",
            "languages": ", ".join(languages) if languages else "not specified",
            "files_mentioned": ", ".join(context.files) if context.files else "none listed",
            "constraints": ", ".join(context.constraints) if context.constraints else "none listed",
            "error_logs": "\n".join(context.error_logs) if context.error_logs else "",
            "repository_summary": context.repository_summary or "",
            "output_format": strategy.default_output_format,
            "mode": request.mode,
        }

    def _validate_placeholders(self, strategy: StrategySpec, ctx: dict[str, str]) -> None:
        missing = [k for k in strategy.required_placeholders if not str(ctx.get(k, "")).strip()]
        if missing:
            msg = f"Missing required template fields: {', '.join(missing)}"
            raise ValueError(msg)

    def compose(
        self,
        *,
        request: UserRequest,
        intent: IntentResult,
        context: ExtractedContext,
        strategy: StrategySpec,
    ) -> ComposedPrompt:
        target = self._normalize_target(request.target_ai)
        try:
            target_tpl = self._env.get_template(f"targets/{target}.md.j2")
        except TemplateNotFound as exc:
            msg = f"Missing target template for {target!r}"
            raise FileNotFoundError(msg) from exc

        strategy_tpl = self._env.get_template(f"strategies/{strategy.strategy_template}")
        ctx = self._build_context(request, intent, context, strategy)
        self._validate_placeholders(strategy, ctx)

        parts = [
            target_tpl.render(**ctx),
            "",
            strategy_tpl.render(**ctx),
        ]
        body = "\n".join(parts).strip()
        sections_used = [f"target:{target}", f"strategy:{strategy.strategy_id}"]
        return ComposedPrompt(
            body=body,
            sections_used=sections_used,
            template_version=strategy.template_version,
        )
