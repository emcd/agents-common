# Symlink Target Validation Analysis

## Problem Statement

The codebase creates symlinks without validating that target directories exist, leading to dangling symlinks. Specifically, `.codex -> .auxiliary/configuration/coders/codex` is created even though the target directory is never populated because Codex doesn't support per-project mode.

## Current Behavior

### Symlink Types

The system creates two categories of symlinks:

#### 1. Memory File Symlinks (Always Created)
Located at project root, pointing to `conventions.md`:
- `AGENTS.md -> .auxiliary/configuration/conventions.md`
- `CLAUDE.md -> .auxiliary/configuration/conventions.md`
- `GEMINI.md -> .auxiliary/configuration/conventions.md`
- `QWEN.md -> .auxiliary/configuration/conventions.md`

These are **per-coder memory files** that coders expect at project root.

Created by: `create_memory_symlinks_for_coders()` in memorylinks.py:89-121

#### 2. Coder Directory Symlinks (Per-Project Mode Only)
Located at project root, pointing to coder-specific directories:
- `.claude -> .auxiliary/configuration/coders/claude`
- `.gemini -> .auxiliary/configuration/coders/gemini`
- `.opencode -> .auxiliary/configuration/coders/opencode`
- `.qwen -> .auxiliary/configuration/coders/qwen`
- `.codex -> .auxiliary/configuration/coders/codex` ⚠️ **DANGLING**

These provide convenient access to coder configurations stored under `.auxiliary/`.

Created by: `_create_coder_directory_symlinks()` in population.py:131-179

### Problem Code

In `_create_coder_directory_symlinks()` (population.py:131-179):

```python
for coder_name in coders:
    try: renderers[ coder_name ]
    except KeyError as exception:
        raise _exceptions.CoderAbsence( coder_name ) from exception

    # Source: actual location under .auxiliary/configuration/coders/
    source = (
        target / '.auxiliary' / 'configuration' / 'coders' / coder_name )
    # Link: expected location for coder (.claude, .opencode, etc.)
    link_path = target / f'.{coder_name}'

    attempted += 1
    was_created, symlink_name = _memorylinks.create_memory_symlink(
        source, link_path, simulate )
    if was_created: created += 1
    symlink_names.append( symlink_name )
```

**Issues:**
1. No validation that `source` directory exists
2. No check if coder supports per-project mode
3. Creates symlinks blindly for all configured coders

## Root Cause

The architectural mismatch:

1. **Codex renderer** only supports `per-user` mode (codex.py:42)
2. **`populate project` command** runs in `per-project` mode (population.py:229)
3. Content is never generated to `.auxiliary/configuration/coders/codex/`
4. Symlink is created anyway, pointing to non-existent directory

## Proposed Solution

### Design Principle

**Coder directory symlinks should only be created for coders whose default mode is per-project.**

Rationale:
- Per-project coder directories only exist when coder's default mode is per-project
- Symlinks are a convenience feature for per-project workflows
- Per-user default coders access their config from `~/` paths, not project directories
- We honor renderer `mode_default`, not just `modes_available`

### Implementation

#### Option 1: Default Mode Filtering (Recommended)

Modify `_create_coder_directory_symlinks()` to filter by renderer default mode.

**Note to implementer:** The example code below shows the logical approach but does not follow all project coding conventions. Please follow established project conventions when implementing.

**Filtering Logic:** Check `renderer.mode_default == 'per-project'`, not just whether per-project is in `modes_available`. This honors the renderer's preferred usage pattern.

Key changes:
- Skip coders whose `mode_default` is not `'per-project'`
- Log debug message for skipped coders
- Continue with existing symlink creation for qualifying coders

**Advantages:**
- Respects renderer design and default mode preference
- No dangling symlinks
- Clear semantics: per-project symlinks for per-project default coders
- Minimal code changes

**Disadvantages:**
- None identified

#### Option 2: Source Existence Validation

Add validation in `create_memory_symlink()`:

```python
def create_memory_symlink(
    source: __.Path,
    link_path: __.Path,
    simulate: bool = False,
) -> tuple[ bool, str ]:
    ''' Creates symlink from coder memory file to project conventions.

        ... existing docstring ...
    '''
    symlink_name = link_path.name

    # NEW: Validate source exists
    if not source.exists():
        _scribe.warning(
            f"Skipping symlink {symlink_name}: "
            f"source {source} does not exist" )
        return ( False, symlink_name )

    try:
        relative_source = __.os.path.relpath(
            source, start = link_path.parent )
    except ValueError:
        relative_source = str( source.resolve( ) )

    # ... rest of existing logic ...
```

**Advantages:**
- Defensive programming: catches any missing targets
- Could help with other edge cases

**Disadvantages:**
- Treats symptom rather than cause
- Symlinks might be desired even if target doesn't exist yet
- Less clear about the actual requirement (mode compatibility)
- Could mask configuration errors

#### Option 3: Combined Approach

Use both mode-based filtering (Option 1) and source validation (Option 2):
- Mode filtering in `_create_coder_directory_symlinks()` for coder directories
- Source validation in `create_memory_symlink()` as safety net

