---
title: Exec Plan
slug: exec-plan
summary: "Model-agnostic execution planning for long-running agent work"
type: spec
tags: [topic, ai-first, agent, planning, execution, model-agnostic, mcp, a2a, tool-governance]
last_updated: 2025-12-17
---

# Topic: Exec Plan — Model-Agnostic Execution Planning

## Agent Contract

- **PURPOSE**:
  - Define a vendor-neutral specification for long-running AI agent task management using living Markdown plan documents
  - Make execution safe, resumable, and auditable through explicit constraints, evidence capture, and continuous plan updates
  - Enable multi-agent collaboration without losing coherence or violating tool governance
  - Examples of compatible runtimes (non-normative): OpenAI Codex, Claude Code, Gemini, internal agent runners
- **USE_WHEN**:
  - Work is non-trivial: multi-step, cross-cutting, or requires coordination across subsystems
  - Work is interruption-prone: spans multiple sessions, context windows, handoffs, or multiple agents
  - Work is risky: includes irreversible operations, security-sensitive changes, production-adjacent actions, or unknowns
  - Work must be reproducible: acceptance must be demonstrable by commands + expected outputs
- **DO_NOT_USE_WHEN**:
  - Trivial edits that can be completed safely in one short sitting without meaningful risk
  - Exploratory tinkering where you will not preserve state, evidence, or outcomes
  - Real-time multi-human co-editing where a living single-writer plan cannot be maintained
- **PRIORITY**:
  - Self-containment and safety override convenience; if a plan is not self-contained, it is non-compliant
  - The plan is a living document; updates to living sections are mandatory as work progresses
  - “Text is not truth”: validate state with tools/tests and capture evidence rather than relying on descriptions
  - Normative terms (MUST/SHOULD/MAY) follow `docs/SSOT.md`
- **RELATED_TOPICS**:
  - ssot-guide
  - agents-readme
  - code-mcp
  - agent-skill

In this repository, agents that apply this specification in practice (for example `repo-orchestrator` and `doc-maintainer`) are defined in `AGENTS.md`.

### Decision Tree (MUST)

Use an ExecPlan if ANY of the following is true:
- Expected agent work is >30 minutes OR involves >5 non-trivial steps
- Touches multiple subsystems (e.g., UI + API + DB), or requires a refactor with wide blast radius
- Includes operations that may be irreversible or security-sensitive (data loss, auth, payments, production deploy)
- Requires external research / unknowns where assumptions are likely to change
- Requires multi-agent work, a handoff, or spans multiple sessions/context windows

Otherwise, use a lightweight task list.

### Read–Update Loop (MUST)

1. Read the plan end-to-end (including Constraints/Safety and Validation).
2. Execute only the `Next Action` (smallest safe step).
3. Immediately update the living sections (Progress, Surprises, Decision Log, Outcomes when relevant) and bump `updated`.
4. Repeat.

### Stop / Escalation Conditions (MUST)

Stop execution and update the plan when:
- You hit 3 consecutive failed attempts at the same step without new evidence
- A constraint or safety rule would be violated
- The plan’s assumptions are invalidated (requires plan revision)
- A human approval gate is reached (see `Constraints & Safety` and `Tooling Interface & Governance`)

### Integration with Agent Instruction Files (MUST)

Many runtimes rely on repo instruction files (for example `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`).
When executing a plan:
- **Precedence**: runtime/system instructions > scoped repo instruction files > PLAN.md constraints > this spec
- Always follow the strictest applicable constraint; precedence only resolves direct conflicts.
- If instructions conflict, stop and record the conflict under `Surprises & Discoveries` with evidence.

---

## TL;DR

- **WHAT**: ExecPlan is a self-contained, living plan document for executing complex tasks safely over long durations.
- **WHY**: Prevents state loss across sessions/agents, improves reproducibility, and makes decisions auditable.
- **WHEN**: Use when complexity/risk/interruption likelihood is high (not only “time spent”).
- **HOW**: Write a PLAN that follows the Standard ExecPlan Schema, declare tool governance, execute stepwise, and continuously update living sections.
- **WATCH_OUT**: Do not rely on external URLs for execution; snapshot required knowledge into the plan with timestamps and evidence.

---

## Naming & File Conventions (MUST)

This spec distinguishes policy files from per-task plan files.

- `docs/EXEC_PLAN.md`: This specification (policy + schema). It is not a per-task plan.
- `PLAN.md`: A per-task ExecPlan document (living). The file may be named differently (e.g., `plans/<task>-PLAN.md`), but it MUST follow this schema.
- `PLANS.md`: Optional repo-root “planning policy pointer” used by some runtimes; SHOULD link to `docs/EXEC_PLAN.md` and declare repo defaults (profiles, tool allowlists).

