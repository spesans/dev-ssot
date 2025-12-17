---
title: README & AGENTS Patterns
slug: agents-readme
summary: "Guide for implementing README and AGENTS documentation patterns"
type: guide
tags: [topic, ai-first, documentation, agents, readme, repository-structure]
last_updated: 2025-12-17
---

# README & AGENTS Patterns

## Agent Contract

- **PURPOSE**:
  - Define a practical documentation standard for AI-first repositories using `README.md` (humans) and `AGENTS.md` (coding agents)
  - Prevent instruction drift and ambiguity by specifying precedence and inheritance rules for agent instructions
  - Provide repeatable patterns for monorepos via “worldview boundaries” and short, link-based instruction files
- **USE_WHEN**:
  - Bootstrapping a repository that will be edited with coding agents (Copilot, Codex CLI, etc.)
  - Refactoring an existing repository to reduce onboarding time and documentation drift
  - Designing a monorepo with multiple independently-built and/or independently-deployed subsystems
- **DO_NOT_USE_WHEN**:
  - One-off scripts with no ongoing maintenance
  - Pure implementation-detail directories (`src/**`, `lib/**`, `utils/**`) that are not subsystem boundaries
- **PRIORITY**:
  - Root `README.md` is **MUST** (human entry point)
  - Root `AGENTS.md` is **MUST** (agent entry point; “README for agents”, standard Markdown, no required schema)
  - Subdirectory `README.md` / `AGENTS.md` **SHOULD** exist only at worldview boundaries; the format permits deeper nesting, but this guide’s policy is boundary-based for maintainability
  - Instruction conflicts **MUST** be resolved by explicit precedence rules (see “Precedence & Inheritance”)
  - Repositories **MUST NOT** place README/AGENTS files inside implementation-detail folders
- **NORMATIVE KEYWORDS**:
  - This document uses **MUST**, **SHOULD**, and **MAY** as defined in `docs/SSOT.md`
- **RELATED_TOPICS**:
  - ssot-guide
  - exec-plan
  - code-mcp
  - agent-skill
  - repository-structure
  - documentation-as-code

---

## TL;DR

- Put `README.md` and `AGENTS.md` at the repository root and cross-link them.
- Treat `AGENTS.md` as **instructions for coding agents** (a “README for agents”), not as a required schema or machine-readable registry.
- Keep `AGENTS.md` short and operational:
  - Prefer copy-paste runnable commands.
  - Do not document “example” commands that do not exist in the repo.
  - Link out to deeper docs instead of duplicating them.
- If instructions conflict:
  1. **Explicit user instructions win**.
  2. Otherwise, the **most specific instruction file for the edited path wins** (nearest `AGENTS.md`, plus any tool-specific path instructions).
- If you need a **machine-readable agent inventory**, keep it **out of `AGENTS.md`** (e.g., `catalog/runtime-agents.yaml`) and label it as a repository-specific extension.

---

## Canonical Definitions

### README.md

**Definition**: The authoritative human-facing instruction manual for a repository or subsystem, providing orientation, setup instructions, and navigation to deeper documentation.

**Scope**:
- **Includes**:
  - Repository/module purpose and value proposition
  - Technical stack and prerequisites
  - Installation and quick start procedures
  - High-level directory structure explanation
  - Links to specialized documentation (`AGENTS.md`, `SSOT.md`, `PLAN.md`)
- **Excludes**:
  - Detailed API specifications (belongs in dedicated docs)
  - Agent-specific operational instructions (belongs in `AGENTS.md`)
  - Low-level implementation details (belongs in code comments)

**Authoritative Source**: [GitHub README Documentation](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)

### AGENTS.md

**Definition**: A simple, open format for guiding coding agents. Think of `AGENTS.md` as a **README for agents**: a dedicated, predictable place to provide context and instructions that help AI coding agents work effectively on your project.

