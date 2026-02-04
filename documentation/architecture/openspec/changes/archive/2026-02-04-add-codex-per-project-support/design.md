# Design: Codex per-project configuration

## Goals

- Make Codex behave like other **per-project** coders in this repository:
  `agentsmgr populate project` creates project-scoped config and content.
- Keep Codex configuration consistent with our existing “store everything under
  `.auxiliary/configuration/` and expose via symlinks” pattern.
- Keep Codex “skills” integration aligned with the cross-coder Agent Skills
  capability (`add-agent-skills-support`).

## Non-Goals

- Re-introduce or rely on Codex “custom prompts” (`~/.codex/prompts`), which are
  per-user and deprecated.
- Model selection strategy changes beyond providing sane defaults in the
  project template.

## Output Layout (Per-Project)

Generated / templated files live under:

- `.auxiliary/configuration/coders/codex/config.toml`

And the project root exposes:

- `.codex` → `.auxiliary/configuration/coders/codex` (symlink)

This yields the Codex-supported paths:

- `.codex/config.toml`

## Skills

Codex supports `.codex/skills/…` for Agent Skills (`SKILL.md`).

This change does not define or generate skills. Instead, Codex should consume
the shared skills output introduced by `add-agent-skills-support`, which
generates skills under `.auxiliary/configuration/coders/codex/skills/` and
exposes them at `.codex/skills/` via the existing `.codex` symlink.
