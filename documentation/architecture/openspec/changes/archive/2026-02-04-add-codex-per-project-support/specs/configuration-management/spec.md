# configuration-management (delta)

## MODIFIED Requirements

### Requirement: Structured Source Data Management

The system SHALL maintain structured source data that generates content for
multiple AI tools from single sources while supporting diverse tool formats.

#### Scenario: Codex per-project configuration storage
- **WHEN** Codex per-project configuration is generated
- **THEN** the canonical file is stored under
  `.auxiliary/configuration/coders/codex/config.toml`
- **AND** it is exposed to Codex at `.codex/config.toml` via symlink
