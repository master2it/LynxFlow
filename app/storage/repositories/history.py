"""Async-friendly repositories using asyncio.to_thread for SQLite I/O."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime

from sqlalchemy.engine import Engine
from sqlmodel import Session, select

from app.storage.db.models import AppSetting, PromptHistory


class PromptHistoryRepository:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def _list_recent_sync(self, limit: int) -> list[PromptHistory]:
        with Session(self._engine) as session:
            stmt = select(PromptHistory).order_by(PromptHistory.id.desc()).limit(limit)
            return list(session.exec(stmt).all())

    async def list_recent(self, limit: int = 50) -> list[PromptHistory]:
        return await asyncio.to_thread(self._list_recent_sync, limit)

    def _add_sync(
        self,
        *,
        target_ai: str,
        task_type: str,
        mode: str,
        raw_preview: str,
        final_prompt: str,
        warnings: list[str] | None,
    ) -> PromptHistory:
        with Session(self._engine) as session:
            row = PromptHistory(
                created_at=datetime.now().astimezone(),
                target_ai=target_ai,
                task_type=task_type,
                mode=mode,
                raw_preview=raw_preview,
                final_prompt=final_prompt,
                warnings_json=json.dumps(warnings or []),
            )
            session.add(row)
            session.commit()
            session.refresh(row)
            return row

    async def add(
        self,
        *,
        target_ai: str,
        task_type: str,
        mode: str,
        raw_preview: str,
        final_prompt: str,
        warnings: list[str] | None = None,
    ) -> PromptHistory:
        return await asyncio.to_thread(
            self._add_sync,
            target_ai=target_ai,
            task_type=task_type,
            mode=mode,
            raw_preview=raw_preview,
            final_prompt=final_prompt,
            warnings=warnings,
        )


class SettingsRepository:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def _get_sync(self, key: str) -> str | None:
        with Session(self._engine) as session:
            row = session.get(AppSetting, key)
            return row.value if row else None

    async def get(self, key: str) -> str | None:
        return await asyncio.to_thread(self._get_sync, key)

    def _set_sync(self, key: str, value: str) -> None:
        with Session(self._engine) as session:
            row = session.get(AppSetting, key)
            if row:
                row.value = value
            else:
                session.add(AppSetting(key=key, value=value))
            session.commit()

    async def set(self, key: str, value: str) -> None:
        await asyncio.to_thread(self._set_sync, key, value)
