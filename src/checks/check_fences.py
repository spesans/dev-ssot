#!/usr/bin/env python3
"""
check_fences.py

Detects unclosed fenced code blocks in Markdown files.

Usage:
  python3 check_fences.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


MD_FILES = [Path("README.md"), Path("AGENTS.md"), Path("SSOT.md")] + sorted(Path("docs").rglob("*.md"))
FENCE_RE = re.compile(r"^(?P<fence>`{3,}|~{3,})")


def lint_file(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return errors
    text = path.read_text(encoding="utf-8", errors="replace")

    in_fence = False
    fence_marker = ""
    opened_at = 0

    for idx, line in enumerate(text.splitlines(), start=1):
        m = FENCE_RE.match(line)
        if not m:
            continue
        marker = m.group("fence")
        if not in_fence:
            in_fence = True
            fence_marker = marker
            opened_at = idx
            continue

        if marker.startswith(fence_marker[:1]) and len(marker) >= len(fence_marker):
            in_fence = False
            fence_marker = ""
            opened_at = 0

    if in_fence:
        errors.append(f"{path}: unclosed fence starting at line {opened_at}")

    return errors


def main() -> int:
    all_errors: list[str] = []
    checked = 0

    for f in MD_FILES:
        checked += 1
        all_errors.extend(lint_file(f))

    if all_errors:
        for e in all_errors:
            print(e, file=sys.stderr)
        return 1

    print(f"OK: fence check passed for {checked} markdown files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

