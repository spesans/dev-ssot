#!/usr/bin/env python3
"""
check_references.py

Lints SSOT-style references in Markdown docs.

Goals (best-effort, deterministic):
- Ensure every [R##] used in the document body is defined in the References section.
- Ensure every defined [R##] is used somewhere in the doc body (excluding the References section itself).
- Ensure each reference definition includes a URL and a 'retrieved'/'accessed' date.

Usage:
  python3 check_references.py docs
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


REF_USE_RE = re.compile(r"\[R(\d+)\]")
# Definition line examples:
# - [R12] OpenAI. "...". https://... (retrieved 2025-12-20)
REF_DEF_RE = re.compile(r"^\s*[-*]\s*\[R(\d+)\]\s+.+", re.IGNORECASE | re.MULTILINE)
URL_RE = re.compile(r"https?://\S+")
DATE_RE = re.compile(r"\((retrieved|accessed)\s+\d{4}-\d{2}-\d{2}", re.IGNORECASE)
FENCE_RE = re.compile(r"^(?P<fence>`{3,}|~{3,})")
SKIP_DIRS = {"_templates", "overrides"}


def split_references_section(text: str) -> tuple[str, str]:
    """
    Split markdown into (body, references_section) by the first '## References' heading.
    If not found, return (text, "").
    """
    m = re.search(r"(?m)^##\s+References\s*$", text)
    if not m:
        return text, ""
    idx = m.start()
    return text[:idx], text[idx:]


def strip_code(text: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    in_fence = False
    fence_marker = ""
    for line in lines:
        m = FENCE_RE.match(line)
        if m:
            marker = m.group("fence")
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
        if line.startswith("    ") or line.startswith("\t"):
            continue
        out.append(line)
    return "\n".join(out)


def should_skip(path: Path, docs_dir: Path) -> bool:
    try:
        rel = path.relative_to(docs_dir)
    except ValueError:
        return False
    return any(part in SKIP_DIRS for part in rel.parts)


def lint_file(path: Path, docs_dir: Path) -> list[str]:
    errors: list[str] = []
    if should_skip(path, docs_dir):
        return errors
    text = path.read_text(encoding="utf-8", errors="replace")

    body, refs = split_references_section(text)

    used = set(REF_USE_RE.findall(strip_code(body)))
    # Parse definitions from References section only
    defined = set(REF_DEF_RE.findall(refs))

    # 1) Missing definitions
    missing = sorted(used - defined, key=int)
    if missing:
        errors.append(
            f"{path}: undefined references used in body: " + ", ".join(f"R{x}" for x in missing)
        )

    # 2) Unused definitions
    unused = sorted(defined - used, key=int)
    if unused:
        errors.append(
            f"{path}: unused references defined (never used in body): "
            + ", ".join(f"R{x}" for x in unused)
        )

    # 3) Each definition should include URL and retrieved/accessed date
    for line in refs.splitlines():
        m = REF_DEF_RE.match(line)
        if not m:
            continue
        if not URL_RE.search(line):
            errors.append(f"{path}: reference [R{m.group(1)}] missing URL: {line.strip()}")
        if not DATE_RE.search(line):
            errors.append(
                f"{path}: reference [R{m.group(1)}] missing '(retrieved|accessed YYYY-MM-DD)': "
                f"{line.strip()}"
            )

    # 4) If References section exists but empty definitions
    if refs and not defined:
        errors.append(f"{path}: has '## References' but no [R##] definitions found.")

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 check_references.py <docs_dir>", file=sys.stderr)
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

    print(f"OK: references lint passed for {len(md_files)} markdown files under {docs_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
