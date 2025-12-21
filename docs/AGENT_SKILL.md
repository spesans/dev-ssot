---
title: Universal Agent Skill
slug: agent-skill
summary: "Skill spec overview"
type: spec
tags: [topic, ai-first, agent, skill, specification]
last_updated: 2025-12-21
---

# Universal Agent Skill

> Universal Specification

## Agent Contract

- **PURPOSE**:
  - Define a vendor-neutral, SSOT-friendly specification for **Agent Skills** as portable, folder-based packages
  - Standardize **skill discovery, metadata, tool contracts, permissions/safety, and execution hooks**
  - Provide a deterministic bridge from **Skill packages** to major host ecosystems (Claude Skills, MCP tools, OpenAI tool calling) via explicit **Host Profiles** and **Adapter rules**
- **USE_WHEN**:
  - Authoring reusable agent capabilities that must be portable across hosts/runtimes
  - Building a skill library for a team/org with governance, reviewability, and predictable behavior
  - Implementing an adapter that maps folder-based skills into a host tool system (Claude API, MCP, OpenAI Responses/tool calling)
- **DO_NOT_USE_WHEN**:
  - You only need a one-off script with no portability or governance requirements
  - You are implementing a host-specific feature that cannot reasonably be expressed as a portable skill (document it under the host’s own spec instead)
- **PRIORITY**:
  - Normative requirement keywords (MUST/SHOULD/MAY) follow `docs/SSOT.md` (BCP 14) and are interpreted only when capitalized
  - The baseline `SKILL.md` format follows the open Agent Skills standard (agentskills.io). [R11]
  - This spec separates:
    - **Normative Specification**: Universal requirements intended to be host-agnostic
    - **Host Profiles**: Host facts and constraints (with primary-source links)
  - If a Host Profile conflicts with the Normative Specification, host constraints win for that host; record the delta via `host_overrides`
- **RELATED_TOPICS**:
  - ssot-guide
  - exec-plan
  - code-mcp

In this repository, responsibilities for applying this specification are assigned to the `repo-orchestrator` and `doc-maintainer` agents described in `AGENTS.md`.

---

## TL;DR

- **WHAT**: A **Skill** is a folder with a required `SKILL.md` (YAML frontmatter + Markdown body) plus optional scripts, references, and assets. [R11]
- **WHY**: Skills encode reusable procedures and tool contracts with **progressive disclosure** (metadata first, detail on-demand) to improve reliability and reduce context overhead.
- **HOW (Canonical)**:
  - **Source of truth** is `SKILL.md` frontmatter (`name`, `description`) + Markdown body (Agent Skills standard). [R11]
  - **Progressive disclosure**: load metadata at discovery, load instructions/resources only when activated. [R11], [R12]
  - **Tool contracts** (`tools` / `tools.json`) are OPTIONAL extensions for tool-enabled adapters and use **JSON Schema 2020-12**. [R7]
- **HOST REALITY**:
  - **Claude API Skills** are attached via `container.skills` and have hard limits (e.g., max 8 skills/request, 8MB upload) [R2]
  - **OpenAI Structured Outputs** and tool calling can enforce schemas with `strict: true` [R5]
- **MCP** is a tool connectivity protocol (not a skill format) and maps via a stable schema translation (`input_schema` → `inputSchema`) [R4]
- **Codex Agent Skills** are discovered from multiple scopes with higher-precedence overrides: [R12]
  - `CWD`: `./.codex/skills` (highest; per-working-dir overrides)
  - `PARENT`: a folder above CWD within a git repo
  - `REPO`: `$REPO_ROOT/.codex/skills`
  - `USER`: `$CODEX_HOME/skills` (default: `~/.codex/skills`)
  - Skills can be invoked explicitly or implicitly when the task matches the description. [R12]
- **WATCH_OUT**:
  - Do not ship broken examples (SSOT risk): examples must be runnable-minimal or explicitly “pseudocode”
  - Avoid “runtime: node + .ts entrypoint” unless the host explicitly provides a TypeScript runner (default Node cannot execute TS)
  - Keep frontmatter concise; large content belongs in the body or referenced files

---

## Canonical Definitions

### Skill Package

**Definition**: A portable, folder-based unit of agent capability consisting of a required `SKILL.md` plus optional code and resources.

**Scope**:
- **Includes**:
  - `SKILL.md` (required): YAML frontmatter (machine-readable) + Markdown instructions (model-readable)
  - Optional implementations under `scripts/` and optional supporting files (`references/`, `assets/`, `tests/`, etc.)
- **Excludes**:
  - Host-locked configuration that cannot be expressed as `host_overrides`

**Sources**: [R11]

### Skill Manifest (`SKILL.md`)

**Definition**: The single source of truth file inside a skill package.

**Rules**:
- MUST be located at the skill root: `/<skill_dir>/SKILL.md`
- MUST begin with YAML frontmatter delimited by `---`
- MUST contain a Markdown body that can be injected/loaded on demand by the host

**Sources**: [R11], [R2], [R3]

### Universal Skill Frontmatter

**Definition**: The YAML frontmatter object at the top of `SKILL.md`. The Agent Skills standard requires `name` and `description` and defines a small set of optional fields; this document adds SSOT-oriented extensions for hosts/adapters that support them. [R11]

