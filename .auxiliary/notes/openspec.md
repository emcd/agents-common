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
│   └── resources/
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

### Phase 1: Extend Population Logic

#### 1.1 Extend `sources/agentsmgr/population.py`

**New Function**: `_copy_coder_resources()`
- Copy from `defaults/per-project/resources/<coder>/`
  to `.auxiliary/configuration/coders/<coder>/` for all coders
- Handle missing directories gracefully
- Integrate with existing simulation mode
- Support both file and directory copying with recursive preservation

**Modify**: existing population workflow
- Add call to `_copy_coder_resources()` after directory structure creation
- Ensure happens before symlink creation to avoid copying broken links

#### 1.2 Extend `sources/agentsmgr/operations.py`

**Extend existing**: `operations.py` with generic file operation functions

**New Functions**:
- `copy_coder_resources(source, target, coder, simulate=False)`
- `ensure_coder_directories(target, coder, simulate=False)`
- `copy_resource_content(source_dir, target_dir, simulate=False)`
- `find_available_coders(source_path)` - discover available coders in defaults

### Phase 2: CLI Integration

#### 2.1 Update Help Text

**Update `populate` subcommand help** to mention population of coder commands from defaults

### Phase 3: Error Handling and Validation

#### 3.1 New Exceptions in `sources/agentsmgr/exceptions.py`

**New Exception Classes**:
- `CoderResourceAbsence` - when coder resources not found in defaults
- `CoderResourceCopyFailure` - when copying coder resources fails

#### 3.2 Validation Logic

**Pre-copying checks**:
- Verify source directories exist in defaults for each coder
- Validate target directories are writable
- Check for conflicts with existing resources

**Post-copying validation**:
- Verify resources were copied successfully
- Validate resource file formats
- Ensure proper permissions

### Phase 4: Testing

#### 4.1 Unit Tests

**New test module**: `tests/test_coder_resource_copying.py`

**Test cases**:
- Successful copying of coder resources for multiple coders
- Missing source directories handling
- File permission issues
- Simulation mode behavior
- Integration with existing symlink creation

#### 4.2 Integration Tests

**Extend existing tests**:
- `test_populate_project.py` - add coder resource copying verification
- End-to-end workflow testing

### Phase 5: Documentation

#### 5.1 Update Documentation

**README updates**:
- Document coder resource integration
- Examples of using coder resources from defaults
- Troubleshooting guide

**AGENTS.md enhancements**:
- Update instructions to reference copied coder resources
- Add workflow examples

#### 6.2 Code Documentation

**Docstrings and comments**:
- Comprehensive documentation for new resource copying functions
- Integration points with existing code
- Error condition documentation

## Implementation Sequence

1. **Extend population logic** in `populations.py`
2. **Add error handling** with new exception classes
3. **Update CLI help text**
4. **Add comprehensive tests**
5. **Update documentation**
6. **Integration testing**

## Backward Compatibility

- Existing `agentsmgr populate project` behavior unchanged
- Coder resource copying is additive, doesn't replace existing functionality
- Default to copying all available resources from defaults
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
- Graceful degradation when coder resources are missing
- Clear error messages and recovery instructions

## Success Criteria

1. ✅ Coder resources are copied during `agentsmgr populate project`
2. ✅ Resources are available in expected locations (`.auxiliary/configuration/coders/<coder>/`)
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