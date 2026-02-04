# configuration-management

## Purpose

Provides structured, data-driven storage for AI agent configurations that remain tool-agnostic while enabling generation of tool-specific outputs. Maintains single source of truth for commands, agents, and related tooling across multiple AI development environments.
## Requirements
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

### Requirement: Structured Source Data Management

The system SHALL maintain structured source data that generates content for multiple AI tools from single sources while supporting diverse tool formats.

Priority: Critical

#### Scenario: Single source of truth
- **WHEN** command or agent is defined
- **THEN** metadata stored in tool-agnostic TOML configurations
- **AND** single source drives generation for all supported AI tools

#### Scenario: Content body separation
- **WHEN** tool-specific content is needed
- **THEN** content bodies separated by coder
- **AND** appropriate fallback strategies applied

#### Scenario: Format handling
- **WHEN** different AI tools require different formats
- **THEN** generic templates handle format differences
- **AND** transformations applied at generation time

#### Scenario: Hook script distribution
- **WHEN** hook scripts are distributed
- **THEN** distributed via minimal Copier template
- **AND** not dynamically generated

