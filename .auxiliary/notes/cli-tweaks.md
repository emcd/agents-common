# CLI Improvements for Populate Command

## Overview

This document outlines planned improvements to the `agentsmgr populate` command interface to enhance usability and flexibility.

## Proposed Changes

### 1. Make `source` and `target` Arguments Positional

**Current Behavior:**
```bash
agentsmgr populate --source=github:foo/bar --target=/path/to/project
```

**Proposed Behavior:**
```bash
agentsmgr populate github:foo/bar /path/to/project
agentsmgr populate  # Uses defaults (current directory)
```

**Rationale:**
- Natural command-line interface pattern (similar to `cp source target`)
- Reduces verbosity for the most common arguments
- Both arguments have sensible defaults, so they remain optional

**Considerations:**
- Breaking change for existing scripts using `--source`/`--target` flags
- Acceptable given alpha version status (1.0a1)
- Documentation and README examples must be updated
- Positional argument order is significant: `source` must precede `target`

### 2. Add `profile` Argument for Alternative Configuration Files

**Purpose:**
Enable users to specify an alternative Copier answers file instead of always using the auto-detected `.auxiliary/configuration/copier-answers--agents.yaml`.

**Use Cases:**
- Testing with different configurations without modifying main answers file
- Supporting multiple configuration profiles per project
- Development and testing workflows

**Proposed Behavior:**
```bash
agentsmgr populate --profile=/path/to/alt-answers.yaml
agentsmgr populate --profile=../other-config.yaml --simulate
```

**Design Decisions:**
- Accept full file path for maximum flexibility
- Optional argument (defaults to auto-detected answers file)
- Path resolution: relative paths resolved from current working directory
- Independent from `target` argument (specifies *what* to generate, not *where*)

**Error Handling:**
- Non-existent profile file should raise appropriate configuration error
- Invalid YAML in profile file should raise configuration validation error

### 3. Maintainer Commands Separation

**Current State:**
The `validate` command is maintainer-facing (for template developers) but exists in the user-facing CLI alongside production commands like `populate`.

**Issue:**
Mixing maintainer-facing and user-facing commands in the same interface creates confusion and clutter for end users.

**Resolution:**
Move `validate` command to separate `agentsmgr-maintainer` CLI entrypoint. See TODO item below.

## Implementation Notes

**Reference Implementation:**
The `librovore` project provides a reference for implementing positional arguments using the tyro library pattern. See `sources/librovore/cli.py` lines 107-118.

**Breaking Changes:**
- Positional arguments change is a breaking change
- Should be acceptable given project is at version 1.0a1
- Release notes should clearly document the interface change

**Related Files:**
- `sources/agentsmgr/commands/population.py` - PopulateCommand class
- `sources/agentsmgr/commands/base.py` - retrieve_configuration() function
- `sources/agentsmgr/commands/validation.py` - ValidateCommand (to be moved)
- `sources/agentsmgr/cli.py` - CLI application structure
- `README.rst` - Usage examples to be updated
