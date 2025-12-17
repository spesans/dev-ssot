# SSOT for AI-First Development

**Single Source of Truth for AI-First Development**

A centralized repository managing structured knowledge documents optimized for both AI agents and human developers.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue.svg)](https://spesans.github.io/dev-ssot/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/spesans/dev-ssot/pulls)

---

## Overview

This repository establishes a **Single Source of Truth (SSOT)** for AI-First Development, providing canonical documentation that serves as the authoritative reference for both autonomous agents and development teams.

Each document follows a rigorous **11-section structure** designed to eliminate ambiguity and ensure consistency across all knowledge artifacts.

### Key Features

- **Vendor-Neutral Specifications** - Works with any AI model (Claude, GPT, Gemini, etc.)
- **Machine-Readable Structure** - Optimized for AI agent consumption
- **Human-Friendly Documentation** - Clear explanations with practical examples
- **Living Documents** - Continuously updated with timestamps and change logs

---

## Quick Start

```bash
# Clone the repository
git clone https://github.com/spesans/dev-ssot.git
cd dev-ssot

# Install docs dependencies
pip install -r requirements-docs.txt

# Serve docs locally
mkdocs serve
```

### Create a New Topic

```bash
# Copy the template
cp docs/_templates/TOPIC_TEMPLATE.md docs/YOUR_TOPIC.md

# Edit frontmatter and content
# Follow the 11-section structure
```

---

## Core Documents

| Document | Description | Type |
|:---------|:------------|:----:|
| [**SSOT.md**](./docs/SSOT.md) | Governance guide for Single Source of Truth principles | Guide |
| [**AGENT_SKILL.md**](./docs/AGENT_SKILL.md) | Universal specification for agent skills | Spec |
| [**CODE_MCP.md**](./docs/CODE_MCP.md) | Model Context Protocol implementation guide | Reference |
| [**EXEC_PLAN.md**](./docs/EXEC_PLAN.md) | AI-driven task planning methodology | Spec |
| [**TYPESCRIPT_SET.md**](./docs/TYPESCRIPT_SET.md) | TypeScript configuration standards | Spec |
| [**README_AGENTS.md**](./docs/README_AGENTS.md) | Documentation patterns for AI-First repos | Guide |

---

## Repository Structure

```
dev-ssot/
├── docs/                           # Core documentation
│   ├── SSOT.md                    # Governance guide
│   ├── AGENT_SKILL.md             # Universal agent skill specification
│   ├── CODE_MCP.md                # MCP implementation guide
│   ├── EXEC_PLAN.md               # ExecPlan methodology
│   ├── TYPESCRIPT_SET.md          # TypeScript standards
│   ├── README_AGENTS.md           # Documentation patterns
│   └── _templates/                # Document templates
│       ├── TOPIC_TEMPLATE.md      # Standard 11-section structure
│       ├── SECTION_TEMPLATE.md    # Reusable section patterns
│       └── FRONT_MATTER.md        # Metadata requirements
│
├── AGENTS.md                       # Agent catalog for this repo
├── README.md                       # This file
├── mkdocs.yml                      # Documentation site config
└── LICENSE                         # MIT License
```

---

## Document Architecture

### The 11-Section Structure

Every official document follows this standardized architecture:

| # | Section | Purpose |
|:-:|:--------|:--------|
| 1 | **Frontmatter** | YAML metadata (`title`, `slug`, `tags`, `type`, `last_updated`) |
| 2 | **Agent Contract** | Operational boundaries, priorities, and use conditions |
| 3 | **TL;DR** | Executive summary: What, Why, When, How, Watch Out |
| 4 | **Canonical Definitions** | Unambiguous terminology with scope boundaries |
| 5 | **Core Patterns** | Implementation approaches with trade-offs |
| 6 | **Decision Checklist** | Verification criteria and validation points |
| 7 | **Anti-patterns** | Common pitfalls and what to avoid |
| 8 | **Evaluation** | Metrics, testing strategies, success criteria |
| 9 | **Update Log** | Timestamped change history with attribution |
| 10 | **See Also** | Navigation to prerequisites and related topics |
| 11 | **References** | Authoritative sources with access dates |

### Document Types

| Type | Description |
|:-----|:------------|
| `spec` | Technical specification with strict requirements |
| `guide` | Implementation guidance with flexibility |
| `reference` | Reference material for lookup |
| `policy` | Governance or procedural documentation |
| `concept` | Conceptual explanation of ideas |

---

## For AI Agents

This repository is designed for AI agent consumption. Key points:

```yaml
# Agent Configuration Reference
standards:
  - Follow the 11-section structure for all documentation
  - Reference SSOT.md for canonical definitions
  - Use AGENTS.md for capability routing

priorities:
  - SSOT.md > README.md when definitions conflict
  - Implementation must match specifications
  - Update living sections (Progress, Decisions, Outcomes) in real-time

  constraints:
    - Never hallucinate definitions not in SSOT
    - Always validate external data (see TYPESCRIPT_SET.md)
    - Maintain timestamps in ISO 8601 format
```

See [AGENTS.md](./AGENTS.md) for the full agent catalog and routing rules.

---

## Contributing

### Submission Process

1. **Fork** the repository
2. **Create** a topic branch: `git checkout -b topic/your-topic-name`
3. **Apply** the [TOPIC_TEMPLATE.md](./docs/_templates/TOPIC_TEMPLATE.md) structure
4. **Validate** against quality requirements
5. **Submit** a pull request with detailed description

### Quality Checklist

- [ ] All 11 sections present and populated
- [ ] No placeholder text remaining
- [ ] Definitions eliminate ambiguity
- [ ] Code examples are executable
- [ ] References include access dates
- [ ] Update Log entry added

---

## Governance

| Activity | Frequency | Responsibility |
|:---------|:----------|:---------------|
| Content review | Monthly | Document owners |
| Reference validation | Quarterly | Automation tools |
| Structure updates | Semi-annually | Architecture team |
| Template evolution | As needed | Community consensus |

---

## Related Links

- [Documentation Site](https://spesans.github.io/dev-ssot/)
- [AGENTS.md Specification](https://agents.md)
- [Model Context Protocol](https://modelcontextprotocol.io/)

---

## License

MIT License - See [LICENSE](./LICENSE) for full terms.

---

**Maintained by**: SpeSan | **Last Updated**: 2025-12-17
