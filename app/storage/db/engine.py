"""SQLAlchemy engine and session factory."""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy.engine import Engine
from sqlmodel import Session, create_engine

from app.core.config import Settings


def get_engine(settings: Settings) -> Engine:
    """SQLite engine suitable for asyncio.to_thread access."""
    url = f"sqlite:///{settings.database_path.as_posix()}"
    return create_engine(
        url,
        echo=False,
        connect_args={"check_same_thread": False},
    )


def session_scope(engine: Engine) -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
