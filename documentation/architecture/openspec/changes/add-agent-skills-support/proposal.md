# Change: Add Agent Skills support (cross-coder)

## Why

We want a portable, version-controlled way to distribute reusable expertise
to multiple coding agents and CLIs. The Agent Skills format provides a simple
filesystem-based standard (`<skill>/SKILL.md` with YAML frontmatter) that
multiple tools can integrate with.

This should be a separate change from Codex per-project configuration, because
skills are a cross-tool concern and will impact how (and where) we generate
reusable instruction packages for **all** coders.

## What Changes

- Add a first-class **skills** item type to the `agentsmgr` generation model.
- Define an Agent Skills–compatible output layout under
  `.auxiliary/configuration/skills/<skill-name>/SKILL.md`.
- Provide a compatibility “mount point” in project roots (e.g. `.skills`)
  to make discovery easy for tools that expect a conventional skills
  directory.
- Add templates that emit valid Agent Skills `SKILL.md` files:
  - YAML frontmatter: `name`, `description`, optional `allowed-tools`
  - Markdown body: skill instructions
- Add semantic-tool mapping support for Agent Skills `allowed-tools` so our
  existing tool-agnostic TOML metadata can populate it.
- Update coder templates/configuration (where supported) to surface the skills
  directory for discovery.

## Impact

- Affected specs:
  - `multi-tool-support`
  - `configuration-management`
  - `path-compatibility`
- Affected code (expected):
  - `sources/agentsmgr/generator.py` (new item type + output mapping)
  - `sources/agentsmgr/context.py` (Agent Skills `allowed-tools` mapping)
  - `sources/agentsmgr/renderers/*` (symlink / discovery hook if needed)
  - `defaults/{configurations,contents,templates}/skills/` (new tier)

## Notes

- Codex per-project support should consume this capability by exposing
  `.codex/skills` to the shared skills directory, rather than inventing a
  Codex-only “skills from commands/agents” mapping.

