# Migration Prompt: Designs and PRD to Openspec

## Purpose

This document provides prompts to give to LLMs to assist with migrating existing design documents and product requirements to Openspec format.

## Migration Strategy

### Recommended Order: PRD First, Then Designs

**Phase 1: PRD → Capability Specs** (Requirements-driven)
1. Analyze PRD functional requirements
2. Group into logical capabilities from user perspective
3. Create `specs/[capability]/spec.md` with scenarios
4. Result: Capability structure driven by user needs

**Phase 2: Designs → Capability Design Docs** (Implementation-supporting)
1. For each design in `designs/*.rst`:
   - Identify which capability/capabilities it supports
   - Extract technical content
   - Add to `specs/[capability]/design.md`
2. Handle special cases:
   - Cross-cutting designs (split appropriately)
   - Infrastructure designs (create new capabilities if needed)
   - Orphaned designs (evaluate if still relevant)

**Rationale:**
- ✅ Capability structure reflects user needs, not implementation artifacts
- ✅ Ensures specs align with actual requirements
- ✅ Designs naturally map to existing capabilities
- ✅ Product-oriented organization

**NOT:** Designs first (creates implementation-driven structure that may not align with user needs)

### Conservative Migration Approach

**During migration (parallel existence):**
```
documentation/architecture/
├── designs/           # Keep old RST files here (unchanged)
│   ├── linter-core.rst
│   └── cli.rst
└── openspec/          # New Openspec structure
    ├── project.md
    └── specs/
        ├── linter-core/
        │   ├── spec.md
        │   └── design.md
        └── configuration/
```

**After validation (single cleanup):**
```bash
# When confident, single cleanup step:
rm -rf documentation/architecture/designs/
mv documentation/architecture/openspec documentation/architecture/designs
# Result: documentation/architecture/designs/specs/
```

**Benefits:**
- ✅ No information loss during migration
- ✅ Easy rollback if issues found
- ✅ Can reference old designs while building new
- ✅ Single cleanup step when confident
- ✅ Clearer git history

**NOT:** Immediate archival, symlinking, or parallel naming schemes that create confusion

---

## Migration Prompt: PRD (RST → Openspec Specs)

**Execute this FIRST to establish capability structure**

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
5. **Proceed to Phase 2: Map designs to these capabilities**

---

## Migration Prompt: Design Documents (RST → Openspec)

**Execute this SECOND after PRD migration establishes capability structure**

### Context Requirements

Before migrating designs, you must have:
- ✅ Completed PRD migration (Phase 1)
- ✅ Created capability structure in `openspec/specs/`
- ✅ Validated all capability specs with `openspec validate --specs --strict`

### Mapping Strategy

For each design document:
1. **Identify target capability/capabilities** - Which specs does this design support?
2. **Extract technical content** - Code examples, patterns, architecture
3. **Add to appropriate design.md** - May split across multiple capabilities
4. **Handle special cases:**
   - **1:1 mapping:** `designs/linter-core.rst` → `specs/linter-core/design.md`
   - **Cross-cutting:** `designs/cli.rst` → parts to `specs/configuration/design.md`, parts to `specs/reporting/design.md`
   - **Infrastructure:** Create new capability if no PRD equivalent exists

### Prompt Template

```
I need to migrate a design document from reStructuredText to Openspec format, mapping it to existing capability specifications.

Source document: [path to designs/*.rst]

CONTEXT:
I have already created capability specs from the PRD. The following capabilities exist:
[List existing specs/*/spec.md files]

TASK:
Map the technical content from this design document to the appropriate capability design.md file(s).

OUTPUT STRUCTURE:
For each capability this design supports, provide:
- specs/[capability-name]/design.md (or additions to existing design.md)

MAPPING INSTRUCTIONS:
1. Identify which capability/capabilities this design supports
2. If design maps to multiple capabilities, split content appropriately
3. If design is infrastructure with no PRD mapping, suggest new capability name
4. Preserve all technical content - no information loss

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

For projects with many documents:

### Phase 1: Migrate PRD
1. Run PRD migration prompt with full prd.rst content
2. Review generated capability specs
3. Validate: `openspec validate --specs --strict`
4. Create openspec/project.md with high-level vision
5. **Result:** Capability structure established

### Phase 2: Map Designs to Capabilities
```bash
# List existing capabilities
ls documentation/architecture/openspec/specs/

# List design documents to migrate
ls documentation/architecture/designs/
```

For each design:
1. Identify which capability/capabilities it supports
2. Run design migration prompt with capability context
3. Add technical content to appropriate design.md files
4. Validate updated specs

### Phase 3: Prioritize Design Migration
1. **Core capabilities** - Most referenced designs first
2. **Active capabilities** - Currently developed features
3. **Infrastructure** - Cross-cutting or foundational designs
4. **Stable capabilities** - Rarely changed designs last

### Phase 4: Validate Complete Migration
- [ ] All PRD requirements have specs with scenarios
- [ ] All design content mapped or justified as excluded
- [ ] `openspec validate --specs --strict` passes for all
- [ ] Can create change proposals against new specs
- [ ] Sphinx renders Markdown specs correctly

### Phase 5: Update References (After Validation)
- Update slash commands to reference openspec/specs/
- Update CLAUDE.md with new paths
- Keep old designs/ directory for reference (don't delete yet)
- Test workflow with new structure

### Phase 6: Cleanup (1-2 Release Cycles Later)
```bash
# After validating new structure works:
rm -rf documentation/architecture/designs/
mv documentation/architecture/openspec documentation/architecture/designs
# Update all references in CLAUDE.md, commands, etc.
```

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

## Example: Metrics Export Migration

### Step 1: PRD Creates Capability

**PRD content:**
```rst
FR-001: Export Metrics
Users shall export usage metrics in JSON format
Priority: High
```

**Becomes:**
```
specs/metrics-export/spec.md:

### Requirement: Metrics Export
Users SHALL export usage metrics to analyze usage patterns.

Priority: High

#### Scenario: JSON export success
- **WHEN** user requests metrics export
- **THEN** system provides JSON formatted output
```

### Step 2: Design Maps to Capability

**Design content (designs/api.rst):**
```rst
Export API
===========

The export API provides metrics data via REST endpoints.

Endpoint: GET /api/metrics/export
Returns: JSON formatted metrics data
```

**Maps to:**
```
specs/metrics-export/design.md:

## API Architecture

### Export Endpoint
REST endpoint for metrics export.

**Endpoint:** `GET /api/metrics/export`
**Response:** JSON formatted metrics data
```

**Result:** Design content naturally fits into capability established by PRD requirements.
