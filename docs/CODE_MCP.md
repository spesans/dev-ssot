---
title: Code MCP
slug: code-mcp
summary: "Code MCP guide"
type: reference
tags: [topic, ai-first, agent, mcp, code, optimization]
last_updated: 2025-12-21
---

# Code MCP

> Model-Agnostic Code Execution for MCP Integrations

## Agent Contract

- **PURPOSE**:
  - Define a vendor-neutral implementation guide for Code MCP: wrapping MCP tools as typed code APIs and invoking them via sandboxed code execution
  - Establish a **Runtime Contract** that removes ambiguity around imports, outputs, schemas, and error handling for AI-generated code
  - Reduce context and token usage via **progressive disclosure** while improving security, privacy, and reproducibility
- **USE_WHEN**:
  - You have many tools and tool definitions crowd out task context (typical signals: **≥10 tools** per session, or **tool definitions >10k tokens** in aggregate)
  - Tool outputs are large and should be filtered/aggregated in a sandbox before returning to the model
  - You can enforce OS-level isolation and maintain auditable execution and approval gates for high-risk actions
- **DO_NOT_USE_WHEN**:
  - A small, stable tool set fits comfortably in context and direct tool invocation is simpler
  - You cannot provide OS-level isolation, resource limits, and audited tool access (security and compliance risk)
  - You have strict end-to-end latency budgets that cannot accommodate sandbox overhead
- **PRIORITY**:
  - Security and user consent **override** cost optimization; Code MCP MUST NOT weaken isolation to reduce latency
  - **Brokered tool access** (sandbox with no external egress) SHOULD be the default topology for untrusted code execution
  - Progressive disclosure SHOULD be enabled whenever tool definitions materially reduce task context quality
- **RELATED_TOPICS**:
  - mcp-protocol
  - sandbox-execution
  - progressive-disclosure
  - token-optimization
  - agent-skill

In this repository, recommended agents for applying this specification (such as `repo-orchestrator` and `doc-maintainer`) are defined in `AGENTS.md`.

---

## TL;DR

- **WHAT**: Run model-generated code in an isolated sandbox that calls MCP tools through generated **Code Wrappers** (typed APIs) instead of direct model-to-tool calls.
- **WHY**: Keep tool schemas and intermediate data out of model context (often large token savings) while enforcing stronger isolation and auditable execution.
- **WHEN**: Use when tools/definitions are large, tool outputs are large, or tool selection accuracy suffers due to tool overload.
- **HOW**: Implement (1) wrapper/codegen from MCP `tools/list`, (2) a sandbox runner with a strict runtime contract, (3) progressive disclosure via a tool catalog, and (4) a policy-enforcing tool broker (recommended).
- **WATCH_OUT**: Do not mount `docker.sock`, do not rely on language-level sandboxes for security, do not leak credentials into the sandbox, and do not mix logs with machine-readable outputs.

### Direct Tool Invocation vs Code MCP

| Aspect | Direct tool invocation | Code MCP |
|---|---|---|
| Tool definitions in context | Usually upfront | On-demand (progressive disclosure) |
| Large outputs | Often returned to model | Filter/aggregate in sandbox |
| Security boundary | Model → tool | Model → code → sandbox → broker → tool |
| Operational complexity | Low | Higher (runner, codegen, audit, broker) |
| Best for | Few tools, small outputs | Many tools, large outputs, cost-sensitive deployments |

---

## Canonical Definitions

> **NOTE**: Requirement keywords (MUST/SHOULD/MAY) follow RFC2119/BCP14 semantics as used throughout MCP. [R2]

### Code MCP

**Definition**: An architectural pattern where MCP tools are wrapped as typed code APIs (Code Wrappers) and invoked through AI-generated code executed in a secure sandbox, rather than through direct model-to-tool invocation.

**Scope**:
- **Includes**:
  - Tool wrappers generated from MCP `tools/list` definitions
  - Sandbox runner with strict runtime contract (imports, output, limits, errors)
  - Progressive disclosure of tool definitions (catalog + on-demand schema loading)
  - In-sandbox filtering/aggregation to keep large intermediate data out of model context
- **Excludes**:
  - Running untrusted AI-generated code on the host
  - Relying on language-level sandboxes as the primary security boundary
  - Treating generated wrappers as the canonical source of tool truth

**Example**:

```typescript
// Model generates code that calls wrappers. The sandbox executes it.
import * as gdrive from "./servers/google_drive/index.js";

async function main() {
  const doc = await gdrive.getDocument({ documentId: "abc123" });
  const summary = summarize(doc.structuredContent ?? doc.content);

  // Runner collects `result` and returns a single JSON response to the host.
  (globalThis as any).result = { summary };
}

await main();
```

