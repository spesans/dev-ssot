---
title: Single Source of Truth (SSOT)
slug: ssot-guide
summary: "SSOT principles and implementation guide"
type: guide
tags: [topic, ai-first, ssot, governance, documentation]
schema_version: 2.0.0
document_role: meta_governance
primary_ssot_path: docs/SSOT.md
recommended_project_ssot_path: /SSOT.md
agent_instruction_file: /AGENTS.md
last_updated: 2025-12-29
---

# Single Source of Truth (SSOT)

> Architecture and Governance

> **Note (Determinism)**: In this repository, `docs/SSOT.md` is the authoritative SSOT for SSOT governance terms and normative keywords. In adopter repositories, you MUST declare exactly one "Project SSOT" path (RECOMMENDED: `/SSOT.md`) and ensure `AGENTS.md` / `README.md` link to it. If you keep this governance guide under `docs/`, rename it (e.g., `docs/SSOT_GOVERNANCE.md`) to avoid confusing it with the Project SSOT.

## Agent Contract

- **PURPOSE**:
  - Define SSOT governance and requirement language (BCP 14) for humans and AI agents
  - Provide a deterministic truth hierarchy and conflict-resolution protocol
  - Specify practical patterns for authoring, validating, and evolving SSOT artifacts (Markdown + machine-readable contracts)
- **USE_WHEN**:
  - Resolving conflicting definitions found in multiple documents or code
  - Creating or updating canonical definitions, schemas, enums, policies, or workflows
  - Implementing data contracts (APIs, databases, events, client/server boundaries) that must be validated
  - Auditing for drift between documentation and implementation
- **DO_NOT_USE_WHEN**:
  - Capturing implementation details that belong in code (comments, ADRs, commit diffs)
  - Tracking temporary tasks (use `PLAN.md` per `docs/EXEC_PLAN.md`)
  - Recording historical change history for releases (use `CHANGELOG.md` if applicable)
  - Writing tutorials or how-to guides (use dedicated `docs/` topics)
- **PRIORITY (TYPE-BASED PRECEDENCE)**:
  - **Definitions & Contracts (WHAT things ARE)**:
    1. **Project SSOT** (declared path; in this repo: `docs/SSOT.md`) — **MUST** be the authority for definitions, schemas, enums, and policies.
  - **Operational Instructions (HOW work is performed)**:
    1. `AGENTS.md` (scoped instruction files) — **SHOULD** be the authority for commands, workflows, style, and review steps.
  - **Informative Sources**:
    - `README.md`, wikis, issue comments, code comments — **MAY** provide context but **MUST NOT** override the Project SSOT.
  - **Deterministic conflict rules**:
    - If a definition in `AGENTS.md` contradicts the Project SSOT: the Project SSOT wins for the definition.
    - If a workflow instruction in the Project SSOT contradicts `AGENTS.md`: `AGENTS.md` wins for operational steps.
    - If a user request contradicts the Project SSOT: treat it as a **change request** (do not silently ignore; do not guess).
- **RELATED_TOPICS**:
  - agents-readme
  - exec-plan
  - documentation-as-code
  - governance-policy

### Agent-Specific Behavior

- **When encountering conflicting information**:
  1. Classify the statement as **Definition/Contract**, **Operational Instruction**, or **Implementation Detail**.
  2. Apply **PRIORITY (TYPE-BASED PRECEDENCE)**.
  3. If the Project SSOT is ambiguous or incomplete, produce a **Spec Gap Report** and propose a clarification patch.
- **Spec Gap Report (MUST)**:
  - Use this exact schema so output is deterministic and machine-parsable:

    ```yaml
    spec_gap:
      missing_key: "<term | constant | schema | policy>"
      why_needed: "<why the agent cannot proceed safely>"
      where_used: "<file/symbol/feature or user request>"
      candidate_options:
        - "<option 1>"
        - "<option 2>"
      recommended_default: "<single recommended value>"
      impact:
        if_adopted: "<behavior/change>"
        if_deferred: "<risk/blocker>"
      proposed_ssot_location: "<path#anchor>"
    ```