**Recommended location for per-task plans**:
- `plans/<yyyy-mm-dd>-<task-slug>-PLAN.md` (or `plans/<task-slug>-PLAN.md`)

**Path assumptions**:
- This document assumes it lives at `docs/EXEC_PLAN.md`.
- Internal doc links are displayed as repo-root paths (e.g., `docs/SSOT.md`) but may link via local relative paths for rendering.

---

## Absolute Requirements (NON-NEGOTIABLE)

Any ExecPlan claiming compliance with this spec MUST satisfy ALL of the following. (Derived from and aligned with PLANS.md-style guidance; see [R1].)

1) **Complete Self-Containment**
   - No external URL is required to execute the plan.
   - External research is allowed, but all execution-critical knowledge MUST be snapshotted into the plan with retrieval timestamp and source. [R1]

   Example snapshot format (recommended):

   ```markdown
   Research Snapshot
   - Retrieved: 2025-11-22T14:05:00Z
   - Source: https://example.com/spec
   - Notes: <only what is required to execute, in your own words>
   ```

2) **Living Document Obligation**
   - `Progress`, `Surprises & Discoveries`, `Decision Log`, `Outcomes & Retrospective` MUST be updated as work proceeds. [R1]

3) **Novice Executability**
   - Assume the executor has only the repo working tree + this plan and no prior memory. [R1]

4) **Observable Working Behavior**
   - Acceptance MUST be phrased as verifiable behavior (commands + expected outputs), not intentions. [R1]

5) **Tool-Grounded Truth**
   - Do not trust descriptions (including the plan itself) over verified tool outputs/tests; record evidence. [R6]

6) **Safety & Governance**
   - The plan MUST declare tool permissions, approval-required operations, and forbidden operations. [R2]

7) **Secrets & Sensitive Data Hygiene**
   - Secrets/PII MUST NOT be embedded in the plan or logs; redact and use placeholders. [R2]

---

## Formatting Rules (Compatibility Profiles)

ExecPlans are consumed by both humans and agent runtimes. Choose a compatibility profile and stick to it.
These rules apply to per-task PLAN files; this spec may use additional Markdown for exposition.

### Timestamp Format (MUST)

- Use RFC 3339 / ISO 8601 timestamps:
  - Recommended (UTC): `YYYY-MM-DDTHH:MM:SSZ`
  - Allowed (local offset): `YYYY-MM-DDTHH:MM:SS+09:00`
- Do NOT use ambiguous formats like `YYYY-MM-DD HH:MM`.

### Profile: Codex-Compatible Strict Mode (`codex-strict`) (SHOULD) [R1]

- **Prose-first**: Prefer paragraphs and bullet lists; avoid tables and HTML.
- **Checklists**: Use checkboxes only in `Progress`. Use bullets elsewhere.
- **Code blocks**: Avoid nested fences; keep snippets short; prefer inline commands like `npm test`.
- **External links**: Do not place execution-critical external URLs in the plan body; if research is required, snapshot the needed content into the plan with timestamp + source URL. Local URLs used only for validation (e.g., `http://localhost:3000/...`) are allowed.

### Profile: Repo-Native Mode (`repo-native`) (MAY)

- GitHub-friendly Markdown (tables, `<details>`) is allowed, but must remain copy-pastable and must not hide required information behind collapsibles.
- Still follow the self-containment, timestamp, and section-order rules.

### Plan Mutability Rules (MUST) [R1]

- **Minor edits** (typos, clarity, formatting) are allowed without a revision entry.
- **Meaning changes** (scope, milestones, acceptance, safety constraints, tool permissions) MUST follow the Plan Revision Workflow and be recorded with evidence and rationale.

---

## Canonical Definitions

### ExecPlan

**Definition**: A self-contained, living plan document that serves as both specification and execution guide for long-running agent work, updated continuously as execution proceeds. [R1]

**Scope**:
- **Includes**:
  - Purpose + context + constraints + acceptance criteria
  - Explicit tooling permissions and approval gates
  - Living sections (Progress/Surprises/Decisions/Outcomes)
  - Recovery paths and evidence capture
- **Excludes**:
  - “Go read this URL” as required execution knowledge
  - Hidden assumptions (“obvious” project conventions not written down)
  - Non-verifiable completion claims

**Related Concepts**:
- **Similar**: Runbooks, technical specs, project plans
- **Contrast**: TODO lists, issue tickets, static requirement docs
- **Contains**: Milestones, concrete steps, validation, decision history

**Example**:

