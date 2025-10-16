# TODO

## Code Quality

## Features

- [ ] **Separate maintainer CLI entrypoint**: Create `agentsmgr-maintainer` entrypoint in `pyproject.toml` for maintainer-facing commands. Move `validate` command from user-facing `agentsmgr` CLI to this new maintainer CLI. This separates template development/testing tools from production user commands. Maintainer CLI should include commands like `validate` and any future development/testing utilities.

- [ ] **Implement source precedence hierarchy**: Extend source resolution to follow CLI → environment → configuration precedence. Currently CLI only supports explicit `--source` parameter. Add environment variable support (e.g., `AGENTSMGR_SOURCE`) and configuration file fallback using `sources.default` from `data/configuration/general.toml`. Update `retrieve_data_location()` in `sources/agentsmgr/commands/base.py` to implement this precedence chain.

- [ ] Tag prefix support.

- [ ] **Tool groups for common combinations**: Define standard tool groups in configuration (e.g., "file_operations", "shell_access"). Create template helpers for common tool sets. Validate tool names against known Qwen tools. (Related to Phase 2 enhancement features but deferred as not core to Qwen support.)

- [ ] Review common templating for Gemini/Qwen3.

- [ ] **GIT_DIR and worktree support**: Update git-related functionality to respect `GIT_DIR` environment variable and handle git worktrees (where `.git` is a file pointing to the actual git directory). This affects:
  - `update_git_exclude()` in `sources/agentsmgr/commands/operations.py` (currently assumes `.git/info/exclude` path)
  - `_detect_git_branch()` in `defaults/globals/claude/statusline.py` (currently assumes `.git/HEAD` path)
  - Implementation should check `GIT_DIR` env var, parse `.git` file if it exists (worktree case), and gracefully handle edge cases

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
