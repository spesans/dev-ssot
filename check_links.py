from __future__ import annotations
from pathlib import Path
import re
import sys

MD_FILES = [Path("README.md"), Path("AGENTS.md")] + sorted(Path("docs").rglob("*.md"))
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
FENCE_RE = re.compile(r"^(?P<fence>`{3,}|~{3,})")
SKIP_PREFIXES = ("http://", "https://", "mailto:", "tel:")
BROKEN = []

def strip_fenced_code(text: str) -> str:
    lines = text.splitlines()
    out = []
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

for md in MD_FILES:
    if not md.exists():
        continue
    raw_text = md.read_text(encoding="utf-8")
    text = strip_fenced_code(raw_text)
    for raw in LINK_RE.findall(text):
        target = raw.strip()
        if " " in target and not target.startswith("<"):
            target = target.split(" ", 1)[0].strip()
        target = target.strip("<>")
        if not target or target.startswith("#"):
            continue
        if target.startswith(SKIP_PREFIXES):
            continue
        path_part = target.split("#", 1)[0]
        if not path_part:
            continue
        if ":" in path_part and not path_part.startswith(("./", "../")):
            continue
        resolved = (md.parent / path_part).resolve()
        if not resolved.exists():
            BROKEN.append(f"{md}:{target} -> {resolved}")

print("Starting link check...", flush=True)
if BROKEN:
    print("Broken relative links:", flush=True)
    for item in BROKEN:
        print(" -", item, flush=True)
    sys.exit(1)

print("OK: no broken relative links found (excluding code blocks)", flush=True)