**Sources**: [R1], [R3]

### Code Wrapper

**Definition**: A thin, typed function that maps a single MCP tool to a language-native API, forwarding calls to an MCP client/broker and returning MCP Tool Results in a consistent shape.

**Scope**:
- **Includes**:
  - A stable mapping to MCP tool `name` and JSON Schema (`inputSchema`, optional `outputSchema`)
  - Type hints and/or runtime validation for inputs and structured outputs
  - Standardized error and result normalization rules
- **Excludes**:
  - Business logic, aggregation, or summarization (belongs in skills/workflows)
  - Credential acquisition and OAuth flows (belongs in host/broker)

**Example**:

```python
# servers/google_drive/get_document.py (generated)
from typing import Any, TypedDict
from client.mcp_client import call_tool

class GetDocumentInput(TypedDict):
    documentId: str

async def get_document(arguments: GetDocumentInput) -> dict[str, Any]:
    return await call_tool(server_id="google-drive", name="get_document", arguments=arguments)
```

**Sources**: [R3]

### Tool Broker (Recommended)

**Definition**: A host-side component that mediates all tool calls from sandboxes, enforcing policy (approvals, allowlists), handling credentials/OAuth, and emitting audit logs.

**Scope**:
- **Includes**:
  - Tool-call authorization gates (especially for destructive or spending actions)
  - Credential isolation (sandboxes do not hold long-lived tokens)
  - Egress control (broker talks to external services; sandbox does not)
  - Auditing (who/what/when, hashes, sizes, outcomes)
- **Excludes**:
  - Acting as a general-purpose network proxy for arbitrary outbound traffic

**Example**:

```text
Sandbox code  ──► wrappers ──► broker (policy+auth+audit) ──► MCP server(s)
```

**Sources**: [R8], [R6]

### Runtime Contract (Normative)

**Definition**: A fixed set of execution-time rules that AI-generated code and the sandbox runner MUST follow (filesystem layout, import paths, output/error formats, size limits, and redaction rules).

**Scope**:
- **Includes**:
  - Supported language/runtime versions
  - Import rules and naming conventions
  - Output and error contracts (machine-readable vs logs)
  - Limits (time/memory/filesystem/network) and redaction requirements
- **Excludes**:
  - Tool schemas themselves (authoritative source is MCP server via `tools/list`)

**Sources**: [R2], [R3]

### Tool Catalog (Progressive Disclosure)

**Definition**: A tiered discovery mechanism that exposes tool names and descriptions first, then loads full schemas only when needed.

**Scope**:
- **Includes**:
  - Minimal “manifest” (serverId, tool name, title/description)
  - On-demand retrieval of full tool definitions (input/output schemas)
  - Cache invalidation on MCP `notifications/tools/list_changed`
- **Excludes**:
  - Pre-loading all tool schemas into the system prompt

**Sources**: [R1], [R3]

---

## Core Patterns

### Pattern: Architecture Topologies

**Intent**: Provide a secure, reproducible way to execute AI-generated code that uses MCP tools without dumping full tool schemas or large intermediate data into the model context.

**Context**: Any system running untrusted, model-generated code that calls external tools or handles sensitive data.

**Implementation**:

**Topology A (Direct)**: Sandbox connects directly to MCP servers (requires strict egress controls inside the sandbox).

```text
Model ──► Host Orchestrator ──► Sandbox Runner ──► MCP Client ──► MCP Server(s)
```

**Topology B (Brokered, Recommended)**: Sandbox has no external egress; only the broker talks to MCP servers and external networks.

```text
Model ──► Host Orchestrator ──► Sandbox Runner ──► Wrappers ──► Tool Broker ──► MCP Server(s)
                                                 (policy+auth+audit)
```

**Key Principles**:
- Prefer brokered access to keep credentials and network policy out of the sandbox.
- Treat all tool metadata (including descriptions/annotations/icons) as untrusted unless sourced from a trusted server. [R2]

**Trade-offs**:
- ✅ **Advantages**: Strong isolation, easier approvals and auditing, better secret hygiene.
- ⚠️ **Disadvantages**: More infrastructure (broker, catalog, runner), potential latency.
- 💡 **Alternatives**: Direct egress with an egress proxy and strict allowlists (higher risk).

**Sources**: [R2], [R8]

---

### Pattern: Runtime Contract (Normative)

**Intent**: Ensure AI-generated code “just works” across sessions and models, with unambiguous rules for imports, outputs, and error handling.

**Context**: Any Code MCP system that expects models to write executable code reliably.

**Normative Requirements**:

#### Supported Runtimes (MUST)
- Python: **3.11+**
- Node.js: **20+**

