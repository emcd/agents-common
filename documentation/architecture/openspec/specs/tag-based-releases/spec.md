# tag-based-releases

## Purpose

Enables lightweight, rapid configuration updates through tag-based versioning without requiring heavyweight project releases. Provides atomic, consistent deployment of configuration changes.

## Requirements

### Requirement: Tag-Based Release Distribution

The system SHALL support lightweight tag-based releases for rapid configuration updates without heavyweight project release processes.

Priority: High

#### Scenario: Tag versioning scheme
- **WHEN** releases are published
- **THEN** repository supports agents-N tag versioning
- **AND** uses sequential numbering (agents-1, agents-2, etc.)

#### Scenario: Version pinning
- **WHEN** CLI tooling pulls configurations
- **THEN** can pull from specific tagged versions
- **AND** supports full source@ref#subdir syntax
- **AND** downstream projects can pin to known-good versions

#### Scenario: Latest tag fallback
- **WHEN** no explicit ref specified
- **THEN** CLI tooling uses latest tag
- **AND** provides predictable default behavior

#### Scenario: Automated deployment
- **WHEN** tags are created
- **THEN** publishing workflow automatically deploys tagged releases
- **AND** completes within 5 minutes of tag creation

#### Scenario: Rollback capability
- **WHEN** issues found with a release
- **THEN** projects can rollback to previous tag
- **AND** provides atomic, consistent configuration state
