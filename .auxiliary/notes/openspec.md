# OpenSpec Integration Plan for agentsmgr

## Overview

This plan outlines modifications to `agentsmgr` to support population of statically-generated OpenSpec commands from `defaults/` directories, enabling template-based projects to include OpenSpec tooling without committing generated commands to git.

## Current State Analysis

- OpenSpec skeleton has been added to `template/.auxiliary/configuration/openspec/`
- AGENTS.md has been updated to include OpenSpec instructions
- OpenSpec commands currently in `.claude/commands/openspec/` and `.opencode/command/openspec-*.md`
- Template `.gitignore` prevents committing commands in `.auxiliary/configuration/coders/claude/commands/`
- Need mechanism to populate OpenSpec commands during `agentsmgr populate project`

## Proposed Directory Structure

### New Defaults Directories
```
defaults/
├── per-project/
│   └── configurations/
│       ├── claude/
│       │   └── commands/
│       │       └── openspec/
│       │           ├── apply.md
│       │           ├── archive.md
│       │           └── proposal.md
│       └── opencode/
│           └── command/
│               ├── openspec-apply.md
│               ├── openspec-archive.md
│               └── openspec-proposal.md
```

### Target Population Structure
```
.auxiliary/configuration/
├── coders/
│   ├── claude/
│   │   └── commands/
│   │       └── openspec/
│   │           ├── apply.md
│   │           ├── archive.md
│   │           └── proposal.md
│   └── opencode/
│       └── command/
│           ├── openspec-apply.md
│           ├── openspec-archive.md
│           └── openspec-proposal.md
```

## Implementation Plan

### Phase 1: Extend Directory Structure

1. **Create defaults directories**:
   - `defaults/per-project/configurations/claude/commands/openspec/`
   - `defaults/per-project/configurations/opencode/command/`

2. **Move existing OpenSpec commands**:
   - From `.claude/commands/openspec/` to `defaults/per-project/configurations/claude/commands/openspec/`
   - From `.opencode/command/openspec-*.md` to `defaults/per-project/configurations/opencode/command/`

### Phase 2: Extend Population Logic

#### 2.1 Extend `sources/agentsmgr/population.py`

**New Function**: `_populate_coder_commands()`
- Copy from `defaults/per-project/configurations/<coder>/`
  to `.auxiliary/configuration/coders/<coder>/` for all coders
- Handle missing directories gracefully
- Integrate with existing simulation mode
- Support both file and directory copying with recursive preservation

**Modify**: existing population workflow
- Add call to `_populate_coder_commands()` after directory structure creation
- Ensure happens before symlink creation to avoid copying broken links

#### 2.2 Extend `sources/agentsmgr/operations.py`

**Extend existing**: `operations.py` with generic file operation functions

**New Functions**:
- `populate_coder_commands(source, target, coder, simulate=False)`
- `ensure_coder_directories(target, coder, simulate=False)`
- `copy_coder_content(source_dir, target_dir, simulate=False)`
- `find_available_coders(source_path)` - discover available coders in defaults

### Phase 3: CLI Integration

#### 3.1 Update Help Text

**Update `populate` subcommand help** to mention population of coder commands from defaults

### Phase 4: Error Handling and Validation

#### 4.1 New Exceptions in `sources/agentsmgr/exceptions.py`

**New Exception Classes**:
- `CoderCommandAbsence` - when coder commands not found in defaults
- `CoderCommandPopulationFailure` - when copying coder commands fails

#### 4.2 Validation Logic

**Pre-population checks**:
- Verify source directories exist in defaults for each coder
- Validate target directories are writable
- Check for conflicts with existing commands

**Post-population validation**:
- Verify commands were copied successfully
- Validate command file formats
- Ensure proper permissions

### Phase 5: Testing

#### 5.1 Unit Tests

**New test module**: `tests/test_coder_command_population.py`

**Test cases**:
- Successful population of coder commands for multiple coders
- Missing source directories handling
- File permission issues
- Simulation mode behavior
- Integration with existing symlink creation

#### 5.2 Integration Tests

**Extend existing tests**:
- `test_populate_project.py` - add coder command population verification
- End-to-end workflow testing

### Phase 6: Documentation

#### 6.1 Update Documentation

**README updates**:
- Document coder command integration
- Examples of using coder commands from defaults
- Troubleshooting guide

**AGENTS.md enhancements**:
- Update instructions to reference populated coder commands
- Add workflow examples

#### 6.2 Code Documentation

**Docstrings and comments**:
- Comprehensive documentation for new generic functions
- Integration points with existing code
- Error condition documentation

## Implementation Sequence

1. **Create defaults directory structure**
2. **Move existing openspec commands** to defaults
3. **Extend population logic** in `populations.py`
4. **Add error handling** with new exception classes
5. **Update CLI help text**
6. **Add comprehensive tests**
7. **Update documentation**
8. **Integration testing**

## Backward Compatibility

- Existing `agentsmgr populate project` behavior unchanged
- OpenSpec population is additive, doesn't replace existing functionality
- Default to including openspec commands, provide option to disable if needed
- Maintain existing simulation mode support

## Risk Mitigation

**Low Risk**:
- Directory creation and file copying operations are well-understood
- Existing population patterns can be reused
- Simulation mode provides safe testing

**Medium Risk**:
- Integration with existing population workflow needs careful sequencing
- Error handling for file permission issues
- Path resolution across different operating systems

**Mitigation**:
- Extensive testing with simulation mode first
- Graceful degradation when openspec commands are missing
- Clear error messages and recovery instructions

## Success Criteria

1. ✅ Coder commands are populated during `agentsmgr populate project`
2. ✅ Commands are available in expected locations (`.auxiliary/configuration/coders/<coder>/`)
3. ✅ Existing functionality remains unchanged
4. ✅ Simulation mode works correctly
5. ✅ Appropriate error handling for edge cases
6. ✅ Comprehensive test coverage
7. ✅ Clear documentation for users

## Next Steps

1. Review and approve this plan
2. Begin Phase 1 implementation (directory structure and command migration)
3. Proceed through phases sequentially
4. Test at each phase before proceeding
5. Final integration testing and documentation