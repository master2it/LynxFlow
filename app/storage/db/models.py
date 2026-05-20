"""SQLModel table definitions."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, Text
from sqlmodel import Field, SQLModel


class PromptHistory(SQLModel, table=True):
    """Persisted prompt history (redacted text only)."""

    __tablename__ = "prompt_history"

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now().astimezone())
    target_ai: str = Field(max_length=32)
    task_type: str = Field(max_length=64)
    mode: str = Field(max_length=64)
    raw_preview: str = Field(sa_column=Column(Text, nullable=False))
    final_prompt: str = Field(sa_column=Column(Text, nullable=False))
    warnings_json: str | None = Field(default=None, sa_column=Column(Text, nullable=True))


class AppSetting(SQLModel, table=True):
    """Key-value settings."""

    __tablename__ = "app_settings"

    key: str = Field(primary_key=True, max_length=128)
    value: str = Field(sa_column=Column(Text, nullable=False))
