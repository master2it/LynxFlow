"""Map intent / task type to bundled strategy specs."""

from __future__ import annotations

from app.application.schemas.generation import StrategySpec
from app.core.constants import DEFAULT_TASK_TYPE
from app.intelligence.strategy_engine.loader import load_strategy

_SPEC_BY_TASK: dict[str, str] = {
    "responsive_ui": "responsive_ui",
    "bug_fix": "bug_fix",
    "refactor": "refactor",
    "architecture": "architecture",
    "performance": "optimization",
    "security_review": "debugging",
    "test_generation": "debugging",
    "documentation": "debugging",
    "migration": "refactor",
    "general": "general",
}


def resolve_strategy_name(task_type: str) -> str:
    return _SPEC_BY_TASK.get(task_type, DEFAULT_TASK_TYPE)


def load_strategy_for_task(task_type: str) -> StrategySpec:
    name = resolve_strategy_name(task_type)
    return load_strategy(name)
