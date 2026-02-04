# multi-tool-support

## Purpose

Enables extensible content generation for multiple AI development tools without restructuring existing data sources. Supports clean addition of new tools through plugin architecture.
## Requirements
### Requirement: Multi-Tool Content Generation

The system SHALL support extensible content generation for multiple AI tools
without restructuring existing data sources when new tools are added.

#### Scenario: Adding the Agent Skills format
- **WHEN** the Agent Skills format is added
- **THEN** only the new `skills/` source directories and templates are added
- **AND** existing `commands/` and `agents/` sources remain valid
 - **AND** skill outputs are generated per coder under
   `.auxiliary/configuration/coders/<coder>/skills/` without changing existing
   output layouts

