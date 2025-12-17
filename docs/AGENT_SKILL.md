---
title: Universal Agent Skill
slug: agent-skill
summary: "Skill spec overview"
type: spec
tags: [topic, ai-first, agent, skill, specification]
last_updated: 2025-12-17
---

# Topic: Universal Agent Skill — Universal Specification

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

- **WHAT**: A **Skill** is a folder with a required `SKILL.md` (YAML frontmatter + Markdown body) plus optional tools, scripts, templates, and tests.
- **WHY**: Skills encode reusable procedures and tool contracts with **progressive disclosure** (metadata first, detail on-demand) to improve reliability and reduce context overhead.
- **HOW (Canonical)**:
  - **Source of truth** is `SKILL.md` frontmatter (including `tools`)
  - **Tool contracts** use **JSON Schema 2020-12**
  - **`tools.json` is optional** and treated as a derived/interop artifact
- **HOST REALITY**:
  - **Claude API Skills** are attached via `container.skills` and have hard limits (e.g., max 8 skills/request, 8MB upload) [R2]
  - **OpenAI Structured Outputs** and tool calling can enforce schemas with `strict: true` [R5]
  - **MCP** is a tool connectivity protocol (not a skill format) and maps via a stable schema translation (`input_schema` → `inputSchema`) [R4]
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
  - Optional implementations under `scripts/` and optional supporting files (`templates/`, `tests/`, etc.)
- **Excludes**:
  - Host-locked configuration that cannot be expressed as `host_overrides`

**Sources**: [R1], [R2]

### Skill Manifest (`SKILL.md`)

**Definition**: The single source of truth file inside a skill package.

**Rules**:
- MUST be located at the skill root: `/<skill_dir>/SKILL.md`
- MUST begin with YAML frontmatter delimited by `---`
- MUST contain a Markdown body that can be injected/loaded on demand by the host

**Sources**: [R1], [R2], [R3]

### Universal Skill Frontmatter

**Definition**: The YAML frontmatter object at the top of `SKILL.md`, validated against a versioned schema (`spec_version`).

**Why it matters**:
- Hosts discover skills primarily through metadata (`name`, `description`) [R2]
- Tool contracts and safety/permissions must be machine-validated to prevent drift

**Sources**: [R2]

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

**Sources**: [R1], [R2], [R3], [R4], [R6]

### Adapter (Three-Layer Model)

**Definition**: A host-side component that maps the Universal skill package into a host’s native representation (tools, catalogs, runtime wrappers) without changing the skill itself.

**Layers**:
1. **Specification**: `SKILL.md` + directory layout (vendor-neutral)
2. **Adapter**: host-specific mapping and enforcement
3. **Implementation**: executable code and resources

**Sources**: [R1], [R4]

### Progressive Disclosure

**Definition**: A loading strategy where hosts ingest **metadata first**, then load the body/resources only when a skill is relevant.

**Sources**: [R1], [R2]

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
├── tools.json                # Optional derived artifact (see Tool Source Priority)
├── scripts/                  # Optional executable implementations
├── templates/                # Optional templates/resources
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

#### 3) Universal Skill Frontmatter Schema (MUST)

The frontmatter MUST include these fields:

- `spec_version` (string): Universal spec version for the frontmatter schema (e.g., `"2.1"`).
- `name` (string): skill identifier.
- `description` (string): human/model-readable description including “when to use”.
- `version` (string): skill package version (semantic versioning).

To maximize portability, `name` and `description` MUST satisfy the Claude API constraints:
- `name` MUST be 1–64 characters and match `^[a-z0-9-]+$` and MUST NOT include XML tags or host-reserved words. [R2]
- `description` MUST be non-empty, ≤1024 characters, and MUST NOT include XML tags. [R2]

Additional recommended fields (OPTIONAL but strongly recommended for governance):
- `tags`: string array for cataloging/search
- `when_to_use`: trigger metadata for deterministic selection
- `tools`: tool definitions (canonical)
- `permissions`: least-privilege declaration
- `safety`: PII/redaction/confirmation constraints
- `secrets`: required env vars (declarative)
- `depends_on`: declared skill/tool dependencies (host-mediated composition)
- `provenance`: supply-chain metadata (repo/commit/review)
- `host_overrides`: host-specific overlay configuration
- `evaluation`: smoke tests, fixtures, metrics hints
- `extensions`: free-form extension map (`x_*` or custom blocks)

Reserved host identifiers (RECOMMENDED):
- `claude-api`
- `claude-code`
- `mcp`
- `openai-responses`
- `codex-cli`

#### 4) Tool Definition (MUST)

Tools MUST be declared under `tools` in `SKILL.md` frontmatter.

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
- `tools[].name` MUST satisfy the same constraints as `name` (1–64 chars, `^[a-z0-9-]+$`). [R2]

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
- Codex CLI configuration is located at `~/.codex/config.toml`. [R6]
- Codex CLI provides an approval/policy model (e.g., execpolicy rules) to gate risky commands. [R6]
- Codex is available as both a local CLI and a hosted cloud surface; filesystem and sandbox assumptions differ between them. [R9], [R10]

**Implications**:
- Treat Codex CLI as a host that can run adapters and connect to MCP; do not assume native Skill discovery unless explicitly supported by the current Codex version.

---

## Decision Checklist

### Universal MUST Checklist

- [ ] `SKILL.md` exists at the skill root and begins with YAML frontmatter.
- [ ] Frontmatter includes `spec_version`, `name`, `description`, `version`.
- [ ] `name`/`tools[].name` follow portability baseline (`^[a-z0-9-]+$`, ≤64 chars). [R2]
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
- [ ] **Codex CLI**: risky operations are gated by approvals/execpolicy. [R6]

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

### Validation (Recommended)

- Validate frontmatter against the embedded JSON Schema (Appendix A).
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

### Example: `SKILL.md` (Minimal, Portable)

```markdown
---
spec_version: "2.1"
name: pdf-processing
description: Extract text from PDFs; use when PDFs or OCR are mentioned.
version: 1.0.0
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
  "title": "Universal Skill Frontmatter (spec_version 2.1)",
  "type": "object",
  "required": ["spec_version", "name", "description", "version"],
  "additionalProperties": false,
  "properties": {
    "spec_version": { "type": "string", "pattern": "^2\\\\.[0-9]+$" },
    "name": { "type": "string", "minLength": 1, "maxLength": 64, "pattern": "^[a-z0-9-]+$" },
    "description": { "type": "string", "minLength": 1, "maxLength": 1024 },
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
        "name": { "type": "string", "minLength": 1, "maxLength": 64, "pattern": "^[a-z0-9-]+$" },
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
        "name": { "type": "string", "minLength": 1, "maxLength": 64, "pattern": "^[a-z0-9-]+$" },
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

- 2025-12-17 docs(skill): Rebranded to SpeSan and performed final content check. (Author: SpeSan)
- 2025-12-17T00:00:00Z docs(skill): Major rewrite for 2025 portability: add explicit Host Profiles (Claude API/Code, MCP, OpenAI strict, Codex CLI), fix broken examples by switching to runnable-minimal/pseudocode-only, define tool source priority, normalize runtime/entrypoint rules, add machine-readable frontmatter/tools.json schemas. (Author: SSOT Admin)
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
**Canonical URL**: `https://github.com/artificial-intelligence-first/ssot/blob/main/docs/AGENT_SKILL.md`
**License**: MIT
