# agentsmgr

CLI and library for generating and populating AI coder configurations from
structured sources. Capability requirements live under
`documentation/architecture/openspec/specs/` (OpenSpec); this README holds
package layout and design rationale next to the code.

## Purpose

agents-common combines:

- **Copier** for minimal base coder settings and directory scaffolding
  (`template/`).
- **agentsmgr** for rendering `components/` → `distribution/` and populating
  downstream projects or user homes from `distribution/`.

That hybrid keeps base settings on the proven Copier path while agent commands,
agents, skills, and instructions can iterate without full template releases.
Configuration is detected from Copier answers files, with defaults when answers
are absent. Downstream populate records managed paths as file-level entries in
`.git/info/exclude`.

Content releases use lightweight `agents-N` git tags so consumers can pin or
roll back configuration sets independently of package versioning.

## Layout

```
sources/agentsmgr/
├── cli.py              # Tyro CLI entry
├── cmdbase.py          # Shared command helpers / configuration load
├── core.py             # Display and stream adaptation
├── detection.py        # Project configuration detection
├── population.py       # populate + generate commands
├── generator.py        # components/ → distribution/ rendering
├── operations.py       # Git exclude and filesystem helpers
├── instructions.py     # Instruction fetch from configured git sources
├── memorylinks.py      # Project memory file symlinks
├── userdata.py         # Per-user population helpers
├── exceptions.py       # Package exception hierarchy
├── renderers/          # Coder-specific path and format contracts
│   ├── base.py
│   ├── claude.py
│   ├── codex.py
│   └── opencode.py
└── sources/            # Pluggable content source handlers
    ├── base.py
    ├── git.py
    └── local.py
```

Repository content tiers (outside this package):

```
components/             # Source material (configurations, contents, templates)
distribution/           # Generated artifacts consumed by populate
template/               # Copier template for base coder configuration
```

## Commands

- `agentsmgr detect` — inspect project agent configuration
- `agentsmgr generate` — render `components/` → `distribution/` (optional
  `--check`, `--answers-file`, `--output`)
- `agentsmgr populate` — copy distribution into a project or user target;
  manages coder symlinks, instruction copy, and git excludes

## OpenSpec home

Project OpenSpec scaffolding lives under
`documentation/architecture/openspec/`. The repository root `openspec` path is
a managed symlink to that directory so OPSX tools that expect `./openspec`
work without a real top-level OpenSpec tree.
