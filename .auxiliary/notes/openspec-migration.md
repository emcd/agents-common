# Migration Prompt: Designs and PRD to Openspec

## Purpose

This document provides prompts to give to LLMs to assist with migrating existing design documents and product requirements to Openspec format.

## Migration Prompt: Design Documents (RST → Openspec)

### Prompt Template

```
I need to migrate a design document from reStructuredText to Openspec format.

Source document: [path to designs/*.rst]

Please convert this design document into two Openspec files following these guidelines:

OUTPUT STRUCTURE:
1. spec.md - Requirements and expected behaviors
2. design.md - Technical architecture and implementation patterns

SPEC.MD FORMAT:
- Extract all functional requirements from the design
- Format each as a "Requirement" with scenarios
- Use this structure:

```markdown
# [Capability Name] Specification

## Purpose
[Brief description of what this capability does and why it exists]

## Requirements

### Requirement: [Clear requirement name]
[SHALL/MUST statement describing the requirement]

#### Scenario: [Success case]
- **WHEN** [condition or action]
- **THEN** [expected result]
- **AND** [additional constraints if applicable]

#### Scenario: [Error case]
- **WHEN** [error condition]
- **THEN** [expected error handling]
```

DESIGN.MD FORMAT:
- Convert architecture sections to Markdown
- Preserve code examples (convert RST code-blocks to Markdown fenced code)
- Keep technical details, patterns, and implementation guidance
- Maintain cross-references (convert RST references to Markdown links)
- Structure:

```markdown
# [Capability Name] Design

## Architecture Overview
[High-level component description]

## Components
### [Component Name]
[Description, responsibilities, patterns]

## Data Structures
[Type definitions, schemas, examples]

## Implementation Patterns
[Coding patterns, examples, anti-patterns]

## Integration Points
[How this integrates with other capabilities]

## Technical Decisions
[Key design choices and rationale]
```

CONVERSION GUIDELINES:
1. Preserve all technical content - no information loss
2. Extract requirements from prose into structured scenarios
3. Convert RST directives to Markdown equivalents:
   - `.. code-block:: python` → ` ```python `
   - `:doc:\`filename\`` → `[link](../path/to/file.md)`
   - `**emphasis**` → `**emphasis**` (same)
4. Use WHEN/THEN format for all behavioral requirements
5. Keep code examples with proper syntax highlighting
6. Maintain semantic structure (headings, lists, emphasis)

