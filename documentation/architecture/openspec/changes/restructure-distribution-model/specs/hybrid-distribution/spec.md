## MODIFIED Requirements

### Requirement: Hybrid Distribution Architecture

The system SHALL combine Copier template distribution for base configuration
with agentsmgr CLI distribution for managed artifacts, maintaining a clear
separation between tracked and managed content.

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

#### Scenario: Synced instructions
- **WHEN** external instruction content is needed
- **THEN** it is synced into agents-common and distributed from `distribution/`
- **AND** no network fetch occurs during downstream populate
