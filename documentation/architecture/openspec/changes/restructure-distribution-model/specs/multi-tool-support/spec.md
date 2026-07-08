## MODIFIED Requirements

### Requirement: Multi-Tool Skill Distribution

The system SHALL distribute OPSX workflow skills as portable agentsmgr defaults that work across all configured coders.

#### Scenario: OPSX skill set
- **WHEN** OPSX skills are distributed through agentsmgr
- **THEN** skills cover the complete OPSX workflow (`propose`, `apply`, `archive`, `explore`, `sync`)
- **AND** skills use the `opsx-*` naming convention
- **AND** skills are discovered from `distribution/per-project/general/skills/opsx-*.md`

#### Scenario: Skill portability
- **WHEN** OPSX skills are distributed through agentsmgr
- **THEN** the skill body is tool-agnostic and distributed as-is (source == output)
- **AND** skills reference `openspec` CLI for dynamic instruction assembly

#### Scenario: Skill sanitization
- **WHEN** OPSX skills are curated for template distribution
- **THEN** `stores` guidance is removed from all skills
- **AND** skills remain functional without store configuration

#### Scenario: Old command removal
- **WHEN** OPSX skills replace old OpenSpec commands
- **THEN** old `openspec-*` commands are deleted from distribution
- **AND** skills provide the same workflow through the portable distribution channel