**Why it matters**:
- Hosts discover skills primarily through `name`/`description` at startup, then load the full instructions on activation (progressive disclosure). [R11], [R12]
- If you ship executable scripts/tools, machine-validation (schema/permissions/safety) reduces drift and surprises.

**Sources**: [R11], [R12]

### Tool Contract

**Definition**: A tool definition with JSON Schema contracts for input and output, plus an execution binding (runtime + entrypoint).

**Core fields**:
- `name`, `description`
- `input_schema` (JSON Schema 2020-12)
- `output_schema` (optional)
- `implementation` (runtime + entrypoint + handler)

**Sources**: [R4], [R5], [R7]

### Host

**Definition**: The execution environment that discovers skills and/or tools and mediates how they are loaded, selected, and executed (e.g., Claude API, Claude Code, an MCP client, an OpenAI Responses-based app).

**Sources**: [R11], [R2], [R3], [R4], [R6], [R12]

### Adapter (Three-Layer Model)

**Definition**: A host-side component that maps the Universal skill package into a host’s native representation (tools, catalogs, runtime wrappers) without changing the skill itself.

**Layers**:
1. **Specification**: `SKILL.md` + directory layout (vendor-neutral)
2. **Adapter**: host-specific mapping and enforcement
3. **Implementation**: executable code and resources

**Sources**: [R11], [R4]

### Progressive Disclosure

**Definition**: A loading strategy where hosts ingest **metadata first**, then load the body/resources only when a skill is relevant.

**Sources**: [R11], [R12]

### Compatibility Level

**Definition**: A coarse classification of how completely a host supports this spec.

**Levels**:
- **L0 (Adapter-only)**: Host has no native skill support; an adapter must load `SKILL.md` and register tools.
- **L1 (Metadata)**: Host can discover `name`/`description` but does not execute tools.
- **L2 (Progressive)**: Host supports progressive disclosure (metadata first, instructions/resources on-demand).
- **L3 (Executable)**: Host can execute tool implementations (directly or via an adapter-defined runtime contract).

---

## Core Patterns

### Normative vs Informative (MUST)

- **Normative** statements use uppercase requirement keywords and define what a compliant skill package/adapter MUST do.
- **Host Profiles** provide host facts; they are informative for the Universal spec but binding when targeting that host.

---

### Normative Specification

#### 1) Skill Package Layout (MUST)

A skill package MUST be a directory with this minimum shape:

```text
<skill_dir>/
└── SKILL.md
```

Recommended (OPTIONAL) structure:

```text
<skill_dir>/
├── SKILL.md
├── scripts/                  # Optional executable implementations
├── references/               # Optional documentation (progressive disclosure)
├── assets/                   # Optional templates/resources
├── tools.json                # Optional derived artifact (see Tool Source Priority)
├── tests/                    # Optional tests
└── README.md                 # Optional human-oriented overview
```

Path rules:
- All paths referenced by the skill MUST be **relative to `<skill_dir>`**.
- Skills MUST NOT require absolute paths.

#### 2) `SKILL.md` Format (MUST)

- `SKILL.md` MUST begin with YAML frontmatter delimited by `---`.
- Frontmatter MUST be valid YAML and parse into a single mapping/object.
- The Markdown body MUST be treated as model-facing instructions and MUST NOT rely on host-specific implementation details unless placed under `host_overrides`.

#### 3) `SKILL.md` Frontmatter (MUST)

The frontmatter MUST include these fields (Agent Skills standard): [R11]

- `name` (string): skill identifier; MUST match the parent directory name.
- `description` (string): description of what the skill does and when to use it.

The frontmatter MAY include these optional standard fields: [R11]

- `license` (string): license name or reference to a bundled license file.
- `compatibility` (string): environment requirements (intended product, system packages, network access, etc.), 1–500 characters if provided.
- `metadata` (object): arbitrary key-value mapping (string values recommended) for additional metadata (e.g., `short-description`, `author`, `version`). [R11], [R12]
- `allowed-tools` (string): space-delimited list of pre-approved tools the skill may use (experimental; support may vary).

#### `name` (MUST)
The `name` field MUST follow the Agent Skills specification: [R11]
- MUST be 1–64 characters
- MUST contain only **Unicode lowercase alphanumeric characters** and hyphens
- MUST NOT start or end with `-`
- MUST NOT contain consecutive hyphens (`--`)
- MUST match the parent directory name

#### Portable Subset (SHOULD)
For maximum portability across hosts, filesystems, and CI tooling, skills SHOULD restrict `name` to:
- ASCII only: `[a-z0-9-]`
- Avoid non-ASCII letters even if allowed by the spec

`description` MUST be 1–1024 characters and SHOULD include both what the skill does and when to use it (with keywords that help matching).

Host notes:
- Claude API additionally forbids XML tags and reserved words in `name`/`description`. [R2]
- Codex loads `name`/`description` at startup and can activate skills explicitly (`/skills` or by typing `$` to mention a skill) or implicitly when the task matches the description. [R12]

Extensions (OPTIONAL; SSOT-oriented):
- Fields beyond the Agent Skills standard MAY be ignored or rejected by some clients; for maximum compatibility, store extra simple metadata under `metadata`. [R11]
- Common SSOT extensions include:
  - `spec_version`: this document’s schema version (e.g., `"2.1"`).
  - `version`: a skill package version (semantic versioning). [R8]
  - `tags`, `when_to_use`, `tools`, `permissions`, `safety`, `secrets`, `depends_on`, `provenance`, `host_overrides`, `evaluation`, `extensions`.

