# path-compatibility

## Purpose

Ensures generated content references correct paths so distributed configurations work correctly in downstream projects. Maintains compatibility with established project deployment patterns.

## Requirements

### Requirement: Generated Content Path Compatibility

The system SHALL ensure generated content references correct paths for compatibility with downstream project deployment patterns.

Priority: Critical

#### Scenario: Configuration path references
- **WHEN** commands and agents are generated
- **THEN** reference .auxiliary/configuration/ paths
- **AND** maintain compatibility with existing projects

#### Scenario: Hook script paths
- **WHEN** hook scripts are distributed via Copier template
- **THEN** scripts function correctly when deployed
- **AND** path references remain valid

#### Scenario: Template reference validity
- **WHEN** agentsmgr populate generates content
- **THEN** template references remain valid after generation
- **AND** paths resolve correctly in target projects

#### Scenario: Targeting mode support
- **WHEN** content is generated
- **THEN** supports per-user targeting mode
- **AND** supports per-project targeting mode
- **AND** manages symlinks appropriately for each mode
