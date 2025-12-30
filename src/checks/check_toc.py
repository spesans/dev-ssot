#!/usr/bin/env python3
"""
check_toc.py

Validates manual "Table of Contents" entries (if present) against headings.

Usage:
  python3 check_toc.py docs
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


FENCE_RE = re.compile(r"^(`{3,}|~{3,})")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
TOC_HEADINGS = {"## Table of Contents", "## Contents"}
TOC_LINK_RE = re.compile(r"\[[^\]]+\]\((#[^)]+)\)")
SKIP_DIRS = {"_templates", "overrides"}


def should_skip(path: Path, docs_dir: Path) -> bool:
    try:
        rel = path.relative_to(docs_dir)
    except ValueError:
        return False
    return any(part in SKIP_DIRS for part in rel.parts)


def slugify(text: str) -> str:
    slug = text.strip().lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    slug = re.sub(r"-{2,}", "-", slug)
    return slug.strip("-")


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
        m = HEADING_RE.match(line)
        if m:
            headings.append(m.group(2).strip())
    return headings


def build_anchor_set(headings: list[str]) -> set[str]:
    anchors: set[str] = set()
    counts: dict[str, int] = {}
    for heading in headings:
        base = slugify(heading)
        if base in counts:
            counts[base] += 1
            anchor = f"{base}-{counts[base]}"
        else:
            counts[base] = 0
            anchor = base
        anchors.add(f"#{anchor}")
    return anchors


def lint_file(path: Path, docs_dir: Path) -> list[str]:
    errors: list[str] = []
    if should_skip(path, docs_dir):
        return errors

    text = path.read_text(encoding="utf-8", errors="replace")
    headings = extract_headings(text)
    anchor_set = build_anchor_set(headings)

    in_fence = False
    fence_marker = ""
    in_toc = False
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

        if line.strip() in TOC_HEADINGS:
            in_toc = True
            continue
        if in_toc and line.startswith("#"):
            in_toc = False
        if not in_toc:
            continue

        for anchor in TOC_LINK_RE.findall(line):
            if anchor not in anchor_set:
                errors.append(f"{path}: TOC anchor not found: {anchor}")

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 check_toc.py <docs_dir>", file=sys.stderr)
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

    print(f"OK: TOC check passed for {len(md_files)} markdown files under {docs_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
