# path-compatibility (delta)

## MODIFIED Requirements

### Requirement: Generated Content Path Compatibility

The system SHALL ensure generated content references correct paths for
compatibility with downstream project deployment patterns.

#### Scenario: Codex per-project config paths
- **WHEN** Codex per-project configuration is populated
- **THEN** `.codex/config.toml` exists in the project root (directly or via
  symlink)