#### Filesystem & Imports (MUST)
- Working directory MUST be `/workspace`.
- AI-generated code MUST be able to import wrappers from an always-present, importable path:
  - Python: `import servers.<server_module>` or `from servers.<server_module> import <tool_fn>`
  - Node: `import * as <alias> from "./servers/<server_module>/index.js"`
- Wrapper package/module layout MUST be stable across runs. If you change layout, update your project SSOT.

#### Naming Rules (MUST)
- MCP tool names are protocol identifiers and MUST be treated as case-sensitive strings. [R3]
- Wrapper identifiers MUST be derived deterministically:
  - `server_module`: snake_case derived from a stable `server_id` (e.g., `google-drive` → `google_drive`)
  - `tool_fn` (Python): snake_case derived from MCP tool name by splitting on `[._-]` and joining with `_`
  - `toolFn` (TS/JS): camelCase derived from MCP tool name by splitting on `[._-]`
- Wrapper code MUST preserve the original MCP tool name for `tools/call` (do not “sanitize” the protocol name). [R3]

#### Output Contract (MUST)
- The sandbox runner process MUST print **exactly one** machine-readable result to stdout as a **single-line JSON object**.
- All logs, progress messages, and debugging output MUST go to stderr.
- Default size limits (override only with an explicit SSOT decision):
  - `stdout` max: **64 KiB**
  - `stderr` max: **256 KiB**
- Runner MUST redact secrets/PII in both stdout and stderr before returning to the host.

#### Runner Telemetry Envelope (MUST)

When emitting the single JSON line on stdout, include the following minimum fields:

```json
{
  "run_id": "uuid-or-stable-id",
  "trace_id": "trace-id",
  "tool_name": "tool-or-script-name",
  "tool_version": "optional",
  "input_digest": "sha256:...",
  "output_digest": "sha256:...",
  "sandbox_image": "optional-image-id",
  "duration_ms": 1234,
  "approval_state": "NOT_REQUIRED",
  "result": { "ok": true, "data": "..." }
}
```

- Logs MUST go to stderr, never stdout.
- `result` MUST be the only potentially large payload; metadata stays small and stable.

Alignment: use the same key names as `docs/SSOT.md` telemetry keys.

#### Result Contract (MUST)
The runner’s `result` field MUST be shaped as:

```json
{
  "ok": true,
  "data": {},
  "metrics": { "duration_ms": 123 }
}
```

or, on failure:

```json
{
  "ok": false,
  "error": { "type": "ToolError", "message": "…", "retryable": true },
  "metrics": { "duration_ms": 123 }
}
```

#### Code-to-Runner Handoff (SHOULD)
- Preferred: AI-generated code SHOULD set a JSON-serializable `result` value:
  - Python: assign to a global `result` variable
  - Node: assign to `globalThis.result`
- Runner SHOULD use that value as `data`. If absent, runner MAY fall back to parsing the last stdout line as JSON.

**Sources**: [R2], [R8]

---

### Pattern: Wrapper Generation from MCP `tools/list`

**Intent**: Generate consistent wrappers from the MCP server’s authoritative tool definitions so models can rely on stable names, inputs, and outputs.

**Context**: Whenever onboarding a new MCP server or when tool schemas drift over time.

**Implementation**:

1. Fetch tools from each server via MCP `tools/list`. [R3]
2. For each tool definition, generate:
   - A wrapper function (Python/JS) that calls `tools/call` with `name` + `arguments`
   - Optional static types and runtime validators derived from `inputSchema` / `outputSchema`
3. Subscribe to `notifications/tools/list_changed` when the server advertises `tools.listChanged`, and invalidate/regenerate wrappers on change. [R3]

**MCP Tool Definition Fields (2025-11-25)**:
- `name` (required), `title` (optional), `description` (recommended)
- `inputSchema` (required JSON Schema; default dialect is 2020-12) [R5]
- `outputSchema` (optional JSON Schema)
- `icons` (optional) and `annotations` (optional) [R3], [R5]

**Tool Name Guidance (MUST Support)**:
- Tool names may include `_`, `-`, and `.` and be up to 128 characters. Wrapper generation MUST handle these safely. [R3]

**Example: Wrapper Stub (Python)**:

```python
from typing import Any, TypedDict
from client.mcp_client import call_tool

class GetWeatherInput(TypedDict):
    location: str

async def get_weather(arguments: GetWeatherInput) -> dict[str, Any]:
    # tool name is the MCP protocol identifier
    return await call_tool(server_id="weather", name="get_weather", arguments=arguments)
```

**Example: Wrapper Stub (Node ESM)**:

```js
// servers/weather/index.js
import { callTool } from "../../client/mcp_client.js";

export async function getWeather(arguments) {
  return await callTool({ serverId: "weather", name: "get_weather", arguments });
}
```

**Sources**: [R3], [R5]

---

### Pattern: Tool Result Normalization (MCP Tool Result)

**Intent**: Prevent downstream ambiguity by consistently interpreting MCP Tool Results across wrappers and languages.

**Context**: Any wrapper that returns MCP tool results to sandbox code.

**Rules (MUST)**:
- Treat `isError: true` as a tool-level failure.
- Prefer `structuredContent` when present.
- If returning structured content, tools SHOULD also include a serialized JSON string in a `content` text block for compatibility. [R3]

**Recommended Normalized Shape (SHOULD)**:

```ts
type ToolCallResult<T> =
  | { ok: true; data: T; raw: any }
  | { ok: false; error: { type: string; message: string; retryable: boolean }; raw?: any };
```

**Sources**: [R3]

---

### Pattern: Progressive Disclosure via Tool Catalog

**Intent**: Keep tool definitions out of the model context until they are needed, while still enabling accurate tool selection and code generation.

**Context**: Any deployment where tool definitions are large or numerous.

**Implementation**:

1. Expose a **manifest** to the model (names + short descriptions only):
   - `{ serverId, toolName, title?, description? }`
2. Allow on-demand retrieval of full tool definitions:
   - `{ inputSchema, outputSchema?, icons?, annotations? }`
3. Cache definitions per session; invalidate on:
   - `notifications/tools/list_changed` (server-side) [R3]
   - TTL expiry or explicit operator refresh (host policy)

**Standard Host-Side API (SSOT for This Document)**:

```ts
// These are host/orchestrator utilities (not MCP tools).
catalog.searchTools({ query, serverId, detail: "name" | "name+description" });
catalog.getToolDefinition({ serverId, name }); // returns full tool definition
```

**Registry (Optional)**:
- MCP Registry MAY be used as a discovery index, but `tools/list` from the connected server remains the authoritative source of truth. [R7], [R3]

**Sources**: [R1], [R3], [R7]

---

### Pattern: Sandbox Security (Isolation, Network, Secrets)

**Intent**: Execute untrusted AI-generated code safely.

**Context**: Always. If you execute untrusted code, security is not optional.

**Rules (MUST)**:
- Use OS-level isolation (containers/microVMs) and enforce CPU/memory/time/disk limits at the sandbox boundary. [R8]
- Do **not** mount `/var/run/docker.sock` into the sandbox or any long-running service that can be influenced by untrusted inputs; Docker socket access is effectively host control. [R9]
- Sandboxes MUST NOT contain long-lived credentials. Prefer broker-managed auth.

**Network Modes (Choose One; Do Not Mix)**:

**Mode A (Brokered, Recommended)**:
- Sandbox has **no external egress**.
- Broker has controlled egress and holds credentials.

```yaml
networks:
  sandbox-net:
    internal: true
  egress-net: {}

services:
  sandbox:
    image: your-sandbox
    networks: [sandbox-net]
  tool-broker:
    image: your-broker
    networks: [sandbox-net, egress-net]
```

**Mode B (Direct Egress)**:
- Sandbox can reach MCP servers and external APIs.
- You MUST implement strict egress allowlists (proxy/firewall/DNS controls) and block metadata endpoints.

**Audit Logging (MUST)**:
- Record at minimum: timestamp, code hash, serverId/toolName, arguments hash, result size, duration, approval decisions, and redaction events.

**Sources**: [R8], [R9], [R2]

---

### Pattern: MCP Authorization (OAuth 2.1) for Remote Servers

**Intent**: Implement correct and interoperable authorization for MCP servers accessed over HTTP transports.

**Context**: Any deployment calling remote MCP servers over HTTP where access is restricted.

**Key Requirements (2025-11-25)**:
- Authorization is optional at protocol level, but when used for HTTP-based transports, implementations SHOULD follow the MCP authorization specification. [R4]
- MCP servers MUST implement OAuth 2.0 Protected Resource Metadata (RFC 9728) for authorization server discovery. [R4]
- MCP clients MUST implement Resource Indicators (RFC 8707). [R4]
- Discovery MUST support RFC 8414 and/or OpenID Connect Discovery. [R4], [R5]
- Incremental scope consent via `WWW-Authenticate` should be supported. [R5]

**Code MCP Recommendation (SHOULD)**:
- Implement authorization in the Tool Broker so sandboxes never handle tokens.

**Sources**: [R4], [R5]

---

### Pattern: Reliability, Self-Correction, and Replay

