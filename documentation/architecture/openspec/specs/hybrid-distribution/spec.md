# hybrid-distribution

## Purpose

Combines proven Copier template distribution for static base configuration with dynamic CLI-based content generation for rapid iteration. Enables fast updates to agent configurations without requiring full template releases.

## Requirements

### Requirement: Hybrid Distribution Architecture

The system SHALL combine Copier template distribution for base configuration
with agentsmgr CLI distribution for managed artifacts, maintaining a clear
separation between tracked and managed content.

Priority: High

#### Scenario: Minimal Copier template
- **WHEN** base configuration is distributed
- **THEN** minimal Copier template provides base settings templates
- **AND** provides directory structure
- **AND** handles hook path references
- **AND** handles MCP server configurations

#### Scenario: Two-tier downstream model
- **WHEN** a downstream repo is configured
- **THEN** tracked files are managed by Copier (project-owned, merge-friendly)
- **AND** managed artifacts are distributed by agentsmgr (git-ignored at file level)
- **AND** downstream custom skills/commands appear naturally in `git status`

#### Scenario: File-level exclude management
- **WHEN** agentsmgr distributes artifacts downstream
- **THEN** it manages `.git/info/exclude` at the individual-file level
- **AND** blanket directory ignores are not used
- **AND** ownership is derived from the current `distribution/` tree

#### Scenario: Pre-generated artifacts
- **WHEN** command/agent artifacts are produced
- **THEN** they are pre-generated in agents-common and committed to `distribution/`
- **AND** downstream `agentsmgr populate` copies from `distribution/` without generation
- **AND** staleness is detected via `agentsmgr generate --check`

#### Scenario: Dynamic content generation
- **WHEN** tool-specific content is needed
- **THEN** agentsmgr generate produces distribution artifacts from components/
- **AND** agentsmgr populate copies distribution artifacts to downstream targets
- **AND** supports detect, generate, and populate commands

#### Scenario: Synced instructions
- **WHEN** external instruction content is needed
- **THEN** it is synced into agents-common and distributed from `distribution/`
- **AND** no network fetch occurs during downstream populate

#### Scenario: Configuration detection
- **WHEN** agentsmgr CLI runs
- **THEN** detects configuration from Copier answers files
- **AND** falls back to defaults when answers not available

#### Scenario: Plugin-based source handlers
- **WHEN** content sources are accessed
- **THEN** supports plugin-based source handlers
- **AND** includes git and local filesystem handlers
- **AND** provides extensible architecture for new handlers
