# Directory Organization

## Architecture Decision: Separation of User Defaults and Package Data

### Structure

```
defaults/                      # NOT published - user's personal agent configs
├── configurations/            # TOML metadata for commands/agents
├── contents/                  # Markdown/TOML content bodies
└── templates/                 # Jinja2 templates for rendering

data/agentsmgr/                # Published as package data
└── profiles/                  # Test profiles for validation command
    ├── answers-default.yaml
    └── answers-maximum.yaml
```

### Rationale

**`defaults/` Directory (Not Published):**
- Contains evolving user content (commands, agents, templates)
- Designed to be independently versioned and updated
- Users pull via `agentsmgr populate --source=agents-common@agents-N`
- Can be ignored in favor of alternative repositories
- Should NOT be published as package data

**`data/agentsmgr/` Directory (Published):**
- Contains testing infrastructure for the agentsmgr tool itself
- Validation profiles support `agentsmgr validate` and `agentsmgr survey` commands
- Follows Python packaging conventions for distributable resources
- Should be published with the package distribution

### Key Principle

The distinction is between:
1. **User content** (defaults/) - Personal, evolving, git-versioned agent configurations
2. **Tool infrastructure** (data/) - Immutable testing resources distributed with the package

This separation prevents accidental publishing of user defaults while ensuring validation infrastructure is available to all package users.

## Current State (Pre-Refactoring)

Currently (as of Phase 3.5 implementation):
- Agent configs are in `data/{configurations,contents,templates}` (WRONG - should be `defaults/`)
- Validation profiles are in `data/configurations/answers-*.yaml` (WRONG - should be `data/agentsmgr/profiles/`)
- Code references need updating in `commands.py` for profile discovery

## TODO

- [ ] Move `data/{configurations,contents,templates}` → `defaults/{configurations,contents,templates}`
- [ ] Move `data/configurations/answers-*.yaml` → `data/agentsmgr/profiles/answers-*.yaml`
- [ ] Update `survey_variants()` to look in `data/agentsmgr/profiles/`
- [ ] Update `_retrieve_variant_answers_file()` to use new path
- [ ] Update any other code references to data paths