**Intent**: Make Code MCP robust to transient failures while preventing infinite loops and enabling reproduction.

**Context**: Any production system executing model-generated code.

**Implementation**:

```python
MAX_RETRIES = 3

def is_retryable(error_type: str) -> bool:
    return error_type in {"Timeout", "RateLimit", "TransientNetwork"}

async def run_with_self_correction(task: str):
    for attempt in range(1, MAX_RETRIES + 1):
        code = await model.generate_code(task)
        run = await sandbox.run(code)
        if run["ok"]:
            return run["data"]
        if not run["error"]["retryable"]:
            break
        task = task + f"\n\nPrevious error (attempt {attempt}): {run['error']['message']}"
    return {"error": "handoff_required"}
```

**Rules (MUST)**:
- Self-correction MUST have a hard cap (`MAX_RETRIES`).
- Store enough data to replay: code hash, tool call list, inputs, and environment identifiers.

**Sources**: [R1], [R2]

---

### Pattern: System Prompt Design (Code MCP Mode)

**Intent**: Configure a model to reliably operate in Code MCP mode with progressive disclosure and strict output rules.

**Context**: When initializing the agent session.

**Implementation**:

```markdown
You solve tasks by writing code that runs in a sandbox.

Rules:
- Do not call MCP tools directly; use code wrappers instead.
- Use tool catalog progressive disclosure:
  1) `catalog.searchTools({ query, detail: "name" | "name+description" })`
  2) `catalog.getToolDefinition({ serverId, name })` when you need schemas
- The sandbox runner returns exactly one JSON line to stdout; logs go to stderr.
- Keep large intermediate data inside the sandbox; return only summaries/aggregates.
```

**Sources**: [R1]

---

### MCP Spec Alignment (Protocol Revision: 2025-11-25)

**Intent**: Prevent spec drift by explicitly tracking MCP behaviors this pattern depends on.

**Key 2025-11-25 Changes Relevant to Code MCP**:
- Tool name guidance and icon metadata for tools/resources/prompts. [R5], [R3]
- Authorization improvements (OIDC discovery, incremental scope consent, client ID metadata docs). [R5], [R4]
- JSON Schema 2020-12 established as default dialect. [R5]
- Input validation errors should be returned as Tool Execution Errors (not Protocol Errors) to enable model self-correction. [R5]
- Experimental “tasks” for durable requests (feature-gated; record `task_id` in evidence/telemetry when used). [R5]
- Sampling can include tools/toolChoice; `includeContext` values `thisServer`/`allServers` are soft-deprecated in the schema. [R2]

**Compatibility Notes (Recommended Defaults)**:
| MCP Feature | Code MCP Handling |
|---|---|
| `tools/list` + `tools/call` | Required; wrappers generated from `tools/list` and call `tools/call`. |
| `notifications/tools/list_changed` | Should be handled to invalidate caches and regenerate wrappers. |
| `inputSchema` / `outputSchema` | Required/optional as per MCP; wrapper codegen must support both. |
| Tool `icons` + naming guidance | Must not break codegen or file naming. |
| OAuth 2.1 authorization | Prefer broker-managed implementation for HTTP transports. |
| Experimental `tasks` | Optional; support only if you need durable/polling requests (feature-gated). |

**Sources**: [R2], [R3], [R4], [R5]

**Note**: MCP explicitly labels `tasks` as experimental in the 2025-11-25 changelog. Treat it as optional and monitor upgrades via Update Log. [R5]

---

## Decision Checklist

- [ ] **Runtime Contract implemented and tested**: Stable imports, single-line stdout JSON, stderr logs, size limits, redaction [R2]
  - **Verify**: Run known-good code and verify stdout JSON parses; verify extra stdout is rejected or captured.
  - **Impact**: Ambiguous imports/outputs cause repeated agent failures and unsafe leakage.
  - **Mitigation**: Enforce contract in runner; add conformance tests.

- [ ] **OS-level isolation is enforced**: Containers/microVMs with CPU/memory/time/file/network limits [R8]
  - **Verify**: Run resource exhaustion tests and confirm limits trigger.
  - **Impact**: Host compromise or denial-of-service.
  - **Mitigation**: Use gVisor/Kata/Firecracker; defense-in-depth inside the sandbox is not sufficient.

- [ ] **No Docker socket exposure**: `docker.sock` is not mounted in any component reachable by untrusted inputs [R9]
  - **Verify**: Audit container specs; search configs for `/var/run/docker.sock`.
  - **Impact**: Effective host control.
  - **Mitigation**: Use Kubernetes Jobs, a dedicated sandbox service, or a strictly filtered socket proxy for local dev only.

