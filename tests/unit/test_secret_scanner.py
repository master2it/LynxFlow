from __future__ import annotations

from app.intelligence.privacy.secret_scanner import scan_and_redact


def test_redacts_env_paths() -> None:
    s = scan_and_redact("read .env then open id_rsa")
    assert ".env" not in s.text
    assert "id_rsa" not in s.text
    assert s.redactions >= 1


def test_redacts_inline_secret_assignment() -> None:
    s = scan_and_redact("token=abc123")
    assert "abc123" not in s.text
    assert "[REDACTED]" in s.text
