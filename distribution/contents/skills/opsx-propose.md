---
name: "opsx-propose"
description: "Propose a new OpenSpec change - create it and generate all artifacts in one step."
---

## Purpose

Propose a new change - create the change and generate all artifacts in one step.

Artifacts created:
- proposal.md (what & why)
- design.md (how)
- tasks.md (implementation steps)

When ready to implement, use `opsx-apply`.

## Process

### 1. Gather Input

If no input provided, ask what the user wants to build. From their description, derive a kebab-case name (e.g., "add user authentication" -> `add-user-auth`).

Do NOT proceed without understanding what the user wants to build.

### 2. Create the Change Directory

```bash
openspec new change "<name>"
```

This creates a scaffolded change in the planning home resolved by the CLI with `.openspec.yaml`.

### 3. Get the Artifact Build Order

```bash
openspec status --change "<name>" --json
```

Parse the JSON to get:
- `applyRequires`: array of artifact IDs needed before implementation
- `artifacts`: list of all artifacts with their status and dependencies
- `planningHome`, `changeRoot`, `artifactPaths`, and `actionContext`: path and scope context

### 4. Create Artifacts in Sequence

Loop through artifacts in dependency order (artifacts with no pending dependencies first):

a. For each artifact that is `ready` (dependencies satisfied):
   - Get instructions: `openspec instructions <artifact-id> --change "<name>" --json`
   - The instructions JSON includes: `context`, `rules`, `template`, `instruction`, `resolvedOutputPath`, `dependencies`
   - Read any completed dependency files for context
   - Create the artifact file using `template` as the structure
   - Apply `context` and `rules` as constraints - do NOT copy them into the file

b. Continue until all `applyRequires` artifacts are complete.

c. If an artifact requires user input (unclear context), ask for clarification.

### 5. Show Final Status

```bash
openspec status --change "<name>"
```

Summarize: change name, artifacts created, readiness for implementation.

## Guardrails

- Create ALL artifacts needed for implementation (as defined by schema's `apply.requires`)
- Always read dependency artifacts before creating a new one
- If context is critically unclear, ask the user - but prefer making reasonable decisions to keep momentum
- If a change with that name already exists, ask if user wants to continue it or create a new one
- Verify each artifact file exists after writing before proceeding to next
- Follow the `instruction` field from `openspec instructions` for each artifact type
- `context` and `rules` are constraints for YOU, not content for the file
