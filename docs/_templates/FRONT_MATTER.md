---
title: Front Matter Guide
slug: front-matter-guide
summary: "YAML frontmatter requirements"
type: reference
tags: [template, frontmatter, ssot]
last_updated: 2025-12-17
---

# Front Matter Guide

```yaml
---
title: Topic Name
slug: topic-name
summary: "Short doc label (<50 chars)."
type: spec
tags: [tag1, tag2, tag3]
last_updated: 2025-12-17
---
```

## Usage Rules

- Apply this front matter to every "official document" (AGENTS, SSOT, PLAN, SKILL, specs, designs, procedures, AI reference topics, etc.).
- Every md under `/docs` or `/knowledge` must include it; `/drafts`, `/notes`, `/scratch`, and similar work logs are exempt.
- The repository root `README.md` is the lone exception even if it is official.
- Skip it for transient notes or drafts where title/slug/tags/summary would be meaningless noise.
- Keep `summary` concise (<=50 characters) and focused on the doc's label.
- Always include `type` using one of: `spec`, `guide`, `reference`, `policy`, `concept`.
- Close the front matter and insert exactly one blank line before the first heading (`#` or `##` etc.).
