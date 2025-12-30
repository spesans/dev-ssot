---
title: Agent Instructions (dev-ssot)
slug: agents-instructions
summary: "Operational instructions for coding agents in this repository"
type: policy
tags: [agents, instructions, ssot, docs]
last_updated: 2025-12-31
---

# Agent Instructions (dev-ssot)

This file contains operational instructions for AI coding agents working in this repository.

**Agents Catalog** is maintained separately:
- Human-readable: `docs/AGENTS_CATALOG.md`
- Machine-readable: `src/catalog/runtime-agents.yaml`

## Setup

- **Runtime**: Python 3.11 is the CI baseline.
- **Docs dependencies**:
  - Install: `python3 -m pip install -r requirements-docs.txt`
  - Preferred: use the existing `venv/` if present (e.g., `venv/bin/mkdocs`).

## Build

- Build docs (strict): `venv/bin/mkdocs build --strict`
- Serve docs locally: `venv/bin/mkdocs serve`

## Test / Validate

Run these from repo root:

- `venv/bin/python src/checks/check_fences.py`
- `venv/bin/python src/checks/check_section_order.py docs`
- `venv/bin/python src/checks/check_toc.py docs`
- `venv/bin/python src/checks/check_references.py docs`
- `venv/bin/python src/checks/check_links.py docs`
- `venv/bin/python src/checks/check_last_updated.py docs`

## Style

- Write documentation and code in **English**.
- Keep docs deterministic and machine-verifiable:
  - Preserve the required section order (see `docs/SSOT.md`).
  - For SSOT-style docs under `docs/`, update `last_updated`, prepend an `Update Log` entry, and keep `References` consistent.

## Security

- Do not introduce normative/spec meaning changes implicitly.
  - If a request conflicts with SSOT definitions/contracts/safety constraints, treat it as a change request: propose → confirm → apply (see `docs/SSOT.md`). [R1]
- Do not paste secrets/PII into docs, plans, or logs.

## PR

- Keep changes minimal and traceable.
- Prefer small commits and preserve evidence (commands + outputs) for doc validation work.

## Context Links

- Governance: [SSOT.md](./docs/SSOT.md)
- Planning: [EXEC_PLAN.md](./docs/EXEC_PLAN.md)
- Patterns: [README_AGENTS.md](./docs/README_AGENTS.md)
- Templates: [TOPIC_TEMPLATE.md](./docs/_templates/TOPIC_TEMPLATE.md)
- Agent inventory: [AGENTS_CATALOG.md](./docs/AGENTS_CATALOG.md)

## Update Log

- **2025-12-31** – Move validation scripts and runtime agent inventory under `src/` and update references. (Author: repo-orchestrator)
- **2025-12-30** – Simplify validation: remove RELATED_TOPICS slug enforcement and remove stub topic pages. (Author: repo-orchestrator)
- **2025-12-30** – Add additional doc validation checks (fence closure, last_updated/Update Log, RELATED_TOPICS) and ensure CI runs `mkdocs build --strict` on PRs. (Author: repo-orchestrator)
- **2025-12-30** – Split Agents Catalog into `docs/AGENTS_CATALOG.md` + `catalog/runtime-agents.yaml`; repurposed repo-root `AGENTS.md` as operational instructions. (Author: repo-orchestrator)

## References

- [R1] SpeSan. "SSOT for AI-First Development: SSOT." https://github.com/spesans/dev-ssot/blob/main/docs/SSOT.md (accessed 2025-12-30)

---

**Document ID**: `AGENTS.md`
**Canonical URL**: `https://github.com/spesans/dev-ssot/blob/main/AGENTS.md`
**License**: MIT
