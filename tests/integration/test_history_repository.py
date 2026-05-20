from __future__ import annotations

import pytest

from app.storage.repositories.history import PromptHistoryRepository


@pytest.mark.asyncio
async def test_history_roundtrip(engine) -> None:
    repo = PromptHistoryRepository(engine)
    row = await repo.add(
        target_ai="cursor",
        task_type="refactor",
        mode="production_ready",
        raw_preview="hello",
        final_prompt="world",
        warnings=["w"],
    )
    assert row.id is not None

    rows = await repo.list_recent(10)
    assert any(r.final_prompt == "world" for r in rows)
