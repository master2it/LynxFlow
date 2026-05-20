from __future__ import annotations

import logging

import pytest

from app.core.logging import log_event, setup_logging


def test_log_event_does_not_include_sensitive_payload(caplog: pytest.LogCaptureFixture) -> None:
    setup_logging(logging.DEBUG)
    logger = logging.getLogger("test_privacy")
    secret = "token=supersecretvalue"
    with caplog.at_level(logging.INFO, logger="test_privacy"):
        log_event(logger, "test_event", model="m", status="ok")
        log_event(logger, "test_event2", note="ok")
    assert secret not in caplog.text
