# Agents Catalog

> **Machine-readable catalog of autonomous agents operating in this repository**

---

## Primary Directive

All agents operating in this repository must:

1. **Follow SSOT principles** - Reference `docs/SSOT.md` as the authoritative source for definitions
2. **Maintain the 11-section structure** - All documentation must follow the standard architecture
3. **Use ISO 8601 timestamps** - All logged entries use `YYYY-MM-DDTHH:MM:SSZ` format
4. **Preserve traceability** - Document decisions with rationale and evidence

---

## Scope

Complete inventory of autonomous agents operating across this repository.

---

## Agent List

| ID | Type | Scope | Role |
|:---|:-----|:------|:-----|
| `repo-orchestrator` | Manager | Entire repo | Coordinates cross-cutting concerns and architectural consistency |
| `doc-maintainer` | Specialist | `docs/` | Manages SSOT documentation and validates structure |

---

## Agent Definitions

### repo-orchestrator

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

---

### doc-maintainer

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

## Agent Capability Matrix

| Agent ID | Code Gen | Testing | Deploy | Schema | Review | Scope |
|:---------|:--------:|:-------:|:------:|:------:|:------:|:------|
| `repo-orchestrator` | ● | ● | ◐ | ○ | ● | Global |
| `doc-maintainer` | ○ | ○ | ○ | ● | ● | `docs/` |

**Legend**:
- ● Full capability
- ◐ Partial/assisted capability
- ○ No capability

---

## Routing Rules

### Documentation Requests

```
Request Type                    → Agent
─────────────────────────────────────────
General architecture            → repo-orchestrator
Cross-cutting concerns          → repo-orchestrator
Specific SSOT topic             → doc-maintainer
Template maintenance            → doc-maintainer
Freshness validation            → doc-maintainer
```

### Conflict Resolution

When agents have overlapping concerns:

1. **Scope conflict**: Agent with narrower scope takes precedence for its domain
2. **Priority conflict**: Refer to `repo-orchestrator` for resolution
3. **Definition conflict**: `SSOT.md` is the authoritative source

---

## Context & Navigation

| Resource | Description |
|:---------|:------------|
| [Home](./README.md) | Repository overview and human setup instructions |
| [SSOT.md](./docs/SSOT.md) | Governance guide and canonical definitions |
| [AGENT_SKILL.md](./docs/AGENT_SKILL.md) | Universal agent skill specification |
| [EXEC_PLAN.md](./docs/EXEC_PLAN.md) | Task planning methodology |

---

*Last Updated: 2025-11-25*
