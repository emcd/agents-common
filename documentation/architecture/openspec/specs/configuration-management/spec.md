# configuration-management

## Purpose

Provides structured, data-driven storage for AI agent configurations that remain tool-agnostic while enabling generation of tool-specific outputs. Maintains single source of truth for commands, agents, and related tooling across multiple AI development environments.

## Requirements

### Requirement: Data-Driven Repository Structure

The repository SHALL organize AI tool configurations as structured data sources with 3-tier separation to enable tool-agnostic maintenance while generating tool-specific outputs.

Priority: Critical

#### Scenario: Three-tier data organization
- **WHEN** configurations are stored
- **THEN** repository uses `defaults/` directory with three separate tiers
- **AND** configurations/ contains tool-agnostic metadata
- **AND** contents/ contains coder-specific content bodies
- **AND** templates/ contains generic Jinja2 templates

#### Scenario: Tool-agnostic metadata
- **WHEN** slash command or agent metadata is defined
- **THEN** TOML configurations provide semantic allowed-tools specifications
- **AND** metadata remains independent of specific AI tool formats

#### Scenario: Coder-specific content fallback
- **WHEN** content is needed for a specific AI tool
- **THEN** system uses appropriate coder-specific content
- **AND** supports fallback strategies (Claude ↔ Opencode, Gemini isolated)

#### Scenario: Consistent terminology
- **WHEN** directories are created
- **THEN** naming follows consistent terminology conventions
- **AND** supports comprehensive slash command and agent metadata definitions

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