```markdown
# PLAN: Implement OAuth2 Authentication

## Purpose / Big Picture
Enable users to sign in using Google OAuth2. Visible behavior: a “Sign in with Google” button,
Google redirect, and a logged-in dashboard session on return.

## Progress
Status: IN_PROGRESS
Next Action: Implement OAuth2 callback handler.

- [x] 2025-11-16T14:00:00Z - Read existing auth implementation (Author: Agent-007)
- [x] 2025-11-16T14:10:00Z - Identified current session storage and cookie settings (Author: Agent-007)
- [ ] 2025-11-16T14:20:00Z - Implement OAuth2 callback handler (Owner: Agent-007)

## Surprises & Discoveries
- 2025-11-16T14:12:00Z - Existing auth uses JWT + cookie sessions; OAuth2 must integrate without breaking refresh flows.
  Evidence: `src/auth/session.ts:42`
```

**Sources**: [R1]

### PLAN.md

**Definition**: A per-task ExecPlan document (often named `PLAN.md`) that follows the Standard ExecPlan Schema and is updated during execution. [R1]

**Scope**:
- **Includes**: One task’s end-to-end plan, constraints, steps, validation, and living updates
- **Excludes**: Repo-wide policy and global governance (belongs in `docs/SSOT.md` / `PLANS.md`)

**Sources**: [R1]

### PLANS.md

**Definition**: An optional repo-level planning policy file consumed by some agent runtimes; it points to the canonical planning spec and may define default profiles and allowlists. [R1]

**Scope**:
- **Includes**: Defaults (profiles, tool allowlists), pointers to `docs/EXEC_PLAN.md`, and repo-specific conventions
- **Excludes**: Per-task progress and decision history (belongs in PLAN files)

**Sources**: [R1]

### Context Snapshot

**Definition**: A compact, high-signal summary embedded in the plan that enables reliable resumption after context refresh or handoff. [R5]

**Scope**:
- **Includes**: current status, next action, key decisions, blockers, and evidence pointers
- **Excludes**: raw logs and tool output dumps (store elsewhere; summarize here)

**Sources**: [R5]

### Evidence

**Definition**: A minimal, reproducible record that supports a claim (a command, where it ran, and the relevant output/file pointer). [R6]

**Scope**:
- **Includes**: command, working directory, outcome, and a small output excerpt or file path
- **Excludes**: secrets, PII, and large uncurated logs

**Sources**: [R6]

### MCP (Model Context Protocol)

**Definition**: A protocol for standardizing model access to tools and data via servers, with emphasis on tool safety and user consent/controls. [R2]

**Scope**:
- **Includes**: declaring allowed servers/tools, bounding filesystem/network access, and approval gates
- **Excludes**: assuming tool descriptions are trustworthy without verification

**Sources**: [R2]

### A2A (Agent-to-Agent)

**Definition**: An interoperability approach for agent-to-agent messaging designed to complement tool/data protocols (like MCP) for long-running coordinated work. [R3]

**Scope**:
- **Includes**: structured inter-agent messages and coordination over long tasks
- **Excludes**: unlogged, ephemeral chat as the only coordination mechanism

**Sources**: [R3]

### Relationship to SSOT

ExecPlans are self-contained specifications for individual tasks, while `docs/SSOT.md` is the canonical source for long-lived definitions, schemas, and policies in this repository.

- A plan MAY embed only the parts required for the task as a local snapshot, but SHOULD link to the canonical location.
- If a snapshot diverges from canonical SSOT, the plan MUST be updated to match SSOT, or SSOT must be updated via a documented change process.
- If the plan reveals a missing or ambiguous SSOT definition, record it as a spec gap and propose an SSOT update alongside the plan work.

---

## Core Patterns

### Pattern: Standard ExecPlan Schema (MUST)

**Intent**: Enforce a strict, consistent plan structure so agents can parse, execute safely, and resume reliably. [R1]

**Context**: Every per-task PLAN file.

**Implementation**:

Plans that claim compliance with this spec MUST include all sections marked `(MUST)` in the order below. Sections marked `(MUST if ...)` are conditional requirements.

