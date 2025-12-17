---
title: TypeScript Standard Set
slug: typescript-standard
summary: "TypeScript configuration SSOT for all projects"
type: spec
tags: [typescript, standards, linting, testing, zod, ssot]
last_updated: 2025-12-17
---

# Topic: TypeScript Standard Set

## Agent Contract

- **PURPOSE**:
  - Define the authoritative TypeScript toolchain and configuration for AI-first projects (compiler, linting, formatting, runtime validation, CI gates)
  - Make AI-generated code safe and deterministic by enforcing strict typing, type-aware linting, and runtime validation at IO boundaries
  - Provide copy-pasteable templates that match current tooling defaults (ESLint v9+ flat config, `typescript-eslint` meta package, `pnpm` via Corepack, Node.js LTS)
- **USE_WHEN**:
  - Creating or modernizing a TypeScript project (service, web app, CLI, agent, or library)
  - Setting up or reviewing `tsconfig*`, ESLint, Prettier, scripts, or CI for TypeScript
  - AI agents generate TypeScript code or configuration and need a deterministic standard
- **DO_NOT_USE_WHEN**:
  - Working in a non-TypeScript codebase
  - Documenting product/business logic (belongs in project-level docs/specs)
  - Throwaway prototypes where the team explicitly accepts reduced safety (must be recorded as a deviation)
- **PRIORITY**:
  - This document overrides project-local conventions when they conflict with the non-negotiables defined here
  - Deviations MUST be explicit, scoped, timeboxed, and documented (see “Deviation Protocol”)
- **NORMATIVE KEYWORDS**:
  - This document uses **MUST**, **SHOULD**, and **MAY** as defined in `docs/SSOT.md`
- **RELATED_TOPICS**:
  - ssot-guide
  - exec-plan
  - agents-readme
  - code-mcp
  - agent-skill

### Non-Negotiables (MUST)

- TypeScript `strict: true`
- ESLint v9+ **flat config** (`eslint.config.*`) as the canonical configuration
- **Type-aware linting** enabled for TypeScript sources (no-unsafe rules enforced)
- `pnpm` as the standard package manager (via Corepack) for commands, examples, and CI
- Runtime validation at IO boundaries using **Zod** (no `as Type` for external data)

### AI Directive Block (MUST)

```yaml
ai_directive:
  defaults:
    package_manager: pnpm
    node: "24"
    typescript: ">=5.9"
    eslint: ">=9 (flat config)"
    typescript_eslint: ">=8 (meta package)"
    prettier: ">=3"
    zod: ">=4"
  required_outputs:
    - tsconfig.base.json
    - eslint.config.mjs
    - prettier.config.cjs
    - package.json#scripts (lint/typecheck/test/format/check)
  invariants:
    - strict_typescript
    - typed_linting
    - zod_at_io_boundaries
    - no_type_assertions_for_external_data
```

### Deviation Protocol (MUST)

Any deviation from this SSOT MUST be recorded in the adopting repository (recommended: `/SSOT.md` or `/docs/SSOT.md`) using:

```yaml
deviation:
  topic: typescript-standard
  what: "<what is changed>"
  why: "<why the standard cannot be followed>"
  scope: "<files/packages affected>"
  timebox: "<end date or version>"
  alternatives_considered:
    - "<alternative 1>"
    - "<alternative 2>"
  approver: "<human approver>"
  decided_at: "YYYY-MM-DDTHH:MM:SSZ"
```

---

## TL;DR

- **WHAT**: A strict, 2025-compatible TypeScript standard for compiler settings, typed linting, formatting, runtime validation, scripts, and CI gates.
- **WHY**: Prevent “`any`-driven” production bugs and configuration drift, especially under AI-assisted code generation.
- **WHEN**: New repos, upgrades to ESLint v9+, or any time agents generate TypeScript/config files.
- **HOW**: Extend `tsconfig.base.json`, use ESLint flat config + `typescript-eslint` typed presets, run Prettier separately, validate IO with Zod, and enforce via CI.
- **WATCH_OUT**: `.eslintrc.*` does not auto-load on ESLint v9; mixing `pnpm`/`npm` examples causes agent drift; `response.json()` often yields `any` and must be sanitized to `unknown` before validation.