Reserved host identifiers (RECOMMENDED):
- `claude-api`
- `claude-code`
- `mcp`
- `openai-responses`
- `codex-cli`

#### 4) Tool Definition (OPTIONAL; Normative if present)

If a skill declares tools, it MUST declare them under `tools` in `SKILL.md` frontmatter.

Canonical tool fields:

```yaml
tools:
  - name: extract-text
    description: Extract text from a PDF file.
    input_schema:
      type: object
      additionalProperties: false
      properties:
        path: { type: string }
      required: [path]
    output_schema:
      type: object
      additionalProperties: false
      properties:
        text: { type: string }
        page_count: { type: integer, minimum: 0 }
      required: [text, page_count]
    implementation:
      runtime: python
      entrypoint: scripts/pdf.py
      handler: extract_text
```

Tool naming constraints (portability baseline):
- `tools[].name` MUST be 1–64 characters, lowercase alphanumeric + hyphens, MUST NOT start or end with `-`, and MUST NOT contain consecutive hyphens (`--`). [R11]

##### Tool Handler Signature (RECOMMENDED)

Adapters SHOULD standardize handlers to:

```text
handler(args: object, ctx: RunContext) -> object
```

Where:
- `args` is already validated against `input_schema` by the adapter.
- `ctx` is host-provided and may include paths, logging, and a host-mediated tool invocation interface.

#### 5) Runtimes and Entrypoints (MUST)

`implementation.runtime` MUST be one of:
- `python`
- `node`
- `bash`

Entrypoint rules:
- For `runtime: python`, `entrypoint` MUST end in `.py`.
- For `runtime: node`, `entrypoint` MUST end in `.js` or `.mjs` (do not point at `.ts` unless the host explicitly provides a TS runner).
- For `runtime: bash`, `entrypoint` MUST end in `.sh` and the script MUST read JSON from stdin and write JSON to stdout (adapter responsibility to enforce).

Dependencies:
- Skills MAY declare `implementation.dependencies`, but hosts MAY ignore it.
- If a host installs dependencies, it MUST do so in a way that does not weaken sandboxing or violate approvals.
- If declared, dependencies SHOULD use these keys:
  - `pip`: Python packages (optionally pinned)
  - `npm`: Node packages (optionally pinned)
  - `system`: OS-level packages/tools
  - `notes`: human-readable caveats

Example:

```yaml
implementation:
  runtime: python
  entrypoint: scripts/pdf.py
  handler: extract_text
  dependencies:
    pip: ["pdfplumber==0.11.4"]
    system: ["poppler-utils"]
    notes: "Hosts without package installation must vendor dependencies."
```

#### 6) Tool Source Priority (MUST)

When multiple tool-definition sources exist, adapters MUST resolve in this order:

1. `SKILL.md` frontmatter `tools` (canonical)
2. `tools.json` (optional derived artifact, used for interop/caching)
3. Host-provided tool catalogs (e.g., MCP `tools/list`) which are not part of the skill package

If `tools.json` exists and disagrees with `SKILL.md`, the adapter MUST treat it as stale and prefer `SKILL.md`.

##### `tools.json` Format (OPTIONAL; Normative if present)

If `tools.json` is present at the skill root, it MUST be a JSON array whose items are the same canonical tool objects as `SKILL.md` frontmatter `tools`.

Guidance:
- `tools.json` SHOULD be treated as a generated/interop artifact (cache), not author-written SSOT.
- Adapters SHOULD be able to regenerate `tools.json` from `SKILL.md` deterministically.
- When exposing tools through MCP, adapters MUST map `input_schema` → `inputSchema` (and MAY emit host-specific JSON with camelCase fields) without changing the canonical definition.

#### 7) JSON Schema Requirements (MUST)

Tool schemas (`input_schema`, `output_schema`) MUST be valid JSON Schema using the 2020-12 vocabulary. [R7]

Minimum portability rules:
- `input_schema` MUST be `type: object`.
- Each object schema SHOULD set `additionalProperties: false` for predictable validation.

##### OpenAI Strict-Compatible Schema Profile (Normative)

If a host maps a tool to OpenAI tool calling or structured outputs with `strict: true`, then each object schema in `input_schema` MUST satisfy:
- `additionalProperties: false` [R5]

Additionally, to ensure deterministic key presence across strict validators, adapters SHOULD:
- list all keys in `required` and use nullable unions (e.g., `type: ["string", "null"]`) to represent optionality.

#### 8) Permissions & Safety (MUST)

Skills MUST be authored with least privilege in mind, and adapters MUST enforce a **default-deny** posture.

Canonical permission structure:

```yaml
permissions:
  filesystem:
    read: ["**/*.pdf"]
    write: ["output/**"]
  network:
    outbound: []        # empty = no network
  processes:
    allow_subprocess: false
```

Glob semantics (MUST):
- Patterns are matched against **normalized, root-relative paths** using `/` as the separator.
- `*` matches within a single path segment; `**` matches across segments.
- Hosts MUST normalize Windows `\\` to `/` before matching.
- This spec does not use negation globs (no leading `!`).

Safety structure (MUST, minimum):

```yaml
safety:
  require_confirmation_for:
    - destructive_writes
    - external_network
  redact:
    secrets: true
    pii: true
```

