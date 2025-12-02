# Openspec Integration for Designs and Specs

## Decision Summary

We will adopt Openspec for managing design documentation and change proposals while preserving our existing standards enforcement mechanisms. This provides delta merging to keep designs synchronized with reality while maintaining project quality standards.

## Core Problem Solved

**Current pain:** Changes are planned and implemented in `.auxiliary/notes/`, but designs in `documentation/architecture/designs/*.rst` are never updated. This causes design drift where documentation becomes out-of-sync with reality.

**Solution:** Use Openspec's delta merging to automatically keep design documents synchronized when changes are archived.

## Architecture

### Directory Structure

```
documentation/
├── architecture/
│   ├── decisions/           # ADRs (RST) - Keep for now
│   ├── designs/            # SYMLINK → openspec/specs/ (for backward compat)
│   └── openspec/           # Openspec-managed
│       ├── AGENTS.md       # Openspec + project standards
│       ├── project.md      # Project context
│       ├── specs/          # Living design docs (Markdown)
│       │   ├── [capability]/
│       │   │   ├── spec.md     # Requirements with scenarios
│       │   │   └── design.md   # Technical architecture
│       └── changes/
│           ├── active/
│           │   └── [change-id]/
│           │       ├── proposal.md
│           │       ├── tasks.md
│           │       ├── progress.md         # Replaces .auxiliary/notes/*--progress.md
│           │       └── specs/
│           │           └── [capability]/
│           │               └── spec.md     # Delta (ADDED/MODIFIED/REMOVED)
│           └── archive/
│               └── YYYY-MM-DD-[id]/        # Timestamped history

.auxiliary/
├── instructions/          # Standards (RST) - Never migrate
│   ├── practices.rst
│   ├── practices-python.rst
│   ├── nomenclature.rst
│   └── ...
└── notes/                 # Issues, ideas, test plans (not progress tracking)
    ├── issues.md
    ├── todo.md
    └── ...
```

### Key Decisions

1. **Use Openspec tooling for delta merging** - Don't reimplement, it works
2. **Convert designs to Markdown** - One-time migration from RST
3. **Keep standards in RST** - practices.rst, nomenclature.rst remain
4. **Progress tracking moves to change directories** - No more scattered `.auxiliary/notes/*--progress.md`
5. **Use myst_parser for Sphinx** - Render Markdown in generated docs
6. **Keep custom slash commands** - Enhance existing workflow, don't replace

## Command Responsibilities

### /cs-design-python (Creates New Specs)

**Purpose:** Design new capabilities from scratch

**Output:**
```
openspec/specs/[capability]/
├── spec.md      # Requirements with WHEN/THEN scenarios
└── design.md    # Technical architecture, patterns, examples
```

**Workflow:**
```
User: "Design a metrics export system"
→ /cs-design-python metrics-export
→ Creates openspec/specs/metrics-export/{spec.md, design.md}
→ Follows practices-python.rst standards
→ Writes requirements as scenarios
→ Documents architecture in design.md
```

**Changes from current:**
- Output location: `openspec/specs/[capability]/` (not `designs/*.rst`)
- Output format: Markdown (not RST)
- Create both spec.md and design.md
- Use scenario format for requirements

### /openspec:proposal (Modifies Existing Specs)

**Purpose:** Propose changes to existing capabilities

**Output:**
```
openspec/changes/active/[change-id]/
├── proposal.md
├── tasks.md
└── specs/[capability]/
    └── spec.md     # Delta (ADDED/MODIFIED/REMOVED)
```

**Workflow:**
```
User: "Update metrics-export to support CSV format"
→ /openspec:proposal update-metrics-csv
→ Creates change directory with proposal, tasks
→ Creates delta spec showing ADDED/MODIFIED requirements
→ References @.auxiliary/instructions via AGENTS.md
```

**Standards enforcement:**
- AGENTS.md references practices.rst, practices-python.rst
- Requires reading standards before creating proposals
- Validates scenario format, requirement structure

### /cs-code-python (Implements Either)

**Purpose:** Implement new specs or change proposals following standards