- **Clarification Patch Format (MUST)**:
  - Provide a unified diff against the Project SSOT (or the closest authoritative file), for example:

    ```diff
    diff --git a/docs/SSOT.md b/docs/SSOT.md
    --- a/docs/SSOT.md
    +++ b/docs/SSOT.md
    @@
    -Old text
    +New text
    ```

- **When generating new code**:
  - Derive constants (API versions, enums, regexes, retention periods) from the Project SSOT.
  - If a required definition does not exist, treat it as a **spec gap** (do not invent values).
- **Link fallback (MUST)**:
  - If a referenced link cannot be retrieved in the current environment, do not guess.
  - Request the needed excerpt, or snapshot the required points into the Project SSOT with a retrieval timestamp.
- **Security & Change Control (MUST)**:
  - Contradictions between a user request and the Project SSOT are handled as a **spec change request**:
    1. Propose an SSOT update (patch) with rationale and impact.
    2. Obtain explicit confirmation.
    3. Implement code changes to match the updated SSOT.
  - Treat unverified external data (logs, third-party API responses, pasted configs) as untrusted input; validate before relying on it.
  - Do not hallucinate policies or requirements not explicitly stated in the Project SSOT.

---

## TL;DR

- **WHAT**: SSOT is a governance architecture designating exactly **one authoritative location** for every critical definition, schema, policy, and workflow.
- **WHY**: Eliminates "multiple truths", reduces agent hallucinations, ensures system consistency, and simplifies maintenance by propagating changes from one source.
- **WHEN**: Apply at repository initialization and maintain continuously as the system evolves.
- **HOW**: Declare a single Project SSOT path; write canonical definitions and machine-readable contracts; make all other documents and code reference the SSOT; enforce via CI.
- **WATCH_OUT**: Avoid stale SSOT, duplication, and stringly-typed validation (grep/regex as a compliance mechanism).

---

## Canonical Definitions

### Single Source of Truth (SSOT)

```yaml
id: ssot
kind: definition
status: stable
owner: doc-maintainer
source_refs: [R8, R9]
changed_in: 2025-12-17T11:46:50Z
```

**Definition**: A data structuring and governance principle where every critical piece of information (definitions, policies, schemas, contracts) is mastered in exactly one authoritative location, and all other locations reference it.

**Scope**:
- **Includes**: canonical definitions, data contracts, governance policies, architecture decisions that affect correctness/safety
- **Excludes**: derived copies (unless auto-generated and read-only), temporary drafts, implementation-only details

**Example**:

```markdown
# README.md
For canonical API definitions, see [SSOT](./docs/SSOT.md).
```

**Sources**: [R8], [R9]

### Project SSOT

```yaml
id: project-ssot
kind: definition
status: stable
owner: repo-orchestrator
source_refs: [R5, R6]
changed_in: 2025-12-17T11:46:50Z
```

**Definition**: The single, explicitly declared artifact (file or directory entrypoint) that is authoritative for a specific repository’s definitions and contracts.

**Requirements**:
- The repository MUST declare the Project SSOT path (e.g., in `AGENTS.md` and in the SSOT frontmatter).
- Every definition/contract MUST have exactly one authoritative location inside the Project SSOT.

**Recommended naming (informative)**:
- Adopter repositories SHOULD use `/SSOT.md` as the Project SSOT, and keep this governance guide under `docs/` with a non-conflicting name (e.g., `docs/SSOT_GOVERNANCE.md`).

**Sources**: [R5], [R6]

### Data Contract

```yaml
id: data-contract
kind: definition
status: stable
owner: doc-maintainer
source_refs: [R3, R4]
changed_in: 2025-12-17T11:46:50Z
```