##### Pattern: Permissions x Roots (Intersection)

**Principle**:
- Skill `permissions` express **intent** (least privilege requested).
- MCP `roots` express **enforced boundaries** (what the runtime actually allows). [R4]
- The adapter/host MUST apply the **intersection** as effective permissions.

**Rule**:
- If a requested permission is outside the MCP roots, the adapter MUST deny it.
- If MCP roots are broader than requested permissions, the adapter MUST still constrain to the skill’s declared permissions (least privilege).

Per-tool confirmation (OPTIONAL, recommended for high-risk tools):

```yaml
tools:
  - name: delete-output
    description: Delete generated output files.
    confirmation:
      level: destructive_writes
      prompt: "This will delete files under output/**."
    input_schema:
      type: object
      additionalProperties: false
      properties:
        dry_run: { type: boolean }
      required: [dry_run]
    implementation:
      runtime: bash
      entrypoint: scripts/delete_output.sh
```

Secrets (RECOMMENDED):

```yaml
secrets:
  required:
    - name: OCR_SERVICE_API_KEY
      usage: env
      description: API key for OCR provider
```

Secrets handling rules:
- Hosts MUST treat secrets as sensitive and MUST redact them from logs and tool outputs by default.
- Secrets SHOULD be inherited only by the tool runtime process tree that needs them.

Provenance (RECOMMENDED):

```yaml
provenance:
  source_repo: "https://github.com/<org>/<repo>"
  source_commit: "<git sha>"
  reviewed_by: ["<reviewer>"]
  signature: "<optional signature>"
```

Supply-chain guidance:
- Hosts SHOULD require review/auditing for skills from untrusted sources.
- Adapters SHOULD surface provenance metadata in catalogs and logs (redacting secrets).

#### 9) Runtime Result Protocol (MUST)

Adapters MUST provide a consistent interpretation of tool results across runtimes:

- **Success**: a JSON object that matches `output_schema`
- **Error**: a structured error object (adapter may map exceptions into this form)
- **Async** (optional): a structured “task handle” that can be mapped to MCP Tasks or host-specific job control

Canonical error envelope (RECOMMENDED):

```json
{
  "status": "error",
  "error": {
    "code": "INVALID_ARGUMENT",
    "message": "path must end with .pdf",
    "retriable": false
  }
}
```

Canonical async envelope (RECOMMENDED):

```json
{
  "status": "async",
  "task": {
    "id": "task_123",
    "status": "running"
  }
}
```

Cancellation:
- Adapters MUST translate the host’s cancellation mechanism into an execution stop signal and SHOULD allow tools to perform cleanup.

#### 10) Selection & Progressive Disclosure (MUST)

Frontmatter MAY include deterministic triggers:

```yaml
when_to_use:
  mentions: ["pdf", "ocr", "scan"]
  file_types: [".pdf"]
  intents: ["document_extraction"]
```

Selection algorithm (Normative, deterministic baseline):

```text
1. If the user explicitly names a skill/tool, select it (manual override).
2. Score each skill by trigger matches:
   - +3 per file_type match
   - +2 per mention match (case-insensitive)
   - +1 per intent match (host-derived)
3. Select all skills with score >= threshold (default threshold = 3).
4. Tie-breaker order:
   - higher score
   - higher `when_to_use.priority` if present
   - lexical order by `name` (stable)
```

Progressive disclosure rules:
- Hosts MUST load `name` and `description` for discovery.
- Hosts SHOULD load the body only when a skill is selected/triggered.
- Authors SHOULD keep frontmatter concise and move details into the body or referenced files.

---

### Host Adapter Model (Informative)

Adapters are responsible for:
- Parsing `SKILL.md` frontmatter
- Enforcing schema, permissions, and safety gates
- Mapping tools into the host’s tool system (Claude tools, OpenAI tools, MCP tools)
- Bridging async/cancellation semantics

Mapping table (tools):

| Universal | Claude API Skills | MCP | OpenAI tool calling / Structured Outputs |
|---|---|---|---|
| `tool.name` | tool name | `tool.name` | function/tool name |
| `tool.description` | tool description | `tool.description` | description |
| `tool.input_schema` | host-mapped schema | `tool.inputSchema` | JSON Schema (`parameters` / `json_schema`) |
| `tool.output_schema` | host-mapped schema (optional) | (optional) `outputSchema` | Structured outputs schema (optional) |

**Sources**: [R2], [R4], [R5]

---

### Host Profiles (Facts + Guidance)

#### Host Profile: Claude API (Developer Platform)

**Facts** (from the official Skills guide):
- Claude’s Skills overview defines the conceptual model and usage boundaries. [R1]
- Skills are specified via a `container` parameter and `container.skills` in Messages requests. [R2]
- Skills require beta headers, including `code-execution-2025-08-25` and `skills-2025-10-02`. [R2]
- Maximum Skills per request: **8**. [R2]
- Maximum Skill upload size: **8MB** (all files combined). [R2]
- Custom Skills are versioned; guides describe auto-generated epoch-style versions and using `"latest"` for the most recent version. [R2]
- YAML frontmatter constraints include:
  - `name`: max 64, lowercase letters/numbers/hyphens only, no XML tags, no reserved words. [R2]
  - `description`: max 1024, non-empty, no XML tags. [R2]
