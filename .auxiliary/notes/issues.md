# Known Issues

## populate project: No validation for project configuration presence

**Status**: Open
**Severity**: Medium
**Component**: `sources/agentsmgr/population.py:PopulateProjectCommand`

### Description

The `populate project` command will execute successfully even when run in a directory without project configuration (e.g., `.copier-answers.yml`). This allows the command to run in unexpected contexts and may lead to confusion.

### Example

```bash
# Running in project root without explicit source
hatch run agentsmgr populate project .
```

When no configuration is found at the target location, the command still:
- Attempts to retrieve configuration (using defaults or auto-detection)
- Generates content (0 items if no data source content exists)
- Updates instructions
- Manages git exclude entries

### Expected Behavior

The command should either:
1. Validate that target directory contains project configuration and fail gracefully if missing
2. Emit a clear warning when running without detected project configuration
3. Require explicit confirmation when no configuration is found

### Impact

- Users may accidentally run `populate project` in wrong directory
- Silent failures when configuration is missing
- Potential confusion about where content should be generated

### Related

- `populate user` doesn't have this issue since it operates on user-global scope
- Both commands currently auto-detect configuration which may mask the problem
