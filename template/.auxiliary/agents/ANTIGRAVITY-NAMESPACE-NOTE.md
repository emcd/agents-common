# Antigravity Namespace Note

Google Antigravity CLI (`agy`) hardcodes `.agents/` as its workspace
configuration directory (plus the `.agent/`, `_agents/`, `_agent/`
aliases). That name collides with the shared `.agents/skills`
discovery convention this tree uses for interop across harnesses:
root `.agents` here symlinks to `.auxiliary/agents/`, so Antigravity
resolves its workspace files into this directory.

Files in this directory that belong to Antigravity (rather than to
the shared canonical tree):

- `mcp_config.json` — template-rendered workspace MCP servers for
  Antigravity only. Deliberately carries no `env` block: Antigravity
  takes `env` values literally instead of expanding them, which would
  clobber inherited `AGENTMUX_*` variables, so servers inherit the
  process environment (same as OpenCode and Codex). Do not edit this
  file in the Antigravity TUI without committing the result — the TUI
  writes through the symlink into this tracked file.
- `scripts/mcp-discover-shim.py` — populate-managed, git-excluded
  temporary compatibility shim. Antigravity probes MCP servers with
  `server/discover` before `initialize`; `agentmux` (on `rmcp` 1.x)
  exits instead of answering. TEMPORARY: drop the shim from
  distribution and invoke `agentmux host mcp` directly once `agentmux`
  ships `server/discover` support (`rmcp >= 3.x`).

Skills need no Antigravity-specific handling: `.agents/skills`
resolves to the canonical `skills/` tree in this directory, which is
exactly what Antigravity, Muse Code, and generic Agent Skills
consumers all read.


Deselecting Antigravity: removing `antigravity` from the `coders`
answer stops future updates to `mcp_config.json` (excluded files are
not re-rendered) and stops populate from refreshing the shim, but
neither file is deleted automatically. Delete both by hand
(`mcp_config.json` in this directory and
`scripts/mcp-discover-shim.py`), verify `git status` is clean
afterward, and commit the removal with the answers change.
