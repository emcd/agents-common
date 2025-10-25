# Subcommand Split Analysis: `populate project` and `populate user`

## Current State Assessment

The existing `populate` command (`sources/agentsmgr/population.py:182-285`) handles multiple concerns:

### Project-scoped operations
- Generating agent/command content to `.auxiliary/configuration/coders/`
- Creating symlinks (`.claude` → `.auxiliary/configuration/coders/claude`, etc.)
- Populating instructions to `.auxiliary/instructions`
- Managing `.git/info/exclude` entries

### User-scoped operations (via `--update-globals` flag)
- Copying/merging global settings to per-user directories
- Handled by `userdata.populate_globals()` (`sources/agentsmgr/userdata.py:43-89`)

### Mode-specific behavior
- `--mode` parameter controls targeting (`default`, `per-user`, `per-project`, `nowhere`)
- `--update-globals` is orthogonal to mode (line 209-214 in `population.py`)

---

## Proposed Split: Design Analysis

### Strengths of the Split

1. **Clearer Mental Model**: The current design conflates two distinct concerns—populating a *project* vs. populating *user configuration*. Splitting makes each subcommand's purpose explicit.

2. **Better Flag Semantics**: Removing `--update-globals` makes sense because:
   - `populate project` would *never* touch user files
   - `populate user` would *only* touch user files
   - No ambiguity about what gets updated

3. **Improved Safety**: Reduces accidental user config overwrites—users must explicitly run `populate user` to affect their global settings.

4. **Future Extensibility**: Creates a clear namespace for project-specific vs. user-specific flags without conflicts.

### Potential Challenges

#### 1. Workflow Impact
Users currently running `agentsmgr populate --update-globals` would need to:
```bash
agentsmgr populate project  # Update project files
agentsmgr populate user     # Update user globals
```

This is *more explicit* but requires two commands. Consider whether this is acceptable for your workflow.

#### 2. Shared Parameters
Both subcommands would need:
- `source`: Data source location
- `profile`: Alternative Copier answers file
- `simulate`: Dry-run mode
- `tag_prefix`: Version tag filtering

**Decision**: `populate user` does NOT accept a `target` parameter. User globals are resolved from renderer configuration (`userdata.py:70-75`), not a target directory.

#### 3. Mode Parameter
**Decision**: Drop the `--mode` flag entirely as part of the split. With distinct subcommands:
- `populate project` always targets the project
- `populate user` always targets user directories
The mode concept becomes unnecessary.

#### 4. Git Exclude Management
**Decision**: `populate project` is responsible for maintaining `.git/info/exclude`. This makes sense as it's managing project-local symlinks and configuration.

---

## Wrapper Scripts Integration

The wrapper scripts (`miscellany/claude-xai`, `miscellany/claude-ds`) are bash scripts that:
- Source environment variables from `.auxiliary/secrets/*.env`
- Override `ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN`, etc.
- Execute the `claude` CLI with modified environment

### Approach: Install During `populate user`

**Decision**: Integrate wrapper installation into `populate user` command.

**Rationale**:
- Centralized management—`populate user` handles *all* user-scope installation
- Scripts available in PATH without manual intervention
- Natural fit for "configure my user environment" semantics

**Implementation**:
```python
# In userdata.py, extend populate_globals()
def populate_user_wrappers(
    data_location: Path,
    simulate: bool = False,
) -> tuple[int, int]:
    '''Installs wrapper scripts to user bin directory.

    Uses ~/.local/bin as the standard user executables location.
    '''
    wrappers_dir = data_location / 'user' / 'executables'
    user_bin = Path.home() / '.local' / 'bin'

    if not wrappers_dir.exists():
        return (0, 0)

    attempted = 0
    installed = 0
    for script in wrappers_dir.glob('*'):
        if not script.is_file():
            continue
        attempted += 1
        target = user_bin / script.name
        if not simulate:
            user_bin.mkdir(parents=True, exist_ok=True)
            shutil.copy2(script, target)
            target.chmod(target.stat().st_mode | 0o111)  # Make executable
        installed += 1

    return (attempted, installed)
```

**Key Decisions**:
- Move wrappers from `miscellany/` to `user/executables/` in data source
- Use `~/.local/bin` as standard user executables location (XDG doesn't specify an env var for this)
- Wrappers are **copied** (not symlinked) since source can be remote
- **Overwrite** existing wrappers—users want latest versions
- Wrapper names remain as-is (e.g., `claude-xai`, `claude-ds`)—they wrap the `claude` command
- Flat directory structure (`user/executables/`) for simplicity

---

## Recommendations

### 1. Subcommand Split

```bash
agentsmgr populate project [--source SOURCE] [--target TARGET] [--profile PROFILE] [--tag-prefix PREFIX] [--simulate]
agentsmgr populate user [--source SOURCE] [--profile PROFILE] [--tag-prefix PREFIX] [--simulate]
```

**Key Points**:
- Drop `--mode` flag entirely (no longer needed with distinct subcommands)
- `populate user` has NO `target` parameter (uses renderer-resolved paths)
- `populate project` manages `.git/info/exclude`
- Both share `--source`, `--profile`, `--simulate`, `--tag-prefix`

### 2. Wrapper Scripts Integration

- Integrate into `populate user` command
- Move wrappers from `miscellany/` to `user/executables/` in data source
- Install to `~/.local/bin` (standard location, XDG doesn't define an env var for user executables)
- Copy wrappers (not symlink) since source can be remote
- Overwrite existing wrappers to ensure latest versions
- Retain wrapper names (`claude-xai`, `claude-ds`) as they wrap the `claude` command
- Make scripts executable during copy

### 3. Data Source Reorganization

```
data-source/
├── user/
│   ├── executables/
│   │   ├── claude-xai            # Wrapper scripts
│   │   └── claude-ds
│   └── configurations/
│       ├── claude/
│       │   └── settings.json     # Per-user settings
│       └── opencode/
│           └── opencode.json
├── configurations/
│   ├── agents/
│   └── commands/
└── contents/
```

### 4. Migration Path

**Not needed**: `agentsmgr` is still in alpha, so breaking changes are acceptable without deprecation periods.

---

## Resolved Questions

All design questions have been resolved:

1. **Wrapper Script Naming**: ✅ Retain current names (`claude-xai`, `claude-ds`) as they wrap the `claude` command
2. **Directory Structure**: ✅ Use flat directory (`globals/executables/`) for simplicity
3. **Overwrite Behavior**: ✅ Overwrite existing wrappers to ensure users get latest versions
4. **Per-Project Wrappers**: ✅ Not needed currently; can revisit if use case emerges
5. **Symlink vs. Copy**: ✅ Copy wrappers since data source can be remote (e.g., GitHub repo)
6. **Target Parameter**: ✅ `populate user` does NOT accept `target` (uses renderer-resolved paths)
7. **Mode Flag**: ✅ Drop `--mode` entirely; distinct subcommands make it unnecessary
8. **Git Exclude**: ✅ `populate project` maintains `.git/info/exclude`
9. **Migration**: ✅ No migration path needed (alpha stage allows breaking changes)

---

## Summary

This split creates a cleaner separation of concerns and sets up a natural home for user-scope tooling like wrapper scripts. The key is ensuring the data source structure supports both project and user artifacts cleanly.

The main tradeoffs:
- **Clarity vs. Convenience**: Two commands instead of one flag, but much clearer semantics
- **Structure vs. Flexibility**: Prescriptive data source layout vs. ad-hoc organization
- **Safety vs. Ease**: Explicit user action required for global changes vs. single command does everything
