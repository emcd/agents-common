# configuration-management (delta)

## MODIFIED Requirements

### Requirement: Data-Driven Repository Structure

The repository SHALL organize AI tool configurations as structured data sources
with 3-tier separation to enable tool-agnostic maintenance while generating
tool-specific outputs.

#### Scenario: Skills as a first-class item type
- **WHEN** reusable expertise is added to the repository
- **THEN** it can be represented as “skills” with:
  - tool-agnostic metadata
  - a tool-agnostic body by default (with optional tool-specific overrides)
  - templates that emit tool-compatible frontmatter and discovery paths

#### Scenario: Tool-specific permissions mapping
- **WHEN** a skill specifies “allowed tools” in tool-agnostic semantic form
- **THEN** the system maps/format those tool specifications per coder where
  supported
- **AND** the system omits or warns for fields that are unsupported by a given
  target tool (without failing generation)
