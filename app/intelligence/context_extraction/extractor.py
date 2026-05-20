"""Heuristic context extraction (MVP)."""

from __future__ import annotations

import re

from app.application.schemas.generation import ExtractedContext

_FILE_PATTERN = re.compile(
    r"[`\"']?([\w./\\-]+\.(?:py|ts|tsx|js|jsx|json|md|yml|yaml|toml))[`\"']?", re.I
)
_ERROR_PATTERN = re.compile(r"(?:Error|Exception|Traceback)[^\n]{0,200}", re.I)


def extract_context(text: str, task_type: str) -> ExtractedContext:
    files = sorted({m.group(1) for m in _FILE_PATTERN.finditer(text)})
    error_logs = [m.group(0).strip() for m in _ERROR_PATTERN.finditer(text)]

    frameworks: list[str] = []
    languages: list[str] = []
    constraints: list[str] = []

    pairs = [
        (frameworks, "angular", r"\bangular\b"),
        (frameworks, "react", r"\breact\b"),
        (frameworks, "next", r"\bnext\.?js\b"),
        (languages, "typescript", r"\btypescript\b|\bts\b"),
        (languages, "python", r"\bpython\b"),
        (languages, "javascript", r"\bjavascript\b|\bjs\b"),
    ]
    for bucket, name, pat in pairs:
        if re.search(pat, text, re.I) and name not in bucket:
            bucket.append(name)

    if re.search(r"\bdeadline\b", text, re.I):
        constraints.append("mentions_deadline")
    if re.search(r"\bbackwards? compatible\b", text, re.I):
        constraints.append("backwards_compatibility")
    if re.search(r"\baccessib", text, re.I):
        constraints.append("accessibility")

    confidence = 0.55
    if files:
        confidence += 0.1
    if frameworks or languages:
        confidence += 0.1
    confidence = min(0.92, confidence)

    return ExtractedContext(
        task_type=task_type,
        frameworks=frameworks,
        languages=languages,
        files=files,
        constraints=constraints,
        error_logs=error_logs,
        confidence=confidence,
        repository_summary=None,
    )
