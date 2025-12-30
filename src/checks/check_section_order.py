#!/usr/bin/env python3
"""
check_section_order.py

Validates the required 11-section structure order for SSOT-style docs.

Usage:
  python3 check_section_order.py docs
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


REQUIRED_HEADINGS = [
    "## Agent Contract",
    "## TL;DR",
    "## Canonical Definitions",
    "## Core Patterns",
    "## Decision Checklist",
    "## Anti-patterns / Pitfalls",
    "## Evaluation",
    "## Update Log",
    "## See Also",
    "## References",
]
OPTIONAL_HEADING = "## Practical Examples"
FENCE_RE = re.compile(r"^(`{3,}|~{3,})")
H2_RE = re.compile(r"^##\s+(.+?)\s*$")
SKIP_DIRS = {"_templates", "overrides"}


def should_skip(path: Path, docs_dir: Path) -> bool:
    try:
        rel = path.relative_to(docs_dir)
    except ValueError:
        return False
    return any(part in SKIP_DIRS for part in rel.parts)


def extract_headings(text: str) -> list[str]:
    headings: list[str] = []
    in_fence = False
    fence_marker = ""
    for line in text.splitlines():
        m = FENCE_RE.match(line)
        if m:
            marker = m.group(1)
            if not in_fence:
                in_fence = True
                fence_marker = marker
                continue
            if marker.startswith(fence_marker[:1]) and len(marker) >= len(fence_marker):
                in_fence = False
                fence_marker = ""
                continue
        if in_fence:
            continue
        m = H2_RE.match(line)
        if m:
            headings.append(f"## {m.group(1).strip()}")
    return headings


def lint_file(path: Path, docs_dir: Path) -> list[str]:
    errors: list[str] = []
    if should_skip(path, docs_dir):
        return errors

    text = path.read_text(encoding="utf-8", errors="replace")
    headings = extract_headings(text)
    positions: dict[str, int] = {}
    for idx, h in enumerate(headings):
        if h not in positions:
            positions[h] = idx

    missing = [h for h in REQUIRED_HEADINGS if h not in positions]
    if missing:
        errors.append(f"{path}: missing required headings: {', '.join(missing)}")
        return errors

    last_idx = -1
    for h in REQUIRED_HEADINGS:
        idx = positions[h]
        if idx <= last_idx:
            errors.append(f"{path}: section order violation at '{h}'")
            break
        last_idx = idx

    if OPTIONAL_HEADING in positions:
        eval_idx = positions["## Evaluation"]
        update_idx = positions["## Update Log"]
        opt_idx = positions[OPTIONAL_HEADING]
        if not (eval_idx < opt_idx < update_idx):
            errors.append(
                f"{path}: '{OPTIONAL_HEADING}' must appear between '## Evaluation' and '## Update Log'"
            )

    if path.name == "SSOT.md":
        for token in ("BCP 14", "RFC 2119", "RFC 8174"):
            if token not in text:
                errors.append(f"{path}: missing '{token}' in Normative Keywords section")
                break

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 check_section_order.py <docs_dir>", file=sys.stderr)
        return 2

    docs_dir = Path(sys.argv[1])
    if not docs_dir.exists() or not docs_dir.is_dir():
        print(f"Not a directory: {docs_dir}", file=sys.stderr)
        return 2

    md_files = sorted(docs_dir.rglob("*.md"))
    if not md_files:
        print(f"No markdown files found under: {docs_dir}", file=sys.stderr)
        return 2

    all_errors: list[str] = []
    for f in md_files:
        all_errors.extend(lint_file(f, docs_dir))

    if all_errors:
        for e in all_errors:
            print(e, file=sys.stderr)
        return 1

    print(f"OK: section order check passed for {len(md_files)} markdown files under {docs_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
