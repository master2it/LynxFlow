# Template format

Bundled templates live under `app/templates/` and are shipped as package data.

## Layout

- `blocks/`: reusable markdown fragments included by strategies.
- `targets/`: tool-specific guidance (`cursor`, `claude`, `chatgpt`, `windsurf`, `copilot`).
- `strategies/`: YAML specs plus Jinja strategy bodies (`*.md.j2`).

## Strategy YAML

Each `strategies/<name>.yaml` file validates into `StrategySpec` (`app/application/schemas/generation.py`):

- `strategy_id`, `task_type`, `template_version`
- `strategy_template` (filename under `strategies/`, usually `*.md.j2`)
- `required_placeholders` (must be present in the render context)
- `default_output_format`
- `required_sections` (used by the MVP checklist scorer)

## Rendering

`PromptComposer` uses Jinja2 `PackageLoader("app", "templates")` with `StrictUndefined` so missing context fails fast during composition.

## Versioning

Bump `template_version` when changing placeholders or meaningfully altering strategy behavior.
