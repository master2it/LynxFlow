"""Redact sensitive patterns before persistence or logging."""

from __future__ import annotations

import re
from dataclasses import dataclass

# Path-like and credential hints (README-derived)
_PATH_SECRET_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(?i)\.env(?:\.[\w-]+)?"),
    re.compile(r"(?i)[\w/\\]*\.pem\b"),
    re.compile(r"(?i)[\w/\\]*\.key\b"),
    re.compile(r"(?i)[\w/\\]*\.p12\b"),
    re.compile(r"(?i)[\w/\\]*\.pfx\b"),
    re.compile(r"(?i)\bid_rsa\b"),
    re.compile(r"(?i)\bid_ed25519\b"),
    re.compile(r"(?i)secrets?\.[\w.]+"),
    re.compile(r"(?i)credentials?\.[\w.]+"),
    re.compile(r"(?i)\.aws/"),
    re.compile(r"(?i)\.gcp/"),
    re.compile(r"(?i)\.azure/"),
)

# Inline secret-ish assignments (very conservative)
_INLINE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(?i)(api[_-]?key|token|password|secret)\s*[:=]\s*\S+"),
)


@dataclass(frozen=True)
class ScanResult:
    text: str
    redactions: int
    warnings: list[str]


def scan_and_redact(text: str) -> ScanResult:
    """Replace suspicious substrings with [REDACTED]."""
    redactions = 0
    out = text
    for pat in _PATH_SECRET_PATTERNS:
        out, n = pat.subn("[REDACTED]", out)
        redactions += n
    for pat in _INLINE_PATTERNS:
        out, n = pat.subn(lambda m: m.group(1) + "=[REDACTED]", out)
        redactions += n

    warnings: list[str] = []
    if redactions:
        warnings.append(f"Redacted {redactions} potential secret pattern(s).")

    return ScanResult(text=out, redactions=redactions, warnings=warnings)


def truncate_preview(text: str, max_len: int = 200) -> str:
    t = text.strip().replace("\n", " ")
    if len(t) <= max_len:
        return t
    return t[: max_len - 1] + "…"
