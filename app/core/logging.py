"""Privacy-safe logging setup."""

from __future__ import annotations

import logging
import sys
from typing import Any


def setup_logging(level: int = logging.INFO) -> None:
    """Configure root logger. Never log raw prompts or full user text here."""
    root = logging.getLogger()
    if root.handlers:
        return
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"),
    )
    root.addHandler(handler)
    root.setLevel(level)


def log_event(logger: logging.Logger, event: str, **fields: Any) -> None:
    """Structured-ish single line without sensitive payloads."""
    parts = [f"event={event}"]
    for k, v in sorted(fields.items()):
        if v is None:
            continue
        parts.append(f"{k}={v}")
    logger.info(" ".join(parts))
