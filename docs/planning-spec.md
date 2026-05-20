# LynxFlow planning specification (archived copy)

This file preserves the original long-form product and architecture README.
For the maintained architecture summary, see [`architecture.md`](architecture.md).
For day-to-day contributor setup, see the root [`README.md`](../README.md) and [`CONTRIBUTING.md`](../CONTRIBUTING.md).

---

# LynxFlow

> Local-first desktop prompt engineering for developers, powered by Ollama.

[![Status](https://img.shields.io/badge/status-planning-blue)](#project-status)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](#requirements)
[![License](https://img.shields.io/badge/license-TBD-lightgrey)](#license)
[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/TBD/badge)](#security-and-privacy)

LynxFlow is a professional desktop application that turns messy programming requests into structured, project-aware prompts for tools such as Cursor, Claude, ChatGPT, Windsurf, and Copilot. It is designed to run locally by default using Ollama, so source code and project context can stay on the user's machine.

This document is written as an open-source ready project README plus architecture guide. Split it later into `README.md`, `docs/architecture.md`, `CONTRIBUTING.md`, `SECURITY.md`, and `ROADMAP.md` as the repository grows.

---

## Table of contents

- [Why LynxFlow?](#why-lynxflow)
- [Project status](#project-status)
- [Core features](#core-features)
- [How it works](#how-it-works)
- [Architecture](#architecture)
- [Recommended stack](#recommended-stack)
- [Repository structure](#repository-structure)
- [Core modules](#core-modules)
- [Data model](#data-model)
- [Prompt template system](#prompt-template-system)
- [Local RAG and memory](#local-rag-and-memory)
- [Ollama integration](#ollama-integration)
- [Security and privacy](#security-and-privacy)
- [Performance guidelines](#performance-guidelines)
- [User experience guidelines](#user-experience-guidelines)
- [Development setup](#development-setup)
- [Testing strategy](#testing-strategy)
- [Release process](#release-process)
- [Open-source project checklist](#open-source-project-checklist)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [Governance](#governance)
- [License](#license)

---

## Why LynxFlow?

Many prompt tools are simple wrappers:

```text
textarea -> AI model -> prompt
```

That flow usually produces generic prompts because it ignores project structure, constraints, prior successful prompts, target AI behavior, and developer preferences.

LynxFlow uses a context-engineering pipeline instead:

```text
User input
  -> context extraction
  -> intent detection
  -> repository understanding
  -> strategy selection
  -> retrieval from local memory
  -> prompt composition
  -> LLM enhancement
  -> prompt scoring
  -> final prompt
```

The goal is not just prompt generation. The goal is local, repeatable, project-aware AI workflow engineering.

---

## Project status

**Current stage:** Planning / pre-MVP

LynxFlow is intended to become a production-ready open-source desktop application. Until a first stable release exists, public APIs, storage schemas, template formats, and project structure may change.

Recommended status labels:

| Label      | Meaning                                                              |
| ---------- | -------------------------------------------------------------------- |
| `planning` | Architecture and product scope are being refined.                    |
| `mvp`      | Core app works but APIs and UX may change.                           |
| `beta`     | Usable by early adopters; backwards compatibility is not guaranteed. |
| `stable`   | Public workflows and data formats are versioned.                     |

---

## Core features

### MVP scope

- PySide6 desktop UI for Windows.
- Local Ollama model integration.
- Structured project/problem input forms.
- Prompt templates for common engineering tasks.
- Intent detection for task routing.
- Prompt composition with target profiles for Cursor, Claude, ChatGPT, Windsurf, and Copilot.
- SQLite prompt history and settings storage.

### Planned features

- Drag-and-drop repository analyzer.
- Local RAG over successful prompts, project summaries, and reusable patterns.
- User memory for preferred style, target tools, coding conventions, and project defaults.
- Prompt scoring before final output.
- Plugin system for new targets, strategies, repository analyzers, and template packs.
- Optional integrations for Git, VS Code, Cursor, and team template libraries.

---

## How it works

LynxFlow should never send raw user text directly to a model as the final prompt. The application should decompose each request into structured data, route it through a strategy, then compose the final prompt from reusable layers.

### Pipeline

```text
1. User submits a request
2. Context extractor converts messy input into structured facts
3. Intent detector classifies the task type
4. Repository analyzer summarizes relevant files and project rules
5. Strategy engine selects the best prompting approach
6. Local RAG retrieves similar successful prompts or templates
7. Prompt composer builds a layered prompt
8. Ollama improves wording and resolves ambiguity
9. Prompt scorer checks clarity, completeness, and token efficiency
10. User receives a final prompt with copy/export actions
```

### Prompt composition model

A high-quality prompt should be composed from layers:

```text
system rules
+ task strategy
+ project context
+ user goal
+ constraints
+ output format
+ target AI profile
+ validation checklist
```

Avoid one giant hard-coded prompt. Use small, testable components that can be versioned independently.

---

## Architecture

```text
+-----------------------+
| PySide6 Desktop UI    |
+----------+------------+
           |
           v
+-----------------------+
| Application Layer     |
| - workflow engine     |
| - prompt composer     |
| - task router         |
| - use cases           |
+----------+------------+
           |
           v
+-----------------------+
| Intelligence Layer    |
| - intent detection    |
| - context extraction  |
| - repository analysis |
| - strategy engine     |
| - prompt scoring      |
+----------+------------+
           |
           v
+-----------------------+
| AI Layer              |
| - Ollama client       |
| - model router        |
| - embeddings          |
| - local RAG           |
+----------+------------+
           |
           v
+-----------------------+
| Persistence Layer     |
| - SQLite              |
| - migrations          |
| - templates           |
| - prompt history      |
| - user memory         |
+-----------------------+
```

### Design principles

- **Local-first:** default to local models, local storage, and no external network calls for code or prompts.
- **Explicit boundaries:** UI, application logic, AI clients, analysis, and persistence should not be mixed.
- **Async by default:** never block the UI thread during model calls, repository scans, or embedding generation.
- **Composable strategies:** every task type should have a named strategy, test cases, and prompt template layers.
- **Privacy by design:** do not log source files, secrets, prompts, or embeddings unless the user explicitly enables it.
- **Inspectable output:** show users what context was used and allow them to remove sensitive context before copying a prompt.

---

## Recommended stack

### Desktop UI

| Tool        | Purpose                                   |
| ----------- | ----------------------------------------- |
| PySide6     | Native-like desktop UI.                   |
| Qt Designer | Optional visual layout design.            |
| qasync      | Async integration between Qt and asyncio. |

### Backend and core

| Tool                           | Purpose                                                                |
| ------------------------------ | ---------------------------------------------------------------------- |
| Python 3.12+                   | Main application language.                                             |
| Pydantic v2                    | Strong validation for settings, extracted context, and prompt schemas. |
| asyncio                        | Non-blocking workflows.                                                |
| FastAPI                        | Optional internal API for future extensions or local service mode.     |
| SQLite                         | Local persistence.                                                     |
| Alembic or SQLModel migrations | Storage schema evolution.                                              |

### AI and retrieval

| Tool                                 | Purpose              |
| ------------------------------------ | -------------------- |
| Ollama                               | Local model runtime. |
| nomic-embed-text                     | Local embeddings.    |
| ChromaDB or FAISS                    | Local vector search. |
| tiktoken or model-specific tokenizer | Token budgeting.     |

### Recommended local models

| Purpose                   | Suggested model     | Notes                                        |
| ------------------------- | ------------------- | -------------------------------------------- |
| Primary prompt generation | `qwen2.5-coder:14b` | Better for coding-oriented prompts.          |
| Fast fallback             | `phi4`              | Useful for quick analysis and summarization. |
| General prompt generation | `llama3.1:8b`       | Good default where resources are limited.    |
| Large project analysis    | `deepseek-coder-v2` | Use only when hardware can handle it.        |
| Embeddings                | `nomic-embed-text`  | Local retrieval and memory.                  |

> Model names and availability should be checked during setup because local Ollama libraries change over time.

---

## Repository structure

Recommended open-source repository layout:

```text
lynxflow/
  app/
    main.py
    core/
      config.py
      constants.py
      lifecycle.py
      logging.py
    ui/
      windows/
      widgets/
      dialogs/
      themes/
    application/
      workflow/
      prompt_composer/
      task_router/
      use_cases/
    intelligence/
      context_extraction/
      intent_detection/
      memory/
      prompt_scoring/
      repo_analyzer/
      strategy_engine/
    ai/
      embeddings/
      model_router/
      ollama_client/
      rag/
    storage/
      db/
      migrations/
      repositories/
    templates/
      architecture/
      debugging/
      optimization/
      refactor/
      responsive/
    assets/
  docs/
    architecture.md
    adr/
      0001-local-first-ollama.md
    security-model.md
    template-format.md
  tests/
    unit/
    integration/
    fixtures/
  scripts/
    dev.ps1
    lint.py
    package.py
  .github/
    ISSUE_TEMPLATE/
      bug_report.yml
      feature_request.yml
    workflows/
      ci.yml
      release.yml
    dependabot.yml
  .editorconfig
  .gitignore
  .pre-commit-config.yaml
  CHANGELOG.md
  CODE_OF_CONDUCT.md
  CONTRIBUTING.md
  GOVERNANCE.md
  LICENSE
  README.md
  SECURITY.md
  pyproject.toml
  uv.lock
```

### Why this structure?

- `app/application` contains use cases and workflow orchestration.
- `app/intelligence` contains deterministic and model-assisted analysis.
- `app/ai` contains model clients and retrieval infrastructure.
- `app/storage` isolates persistence details.
- `docs/adr` records important architecture decisions.
- `.github` improves contributor experience and repository automation.

---

## Core modules

### 1. Intent detection

Intent detection classifies the user's task so the app can select the correct strategy.

Example input:

```text
make my angular dashboard responsive
```

Example structured output:

```json
{
  "task_type": "responsive_ui",
  "framework": "angular",
  "domain": "dashboard",
  "priority": "mobile_first",
  "confidence": 0.91
}
```

Recommended task types:

| Task type         | Strategy                                  |
| ----------------- | ----------------------------------------- |
| `responsive_ui`   | Mobile-first layout analysis.             |
| `bug_fix`         | Root-cause analysis before patching.      |
| `refactor`        | Analyze-first, preserve behavior.         |
| `architecture`    | System design with trade-offs.            |
| `performance`     | Bottleneck analysis and measurement plan. |
| `security_review` | Threat modeling and safe remediation.     |
| `test_generation` | Coverage-gap analysis.                    |
| `documentation`   | Audience-aware explanation.               |
| `migration`       | Risk-based incremental migration.         |

### 2. Context extraction

Context extraction converts messy user input into structured facts.

Extract at minimum:

- Frameworks, languages, package managers, and build tools.
- File names, paths, stack traces, commands, and error messages.
- Database, API, cloud, and deployment context.
- Constraints such as deadline, performance, accessibility, security, or backwards compatibility.
- User preferences such as target AI, tone, verbosity, and coding style.

All extracted context should be represented as validated Pydantic models.

### 3. Repository analyzer

The repository analyzer should support drag-and-drop project folders and build a compact project summary.

Initial files to detect:

| Ecosystem               | Files                                                                                                            |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------- |
| JavaScript / TypeScript | `package.json`, `pnpm-lock.yaml`, `yarn.lock`, `tsconfig.json`, `vite.config.*`, `angular.json`, `next.config.*` |
| Python                  | `pyproject.toml`, `requirements.txt`, `uv.lock`, `poetry.lock`, `setup.cfg`, `tox.ini`                           |
| Containers              | `Dockerfile`, `docker-compose.yml`, `.dockerignore`                                                              |
| CI/CD                   | `.github/workflows/*`, `.gitlab-ci.yml`                                                                          |
| Project rules           | `README.md`, `CONTRIBUTING.md`, `.cursor/rules/*`, `CLAUDE.md`, `AGENTS.md`                                      |
| Quality tools           | ESLint, Prettier, Ruff, Black, mypy, pytest, coverage configs                                                    |

Repository analysis must use allowlists, size limits, ignore rules, and token budgets. Never blindly read the whole repository into memory or inject complete source trees into prompts.

### 4. Strategy engine

The strategy engine chooses how to solve the request before any final prompt is written.

Example strategy object:

```json
{
  "strategy_id": "refactor.analyze_first",
  "task_type": "refactor",
  "required_sections": [
    "goal",
    "current_behavior",
    "constraints",
    "risk_analysis",
    "step_by_step_plan",
    "validation"
  ],
  "default_output_format": "implementation_plan_then_patch"
}
```

Strategy files should be data-driven where possible:

```text
templates/
  strategies/
    responsive_ui.yaml
    bug_fix.yaml
    refactor.yaml
    architecture.yaml
```

### 5. Prompt composer

The composer builds final prompts from reusable blocks.

Recommended sections:

1. Role and target tool instructions.
2. User goal.
3. Project context summary.
4. Relevant repository facts.
5. Constraints and non-goals.
6. Required reasoning strategy.
7. Expected output format.
8. Validation checklist.

The composer should support target-specific profiles because Cursor, Claude, ChatGPT, Windsurf, and Copilot often perform best with different prompt shapes.

### 6. Prompt scorer

Before presenting the prompt, score it for:

| Criterion            | Example check                                    |
| -------------------- | ------------------------------------------------ |
| Clarity              | Is the goal explicit?                            |
| Context completeness | Are frameworks, files, and constraints included? |
| Ambiguity            | Are uncertain assumptions called out?            |
| Token efficiency     | Is irrelevant repository context excluded?       |
| Target fit           | Does the prompt match the selected AI tool?      |
| Safety               | Are secrets or private files excluded?           |
| Testability          | Does the prompt request validation steps?        |

Scores should be explainable to the user, not hidden magic.

---

## Data model

Use explicit schemas for every boundary between modules.

Example request model:

```python
from pydantic import BaseModel, Field

class UserRequest(BaseModel):
    raw_text: str = Field(min_length=1)
    target_ai: str = "cursor"
    repository_path: str | None = None
    mode: str = "production_ready"
```

Example extracted context model:

```python
from pydantic import BaseModel

class ExtractedContext(BaseModel):
    task_type: str
    frameworks: list[str] = []
    languages: list[str] = []
    files: list[str] = []
    constraints: list[str] = []
    error_logs: list[str] = []
    confidence: float
```

Persist only what is necessary. Give users a clear setting to disable history, memory, or embeddings.

---

## Prompt template system

Templates should be small, composable, versioned text files. Avoid storing one giant prompt per task.

Example layout:

```text
templates/
  blocks/
    output_rules.md
    validation_checklist.md
    privacy_guardrails.md
  targets/
    cursor.md
    claude.md
    chatgpt.md
    windsurf.md
    copilot.md
  strategies/
    responsive_ui.md
    refactor.md
    bug_fix.md
    architecture.md
  frameworks/
    angular.md
    react.md
    python.md
```

Supported placeholders:

```text
{{ task_type }}
{{ user_goal }}
{{ framework }}
{{ repository_summary }}
{{ constraints }}
{{ target_ai }}
{{ output_format }}
```

Template rules:

- Validate required placeholders before rendering.
- Version templates with a `template_version` field.
- Store examples and regression tests for important templates.
- Support user overrides without modifying bundled templates.
- Keep target-specific instructions separate from task-specific strategy.

---

## Local RAG and memory

Local RAG should improve prompt quality over time without sending data outside the user's machine.

### Retrieval workflow

```text
User request
  -> embedding
  -> search local prompt memory
  -> retrieve similar successful prompts and project summaries
  -> filter by target AI, task type, and repository
  -> inject only relevant snippets
  -> compose final prompt
```

### Store

- Successful prompts selected by the user.
- User-approved project summaries.
- Template usage metadata.
- Prompt quality scores and user ratings.

### Do not store by default

- Raw source files.
- Secrets or environment files.
- Full terminal logs with credentials.
- Private repository paths when telemetry is disabled.

### Memory example

```json
{
  "preferred_style": "production_ready",
  "preferred_ai": "cursor",
  "coding_style": "minimal_comments",
  "architecture_style": "clean_architecture",
  "output_preference": "plan_then_patch"
}
```

---

## Ollama integration

Recommended flow:

```text
Desktop app
  -> async application service
  -> Ollama HTTP API
  -> streamed response
  -> prompt scorer
  -> UI renderer
```

Implementation guidelines:

- Use async HTTP calls and stream responses to the UI.
- Add request cancellation from the UI.
- Add timeouts, retries, and clear user-facing errors.
- Detect unavailable models and guide users to pull them.
- Use a model router instead of hard-coding one model everywhere.
- Separate analysis models from generation models where useful.
- Log model metadata, latency, and token usage without logging sensitive prompt content.

---

## Security and privacy

LynxFlow's trust story is simple: local-first, inspectable, and user-controlled.

### Privacy defaults

- No cloud calls for project code by default.
- No telemetry by default unless the user explicitly opts in.
- No raw source files in logs.
- No raw prompts in crash reports.
- User can clear prompt history, memory, embeddings, and repository summaries.

### Secret handling

Never index or inject common sensitive files:

```text
.env
.env.*
*.pem
*.key
*.p12
*.pfx
id_rsa
id_ed25519
secrets.*
credentials.*
.aws/
.gcp/
.azure/
```

Use secret scanning before storing prompt history or repository summaries. When a possible secret is detected, redact it and show a warning.

### Local storage

- Use SQLite for structured data.
- Encrypt sensitive settings where practical.
- Store API keys, if ever supported, in the OS keychain instead of plain text files.
- Allow users to choose the data directory.
- Document where data is stored on disk.

### Supply-chain security

Recommended repository protections:

- Enable branch protection or repository rules for `main` and release branches.
- Require CI checks before merge.
- Require at least one review before merge once contributors exist.
- Use least-privilege GitHub Actions permissions.
- Pin important third-party GitHub Actions by full commit SHA in release workflows.
- Enable Dependabot or Renovate for dependency updates.
- Generate an SBOM for releases when packaging begins.
- Publish hashes for release artifacts.
- Add `SECURITY.md` with supported versions and private vulnerability reporting instructions.

---

## Performance guidelines

### Never

- Run model calls on the UI thread.
- Load an entire repository into memory.
- Inject complete source trees into prompts.
- Recompute embeddings for unchanged files.
- Store duplicate embeddings for identical content.
- Block app startup on model discovery.

### Always

- Stream long AI responses.
- Cache repository summaries and embeddings.
- Chunk large files and summarize them hierarchically.
- Respect token budgets per target AI.
- Use file size limits and ignore rules.
- Let users cancel long-running scans.
- Show progress for repository analysis.

Recommended budgets:

| Context type       | Default budget    |
| ------------------ | ----------------- |
| User request       | Keep complete.    |
| Project summary    | 500-1,500 tokens. |
| Relevant files     | 2-8 snippets.     |
| Retrieved examples | 1-3 examples.     |
| Output rules       | 200-500 tokens.   |

---

## User experience guidelines

Recommended layout:

```text
+--------------------------------------------------+
| Sidebar                                          |
| - History                                        |
| - Templates                                      |
| - Projects                                       |
| - Settings                                       |
+--------------------------------------------------+
| Input                                            |
| - Natural language request                       |
| - Target AI                                      |
| - Mode                                           |
| - Optional repository context                    |
+--------------------------------------------------+
| Structured context preview                       |
| - Detected task                                  |
| - Frameworks                                     |
| - Constraints                                    |
| - Files included/excluded                        |
+--------------------------------------------------+
| Generated prompt                                 |
| [Copy] [Improve] [Explain] [Export] [Save]       |
+--------------------------------------------------+
```

UX principles:

- Let users see and edit extracted context before final generation.
- Show which files were analyzed and which were ignored.
- Make privacy controls visible, not buried.
- Provide one-click copy, but also export to Markdown.
- Support keyboard shortcuts for power users.
- Keep advanced settings available but out of the default path.

---

## Development setup

> Commands are placeholders until the repository has a committed package manager and lockfile.

### Requirements

- Windows 10/11, macOS, or Linux for development.
- Python 3.12 or newer.
- Ollama installed and running.
- Git.
- Optional: `uv` for faster Python dependency management.

### Clone and install

```bash
git clone https://github.com/master2it/lynxflow.git
cd lynxflow
python -m venv .venv
. .venv/Scripts/activate
pip install -e ".[dev]"
```

For Unix-like shells:

```bash
source .venv/bin/activate
pip install -e ".[dev]"
```

### Pull recommended Ollama models

```bash
ollama pull qwen2.5-coder:14b
ollama pull phi4
ollama pull nomic-embed-text
```

### Run the app

```bash
python -m app.main
```

### Run quality checks

```bash
ruff check .
ruff format --check .
pytest
```

---

## Testing strategy

Use tests to make prompt generation predictable, not just to check Python code.

### Test layers

| Layer               | What to test                                                      |
| ------------------- | ----------------------------------------------------------------- |
| Unit                | Intent detection, context extraction parsing, template rendering. |
| Integration         | Ollama client, repository analyzer, SQLite repositories.          |
| Golden prompt tests | Final prompt snapshots for important scenarios.                   |
| Regression tests    | Bugs from real user reports.                                      |
| Privacy tests       | Secret redaction, ignored files, logging behavior.                |
| UI smoke tests      | App starts, basic workflow completes, cancellation works.         |

### Golden prompt example

```text
tests/fixtures/prompts/responsive_angular_input.txt
tests/fixtures/prompts/responsive_angular_expected.md
```

Golden tests should allow small formatting changes but fail on missing required sections, leaked secrets, or lost constraints.

---

## Release process

Use a predictable release process from the beginning.

1. Update `CHANGELOG.md` under `Unreleased`.
2. Confirm tests, linting, packaging, and security checks pass.
3. Bump version according to Semantic Versioning once the public API exists.
4. Create a signed Git tag, for example `v0.1.0`.
5. Build release artifacts.
6. Generate checksums and, later, SBOMs.
7. Publish release notes with upgrade notes and known issues.

### Versioning policy

Before `1.0.0`, breaking changes may happen in minor releases. After `1.0.0`:

| Change                                        | Version bump |
| --------------------------------------------- | ------------ |
| Breaking public API or template format change | Major        |
| Backwards-compatible feature                  | Minor        |
| Backwards-compatible bug fix                  | Patch        |

### Changelog categories

Use these categories in `CHANGELOG.md`:

- Added
- Changed
- Deprecated
- Removed
- Fixed
- Security

---

## Open-source project checklist

Before making the repository public, add these files:

| File                               | Purpose                                                                    |
| ---------------------------------- | -------------------------------------------------------------------------- |
| `README.md`                        | Explains what the project does, why it exists, and how to start.           |
| `LICENSE`                          | Defines legal permissions for users and contributors.                      |
| `CONTRIBUTING.md`                  | Explains how to set up the project, file issues, and submit pull requests. |
| `CODE_OF_CONDUCT.md`               | Sets behavior expectations for the community.                              |
| `SECURITY.md`                      | Explains supported versions and private vulnerability reporting.           |
| `CHANGELOG.md`                     | Tracks notable changes by release.                                         |
| `GOVERNANCE.md`                    | Explains maintainers, decision-making, and release authority.              |
| `.github/ISSUE_TEMPLATE/*`         | Makes bug reports and feature requests useful.                             |
| `.github/PULL_REQUEST_TEMPLATE.md` | Encourages test notes, screenshots, and risk descriptions.                 |
| `.github/dependabot.yml`           | Keeps dependencies and GitHub Actions updated.                             |
| `.editorconfig`                    | Normalizes editor behavior across contributors.                            |
| `.pre-commit-config.yaml`          | Runs formatting, linting, and basic checks before commits.                 |

Recommended issue labels:

```text
good first issue
help wanted
bug
feature
docs
security
performance
ui
ai
repo-analyzer
templates
blocked
needs reproduction
```

Recommended pull request checklist:

```markdown
- [ ] I linked the related issue.
- [ ] I added or updated tests.
- [ ] I updated documentation where needed.
- [ ] I checked that no secrets or private files are included.
- [ ] I described user-visible changes.
- [ ] I added screenshots or recordings for UI changes.
```

---

## Roadmap

### Phase 0: Foundation

- Decide project name, license, governance, and repository structure.
- Add README, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, and CHANGELOG.
- Configure CI for linting, formatting, and tests.
- Create architecture decision records.

### Phase 1: MVP

- PySide6 desktop shell.
- Ollama model detection and streaming generation.
- Basic prompt generation workflow.
- Prompt templates for debugging, refactoring, architecture, responsive UI, and optimization.
- SQLite settings and prompt history.

### Phase 2: Project-aware intelligence

- Intent detection.
- Context extraction schemas.
- Repository analyzer with safe file filtering.
- Target AI profiles.
- Structured context preview before generation.

### Phase 3: Local learning loop

- Local embeddings.
- RAG over approved prompt history and templates.
- User memory.
- Prompt scoring.
- Golden prompt evaluation suite.

### Phase 4: Ecosystem

- Plugin API.
- Template marketplace or shared template packs.
- Git integration.
- VS Code and Cursor integration.
- Signed release artifacts and SBOMs.

---

## Contributing

Contributions should be welcome once the MVP foundation is ready. Until then, use issues for design discussion and small documentation improvements.

Good first contribution areas:

- Documentation cleanup.
- Prompt template examples.
- Test fixtures.
- UI accessibility improvements.
- Repository analyzer rules for additional frameworks.
- Security and privacy review.

Expected contribution workflow:

1. Open or claim an issue before large changes.
2. Fork the repository and create a feature branch.
3. Add tests or golden prompt fixtures.
4. Run linting, formatting, and tests locally.
5. Open a pull request with a clear description and screenshots for UI changes.

Commit message style:

```text
type(scope): short summary
```

Examples:

```text
feat(repo-analyzer): detect angular workspace files
fix(ollama): handle missing model errors
docs(readme): add development setup
```

Recommended types: `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `build`, `ci`, `chore`.

---

## Governance

Suggested initial governance model:

- The project starts as maintainer-led.
- Maintainers review pull requests, manage releases, and define roadmap priorities.
- Major architecture changes should be documented in `docs/adr`.
- Security issues are handled privately according to `SECURITY.md`.
- As the contributor base grows, add maintainers based on sustained, high-quality participation.

Decision-making should favor:

1. User privacy.
2. Local-first functionality.
3. Clear architecture boundaries.
4. Contributor experience.
5. Maintainability over cleverness.

---

## License

Choose a license before publishing the repository.

Common options:

| License    | When to choose it                                                                                       |
| ---------- | ------------------------------------------------------------------------------------------------------- |
| MIT        | Simple permissive license. Good for broad adoption.                                                     |
| Apache-2.0 | Permissive license with explicit patent grant. Often preferred for larger projects.                     |
| GPL-3.0    | Strong copyleft license. Requires derivatives to remain open under compatible terms.                    |
| AGPL-3.0   | Strong copyleft with network-use provisions. More relevant for server software than local desktop apps. |

Recommended default for LynxFlow: **Apache-2.0** if you want permissive adoption plus patent protection, or **MIT** if you want maximum simplicity.

After choosing, add:

```text
LICENSE
SPDX-License-Identifier headers where practical
LICENSES/ directory if following REUSE
```

---

## Biggest mistakes to avoid

- Treating LynxFlow as a thin wrapper around an LLM.
- Ignoring repository context.
- Using a single prompt template for every task.
- Storing sensitive project data without clear user control.
- Running AI calls on the UI thread.
- Shipping without tests for prompt templates and repository analysis.
- Publishing as open source without license, contribution, security, and governance files.
- Overbuilding plugins before the core workflow is reliable.

---

## Long-term vision

LynxFlow should become a local AI engineering workbench for developers who want better prompts without giving up control of their code.

The durable value is:

- Context engineering.
- Repository understanding.
- Reusable AI workflows.
- Strategy-driven prompt generation.
- Local memory.
- Prompt optimization.
- Project-aware generation.
- Transparent privacy controls.

That is what separates a real engineering tool from a toy prompt wrapper.