**Advantages:**
- Defense in depth
- Clear intent at call site, safety net in utility function

**Disadvantages:**
- More complex
- Possibly redundant

### Recommended Approach

**Implement Option 1 (mode-based filtering) only.**

Reasoning:
1. Addresses root cause: per-project symlinks for per-project coders
2. Explicit and clear semantics
3. Source validation could be too defensive (prevents intentional future patterns)
4. Aligns with overall fix in per-user-coders.md

### Integration with Per-User Coder Fix

The symlink fix integrates naturally with per-user coder filtering:

In `_create_all_symlinks()` (population.py:50-96):

```python
def _create_all_symlinks(
    configuration: __.cabc.Mapping[ str, __.typx.Any ],
    target: __.Path,
    mode: str,
    simulate: bool,
) -> tuple[ str, ... ]:
    ''' Creates all symlinks and returns their names for git exclude.

        Creates memory symlinks for all coders and coder directory
        symlinks for per-project mode (filtered by coder capabilities).
        Returns tuple of all symlink names for git exclude update.
    '''
    all_symlink_names: list[ str ] = [ ]
    if mode == 'nowhere': return tuple( all_symlink_names )

    # Memory symlinks: created for ALL coders
    # (They point to conventions.md which exists for all coders)
    links_attempted, links_created, symlink_names = (
        _memorylinks.create_memory_symlinks_for_coders(
            coders = configuration[ 'coders' ],
            target = target,
            renderers = _renderers.RENDERERS,
            simulate = simulate,
        ) )
    all_symlink_names.extend( symlink_names )
    if links_created > 0:
        _scribe.info(
            f"Created {links_created}/{links_attempted} memory symlinks" )

    # Coder directory symlinks: only for per-project capable coders
    needs_coder_symlinks = (
        mode == 'per-project'
        or ( mode == 'default' and any(
            _renderers.RENDERERS[ coder ].mode_default == 'per-project'
            for coder in configuration[ 'coders' ] ) ) )
    if needs_coder_symlinks:
        # Directory symlinks will internally filter by mode support
        (   coder_symlinks_attempted,
            coder_symlinks_created,
            coder_symlink_names ) = (
            _create_coder_directory_symlinks(
                coders = configuration[ 'coders' ],  # Pass all coders
                target = target,
                renderers = _renderers.RENDERERS,
                simulate = simulate,
            ) )
        all_symlink_names.extend( coder_symlink_names )
        if coder_symlinks_created > 0:
            _scribe.info(
                f"Created {coder_symlinks_created}/"
                f"{coder_symlinks_attempted} coder directory symlinks" )

    return tuple( all_symlink_names )
```

**Key Points:**
1. Memory symlinks for ALL coders (they all share conventions.md)
2. Directory symlinks only for per-project capable coders
3. Filtering happens inside `_create_coder_directory_symlinks()`
4. Caller passes all coders, callee filters appropriately

## Testing Requirements

See `.auxiliary/notes/test-plans.md` for detailed test specifications.

## Cleanup of Existing Projects

For projects with existing `.codex` symlinks:

```bash
# Remove dangling .codex symlink
if [ -L .codex ] && [ ! -e .codex ]; then
    rm .codex
    echo "Removed dangling .codex symlink"
fi
```

Could be added as:
1. Manual step in migration guide
2. Automatic cleanup in `populate project` command
3. Utility command: `agentsmgr maintenance clean-symlinks`

## Memory Symlink Considerations

### Current Behavior

Memory symlinks (AGENTS.md, CLAUDE.md, etc.) are created for ALL coders, pointing to shared `conventions.md`:

```python
def create_memory_symlinks_for_coders(
    coders: __.cabc.Sequence[ str ],
    target: __.Path,
    renderers: __.cabc.Mapping[ str, __.typx.Any ],
    simulate: bool = False,
) -> tuple[ int, int, tuple[ str, ... ] ]:
    source = target / '.auxiliary' / 'configuration' / 'conventions.md'
    if not source.exists( ):
        raise _exceptions.MemoryFileAbsence( source )
    # ... creates {renderer.memory_filename} for each coder
```

### Question: Should Memory Symlinks Be Conditional?

**Arguments for filtering:**
- Consistency with directory symlink logic
- Per-user coders might not need/use project-level memory files

**Arguments against filtering (current behavior):**
- Memory files are project-level conventions useful to ALL coders
- Even per-user coders might be used in project context
- `conventions.md` exists regardless of coder mode
- No harm in extra symlinks pointing to valid shared file

**Recommendation:** Keep current behavior (create for all coders).

Rationale:
- Memory symlinks don't create dangling links (conventions.md always exists)
- Provides flexibility for mixed usage patterns
- Simpler mental model: "memory files for everyone, directories for per-project"

## Related Files

- `sources/agentsmgr/population.py` - Main symlink orchestration
- `sources/agentsmgr/memorylinks.py` - Symlink creation utilities
- `sources/agentsmgr/renderers/base.py` - Renderer mode declarations
- `.git/info/exclude` - Git exclude management for symlinks
