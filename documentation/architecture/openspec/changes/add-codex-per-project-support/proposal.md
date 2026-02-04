# Change: Add Codex per-project support (config)

## Why

`agentsmgr` currently treats Codex as **per-user only** and therefore does not
generate Codex project-scoped configuration. Codex supports per-project
configuration via `.codex/config.toml`. This makes Codex a good fit for the
same per-project workflow we already use for Claude Code, Gemini, and OpenCode.

## What Changes

- Update the Codex renderer to support `per-project` targeting and make it the
  default for Codex (while keeping `per-user` available for legacy setups).
- Add a Copier template for Codex per-project configuration that renders to
  `.auxiliary/configuration/coders/codex/config.toml` and is exposed to Codex
  via a `.codex` symlink.
- Keep skills as a separate concern handled by the cross-coder change
  `add-agent-skills-support`. This Codex change does not map existing
  commands/agents to skills.

## Impact

- Affected specs:
  - `multi-tool-support`
  - `configuration-management`
  - `path-compatibility`
- Affected code (expected):
  - `sources/agentsmgr/renderers/codex.py`
  - `template/.auxiliary/configuration/coders/` (Codex project config template)

## Breaking / Migration Notes

- Codex will move from **per-user default** → **per-project default** in
  `agentsmgr populate`. Users relying on global `~/.codex/config.toml` should
  keep running `agentsmgr populate user` with Codex explicitly enabled (or keep
  their existing global file) while migrating projects to `.codex/config.toml`.
