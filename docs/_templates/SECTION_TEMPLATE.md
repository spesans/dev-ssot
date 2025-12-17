---
title: Section Templates
slug: section-templates
summary: "Section Templates"
type: reference
tags: [template, ai-first]
last_updated: YYYY-MM-DD
---

# Section Templates

> **NOTE FOR AI AGENTS**:
> - This file defines **section structure templates**.
> - Placeholders ([like this]) and pseudo-code in this file should NOT be treated as actual domain knowledge.
> - Use them only as scaffolding when generating content.

Use these templates when adding new sections to existing topic documents.

---

## Pattern Section Template

```markdown
### Pattern: [Pattern Name]

**Intent**: [One sentence describing what problem this solves]

**Context**: [When and why you would use this pattern]

**Implementation**:

​```[language]
# Complete, runnable example
[code here]
​```

**Key Principles**:
- [Principle 1]: [Explanation and rationale]
- [Principle 2]: [Explanation and rationale]

**Trade-offs**:
- ✅ **Advantages**: [Benefits]
- ⚠️ **Disadvantages**: [Limitations]
- 💡 **Alternatives**: [Other approaches to consider]

**Sources**: [R#]
```

---

## Anti-pattern Section Template

```markdown
### Anti-pattern: [Problematic Approach]

**Symptom**: [How you recognize this problem is occurring]

**Why It Happens**: [Common reasons developers fall into this trap]

**Impact**:
- [Negative consequence 1]
- [Negative consequence 2]
- [Negative consequence 3]

**Solution**: [Correct approach to use instead]

**Example**:

​```[language]
# ❌ Anti-pattern
[problematic code]

# ✅ Correct pattern
[better code]
​```

**Sources**: [R#]
```

---

## Definition Section Template

```markdown
### [Term or Concept]

**Definition**: [Precise, unambiguous definition in one sentence]

**Scope**:
- **Includes**: [What falls within this definition]
- **Excludes**: [What is outside this definition]

**Related Concepts**:
- **Similar**: [Related but distinct concepts]
- **Contrast**: [Opposite or alternative concepts]

**Example**:

​```[language]
# Concrete example illustrating the concept
[code or text example]
​```

**Sources**: [R#]
```

---

## Decision Checklist Item Template

```markdown
- [ ] **[Requirement/Constraint/Goal]**: [Specific condition] [R#]
  - **Verify**: [How to check if this is true]
  - **Impact**: [What happens if not met]
  - **Mitigation**: [How to address if not met]
```

---

## Evaluation Metric Template

```markdown
**[Metric Name]**: [What this measures]
- **Why It Matters**: [Business or technical importance]
- **Target**: [Acceptable threshold or range]
- **Measurement**: [How to calculate or obtain this metric]
- **Tools**: [Software or methods to use]
- **Frequency**: [How often to measure]

**Sources**: [R#]
```

---

## Case Study Template

```markdown
### Case Study: [Organization or Project Name]

**Context**: [Background and situation]

**Challenge**: [Problem they faced]

**Approach**: [How they applied this pattern/topic]

**Results**:
- [Outcome 1 with metrics if available]
- [Outcome 2 with metrics if available]
- [Outcome 3 with metrics if available]

**Lessons Learned**:
- [Key insight 1]
- [Key insight 2]

**Sources**: [R#]
```

---

## Code Example Template

```markdown
### Example: [Descriptive Title]

**Scenario**: [What this example demonstrates]

**Code**:

​```[language]
# [Brief comment about what this does]
[complete, runnable code]
​```

**Explanation**:
1. [Step 1]: [What this part does and why]
2. [Step 2]: [What this part does and why]
3. [Step 3]: [What this part does and why]

**Output**:
​```
[Expected output or result]
​```

**Variations**:
- [Variation 1]: [How to adapt for different use case]
- [Variation 2]: [How to adapt for different use case]

**Sources**: [R#]
```

---

## Comparison Table Template

```markdown
### Comparison: [Thing A] vs [Thing B]

| Aspect | [Thing A] | [Thing B] |
|--------|-----------|-----------|
| **Purpose** | [Primary use case] | [Primary use case] |
| **Strengths** | [Key advantages] | [Key advantages] |
| **Weaknesses** | [Limitations] | [Limitations] |
| **Performance** | [Metrics] | [Metrics] |
| **Complexity** | [Implementation difficulty] | [Implementation difficulty] |
| **Best For** | [Ideal scenarios] | [Ideal scenarios] |

**Decision Guide**:
- Choose [Thing A] when: [Conditions]
- Choose [Thing B] when: [Conditions]

**Sources**: [R#]
```

---

## Troubleshooting Section Template

```markdown
### Troubleshooting: [Problem Description]

**Symptoms**:
- [Observable issue 1]
- [Observable issue 2]

**Common Causes**:
1. **[Cause 1]**: [Explanation]
   - **Check**: [Diagnostic step]
   - **Fix**: [Solution]

2. **[Cause 2]**: [Explanation]
   - **Check**: [Diagnostic step]
   - **Fix**: [Solution]

**Debugging Steps**:
1. [First thing to check]
2. [Second thing to check]
3. [Third thing to check]

**Prevention**: [How to avoid this issue in the future]

**Sources**: [R#]
```

---

## Best Practice Template

```markdown
### Best Practice: [Practice Name]

**Principle**: [Core idea in one sentence]

**Rationale**: [Why this is important]

**Implementation**:

​```[language]
# ✅ Recommended approach
[code example]
​```

**Benefits**:
- [Benefit 1]
- [Benefit 2]
- [Benefit 3]

**Common Violations**:

​```[language]
# ❌ Don't do this
[anti-pattern code]
​```

**Sources**: [R#]
```

---

## Migration Guide Template

```markdown
### Migration: [From Old Approach] → [To New Approach]

**Why Migrate**: [Motivation for changing]

**Breaking Changes**:
- [Change 1 and impact]
- [Change 2 and impact]

**Migration Steps**:

1. **[Step 1]**: [What to do]
   ​```[language]
   # Before
   [old code]

   # After
   [new code]
   ​```

2. **[Step 2]**: [What to do]
   ​```[language]
   # Before
   [old code]

   # After
   [new code]
   ​```

**Verification**:
- [ ] [Test 1 passes]
- [ ] [Test 2 passes]
- [ ] [Metric 3 is maintained]

**Rollback Plan**: [How to revert if issues occur]

**Sources**: [R#]
```

---

## Usage Notes

1. **Copy the appropriate template** from above
2. **Replace all [placeholders]** with actual content
3. **Add to the appropriate section** of the target document
4. **Assign next available reference ID** [R#]
5. **Add full citation** to References section
6. **Update frontmatter** (`last_updated`, add to `sources` array)
7. **Add entry to Update Log**
8. **Commit** with descriptive message

**See also**: `_meta/CONTRIBUTING.md` for full workflow guidance
