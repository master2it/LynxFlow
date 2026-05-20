from __future__ import annotations

from pathlib import Path

from app.application.prompt_composer.composer import PromptComposer
from app.application.schemas.generation import UserRequest
from app.application.task_router.router import load_strategy_for_task
from app.intelligence.context_extraction.extractor import extract_context
from app.intelligence.intent_detection.detector import detect_intent


def _normalize_ws(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.strip().splitlines()).strip()


def test_golden_responsive_angular_prompt() -> None:
    raw = "make my angular dashboard responsive with mobile-first layout"
    intent = detect_intent(raw)
    ctx = extract_context(raw, intent.task_type)
    strategy = load_strategy_for_task(intent.task_type)
    composer = PromptComposer()
    req = UserRequest(
        raw_text=raw, target_ai="cursor", repository_path=None, mode="production_ready"
    )
    composed = composer.compose(request=req, intent=intent, context=ctx, strategy=strategy)

    assert "mobile" in composed.body.lower() or "responsive" in composed.body.lower()
    assert "angular" in composed.body.lower()
    assert "breakpoints" in composed.body.lower()
    assert "cursor" in composed.body.lower()

    expected_path = (
        Path(__file__).parents[1] / "fixtures" / "prompts" / "responsive_angular_expected.md"
    )
    if expected_path.exists():
        expected = _normalize_ws(expected_path.read_text(encoding="utf-8"))
        actual = _normalize_ws(composed.body)
        assert actual == expected
