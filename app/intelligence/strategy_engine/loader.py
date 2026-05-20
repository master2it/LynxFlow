"""Load strategy specs from bundled YAML."""

from __future__ import annotations

from importlib import resources
from pathlib import Path

import yaml

from app.application.schemas.generation import StrategySpec


def load_strategy(spec_name: str) -> StrategySpec:
    """Load `spec_name.yaml` from app.templates.strategies."""
    pkg = resources.files("app.templates").joinpath("strategies", f"{spec_name}.yaml")
    if not pkg.is_file():
        msg = f"Unknown strategy spec: {spec_name}"
        raise FileNotFoundError(msg)
    data = yaml.safe_load(pkg.read_text(encoding="utf-8"))
    return StrategySpec.model_validate(data)


def strategies_dir() -> Path:
    """Filesystem path to templates (dev / tests)."""
    return Path(__file__).resolve().parents[2] / "templates"
