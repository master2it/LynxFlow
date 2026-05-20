from __future__ import annotations

from pathlib import Path

from app.intelligence.repo_analyzer.analyzer import analyze_repository


def test_analyze_repository_allowlist(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text('{"name":"demo"}', encoding="utf-8")
    (tmp_path / "README.md").write_text("# Demo", encoding="utf-8")
    summary = analyze_repository(str(tmp_path))
    assert summary is not None
    assert "package.json" in summary


def test_analyze_repository_missing_returns_none(tmp_path: Path) -> None:
    assert analyze_repository(str(tmp_path)) is None
