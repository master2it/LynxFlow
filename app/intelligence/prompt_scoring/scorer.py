"""MVP prompt scoring: required section checklist."""

from __future__ import annotations

from app.application.schemas.generation import ComposedPrompt, PromptScore, StrategySpec


def score_prompt(composed: ComposedPrompt, strategy: StrategySpec | None) -> PromptScore:
    """Return explainable checklist; no ML in MVP."""
    checklist: dict[str, bool] = {
        "has_goal": "user goal" in composed.body.lower() or "goal" in composed.body.lower(),
        "has_constraints": "constraint" in composed.body.lower(),
        "has_output_format": "output" in composed.body.lower() or "format" in composed.body.lower(),
    }
    if strategy and strategy.required_sections:
        for sec in strategy.required_sections:
            key = f"section:{sec}"
            checklist[key] = sec.lower() in composed.body.lower()

    passed = sum(1 for v in checklist.values() if v) >= max(2, len(checklist) // 2)
    notes: list[str] = []
    if not checklist.get("has_goal"):
        notes.append("Make the user goal more explicit.")
    return PromptScore(passed=passed, checklist=checklist, notes=notes)
