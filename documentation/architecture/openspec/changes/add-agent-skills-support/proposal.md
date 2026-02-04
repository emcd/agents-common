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
- Define an Agent Skills–compatible output layout under each coder’s project
  configuration directory (to match tool-specific discovery paths), e.g.:
  - `.auxiliary/configuration/coders/claude/skills/<skill-name>/SKILL.md`
  - `.auxiliary/configuration/coders/opencode/skills/<skill-name>/SKILL.md`
  - `.auxiliary/configuration/coders/codex/skills/<skill-name>/SKILL.md`
  (and reached via existing symlinks like `.claude`, `.opencode`, `.codex`).
- Add templates that emit valid Agent Skills `SKILL.md` files:
  - YAML frontmatter: `name`, `description`, optional `allowed-tools`
  - Markdown body: skill instructions
  - Prefer a single shared `SKILL.md` template across coders (format is a
    standard), only varying emission of tool-specific fields like
    `allowed-tools`.
- Add semantic-tool mapping support for `allowed-tools`, but format it per
  tool’s expectations (e.g. Claude uses `Read, Grep` style and accepts
  `Bash(gh *)`; OpenCode ignores unknown frontmatter fields and enforces skill
  permissions elsewhere).
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

- We should not automatically map existing commands/subagents into skills.
