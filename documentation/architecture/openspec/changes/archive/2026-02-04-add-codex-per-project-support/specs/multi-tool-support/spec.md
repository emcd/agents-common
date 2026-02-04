# multi-tool-support (delta)

## MODIFIED Requirements

### Requirement: Multi-Tool Content Generation

The system SHALL support extensible content generation for multiple AI tools
without restructuring existing data sources when new tools are added.

#### Scenario: Adding Codex per-project support
- **WHEN** Codex is enabled for a project
- **THEN** Codex outputs are generated in per-project mode by default
- **AND** only Codex-specific templates and directories are added
- **AND** existing `configurations/` and `contents/` sources remain compatible
