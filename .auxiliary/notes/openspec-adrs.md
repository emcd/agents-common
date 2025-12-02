# Openspec Integration for ADRs and Architecture (Deferred)

## Status

**DEFERRED** - Validate Openspec workflow with designs/specs first before tackling architectural decisions.

## Problem Statement

Traditional ADR (Architecture Decision Record) approach has limitations:
- Superseded ADRs pile up in the index over time
- Current architectural state scattered across multiple ADRs
- Hard to answer "what's the current architecture?"
- No automatic synchronization when decisions change

## Proposed Solution: Architecture as Living Specs with Decision Deltas

### Concept

Treat architecture documentation like any other spec:
- Current architecture lives in `openspec/specs/architecture/design.md`
- Architectural decisions are deltas against that living document
- Change history preserved in archives with full context (why, alternatives, trade-offs)

### Structure

```
openspec/
├── specs/
│   └── architecture/
│       ├── spec.md          # High-level architecture requirements
│       └── design.md        # Current architectural decisions (living doc)
└── changes/
    └── archive/
        ├── 2024-11-15-adopt-libcst/
        │   ├── proposal.md                     # "Why LibCST over ast"
        │   │                                   # Includes alternatives considered
        │   └── specs/architecture/design.md    # MODIFIED: Analysis Technology
        │                                       # (changed from ast → LibCST)
        └── 2024-12-01-add-plugin-system/
            ├── proposal.md
            └── specs/
                ├── architecture/design.md      # MODIFIED: Added plugin patterns
                └── plugins/spec.md             # ADDED: Plugin capability
```

### Benefits

**Current architecture:**
- ✅ ONE document: `specs/architecture/design.md`
- ✅ Always up-to-date (delta merging ensures synchronization)
- ✅ Clear picture of "how things work now"

**Historical decisions:**
- ✅ Preserved in archives with full context
- ✅ Can grep to find "when did we decide X"
- ✅ Proposal includes alternatives considered and trade-offs
- ✅ No superseded ADRs cluttering index

**vs Traditional ADRs:**
- ❌ ADRs: Multiple documents to understand current state
- ✅ Deltas: Single document is source of truth
- ❌ ADRs: Superseded ones pile up
- ✅ Deltas: Archives organized by date, easy to ignore
- ❌ ADRs: Can drift out of sync
- ✅ Deltas: Automatically synchronized

### When to Use Traditional ADR vs Architecture Delta