- When skills are specified in a container:
  - Claude sees Skill metadata (`name`, `description`) in the system prompt. [R2]
  - Skill files are copied into the container at `/skills/{directory}/`. [R2]
- Code execution container constraints include:
  - No network access
  - No runtime package installation
  - Fresh container per request [R2]
- Long-running operations may return `stop_reason: "pause_turn"`; you can send the response back in a subsequent request to continue. [R2]
- Downloading generated files uses the Files API with a beta header (e.g., `files-api-2025-04-14`). [R2]

**Implications for this Universal spec**:
- The Universal portability baseline for `name`/`description` is aligned to Claude API limits.
- Declared `network` permissions SHOULD be empty when targeting Claude API.
- Dependency installation SHOULD be avoided; vendor dependencies into the skill package or rely on host preinstalls.

#### Host Profile: Claude Code

**Facts**:
- Claude Code supports skills stored under `.claude/skills/` (project) and `~/.claude/skills/` (user). [R3]

**Implications**:
- Skills intended for Claude Code SHOULD be distributable as folders committed under `.claude/skills/`.

#### Host Profile: MCP (Model Context Protocol)

**Facts**:
- MCP defines a tool discovery/execution protocol; tool schemas are exposed via `tools/list` using `inputSchema`. [R4]
- Newer MCP specs define task-like abstractions (optional) that can be used to represent async operations. [R4]

**Implications**:
- Skills and MCP are complementary:
  - **Skills** package procedures + local code/resources.
  - **MCP** connects a host to external tool servers.
- Adapters SHOULD map `input_schema` → `inputSchema` when exposing skill tools through MCP.

#### Host Profile: OpenAI Structured Outputs / Tool Calling

**Facts**:
- Structured Outputs can be enabled with `strict: true` alongside function definitions or a response format. [R5]

**Implications**:
- To maximize strict compatibility, keep schemas conservative and explicitly deny unknown fields (`additionalProperties: false`).

#### Host Profile: OpenAI Codex CLI

**Facts**:
- Codex skills build on the open Agent Skills standard (`SKILL.md` + YAML frontmatter + Markdown instructions). [R11], [R12]
- Skills are available in the Codex CLI and IDE extensions. [R12]
- Codex discovers skills from multiple scopes; higher-precedence scopes overwrite lower-precedence skills with the same `name`: [R12]
  - `CWD`: `./.codex/skills` (highest; per-working-dir overrides)
  - `PARENT`: a folder above CWD within a git repo (shared-area skills)
  - `REPO`: `$REPO_ROOT/.codex/skills`
  - `USER`: `$CODEX_HOME/skills` (default: `~/.codex/skills`)
- Codex loads each skill’s `name` and `description` at startup and activates skills explicitly (`/skills` or `$` skill mentions) or implicitly when the task matches the description. [R12]
- Codex web and iOS do not support explicit invocation yet (repo skills can still be used via prompting). [R12]
- Codex CLI configuration is located at `~/.codex/config.toml` and includes an approval/policy model to gate risky commands. [R6]
- Codex is available as both a local CLI and a hosted cloud surface; filesystem and sandbox assumptions differ between them. [R9], [R10]

**Implications**:
- Put repo-wide canonical skills in `REPO` and use `CWD` overrides only for narrow, subfolder-specific deltas. [R12]
- Keep `name` stable and directory-matched; keep `description` keyword-rich for activation. Consider `metadata.short-description` for user-facing summaries. [R11], [R12]
- Assume risky operations may be gated by approvals/execpolicy; design scripts/tools to support dry-runs and explicit user confirmation.

---

## Decision Checklist

### Universal MUST Checklist

- [ ] `SKILL.md` exists at the skill root and begins with YAML frontmatter.
- [ ] Frontmatter includes `name` and `description` (Agent Skills standard). [R11]
- [ ] `name` matches the skill directory name and follows the Unicode `name` rules (1–64 chars, lowercase alphanumeric + hyphens, no leading/trailing `-`, no `--`). [R11]
- [ ] **Portable subset (SHOULD)**: `name` sticks to ASCII `[a-z0-9-]` for maximum portability.
- [ ] If `tools` are present, `tools[].name` follows the same portability baseline. [R11]
- [ ] Tool schemas are valid JSON Schema (2020-12) and `input_schema.type` is `object`. [R7]
- [ ] Each object schema sets `additionalProperties: false` when targeting strict schema enforcement. [R5]
- [ ] Permissions are least-privilege and default-deny; network is explicitly empty when required.
- [ ] `safety` exists with redaction + confirmation gates for destructive actions.
- [ ] Any host-specific behavior is isolated under `host_overrides` (no vendor logic in core fields).

### Host Profile Checks

- [ ] **Claude API**: Skill upload ≤8MB; ≤8 skills per request; no network; no package install. [R2]
- [ ] **Claude Code**: Skill folder is placed under `.claude/skills/` or `~/.claude/skills/`. [R3]
- [ ] **MCP**: Tool schema mapping uses `inputSchema` and preserves names/descriptions. [R4]
- [ ] **OpenAI strict**: Schemas are conservative and deny unknown fields (`additionalProperties: false`). [R5]
- [ ] **Codex CLI**: skills are discovered by scope precedence; avoid accidental name collisions unless overriding intentionally; risky operations are gated by approvals/execpolicy. [R12], [R6]

### Host Facts Update Protocol (MUST)