**Notes**:
- No required fields. `AGENTS.md` is standard Markdown; use any headings you like.
- Prefer **short, actionable instructions** over long prose. Use links (“pointer pattern”) to deeper docs.
- Commands in `AGENTS.md` **MUST** be copy-paste runnable in the repo as written (or explicitly marked as placeholders).
- `AGENTS.md` is about **how to work on the repo**, not about describing hypothetical agents.

**Recommended sections** (not required):
- Project overview (agent-focused)
- Setup / build / test commands (copy-paste runnable)
- Code style & conventions (tool-enforced rules first)
- Testing instructions (how to run locally; how CI differs)
- Security notes (what must never be done)
- PR / commit guidelines (required checks, conventions)
- Context links (README, SSOT topics, architecture docs)

**Authoritative Sources**:
- https://agents.md
- https://github.com/agentsmd/agents.md

**Ecosystem & governance (signals, not requirements)**:
- Adoption signal: agents.md tracks 60k+ OSS repos via GitHub code search: https://github.com/search?q=path%3AAGENTS.md+NOT+is%3Afork+NOT+is%3Aarchived&type=code
- Governance signal: the agents.md website footer states “AGENTS.md a Series of LF Projects, LLC”
- Canonical repo: prefer `https://github.com/agentsmd/agents.md` (legacy links may still point elsewhere)

### Runtime Agent Registry (Repository-Specific, Optional)

**Definition**: A repository-specific, machine-readable inventory of long-running “runtime agents” (services, automations, scheduled jobs) or organizational “roles” that you want to track as structured data.

**Notes**:
- This is **not** part of the `AGENTS.md` open format.
- Keep it separate (e.g., `catalog/runtime-agents.yaml`) so `AGENTS.md` stays short and tool-agnostic.
- Treat it as a normal SSOT artifact: versioned, reviewed, and validated.

### Terminology

- **Coding agent**: An interactive assistant used to edit code and docs (e.g., IDE agent, CLI agent). It consumes instruction files like `AGENTS.md`.
- **Runtime agent**: A long-running component in your system (service, worker, bot) with an operational lifecycle.
- **Agent profile**: A named set of configuration/instructions for a tool or workflow (may be in `AGENTS.md`, `.github/*`, or tool-specific config).

### Worldview Boundary

**Definition**: An architectural division point where a subsystem has sufficiently distinct purpose, dependencies, or operational context to warrant independent documentation.

**Objective signals** (the more you have, the more likely you are at a boundary):
- Independent deployable artifact (separate app/service/package release)
- Independent CI pipeline (separate workflows or separate job matrix entries)
- Independent manifest/lockfile (`package.json`, `pyproject.toml`, `go.mod`, etc.)
- Distinct runtime prerequisites (different Node/Python/Java versions, OS deps, etc.)
- Distinct ownership (separate team/reviewers/on-call)
- Distinct primary language or framework

**Scoring heuristic** (adjust to your repo):
- Score each signal: `0 = absent`, `1 = partial`, `2 = strong`
- **6+**: likely a worldview boundary → consider `README.md` + `AGENTS.md`
- **4–5**: depends → consider a subdirectory README only, or a short `AGENTS.md` delta
- **0–3**: not a boundary → do not add README/AGENTS

**Candidate boundary roots are configurable**. Common defaults: `apps/`, `packages/`, `services/`. Add others (e.g., `components/`, `infra/`) only if they meet the boundary signals.

### Precedence & Inheritance

**Goal**: When instructions conflict, agents must not “average” them. The winner must be deterministic.

**Precedence rules**:
1. **Explicit user instructions MUST win** over any repository instruction file.
2. Otherwise, **the most specific instruction for the edited path SHOULD win**, in this order:
   - Tool-specific path-scoped instructions (if your tool supports them)
   - The nearest `AGENTS.md` in the directory tree that contains the edited file
   - Repo-wide instruction files (root `AGENTS.md`, `.github/*` repo-wide instructions)
3. `README.md` is for humans; `AGENTS.md` is for agent operations. If both specify the same command, they **MUST** match.

