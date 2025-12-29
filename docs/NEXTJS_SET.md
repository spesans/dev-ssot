---
title: Next.js Standard Set
slug: nextjs-standard
summary: "Next.js adoption deltas (TypeScript, linting, IO boundaries, env hygiene)"
type: spec
tags: [nextjs, frontend, react, typescript, ssot]
last_updated: 2025-12-29
---

# Next.js Standard Set

> Platform-specific deltas for adopting teams using Next.js

## Agent Contract

- **PURPOSE**:
  - Define **Next.js-specific deltas** on top of [`docs/TYPESCRIPT_SET.md`](./TYPESCRIPT_SET.md) without turning the SSOT into “backend-only” guidance.
  - Make boundaries explicit in a Next.js app: **browser ↔ server ↔ (optional) edge**, and require runtime validation at IO boundaries.
  - Provide deterministic defaults for Next.js adoption surfaces: TypeScript integration, lint/scripts, env separation, and boundary validation.
- **USE_WHEN**:
  - The adopting repository contains a Next.js app (App Router and/or Pages Router).
  - You need a canonical place to record Next.js runtime constraints and boundary rules.
- **DO_NOT_USE_WHEN**:
  - You are not using Next.js (use the Web App Profile in [`docs/TYPESCRIPT_SET.md`](./TYPESCRIPT_SET.md)).
  - You need product/domain specs (belongs in the adopting repository’s Project SSOT).
- **PRIORITY**:
  - This document is a **platform-specific extension** to [`docs/TYPESCRIPT_SET.md`](./TYPESCRIPT_SET.md).
  - If a Next.js delta conflicts with the TypeScript baseline, the Next.js delta wins **only for the Next.js app scope**.
  - App-local `AGENTS.md` files MUST be **delta-only** and SHOULD link to this doc (pointer pattern).
- **NORMATIVE KEYWORDS**:
  - This document uses **MUST**, **SHOULD**, and **MAY** as defined in [`docs/SSOT.md`](./SSOT.md).
- **RELATED_TOPICS**:
  - ssot-guide
  - typescript-standard
  - agents-readme
  - exec-plan

---

## TL;DR

- Use [`docs/TYPESCRIPT_SET.md`](./TYPESCRIPT_SET.md) as the baseline; apply only the Next.js deltas defined here.
- Treat these as IO boundaries: **Route Handlers**, **Server Actions**, **Middleware**, and **external fetches** → validate at runtime. [R3] [R4]
- Prevent env leaks: only `NEXT_PUBLIC_*` is allowed in client-executed modules; keep secrets server-only. [R2]
- TypeScript integration: keep `next-env.d.ts` and include `.next/types/**/*.ts` when applicable. [R1]

---

## Canonical Definitions

### App Router

**Definition**: Next.js routing based on the `app/` directory where Server Components are the default rendering model and routing is defined by filesystem conventions. [R3]

### Pages Router

**Definition**: Next.js routing based on the `pages/` directory (traditional pages and API Routes).

### Route Handler

**Definition**: A server-side handler using the Web `Request`/`Response` model, typically implemented as `app/**/route.ts`. [R3]

### Server Action

**Definition**: A server-executed function designated with the `"use server"` directive and invoked from client-driven flows under Next.js constraints. [R4]

### Public Environment Variable

**Definition**: An environment variable intentionally exposed to browser code, typically `NEXT_PUBLIC_*`. Variables without the `NEXT_PUBLIC_` prefix are server-only by default. [R2]

---

## Core Patterns

### Pattern: Worldview Boundary for a Next.js App

**Intent**: Keep Next.js specifics local to the Next.js subsystem while remaining SSOT-compliant.

**Implementation**:

```text
/
├── docs/
│   ├── TYPESCRIPT_SET.md
│   └── NEXTJS_SET.md
└── apps/
    └── web/
        ├── README.md
        ├── AGENTS.md
        └── src/ ...
```

**Key Principles**:
- `apps/web/AGENTS.md` SHOULD be delta-only and link to:
  - `../../AGENTS.md`
  - `../../docs/TYPESCRIPT_SET.md`
  - `../../docs/NEXTJS_SET.md`
- Do not copy/paste framework standards into `apps/web/AGENTS.md` (pointer pattern).

---

### Pattern: TypeScript Integration (Delta on Web App Profile)

**Intent**: Keep strictness from the baseline while matching Next.js TypeScript integration. [R1]

**Rules (MUST)**:
- The Next.js app `tsconfig.json` MUST extend the baseline (`tsconfig.base.json` in the adopting repo).
- `next-env.d.ts` SHOULD be committed and MUST NOT be edited manually. [R1]
- If your Next.js workflow generates `.next/types/**/*.ts`, your `tsconfig.json` SHOULD include it. [R1]

**Implementation (example)**:

```jsonc
{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": {
    "jsx": "preserve",
    "noEmit": true,
    "plugins": [{ "name": "next" }]
  },
  "include": [
    "next-env.d.ts",
    "**/*.ts",
    "**/*.tsx",
    ".next/types/**/*.ts"
  ],
  "exclude": ["node_modules"]
}
```

**Watch-outs**:
- `.next/` is generated. If your typecheck pipeline requires `.next/types`, ensure the pipeline runs the step that generates it (commonly `next build`) before `tsc`.

---