**Auto-detects mode:**
```bash
/cs-code-python metrics-export
# Checks: Is this a spec? Is this a change-id?
# Reads from openspec/specs/ OR openspec/changes/active/
```

**Pattern 1: Implementing new spec**
```
Reads: openspec/specs/metrics-export/
Creates: .auxiliary/notes/metrics-export--progress.md
Implements: Following design.md
```

**Pattern 2: Implementing change proposal**
```
Reads: openspec/changes/active/update-metrics-csv/
Creates: openspec/changes/active/update-metrics-csv/progress.md
Implements: Following delta specs
Updates: tasks.md as work completes
```

**Shrinking via vibelinter:**
Since vibelinter now enforces:
- Module organization
- Import patterns
- Spacing rules
- Blank lines in functions

cs-code-python focuses on:
- Standards reading and attestation (still required)
- Type annotation patterns (wide parameter, narrow return)
- Exception hierarchy (Omnierror patterns)
- Documentation (narrative mood)
- Immutability preferences
- Quality gate execution

### /openspec:apply (Implements Change Proposals)

**Purpose:** Implement approved change proposals with standards enforcement

**Workflow:**
```
User: "Implement the CSV export change"
→ /openspec:apply update-metrics-csv
→ Reads proposal.md, tasks.md via AGENTS.md
→ Follows practices.rst, practices-python.rst
→ Implements following delta specs
→ Updates tasks.md
→ Validates with vibelinter + quality gates
```

**Standards enforcement via AGENTS.md:**
- References to @.auxiliary/instructions
- Attestation requirements
- Quality gates (linters, tests)

### openspec archive (Merges Deltas)

**Purpose:** Archive completed change and merge deltas to specs

```bash
openspec archive update-metrics-csv
# Moves changes/active/update-metrics-csv/
#    → changes/archive/YYYY-MM-DD-update-metrics-csv/
# Applies deltas to specs/metrics-export/spec.md
# Designs stay synchronized ✓
```

## Workflow Examples

### Creating a New Capability

```
1. User: "I need to add plugin support"
2. /cs-design-python plugins
   → Creates openspec/specs/plugins/{spec.md, design.md}
   → Documents requirements as scenarios
   → Documents architecture
3. User approves design
4. /cs-code-python plugins
   → Implements following spec
   → Creates .auxiliary/notes/plugins--progress.md
   → Validates with vibelinter + quality gates
5. Done - new spec exists in openspec/specs/plugins/
```

### Modifying an Existing Capability

```
1. User: "Plugins should support async loading"
2. /openspec:proposal add-async-plugin-loading
   → Creates change directory
   → Writes proposal.md (why async is needed)
   → Writes tasks.md (implementation steps)
   → Creates delta spec (MODIFIED: Plugin Loading requirement)
3. User approves proposal
4. /openspec:apply add-async-plugin-loading
   → Implements following delta
   → Creates progress.md in change directory
   → Updates tasks.md
   → Validates with vibelinter + quality gates
5. openspec archive add-async-plugin-loading
   → Merges delta to openspec/specs/plugins/spec.md
   → Archives to changes/archive/YYYY-MM-DD-add-async-plugin-loading/
   → Design synchronized ✓
```

## PRD Elimination

Instead of maintaining `documentation/prd.rst` separately, fold product requirements into specs:

**Migration strategy:**
- Functional requirements → spec.md files in relevant capabilities
- Product-level goals/vision → openspec/project.md or README
- User personas → spec Purpose sections
- Delete documentation/prd.rst
- Delete /cs-manage-prd command

**Before (PRD):**
```rst
FR-001: Export Metrics
  Users shall export usage metrics in JSON format
  Priority: High
```

**After (Spec):**
```markdown
openspec/specs/metrics-export/spec.md

### Requirement: Metrics Export
Users SHALL export usage metrics to analyze application usage patterns.

#### Scenario: JSON export
- **WHEN** user requests metrics export
- **THEN** system provides JSON formatted output
- **AND** includes all usage data points

Priority: High
```

## Standards Enforcement

