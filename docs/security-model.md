# Security model (MVP)

## Threat framing

LynxFlow is a **local desktop app**. The primary risks are accidental leakage of secrets into stored history, exported files, or logs, and supply-chain compromise of dependencies.

## Defaults

- **No cloud telemetry** is implemented in the MVP codebase.
- **Ollama** is accessed on `LYNXFLOW_OLLAMA_BASE_URL` (default `http://127.0.0.1:11434`).
- **SQLite** stores redacted previews and final prompts under the configured data directory.

## Secret handling (MVP)

Before persistence, LynxFlow applies conservative pattern redaction (see `app/intelligence/privacy/secret_scanner.py`). This is **not** a guarantee against all secret formats.

Users should treat redaction warnings seriously and manually review before sharing prompts.

## Reporting

See `SECURITY.md` for vulnerability reporting expectations.
