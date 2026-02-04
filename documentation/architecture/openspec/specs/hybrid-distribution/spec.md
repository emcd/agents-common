# hybrid-distribution

## Purpose

Combines proven Copier template distribution for static base configuration with dynamic CLI-based content generation for rapid iteration. Enables fast updates to agent configurations without requiring full template releases.

## Requirements

### Requirement: Hybrid Distribution Architecture

The system SHALL combine base configuration templates with dynamic content generation to maintain proven distribution for static templates while enabling fast iteration for dynamic content.

Priority: High

#### Scenario: Minimal Copier template
- **WHEN** base configuration is distributed
- **THEN** minimal Copier template provides base settings templates
- **AND** provides directory structure
- **AND** handles hook path references
- **AND** handles MCP server configurations

#### Scenario: Dynamic content generation
- **WHEN** tool-specific content is needed
- **THEN** agentsmgr CLI generates content from structured data
- **AND** supports detect, populate, and validate commands

#### Scenario: Generated content management
- **WHEN** content is generated
- **THEN** generated content ignored via .gitignore patterns
- **AND** not committed to project repositories

#### Scenario: Configuration detection
- **WHEN** agentsmgr CLI runs
- **THEN** detects configuration from Copier answers files
- **AND** falls back to defaults when answers not available

#### Scenario: Plugin-based source handlers
- **WHEN** content sources are accessed
- **THEN** supports plugin-based source handlers
- **AND** includes git and local filesystem handlers
- **AND** provides extensible architecture for new handlers
