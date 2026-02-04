# Skills research notes (Agent Skills / SKILL.md)

Sources reviewed (2026-02-04):

- Agent Skills spec: https://agentskills.io/specification.md
- OpenCode skills docs: https://raw.githubusercontent.com/anomalyco/opencode/refs/heads/dev/packages/web/src/content/docs/skills.mdx
- Claude Code skills docs: https://code.claude.com/docs/en/skills.md

## Format (shared)

- A skill is a directory containing a required `SKILL.md` file.
- `SKILL.md` is Markdown with YAML frontmatter.
- Core required frontmatter fields:
  - `name` (lowercase, hyphenated, 1–64 chars; must match directory name)
  - `description` (1–1024 chars)
- Optional frontmatter fields in the base spec: `license`, `compatibility`,
  `metadata`, and an experimental `allowed-tools` (tool-specific behavior).
- In general, tools parse frontmatter and then load the skill body on demand
  (progressive disclosure).

## Locations (tool-specific)

### Claude Code

- Project skills live at `.claude/skills/<skill-name>/SKILL.md`.
- Personal skills live at `~/.claude/skills/<skill-name>/SKILL.md`.
- Claude states “custom slash commands have been merged into skills”, but
  `.claude/commands/` remains supported. (We should not automatically map our
  existing commands/subagents into skills.)
- Claude extends the base spec with extra frontmatter fields and behaviors
  (invocation control, subagents, dynamic context injection).

### OpenCode

OpenCode searches several skill roots, including:

- `.opencode/skills/<name>/SKILL.md`
- `~/.config/opencode/skills/<name>/SKILL.md`
- `.claude/skills/<name>/SKILL.md` (Claude-compatible)
- `~/.claude/skills/<name>/SKILL.md`
- `.agents/skills/<name>/SKILL.md` (agent-compatible)
- `~/.agents/skills/<name>/SKILL.md`

It also documents a native `skill` tool and permission controls in `opencode.json`.

## Implications for emcd-agents

- `SKILL.md` is standardized enough that we probably do **not** need
  coder-specific skill bodies, and we probably do **not** need to generate
  skills from our existing commands/agents. However, some frontmatter fields
  (notably `allowed-tools`) appear to have tool-specific semantics and may
  require per-coder formatting or omission.
- The discovery location *is* tool-specific. A good fit for our repo layout is
  to keep skills under each coder’s config directory and leverage the existing
  top-level symlinks:
  - `.claude -> .auxiliary/configuration/coders/claude` so `.claude/skills/...`
  - `.opencode -> .auxiliary/configuration/coders/opencode` so `.opencode/skills/...`
  - `.codex -> .auxiliary/configuration/coders/codex` so `.codex/skills/...`
- `allowed-tools` is a likely pressure point:
  - Claude documents and enforces it in skills frontmatter.
  - OpenCode appears to ignore unknown frontmatter fields and uses separate
    permission controls.
  - A pragmatic approach is to store a tool-agnostic “semantic tools” list in
    skill configuration and map/format it per coder where supported.
- Because OpenCode also loads `.claude/skills`, we can optionally host the
  canonical project skills in Claude’s skills directory and symlink other
  coders’ `skills/` directories to it to avoid duplication (decision pending).