Any host-specific facts that can drift (limits, defaults, paths) MUST include:
- Primary source URL
- Short summary of the claim
- `(retrieved YYYY-MM-DD)` timestamp

Repositories SHOULD enforce this via CI:
- Link checking
- Reference linting (R# must be defined/used; retrieved/accessed required)

**Rule**: If a fact cannot be verified, treat it as a spec gap and update this doc’s HOST REALITY accordingly.

---

## Anti-patterns / Pitfalls

### Anti-pattern: Broken or Ambiguous Examples

**Symptom**: Code fences are malformed, examples reference undefined structures, or “almost runnable” snippets teach incorrect implementations.

**Impact**: Agents learn the wrong contract; downstream adapters drift or fail at runtime.

**Fix**: Examples must be either:
- runnable-minimal with explicit dependencies and runtime, or
- explicitly labeled as pseudocode with no implied executability

### Anti-pattern: Treating `tools.json` as the Source of Truth

**Symptom**: `tools.json` diverges from `SKILL.md` and becomes the de facto canonical spec.

**Impact**: Drift and duplication; SSOT breaks.

**Fix**: Keep `SKILL.md` frontmatter canonical; regenerate `tools.json` from it.

### Anti-pattern: `runtime: node` with a `.ts` Entrypoint

**Symptom**: Tool declares Node runtime but points at TypeScript source.

**Impact**: Many hosts cannot execute TS directly; tool fails.

**Fix**: Compile to `.js`/`.mjs` or use a host-provided TypeScript runner (host override).

### Anti-pattern: Overbroad Permissions

**Symptom**: `filesystem.read: ["**/*"]` or `network.outbound: ["*"]`.

**Impact**: Security review failure, higher blast radius, and user distrust.

**Fix**: Start from deny-all and grant narrowly scoped globs/hosts.

---

## Evaluation

### Metrics (Informative)

- **Activation precision/recall**: selection accuracy for the intended triggers.
- **Metadata footprint**: measure frontmatter size (bytes) and token estimate; prefer host-provided token counters, else use a conservative char-count fallback.
- **Permission violations**: attempted actions outside declared permissions.
- **Schema conformance**: percent of tool calls that pass input/output validation without retries.

### Skill Telemetry Contract (Minimum)

When a skill is executed (explicitly or implicitly), implementations MUST emit:
- `trace_id`
- `run_id`
- `skill_id` (stable identifier; e.g., `<org>/<skill-name>`)
- `skill_version` (semantic or date-based)
- `skill_source_commit` (if in git)
- `host_id` / `adapter_id` (if applicable)
- `approval_state` (`NOT_REQUIRED|PENDING|APPROVED|DENIED`)

**Alignment**: field names SHOULD match `docs/SSOT.md` “Cross-Document Telemetry Keys”.

### Validation (Recommended)

- Validate frontmatter against the embedded JSON Schema (Appendix A).
- For baseline Agent Skills validation, use the reference library: `skills-ref validate <skill_dir>`. [R11]
- If `tools.json` is present, validate it against the embedded JSON Schema (Appendix B).
- Validate tool schemas against JSON Schema 2020-12 (static) and host-specific subsets (Claude/OpenAI strict).
- Run smoke tests declared in `evaluation.smoke_tests` (if present).

---

## Practical Examples

### Example: Minimal Skill Package

```text
pdf-processing/
├── SKILL.md
└── scripts/
    └── pdf.py
```

### Example: `SKILL.md` (Minimal, Agent Skills Standard)

```markdown
---
name: pdf-processing
description: Extract text and tables from PDF files. Use when the user mentions PDFs, OCR, forms, or document extraction.
metadata:
  short-description: PDF extraction workflows
  version: "1.0.0"
license: Apache-2.0
---

# PDF Processing Skill

Use this skill when the user needs PDF extraction, OCR guidance, or form/document workflows.
```

### Example: `SKILL.md` (Extended, Tool-Backed; SSOT Extensions)

```markdown
---
name: pdf-processing
description: Extract text from PDFs; use when PDFs or OCR are mentioned.
metadata:
  ssot-spec-version: "2.1"
  version: "1.0.0"
when_to_use:
  mentions: ["pdf", "ocr", "scan"]
  file_types: [".pdf"]
permissions:
  filesystem:
    read: ["**/*.pdf"]
    write: ["output/**"]
  network:
    outbound: []
  processes:
    allow_subprocess: false
safety:
  require_confirmation_for: [destructive_writes]
  redact:
    secrets: true
    pii: true
tools:
  - name: extract-text
    description: Extract text from a PDF file.
    input_schema:
      type: object
      additionalProperties: false
      properties:
        path: { type: string }
      required: [path]
    output_schema:
      type: object
      additionalProperties: false
      properties:
        text: { type: string }
      required: [text]
    implementation:
      runtime: python
      entrypoint: scripts/pdf.py
      handler: extract_text
---

# PDF Processing Skill

Use `extract-text` to extract text. If extraction fails, explain why and suggest next steps.
```

### Appendix A: Frontmatter JSON Schema (Machine-Readable)

<!-- ssot-schema:json:UniversalSkillFrontmatter -->
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Skill Frontmatter (Agent Skills + SSOT Extensions)",
  "type": "object",
  "required": ["name", "description"],
  "additionalProperties": false,
  "properties": {
    "spec_version": { "type": "string", "pattern": "^2\\\\.[0-9]+$" },
    "name": { "type": "string", "minLength": 1, "maxLength": 64, "pattern": "^(?!.*--)[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$" },
    "description": { "type": "string", "minLength": 1, "maxLength": 1024 },
    "license": { "type": "string" },
    "compatibility": { "type": "string", "minLength": 1, "maxLength": 500 },
    "metadata": { "type": "object", "additionalProperties": { "type": "string" } },
    "allowed-tools": { "type": "string" },
    "version": { "type": "string", "pattern": "^(0|[1-9]\\\\d*)\\\\.(0|[1-9]\\\\d*)\\\\.(0|[1-9]\\\\d*)(?:-[0-9A-Za-z.-]+)?(?:\\\\+[0-9A-Za-z.-]+)?$" },
    "tags": { "type": "array", "items": { "type": "string" } },
    "when_to_use": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "mentions": { "type": "array", "items": { "type": "string" } },
        "file_types": { "type": "array", "items": { "type": "string" } },
        "intents": { "type": "array", "items": { "type": "string" } },
        "priority": { "type": "integer", "minimum": 0 }
      }
    },
    "permissions": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "filesystem": {
          "type": "object",
          "additionalProperties": false,
          "properties": {
            "read": { "type": "array", "items": { "type": "string" } },
            "write": { "type": "array", "items": { "type": "string" } }
          }
        },
        "network": {
          "type": "object",
          "additionalProperties": false,
          "properties": {
            "outbound": { "type": "array", "items": { "type": "string" } }
          }
        },
        "processes": {
          "type": "object",
          "additionalProperties": false,
          "properties": {
            "allow_subprocess": { "type": "boolean" }
          }
        }
      }
    },
    "safety": {
      "type": "object",
      "additionalProperties": true
    },
    "secrets": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "required": {
          "type": "array",
          "items": {
            "type": "object",
            "additionalProperties": false,
            "required": ["name", "usage"],
            "properties": {
              "name": { "type": "string" },
              "usage": { "type": "string", "enum": ["env"] },
              "description": { "type": "string" },
              "optional": { "type": "boolean" }
            }
          }
        }
      }
    },
    "tools": {
      "type": "array",
      "items": { "$ref": "#/$defs/tool" }
    },
    "host_overrides": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["host", "config"],
        "properties": {
          "host": { "type": "string" },
          "config": { "type": "object", "additionalProperties": true }
        }
      }
    },
    "evaluation": { "type": "object", "additionalProperties": true },
    "provenance": { "type": "object", "additionalProperties": true },
    "depends_on": { "type": "array", "items": { "type": "string" } },
    "extensions": { "type": "object", "additionalProperties": true }
  },
  "$defs": {
    "tool": {
      "type": "object",
      "additionalProperties": false,
      "required": ["name", "description", "input_schema", "implementation"],
      "properties": {
        "name": { "type": "string", "minLength": 1, "maxLength": 64, "pattern": "^(?!.*--)[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$" },
        "description": { "type": "string", "minLength": 1, "maxLength": 1024 },
        "input_schema": { "type": "object" },
        "output_schema": { "type": "object" },
        "confirmation": {
          "type": "object",
          "additionalProperties": false,
          "properties": {
            "level": { "type": "string", "enum": ["never", "always", "destructive_writes", "external_network"] },
            "prompt": { "type": "string" }
          }
        },
        "implementation": {
          "type": "object",
          "additionalProperties": false,
          "required": ["runtime", "entrypoint"],
          "properties": {
            "runtime": { "type": "string", "enum": ["python", "node", "bash"] },
            "entrypoint": { "type": "string" },
            "handler": { "type": "string" },
            "timeout_seconds": { "type": "integer", "minimum": 1 },
            "dependencies": {
              "type": "object",
              "additionalProperties": false,
              "properties": {
                "pip": { "type": "array", "items": { "type": "string" } },
                "npm": { "type": "array", "items": { "type": "string" } },
                "system": { "type": "array", "items": { "type": "string" } },
                "notes": { "type": "string" }
              }
            }
          }
        }
      }
    }
  }
}
```

### Appendix B: `tools.json` JSON Schema (Machine-Readable)

<!-- ssot-schema:json:UniversalToolsJson -->
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "tools.json (Universal Tool List)",
  "type": "array",
  "items": { "$ref": "#/$defs/tool" },
  "$defs": {
    "tool": {
      "type": "object",
      "additionalProperties": false,
      "required": ["name", "description", "input_schema", "implementation"],
      "properties": {
        "name": { "type": "string", "minLength": 1, "maxLength": 64, "pattern": "^(?!.*--)[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$" },
        "description": { "type": "string", "minLength": 1, "maxLength": 1024 },
        "input_schema": { "type": "object" },
        "output_schema": { "type": "object" },
        "confirmation": {
          "type": "object",
          "additionalProperties": false,
          "properties": {
            "level": { "type": "string", "enum": ["never", "always", "destructive_writes", "external_network"] },
            "prompt": { "type": "string" }
          }
        },
        "implementation": {
          "type": "object",
          "additionalProperties": false,
          "required": ["runtime", "entrypoint"],
          "properties": {
            "runtime": { "type": "string", "enum": ["python", "node", "bash"] },
            "entrypoint": { "type": "string" },
            "handler": { "type": "string" },
            "timeout_seconds": { "type": "integer", "minimum": 1 },
            "dependencies": {
              "type": "object",
              "additionalProperties": false,
              "properties": {
                "pip": { "type": "array", "items": { "type": "string" } },
                "npm": { "type": "array", "items": { "type": "string" } },
                "system": { "type": "array", "items": { "type": "string" } },
                "notes": { "type": "string" }
              }
            }
          }
        }
      }
    }
  }
}
```

