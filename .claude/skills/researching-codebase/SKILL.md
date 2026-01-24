---
name: researching-codebase
description: Investigates codebase before planning. Use before any non-trivial implementation task to gather context in isolation.
context: fork
agent: Explore
---

# Codebase Research (ACE-FCA)

Gathers codebase context **in isolation** before planning. Prevents search
artifacts from polluting main context.

## When to Use

- Before planning non-trivial implementations
- When unfamiliar with relevant codebase areas
- Before architectural decisions

## Workflow

1. **Explore codebase** - Investigate architecture, patterns, constraints
2. **Identify scope** - Determine relevant areas based on findings
3. **Distill** - Return structured summary using format below

## Output Format

Follow ACE-FCA quality equation: **Correct + Complete + Minimal noise**

Structure output as:
- **Key Files**: Relevant files with purpose
- **Patterns**: Existing conventions to follow
- **Constraints**: Dependencies, limitations found

See `.claude/rules/context-management.md` and `.claude/rules/core-principles.md`.