### Pattern: Standard Scripts for Next.js Apps

**Intent**: Provide stable entry points for humans and agents, aligned with the baseline toolchain.

**Recommended scripts (SHOULD)**:

```jsonc
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "eslint .",
    "typecheck": "tsc -p tsconfig.json --noEmit"
  }
}
```

**Notes**:
- Ensure your ESLint config enables Next.js rules where applicable (e.g., `next/core-web-vitals`). [R5]
- Keep the canonical lint entrypoint as `eslint` so it remains compatible with ESLint v9 flat config patterns in [`docs/TYPESCRIPT_SET.md`](./TYPESCRIPT_SET.md).

---

### Pattern: Runtime Validation at Next.js IO Boundaries

**Intent**: Make “type safety” real at runtime by validating untrusted inputs and outputs. [R3] [R4]

**Rules (MUST)**:
- Route Handlers MUST validate request inputs (params/query/body) before use. [R3]
- Server Actions MUST treat all arguments as untrusted input and validate them on the server. [R4]
- Middleware MUST treat headers/cookies as untrusted input and validate/normalize before decisions.
- External fetch responses MUST be treated as `unknown` and validated before use (see [`docs/TYPESCRIPT_SET.md`](./TYPESCRIPT_SET.md) “Type Sanitization”).

---

### Pattern: Environment Variable Separation (Server vs Client)

**Intent**: Prevent accidental secret leakage into client bundles. [R2]

**Rules (MUST)**:
- Client-executed modules MUST only read `NEXT_PUBLIC_*` environment variables. [R2]
- Do not use `next.config.js` `env` to inject secrets; those values are exposed to the client bundle. [R6]

**Implementation (recommended)**:
- Create explicit env modules:
  - `src/env/server.ts`: server-only schema + validation
  - `src/env/public.ts`: `NEXT_PUBLIC_*` schema + validation

---

## Decision Checklist

- [ ] **TypeScript**: `tsconfig.json` extends baseline and includes `next-env.d.ts`. [R1]
- [ ] **Linting**: ESLint includes Next.js rules where applicable (e.g., `next/core-web-vitals`). [R5]
- [ ] **Boundaries**: Route Handlers and Server Actions validate inputs at runtime. [R3] [R4]
- [ ] **Env hygiene**: Only `NEXT_PUBLIC_*` is used in client-executed modules; secrets remain server-only. [R2]
- [ ] **Pointer pattern**: `apps/web/AGENTS.md` links to `docs/NEXTJS_SET.md` instead of duplicating it.

---

## Anti-patterns / Pitfalls

### Anti-pattern: TypeScript-only “validation”

**Symptom**: Route Handlers / Server Actions accept typed inputs but never validate at runtime.

**Impact**: Runtime crashes and unsafe assumptions with untrusted data.

**Solution**: Validate at IO boundaries (see “Runtime Validation at Next.js IO Boundaries”). [R3] [R4]

### Anti-pattern: Secret leakage to the client

**Symptom**: A non-`NEXT_PUBLIC_*` secret is referenced from client-executed code, or injected via `next.config.js` `env`.

**Impact**: Secret becomes visible in the browser bundle.

**Solution**: Keep secrets server-only; restrict client envs to `NEXT_PUBLIC_*`. [R2] [R6]

---

## Evaluation

**Minimum success criteria**:
- New contributors can run `dev`, `build`, `lint`, and `typecheck` using only the app’s `AGENTS.md`.
- Runtime validation exists at all declared Next.js IO boundaries.
- No secrets appear in client bundles.

---

## Update Log

- **2025-12-29** – Initial version: Next.js deltas for TypeScript, linting, IO boundaries, and env hygiene. (Author: SpeSan)

---

## See Also

- [`docs/SSOT.md`](./SSOT.md) – Governance, precedence, and normative keywords.
- [`docs/TYPESCRIPT_SET.md`](./TYPESCRIPT_SET.md) – Baseline TypeScript toolchain and Web App Profile.
- [`docs/README_AGENTS.md`](./README_AGENTS.md) – Pointer pattern and worldview boundaries for README/AGENTS.
- [`docs/EXEC_PLAN.md`](./EXEC_PLAN.md) – Planning methodology for multi-step changes.

---

## References

- [R1] Next.js. “TypeScript.” https://nextjs.org/docs/app/building-your-application/configuring/typescript (accessed 2025-12-29)
- [R2] Next.js. “Environment Variables.” https://nextjs.org/docs/app/building-your-application/configuring/environment-variables (accessed 2025-12-29)
- [R3] Next.js. “Route Handlers.” https://nextjs.org/docs/app/building-your-application/routing/route-handlers (accessed 2025-12-29)
- [R4] Next.js. “Server Actions and Mutations.” https://nextjs.org/docs/app/building-your-application/data-fetching/server-actions-and-mutations (accessed 2025-12-29)
- [R5] Next.js. “ESLint.” https://nextjs.org/docs/app/building-your-application/configuring/eslint (accessed 2025-12-29)
- [R6] Next.js. “next.config.js: env.” https://nextjs.org/docs/app/api-reference/config/next-config-js/env (accessed 2025-12-29)

---

**Document ID**: `docs/NEXTJS_SET.md`
**Canonical URL**: `https://github.com/spesans/dev-ssot/blob/main/docs/NEXTJS_SET.md`
**License**: MIT
