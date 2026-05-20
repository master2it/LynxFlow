"""Application startup: directories, DB path, optional Ollama probe (non-blocking)."""

from __future__ import annotations

import logging
from pathlib import Path

from app.core.config import Settings

logger = logging.getLogger(__name__)


def ensure_data_dir(settings: Settings) -> Path:
    """Create data directory if missing."""
    path = settings.data_dir
    path.mkdir(parents=True, exist_ok=True)
    return path


async def background_ollama_probe(settings: Settings) -> None:
    """Optional non-blocking connectivity log (no secrets)."""
    try:
        import httpx

        url = f"{settings.ollama_base_url.rstrip('/')}/api/tags"
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get(url, headers={"User-Agent": settings.http_user_agent})
        logger.info("ollama_probe status=%s", r.status_code)
    except Exception as exc:  # noqa: BLE001 - probe is best-effort
        logger.info("ollama_probe skipped: %s", type(exc).__name__)
