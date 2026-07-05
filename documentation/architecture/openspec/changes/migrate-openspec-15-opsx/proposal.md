# Migrate agents-common to OpenSpec 1.5/OPSX

## Why

The agents-common Copier template still ships OpenSpec commands that reference
`openspec/AGENTS.md`, a monolithic 455-line instruction file. OpenSpec 1.5
introduces OPSX, a CLI-driven workflow where instructions are assembled
dynamically by the CLI and delivered through generated skills. The template
must migrate to OPSX to stay current and to prepare for a future structured
transition to nbspec via OpenSpec 1.5 flexible schemata.

## What Changes

- Delete old `openspec-*` commands (proposal, apply, archive) from
  `defaults/per-project/resources/` for both coders.
- Add curated OPSX skills (`cs-opsx-propose`, `cs-opsx-apply`,
  `cs-opsx-archive`, `cs-opsx-explore`, `cs-opsx-sync`) under
  `defaults/contents/skills/` for portable distribution across coders.
  Skills cover the same workflow as the old commands; explicit coder-specific
  command defaults are not needed since the body content is identical.
- Remove `stores` guidance from all OPSX skills; stores are unstable and
  not part of template policy.
- Add `explore` and `sync` skills not present in old defaults.
- Seed `openspec/config.yaml` with `schema: spec-driven` via Jinja template.
- Rewrite `template/documentation/agents/openspec.md` away from
  `@openspec/AGENTS.md` toward OPSX skills and CLI state queries.
- Update the OpenSpec section in `AGENTS.md.jinja` to match.
- Delete `template/documentation/architecture/openspec/AGENTS.md` (no longer
  needed; OPSX delivers instructions dynamically).
- Drop `openspec/AGENTS.md` entirely; `documentation/agents/openspec.md`
  serves as the LM-readable and human-readable reference, while OPSX
  delivers agent instructions dynamically via CLI.

## Impact

- Affected specs: `configuration-management`, `multi-tool-support`
- Affected code:
  - `defaults/per-project/resources/opencode/command/openspec-*.md` (delete)
  - `defaults/per-project/resources/claude/commands/openspec/*.md` (delete)
  - `defaults/contents/skills/cs-opsx-*.md` (add)
  - `template/documentation/architecture/openspec/AGENTS.md` (delete)
  - `template/documentation/architecture/openspec/config.yaml.jinja` (add)
  - `template/documentation/agents/openspec.md` (rewrite)
  - `template/.auxiliary/configuration/AGENTS.md.jinja` (update OpenSpec section)
- Validation: `openspec validate migrate-openspec-15-opsx --strict`
