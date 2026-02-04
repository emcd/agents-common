# TODO

## Code Quality

## Features

- [ ] **Agent Skills support**: Add a first-class `skills` item type and
  generate Agent Skills–compatible directories under `.skills/` (symlink to
  `.auxiliary/configuration/skills`). Track via OpenSpec change
  `add-agent-skills-support`.

- [ ] **Configurable content absence behavior**: Consider making failure
  behavior configurable when coder content is missing during populate operations.
  Current implementation (as of 2025-10-23) warns and skips missing content,
  which works well for iterative development. However, CI/CD pipelines or
  production deployments might want strict validation. Potential approaches:
  - Add `--strict` flag to fail on missing content
  - Add `--lenient` flag (or make current behavior default with opt-in strictness)
  - Extend to configuration file option for project-wide defaults
  - Consider whether strictness should apply to templates, configurations, etc.
  - Decide on interaction with `--simulate` mode
  - Consider summarizing warnings at end vs. inline logging

- [ ] **Symlink Health Check Subcommand**: Add `agentsmgr maintenance check-symlinks`
  command to report dangling, broken, or unexpected symlinks. Should:
  - Identify all managed symlinks in project
  - Report status of each (valid, dangling, broken, unexpected)
  - Distinguish between expected symlinks (memory files, coder directories) and others
  - Provide actionable recommendations for issues found
  - Support `--json` output for automation

- [ ] **Symlink Cleanup Subcommand**: Add `agentsmgr maintenance clean-symlinks`
  command to remove dangling symlinks with confirmation. Should:
  - Detect all dangling symlinks in project root and `.auxiliary/`
  - Show preview of symlinks to be removed
  - Require confirmation unless `--force` flag provided
  - Support dry-run mode via `--simulate`
  - Log all cleanup actions
  - Optionally clean up backup files from previous symlink updates


## Documentation

## Testing

### AgentsMgr Populate Command Safety Improvements

Based on analysis of the populate command architecture, the following improvements should be considered for production safety:

- [ ] **Enhanced Rollback Capability**: Add built-in restore command to CLI for
  undoing populate operations. Current backup mechanism creates `.json.backup`
  files but lacks easy restoration interface.

- [ ] **Atomic Settings Operations**: Implement atomic file operations for
  settings updates to prevent corruption if interrupted. Current implementation
  writes directly to target files without transaction safety.

- [ ] **Environment Variable Validation**: Add validation and explicit
  reporting of environment variable resolution (especially `CLAUDE_CONFIG_DIR`)
  in simulation mode to prevent unexpected directory targeting.

- [ ] **Pre-flight Validation**: Implement comprehensive pre-flight checks
  including:
  - Write permission validation for target directories
  - JSON syntax validation for existing settings files
  - Disk space availability checks

- [ ] **Enhanced Backup Strategy**: Improve backup mechanism with:
  - Timestamped backup directories for full restoration
  - Compressed backup storage for space efficiency
  - Backup verification and integrity checks
