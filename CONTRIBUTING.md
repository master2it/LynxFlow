# Contributing to LynxFlow

Thanks for your interest in improving LynxFlow. This repository is in early development; APIs and file layouts may change until the first stable release.

## Development setup

Requirements:

- Python 3.12+
- Git
- Ollama (optional for UI enhancement; tests mock HTTP)

Install in editable mode with dev dependencies:

```bash
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

python -m pip install -U pip
python -m pip install -e ".[dev]"
```

If you use `uv`:

```bash
uv sync --extra dev
```

Apply database migrations (also runs automatically on app startup):

```bash
alembic upgrade head
```

Run the app:

```bash
python -m app.main
```

## Quality checks

```bash
ruff check .
ruff format --check .
pytest
```

## Commit messages

Use Conventional Commits:

```text
type(scope): short summary
```

Examples:

```text
feat(repo-analyzer): detect additional manifest files
fix(ollama): improve cancellation during streaming
docs(readme): clarify local-first defaults
```

## Pull requests

- Link the related issue when applicable.
- Add or update tests for behavior changes.
- Update docs when user-facing behavior changes.
- Avoid committing secrets, `.env` files, or private paths in fixtures.

## Security

Please report security issues privately as described in `SECURITY.md`.