### Compatibility Matrix (MUST)

| Component | Standard | Notes |
|---|---|---|
| Node.js | 24 (LTS) | CI examples use Node 24; update when Active LTS changes |
| Package manager | `pnpm` (Corepack) | Examples and CI are `pnpm`-first; no mixed tooling |
| TypeScript | 5.9+ | Uses `verbatimModuleSyntax`; keep modern module behavior |
| ESLint | 9.x | Flat config (`eslint.config.*`) is canonical |
| `typescript-eslint` | 8.x | Use the `typescript-eslint` meta package and typed presets |
| Prettier | 3.x | Formatting handled by Prettier; ESLint only disables conflicts |
| Zod | 4.x | Required for runtime validation at IO boundaries |
| Test runner | Vitest (preferred) | Jest allowed only for legacy/migration |

### Package Manager Policy (MUST)

- All commands in this document use `pnpm`.
- If an adopting repository uses `npm` or `yarn`, it MUST provide a short translation table in its own SSOT and document the deviation.

---

## Canonical Definitions

### Flat Config (ESLint)

**Definition**: ESLint’s modern configuration system using `eslint.config.*` (an exported config array/object), which is the default in ESLint v9+.

**Scope**:
- **Includes**: `eslint.config.js|mjs|cjs`, `ignores` in config, composition by importing config objects/arrays
- **Excludes**: legacy `.eslintrc.*` auto-discovery behavior

### Type-Aware Linting

**Definition**: ESLint rules that require TypeScript type information (typed linting) to detect unsafe usage of `any`, promises, and other type-dependent issues.

**Scope**:
- **Includes**: `typescript-eslint` “TypeChecked” presets and rules like `no-unsafe-*`
- **Excludes**: linting that only parses syntax without type info

### IO Boundary

**Definition**: The boundary where untrusted/external data enters the system and MUST be validated before being treated as typed.

**Scope**:
- **Includes**: HTTP clients/servers, webhooks, queues, DB adapters, file IO, LLM outputs, env vars, CLI args
- **Excludes**: internal function calls between already-validated modules

### Type Sanitization

**Definition**: Converting `any`-typed external values into `unknown` before validation to stop type pollution and satisfy typed lint rules.

**Example**:

```ts validate
export async function readJsonUnknown(response: Response): Promise<unknown> {
  const data: unknown = await response.json();
  return data;
}
```

### Runtime Validation

**Definition**: Validation performed at runtime (not compile time) that proves external data conforms to an expected schema.

**Scope**:
- **Includes**: Zod `.parse()` / `.safeParse()` at IO boundaries
- **Excludes**: `as Type` assertions used as a substitute for validation

---

## Core Patterns

### Pattern: Repository Bootstrap (Single-Package)

**Intent**: Create a new TypeScript repo that immediately satisfies lint/typecheck/format/test/CI gates.

**Implementation**:

```bash
corepack enable
pnpm init

pnpm add zod
pnpm add -D typescript @types/node eslint @eslint/js typescript-eslint eslint-config-prettier prettier vitest tsx
```

**Key Principles**:
- Use Corepack so CI and dev machines resolve the same `pnpm` version.
- Install `typescript-eslint` (meta package) instead of separate parser/plugin packages.

---

### Pattern: TypeScript Compiler Baseline (`tsconfig.base.json`)

**Intent**: Provide an org-wide baseline of strictness and hygiene flags, leaving runtime-specific options to profiles.

#### `tsconfig.base.json` (MUST)

```jsonc
{
  "compilerOptions": {
    "strict": true,

    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "forceConsistentCasingInFileNames": true,
    "useUnknownInCatchVariables": true,

    "verbatimModuleSyntax": true,
    "noEmitOnError": true
  }
}
```

**Notes**:
- `verbatimModuleSyntax` is the modern default for predictable import/export behavior in TS 5+.
- Do NOT put environment-specific settings (`target`, `lib`, `module`, `moduleResolution`, `jsx`) in the base; profiles own those.