---

## Update Log

- 2025-12-21T00:00:00Z docs(skill): Clarified Unicode vs portable `name` rules, refined Codex skill precedence, added permissions x roots pattern, and added telemetry + host-facts protocols. (Author: SpeSan)
- 2025-12-20T08:57:25Z docs(skill): Added agentskills.io and OpenAI Codex Skills as primary sources; aligned baseline frontmatter to the Agent Skills standard; updated Codex host profile, examples, and schema accordingly. (Author: SpeSan)
- 2025-12-17T14:02:59Z docs(skill): Rebranded to SpeSan and performed final content check. (Author: SpeSan)
- 2025-12-17T00:00:00Z docs(skill): Major rewrite for 2025 portability: add explicit Host Profiles (Claude API/Code, MCP, OpenAI strict, Codex CLI), fix broken examples by switching to runnable-minimal/pseudocode-only, define tool source priority, normalize runtime/entrypoint rules, add machine-readable frontmatter/tools.json schemas. (Author: SpeSan)
- 2025-12-09T00:00:00Z docs(skill): Updated specification to v2.0 (Unified Universal). Adopted `SKILL.md` as canonical manifest. Deprecated `skill.yaml` in favor of frontmatter + `tools.json`. (Author: SpeSan)
- 2025-11-24T00:00:00Z docs(skill): Fixed Update Log date inconsistencies. (Author: SpeSan)
- 2025-11-22T00:00:00Z docs(skill): Refined specification based on multi-agent review. Added schema, secrets, runtime protocol, and composition guidance. (Author: SpeSan)
- 2025-11-19T00:00:00Z docs(skill): Added adapter model examples and testing guidance. (Author: SpeSan)
- 2025-11-13T00:00:00Z docs(skill): Initial specification created. (Author: SpeSan)

