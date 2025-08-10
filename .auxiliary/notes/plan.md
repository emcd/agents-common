# Repository Structure Plan and Implementation

## Context and Motivation

This repository was created to maintain separately versioned AI agent configurations and data, following the approach outlined in `@../python-project-common/.auxiliary/notes/separate-docs-llms.md`. The goal is to provide a centralized location for Claude Code custom slash commands, subagent definitions, and similar configurations for other AI tools (Gemini CLI, Opencode, etc.).

## Key Design Decisions

### Directory Naming
- **Top-level organization**: `products/` rather than `vendors/`, `agents/`, or `tools/`
  - Rationale: Claude Code and Gemini CLI are products, making this terminology more precise
  - Avoids confusion like `agents/claude/agents`
  - Keeps top-level directory structure clean

### Subdirectory Naming
- **`configuration/` instead of `settings/`**: Maintains consistent Latin-derived terminology across all directory names
  - Other directories: `agents`, `commands`, `miscellany`, `scripts` (all Latin-derived)
  - Avoids mixing Germanic (`settings`) with Latin-derived names

### Settings Distribution Strategy
- **Template-based approach**: Use `settings.json.jinja` files with local overrides
  - Base templates handle hook configurations that reference distributed scripts
  - Projects can provide `local.toml` for additional customization
  - Avoids duplicating Copier's templating functionality
  - Solves coordination problem between hook paths and script distribution

## Implemented Structure

```
products/
├── claude/
│   ├── agents/          # Subagent definitions
│   ├── commands/        # Slash commands
│   ├── miscellany/      # Templates, snippets
│   ├── scripts/         # Hook executables (consolidated from python-project-common)
│   └── configuration/   # Base settings templates
└── gemini/
    ├── commands/        # Gemini commands
    └── configuration/   # Gemini settings templates
```

## Distribution Model

- **Tag-based releases**: `agents-1`, `agents-2`, etc.
- **Downstream deployment**: Content distributed to `.auxiliary/configuration/` in target repositories
- **Reference paths**: Commands maintain existing `.auxiliary/configuration/` references for downstream compatibility
- **CLI integration**: `agentsmgr prepare-llm-agents` command for environment setup

## Key Benefits

1. **Clean Organization**: Product-focused structure with clear separation
2. **Consolidation**: All Claude tooling (commands, agents, scripts) in one location
3. **Reusability**: Multiple project templates can reference same configurations
4. **Extensibility**: Easy to add new AI tools without restructuring
5. **Maintenance**: Single source of truth for all AI agent configurations
6. **Settings Coordination**: Template-based approach solves hook path coordination

## Implementation Completed

1. ✅ Created `products/` directory structure with `claude/` and `gemini/` subdirectories
2. ✅ Moved existing content from `.auxiliary/configuration/` to new structure
3. ✅ Consolidated Claude hook scripts from python-project-common template
4. ✅ Created template-based settings with `settings.json.jinja` files
5. ✅ Preserved existing reference paths in commands for downstream compatibility

## Next Steps (Not Implemented)

- Update CLI tooling to reference new `products/` structure
- Establish tag-based publishing workflow
- Update python-project-common templates to pull from this repository
- Create proper PRD and architecture documentation
- Update README with new repository purpose and structure