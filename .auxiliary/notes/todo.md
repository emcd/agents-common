# TODO

## Code Quality

## Features

- [ ] **Implement source precedence hierarchy**: Extend source resolution to follow CLI → environment → configuration precedence. Currently CLI only supports explicit `--source` parameter. Add environment variable support (e.g., `AGENTSMGR_SOURCE`) and configuration file fallback using `sources.default` from `data/configuration/general.toml`. Update `retrieve_data_location()` in `sources/agentsmgr/commands/base.py` to implement this precedence chain.

## Documentation

## Testing

### AgentsMgr Populate Command Safety Improvements

Based on analysis of the populate command architecture, the following improvements should be considered for production safety:

- [ ] **Enhanced Rollback Capability**: Add built-in restore command to CLI for undoing populate operations. Current backup mechanism creates `.json.backup` files but lacks easy restoration interface.

- [ ] **Atomic Settings Operations**: Implement atomic file operations for settings updates to prevent corruption if interrupted. Current implementation writes directly to target files without transaction safety.

- [ ] **Environment Variable Validation**: Add validation and explicit reporting of environment variable resolution (especially `CLAUDE_CONFIG_DIR`) in simulation mode to prevent unexpected directory targeting.

- [ ] **Pre-flight Validation**: Implement comprehensive pre-flight checks including:
  - Write permission validation for target directories
  - JSON syntax validation for existing settings files
  - Disk space availability checks
  - Configuration compatibility verification

- [ ] **Enhanced Backup Strategy**: Improve backup mechanism with:
  - Timestamped backup directories for full restoration
  - Compressed backup storage for space efficiency
  - Backup verification and integrity checks
