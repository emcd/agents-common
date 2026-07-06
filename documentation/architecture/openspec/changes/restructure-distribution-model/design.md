## Context

The agents-common project distributes AI agent configurations to downstream repositories through a Copier template and an `agentsmgr` CLI tool. The current model has four distribution layers with blanket directory-level gitignore, preventing downstream repos from committing custom content and obscuring what agentsmgr owns.

The restructuring simplifies to two tiers and introduces a clear source-to-artifact pipeline.

## Goals / Non-Goals

- Goals:
  - Two-tier downstream model: tracked (Copier) vs managed (agentsmgr)
  - Downstream custom skills/commands visible in `git status`
  - Individual-file exclude management via `.git/info/exclude`
  - Pre-generated artifacts committed in agents-common for review visibility
  - Synced external instructions to eliminate network fetch downstream
  - Clear separation: `components/` (source) -> `distribution/` (artifacts) -> downstream

- Non-Goals:
  - agentsmgr Python package split (`agents-common:todos/agentsmgr/15`)
  - copiertv migration (`agents-common:todos/template/8`)
  - Dynamic instruction fetch
  - Broader downstream model changes beyond tracked-vs-managed

## Decisions

### Decision: `defaults/` renamed to `distribution/`

The name `defaults/` is ambiguous (default values? default content?). `distribution/` clearly communicates that this tree is consumed by downstream `agentsmgr populate`.

Alternatives considered:
- Keep `defaults/` -- familiar but unclear purpose
- `managed/` -- conflicts with the mental model (managed is the tier, not the directory)

### Decision: `components/` for source material

Source material for generating command/agent artifacts lives in `components/`, separate from both the distribution output and the template.

Structure mirrors the current 3-tier pipeline (configurations, templates, contents) but only for generated content types (commands, agents). Skills and instructions are distributed directly from `distribution/`.

### Decision: Distribution directory structure

The `distribution/` tree mirrors the downstream target layout:

```
distribution/
├── per-project/
│   ├── general/
│   │   ├── instructions/    # Synced instruction artifacts
│   │   └── skills/          # Portable skills (opsx-*, etc.)
│   └── coders/
│       ├── claude/           # Claude-specific artifacts
│       │   ├── commands/
│       │   └── agents/
│       ├── codex/            # Codex-specific artifacts
│       └── opencode/         # OpenCode-specific artifacts
└── per-user/
    ├── general/              # User-level executables
    └── coders/
        ├── claude/           # Per-user Claude config
        ├── codex/            # Per-user Codex config
        └── opencode/         # Per-user OpenCode config
```

This structure enables:
- Skills and instructions shared across coders in `per-project/general/`
- Coder-specific commands/agents in `per-project/coders/<coder>/`
- Per-user configuration in `per-user/coders/<coder>/`
- Per-user executables in `per-user/general/`

### Decision: Skills distributed directly, not generated

Skills are coder-agnostic and require no transformation. They live directly in `distribution/per-project/general/skills/` as both source and output. This is a conscious tradeoff: skills are the one category where source == output.

### Decision: Instructions synced into agents-common

External instruction content (from `python-project-common` or similar) is synced directly into `distribution/per-project/general/instructions/` as a distribution artifact. No network fetch during downstream populate. Upstream refactors land in agents-common PRs.

Instructions are not components: they are direct distribution artifacts, like skills. The sync mechanism and cadence are implementation details deferred to the first implementation slice.

Python Owner/Python XO are required reviewers for implementation decisions on instruction syncing.

### Decision: Pre-generated artifacts committed

Command/agent artifacts are pre-generated in agents-common and committed to `distribution/`. This provides:
- Review visibility (PRs show exactly what downstream receives)
- Deterministic validation (staleness checks via regenerate-and-diff)
- No surprise generation failures downstream

Staleness validation: `agentsmgr generate --check` regenerates from `components/` and fails on diff.

### Decision: File-level exclude management

agentsmgr manages `.git/info/exclude` at the individual-file level for paths it distributes. This replaces blanket directory ignores.

Ownership is derived from the current `distribution/` tree (no separate manifest). If a managed artifact is removed upstream, next populate removes that file's exclude entry and the downstream maintainer can adopt or delete the now-visible file.

Edge case: if a downstream custom file matches a managed distribution path, next populate may adopt it as managed. Documented but low risk.

### Decision: Generation/population split

- `agentsmgr generate`: produces `components/` -> `distribution/` (maintainer-facing)
- `agentsmgr populate`: consumes `distribution/` -> downstream (user-facing)

`agentsmgr-maintain` is subsumed by `agentsmgr generate`. The generate command handles both production and staleness checking.

## Risks / Trade-offs

- Larger diffs in agents-common when artifacts change -- acceptable because output is exactly what needs review
- Migration complexity for downstream repos (path changes, exclude reconciliation) -- mitigated by clear migration guidance
- Skills source == output inconsistency -- acceptable tradeoff for simplicity

## Migration Plan

1. Create `distribution/` tree alongside `defaults/` during transition
2. Update docs, scripts, and self-dogfooding commands to reference `distribution/`
3. Optionally add a compatibility shim if existing implicit `defaults/` references require it
4. Migrate downstream repos via `copier update` with new answers
5. Remove `defaults/` after transition period
