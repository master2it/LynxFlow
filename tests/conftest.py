"""Pytest configuration and shared fixtures."""

from __future__ import annotations

import pytest

from app.core.config import Settings
from app.storage.db.engine import get_engine
from app.storage.migrate import upgrade_head


@pytest.fixture()
def settings(tmp_path, monkeypatch: pytest.MonkeyPatch) -> Settings:
    monkeypatch.setenv("LYNXFLOW_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("LYNXFLOW_ENHANCE_WITH_OLLAMA", "false")
    return Settings()


@pytest.fixture()
def engine(settings: Settings):
    upgrade_head()
    eng = get_engine(settings)
    return eng
