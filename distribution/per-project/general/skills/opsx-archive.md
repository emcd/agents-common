---
name: "opsx-archive"
description: "Archive a completed OpenSpec change and update specs."
---

## Purpose

Archive a completed OpenSpec change, optionally syncing delta specs to main specs first.

## Process

### 1. Select the Change

If a name is provided, use it. Otherwise:
- Run `openspec list --json` to get available changes
- Ask the user to select from active changes (not already archived)

Do NOT guess or auto-select a change. Always let the user choose.

### 2. Check Artifact Completion

```bash
openspec status --change "<name>" --json
```

If any artifacts are not `done`, display warning and prompt for confirmation.

### 3. Check Task Completion

Read the tasks file to count incomplete vs complete tasks. If incomplete tasks found, display warning and prompt for confirmation.

### 4. Assess Delta Spec Sync State

Use `artifactPaths.specs.existingOutputPaths` from status JSON to check for delta specs. If none exist, proceed without sync prompt.

If delta specs exist:
- Compare each delta spec with its corresponding main spec
- Determine what changes would be applied
- Show a combined summary before prompting

Prompt options:
- If changes needed: "Sync now (recommended)", "Archive without syncing"
- If already synced: "Archive now", "Sync anyway", "Cancel"

If user chooses sync, invoke `opsx-sync` for the change. Proceed to archive regardless of choice.

### 5. Perform the Archive

```bash
mkdir -p "<planningHome.changesDir>/archive"
mv "<changeRoot>" "<planningHome.changesDir>/archive/YYYY-MM-DD-<name>"
```

Generate target name using current date. Check if target already exists; if so, fail with error.

### 6. Display Summary

Show: change name, schema, archive location, spec sync status, any warnings.

## Guardrails

- Always prompt for change selection if not provided
- Use artifact graph (openspec status --json) for completion checking
- Don't block archive on warnings - just inform and confirm
- Preserve .openspec.yaml when moving to archive (it moves with the directory)
- Show clear summary of what happened
- If delta specs exist, always run the sync assessment and show the combined summary before prompting