- [ ] **Tool Broker enforces approvals and secret isolation**: High-risk actions require explicit approval; tokens stay outside sandbox [R2]
  - **Verify**: Attempt destructive tool call without approval; ensure it is denied.
  - **Impact**: Accidental deletion/spend or data exfiltration.
  - **Mitigation**: Broker policy, human-in-the-loop for risky tools, comprehensive auditing.

- [ ] **Wrapper codegen matches MCP schema fields**: `name`, `inputSchema`, `outputSchema`, tool name guidance supported [R3], [R5]
  - **Verify**: Generate wrappers for tool names with `.` and `-`; confirm imports work.
  - **Impact**: Broken wrappers or name collisions.
  - **Mitigation**: Deterministic sanitization for identifiers, preserve protocol names for calls.

- [ ] **Tool results are normalized**: Prefer `structuredContent`, handle `isError`, validate outputs when `outputSchema` exists [R3]
  - **Verify**: Run tools that return both structured and unstructured outputs.
  - **Impact**: Downstream code mis-parses results and fails or leaks data.
  - **Mitigation**: Normalization layer with schema validation.

- [ ] **Progressive disclosure is measured, not assumed**: Token/cost baseline recorded, then compared after rollout [R1]
  - **Verify**: Track token counts for “all-tools upfront” vs “manifest + on-demand.”
  - **Impact**: “98.7%” style numbers become folklore and stop reflecting reality.
  - **Mitigation**: Add a measurement script and report the results per environment.

- [ ] **Schema drift handled**: `notifications/tools/list_changed` invalidates caches and triggers regeneration [R3]
  - **Verify**: Simulate tool list change; confirm cache bust + regen.
  - **Impact**: Silent mismatch between wrappers and server behavior.
  - **Mitigation**: Notification handling + periodic refresh.

---

## Anti-patterns / Pitfalls

### Anti-pattern: Pre-loading All Tool Definitions

**Symptom**: System prompt contains full schemas for all tools, consuming context and inflating costs.

**Why It Happens**: It mirrors direct function-calling patterns.

**Impact**:
- Context window exhaustion
- Higher token costs
- Worse tool selection due to prompt noise

**Solution**: Use a tool catalog (manifest first, schemas on-demand) and keep schemas in the sandbox/codegen, not the prompt.

**Sources**: [R1]

### Anti-pattern: Mounting `docker.sock`

**Symptom**: A service that processes untrusted inputs has access to `/var/run/docker.sock`.

**Why It Happens**: It’s a convenient way to “manage containers from a container.”

**Impact**:
- Effective host takeover
- Privilege escalation and data access outside intended boundaries

**Solution**: Do not mount the Docker socket. Use a dedicated sandboxing service, Kubernetes Jobs, or a tightly filtered socket proxy for local dev only.

**Sources**: [R9]

### Anti-pattern: Language-Level Sandboxing as Primary Security

**Symptom**: Relying on `restricted_imports`, Node `vm`, or similar as the main containment boundary.

**Why It Happens**: Easier than OS-level sandboxing.

**Impact**:
- Trivial bypass
- No kernel-level resource isolation

**Solution**: OS-level isolation is mandatory; language-level restrictions are defense-in-depth only.

**Sources**: [R8]

### Anti-pattern: Mixing Logs with Machine Output

**Symptom**: Human logs and machine-readable outputs both go to stdout, causing parse failures and agent retry loops.

**Solution**: Enforce the runner contract: one JSON line to stdout, logs to stderr.

---

## Evaluation

### Metrics

**Token Reduction Rate**: Reduction vs a baseline that pre-loads all tool schemas.
- **Why It Matters**: Primary cost/context metric. [R1]
- **Target**: Environment-specific; report measured values rather than hard-coding.
- **Measurement**: Tokenize (a) baseline prompt with all tools, (b) catalog-only prompt, (c) average on-demand schema additions.
- **Tools**: Token counters + cost dashboards.

**Tool Selection Accuracy**: How often the system selects the correct tool(s) given a task.
- **Why It Matters**: Progressive disclosure is only valuable if tool discovery remains accurate.
- **Measurement**: Curated task set with expected tool(s); compare selected tools.

**Schema Drift Detection Time**: Time from server tool change to wrapper/catalog update.
- **Why It Matters**: Drift causes silent failures.
- **Measurement**: Trigger `tools/list_changed` and measure update latency.

**Sandbox Overhead**: P95 latency added by sandboxing and brokering.
- **Why It Matters**: Determines feasibility for interactive applications.
- **Measurement**: Trace spans: runner startup, execution, broker call, tool call.

**Sources**: [R1], [R3]

### Testing Strategies