**Definition**: A formal agreement (schema + semantics) defining the structure, format, and constraints of data exchanged between system components (APIs, databases, events, client/server boundaries).

**Normative format guidance**:
- Machine-validated contracts SHOULD be expressed in **OpenAPI 3.1** and/or **JSON Schema (2020-12)** when applicable.
- OpenAPI 3.1 aligns with JSON Schema 2020-12, enabling a single schema vocabulary across tooling and validation. [R3]

**SSOT relationship**:
- The Project SSOT MUST either:
  - embed the canonical machine-readable schemas using stable markers (see Core Patterns), or
  - link to canonical contract files (preferred) and summarize their intent (human-readable governance).

**Sources**: [R3], [R4]

### Living Governance

```yaml
id: living-governance
kind: definition
status: stable
owner: doc-maintainer
source_refs: [R9]
changed_in: 2025-12-17T11:46:50Z
```

**Definition**: Maintaining the SSOT as a version-controlled, continuously updated artifact that evolves synchronously with the system it governs.

**Core idea**:
- SSOT changes are reviewed like code changes.
- SSOT must be updated before (or alongside) implementation changes.

**Sources**: [R9]

### Spec Gap

```yaml
id: spec-gap
kind: definition
status: stable
owner: repo-orchestrator
source_refs: []
changed_in: 2025-12-17T11:46:50Z
```

**Definition**: A required definition/constraint is missing or ambiguous in the Project SSOT, preventing safe implementation.

**Required handling**:
- Agents MUST stop and produce a Spec Gap Report + clarification patch (see Agent-Specific Behavior).

### Normative Keywords (BCP 14)

```yaml
id: normative-keywords
kind: definition
status: stable
owner: doc-maintainer
source_refs: [R1, R2]
changed_in: 2025-12-17T11:46:50Z
```

The key words “MUST”, “MUST NOT”, “REQUIRED”, “SHALL”, “SHALL NOT”,
“SHOULD”, “SHOULD NOT”, “RECOMMENDED”, “NOT RECOMMENDED”, “MAY”, and “OPTIONAL”
in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174)
when, and only when, they appear in all capitals. [R1] [R2]

**Local conventions**:
- Use uppercase keywords for normative requirements; use lowercase in plain English.
- If a deviation from a **MUST** is necessary, record the justification in the Project SSOT (linkable, reviewable).

---

## Core Patterns

### Pattern: SSOT Placement & Naming

**Intent**: Ensure agents and humans can deterministically locate the Project SSOT and avoid path/name ambiguity.

**Implementation (recommended for adopters)**:

```
repository/
├── SSOT.md                      # Project SSOT (definitions + contracts)
├── AGENTS.md                    # Operational instructions for agents
├── README.md                    # Entry point (links to SSOT + docs)
└── docs/
    └── SSOT_GOVERNANCE.md       # This guide (meta governance)
```

**Implementation (allowed alternative, used by this repository)**:

```
repository/
├── AGENTS.md
├── README.md
└── docs/
    ├── SSOT.md                  # Project SSOT (also contains governance guidance)
    └── ssot/                    # Optional split-out domain topics
```

**Split Trigger (SHOULD)**:
- If the Project SSOT exceeds **50 KiB**, split domain topics into `docs/ssot/*.md` and link them from the SSOT index to keep ingestion/review reliable.

**Tool reality (informative)**:
- Many agent runtimes impose instruction/document size limits; keep instruction files (e.g., `AGENTS.md`) concise and layered by scope. [R5]
- Some tools have legacy rule file formats (e.g., Cursor `.cursorrules`); prefer `AGENTS.md` as the shared instruction file across runtimes. [R14]

### Pattern: Reference-Based Documentation

**Intent**: Prevent duplication and drift by requiring downstream documentation to reference the SSOT instead of copying definitions.

**Implementation**:

```markdown
# ❌ Anti-pattern: Duplication
The base URL is `https://api.example.com/v1`.

