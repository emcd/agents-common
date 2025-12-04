Please migrate documentation from RST to Openspec Markdown format.

## Phase 1: PRD Migration (If Exists)

If `documentation/prd.rst` exists:

1. **Analyze and group requirements** into logical user-facing capabilities
2. **Verify implementation** by checking if requirements are actually implemented in `sources/`
3. **Create capability specs** as `documentation/architecture/openspec/specs/[capability]/spec.md`

**Spec structure:**

```markdown
# [capability-name]

## Purpose
[What this capability does and why users need it]

## Requirements

### Requirement: [Name]
[User/system SHALL statement]

Priority: [Critical/High/Medium/Low]

#### Scenario: [Use case]
- **WHEN** [condition]
- **THEN** [expected behavior]
- **AND** [additional outcomes]
```

## Phase 2: Design Migration

For each `documentation/architecture/designs/*.rst` file:

1. **Convert RST to Markdown** using `rst2myst convert` or `pandoc`:
   ```bash
   rst2myst convert documentation/architecture/designs/example.rst
   # Creates example.md in same directory
   # OR
   pandoc -f rst -t markdown documentation/architecture/designs/example.rst -o /tmp/example.md
   ```

2. **Map to capability:**
   - Check if spec already exists from Phase 1
   - If yes, add to existing `specs/[capability]/design.md`
   - If no, create new spec first, then add design.md
   - If cross-cutting, split across multiple design.md files

3. **Editorial cleanup:**
   - Fix any conversion artifacts
   - Verify code blocks have proper syntax highlighting
   - Update cross-references to use Markdown links
   - Ensure technical accuracy and completeness

**Design structure:**

```markdown
# [capability-name] Design

## Overview
[High-level architectural summary]

## Design
[Component descriptions, patterns, system structure]

## Module Contracts
[Responsibilities, collaborators, invariants]

## Implementation Patterns
[Coding patterns, examples, guidance]

## Trade-offs and Alternatives
[Design decisions, alternatives considered, rationale]

## Performance Characteristics
[Performance properties, scaling considerations]

## Extension Points
[How to extend or customize]

## Testing Considerations
[Testing strategies, integration points]

## Future Considerations
[Deferred work, potential enhancements]
```

## Validation

After migration:

```bash
openspec validate --specs --strict
hatch --env develop run docsgen  # Verify Sphinx rendering
```
