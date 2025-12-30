---
title: Agents Catalog
slug: agents-catalog
summary: "Runtime agent inventory and routing rules"
type: reference
tags: [agents, catalog, ai-first, routing]
last_updated: 2025-12-31
---

# Agents Catalog

> Machine-readable inventory of autonomous agents operating in this repository.
> This catalog is the authoritative list of agent IDs and their roles. For operational instructions, use repo-root `AGENTS.md`. [R1]

## Agent Contract

- **PURPOSE**:
  - Provide a deterministic inventory of autonomous agents operating in this repository
  - Enable capability-based routing (which agent should handle which request)
  - Preserve traceability for agent definitions and changes over time
- **USE_WHEN**:
  - Selecting an agent role for a task (routing)
  - Reviewing an agent’s declared scope, constraints, and capabilities
  - Auditing whether a requested change requires a different agent/scope
- **DO_NOT_USE_WHEN**:
  - Looking for repo setup/build/test/style instructions (use repo-root `AGENTS.md`)
  - Resolving normative definition conflicts (use `docs/SSOT.md`)
- **PRIORITY**:
  - This catalog defines **which agents exist** and their **declared roles/scopes**.
  - SSOT precedence and conflict rules are defined in `docs/SSOT.md`; this catalog must not override them.
- **RELATED_TOPICS**:
  - ssot-guide
  - exec-plan
  - agents-readme

---

## TL;DR

- **WHAT**: Canonical list of runtime agents (IDs, roles, scopes, capabilities).
- **WHY**: Ensures deterministic routing and avoids “phantom agents”.
- **WHEN**: Before starting non-trivial work or when scope ownership matters.
- **HOW**: Keep `docs/AGENTS_CATALOG.md` and `src/catalog/runtime-agents.yaml` in sync; validate via CI checks.
- **WATCH_OUT**: Capabilities are not permissions; SSOT constraints still apply.

---

## Canonical Definitions

### Catalog Source of Truth

**Definition**: The canonical inventory is maintained in `src/catalog/runtime-agents.yaml`; this document is the human-readable mirror and index. [R1]

**Scope**:
- **Includes**: agent IDs, role/scope, declared capabilities, constraints, routing rules
- **Excludes**: tool/runtime-specific instructions (kept in repo-root `AGENTS.md`)

**Sources**: [R1]

### Agent List

| ID | Type | Scope | Role |
|:---|:-----|:------|:-----|
| `repo-orchestrator` | Manager | Entire repo | Coordinates cross-cutting concerns and architectural consistency |
| `doc-maintainer` | Specialist | `docs/` | Maintains SSOT docs and validates structure |

### Agent Definitions

#### `repo-orchestrator`

| Field | Value |
|:------|:------|
| **Type** | Manager |
| **Scope** | Entire repository |
| **Version** | 1.0.0 |

**Mission**: Coordinate multi-agent workflows, resolve conflicts, and maintain architectural consistency across the repository.

**Triggers**:
- Manual invocation via CLI
- Cross-cutting documentation requests
- Conflict resolution between specialists

**Inputs**:
- Task requests
- Agent capability queries
- Conflict reports
- Architecture review requests

**Outputs**:
- Task assignments
- Resolution decisions
- Architecture guidance
- Consistency reports

**Tools**:
- GitHub API
- Static analysis tools
- Documentation validators

**Capabilities**:

| Capability | Level |
|:-----------|:-----:|
| Code Generation | ● Full |
| Testing | ● Full |
| Deployment | ◐ Partial |
| Schema Management | ○ None |
| Review | ● Full |

**Constraints**:
- Must consult specialists before cross-cutting changes
- Ensures all documentation follows SSOT principles
- Cannot modify database schemas directly
- Requires approval for dependency updates

#### `doc-maintainer`

| Field | Value |
|:------|:------|
| **Type** | Specialist |
| **Scope** | `docs/` directory and repository root documentation |
| **Version** | 1.0.0 |

**Mission**: Maintain the Single Source of Truth (SSOT), ensure documentation freshness, and validate structure against templates.

**Triggers**:
- Changes to `docs/**/*.md`
- Documentation update requests
- New feature specifications
- Policy changes

**Inputs**:
- Documentation update requests
- New feature specs
- Policy changes
- Template updates

**Outputs**:
- Updated `.md` files
- Validation reports
- Structure compliance reports
- Freshness audits

**Tools**:
- Markdown linters
- Frontmatter validators
- Git history analysis
- Link checkers

**Capabilities**:

| Capability | Level |
|:-----------|:-----:|
| Code Generation | ○ None |
| Testing | ○ None |
| Deployment | ○ None |
| Schema Management | ● Full |
| Review | ● Full |

