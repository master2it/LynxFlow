"""Pydantic models for generation pipeline boundaries."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, field_validator

from app.core.constants import TARGET_AI_OPTIONS


class GenerationProgress(StrEnum):
    """High-level pipeline stages for UI feedback."""

    EXTRACTING = "extracting"
    ANALYZING_REPO = "analyzing_repo"
    ROUTING = "routing"
    COMPOSING = "composing"
    ENHANCING = "enhancing"
    FINALIZING = "finalizing"
    DONE = "done"


class UserRequest(BaseModel):
    """User input for prompt generation."""

    raw_text: str = Field(min_length=1)
    target_ai: str = Field(default="cursor", description="cursor|claude|chatgpt|windsurf|copilot")
    repository_path: str | None = None
    mode: str = Field(default="production_ready", description="e.g. production_ready, exploratory")

    @field_validator("target_ai")
    @classmethod
    def normalize_target(cls, v: str) -> str:
        t = v.strip().lower()
        return t if t in TARGET_AI_OPTIONS else "cursor"


class IntentResult(BaseModel):
    """Classified task from rule-based or future LLM intent detection."""

    task_type: str
    confidence: float = Field(ge=0.0, le=1.0)
    framework: str | None = None
    domain: str | None = None
    priority: str | None = None


class ExtractedContext(BaseModel):
    """Structured facts extracted from messy user input."""

    task_type: str
    frameworks: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    files: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    error_logs: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    repository_summary: str | None = None


class StrategySpec(BaseModel):
    """Data-driven strategy loaded from YAML."""

    strategy_id: str
    task_type: str
    template_version: str
    strategy_template: str
    required_placeholders: list[str] = Field(default_factory=list)
    default_output_format: str = "markdown"
    required_sections: list[str] = Field(default_factory=list)


class ComposedPrompt(BaseModel):
    """Layered prompt before optional LLM enhancement."""

    body: str
    sections_used: list[str] = Field(default_factory=list)
    template_version: str | None = None


class PromptScore(BaseModel):
    """MVP stub: explainable checklist-style scoring."""

    passed: bool
    checklist: dict[str, bool] = Field(default_factory=dict)
    notes: list[str] = Field(default_factory=list)


class ModelMetadata(BaseModel):
    """Non-sensitive model call metadata."""

    model: str
    latency_ms: float | None = None
    done_reason: str | None = None


class GenerationResult(BaseModel):
    """Final output returned to UI and persistence."""

    final_prompt: str
    composed_before_enhance: str | None = None
    sections_used: list[str] = Field(default_factory=list)
    intent: IntentResult | None = None
    context: ExtractedContext | None = None
    strategy: StrategySpec | None = None
    score: PromptScore | None = None
    model_metadata: ModelMetadata | None = None
    warnings: list[str] = Field(default_factory=list)
    redactions_applied: bool = False
    extra: dict[str, Any] = Field(default_factory=dict)
