"""Run Alembic migrations to head (sync, call from asyncio.to_thread on startup)."""

from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config


def find_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "alembic.ini").exists():
            return parent
    msg = "Could not locate alembic.ini"
    raise FileNotFoundError(msg)


def upgrade_head() -> None:
    root = find_repo_root()
    cfg = Config(str(root / "alembic.ini"))
    command.upgrade(cfg, "head")
