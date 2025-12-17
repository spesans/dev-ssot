"""
Generate virtual documentation pages from repository root sources for MkDocs.
This keeps `docs/` free of wrapper files while still exposing root Markdown.
"""

from pathlib import Path

import mkdocs_gen_files

ROOT = Path(__file__).resolve().parent.parent

SOURCES = {
    "index.md": "README.md",
    "AGENTS.md": "AGENTS.md",
    "_templates/TOPIC_TEMPLATE.md": "docs/_templates/TOPIC_TEMPLATE.md",
    "_templates/SECTION_TEMPLATE.md": "docs/_templates/SECTION_TEMPLATE.md",
    "_templates/FRONT_MATTER.md": "docs/_templates/FRONT_MATTER.md",
}

def rewrite_links(name: str, content: str) -> str:
    """Adjust intra-repo relative links to match MkDocs output paths."""
    if name == "index.md":
        content = content.replace("./docs/", "")
        content = content.replace("./_templates/", "_templates/")
        content = content.replace("docs/_templates/", "_templates/") # Handle the new location link if user wrote it relative to root
        content = content.replace("./LICENSE", "https://github.com/artificial-intelligence-first/ssot/blob/main/LICENSE")
    if name == "AGENTS.md":
        content = content.replace("./docs/", "")
        content = content.replace("./README.md", "index.md")
    return content

for target, source_path in SOURCES.items():
    source = ROOT / source_path
    text = source.read_text(encoding="utf-8")
    text = rewrite_links(target, text)
    with mkdocs_gen_files.open(target, "w") as dest:
        dest.write(text)
