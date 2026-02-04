# path-compatibility (delta)

## MODIFIED Requirements

### Requirement: Generated Content Path Compatibility

The system SHALL ensure generated content references correct paths for
compatibility with downstream project deployment patterns.

#### Scenario: Stable skill discovery path
- **WHEN** skills are generated for a project
- **THEN** they are discoverable at a stable root path (e.g. `.skills/`)
- **AND** the underlying source of truth remains under
  `.auxiliary/configuration/`