**Contract Tests**:
- Validate wrapper inputs against `inputSchema`.
- Validate `structuredContent` against `outputSchema` when present.

**Integration Tests**:
- Search → load schema → generate code → run sandbox → verify runner JSON output.
- Verify `notifications/tools/list_changed` invalidates caches and regenerates wrappers.

**Security Tests**:
- Resource exhaustion attempts (CPU/memory/time).
- Network policy violations (unexpected outbound).
- Secret leakage checks (stdout/stderr redaction).

### Success Criteria

- [ ] Runner output is exactly one JSON line to stdout and always parses
- [ ] Wrappers are generated from `tools/list` and handle tool names with `.`/`-`
- [ ] Tool broker prevents unauthorized destructive/spending actions
- [ ] Schema drift is detected and fixed automatically via list_changed/refresh

---

## Practical Examples

### Example: Document Processing Workflow (Node)

```js
import * as gdrive from "./servers/google_drive/index.js";

async function main() {
  console.error("Fetching document…");
  const doc = await gdrive.getDocument({ documentId: "abc123" });

  const text = doc.structuredContent?.content ?? JSON.stringify(doc.content);
  const summary = summarize(text);

  globalThis.result = { summary };
}

main().catch((e) => {
  console.error(e?.stack ?? String(e));
  process.exitCode = 1;
});
```

### Example: Data Filtering Workflow (Python)

```python
import asyncio
import json
import sys

import servers.sheets as sheets

async def main():
    rows = await sheets.get_all_rows({"sheetId": "quarterly"})
    print(f"Processing {len(rows)} rows…", file=sys.stderr)

    metrics = calculate_metrics(rows)
    anomalies = detect_anomalies(rows)

    global result
    result = {
        "summary": metrics["summary"],
        "anomaly_count": len(anomalies),
    }

asyncio.run(main())
```

### Appendix A: Python Runner Reference (Top-level `await` Support)

```python
import asyncio
import hashlib
import io
import json
import sys
import time
import traceback
import uuid
from contextlib import redirect_stderr, redirect_stdout

STDOUT_MAX = 64 * 1024
STDERR_MAX = 256 * 1024

def _wrap_async(user_code: str) -> str:
    body = "\n".join("    " + line for line in user_code.splitlines()) or "    pass"
    return "async def __agent_main__():\n" + body + "\n"

def _truncate(s: str, limit: int) -> str:
    if len(s) <= limit:
        return s
    return s[:limit] + "\n<TRUNCATED>"

def _digest(value: object) -> str:
    payload = json.dumps(value, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"

def main() -> None:
    user_code = sys.stdin.read()
    namespace: dict[str, object] = {}
    input_digest = f"sha256:{hashlib.sha256(user_code.encode('utf-8')).hexdigest()}"
    run_id = f"run_{uuid.uuid4().hex}"
    trace_id = f"trace_{uuid.uuid4().hex}"

    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()
    started = time.monotonic()

    try:
        wrapped = _wrap_async(user_code)
        exec(compile(wrapped, "<agent_code>", "exec"), namespace, namespace)

        async def _run():
            with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
                await namespace["__agent_main__"]()  # type: ignore[index]

        asyncio.run(_run())

        data = namespace.get("result", None)
        duration_ms = int((time.monotonic() - started) * 1000)
        result_payload = {
            "ok": True,
            "data": data,
            "metrics": {"duration_ms": duration_ms},
        }
    except Exception as e:
        duration_ms = int((time.monotonic() - started) * 1000)
        result_payload = {
            "ok": False,
            "error": {
                "type": type(e).__name__,
                "message": str(e),
                "retryable": False,
            },
            "metrics": {"duration_ms": duration_ms},
        }
        stderr_buf.write(traceback.format_exc())

    output_digest = _digest(result_payload)
    out = {
        "run_id": run_id,
        "trace_id": trace_id,
        "tool_name": "python-runner",
        "tool_version": "reference",
        "input_digest": input_digest,
        "output_digest": output_digest,
        "sandbox_image": None,
        "duration_ms": duration_ms,
        "approval_state": "NOT_REQUIRED",
        "result": result_payload,
    }

    # Enforce size limits (redaction omitted in this reference)
    stdout_s = _truncate(stdout_buf.getvalue(), STDOUT_MAX)
    stderr_s = _truncate(stderr_buf.getvalue(), STDERR_MAX)

    # Runner outputs exactly one JSON line to stdout
    sys.stderr.write(stderr_s)
    sys.stdout.write(json.dumps(out, separators=(",", ":")) + "\n")
    sys.stdout.flush()

if __name__ == "__main__":
    main()
```

### Appendix B: Governance and Neutrality

