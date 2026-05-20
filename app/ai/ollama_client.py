"""Async Ollama HTTP client with streaming and cancellation."""

from __future__ import annotations

import asyncio
import json
import time
from collections.abc import AsyncIterator
from typing import Any

import httpx

from app.core.config import Settings


class OllamaError(RuntimeError):
    """User-facing Ollama failures."""


class OllamaClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self._settings.ollama_base_url.rstrip("/"),
            timeout=httpx.Timeout(self._settings.ollama_timeout_seconds),
            headers={"User-Agent": self._settings.http_user_agent},
        )

    async def list_models(self) -> list[str]:
        try:
            async with self._client() as client:
                r = await client.get("/api/tags")
                r.raise_for_status()
                data = r.json()
        except httpx.HTTPError as exc:
            raise OllamaError("Could not reach Ollama. Is it running?") from exc

        models = data.get("models") or []
        names: list[str] = []
        for m in models:
            name = m.get("name")
            if isinstance(name, str):
                names.append(name)
        return names

    async def ensure_model_available(self, model: str) -> None:
        names = await self.list_models()
        if model in names:
            return
        # tags sometimes include :latest suffix
        if any(n == model or n.startswith(f"{model}:") for n in names):
            return
        raise OllamaError(
            f"Model {model!r} not found locally. Try: ollama pull {model}",
        )

    async def generate_stream(
        self,
        *,
        model: str,
        prompt: str,
        system: str | None = None,
        cancel_event: asyncio.Event | None = None,
    ) -> AsyncIterator[str]:
        """Stream decoded `response` text chunks from /api/generate."""
        payload: dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": True,
        }
        if system:
            payload["system"] = system

        attempt = 0
        while True:
            try:
                async with (
                    self._client() as client,
                    client.stream("POST", "/api/generate", json=payload) as resp,
                ):
                    resp.raise_for_status()
                    async for line in resp.aiter_lines():
                        if cancel_event and cancel_event.is_set():
                            return
                        if not line:
                            continue
                        try:
                            obj = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        if obj.get("error"):
                            raise OllamaError(str(obj["error"]))
                        piece = obj.get("response")
                        if isinstance(piece, str) and piece:
                            yield piece
                        if obj.get("done") is True:
                            return
                return
            except (httpx.TimeoutException, httpx.ConnectError, httpx.ReadError) as exc:
                attempt += 1
                if attempt > self._settings.ollama_max_retries:
                    raise OllamaError("Ollama request failed after retries.") from exc
                await asyncio.sleep(0.4 * attempt)

    async def embed(self, model: str, text: str) -> list[float]:
        """Compute embeddings (reserved for future RAG phases)."""
        payload = {"model": model, "prompt": text}
        try:
            async with self._client() as client:
                r = await client.post("/api/embeddings", json=payload)
                r.raise_for_status()
                data = r.json()
        except httpx.HTTPError as exc:
            raise OllamaError("Embeddings request failed.") from exc
        emb = data.get("embedding")
        if not isinstance(emb, list):
            raise OllamaError("Unexpected embeddings response.")
        return [float(x) for x in emb]

    async def enhance_prompt(
        self,
        *,
        model: str,
        composed_prompt: str,
        cancel_event: asyncio.Event | None = None,
    ) -> tuple[str, dict[str, Any]]:
        """Polish wording while preserving structure; returns full text + metadata."""
        system = (
            "You are a senior prompt engineer. Improve clarity and specificity without "
            "removing headings or constraints. Do not add new requirements. "
            "Return only the improved prompt text."
        )
        user = composed_prompt
        started = time.perf_counter()
        parts: list[str] = []
        async for chunk in self.generate_stream(
            model=model,
            prompt=user,
            system=system,
            cancel_event=cancel_event,
        ):
            parts.append(chunk)
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        return "".join(parts).strip(), {
            "model": model,
            "latency_ms": elapsed_ms,
            "done_reason": "stream_end",
        }
