#!/usr/bin/env python3
"""Cross-platform helper to run Ruff checks."""

from __future__ import annotations

import subprocess
import sys


def main() -> int:
    root = __import__("pathlib").Path(__file__).resolve().parents[1]
    exe = sys.executable
    cmds = [
        [exe, "-m", "ruff", "check", str(root)],
        [exe, "-m", "ruff", "format", "--check", str(root)],
    ]
    for cmd in cmds:
        print("+", " ".join(cmd))
        subprocess.check_call(cmd, cwd=root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
