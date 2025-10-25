# TODO

## Code Quality

## Features

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