**Progressive Safety Options (SHOULD for new projects)**:
- `noImplicitOverride: true`
- `exactOptionalPropertyTypes: true`

**Maximum Safety Options (MAY; likely breaking)**:
- `noUncheckedIndexedAccess: true`
- `noPropertyAccessFromIndexSignature: true`

---

### Pattern: TypeScript Profiles (Node Service vs Web App vs Library)

**Intent**: Prevent “one tsconfig fits all” ambiguity by selecting an explicit profile.

**Decision Guide**:
- Choose **Node Service Profile** if Node runs the emitted JS (build output).
- Choose **Web App Profile** if a bundler runs the app (Vite/Next/etc) and `tsc` is typecheck-only.
- Choose **Library Profile** if you publish a package (needs declarations and exports discipline).

#### Node Service Profile (`tsconfig.json`)

```jsonc
{
  "extends": "./tsconfig.base.json",
  "compilerOptions": {
    "target": "ES2024",
    "lib": ["ES2024"],
    "module": "NodeNext",
    "moduleResolution": "NodeNext",

    "rootDir": "./src",
    "outDir": "./dist",

    "types": ["node"],
    "esModuleInterop": true,
    "resolveJsonModule": true
  },
  "include": ["src/**/*.ts", "tests/**/*.ts"],
  "exclude": ["dist", "node_modules"]
}
```

**Node ESM import specifiers (MUST)**:
- If you compile to Node ESM, your runtime import specifiers MUST be compatible with Node (usually `.js` extensions in source).
- If your TypeScript version supports it, you MAY use `rewriteRelativeImportExtensions` to reduce manual `.js` specifiers (document the choice).

#### Web App Profile (`tsconfig.json`)

```jsonc
{
  "extends": "./tsconfig.base.json",
  "compilerOptions": {
    "target": "ES2024",
    "lib": ["ES2024", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "moduleResolution": "Bundler",

    "jsx": "react-jsx",
    "noEmit": true,

    "resolveJsonModule": true
  },
  "include": ["src/**/*.ts", "src/**/*.tsx", "tests/**/*.ts"],
  "exclude": ["dist", "node_modules"]
}
```

#### Library Profile (Declarations + Exports Discipline)

**Baseline (SHOULD)**:
- Emit `.d.ts` files into `dist/types` (or equivalent) and treat them as part of your public contract.
- Prefer **ESM-first** exports; avoid dual-package complexity unless required.

Example `tsconfig.build.json` (types only):

```jsonc
{
  "extends": "./tsconfig.base.json",
  "compilerOptions": {
    "declaration": true,
    "declarationMap": true,
    "emitDeclarationOnly": true,
    "outDir": "./dist/types",

    "stripInternal": true,
    "types": ["node"]
  },
  "include": ["src/**/*.ts"],
  "exclude": ["dist", "node_modules", "**/*.test.ts", "**/*.spec.ts"]
}
```

Example `package.json` exports (informative):

```json
{
  "name": "your-lib",
  "type": "module",
  "exports": {
    ".": {
      "types": "./dist/types/index.d.ts",
      "default": "./dist/index.js"
    }
  }
}
```

---

### Pattern: ESLint (ESLint v9+ Flat Config) + `typescript-eslint`

**Intent**: Enforce bug-preventing rules (including `no-unsafe-*`) and keep config compatible with ESLint v9 defaults.

#### Install (MUST)

```bash
pnpm add -D eslint @eslint/js typescript-eslint eslint-config-prettier prettier
```

#### Canonical Config: `eslint.config.mjs` (MUST)