---

## See Also

### Related Topics (in-repo)
- [SSOT.md](./SSOT.md) – Governance and normative keyword semantics
- [EXEC_PLAN.md](./EXEC_PLAN.md) – Planning methodology for long-running agent work
- [CODE_MCP.md](./CODE_MCP.md) – Running code through MCP with strong isolation patterns

### External References
- Agent Skills (official; specification): https://agentskills.io/ (spec: https://agentskills.io/specification)
- OpenAI Codex Agent Skills: https://developers.openai.com/codex/skills/
- Agent Skills reference library (`skills-ref`): https://github.com/agentskills/agentskills/tree/main/skills-ref
- Claude Skills overview: https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview
- Claude API Skills guide: https://platform.claude.com/docs/en/build-with-claude/skills-guide
- Claude Code Skills: https://code.claude.com/docs/en/skills
- MCP specification: https://modelcontextprotocol.io/specification/2025-11-25
- OpenAI Structured Outputs cookbook: https://cookbook.openai.com/examples/structured_outputs_intro
- OpenAI Codex local config: https://developers.openai.com/codex/local-config/
- OpenAI Codex CLI: https://developers.openai.com/codex/cli/
- OpenAI Codex Cloud: https://developers.openai.com/codex/cloud/

---

## References

### Normative / Primary Sources
- [R11] Agent Skills. "Specification." https://agentskills.io/specification (retrieved 2025-12-20; site: https://agentskills.io/)
- [R12] OpenAI. "Agent Skills (Codex)." https://developers.openai.com/codex/skills/ (retrieved 2025-12-20)
- [R1] Anthropic. "Agent Skills Overview." https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview (retrieved 2025-12-17)
- [R2] Anthropic. "Use Skills with the Claude API." https://platform.claude.com/docs/en/build-with-claude/skills-guide (retrieved 2025-12-17)
- [R3] Anthropic. "Use Skills in Claude Code." https://code.claude.com/docs/en/skills (retrieved 2025-12-17)
- [R4] Model Context Protocol. "Specification (2025-11-25)." https://modelcontextprotocol.io/specification/2025-11-25 (retrieved 2025-12-17)
- [R5] OpenAI. "Structured Outputs Intro (Cookbook)." https://cookbook.openai.com/examples/structured_outputs_intro (retrieved 2025-12-17)
- [R6] OpenAI. "Codex Local Configuration (`config.toml`)." https://developers.openai.com/codex/local-config/ (retrieved 2025-12-17)
- [R7] JSON Schema. "Draft 2020-12." https://json-schema.org/draft/2020-12/json-schema-core.html (retrieved 2025-12-17)
- [R9] OpenAI. "Codex CLI." https://developers.openai.com/codex/cli/ (retrieved 2025-12-17)
- [R10] OpenAI. "Codex Cloud." https://developers.openai.com/codex/cloud/ (retrieved 2025-12-17)

### Informative References
- [R8] Semantic Versioning. https://semver.org/ (retrieved 2025-12-17)

---

**Document ID**: `docs/AGENT_SKILL.md`
**Canonical URL**: `https://github.com/spesans/dev-ssot/blob/main/docs/AGENT_SKILL.md`
**License**: MIT