MCP governance is documented publicly, including stewardship under LF Projects, LLC, which strengthens vendor-neutrality and long-term stability for adopters. [R6]

---

## Update Log

- **2025-12-21** – Add runner telemetry envelope and clarify experimental tasks handling. (Author: SpeSan)
- **2025-12-17** – Rebranded to SpeSan and performed final content check. (Author: SpeSan)
- **2025-12-17** – Major rewrite: added a normative Runtime Contract, aligned wrapper/codegen with MCP 2025-11-25 (`inputSchema`/`outputSchema`, tool results, tool naming, list_changed), removed `docker.sock` guidance, added OAuth 2.1 authorization and governance references. (Author: SpeSan)
- **2025-11-24** – Fixed Update Log date inconsistencies. (Author: SpeSan)
- **2025-11-22** – Updated based on peer review: added System Prompt Design and Self-Correction Loop patterns, clarified OS-level sandbox requirements, added warm pool and debug replay checklists. (Author: SpeSan)
- **2025-11-19** – Enhanced Sandbox-Based Execution pattern with complete Docker implementation, security profiles, and Python wrapper. Added TypeScript stub generation implementation with full type mapping and CLI tooling. (Author: SpeSan)
- **2025-11-14** – Added Practical Examples section with document processing and data analysis pipeline examples. Updated metadata. (Author: SpeSan)
- **2025-11-13** – Initial specification created covering Code MCP architecture, implementation patterns, progressive disclosure, sandbox execution, security practices, and cost optimization strategies. (Author: SpeSan)

---

## See Also

### Prerequisites
- [MCP Specification (2025-11-25)](https://modelcontextprotocol.io/specification/2025-11-25) – Canonical protocol definitions and schemas
- [MCP Tools](https://modelcontextprotocol.io/specification/2025-11-25/server/tools) – Tool definitions, naming guidance, tool results, list_changed
- [MCP Authorization](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization) – OAuth 2.1 requirements for HTTP transports
- [JSON Schema](https://json-schema.org/) – Required for schema validation and type generation

### Related Topics
- [AGENT_SKILL.md](./AGENT_SKILL.md) – Skill packaging and reuse guidance
- [EXEC_PLAN.md](./EXEC_PLAN.md) – Long-running task planning methodology
- [SSOT.md](./SSOT.md) – Governance guide for Single Source of Truth
- [MCP Governance](https://modelcontextprotocol.io/community/governance) – Project governance and stewardship
- [MCP Registry](https://registry.modelcontextprotocol.io/) – Registry index for servers (discovery aid; not the authoritative runtime tool list)

### Advanced / Platform-specific
- [MCP Security Best Practices](https://modelcontextprotocol.io/specification/2025-11-25/basic/security_best_practices) – Protocol-level security guidance
- [gVisor](https://gvisor.dev/) – Container sandboxing runtime
- [Firecracker](https://firecracker-microvm.github.io/) – MicroVM isolation
- [Kata Containers](https://katacontainers.io/) – VM-based container runtime
- [Anthropic: Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp) – Case study motivating Code MCP patterns

---

## References

- [R1] Anthropic. "Code execution with MCP: building more efficient AI agents." Anthropic Engineering Blog. https://www.anthropic.com/engineering/code-execution-with-mcp (accessed 2025-12-17)
- [R2] Model Context Protocol. "Specification (Protocol Revision: 2025-11-25)." https://modelcontextprotocol.io/specification/2025-11-25 (accessed 2025-12-17)
- [R3] Model Context Protocol. "Tools (2025-11-25)." https://modelcontextprotocol.io/specification/2025-11-25/server/tools (accessed 2025-12-17)
- [R4] Model Context Protocol. "Authorization (2025-11-25)." https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization (accessed 2025-12-17)
- [R5] Model Context Protocol. "Key Changes (2025-11-25)." https://modelcontextprotocol.io/specification/2025-11-25/changelog (accessed 2025-12-17)
- [R6] Model Context Protocol. "Governance and Stewardship." https://modelcontextprotocol.io/community/governance (accessed 2025-12-17)
- [R7] Model Context Protocol. "MCP Registry." https://registry.modelcontextprotocol.io/ (accessed 2025-12-17)
- [R8] Model Context Protocol. "Security Best Practices." https://modelcontextprotocol.io/specification/2025-11-25/basic/security_best_practices (accessed 2025-12-17)
- [R9] Docker. "Protect access to the Docker daemon socket." https://docs.docker.com/engine/security/protect-access/ (accessed 2025-12-17)

---

**Document ID**: `docs/CODE_MCP.md`
**Canonical URL**: `https://github.com/spesans/dev-ssot/blob/main/docs/CODE_MCP.md`
**License**: MIT
