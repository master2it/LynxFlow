"""Typed application settings (local-first, no secrets in files)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _default_data_dir() -> Path:
    if sys.platform == "win32":
        base = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
        return Path(base) / "LynxFlow"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "LynxFlow"
    xdg = os.environ.get("XDG_DATA_HOME")
    if xdg:
        return Path(xdg) / "lynxflow"
    return Path.home() / ".local" / "share" / "lynxflow"


class Settings(BaseSettings):
    """Runtime configuration; override via LYNXFLOW_* env vars."""

    model_config = SettingsConfigDict(
        env_prefix="LYNXFLOW_",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ollama_base_url: str = Field(default="http://127.0.0.1:11434")
    ollama_timeout_seconds: float = Field(default=120.0, ge=5.0, le=3600.0)
    ollama_max_retries: int = Field(default=2, ge=0, le=5)

    model_generation: str = Field(default="llama3.1:8b")
    model_fast_analysis: str = Field(default="phi4")
    model_embeddings: str = Field(default="nomic-embed-text")

    data_dir: Path = Field(default_factory=_default_data_dir)

    history_enabled: bool = True
    enhance_with_ollama: bool = True

    http_user_agent: str = "LynxFlow/0.1.0"

    # Token budgets (informational for composer; full enforcement in later phases)
    budget_project_summary_tokens: int = Field(default=1200, ge=200, le=8000)
    budget_output_rules_tokens: int = Field(default=400, ge=100, le=2000)

    @property
    def database_path(self) -> Path:
        return self.data_dir / "lynxflow.db"