# ✅ Correct pattern: Reference
See [SSOT](./docs/SSOT.md#data-contract) for the canonical base URL and auth rules.
```

**Link fallback**:
- If the runtime cannot retrieve the linked SSOT section, snapshot the minimum required excerpt into the consumer document with an ISO 8601 retrieval timestamp.

### Pattern: Data Contracts as Machine-Readable Artifacts

**Intent**: Make contracts executable: validate payloads, generate types, and prevent drift.

**Recommended structure**:

```
repository/
├── openapi/
│   └── api.yaml                 # OpenAPI 3.1 (preferred for HTTP APIs)
├── schemas/
│   └── user.schema.json         # JSON Schema 2020-12 (shared models)
└── docs/
    └── SSOT.md                  # Governance + links + decisions
```

**Guidance**:
- Treat OpenAPI/JSON Schema as the canonical machine-readable truth for validation and generation.
- Use the Project SSOT to govern: ownership, change process, rationale, and high-level semantics.

### Pattern: Schema Embedding in Markdown (Optional)

**Intent**: Enable a single-file SSOT when needed, without breaking Markdown parsing.

**Rules**:
- Precede schema blocks with a stable marker.
- Use a non-breaking fence when demonstrating fences inside Markdown.

**Example (non-breaking fence)**:

````markdown
<!-- ssot-schema:json:User -->
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "id": { "type": "string", "format": "uuid" }
  },
  "required": ["id"],
  "additionalProperties": false
}
```
````

### Pattern: Code Generation from Contracts

**Intent**: Enforce contracts by generating code (types, validators) from the canonical machine-readable artifacts.

**Guidance**:
- Prefer **OpenAPI/JSON Schema → Code** toolchains over parsing Markdown.
- If extracting from Markdown, use a Markdown AST parser + stable markers (do not rely on grep/regex).

**Representative tools (informative)**:
- OpenAPI → TypeScript: `openapi-typescript` [R16]
- JSON Schema → TypeScript: `json-schema-to-typescript` [R17]

### Pattern: CI/CD Validation (Secure, Working Example)

**Intent**: Prevent drift by failing PRs when SSOT rules are violated.

**Security requirement (SHOULD)**:
- Pin GitHub Actions (e.g., `actions/checkout`) to a full-length commit SHA and update via Dependabot/Renovate. [R7] [R15]

**Example**:

```yaml
# .github/workflows/validate-ssot.yml
name: Validate SSOT
on:
  pull_request:
    paths:
      - docs/SSOT.md
      - SSOT.md
      - docs/ssot/**
      - openapi/**
      - schemas/**
      - .github/workflows/validate-ssot.yml

permissions:
  contents: read

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      # Security: pin to a full-length commit SHA (recommended by GitHub)
      - name: Checkout (pinned)
        uses: actions/checkout@8e8c483db84b4bee98b60c0593521ed34d9990e8 # v6.0.1
      - name: Check section ordering
        run: python3 check_section_order.py docs
      - name: Check TOC
        run: python3 check_toc.py docs
      - name: Check references (R#)
        run: python3 check_references.py docs
      - name: Check links
        run: python3 check_links.py docs
```

**Trade-offs**:
- ✅ Works without extra dependencies (good bootstrap)
- ⚠️ Not a full semantic validator; evolve toward structured validation (OpenAPI/JSON Schema validation, Markdown AST linting)

### Pattern: Provide SSOT via MCP (Optional)

**Intent**: Let agents retrieve SSOT/contracts through tools (instead of copying large text into prompts) while preserving traceability.

**Guidance**:
- Publish SSOT artifacts (Markdown + OpenAPI/JSON Schema) as MCP resources with version/commit metadata.
- Treat the Project SSOT as authoritative; MCP is a transport layer, not a second source of truth.
- See `docs/CODE_MCP.md` for a concrete pattern and examples. [R10]

---

## Decision Checklist

- [ ] **SSOT-CHK-001 (Single path)**: The Project SSOT path is declared (and unambiguous).
- [ ] **SSOT-CHK-002 (Type-based precedence)**: `AGENTS.md` instructions do not redefine or contradict SSOT definitions/contracts.
- [ ] **SSOT-CHK-003 (BCP 14)**: Normative Keywords section includes the BCP 14 boilerplate and is referenced by other specs.
- [ ] **SSOT-CHK-004 (Contracts are machine-readable)**: APIs/schemas are represented as OpenAPI 3.1 and/or JSON Schema where applicable.
- [ ] **SSOT-CHK-005 (No duplication)**: Other docs reference SSOT instead of copying canonical values.
- [ ] **SSOT-CHK-006 (Drift protection)**: CI validates SSOT structure and (when present) validates OpenAPI/JSON Schema files.
- [ ] **SSOT-CHK-007 (Secure CI)**: GitHub Actions are pinned to full commit SHAs.
- [ ] **SSOT-CHK-008 (Living governance)**: Changes to SSOT require review and are updated alongside implementation changes.

---

## Anti-patterns / Pitfalls

### Anti-pattern: Multiple Sources of Truth

**Symptom**: `README.md` says API v1, `docs/api.md` says API v2, and code uses v1.5.

**Impact**:
- Agents generate incorrect code.
- Humans lose trust in documentation.

**Solution**: Designate exactly one Project SSOT. Delete conflicting definitions elsewhere and replace them with links.

### Anti-pattern: Implementation as SSOT

**Symptom**: "The code is the documentation."

**Impact**:
- "Why" disappears.
- Contracts become implicit and unreviewable.

**Solution**: Extract contracts and policies into the SSOT; code implements the SSOT.

### Anti-pattern: Stale SSOT

**Symptom**: SSOT defines fields that were removed months ago.

**Solution**: Enforce SSOT updates in PR review and CI checks.

### Anti-pattern: Stringly-Typed Compliance

**Symptom**: Governance is enforced via grep/awk on Markdown prose.

**Impact**: Validation breaks on formatting changes and encourages “gaming the checker”.

**Solution**: Prefer structured artifacts (OpenAPI/JSON Schema) and AST-based linting for Markdown when extraction is required.

---

## Evaluation

### Metrics

- **SSOT Coverage**: % of core entities/policies defined in the Project SSOT.
  - Target: 100% for core entities and safety-critical policies.
- **Documentation Drift**: # of mismatches between SSOT and implementation/contracts.
  - Target: 0; measured on every PR.
- **Spec Gap Rate**: Frequency of missing/ambiguous definitions that block safe work.
  - Target: decreasing over time; measured via Spec Gap Reports.

### Agent Telemetry (Implementable)

#### Cross-Document Telemetry Keys (Minimum)

To enable reproducibility and auditability across **ExecPlans**, **Skills**, and **MCP tool runs**, implementations MUST emit the following minimum correlation keys when applicable:

**MUST**
- `trace_id`: Correlates a multi-step workflow across plans, skills, and tool runs.
- `run_id`: Identifies a single execution attempt within a trace.
- `artifact_id` or `artifact_path`: Points to evidence (log file, JSON output, PLAN path).
- `ssot_document_id`: The SSOT document that governed the run (e.g., `docs/SSOT.md`).
- `ssot_commit`: Git commit SHA of the SSOT version in effect.
- `approval_state`: `NOT_REQUIRED|PENDING|APPROVED|DENIED`.

**SHOULD**
- `tool_name` / `tool_version`
- `sandbox_image` / `runner_id`
- `input_digest` / `output_digest`
- `skill_id` / `skill_version` / `skill_source_commit` (when a skill is involved)

**Notes**
- Field names are intentionally stable across docs. If another doc uses different names, adapters SHOULD map them here.

**Collection points (informative)**:
- PR comments (structured block)
- CI artifacts (`telemetry/*.json`)
- Agent run logs (JSON lines)

**Minimal telemetry schema (example)**:

```json
{
  "ssot_document_id": "docs/SSOT.md",
  "ssot_commit": "<git-sha>",
  "unknown_terms": ["<term>"],
  "sections_cited": ["Canonical Definitions > Data Contract"],
  "spec_gaps": ["<missing_key>"]
}
```

**Optional JSON Schema (example)**:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "AgentTelemetryEvent",
  "type": "object",
  "properties": {
    "ssot_document_id": { "type": "string" },
    "ssot_commit": { "type": "string" },
    "unknown_terms": { "type": "array", "items": { "type": "string" } },
    "sections_cited": { "type": "array", "items": { "type": "string" } },
    "spec_gaps": { "type": "array", "items": { "type": "string" } }
  },
  "required": ["ssot_document_id", "ssot_commit"],
  "additionalProperties": false
}
```

---

## Practical Examples

### Migration Guide: From Chaos to SSOT

**Intent**: Introduce SSOT into an existing repository with scattered documentation and implicit contracts.

**Phase 1: Audit (Day 1–2)**
- Identify all current sources of truth (README, wiki, docs, code constants, schemas).
- List conflicts and decide which should become canonical.

**Phase 2: Establish the Project SSOT (Day 3)**
- Choose and declare the Project SSOT path (RECOMMENDED: `/SSOT.md`).
- If you keep this governance guide under `docs/`, rename it to avoid confusion (e.g., `docs/SSOT_GOVERNANCE.md`).
- Define the top 5 most critical terms/schemas first.

**Phase 3: Refactor Consumers (Week 2)**
- Replace duplicated definitions in `README.md` and `docs/` with links to the SSOT.
- Move executable contracts to OpenAPI/JSON Schema files and link them from SSOT.

**Phase 4: Prevent Regression (Week 3+)**
- Add an SSOT checklist to PR templates.
- Add CI validation (start minimal; evolve toward structured validation).

---

## Update Log

- 2025-12-29 docs(ssot): Clarify Data Contract definition to include client/server boundaries. (Author: SpeSan)
- 2025-12-21 docs(ssot): Add cross-document telemetry keys, update CI validation example with reference linting, and refresh OpenAPI normative reference + retrieved dates. (Author: SpeSan)
- 2025-12-17 Docs(ssot): Rebranded to SpeSan and performed final content check. (Author: SpeSan)
- 2025-12-17T11:46:50Z docs(ssot): Refresh for 2025: resolve placement ambiguity, adopt BCP 14, modernize CI example (actions/checkout v6 + SHA pinning), clarify Data Contracts (OpenAPI 3.1 / JSON Schema), add deterministic agent templates. (Author: SpeSan)
- 2025-11-24T00:00:00Z docs(ssot): Metadata refresh and minor clarifications. (Author: SpeSan)
- 2025-11-22T00:00:00Z docs(ssot): Integrated AI peer review feedback: Agent-Specific Behavior, Security Protocol, glossary template, telemetry fields; clarified guide vs project SSOT. (Author: SpeSan)
- 2025-11-19T00:00:00Z docs(ssot): Initial comprehensive guide structure integrating definitions, patterns, and evaluation metrics. (Author: SpeSan)
- 2025-11-01T00:00:00Z docs(ssot): Seed content based on Docs-as-Code and configuration best practices. (Author: SpeSan)

---

## See Also

### Prerequisites
- [BCP 14 / RFC 2119 + RFC 8174](https://datatracker.ietf.org/doc/rfc8174/) – Normative keyword interpretation [R1] [R2]
- [Secure use of GitHub Actions](https://docs.github.com/en/actions/reference/security/secure-use) – Supply chain hardening and pinning guidance [R7]
- [OpenAPI 3.1 specification](https://spec.openapis.org/oas/v3.1.0) – OpenAPI 3.1 and JSON Schema alignment [R3]
- [Docs as Code](https://www.writethedocs.org/guide/docs-as-code.html) – Treat documentation as an engineering artifact [R9]
- [GitHub Flow](https://docs.github.com/en/get-started/using-github/github-flow) – Lightweight branching model suitable for frequent SSOT updates [R11]
- [Trunk-based development](https://trunkbaseddevelopment.com/) – Alternative branching model optimized for small, frequent merges [R12]
- [A successful Git branching model (Git Flow)](https://nvie.com/posts/a-successful-git-branching-model/) – Historical reference; may be less suitable for high-frequency SSOT changes [R13]

### Related Topics (in-repo)
- [README_AGENTS.md](./README_AGENTS.md) – How SSOT supports the agent ecosystem
- [EXEC_PLAN.md](./EXEC_PLAN.md) – Task planning methodology using SSOT definitions
- [CODE_MCP.md](./CODE_MCP.md) – Exposing SSOT/contracts via MCP
- [TYPESCRIPT_SET.md](./TYPESCRIPT_SET.md) – Language-specific standard (references SSOT for definitions)

---

## References

### Normative References
- [R1] IETF. RFC 2119: "Key words for use in RFCs to Indicate Requirement Levels." https://datatracker.ietf.org/doc/rfc2119/ (retrieved 2025-12-21)
- [R2] IETF. RFC 8174: "Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words." https://datatracker.ietf.org/doc/rfc8174/ (retrieved 2025-12-21)
- [R3] OpenAPI Initiative. "OpenAPI Specification 3.1.0." https://spec.openapis.org/oas/v3.1.0 (retrieved 2025-12-21)
- [R4] JSON Schema. "Draft 2020-12." https://json-schema.org/draft/2020-12/json-schema-core.html (retrieved 2025-12-21)
- [R5] OpenAI. "Custom instructions with AGENTS.md." https://developers.openai.com/codex/guides/agents-md/ (retrieved 2025-12-21)
- [R6] agents.md. "AGENTS.md." https://agents.md/ (retrieved 2025-12-21)
- [R7] GitHub Docs. "Secure use reference." https://docs.github.com/en/actions/reference/security/secure-use (retrieved 2025-12-21)

### Informative References
- [R8] Wikipedia. "Single source of truth." https://en.wikipedia.org/wiki/Single_source_of_truth (retrieved 2025-12-21)
- [R9] Write the Docs. "Docs as Code." https://www.writethedocs.org/guide/docs-as-code.html (retrieved 2025-12-21)
- [R10] Model Context Protocol. "Specification (2025-11-25)." https://modelcontextprotocol.io/specification/2025-11-25 (retrieved 2025-12-21)
- [R11] GitHub Docs. "GitHub Flow." https://docs.github.com/en/get-started/using-github/github-flow (retrieved 2025-12-21)
- [R12] Trunk Based Development. https://trunkbaseddevelopment.com/ (retrieved 2025-12-21)
- [R13] nvie. "A successful Git branching model." https://nvie.com/posts/a-successful-git-branching-model/ (retrieved 2025-12-21)
- [R14] Cursor Docs. "Rules." https://cursor.com/docs/context/rules (retrieved 2025-12-21)
- [R15] GitHub. `actions/checkout`. https://github.com/actions/checkout (retrieved 2025-12-21)
- [R16] GitHub. `openapi-typescript`. https://github.com/openapi-ts/openapi-typescript (retrieved 2025-12-21)
- [R17] GitHub. `json-schema-to-typescript`. https://github.com/bcherny/json-schema-to-typescript (retrieved 2025-12-21)

---

**Document ID**: `docs/SSOT.md`
**Canonical URL**: `https://github.com/spesans/dev-ssot/blob/main/docs/SSOT.md`
**License**: MIT
