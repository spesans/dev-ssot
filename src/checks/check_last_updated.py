#!/usr/bin/env python3
"""
check_last_updated.py

Validates that docs frontmatter `last_updated` matches the most recent Update Log entry.

Rules (best-effort, deterministic):
- Only checks Markdown files under docs/ excluding templates/overrides.
- Requires:
  - YAML frontmatter with `last_updated: YYYY-MM-DD`
  - A `## Update Log` section
  - The first Update Log bullet begins with a date matching `last_updated`

Usage:
  python3 check_last_updated.py docs
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


FRONTMATTER_RE = re.compile(r"(?s)^---\n(.*?)\n---\n")
LAST_UPDATED_RE = re.compile(r"(?m)^last_updated:\s*(\d{4}-\d{2}-\d{2})\s*$")
UPDATE_LOG_H2_RE = re.compile(r"(?m)^##\s+Update Log\s*$")
UPDATE_LOG_FIRST_ENTRY_RE = re.compile(r"^\s*-\s*(?:\*\*)?(\d{4}-\d{2}-\d{2})(?:T[0-9:]+Z)?(?:\*\*)?\b")
SKIP_DIRS = {"_templates", "overrides"}


def should_skip(path: Path, docs_dir: Path) -> bool:
    try:
        rel = path.relative_to(docs_dir)
    except ValueError:
        return False
    return any(part in SKIP_DIRS for part in rel.parts)


def parse_last_updated(text: str) -> str | None:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    fm = m.group(1)
    m2 = LAST_UPDATED_RE.search(fm)
    return m2.group(1) if m2 else None


def parse_update_log_top_date(text: str) -> str | None:
    m = UPDATE_LOG_H2_RE.search(text)
    if not m:
        return None

    after = text[m.end() :].splitlines()
    for line in after:
        if not line.strip():
            continue
        if line.startswith("##"):
            return None
        m2 = UPDATE_LOG_FIRST_ENTRY_RE.match(line)
        if m2:
            return m2.group(1)
        # If we hit a non-empty, non-bullet line first, treat as invalid.
        if line.lstrip().startswith("-"):
            return None
        return None
    return None


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 check_last_updated.py <docs_dir>", file=sys.stderr)
        return 2

    docs_dir = Path(sys.argv[1])
    if not docs_dir.exists() or not docs_dir.is_dir():
        print(f"Not a directory: {docs_dir}", file=sys.stderr)
        return 2

    md_files = sorted(docs_dir.rglob("*.md"))
    if not md_files:
        print(f"No markdown files found under: {docs_dir}", file=sys.stderr)
        return 2

    errors: list[str] = []
    checked = 0
    for f in md_files:
        if should_skip(f, docs_dir):
            continue
        checked += 1
        text = f.read_text(encoding="utf-8", errors="replace")
        last_updated = parse_last_updated(text)
        if not last_updated:
            errors.append(f"{f}: missing frontmatter last_updated")
            continue
        top_date = parse_update_log_top_date(text)
        if not top_date:
            errors.append(f"{f}: missing or invalid Update Log top entry date")
            continue
        if top_date != last_updated:
            errors.append(
                f"{f}: last_updated '{last_updated}' does not match Update Log top date '{top_date}'"
            )

    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        return 1

    print(f"OK: last_updated matches Update Log top entry for {checked} docs under {docs_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

