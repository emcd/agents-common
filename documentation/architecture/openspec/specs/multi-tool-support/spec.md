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

### Requirement: Multi-Tool Skill Distribution

The system SHALL distribute OPSX workflow skills as portable agentsmgr defaults that work across all configured coders.

#### Scenario: OPSX skill set
- **WHEN** OPSX skills are distributed through agentsmgr
- **THEN** skills cover the complete OPSX workflow (`propose`, `apply`, `archive`, `explore`, `sync`)
- **AND** skills use the `opsx-*` naming convention
- **AND** skills are discovered from `distribution/per-project/general/skills/opsx-*.md`

#### Scenario: Skill portability
- **WHEN** OPSX skills are distributed
- **THEN** the skill body is tool-agnostic
- **AND** skills are direct distribution artifacts (not generated from components)
- **AND** skills reference `openspec` CLI for dynamic instruction assembly

#### Scenario: Skill sanitization
- **WHEN** OPSX skills are curated for template distribution
- **THEN** `stores` guidance is removed from all skills
- **AND** skills remain functional without store configuration

#### Scenario: Old command removal
- **WHEN** OPSX skills replace old OpenSpec commands
- **THEN** old `openspec-*` commands are deleted from `components/configurations/commands/`
- **AND** skills provide the same workflow through the portable distribution channel

