"""Allowlisted repository manifest reader (MVP stub)."""

from __future__ import annotations

from pathlib import Path

from app.core.constants import MAX_MANIFEST_BYTES, REPO_MANIFEST_ALLOWLIST


def analyze_repository(repo_path: str | None) -> str | None:
    """Read small allowlisted files only; return compact summary or None."""
    if not repo_path:
        return None
    root = Path(repo_path).expanduser().resolve()
    if not root.is_dir():
        return None

    parts: list[str] = []
    for name in sorted(REPO_MANIFEST_ALLOWLIST):
        fp = root / name
        if not fp.is_file():
            continue
        try:
            size = fp.stat().st_size
        except OSError:
            continue
        if size > MAX_MANIFEST_BYTES:
            parts.append(f"- {name}: skipped (too large)")
            continue
        try:
            text = fp.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        snippet = text[:4000]
        if len(text) > 4000:
            snippet += "\n... (truncated)"
        parts.append(f"### {name}\n{snippet}")

    if not parts:
        return None
    return "Repository manifest snippets:\n" + "\n\n".join(parts)