### Via openspec/AGENTS.md

Update AGENTS.md to reference project standards:

```markdown
## Project Standards

Before any design or implementation work:
- Read @.auxiliary/instructions/practices.rst - General development principles
- Read @.auxiliary/instructions/practices-python.rst - Python-specific patterns
- Read @.auxiliary/instructions/nomenclature.rst - Naming conventions

These standards are MANDATORY for all implementations.

## Quality Gates

All implementations MUST pass:
```bash
hatch --env develop run linters  # Includes vibelinter, ruff, pyright
hatch --env develop run testers  # All tests
```

See @.auxiliary/instructions/validation.rst for details.
```

### Via vibelinter

Automated enforcement of:
- Module organization (imports, type aliases, functions)
- Import patterns (centralized via `__`)
- Spacing (around brackets, delimiters)
- Blank lines in function bodies
- Function/class ordering

### Via cs-code-python

Continued enforcement of:
- Standards reading and attestation
- Type annotation patterns (wide parameter, narrow return)
- Exception hierarchy design (Omnierror patterns)
- Documentation (narrative mood, no parameter docs)
- Immutability preferences
- Quality gate execution

## Sphinx Integration

### Configuration

Add to `conf.py`:
```python
extensions = [
    'myst_parser',  # Markdown support
    # ... other extensions
]

# Configure MyST
myst_enable_extensions = [
    'colon_fence',      # ::: blocks
    'deflist',          # Definition lists
    'tasklist',         # - [ ] tasks
]

# Include .md files in source
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}
```

### Embedding RST in Markdown

Use `eval-rst` directive when needed:
```markdown
## Architecture Overview

```{eval-rst}
.. autoclass:: mypackage.Engine
   :members:
```
```

## Migration Tasks

### Setup Phase
- [ ] Install myst_parser in Sphinx dependencies
- [ ] Create documentation/architecture/openspec/ (or symlink from root)
- [ ] Run `openspec init documentation/architecture/openspec`
- [ ] Update openspec/AGENTS.md with standards references

### Migration Phase
- [ ] Convert designs/*.rst → openspec/specs/*/design.md
  - Use migration prompt (see openspec-migration.md)
  - Pandoc for initial conversion, manual cleanup
  - Extract requirements into spec.md files
- [ ] Migrate prd.rst → various openspec/specs/*/spec.md
- [ ] Create symlink: designs/ → openspec/specs/
- [ ] Update Sphinx conf.py to render Markdown
- [ ] Validate: `openspec validate --specs --strict`

### Command Updates
- [ ] Update /cs-design-python to output to openspec/specs/
- [ ] Update /cs-code-python to auto-detect spec vs change
- [ ] Shrink /cs-code-python (remove vibelinter-enforced checks)
- [ ] Update openspec/AGENTS.md with standards references
- [ ] Delete /cs-manage-prd

### Validation
- [ ] Test new spec creation with /cs-design-python
- [ ] Test change proposal with /openspec:proposal
- [ ] Test implementation with /openspec:apply
- [ ] Test archiving with openspec archive
- [ ] Verify Sphinx builds with Markdown specs

## Benefits

✅ **Design synchronization** - Deltas merged automatically, no drift
✅ **Change history** - Timestamped archives with full context
✅ **Standards enforcement** - Via AGENTS.md + vibelinter + quality gates
✅ **No fork maintenance** - Use Openspec CLI directly
✅ **Clear separation** - Design commands create new, Openspec modifies existing
✅ **Progress tracking** - Co-located with changes, not scattered
✅ **Single source of truth** - openspec/specs/ is canonical

## What We're NOT Getting

❌ **No custom Openspec implementation** - Use their tooling, don't rewrite
❌ **No RST for new designs** - Accepting Markdown as standard
❌ **No separate designs/ directory** - Everything in openspec/specs/
❌ **No .auxiliary/notes/*--progress.md** - Moves to change directories

## Future Considerations

See `openspec-adrs.md` for deferred work on:
- ADRs as architecture deltas
- Broader architecture document management
- Custom tooling if Openspec proves insufficient
