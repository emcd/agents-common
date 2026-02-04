# Design: Agent Skills support

## Background

Agent Skills are directories containing a required `SKILL.md` file with YAML
frontmatter (`name`, `description`, optional fields) followed by Markdown
instructions. Skills can optionally include `scripts/`, `references/`, and
`assets/` directories. Skills are intended to be discovered via filesystem
scans and activated by reading the `SKILL.md` body (progressive disclosure).

## Repository data model

Add a new 3-tier source set:

- `defaults/configurations/skills/<name>.toml`
- `defaults/contents/skills/common/<name>.md` (tool-agnostic body)
  - optional overrides: `defaults/contents/skills/<coder>/<name>.md`
- `defaults/templates/skills/common.md.jinja` (shared SKILL.md template)

This keeps parity with the existing `commands/` and `agents/` organization.

## Output layout

Project-scoped outputs (per coder, matching tool discovery roots):

- `.auxiliary/configuration/coders/<coder>/skills/<name>/SKILL.md`
- Optional bundled resources:
  - `.auxiliary/configuration/coders/<coder>/skills/<name>/scripts/...`
  - `.auxiliary/configuration/coders/<coder>/skills/<name>/references/...`
  - `.auxiliary/configuration/coders/<coder>/skills/<name>/assets/...`

These are surfaced via existing top-level symlinks (e.g. `.claude`, `.opencode`,
`.codex`), so tools discover skills at:

- `.claude/skills/<name>/SKILL.md`
- `.opencode/skills/<name>/SKILL.md`
- `.codex/skills/<name>/SKILL.md`

## Templates

`SKILL.md` should be generated with:

- YAML frontmatter:
  - `name`: from TOML `context.name`
  - `description`: from TOML `context.description`
  - `allowed-tools`: optional; only where the target tool supports it
- Markdown body:
  - tool-agnostic instructions, referencing bundled resources via relative
    paths when needed

## Tool mapping

Our existing semantic tool metadata should be mapped to Agent Skills
`allowed-tools` tokens. This mapping must be:

- deterministic (stable ordering)
- compatible with whichever tooling consumes it (the field is experimental)

Where a given tool cannot be expressed, omit it rather than emitting invalid
tokens.

Because `allowed-tools` appears to be tool-specific (and some tools ignore it),
we should store a single tool-agnostic list in skill configuration (semantic
tools + shell/MCP specifications) and map/format it per coder during rendering.

## Migration / interaction with existing items

We should not automatically convert every existing `command` or `agent` into a
skill. Instead:

- Introduce skills as a separate curated set.
- Allow later work to “promote” selected high-value procedures into skills and
  optionally have commands/agents reference those skills.
