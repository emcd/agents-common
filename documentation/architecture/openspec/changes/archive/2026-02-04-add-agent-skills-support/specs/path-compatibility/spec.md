# path-compatibility (delta)

## MODIFIED Requirements

### Requirement: Generated Content Path Compatibility

The system SHALL ensure generated content references correct paths for
compatibility with downstream project deployment patterns.

#### Scenario: Stable skill discovery path
- **WHEN** skills are generated for a project
- **THEN** they are discoverable via the tool’s expected project root path
  (e.g. `.claude/skills/`, `.codex/skills/`, `.gemini/skills/`, `.opencode/skills/`)
- **AND** the underlying source of truth remains under
  `.auxiliary/configuration/coders/<coder>/skills/`