```js
// @ts-check

import eslintJs from '@eslint/js';
import tseslint from 'typescript-eslint';
import prettierConfig from 'eslint-config-prettier';

export default [
  { ignores: ['**/dist/**', '**/node_modules/**', '**/coverage/**'] },

  eslintJs.configs.recommended,
  ...tseslint.configs.recommendedTypeChecked,
  ...tseslint.configs.stylisticTypeChecked,
  prettierConfig,

  {
    languageOptions: {
      parserOptions: {
        projectService: true
      }
    },
    rules: {
      '@typescript-eslint/no-explicit-any': 'error',
      '@typescript-eslint/no-non-null-assertion': 'error',
      '@typescript-eslint/consistent-type-definitions': ['error', 'type'],

      '@typescript-eslint/consistent-type-imports': [
        'error',
        { fixStyle: 'inline-type-imports' }
      ],

      '@typescript-eslint/ban-ts-comment': [
        'error',
        {
          'ts-expect-error': 'allow-with-description',
          'ts-ignore': true,
          'ts-nocheck': true,
          minimumDescriptionLength: 10
        }
      ]
    }
  },

  {
    files: ['**/*.config.*', 'scripts/**/*', '**/*.js', '**/*.cjs', '**/*.mjs'],
    ...tseslint.configs.disableTypeChecked
  }
];
```

**Notes**:
- `.eslintrc.*` is legacy. Use it only as a migration bridge and plan removal.
- `projectService: true` is the default recommendation for stable typed linting, especially in monorepos.

#### Migration Note (legacy `.eslintrc.*` → flat config)

- Convert `.eslintrc.*` to `eslint.config.*`.
- Replace `extends` chains with imported config objects and array composition.
- Replace `.eslintignore` with `ignores` in config (or keep `.eslintignore` only if you intentionally rely on it and document the deviation).

---

### Pattern: Prettier (Formatting)

**Intent**: Ensure consistent formatting without letting ESLint become a formatter.

#### `prettier.config.cjs`

```js
/** @type {import('prettier').Config} */
module.exports = {
  semi: true,
  trailingComma: 'all',
  singleQuote: true,
  printWidth: 100,
  tabWidth: 2
};
```

#### `.prettierignore`

```gitignore
dist
coverage
node_modules
```

---

### Pattern: Runtime Validation at IO Boundaries (Zod v4)

**Intent**: Make external data safe by validating it before it becomes typed.

**Rules (MUST)**:
- No `as SomeType` for external data (HTTP, DB, env, webhooks, queues, LLM outputs).
- Convert `any` to `unknown` at the boundary before validation (“type sanitization”).
- Derive TypeScript types from schemas (`z.infer`), not the other way around.

#### Boundary Helpers (recommended)

```ts validate
import { z } from 'zod';

export async function readJsonUnknown(response: Response): Promise<unknown> {
  const data: unknown = await response.json();
  return data;
}

export function parseWith<T>(schema: z.ZodType<T>, data: unknown): T {
  return schema.parse(data);
}
```

#### Example: Validating an API Response

```ts validate
import { z } from 'zod';

async function readJsonUnknown(response: Response): Promise<unknown> {
  const data: unknown = await response.json();
  return data;
}

function parseWith<T>(schema: z.ZodType<T>, data: unknown): T {
  return schema.parse(data);
}

const UserSchema = z.object({
  id: z.string(),
  name: z.string(),
  email: z.string().email().optional()
});

export type User = z.infer<typeof UserSchema>;

export async function decodeUser(response: Response): Promise<User> {
  const data = await readJsonUnknown(response);
  return parseWith(UserSchema, data);
}
```

---

### Pattern: Standard Scripts (`pnpm`) (MUST)

**Intent**: Provide a single, consistent command surface for humans and agents.

```json
{
  "scripts": {
    "lint": "eslint .",
    "lint:fix": "eslint . --fix",
    "typecheck": "tsc -p tsconfig.json --noEmit",
    "test": "vitest",
    "format": "prettier --write .",
    "format:check": "prettier --check .",
    "check": "pnpm run lint && pnpm run typecheck && pnpm run test && pnpm run format:check"
  }
}
```

**Notes**:
- `check` is the CI entry point (one command, deterministic).

---

### Pattern: CI Gates (GitHub Actions, Node 24 + pnpm)

**Intent**: Enforce lint/typecheck/test/format gates before merge.

