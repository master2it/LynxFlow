# Architecture

This document summarizes the **implemented MVP (0.1.x)** layout and how modules interact. For the broader product vision and roadmap, see [`planning-spec.md`](planning-spec.md).

## Goals

- **Local-first:** default to local models (Ollama) and local persistence (SQLite).
- **Layered prompts:** compose from reusable templates instead of one hard-coded mega-prompt.
- **Async UI:** keep Qt responsive using `qasync` + `asyncio`.

## Layer diagram

```text
PySide6 UI (MainWindow + WorkflowController)
  -> GeneratePromptUseCase
      -> WorkflowEngine
          -> intent + context heuristics
          -> optional repository manifest snippets
          -> strategy selection (YAML)
          -> PromptComposer (Jinja)
          -> optional Ollama streaming polish
          -> secret scan + persistence
```

## Packages

| Path | Responsibility |
| ---- | -------------- |
| `app/ui/` | Qt widgets, async workflow wiring |
| `app/application/` | Use cases, workflow orchestration, prompt composition |
| `app/intelligence/` | Rule-based MVP “smart” steps + privacy redaction |
| `app/ai/` | Ollama HTTP client + model routing |
| `app/storage/` | SQLite + Alembic migrations + repositories |
| `app/templates/` | Bundled Jinja templates and strategy YAML |
| `app/core/` | Settings, logging, lifecycle helpers |

## Persistence

- SQLite file: `LYNXFLOW_DATA_DIR/lynxflow.db` (see `app/core/config.py`).
- Alembic migrations live in `app/storage/migrations/`.

## Extension points (post-MVP)

- Replace heuristics in `app/intelligence/*` with model-assisted pipelines without changing the use case surface area.
- Add vector memory under `app/intelligence/memory/` and embeddings calls in `app/ai/ollama_client.py`.

## Related docs

- [`adr/0001-local-first-ollama.md`](adr/0001-local-first-ollama.md)
- [`security-model.md`](security-model.md)
- [`template-format.md`](template-format.md)
