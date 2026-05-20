"""Route tasks to strategies."""

from app.application.task_router.router import load_strategy_for_task, resolve_strategy_name

__all__ = ["load_strategy_for_task", "resolve_strategy_name"]