```yaml
name: TypeScript CI

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '24'
          cache: 'pnpm'

      - run: corepack enable
      - run: pnpm install --frozen-lockfile

      - run: pnpm run check
```

**Security note (SHOULD)**:
- Pin GitHub Actions to commit SHAs for supply-chain safety (see `docs/SSOT.md`).

---

### Pattern: Monorepo Notes (pnpm workspaces)

**Intent**: Keep typed linting and builds stable as the repo scales.

**Guidelines (SHOULD)**:
- Place `tsconfig.base.json`, `eslint.config.mjs`, and `prettier.config.cjs` at the workspace root.
- Prefer `projectService: true` over `parserOptions.project` globs.
- Root scripts SHOULD use recursive execution:

```json
{
  "scripts": {
    "check": "pnpm -r run check"
  }
}
```

---

### Pattern: Exceptions (Type Assertions, `any`, and Suppressions)

**Intent**: Provide safe, auditable escape hatches without eroding the standard.

**Allowed (MAY, with justification)**:
- `as const` for literal inference
- DOM narrowing for APIs that are intentionally generic
- Local workarounds for incorrect third-party typings

**Forbidden (MUST NOT)**:
- `as SomeType` for unvalidated external data
- `@ts-ignore` and `@ts-nocheck`

**Standard format for a rule suppression (MUST)**:

```ts validate
declare function thirdPartyCall(): unknown;

// eslint-disable-next-line @typescript-eslint/no-explicit-any -- Third-party typings are wrong (vendor issue #12345, remove after upgrade)
export const unsafeValue: any = thirdPartyCall();
```

**Standard format for type sanitization (MUST)**:

```ts validate
export async function readJsonUnknown(response: Response): Promise<unknown> {
  const data: unknown = await response.json(); // sanitize external any -> unknown before validation
  return data;
}
```

---

### Pattern: SSOT Self-Validation (This Document)

**Intent**: Ensure the SSOT’s code snippets remain executable as tooling evolves.