**Traditional ADR (keep in decisions/*.rst):**
- Cross-cutting decisions that don't map to a specific capability
- Organizational/process decisions (not technical architecture)
- Repository structure decisions
- Tooling choices that don't affect architecture
- Example: "Use Copier for template management"

**Architecture Delta (use Openspec changes):**
- Technology choices affecting system design
  - "Use LibCST instead of ast for code analysis"
- Pattern decisions
  - "Adopt visitor pattern for rule implementation"
- Structure decisions
  - "Modular hybrid architecture for linter core"
- Integration patterns
  - "Plugin system architecture"

### Example: Technology Decision

**Current approach (ADR-002):**
```rst
ADR-002: Syntax Tree Analysis Technology
Status: Accepted

Context: Need to analyze Python code structure...
Decision: Use LibCST for concrete syntax tree analysis
Alternatives: ast, parso, rope
Consequences: ...
```

**Proposed approach (Architecture Delta):**
```
changes/archive/2024-11-15-adopt-libcst/
├── proposal.md
│   # Why
│   Need to analyze Python code while preserving whitespace and comments.
│
│   # What Changes
│   - Affected specs: architecture
│   - Technology: ast → LibCST
│
│   # Alternatives Considered
│   1. ast module - loses formatting information
│   2. parso - less maintained, weaker typing
│   3. rope - refactoring-focused, heavyweight
│   4. LibCST - preserves concrete syntax, strong typing ✓
│
│   # Trade-offs
│   - Performance: Slower than ast (acceptable for linter use case)
│   - Complexity: Steeper learning curve (better documentation mitigates)
│   - Benefits: Preserves all syntax details, enables auto-fixes
│
└── specs/architecture/design.md
    ## MODIFIED Requirements

    ### Component: CST Analysis Technology
    The linter SHALL use LibCST (Concrete Syntax Tree) for Python code analysis
    to preserve whitespace, comments, and exact syntax representation.

    **Rationale:** Enables auto-fixing rules while maintaining code formatting.
    **Alternatives considered:** ast (loses formatting), parso (less maintained)
    **Trade-offs:** ~2x slower than ast, acceptable for linter workload
```

After archive, `specs/architecture/design.md` contains current state.
The archive preserves the full decision context with alternatives and rationale.

## Workflow for Architecture Changes

### Creating an Architecture Decision

```
1. User: "We should use LibCST instead of ast"
2. /openspec:proposal adopt-libcst
   → Creates change directory
   → Writes proposal.md with:
      - Why LibCST is needed
      - Alternatives considered (ast, parso, rope)
      - Trade-off analysis
      - Impact on system
   → Creates delta spec modifying specs/architecture/design.md
   → Includes reasoning in delta comments
3. User approves proposal
4. /openspec:apply adopt-libcst
   → Implements change (switch to LibCST)
   → Updates implementation to use new technology
5. openspec archive adopt-libcst
   → Merges delta to specs/architecture/design.md
   → Archives proposal with full decision context
   → Current architecture updated ✓
```

### Viewing Current Architecture

```bash
# See current architectural decisions
cat openspec/specs/architecture/design.md

# See all components, patterns, technologies currently in use
openspec show architecture --type spec
```

### Researching Decision History

```bash
# When was LibCST adopted?
ls openspec/changes/archive | grep libcst
# 2024-11-15-adopt-libcst

# Why did we choose LibCST?
cat openspec/changes/archive/2024-11-15-adopt-libcst/proposal.md
# See full context: alternatives, trade-offs, rationale
```

## Migration from ADRs to Architecture Deltas

**Approach 1: Keep existing ADRs, use deltas going forward**
- Existing ADRs in decisions/*.rst stay as-is
- New architectural decisions use Openspec changes
- Create initial `specs/architecture/design.md` summarizing current state from all ADRs
- Going forward, deltas modify that living document

**Approach 2: Migrate all ADRs to architecture spec**
- Create comprehensive `specs/architecture/design.md` capturing current architecture
- Convert each ADR to an archived change showing the delta it introduced
- More work, but cleaner long-term

### Phased Migration (Recommended)

**Phase 1: Keep hybrid**
- Existing ADRs remain in decisions/*.rst
- Create initial specs/architecture/design.md
- New decisions use Openspec deltas

**Phase 2: Evaluate**
- After 3-6 months, assess if delta approach works
- If successful, consider migrating old ADRs
- If not, revert to traditional ADRs

## Architecture Document Contents

### specs/architecture/spec.md (Requirements)

High-level architectural requirements:

```markdown
### Requirement: Modularity
The system SHALL be organized into independent, loosely-coupled modules.

#### Scenario: Module independence
- **WHEN** a module is modified
- **THEN** other modules are not affected
- **AND** interfaces remain stable

### Requirement: Extensibility
The system SHALL support adding new capabilities without modifying core components.

#### Scenario: Plugin addition
- **WHEN** a new plugin is added
- **THEN** no core code changes are required
- **AND** plugin integrates via defined interfaces
```

### specs/architecture/design.md (Current Decisions)

Detailed architectural decisions:

```markdown
## Component: Code Analysis

### Technology: LibCST
The linter uses LibCST for concrete syntax tree analysis.

**Rationale:** Preserves whitespace and comments, enabling auto-fix capabilities.
**Alternatives considered:** ast (loses formatting), parso (less maintained)
**Trade-offs:** ~2x slower than ast, acceptable for linter workload
**Decided:** 2024-11-15 (see changes/archive/2024-11-15-adopt-libcst/)

### Pattern: Visitor Pattern
Rules implement LibCST visitor pattern for CST traversal.

**Rationale:** Composable, single-pass analysis, integrates with metadata providers.
**Decided:** 2024-11-17 (see changes/archive/2024-11-17-visitor-pattern/)

## Component: Plugin System

### Architecture: Registry-Based Loading
Plugins register via central registry manager at application startup.

**Rationale:** Explicit registration, controlled initialization order.
**Decided:** 2024-12-01 (see changes/archive/2024-12-01-add-plugin-system/)
```

Each section references the archived change where the decision was made.

## Custom Tooling Considerations

If Openspec proves insufficient for architecture management:

**Potential needs:**
- More sophisticated querying ("what decisions affected module X?")
- Dependency tracking between decisions
- Automatic generation of architecture diagrams from specs
- Better visualization of decision history

**Options:**
1. Extend Openspec with custom scripts
2. Build Python tooling in emcdproj
3. Use external architecture documentation tools

**Decision:** Validate basic Openspec workflow first, then assess tooling gaps.

## Tasks (When Ready)

### Prerequisites
- [ ] Validate Openspec workflow with designs/specs (see openspec-designs.md)
- [ ] Confirm delta merging works as expected
- [ ] Establish comfort with change proposal process

### Setup
- [ ] Create specs/architecture/ directory
- [ ] Write initial architecture/spec.md (high-level requirements)
- [ ] Write initial architecture/design.md (current state from existing ADRs)

### Migration Strategy Decision
- [ ] Decide: Keep existing ADRs or migrate to deltas?
- [ ] Document migration approach chosen
- [ ] Create migration plan if converting existing ADRs

### Workflow Integration
- [ ] Update /cs-architect to optionally create Openspec changes
- [ ] Document when to use ADR vs architecture delta
- [ ] Update CLAUDE.md with decision tree

### Validation
- [ ] Test creating architecture decision as Openspec change
- [ ] Test archiving and verifying delta merge
- [ ] Verify history is preserved and searchable
- [ ] Assess if approach works better than traditional ADRs

## Open Questions

1. **Granularity:** Should all architecture decisions go in one `architecture/` spec, or separate specs for different architectural layers (e.g., `architecture-frontend/`, `architecture-backend/`)?

2. **Cross-cutting decisions:** How to handle decisions that affect multiple capabilities? (Example: "All APIs must be async")

3. **Visualization:** How to generate architecture diagrams from spec files?

4. **Querying:** How to answer questions like "what decisions were made in 2024?" or "what decisions affect the plugin system?"

5. **Tooling gaps:** What functionality would require custom tooling beyond Openspec CLI?

## References

- Main integration plan: `openspec-designs.md`
- ADR format background: https://github.com/joelparkerhenderson/architecture-decision-record
- Openspec documentation: https://github.com/Fission-AI/OpenSpec
