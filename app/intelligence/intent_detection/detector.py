"""Rule-based intent detection (MVP)."""

from __future__ import annotations

import re

from app.application.schemas.generation import IntentResult
from app.core.constants import DEFAULT_TASK_TYPE

_RULES: list[tuple[str, re.Pattern[str], float]] = [
    ("responsive_ui", re.compile(r"\b(responsive|mobile|tailwind|css grid|flex)\b", re.I), 0.75),
    ("bug_fix", re.compile(r"\b(bug|crash|error|stack trace|exception|fix)\b", re.I), 0.72),
    ("refactor", re.compile(r"\b(refactor|cleanup|dedupe|simplify)\b", re.I), 0.7),
    ("architecture", re.compile(r"\b(architecture|design|system design|trade-?off)\b", re.I), 0.68),
    ("performance", re.compile(r"\b(performance|slow|latency|optimize|bottleneck)\b", re.I), 0.68),
    (
        "security_review",
        re.compile(r"\b(security|vulnerability|threat|xss|csrf|injection)\b", re.I),
        0.7,
    ),
    ("test_generation", re.compile(r"\b(test|pytest|jest|coverage)\b", re.I), 0.65),
    ("documentation", re.compile(r"\b(document|readme|changelog|explain)\b", re.I), 0.62),
    ("migration", re.compile(r"\b(migrate|upgrade path|deprecat)\b", re.I), 0.62),
]


def detect_intent(text: str) -> IntentResult:
    best_type = DEFAULT_TASK_TYPE
    best_score = 0.35
    framework: str | None = None
    domain: str | None = None

    for task_type, pattern, base in _RULES:
        if pattern.search(text):
            score = min(0.95, base + 0.05 * len(pattern.findall(text)))
            if score > best_score:
                best_score = score
                best_type = task_type

    fw_patterns = [
        ("angular", re.compile(r"\bangular\b", re.I)),
        ("react", re.compile(r"\breact\b", re.I)),
        ("next", re.compile(r"\bnext\.?js\b", re.I)),
        ("vue", re.compile(r"\bvue\b", re.I)),
        ("python", re.compile(r"\bpython\b", re.I)),
        ("typescript", re.compile(r"\btypescript\b|\bts\b", re.I)),
    ]
    for name, pat in fw_patterns:
        if pat.search(text):
            framework = name
            break

    if re.search(r"\bdashboard\b", text, re.I):
        domain = "dashboard"

    priority = None
    if re.search(r"mobile[- ]first", text, re.I):
        priority = "mobile_first"

    return IntentResult(
        task_type=best_type,
        confidence=best_score,
        framework=framework,
        domain=domain,
        priority=priority,
    )
