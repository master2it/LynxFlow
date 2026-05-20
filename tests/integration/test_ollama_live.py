from __future__ import annotations

import os

import pytest


@pytest.mark.integration
@pytest.mark.asyncio
async def test_live_ollama_skipped_by_default() -> None:
    if not os.environ.get("LYNXFLOW_RUN_INTEGRATION"):
        pytest.skip("Set LYNXFLOW_RUN_INTEGRATION=1 to run live Ollama tests.")
