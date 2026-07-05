---
name: "opsx-apply"
description: "Implement tasks from an approved OpenSpec change."
---

## Purpose

Implement tasks from an OpenSpec change, tracking progress as you go.

## Process

### 1. Select the Change

If a name is provided, use it. Otherwise:
- Infer from conversation context if the user mentioned a change
- Auto-select if only one active change exists
- If ambiguous, run `openspec list --json` and ask the user to select

Always announce: "Using change: <name>" and how to override.

### 2. Check Status

```bash
openspec status --change "<name>" --json
```

Parse the JSON to understand:
- `schemaName`: The workflow being used
- `planningHome`, `changeRoot`, and `actionContext`: planning scope and edit constraints
- Which artifact contains the tasks

### 3. Get Apply Instructions

```bash
openspec instructions apply --change "<name>" --json
```

This returns: `contextFiles`, progress, task list, dynamic instruction.

Handle states:
- If `state: "blocked"` (missing artifacts): show message, suggest creating missing artifacts
- If `state: "all_done"`: congratulate, suggest archive
- Otherwise: proceed to implementation

### 4. Read Context Files

Read every file path listed under `contextFiles` from the apply instructions output.

### 5. Implement Tasks (Loop)

For each pending task:
- Show which task is being worked on
- Make the code changes required
- Keep changes minimal and focused
- Mark task complete in the tasks file: `- [ ]` -> `- [x]`
- Continue to next task

Pause if:
- Task is unclear -> ask for clarification
- Implementation reveals a design issue -> suggest updating artifacts
- Error or blocker encountered -> report and wait for guidance

### 6. Show Status on Completion or Pause

Display tasks completed, overall progress, and next steps.

## Guardrails

- Keep going through tasks until done or blocked
- Always read context files before starting
- If task is ambiguous, pause and ask before implementing
- If implementation reveals issues, pause and suggest artifact updates
- Keep code changes minimal and scoped to each task
- Update task checkbox immediately after completing each task
- Pause on errors, blockers, or unclear requirements - don't guess
- Use contextFiles from CLI output, don't assume specific file names

## Fluid Workflow Integration

This skill supports the "actions on a change" model:
- Can be invoked anytime: before all artifacts are done (if tasks exist), after partial implementation, interleaved with other actions
- Allows artifact updates: if implementation reveals design issues, suggest updating artifacts - not phase-locked, work fluidly
