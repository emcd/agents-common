---
name: "cs-opsx-sync"
description: "Sync delta specs from an OpenSpec change to main specs."
---

## Purpose

Sync delta specs from a change to main specs. This is an agent-driven operation - you read delta specs and directly edit main specs to apply the changes. This allows intelligent merging (e.g., adding a scenario without copying the entire requirement).

## Process

### 1. Select the Change

If a name is provided, use it. Otherwise:
- Run `openspec list --json` to get available changes
- Ask the user to select from changes that have delta specs

Do NOT guess or auto-select a change. Always let the user choose.

### 2. Resolve Change Context

```bash
openspec status --change "<name>" --json
```

### 3. Find Delta Specs

Use `artifactPaths.specs.existingOutputPaths` from the status JSON as the list of delta spec files.

Each delta spec file contains sections like:
- `## ADDED Requirements` - New requirements to add
- `## MODIFIED Requirements` - Changes to existing requirements
- `## REMOVED Requirements` - Requirements to remove
- `## RENAMED Requirements` - Requirements to rename (FROM:/TO: format)

If no delta specs found, inform user and stop.

### 4. Apply Changes to Main Specs

For each capability delta spec:

a. Read the delta spec to understand the intended changes

b. Read the main spec at `openspec/specs/<capability>/spec.md` (may not exist yet)

c. Apply changes intelligently:

   **ADDED Requirements:**
   - If requirement doesn't exist in main spec -> add it
   - If requirement already exists -> update it to match (treat as implicit MODIFIED)

   **MODIFIED Requirements:**
   - Find the requirement in main spec
   - Apply the changes (adding scenarios, modifying existing scenarios, changing description)
   - Preserve scenarios/content not mentioned in the delta

   **REMOVED Requirements:**
   - Remove the entire requirement block from main spec

   **RENAMED Requirements:**
   - Find the FROM requirement, rename to TO

d. Create new main spec if capability doesn't exist yet:
   - Create `openspec/specs/<capability>/spec.md`
   - Add Purpose section (can be brief, mark as TBD)
   - Add Requirements section with the ADDED requirements

### 5. Show Summary

After applying all changes, summarize: which capabilities were updated, what changes were made.

## Key Principle: Intelligent Merging

Unlike programmatic merging, you can apply partial updates:
- To add a scenario, just include that scenario under MODIFIED - don't copy existing scenarios
- The delta represents intent, not a wholesale replacement
- Use your judgment to merge changes sensibly

## Guardrails

- Read both delta and main specs before making changes
- Preserve existing content not mentioned in delta
- If something is unclear, ask for clarification
- Show what you're changing as you go
- The operation should be idempotent - running twice should give same result
