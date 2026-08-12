# Restructure distribution model: tracked vs managed

## Why

The current distribution model has four layers (Copier template, agentsmgr distributed content, agentsmgr generated content, agentsmgr retrieved content) with blanket directory-level gitignore hiding all managed content. This prevents downstream repos from committing custom skills/commands and obscures what agentsmgr owns.

The new model simplifies to two tiers: tracked project-owned files via Copier, and agentsmgr-managed distribution artifacts. Downstream custom skills/commands appear naturally in `git status`. agentsmgr manages `.git/info/exclude` at the individual-file level.

## What Changes

- Rename `defaults/` to `distribution/` as the tree consumed by downstream `agentsmgr populate`.
- Add `components/` for maintainer source material used to generate command/agent artifacts.
- Pre-generate managed command/agent artifacts in agents-common so outputs are committed and reviewable.
- Sync external instruction content directly into `distribution/per-project/general/instructions/` (not components; instructions are direct distribution artifacts).
- agentsmgr manages `.git/info/exclude` at individual-file level instead of blanket directory ignores.
- Split generation from population: `agentsmgr generate` produces `components/` -> `distribution/`; `agentsmgr populate` consumes `distribution/` downstream.

## Impact

- Affected specs: `configuration-management`, `hybrid-distribution`, `multi-tool-support`
- Affected code:
  - `defaults/` renamed to `distribution/`
  - `components/` added (new)
  - `sources/agentsmgr/population.py` (exclude management rewrite)
  - `sources/agentsmgr/operations.py` (generation logic)
  - `sources/agentsmgr/generator.py` (new generate command)
  - Template `.gitignore` and exclude patterns updated
- Adjacent context (not in scope): `agents-common:todos/agentsmgr/15` (package split), `agents-common:todos/template/8` (copiertv migration)
- Validation: `openspec validate restructure-distribution-model --strict`