```markdown
---
id: <stable-id>
status: DRAFT | IN_PROGRESS | BLOCKED | DONE | ABANDONED
owner: <human-or-agent-id>
created: 2025-11-22T14:00:00Z
updated: 2025-11-22T14:00:00Z
profile: codex-strict | repo-native
---

# PLAN: <Task Name>

## Purpose / Big Picture (MUST)
<User-visible goal. 1–3 short paragraphs.>

## Progress (MUST)
Status: IN_PROGRESS | BLOCKED | DONE
Next Action: <single smallest safe step>

- [ ] 2025-11-22T14:00:00Z - <action> (Owner: <id>)

## Context and Orientation (MUST)
<Current architecture, key files, current behavior, and term definitions.>

## Interfaces & Dependencies (SHOULD)
<APIs, data contracts, external services, and integration points.>

## Constraints & Safety (MUST)
### Allowed Scope
- Allowed directories: `src/**`, `tests/**`
- Allowed environments: local/dev only

### Approval-Required Operations
- Dependency upgrades
- Database migrations
- Any deploy/release step
- Any external network call that sends data outside the org

### Forbidden Operations
- Destructive deletes without explicit approval (e.g., `rm -rf`, dropping prod DBs)
- Exfiltration of secrets/PII

### Secrets & PII
- Never paste secrets into this plan or logs; use `<REDACTED>` placeholders.

## Tooling Interface & Governance (MUST)
<Declare allowed tools, MCP servers (if any), allowed roots, and required approvals.>

## Plan of Work (MUST)
<Prose description of approach and ordering.>

## Milestones (SHOULD)
<Decompose into independently verifiable chunks with deliverables and checkpoints.>

## Concrete Steps (SHOULD)
<Step-by-step commands with cwd and expected outcomes. Prefer small steps.>

## Validation & Acceptance (MUST)
<Acceptance criteria + how to verify with commands and expected outputs.>

## Idempotence & Recovery (SHOULD)
<How to retry safely, rollback, and recover from partial failure.>

## Surprises & Discoveries (MUST)
- 2025-11-22T14:10:00Z - <discovery> (Evidence: <file/command>)

## Decision Log (MUST)
- 2025-11-22T14:20:00Z - Decision: <what>
  Alternatives: <A>, <B>
  Rationale: <why>
  Consequences: <what this enables/risks>
  Evidence: <command/file>
  Author: <id>

## Inter-Agent Messages (MUST if multi-agent)
- 2025-11-22T14:30:00Z - From: <agent> To: <agent>
  Intent: <request/notify/block>
  Message: <content>
  Acceptance/Test: <what proves it’s done>

## Handoff Summary (MUST on handoff; SHOULD otherwise)
<Context Snapshot for the next agent/session.>

## Outcomes & Retrospective (MUST)
<What shipped, what changed, what was learned, and follow-ups.>
```

**Key Principles**:
- **Strict ordering**: agents should not infer structure from “similar-looking” headings.
- **Resumability**: `Progress` MUST include `Status` and `Next Action`.
- **Safety first**: constraints, approvals, and forbidden ops are explicit and enforced by stopping.
- **Evidence over narrative**: claims are supported by minimal evidence.

**Trade-offs**:
- ✅ **Advantages**: predictable parsing, safer execution, reliable handoffs, auditable decisions
- ⚠️ **Disadvantages**: verbose for small tasks; requires discipline to keep living sections current
- 💡 **Alternatives**: lightweight checklists for trivial tasks

**Sources**: [R1], [R2]

### Pattern: Plan → Implement → Verify (SHOULD)

**Intent**: Reduce errors by separating planning, implementation, and verification, while allowing context refresh when it helps. [R1]

**Context**: Medium/large tasks with meaningful risk, unknowns, or long tool output histories.

**Implementation**:

```markdown
# Phase 1: Plan
Create or update the PLAN only. Do not change code.

# Phase 2: Implement
Follow `Next Action` iteratively, updating living sections as you go.

# Phase 3: Verify
Run the Validation & Acceptance commands. Fix gaps. Update Outcomes.
```

**Context Refresh Triggers** (SHOULD) [R5]:
- Context is polluted by long logs/tool output
- Switching subsystems or re-scoping the plan
- Handoff to a different agent/runtime

**Sources**: [R1], [R5]

### Pattern: Context Snapshot & Resumption (MUST on context refresh/handoff)

**Intent**: Preserve execution state across sessions and agent handoffs without relying on memory. [R5]

**Context**: Any time you start a new session, change agent/runtime, or prune context.

**Implementation**:

```markdown
## Handoff Summary
Timestamp: 2025-11-22T16:00:00Z
Status: IN_PROGRESS
Next Action: Run `npm test` and fix the failing OAuth callback test.

What’s done:
- Implemented OAuth callback route and session creation.

Key decisions:
- Used library X for OAuth client (see Decision Log 2025-11-22T14:20:00Z).

Blockers/risks:
- Flaky integration test on CI; needs isolation.

Evidence pointers:
- `src/auth/oauth.ts` updated
- Command: `npm test tests/auth/oauth.test.ts` (last run: 2025-11-22T15:40:00Z, failing)
```

**Key Principles**:
- Keep it short and high-signal; link to evidence rather than pasting logs.
- Always include `Status` and `Next Action`.
- Treat context as finite: store full logs in files/artifacts and only summarize the relevant excerpt in the plan.

**Sources**: [R5]

### Pattern: Prototyping Milestones / Spikes (SHOULD)

**Intent**: De-risk unknowns quickly with timeboxed prototypes, while keeping the plan authoritative. [R1]

**Context**: Unknown libraries, unclear performance characteristics, uncertain APIs, or ambiguous requirements.

**Implementation**:

```markdown
## Plan of Work
1) Timebox a 60-minute spike to validate library/API feasibility.
2) Record findings (with evidence) under Surprises & Discoveries.
3) Decide (Decision Log) and update the plan before proceeding.
```

**Sources**: [R1]

### Pattern: Milestone-Based Structuring (SHOULD)

**Intent**: Decompose large work into independently verifiable chunks to reduce risk and support partial progress. [R1]

**Context**: Any task where a single linear checklist would be too long or cross too many subsystems.

**Implementation**:

```markdown
## Milestones
### Milestone 1: Data Model + Migration
- Deliverables:
  - `migrations/001_create_notifications.sql`
  - `src/models/Notification.ts`
- Verify:
  - Run `npm test tests/models/notification.test.ts`
  - Expected: tests pass and migration applies cleanly

### Milestone 2: API Endpoint
- Deliverables:
  - `src/api/notifications.ts`
- Verify:
  - Run `curl -s http://localhost:3000/api/notifications | head`
  - Expected: JSON array response (non-empty in seeded env)
```

**Key Principles**:
- Each milestone has deliverables and a verification method.
- Avoid unverifiable “done” states; define what success looks like.

**Sources**: [R1]

### Pattern: Multi-Agent Coordination (2025 Standard)

**Intent**: Coordinate multiple agents without conflicting edits or implicit dependencies. [R3]

**Context**: When more than one agent contributes to the same PLAN or codebase concurrently.

**Implementation**:

**Preferred layering**:
1. **A2A** for agent-to-agent messaging (if available). Record summaries in `Inter-Agent Messages`. [R3]
2. **MCP** for tool/data access with explicit allowlists and roots. [R2]
3. **Fallback**: file locks + message passing in the plan.

**Fallback lock file schema**:

```yaml
# .agent-locks.yaml
version: 1
generated_at: 2025-11-19T10:30:00Z
ttl_seconds: 3600
locks:
  - owner: frontend-agent-01
    scope:
      paths:
        - "src/components/**"
        - "styles/**"
    acquired_at: 2025-11-19T10:30:00Z
    expires_at: 2025-11-19T11:30:00Z
    notes: "Editing UI components for notifications"
```

**Inter-Agent Messages format** (plan-local, always logged):

```markdown
## Inter-Agent Messages
- 2025-11-19T10:45:00Z - From: frontend-agent-01 To: backend-agent-02
  Intent: REQUEST
  Message: Need endpoint `GET /api/notifications/unread-count` returning `{ count: number, lastChecked: string }`.
  Acceptance/Test: `curl -s http://localhost:3000/api/notifications/unread-count` returns JSON with those keys.
```

**Conflict resolution rules**:
- Prefer a single “Lead Agent” as the only editor of the plan body; other agents propose changes via messages.
- If locks conflict, stop and resolve explicitly; never “race-edit” the same files.

**Sources**: [R3], [R2], [R1]

### Pattern: Plan Revision Workflow

**Intent**: Safely change scope/approach when discoveries invalidate the current plan, while preserving traceability. [R1]

**Context**: When new evidence makes the current approach incorrect, unsafe, or infeasible.

**Implementation**:

```markdown
## Surprises & Discoveries
- 2025-11-19T14:30:00Z - REVISION NEEDED: Current approach doesn’t meet requirements.
  Evidence: <command/file>

## Decision Log
- 2025-11-19T14:45:00Z - Decision: Revise architecture from A to B.
  Alternatives: Keep A and accept limitation; Use C
  Rationale: Evidence indicates A cannot satisfy acceptance criteria.
  Consequences: Adds new dependency; changes milestones.
  Evidence: <command/file>
  Author: Lead Agent

## Plan Revision History
- 2025-11-19T15:00:00Z - Revision 1: <title>
  Changes:
  - Updated milestones 2–3
  - Updated Validation & Acceptance
  Evidence: <command/file>
  Author: Lead Agent
```

**Key Principles**:
- Record evidence first, then revise.
- Preserve the “before” state (as a snapshot) if it matters for auditability.
- Remove or label any hypothetical numbers; do not present unverified metrics as facts.

**Sources**: [R1]

### Pattern: Evidence Capture (MUST)

**Intent**: Make progress, decisions, and outcomes verifiable and reproducible. [R6]

**Context**: Every time you claim something works, fails, or changed.

**Implementation**:

```markdown
- 2025-11-22T15:40:00Z - Ran `npm test tests/auth/oauth.test.ts` (cwd: repo root) -> FAIL
  Evidence: output excerpt: "Expected 302, got 500"
```

**Sources**: [R6]

---

## Automation & Compliance

### ExecPlan Linting (SHOULD)

To enforce “mandatory updates” and schema consistency, repositories SHOULD provide an `execplan-lint` check in CI that validates:
- Required sections exist and appear in the correct order
- Timestamps match RFC 3339/ISO 8601
- `Progress` includes `Status` and `Next Action`
- External URLs appear only in `See Also` / `References` (or are accompanied by an in-plan snapshot)
- No obvious secret patterns are present (best-effort)

### Machine-Check Examples (MAY)

```bash
# External URLs (heuristic; ignore localhost)
grep -nE 'https?://|www\\.' plans/*-PLAN.md | grep -vE 'https?://(localhost|127\\.0\\.0\\.1)'

# Timestamps (RFC 3339)
grep -nE '[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(Z|[+-][0-9]{2}:[0-9]{2})' plans/*-PLAN.md
```

### Ownership & Change Process (SHOULD)

- Per-task plans SHOULD be updated via PR when work is non-trivial or shared.
- This spec (`docs/EXEC_PLAN.md`) is owned by the documentation maintainers; changes should preserve self-containment and the schema’s machine-readability.

---

## Decision Checklist

- [ ] **Self-Containment**: No execution-critical info requires external URLs. [R1]
  - **Verify**: All required knowledge is in the plan; URLs (if any) have snapshotted excerpts.
  - **Impact**: Agents stall, hallucinate, or execute unsafe guesses.
  - **Mitigation**: Embed the necessary excerpt with retrieval time + source.

- [ ] **Schema & Ordering**: All MUST sections exist and are ordered correctly. [R1]
  - **Verify**: Section headings match the Standard ExecPlan Schema.
  - **Impact**: Tooling and agents mis-parse, causing missed constraints or acceptance checks.
  - **Mitigation**: Start from the template; use linting.

- [ ] **Progress Resumability**: `Status` and `Next Action` are present and correct. [R1]
  - **Verify**: A new agent can resume from `Next Action` without clarification.
  - **Impact**: Work restarts incorrectly or repeats.
  - **Mitigation**: Keep `Next Action` to one smallest safe step.

- [ ] **Tool Governance**: Allowed tools/roots/servers and approval gates are explicit. [R2]
  - **Verify**: There is a clear “allowed/approval-required/forbidden” breakdown.
  - **Impact**: Accidental destructive ops or policy violations.
  - **Mitigation**: Default-deny; expand allowlist only as needed with rationale.

- [ ] **Secrets Hygiene**: No secrets/PII are embedded. [R2]
  - **Verify**: Logs and snippets are redacted; placeholders used.
  - **Impact**: Credential leaks, policy violations, incident response.
  - **Mitigation**: Redact; rotate secrets if exposure occurred.

- [ ] **Observable Acceptance**: Acceptance criteria are testable with commands + expected outputs. [R1]
  - **Verify**: Every acceptance item has a concrete verification step.
  - **Impact**: “Done” becomes subjective; regressions go unnoticed.
  - **Mitigation**: Rewrite criteria as externally observable behavior.

- [ ] **Recovery Readiness**: Retry/rollback paths exist for risky steps. [R1]
  - **Verify**: `Idempotence & Recovery` exists (or equivalent) and is actionable.
  - **Impact**: Partial failure leaves the system stuck or corrupted.
  - **Mitigation**: Add safe rollback commands and “if this fails” paths.

- [ ] **Evidence Capture**: Key claims are backed by minimal evidence. [R6]
  - **Verify**: Progress/discoveries/decisions reference commands or file paths.
  - **Impact**: Future readers cannot trust outcomes.
  - **Mitigation**: Add evidence entries; avoid raw log dumps.

---

## Anti-patterns / Pitfalls

### Anti-pattern: Link-Heavy Plans

**Symptom**: The plan contains “See <URL> for details” where that URL is required to proceed.

**Why It Happens**: It is faster to link than to snapshot; agents may also assume web access.

**Impact**:
- Execution stalls when the URL is inaccessible
- Plan becomes non-deterministic as external docs change
- Different agents interpret external content inconsistently

**Solution**: Snapshot the required excerpt into the plan with retrieval timestamp + source.

**Sources**: [R1]

### Anti-pattern: Ambiguous Time Formats

**Symptom**: Logs use `YYYY-MM-DD HH:MM` or omit timezone.

**Why It Happens**: Human convenience; copy/paste from local clocks.

**Impact**:
- Freshness metrics are wrong
- Handoffs misinterpret ordering

**Solution**: Use RFC 3339 timestamps with `Z` or explicit offsets.

**Sources**: [R1]

### Anti-pattern: Implicit Tool Permissions

**Symptom**: The plan assumes “the agent can just run X” without stating approvals, roots, or forbidden ops.

**Why It Happens**: Tooling differs across runtimes; permissions are easy to overlook.

**Impact**:
- Safety violations and policy breaches
- Unrecoverable destructive changes

**Solution**: Declare tool governance explicitly; default-deny. [R2]

**Sources**: [R2]

---

## Evaluation

### Metrics

**External Dependency Count**: Number of external URLs outside `See Also` / `References` (target: 0). [R1]
- **Measurement**: `grep -nE 'https?://|www\\.' <plan-file> | grep -vE 'https?://(localhost|127\\.0\\.0\\.1)'`

**Acceptance Verifiability Ratio**: % of acceptance criteria with command + expected output (target: 100%). [R1]
- **Measurement**: checklist audit; linter heuristics

**Living Freshness**: Time since last update to living sections during active execution (target: <15 minutes). [R1]
- **Measurement**: compare latest timestamps in `Progress`/`Surprises`/`Decision Log`

**Evidence Coverage**: % of key claims backed by evidence pointers (target: high). [R6]
- **Measurement**: spot-check decisions and discoveries for `Evidence:` lines

**Sources**: [R1], [R6]

### Testing Strategies

**Unit Tests**:
- Commands in `Concrete Steps` and `Validation & Acceptance` run successfully
- Plan file paths and names match the actual repository structure

**Integration Tests**:
- Executing the plan end-to-end achieves the stated purpose
- Tool governance constraints are respected (no forbidden ops)

**Resumption Tests**:
- A new agent can resume from `Handoff Summary` and `Next Action` without re-deriving context

### Success Criteria

- [ ] Plan is self-contained and novice-executable
- [ ] Acceptance is demonstrably met via verifiable commands
- [ ] Living sections reflect real execution state and learnings
- [ ] Decisions and discoveries are traceable to evidence

---

## Copy-Pastable Templates

These templates are intended to be pasted into a PLAN file (remove the outer code fence when you paste).

### Minimal Template (smallest compliant)

```markdown
---
id: <stable-id>
status: IN_PROGRESS
owner: <id>
created: 2025-11-22T14:00:00Z
updated: 2025-11-22T14:00:00Z
profile: codex-strict
---

# PLAN: <Task Name>

## Purpose / Big Picture
<...>

## Progress
Status: IN_PROGRESS
Next Action: <...>

- [ ] 2025-11-22T14:00:00Z - <...> (Owner: <id>)

## Constraints & Safety
<allowed/approval-required/forbidden + secrets rules>

## Tooling Interface & Governance
<allowed tools/roots/servers + approvals>

## Validation & Acceptance
<how to verify + expected outputs>

## Surprises & Discoveries
- 2025-11-22T14:00:00Z - <...> (Evidence: <...>)

## Decision Log
- 2025-11-22T14:00:00Z - Decision: <...> (Rationale: <...>; Evidence: <...>; Author: <id>)

## Outcomes & Retrospective
<...>
```

### Standard Template (recommended)

```markdown
---
id: <stable-id>
status: DRAFT
owner: <id>
created: 2025-11-22T14:00:00Z
updated: 2025-11-22T14:00:00Z
profile: codex-strict
---

# PLAN: <Task Name>

## Purpose / Big Picture
<...>

## Progress
Status: DRAFT
Next Action: <...>

## Context and Orientation
<current behavior, key files, definitions>

## Interfaces & Dependencies
<APIs/contracts/services>

## Constraints & Safety
<allowed/approval-required/forbidden + secrets>

## Tooling Interface & Governance
<tools/MCP servers/roots + approvals>

## Plan of Work
<prose approach>

## Milestones
<independently verifiable chunks>

## Concrete Steps
1) <step> (cwd: <...>) -> expected: <...>

## Validation & Acceptance
- Criterion: <...>
  - Verify: `<command>`
  - Expected: <output excerpt>

## Idempotence & Recovery
<rollback/retry plan>

## Surprises & Discoveries
- 2025-11-22T14:00:00Z - <...> (Evidence: <...>)

## Decision Log
- 2025-11-22T14:00:00Z - Decision: <...>
  Alternatives: <...>
  Rationale: <...>
  Consequences: <...>
  Evidence: <...>
  Author: <id>

## Handoff Summary
<Context Snapshot for resumption>

## Outcomes & Retrospective
<...>
```

### Multi-Agent Add-on (use when >1 agent)

```markdown
## Inter-Agent Messages
- 2025-11-22T14:00:00Z - From: <agent> To: <agent>
  Intent: <REQUEST|NOTIFY|BLOCK>
  Message: <...>
  Acceptance/Test: <...>
```

---

## Update Log

- **2025-12-17** – Rebranded to SpeSan and performed final content check. (Author: SpeSan)
- **2025-12-17T00:00:00Z** – Major revision: added non-negotiable requirements, compatibility profiles, MCP/A2A integration, context snapshot guidance, explicit tool governance, stricter timestamp rules, updated schema with Validation vs Concrete Steps split, and copy-pastable templates. (Author: doc-maintainer)
- **2025-11-22T00:00:00Z** – Refined specification based on peer review. Added Standard ExecPlan Schema and clarified revision protocols. (Author: SpeSan)
- **2025-11-19T00:00:00Z** – Added multi-agent coordination and plan revision workflow patterns. (Author: SpeSan)
- **2025-11-16T00:00:00Z** – Initial document creation based on PLANS.md-style guidance. (Author: Claude)

---

## See Also

### Prerequisites
- [`docs/SSOT.md`](./SSOT.md) – Canonical governance for definitions, MUST/SHOULD semantics, and conflict resolution.
- [`docs/README_AGENTS.md`](./README_AGENTS.md) – How to structure repo instructions (`AGENTS.md`) and AI-first docs.

### Related Topics
- [`docs/CODE_MCP.md`](./CODE_MCP.md) – Practical MCP patterns (sandboxing, allowlists, progressive disclosure) aligned with tool governance.
- [`docs/AGENT_SKILL.md`](./AGENT_SKILL.md) – Baseline agent competencies assumed by this spec.

### Advanced / Platform-specific (not required for execution)
- OpenAI Cookbook PLANS.md guidance – Source inspiration for long-running planning patterns. https://cookbook.openai.com/articles/codex_exec_plans
- MCP specification – Defines tool/data access protocol expectations and safety controls. https://modelcontextprotocol.io/specification/2025-11-25
- A2A announcement – Background on interoperable agent-to-agent coordination. https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/
- GitHub MCP registry/allowlist controls – Example of real-world tool governance evolution. https://github.blog/changelog/2025-11-18-internal-mcp-registry-and-allowlist-controls-for-vs-code-stable-in-public-preview/
- OpenAI Agents SDK session memory – Practical context engineering patterns for long tasks. https://cookbook.openai.com/examples/agents_sdk/session_memory
- Claude Code best practices – Additional guidance on instruction files and operational safety. https://www.anthropic.com/engineering/claude-code-best-practices

---

## References

- [R1] OpenAI. “Using PLANS.md for multi-hour problem solving.” OpenAI Cookbook. https://cookbook.openai.com/articles/codex_exec_plans (accessed 2025-12-17)
- [R2] Model Context Protocol. “Specification.” https://modelcontextprotocol.io/specification/2025-11-25 (accessed 2025-12-17)
- [R3] Google Developers Blog. “Announcing the Agent2Agent Protocol (A2A).” https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/ (accessed 2025-12-17)
- [R4] GitHub Changelog. “MCP registry and allowlist controls for VS Code Stable in public preview.” https://github.blog/changelog/2025-11-18-internal-mcp-registry-and-allowlist-controls-for-vs-code-stable-in-public-preview/ (accessed 2025-12-17)
- [R5] OpenAI Cookbook. “Context Engineering – Short-Term Memory Management with Sessions from OpenAI Agents SDK.” https://cookbook.openai.com/examples/agents_sdk/session_memory (accessed 2025-12-17)
- [R6] OpenAI. “Introducing Codex.” https://openai.com/index/introducing-codex/ (accessed 2025-12-17)
- [R7] Anthropic. “Claude Code Best Practices.” https://www.anthropic.com/engineering/claude-code-best-practices (accessed 2025-12-17)

---

**Document ID**: `docs/EXEC_PLAN.md`
**Canonical URL**: `https://github.com/artificial-intelligence-first/ssot/blob/main/docs/EXEC_PLAN.md`
**License**: MIT
