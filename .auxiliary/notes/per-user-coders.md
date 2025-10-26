# Per-User Coder Population Analysis

## Problem Statement

Currently, `populate project` attempts to handle all coders in the configuration, regardless of their supported targeting modes. This creates issues when coders like Codex only support per-user mode but are included in per-project population runs.

## Current Behavior

### `populate project` Command
- Runs in `mode = 'per-project'` (population.py:229)
- Attempts to populate content for all coders in configuration
- Creates per-project directory symlinks for all coders
- Fails to respect renderer mode capabilities

### `populate user` Command
- Runs `populate_globals()` which handles per-user configuration
- Only processes global configuration files
- Does NOT generate agent commands/agents content for per-user coders

## Design Intent

Based on renderer architecture, coders fall into categories:

### Per-User Only Coders
- **Codex**: Only supports `~/.codex` or `$CODEX_HOME`
- `modes_available = frozenset( ( 'per-user', ) )`
- Should have custom slash commands/agents populated to user directory

### Per-Project Capable Coders
- **Claude**: Supports both modes, defaults to per-project
- **OpenCode**: Supports both modes
- **Gemini**: Mode capabilities TBD
- **Qwen**: Mode capabilities TBD

## Desired Behavior

### `populate project` Command
Should populate **only** coders whose default mode is per-project:
1. Filter coders by checking `renderer.mode_default == 'per-project'`
2. Generate content for filtered coders to `.auxiliary/configuration/coders/{coder}/`
3. Create symlinks only for filtered coders
4. Skip per-user-default coders with informational logging

### `populate user` Command
Should populate **only** coders whose default mode is per-user:
1. Filter coders by checking `renderer.mode_default == 'per-user'`
2. Generate content for filtered coders to `~/.{coder}/` or equivalent
3. Use renderer's `resolve_base_directory()` with `mode='per-user'`
4. Handle commands, agents, and other item types

## Implementation Requirements

### 1. Renderer Mode Filtering

Create utility function in appropriate module (likely `renderers/__init__.py` or `operations.py`).

**Note to implementer:** The example code below shows the logical approach but does not follow all project coding conventions (e.g., space padding inside delimiters). Please follow established project conventions when implementing.

**Filtering Logic:** Filter coders by their **default mode** (`renderer.mode_default`), not just by whether a mode is available in `modes_available`. The default mode represents the intended usage pattern for each coder.

Example approach:
- Filter function that checks `renderer.mode_default == target_mode`
- Log debug messages for skipped coders
- Return tuple of coder names matching the target mode

### 2. Update `populate project` Command

Modify `PopulateProjectCommand.execute()` (population.py:212-257).

**Key changes:**
- Filter coders to include only those with `mode_default == 'per-project'`
- Create filtered configuration for content generator
- Pass filtered configuration to `_create_all_symlinks()`
- Warn if no per-project default coders found

**Note:** Look for opportunities to factor common code between `populate project` and `populate user` into shared utility functions.

### 3. Update `populate user` Command

Modify `PopulateUserCommand.execute()` (population.py:289-323) to include content generation.

**Key changes:**
- Filter coders to include only those with `mode_default == 'per-user'`
- **NEW:** Generate commands/agents content for per-user coders (not just globals/wrappers)
- For each per-user coder, resolve target directory via `renderer.resolve_base_directory(mode='per-user', ...)`
- Generate content to resolved target directories (e.g., `~/.codex/`)
- Continue with existing globals and wrappers logic
- Update result to include per-user content generation counts

**Note:** Look for opportunities to factor common code between `populate project` and `populate user` into shared utility functions. The content generation loop is likely duplicated.

### 4. Update Symlink Creation

Already covered in symlink-targets.md. Key points:

- **Memory symlinks:** Create for ALL coders (regardless of default mode) since all coders support per-project memory files
- **Directory symlinks:** Create only for coders with `mode_default == 'per-project'`
- Filtering logic implemented in `_create_coder_directory_symlinks()` (see symlink-targets.md)

## Testing Requirements

See `.auxiliary/notes/test-plans.md` for detailed test specifications.

## Documentation Updates

- Clarify in README.rst which command to use for which coders
- Add examples showing mixed coder configurations
- Document the per-user vs per-project distinction

## Design Clarifications

Based on feedback:

1. **`populate all` subcommand:** Not in scope. We just split the populate command into `project`/`user` subcommands. A future `populate all` could be considered later but would be scope creep now.

2. **Renderer default mode:** Renderers already declare `mode_default` as their preference. If this is not being honored, that's a bug that needs fixing.

3. **Coders supporting both modes:** We honor the renderer's `mode_default` preference. This is the correct behavior per spec.

4. **Memory symlinks:** Should be created for ALL configured coders, regardless of default mode. All coders support per-project memory files (like `AGENTS.md`), even if they don't support per-project configuration of themselves. This distinction is important.

## Related Files

- `sources/agentsmgr/population.py` - Main implementation file
- `sources/agentsmgr/renderers/codex.py` - Codex renderer
- `sources/agentsmgr/renderers/base.py` - Renderer base class
- `sources/agentsmgr/operations.py` - Content generation operations
- `sources/agentsmgr/memorylinks.py` - Symlink management
