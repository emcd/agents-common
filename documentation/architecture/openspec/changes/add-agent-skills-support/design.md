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
- `defaults/contents/skills/<coder>/<name>.md`
- `defaults/templates/skills/<flavor>.<ext>.jinja`

This keeps parity with the existing `commands/` and `agents/` organization.

## Output layout

Project-scoped outputs:

- `.auxiliary/configuration/skills/<name>/SKILL.md`
- Optional bundled resources:
  - `.auxiliary/configuration/skills/<name>/scripts/...`
  - `.auxiliary/configuration/skills/<name>/references/...`
  - `.auxiliary/configuration/skills/<name>/assets/...`

Discovery mount point:

- `.skills` → `.auxiliary/configuration/skills` (symlink)

Coders that have their own expected skills directory can additionally symlink
to `.skills` (handled in their renderer), but the shared mount point is the
source of truth.

## Templates

`SKILL.md` should be generated with:

- YAML frontmatter:
  - `name`: from TOML `context.name`
  - `description`: from TOML `context.description`
  - `allowed-tools`: optional; space-delimited per the spec
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

## Migration / interaction with existing items

We should not automatically convert every existing `command` or `agent` into a
skill. Instead:

- Introduce skills as a separate curated set.
- Allow later work to “promote” selected high-value procedures into skills and
  optionally have commands/agents reference those skills.

