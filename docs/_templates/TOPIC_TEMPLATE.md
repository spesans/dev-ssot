---
title: Topic Template
slug: topic-template
summary: "11-section SSOT topic template"
type: reference
tags: [template, ai-first, topic]
last_updated: 2025-12-17
---

# Topic Template

> Copy this file to create a new topic, then replace the frontmatter and this H1 with your topic title.

## Agent Contract

- **PURPOSE**:
  - [Central purpose that this topic defines]
- **USE_WHEN**:
  - [Specific situations when agents should reference this document]
- **DO_NOT_USE_WHEN**:
  - [Cases where this topic should NOT be applied]
- **PRIORITY**:
  - [Priority rules when content conflicts with other topics]
- **RELATED_TOPICS**:
  - [related-topic-slug-1]
  - [related-topic-slug-2]

---

## TL;DR

- **WHAT**: [One-sentence definition of this topic]
- **WHY**: [What value it provides / What problem it solves]
- **WHEN**: [Typical application scenarios]
- **HOW**: [Fundamental approach or pattern]
- **WATCH_OUT**: [Most critical pitfall to avoid]

---

## Canonical Definitions

> **NOTE**: Terminology definitions must **eliminate ambiguity**.
> Use the "Definition Section Template" from SECTION_TEMPLATE as needed.

### [Term 1]

**Definition**: [Clear, unambiguous definition (one sentence)]

**Scope**:
- **Includes**: [...]
- **Excludes**: [...]

**Related Concepts**:
- **Similar**: [...]
- **Contrast**: [...]
- **Contains**: [...]

**Example**:

```[language]
# Concrete example illustrating this term
[code or text example]
```

**Sources**: [R1]

### [Term 2]

[Continue with same structure]

---

## Core Patterns

> **NOTE**: Each pattern should be based on the "Pattern Section Template" from SECTION_TEMPLATE.

### Pattern: [Pattern Name]

**Intent**: [What problem does this pattern solve?]

**Context**: [Under what assumptions/situations should this be used?]

**Implementation**:

```[language]
# Complete, runnable code example
[code here]
```

**Key Principles**:
- [Principle 1]: [Why it matters]
- [Principle 2]: [Why it matters]

**Trade-offs**:
- ✅ **Advantages**: [Benefits]
- ⚠️ **Disadvantages**: [Drawbacks/constraints]
- 💡 **Alternatives**: [Other patterns to consider]

**Sources**: [R#]

---

## Decision Checklist

> **NOTE**: All important decisions should be converted to checklist items.
> Use the "Decision Checklist Item Template" from SECTION_TEMPLATE for individual items.

- [ ] **[Requirement/Constraint/Goal]**: [Specific condition] [R#]
  - **Verify**: [How to check this]
  - **Impact**: [What happens if not met]
  - **Mitigation**: [How to address if not met]

---

## Anti-patterns / Pitfalls

> **NOTE**: Make incorrect usage and common failures explicit.
> Use this as a detection hook for "what NOT to do".

### Anti-pattern: [Problematic Approach]

**Symptom**: [What state indicates this anti-pattern is present?]

**Why It Happens**: [Why is this tendency common?]

**Impact**:
- [Negative consequence 1]
- [Negative consequence 2]
- [Negative consequence 3]

**Solution**: [Which pattern/procedure should be used instead?]

**Example**:

```[language]
# ❌ Anti-pattern
[problematic code]

# ✅ Correct pattern
[better code]
```

**Sources**: [R#]

---

## Evaluation

> **NOTE**: Measurement and testing to determine if this topic is being "applied correctly".

### Metrics

**[Metric Name]**: [What does this measure?]
- **Why It Matters**: [Business or technical importance]
- **Target**: [Acceptable range/target value]
- **Measurement**: [How to measure this]
- **Tools**: [Tools to use]
- **Frequency**: [How often to measure]

**Sources**: [R#]

### Testing Strategies

**Unit Tests**:
- [Points to test]

**Integration Tests**:
- [Scenario-based tests]

**Performance Benchmarks**:
- [What conditions and what values to check]

### Success Criteria

- [ ] [Functional requirement 1 is met]
- [ ] [Performance target 2 is achieved]
- [ ] [Quality standard 3 is maintained]

---

## Update Log

- **YYYY-MM-DD** – [Summary of changes] (Author: [name])

---

## See Also

### Prerequisites
- [link-to-foundational-topic] – [Why this is a prerequisite for this topic]

### Related Topics
- [link-to-complementary-topic] – [How they complement each other]
- [link-to-alternative-approach] – [When to switch between them]

### Advanced / Platform-specific
- [link-to-advanced-topic] – [How to extend this]
- [link-to-platform-guide] – [Implementation differences on specific platforms]

---

## References

- [R1] Author, A. (Year). "Article Title." Publication Name. https://example.com/article (accessed YYYY-MM-DD)
- [R2] Organization. "Documentation Title." Official Docs. https://docs.example.com (accessed YYYY-MM-DD)
- [R3] Researcher, B. et al. (Year). "Research Paper Title." Conference/Journal. https://arxiv.org/... (accessed YYYY-MM-DD)
- [R4] Blogger, C. "Blog Post Title." Personal Blog. https://blog.example.com (accessed YYYY-MM-DD)

---

**Document ID**: `[directory]/[filename]`
**Canonical URL**: `https://github.com/spesans/dev-ssot/blob/main/[directory]/[filename].md`
**License**: MIT