SOURCE DOCUMENT:
[Paste content of designs/*.rst file here]

Please provide both spec.md and design.md in full.
```

### Example Conversion

**Input (designs/linter-core.rst):**
```rst
Linter Core Framework Design
*******************************************************************************

This document specifies the core linter framework design implementing the
validated hybrid modular architecture from ADR-001.

Core Framework Architecture
===============================================================================

The linter core consists of five primary components:

**Violation Data Structures**
  Immutable data classes representing rule violations.

**BaseRule Framework**
  Abstract base class providing collection-then-analysis pattern.

Data Structure Design
===============================================================================

The violation data structures follow immutable design patterns:

.. code-block:: python

    class Violation( __.immut.DataclassObject ):
        ''' Represents a rule violation. '''
        rule_id: str
        filename: str
        line: int
        message: str
```

**Output (specs/linter-core/spec.md):**
```markdown
# linter-core Specification

## Purpose
Provides the foundational framework for implementing linting rules with
violation collection and reporting.

## Requirements

### Requirement: Violation Reporting
The framework SHALL provide immutable data structures for representing
rule violations with precise location information.

#### Scenario: Violation creation
- **WHEN** a rule detects a violation
- **THEN** a Violation object is created
- **AND** includes file path, line number, and message

### Requirement: Rule Execution
The framework SHALL execute rules using collection-then-analysis pattern.

#### Scenario: Single-pass analysis
- **WHEN** the engine processes a file
- **THEN** all rules collect data in one pass
- **AND** analysis occurs after collection completes
```

**Output (specs/linter-core/design.md):**
```markdown
# linter-core Design

## Architecture Overview
The linter core implements a hybrid modular architecture with five primary
components forming the analysis pipeline.

## Components

### Violation Data Structures
Immutable data classes representing rule violations with precise location
information and context extraction capabilities.

**Implementation:**
```python
class Violation( __.immut.DataclassObject ):
    ''' Represents a rule violation. '''
    rule_id: str
    filename: str
    line: int
    message: str
```

### BaseRule Framework
Abstract base class providing the collection-then-analysis pattern with
LibCST metadata integration.

## Implementation Patterns

### Collection-Then-Analysis Pattern
Rules collect data during CST traversal, then analyze collected data:
1. Visit phase: Collect relevant nodes
2. Analysis phase: Process collected data
3. Reporting phase: Generate violations
```

---

## Migration Prompt: PRD (RST → Openspec Specs)

### Prompt Template

```
I need to migrate a Product Requirements Document to Openspec specification format.

Source document: documentation/prd.rst

Please analyze the PRD and create multiple capability specs following these guidelines:

ANALYSIS TASK:
1. Identify distinct capabilities/features in the PRD
2. Group related functional requirements under each capability
3. Create separate spec directories for each capability

OUTPUT STRUCTURE:
For each capability, create:
- specs/[capability-name]/spec.md

SPEC.MD FORMAT:

```markdown
# [Capability Name] Specification

## Purpose
[What this capability does and why users need it]
[Reference user personas if applicable]

## Requirements

### Requirement: [Requirement Name]
[User/system SHALL statement from functional requirement]

Priority: [Critical/High/Medium/Low from PRD]

#### Scenario: [Primary use case]
- **WHEN** [user action or condition]
- **THEN** [expected system behavior]
- **AND** [additional outcomes]

#### Scenario: [Error case]
- **WHEN** [error condition]
- **THEN** [error handling behavior]

#### Scenario: [Edge case]
- **WHEN** [edge condition]
- **THEN** [expected behavior]

### Requirement: [Next requirement]
...
```

CONVERSION GUIDELINES:
1. Functional Requirement → Requirement with scenarios
2. User Story → Scenario (convert "As a... I want... So that..." to WHEN/THEN)
3. Acceptance Criteria → Additional scenarios
4. Non-Functional Requirements → Add to relevant capability specs
5. Goals/Objectives → spec.md Purpose section
6. User Personas → Reference in Purpose sections
7. Constraints → Document in relevant specs as requirements

EXAMPLE MAPPING:

PRD Functional Requirement:
```
FR-001: Export Metrics (Priority: High)
Users shall export usage metrics in JSON format to analyze application usage.

Acceptance Criteria:
- JSON output includes all tracked metrics
- Export completes within 5 seconds
- Invalid requests return error messages
```

Becomes specs/metrics-export/spec.md:
```markdown
# metrics-export Specification

## Purpose
Enables users to export application usage metrics for analysis and reporting.
Target users: Administrators, data analysts

## Requirements

### Requirement: Metrics Export
Users SHALL export usage metrics to analyze application usage patterns.

Priority: High

#### Scenario: JSON export success
- **WHEN** user requests metrics export
- **THEN** system provides JSON formatted output
- **AND** includes all tracked metrics
- **AND** completes within 5 seconds

#### Scenario: Invalid export request
- **WHEN** export request has invalid parameters
- **THEN** system returns descriptive error message
- **AND** no partial data is exported
```

CAPABILITY IDENTIFICATION:
Group requirements into capabilities based on:
- User-facing features (authentication, reporting, configuration)
- System components (storage, API, plugin system)
- Functional domains (user management, data export, notifications)

SOURCE DOCUMENT:
[Paste content of prd.rst file here]

Please provide:
1. List of identified capabilities
2. Full spec.md for each capability
3. Recommendations for project.md content (goals, vision, personas)
```

### Post-Migration Tasks

After receiving LLM output:
1. Review generated specs for completeness
2. Validate scenario format: `openspec validate --specs --strict`
3. Create project.md with high-level goals and vision from PRD
4. Cross-reference related specs
5. Update Sphinx documentation to include new specs

---

## Validation Checklist

After migration:

### Structure Validation
- [ ] Each capability has specs/[name]/spec.md
- [ ] Design-heavy capabilities have specs/[name]/design.md
- [ ] All specs follow Openspec format
- [ ] `openspec validate --specs --strict` passes

### Content Validation
- [ ] All functional requirements converted to Requirements
- [ ] All requirements have at least one Scenario
- [ ] Scenarios use WHEN/THEN format
- [ ] Code examples have proper syntax highlighting
- [ ] Cross-references updated to Markdown links
- [ ] Priority levels preserved
- [ ] No information lost from original documents

### Documentation Validation
- [ ] Sphinx renders Markdown specs correctly
- [ ] Code examples display properly
- [ ] Links work correctly
- [ ] Generated docs match original quality

### Process Validation
- [ ] Can create change proposals against new specs
- [ ] Delta format works for ADDED/MODIFIED/REMOVED
- [ ] Archive process merges deltas correctly
- [ ] Workflow integrates with slash commands

---

## Iterative Refinement Prompt

If LLM output needs refinement:

```
The generated specs need refinement. Please address these issues:

ISSUES:
[List specific problems, e.g.:]
- Scenario X doesn't use WHEN/THEN format correctly
- Requirement Y is too vague, needs specificity
- Code example Z lost syntax highlighting
- Missing scenarios for error cases in Requirement A

REQUIREMENTS:
- All scenarios must follow strict WHEN/THEN format
- Requirements must be specific and testable
- Preserve all code examples with syntax highlighting
- Include success, error, and edge case scenarios for each requirement

Please provide corrected versions of the affected sections.
```

---

## Batch Migration Strategy

For projects with many design docs:

### Phase 1: Identify Capabilities
```bash
# List all design documents
ls documentation/architecture/designs/

# Identify which map to distinct capabilities
# Example: linter-core.rst, cli.rst, configuration.rst
```

### Phase 2: Prioritize
1. Core capabilities (most referenced)
2. Actively developed capabilities
3. Stable, rarely changed capabilities

### Phase 3: Migrate Iteratively
- One capability at a time
- Validate each before moving to next
- Test change proposal workflow on each

### Phase 4: Update References
- Update slash commands to reference new locations
- Update CLAUDE.md with new paths
- Redirect old design links if needed

---

## Common Conversion Patterns

### RST → Markdown

| RST | Markdown |
|-----|----------|
| `.. code-block:: python` | ` ```python ` |
| `:doc:\`filename\`` | `[filename](path.md)` |
| `:ref:\`label\`` | `[label](#anchor)` |
| `**bold**` | `**bold**` |
| `*italic*` | `*italic*` |
| `` `code` `` | `` `code` `` |
| Heading with underline | `## Heading` |

### Requirements Extraction Patterns

| PRD Format | Spec Format |
|------------|-------------|
| "FR-001: Users shall..." | "### Requirement: [Name]\nUsers SHALL..." |
| "As a user, I want..." | "#### Scenario: [Name]\n- **WHEN** user..." |
| "Acceptance: System must..." | "- **THEN** system..." |
| "Priority: High" | "Priority: High" (after requirement) |
| "Non-functional: Performance" | Separate requirement with scenarios |

---

## Post-Migration Cleanup

After successful migration:

```bash
# Archive old designs (don't delete immediately)
mkdir -p documentation/architecture/designs-archived
mv documentation/architecture/designs/*.rst documentation/architecture/designs-archived/

# Create symlink for backward compatibility
ln -s ../openspec/specs documentation/architecture/designs

# Update git to track new locations
git add documentation/architecture/openspec/specs/
git rm documentation/prd.rst
git commit -m "Migrate designs and PRD to Openspec format."
```

Keep archived files for 1-2 release cycles to ensure nothing was lost.
