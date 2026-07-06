---
name: "cs-review-todos"
description: "Review open todos and issues in the project notebook using the nb MCP server."
---

## Purpose

Review open todos and issues in the project notebook, providing actionable
insights about outstanding work items and technical debt.

## Process

### 1. Discover Open Items

Use the `nb` MCP server to find open todos and issues:

- `nb.tasks` - list all open todos
- `nb.search` with `#status-open` tag - find items marked open
- `nb.search` with `#component-*` tags - find component-specific items

Also search the codebase for inline TODO-style comments:

- Use Grep to find `TODO`, `FIXME`, `XXX`, `HACK`, `NOTE` patterns
- Search source code, documentation, and configuration files
- Capture surrounding context (3-5 lines) for each finding

### 2. Categorize and Prioritize

Organize findings by:

- **Component**: Group by `#component-*` tags
- **Type**: Distinguish `#task-bug`, `#task-design`, `#task-enhance`, etc.
- **Status**: Note any `#status-blocked` or `#status-review` items

### 3. Report

Provide a structured summary:

- **Open count**: Total items by category
- **Blocked items**: Items requiring input or decisions
- **Stale items**: Items with no recent activity
- **Recommended next steps**: Prioritized action list

## Guardrails

- Do not modify notebook state unless explicitly requested.
- Focus on summarizing and prioritizing, not executing tasks.
- If notebook is empty or has no open items, report that cleanly.