**Constraints**:
- Must strictly follow the 11-section structure for all topic documents
- Must verify no duplication exists against `SSOT.md`
- Must update `last_updated` field on modifications
- Cannot modify code files outside documentation

---

## Core Patterns

### Pattern: Routing a Request

**Intent**: Pick the smallest-scope agent that can safely execute the request.

**Context**: Any task that touches multiple directories, changes governance rules, or updates templates.

**Implementation**:
- Prefer `doc-maintainer` for changes under `docs/**` that do not require cross-cutting decisions.
- Prefer `repo-orchestrator` for cross-cutting changes across multiple domains (docs + tooling + CI).
- If in doubt, default to `repo-orchestrator` for initial triage, then delegate.

**Sources**: [R1]

### Pattern: Conflict Resolution (SSOT-aligned)

**Intent**: Resolve conflicts deterministically without violating SSOT constraints.

**Context**: Conflicting instructions, overlapping agent scopes, or conflicts between a user request and repository governance.

**Implementation**:
- **Type-based precedence** (definitions/contracts vs operational instructions) is defined in `docs/SSOT.md`.
- If a **user request** conflicts with SSOT **definitions/contracts/safety constraints**, treat it as a **spec change request** (propose → confirm → apply).
- For overlapping agent scopes:
  - **Narrower scope wins** for domain-specific edits.
  - Escalate cross-cutting conflicts to `repo-orchestrator` for triage.

**Sources**: [R1]

### Pattern: Updating the Catalog

**Intent**: Keep the catalog machine-usable and traceable.

**Context**: Adding/removing an agent, changing scope/capabilities, or updating routing rules.

**Implementation**:
- Update `src/catalog/runtime-agents.yaml` first.
- Mirror the change in this document.
- Update `last_updated` and add an `Update Log` entry.
- Run doc validation (`mkdocs build --strict` and check scripts).

**Sources**: [R1]

---

## Decision Checklist

- [ ] **Inventory updated**: Agent changes are reflected in `src/catalog/runtime-agents.yaml`. [R1]
  - **Verify**: YAML includes the new/updated agent ID and fields.
  - **Impact**: Routing becomes ambiguous or inconsistent.
  - **Mitigation**: Treat YAML as authoritative and regenerate/repair the mirror.
- [ ] **Mirror updated**: `docs/AGENTS_CATALOG.md` matches the YAML inventory. [R1]
  - **Verify**: Agent IDs and roles match.
  - **Impact**: Humans and tools disagree on which agents exist.
  - **Mitigation**: Update the mirror and re-run checks.

---

## Anti-patterns / Pitfalls

### Anti-pattern: Treating capabilities as permission

**Symptom**: “Agent X can deploy, therefore deploy is allowed.”

**Why It Happens**: Capability tables look like authorization matrices.

**Impact**:
- Violates SSOT safety constraints
- Creates non-deterministic behavior across runtimes

**Solution**: Treat SSOT constraints and tool governance as the source of permission; capabilities are descriptive only. [R1]

**Sources**: [R1]

---

## Evaluation

### Validation Commands

- `python3 src/checks/check_section_order.py docs`
- `python3 src/checks/check_toc.py docs`
- `python3 src/checks/check_references.py docs`
- `python3 src/checks/check_links.py docs`
- `python -m mkdocs build --strict`

**Sources**: [R1]

---

## Update Log

- **2025-12-31** – Update inventory and validation command paths after moving tooling under `src/`. (Author: repo-orchestrator)
- **2025-12-30** – Align catalog conflict-resolution guidance with SSOT (type-based precedence + spec change request protocol). (Author: repo-orchestrator)
- **2025-12-30** – Split Agents Catalog out of repo-root `AGENTS.md`; added YAML mirror and MkDocs nav support. (Author: repo-orchestrator)

---

## See Also

### Prerequisites
- [SSOT.md](./SSOT.md) – Definitions, contracts, and conflict rules

### Related Topics
- [EXEC_PLAN.md](./EXEC_PLAN.md) – Execution planning methodology
- [README_AGENTS.md](./README_AGENTS.md) – Patterns for instruction files and precedence

---

## References

- [R1] SpeSan. "SSOT for AI-First Development: SSOT." https://github.com/spesans/dev-ssot/blob/main/docs/SSOT.md (accessed 2025-12-30)

---

**Document ID**: `docs/AGENTS_CATALOG.md`
**Canonical URL**: `https://github.com/spesans/dev-ssot/blob/main/docs/AGENTS_CATALOG.md`
**License**: MIT
