# LynxFlow

> Local-first desktop prompt engineering for developers, powered by Ollama.

[![Status](https://img.shields.io/badge/status-mvp-green)](#project-status)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](#requirements)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

LynxFlow helps you turn messy engineering requests into **structured, layered prompts** tuned for tools like Cursor, Claude, ChatGPT, Windsurf, and Copilot. It runs **locally by default** (Ollama + SQLite) so your repo context stays on your machine.

## Quick start

Requirements:

- Python **3.12+**
- [Ollama](https://ollama.com/) (optional for the “polish/enhance” step; tests mock HTTP)

Install:

```bash
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

python -m pip install -U pip
python -m pip install -e ".[dev]"
```

Optional (recommended for reproducible installs):

```bash
uv sync --extra dev
```

Run database migrations (also runs on app startup):

```bash
alembic upgrade head
```

Run the desktop app:

```bash
python -m app.main
```

Recommended local models (examples):

```bash
ollama pull llama3.1:8b
ollama pull phi4
ollama pull nomic-embed-text
```

## Development

```bash
ruff check .
ruff format --check .
pytest -m "not integration"
```

## Documentation

- [`docs/architecture.md`](docs/architecture.md) — module boundaries and runtime flow
- [`docs/template-format.md`](docs/template-format.md) — bundled templates and strategy YAML
- [`docs/security-model.md`](docs/security-model.md) — MVP security notes
- [`docs/planning-spec.md`](docs/planning-spec.md) — long-form product + roadmap source document

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Security

See [`SECURITY.md`](SECURITY.md).

## License

Apache-2.0, see [`LICENSE`](LICENSE).