**Contract**:
- Code blocks marked with `validate` in the fence info string (e.g. ```` ```ts validate ````) MUST pass `tsc` + `eslint` under a temporary project.
- Validated TypeScript fences SHOULD be standalone (no relative imports) unless the validation workflow explicitly supports multi-file extraction.
- JSON blocks MUST be valid JSON (no comments). Use `jsonc` fences when comments are present.
- YAML blocks MUST be valid YAML.

**Sample workflow (informative)**:

```yaml
name: Validate TypeScript Standard Document

on:
  pull_request:
    paths:
      - 'docs/TYPESCRIPT_SET.md'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '24'
          cache: 'pnpm'

      - run: corepack enable

      - name: Validate fenced examples
        run: |
          set -euo pipefail

          tmpdir="$(mktemp -d)"
          cp docs/TYPESCRIPT_SET.md "$tmpdir/doc.md"
          cd "$tmpdir"

          cat > package.json << 'EOF'
          {
            "name": "typescript-standard-validate",
            "private": true,
            "type": "module"
          }
          EOF

          pnpm add -D typescript @types/node eslint @eslint/js typescript-eslint eslint-config-prettier prettier zod

          node --input-type=module << 'NODE'
          import { readFileSync, mkdirSync, writeFileSync } from 'node:fs';
          import { join } from 'node:path';

          const md = readFileSync('doc.md', 'utf8');
          const lines = md.split('\n');

          const outDir = 'examples';
          mkdirSync(outDir, { recursive: true });

          let inFence = false;
          let fenceLang = '';
          let buffer = [];
          let exampleIndex = 0;

          function flushFence() {
            if (!inFence) return;
            const langParts = fenceLang.trim().split(/\\s+/);
            const lang = (langParts[0] ?? '').toLowerCase();
            const wantsValidate = langParts.includes('validate');
            if (wantsValidate && (lang === 'ts' || lang === 'typescript')) {
              exampleIndex += 1;
              const filename = join(outDir, `example-${exampleIndex}.ts`);
              writeFileSync(filename, buffer.join('\\n'), 'utf8');
            }
            inFence = false;
            fenceLang = '';
            buffer = [];
          }

          for (const line of lines) {
            const fenceMatch = line.match(/^```(.*)$/);
            if (fenceMatch) {
              if (!inFence) {
                inFence = true;
                fenceLang = fenceMatch[1] ?? '';
                buffer = [];
              } else {
                flushFence();
              }
              continue;
            }
            if (inFence) buffer.push(line);
          }
          flushFence();

          if (exampleIndex === 0) {
            console.error('No validated TypeScript code fences found.');
            process.exit(1);
          }
          NODE

          cat > tsconfig.base.json << 'EOF'
          {
            "compilerOptions": {
              "strict": true,
              "noUnusedLocals": true,
              "noUnusedParameters": true,
              "noImplicitReturns": true,
              "noFallthroughCasesInSwitch": true,
              "forceConsistentCasingInFileNames": true,
              "useUnknownInCatchVariables": true,
              "verbatimModuleSyntax": true,
              "noEmitOnError": true
            }
          }
          EOF

          cat > tsconfig.json << 'EOF'
          {
            "extends": "./tsconfig.base.json",
            "compilerOptions": {
              "target": "ES2024",
              "lib": ["ES2024"],
              "module": "NodeNext",
              "moduleResolution": "NodeNext",
              "types": ["node"],
              "noEmit": true
            },
            "include": ["examples/**/*.ts"]
          }
          EOF

          cat > eslint.config.mjs << 'EOF'
          import eslintJs from '@eslint/js';
          import tseslint from 'typescript-eslint';
          import prettierConfig from 'eslint-config-prettier';

          export default [
            { ignores: ['**/node_modules/**'] },
            eslintJs.configs.recommended,
            ...tseslint.configs.recommendedTypeChecked,
            ...tseslint.configs.stylisticTypeChecked,
            prettierConfig,
            {
              languageOptions: { parserOptions: { projectService: true } },
              rules: {
                '@typescript-eslint/no-explicit-any': 'error',
                '@typescript-eslint/no-non-null-assertion': 'error',
                '@typescript-eslint/consistent-type-definitions': ['error', 'type']
              }
            }
          ];
          EOF

          pnpm exec tsc -p tsconfig.json
          pnpm exec eslint examples
```

---

## Decision Checklist

- [ ] **Toolchain matches the Compatibility Matrix**: Node 24, ESLint 9 (flat config), `typescript-eslint` 8, Zod 4. [R1]
  - **Verify**: `node -v`, `pnpm -v`, `pnpm list eslint typescript-eslint zod`
  - **Impact**: older tooling breaks templates or silently disables linting
  - **Mitigation**: upgrade tooling or record a deviation with a timebox

- [ ] **ESLint uses flat config and typed linting**: `eslint.config.*` exists and typed rules run on `.ts/.tsx`. [R3]
  - **Verify**: `pnpm exec eslint .` and confirm `eslint.config.*` is loaded
  - **Impact**: unsafe `any` usage slips through
  - **Mitigation**: adopt `eslint.config.mjs` + `recommendedTypeChecked`

- [ ] **IO boundaries validate external data with Zod**. [R6]
  - **Verify**: boundary modules parse `unknown` with `.parse()`/`.safeParse()`
  - **Impact**: runtime bugs and security issues from trusting unvalidated data
  - **Mitigation**: add schemas and boundary helpers; forbid `as Type` for external inputs

- [ ] **CI enforces `pnpm run check`**. [R7]
  - **Verify**: GitHub Actions runs on PRs and blocks merge on failure
  - **Impact**: style/type/test drift
  - **Mitigation**: add `TypeScript CI` workflow and branch protections

- [ ] **Exceptions are documented and local**.
  - **Verify**: suppressions have justification and scope is minimal
  - **Impact**: standards decay into “disable until it passes”
  - **Mitigation**: enforce suppression format and review deviations

---

## Anti-patterns / Pitfalls

### Anti-pattern: Relying on `.eslintrc.*` with ESLint v9+

**Symptom**: ESLint runs but ignores your rules/config, or fails to find config.

**Why It Happens**: ESLint v9 defaults to flat config and does not auto-load legacy config files.

**Solution**: Use `eslint.config.*` and compose configs via imports.

### Anti-pattern: Mixing `pnpm` policy with `npm` examples

**Symptom**: Agents generate `npm ci`/`npm run` while the repo uses `pnpm`, causing CI and local commands to diverge.

**Solution**: Keep SSOT examples `pnpm`-only and provide a repo-local translation if needed.

### Anti-pattern: Passing `any` from `response.json()` directly into Zod

**Symptom**: Typed lint rules (`no-unsafe-*`) fire, or unsafe data leaks into the codebase.

**Bad**:

```ts
type UnsafeResponse = { json(): Promise<any> };
declare const response: UnsafeResponse;
declare const Schema: { parse: (value: unknown) => unknown };

async function bad(): Promise<void> {
  const data = await response.json(); // typically `any`
  Schema.parse(data);
}
```

**Good**:

```ts
type UnsafeResponse = { json(): Promise<any> };
declare const response: UnsafeResponse;
declare const Schema: { parse: (value: unknown) => unknown };

async function good(): Promise<void> {
  const data = (await response.json()) as unknown;
  Schema.parse(data);
}
```

### Anti-pattern: Swallowing CI failures

**Symptom**: CI “passes” even when lint/typecheck fail (e.g., `|| true`).

**Solution**: CI MUST fail on `eslint`/`tsc` errors; do not mask failures.

---

## Evaluation

### Success Criteria

- [ ] `pnpm run check` passes on a clean checkout
- [ ] CI blocks merges when lint/typecheck/test/format fail
- [ ] IO boundary modules validate external inputs with Zod
- [ ] Deviations are documented with scope + timebox

### Testing Strategy

- **Unit**: Validate schemas and boundary helpers (`safeParse` failure cases included)
- **Integration**: Validate inbound/outbound API payloads at adapters
- **CI**: Run `pnpm run check` on every PR

---

## Update Log

- **2025-12-17T00:00:00Z** – Major revision: updated to ESLint v9 flat config, `typescript-eslint` meta package + typed presets, Node 24 + pnpm-first CI, clarified tsconfig profiles (`verbatimModuleSyntax`), added IO boundary type-sanitization pattern, and fixed SSOT self-validation guidance. (Author: SSOT Admin)
- **2025-11-24T00:00:00Z** – Initial TypeScript standard set published. (Author: SSOT Admin)

---

## See Also

### Prerequisites

- [`docs/SSOT.md`](./SSOT.md) – Normative keywords, governance, and precedence rules.

### Related Topics

- [`docs/README_AGENTS.md`](./README_AGENTS.md) – How to structure repo-level instructions for humans and agents.
- [`docs/EXEC_PLAN.md`](./EXEC_PLAN.md) – Planning methodology for multi-step changes and validations.

---

## References

- [R1] Node.js. “Releases.” https://nodejs.org/en/about/releases/ (accessed 2025-12-17)
- [R2] TypeScript. “TSConfig Reference.” https://www.typescriptlang.org/tsconfig (accessed 2025-12-17)
- [R3] ESLint. “Configure ESLint.” https://eslint.org/docs/latest/use/configure/ (accessed 2025-12-17)
- [R4] typescript-eslint. “Documentation.” https://typescript-eslint.io/ (accessed 2025-12-17)
- [R5] Prettier. “Configuration.” https://prettier.io/docs/en/configuration.html (accessed 2025-12-17)
- [R6] Zod. “Documentation.” https://zod.dev/ (accessed 2025-12-17)
- [R7] pnpm. “Documentation.” https://pnpm.io/ (accessed 2025-12-17)
- [R8] Vitest. “Guide.” https://vitest.dev/guide/ (accessed 2025-12-17)

---

**Document ID**: `docs/TYPESCRIPT_SET.md`
**Canonical URL**: `https://github.com/artificial-intelligence-first/ssot/blob/main/docs/TYPESCRIPT_SET.md`
**License**: MIT