**Inheritance model**:
- Child `AGENTS.md` files **inherit** parent intent but should contain **deltas only**.
- Child files **SHOULD** link to parent `AGENTS.md` and `README.md` instead of copying content.

---

## Core Patterns

### Pattern: Root Documentation Pair (README + AGENTS)

**Intent**: Establish predictable entry points for both humans and agents.

**Implementation**:

```text
/
├── README.md          # Human entry point (map)
├── AGENTS.md          # Agent entry point (instructions)
├── docs/              # Deep dives, SSOT topics
├── apps/              # Optional: worldview boundaries
├── packages/          # Optional: worldview boundaries
└── services/          # Optional: worldview boundaries
```

**Root README.md Template** (copy-paste safe):

````markdown
# <Project Name>

## Overview
<What this repo does, in 2–3 sentences.>

## Quick start

```bash
# Prerequisites
# - Use an active, supported runtime (e.g., Node.js LTS).
# - Prefer project-pinned tool versions (e.g., via `packageManager` + Corepack).

corepack enable
pnpm install

# Replace these with real scripts that exist in this repository.
pnpm run dev
pnpm run test
pnpm run lint
```

## Documentation
- Agent instructions: [AGENTS.md](./AGENTS.md)
- Canonical definitions (SSOT): [docs/SSOT.md](./docs/SSOT.md)
- Execution planning methodology: [docs/EXEC_PLAN.md](./docs/EXEC_PLAN.md)

## Repository layout
- `docs/` - Specifications and deep dives
- `apps/` - Deployable applications (if present)
- `packages/` - Shared libraries (if present)
- `services/` - Deployable services/workers (if present)
````

**Root AGENTS.md Template** (standard-aligned):

```markdown
# AGENTS.md

## Project overview
<What this repo does, in agent-friendly terms.>

## Setup commands
- Install dependencies: `<command>`
- Start dev: `<command>`

## Build & test
- Lint: `<command>`
- Typecheck: `<command>`
- Tests: `<command>`

## Code style
- <Concrete rules enforced by tooling (formatter, linter, naming conventions).>

## Security notes
- <What must never be done (secrets, prod data access, exfiltration, etc.).>

## PR guidelines
- <Required checks, branch rules, commit conventions.>

## Context links
- Human README: `./README.md`
- Canonical definitions: `./docs/SSOT.md`
```

**Trade-offs**:
- ✅ Clear separation: humans get orientation; agents get operational instructions.
- ⚠️ Requires discipline: keep `AGENTS.md` short; move catalogs/registries to separate files.

### Pattern: Worldview-Boundary Subdirectory Docs

**Intent**: Provide localized instructions where context meaningfully diverges (different runtime, commands, policies).

**Implementation**:

```text
/
├── README.md
├── AGENTS.md
├── apps/
│   ├── web/
│   │   ├── README.md
│   │   ├── AGENTS.md
│   │   └── src/          # ← NO README/AGENTS here
│   └── api/
│       ├── README.md
│       └── AGENTS.md
└── packages/
    └── ui-kit/
        ├── README.md
        └── AGENTS.md
```

**Subdirectory AGENTS.md Template** (delta-only):

```markdown
# AGENTS.md (apps/web)

## Inherits
- Parent agent instructions: `../../AGENTS.md`
- Human overview: `./README.md` (and `../../README.md`)

## Local setup
- Install deps: `<command>`
- Start dev: `<command>`

## Local test
- Tests: `<command>`

## Local notes
- <Only what differs from parent instructions.>
```

**Trade-offs**:
- ✅ Reduces noise for subsystem work, improves command accuracy.
- ⚠️ Risk of duplication; enforce delta-only and link-based inheritance.

### Pattern: The Pointer Pattern (Keep AGENTS.md Small)

**Intent**: Prevent context overload and instruction drift.

**Guidelines**:
- `AGENTS.md` **SHOULD** stay under ~200 lines (adjust as needed).
- Prefer bullets over paragraphs.
- Prefer links to `docs/` for long-form explanations.
- If a section grows, split at the next worldview boundary and add a child `AGENTS.md` with deltas.

