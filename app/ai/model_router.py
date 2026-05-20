"""Map logical roles to configured Ollama model names."""

from __future__ import annotations

from typing import Literal

from app.core.config import Settings

ModelPurpose = Literal["generation", "fast_analysis", "embeddings"]


class ModelRouter:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def model_for(self, purpose: ModelPurpose) -> str:
        if purpose == "generation":
            return self._settings.model_generation
        if purpose == "fast_analysis":
            return self._settings.model_fast_analysis
        return self._settings.model_embeddings
