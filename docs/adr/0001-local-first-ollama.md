# ADR 0001: Local-first default with Ollama and async UI

## Status

Accepted

## Context

LynxFlow targets developers who want structured, project-aware prompts without shipping source code to third-party clouds by default.

## Decision

1. **Local-first:** Default runtime uses local Ollama HTTP API and local SQLite storage.
2. **Async UI:** Long-running model calls, repository reads, and database I/O must not block the Qt GUI thread; use `qasync` with `asyncio`.
3. **Inspectable pipeline:** The app composes prompts from layered templates before optional LLM polish, so users can reason about what changed.

## Consequences

- Ollama availability becomes a core operational dependency for enhancement features.
- Tests mock HTTP (`respx`) for deterministic CI; live Ollama tests are opt-in behind `LYNXFLOW_RUN_INTEGRATION=1`.