### Pattern: Optional Runtime Agent Registry (Extension)

**Intent**: Keep structured “agent catalogs” out of `AGENTS.md` while still supporting automation.

**Recommended location**: `catalog/runtime-agents.yaml` (or `catalog/agents.yaml`)

**Example**:

```yaml
# catalog/runtime-agents.yaml
version: 1
agents:
  - id: billing-worker
    type: runtime
    owner: team-payments
    repo_paths:
      - services/billing/
    interfaces:
      - queue: billing.jobs
    deployments:
      - environment: prod
        schedule: "*/5 * * * *"
```

**Rule**: If you add a registry, `AGENTS.md` should link to it and clearly state it is repository-specific (not part of the open format).

### Pattern: README ↔ AGENTS Navigation Chain

**Intent**: Ensure humans and agents can traverse between orientation and operations at every documentation level.

**Implementation**:

In `README.md`:

```markdown
## Documentation
- Agent instructions: [AGENTS.md](./AGENTS.md)
```

In `AGENTS.md`:

```markdown
## Context links
- Human README: `./README.md`
- Canonical definitions: `./docs/SSOT.md`
```

---

## Decision Checklist

### Before Creating a Subdirectory README.md

- [ ] **Worldview Boundary**: Does this directory represent a distinct subsystem with independent lifecycle signals?
- [ ] **Different Commands**: Do setup/build/test steps differ from parent?
- [ ] **Different Runtime**: Does it require a different runtime or toolchain?
- [ ] **Ownership**: Does it have separate ownership or review rules?
- [ ] **Navigation**: Will it link back to the parent README and to the local/parent `AGENTS.md`?

### Before Creating a Subdirectory AGENTS.md

- [ ] **Delta Exists**: Are there concrete instruction deltas (commands, constraints) vs. parent?
- [ ] **Conflict Risk**: Are there tool-specific instructions (e.g., Copilot) that might conflict? If so, is precedence documented?
- [ ] **Executability**: Are all documented commands verified in CI or by a maintainer?
- [ ] **Pointer Pattern**: Can long instructions be moved to `docs/` and linked?

### Content Quality Checks

README.md:
- [ ] Overview explains “what” and “why” in ≤ 3 sentences.
- [ ] Quick start commands are copy-paste runnable (or clearly marked placeholders).
- [ ] Tool versions are derived from repo config (avoid “install globally” guidance when Corepack/pinning exists).
- [ ] Links to `AGENTS.md` and relevant SSOT docs exist.

AGENTS.md:
- [ ] Includes runnable setup/build/test commands (or explicit placeholders).
- [ ] States code style rules that are enforced by tooling.
- [ ] Contains explicit security boundaries (what must not happen).
- [ ] Defines PR/commit requirements that are observable (CI checks).
- [ ] Avoids catalogs and long narratives; uses links for depth.

Runtime agent registry (optional):
- [ ] Clearly labeled as repository-specific (not an AGENTS.md requirement).
- [ ] Has a version field and validation strategy.
- [ ] Has traceability for changes (PR links, rationale in `SSOT.md` if needed).

### Anti-Documentation Locations

**NEVER create README.md or AGENTS.md in**:
- [ ] `src/` (implementation root)
- [ ] `src/utils/`, `src/lib/`, `src/helpers/` (utility folders)
- [ ] `src/components/**` (component organization without independent lifecycle)
- [ ] `tests/`, `__tests__/`, `spec/` (test directories)
- [ ] `dist/`, `build/`, `out/` (build artifacts)
- [ ] `node_modules/`, `.git/` (system directories)

---

## Anti-patterns / Pitfalls

### Anti-pattern: Treating AGENTS.md as a Required Schema or Agent Catalog

**Symptom**: `AGENTS.md` becomes a large, structured “inventory” with per-agent fields, required tables, and registry-like content.

