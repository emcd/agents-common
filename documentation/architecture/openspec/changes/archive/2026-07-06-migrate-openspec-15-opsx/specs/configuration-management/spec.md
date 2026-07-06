## MODIFIED Requirements

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

#### Scenario: OPSX skill distribution
- **WHEN** OpenSpec 1.5 OPSX skills are distributed
- **THEN** curated OPSX skill files are shipped as `agentsmgr` defaults under `defaults/contents/skills/`
- **AND** skills have `stores` guidance removed for template safety
- **AND** skills are discoverable through the standard skills pipeline
