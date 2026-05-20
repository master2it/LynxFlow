from __future__ import annotations

import httpx
import pytest
import respx

from app.ai.model_router import ModelRouter
from app.ai.ollama_client import OllamaClient, OllamaError
from app.core.config import Settings


@pytest.mark.asyncio
async def test_list_models_success(settings: Settings) -> None:
    client = OllamaClient(settings)
    router = ModelRouter(settings)

    with respx.mock:
        respx.get(f"{settings.ollama_base_url.rstrip('/')}/api/tags").mock(
            return_value=httpx.Response(
                200,
                json={"models": [{"name": "llama3.1:8b"}, {"name": "phi4:latest"}]},
            ),
        )
        names = await client.list_models()
        assert "llama3.1:8b" in names
        assert router.model_for("generation") == settings.model_generation


@pytest.mark.asyncio
async def test_ensure_model_missing_raises(settings: Settings) -> None:
    client = OllamaClient(settings)
    with respx.mock:
        respx.get(f"{settings.ollama_base_url.rstrip('/')}/api/tags").mock(
            return_value=httpx.Response(200, json={"models": []}),
        )
        with pytest.raises(OllamaError):
            await client.ensure_model_available(settings.model_generation)


@pytest.mark.asyncio
async def test_generate_stream_reads_chunks(settings: Settings) -> None:
    client = OllamaClient(settings)
    lines = [
        '{"response":"Hello","done":false}',
        '{"response":" world","done":true}',
    ]
    body = ("\n".join(lines) + "\n").encode()

    with respx.mock:
        respx.post(f"{settings.ollama_base_url.rstrip('/')}/api/generate").mock(
            return_value=httpx.Response(200, content=body),
        )

        parts: list[str] = []
        async for chunk in client.generate_stream(model="m", prompt="p", system=None):
            parts.append(chunk)
        assert "".join(parts) == "Hello world"