**Impact**:
- Tool incompatibility (agents expect a simple instructions file)
- High maintenance cost and frequent drift
- Less useful operational guidance (commands and constraints get buried)

**Remediation steps**:
1. Move registry content to `catalog/runtime-agents.yaml` (or similar).
2. Replace `AGENTS.md` with concise “how to work here” instructions.
3. Add a link from `AGENTS.md` to the registry and mark it as repository-specific.

### Anti-pattern: Conflicting Instruction Files (AGENTS vs Tool-Specific Instructions)

**Symptom**: `AGENTS.md`, `.github/copilot-instructions.md`, and path-scoped instructions disagree on commands, style, or security rules.

**Impact**:
- Agents behave inconsistently across tools
- Review churn (“the agent did the wrong thing”)

**Remediation steps**:
1. Establish precedence (“user > path-specific > nearest AGENTS > repo-wide”) and document it.
2. Make one source canonical (usually `AGENTS.md`) and make tool-specific files reference it.
3. Add CI checks for drift (see Practical Examples).

### Anti-pattern: Unverified or Non-Existent Commands in Docs

**Symptom**: Docs mention scripts/tools that do not exist (e.g., `pnpm agents:run` without a corresponding script).

**Impact**:
- Agents waste cycles failing commands
- Onboarding breaks

**Remediation steps**:
1. Replace invented commands with real scripts from the repo.
2. If you need placeholders, mark them explicitly as `<command>`.
3. Add CI that runs the documented commands.

### Anti-pattern: Broken Markdown Templates (Nested Code Fences)

**Symptom**: A “template inside a template” causes fenced blocks to terminate early, turning the template’s headings into real headings.

**Impact**: Copy-paste becomes unreliable and the doc structure becomes corrupted.

