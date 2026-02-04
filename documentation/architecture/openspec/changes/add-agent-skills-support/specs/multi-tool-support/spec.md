# multi-tool-support (delta)

## MODIFIED Requirements

### Requirement: Multi-Tool Content Generation

The system SHALL support extensible content generation for multiple AI tools
without restructuring existing data sources when new tools are added.

#### Scenario: Adding the Agent Skills format
- **WHEN** the Agent Skills format is added
- **THEN** only the new `skills/` source directories and templates are added
- **AND** existing `commands/` and `agents/` sources remain valid