**Remediation steps**:
1. Use a 4-backtick outer fence (````) when the template contains inner fences (```).
2. Prefer inline code for short command lists.

### Anti-pattern: AGENTS.md Bloat

**Symptom**: `AGENTS.md` grows to hundreds of lines of mixed guidance, making it hard for agents to find the few commands they need.

**Impact**: Context compression, missed constraints, inconsistent behavior.

**Remediation steps**:
1. Apply the pointer pattern: move long content to `docs/` and link it.
2. Split at worldview boundaries and keep child `AGENTS.md` delta-only.
3. Audit quarterly and delete stale sections.

### Anti-pattern: Documentation Duplication

**Symptom**: The same content appears in both `README.md` and `AGENTS.md`, or in both parent and child documents.

**Impact**: Drift and confusion about what is authoritative.

**Remediation steps**:
1. Enforce “README = orientation, AGENTS = operations”.
2. Replace duplicated paragraphs with links.
3. Add link-checking and drift detection in CI.

### Anti-pattern: Missing Navigation Links

**Symptom**: `README.md` and `AGENTS.md` exist but do not reference each other (or parent/child docs).

**Impact**: Dead-ends for humans and agents; slow onboarding.

**Remediation steps**:
1. Add a “Documentation/Context links” section to both files.
2. Validate links in CI (see Practical Examples).

---

## Evaluation

### Metrics

**Instruction Completeness** (per `AGENTS.md`):
- **Target**: Setup + Build/Test + Style + Security + PR guidelines + Context links present.
- **Measurement**: Checklist-based audit or simple section detection.

**Command Executability Rate**:
- **Target**: 100% of documented commands in `AGENTS.md` succeed in CI (or are explicitly marked as placeholders).
- **Measurement**: CI job executes commands extracted from a maintained list.

**Conflict-Free Instruction Score**:
- **Target**: No conflicting requirements between `AGENTS.md` and tool-specific instruction files for the same path.
- **Measurement**: CI compares key values (commands, forbidden actions, style rules) or enforces “tool-specific files must link to AGENTS.md”.

**Documentation Drift Detection Coverage**:
- **Target**: Changes to manifests/lockfiles/CI configs require a doc update (README/AGENTS) or an explicit waiver.
- **Measurement**: CI checks PR diffs for “high-impact files changed” without corresponding doc changes.

### Test Strategies

**Human onboarding smoke test**:
- A new contributor follows `README.md` only.
- Success when they can set up and find deeper docs with ≤ 2 navigation hops.

**Agent workflow smoke test**:
- An agent uses `AGENTS.md` only to set up and run tests.
- Success when CI passes and the agent does not need “tribal knowledge”.

---

## Practical Examples

### Tooling / Platform Notes (GitHub Copilot)

GitHub Copilot supports its own instruction files in addition to `AGENTS.md`:
- Repo-wide: `.github/copilot-instructions.md`
- Path-scoped: `.github/copilot-instructions/**/*.instructions.md`

**Recommended policy**:
- Keep canonical “how to work here” instructions in `AGENTS.md`.
- Use Copilot instruction files only for Copilot-specific guidance, and link back to `AGENTS.md`.

**Operational note**: Tool support varies. Ensure your tool is configured to read instruction files from the directory you opened as the workspace root.

### CI/CD Automation (Docs Validation + Drift Detection)

**Intent**: Keep documentation runnable, linked, and up-to-date as the repo evolves.

**Example workflow**:

```yaml
# .github/workflows/validate-docs.yml
name: Validate docs & instructions

on:
  pull_request:
    paths:
      - "**/*.md"
      - ".github/**"
      - "package.json"
      - "pnpm-lock.yaml"
      - "yarn.lock"
      - "package-lock.json"
      - "pyproject.toml"
      - "requirements*.txt"
      - "go.mod"
      - "go.sum"
  push:
    paths:
      - "**/*.md"
      - ".github/**"
      - "package.json"
      - "pnpm-lock.yaml"
      - "yarn.lock"
      - "package-lock.json"

jobs:
  markdown:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6

      - name: Lint Markdown
        uses: DavidAnson/markdownlint-cli2-action@v22
        with:
          globs: |
            **/*.md

      - name: Check links
        uses: lycheeverse/lychee-action@v2
        with:
          args: >-
            --no-progress
            --exclude-mail
            --accept 200,206,429
            .

      - name: Validate README/AGENTS placement (example policy)
        shell: bash
        run: |
          set -euo pipefail

          # Root pair is mandatory
          test -f "./README.md"
          test -f "./AGENTS.md"

          # Example worldview-boundary roots (adjust to your repo)
          while IFS= read -r -d '' dir; do
            has_readme=0
            has_agents=0
            [[ -f "$dir/README.md" ]] && has_readme=1
            [[ -f "$dir/AGENTS.md" ]] && has_agents=1

            # If you create one, strongly prefer creating the other (warn-only here)
            if [[ "$has_readme" -eq 1 && "$has_agents" -eq 0 ]]; then
              echo "Warning: $dir has README.md but no AGENTS.md"
            fi
            if [[ "$has_agents" -eq 1 && "$has_readme" -eq 0 ]]; then
              echo "Warning: $dir has AGENTS.md but no README.md"
            fi
          done < <(find . -maxdepth 2 -type d \\( -path "./apps/*" -o -path "./packages/*" -o -path "./services/*" \\) -print0)

      - name: Drift detection (example)
        if: ${{ github.event_name == 'pull_request' }}
        shell: bash
        run: |
          set -euo pipefail
          base="${{ github.event.pull_request.base.sha }}"
          head="${{ github.event.pull_request.head.sha }}"

          changed="$(git diff --name-only "$base" "$head")"

          # If “high-impact” files changed, require README/AGENTS changes (or add a waiver file).
          needs_docs=0
          echo "$changed" | grep -E -q '(^package\\.json$|^pnpm-lock\\.yaml$|^yarn\\.lock$|^package-lock\\.json$|^\\.github/workflows/)' && needs_docs=1 || true

          if [[ "$needs_docs" -eq 1 ]]; then
            echo "$changed" | grep -E -q '(^README\\.md$|^AGENTS\\.md$|^docs/)' || {
              echo "Error: High-impact changes detected without README/AGENTS/docs updates."
              exit 1
            }
          fi
```

### Migration Guide (Catalog → Instructions)

**Goal**: Align an existing repository that uses `AGENTS.md` as a registry with the open `AGENTS.md` format (instructions-first).

1. **Extract catalogs**: Move any “agent inventory” sections out of `AGENTS.md` into `catalog/runtime-agents.yaml` (or equivalent).
2. **Rewrite `AGENTS.md`**: Keep only operational instructions (setup/build/test/style/security/PR).
3. **Add precedence**: Document conflict rules and ensure subdirectory inheritance is delta-only.
4. **Align tool-specific files**: If using Copilot instructions, make them reference `AGENTS.md` and avoid contradictory rules.
5. **Automate validation**: Add CI for link checks, markdown lint, and drift detection.

---

## Update Log

- **2025-12-17** – Rebranded to SpeSan and performed final content check. (Author: SpeSan)
- **2025-12-17** – Major revision to align with the open `AGENTS.md` standard (instructions-first). Re-defined `AGENTS.md` as “README for agents”, moved catalogs to an optional runtime registry extension, added explicit precedence/inheritance rules, refreshed templates (copy-paste safe fences), updated CI examples (`actions/checkout@v6`), and refreshed references. (Author: SpeSan)
- **2025-11-22** – Refined templates based on peer review. Added `Triggers`, `Implementation`, `Security`, and `Observability` fields to AGENTS.md template. Fixed README.md code block syntax. Clarified document purpose as a guide. (Author: SpeSan)
- **2025-11-19** – Added comprehensive CI/CD Automation section with validation workflows, automated agent extraction from code, and validation scripts. Added Migration Guide with phased approach for converting existing projects to README/AGENTS structure. (Author: SpeSan)
- **2025-11-17** – Updated AGENTS.md basic structure section to include Primary Directive as the first section, providing repository-wide behavior rules for all autonomous agents. Reorganized structure documentation for clarity. (Author: SpeSan)
- **2025-11-15** – Initial document creation based on AGENTS.md spec, README best practices, and AI-first architecture patterns. (Author: SpeSan)
- **2025-11-14** – Standardized Agent Contract and TL;DR sections for consistency with other SSOT documents. Updated canonical URL for renamed file. (Author: SpeSan)

---

## See Also

### Prerequisite Knowledge

- GitHub Flavored Markdown
- Repository structures (monorepo vs polyrepo)
- Documentation-as-code practices

### Related Topics (in this repository)

- `docs/SSOT.md` (governance, normative keywords)
- `docs/EXEC_PLAN.md` (planning methodology for work)
- `docs/CODE_MCP.md` (Model Context Protocol and tool integration)
- `docs/AGENT_SKILL.md` (capability framing)

### Ecosystem

- `AGENTS.md` (instruction standard) and MCP (tool connectivity standard) are complementary:
  - `AGENTS.md` tells an agent **what to do and how to work in this repo**
  - MCP defines **how an agent connects to tools and data sources**

---

## References

- [R1] AGENTS.md. *AGENTS.md: A simple, open format for guiding coding agents*. https://agents.md
- [R2] AGENTS.md GitHub Repository. https://github.com/agentsmd/agents.md
- [R3] GitHub Documentation. *About READMEs*. https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes
- [R4] GitHub Documentation. *Using GitHub Copilot CLI* (instruction files). https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-copilot-cli
- [R5] GitHub Flavored Markdown Specification. https://github.github.com/gfm/
- [R6] Model Context Protocol. https://modelcontextprotocol.io

---

**Document ID**: `agents-readme-guide-v2`
**Canonical URL**: `https://github.com/spesans/dev-ssot/blob/main/docs/README_AGENTS.md`
**Version**: 2.0.0
**License**: MIT
**Maintained By**: Repository documentation team
**Last Review**: 2025-12-17
**Next Review Due**: 2026-01-17 (monthly review cycle)
