# Known Issues

## Populate Command: Coder Directory Symlinks Not Created in Default Mode

**Date**: 2025-10-22
**Status**: Partially Fixed - Needs Further Investigation

### Problem
When running `agentsmgr populate` with `--mode default` (or no mode specified), coder directory symlinks (`.claude`, `.opencode`, `.qwen`) are not being created even though all three coders have `mode_default = 'per-project'`.

### Expected Behavior
When `mode='default'`, the populate command should:
1. Check each coder's `mode_default` attribute
2. Create coder directory symlinks for coders with `mode_default='per-project'`
3. Add those symlink names to `.git/info/exclude`

### Current Behavior
- Command completes with minimal output
- No change to `.git/info/exclude`
- Coder directory symlinks are not created

### Fix Applied
Modified `sources/agentsmgr/population.py:74-78` to check if any coder has `mode_default='per-project'` when `mode='default'`:

```python
needs_coder_symlinks = (
    mode == 'per-project'
    or ( mode == 'default' and any(
        _renderers.RENDERERS[ coder ].mode_default == 'per-project'
        for coder in configuration[ 'coders' ] ) ) )
```

### Status
- Logic fix applied and passes linters/tests
- Command runs but produces minimal output
- Needs investigation to determine why symlinks aren't being created
- Possibly the symlinks already exist and the logic correctly skips them
- Need to verify actual behavior and expected output

### Related Files
- `sources/agentsmgr/population.py` - Symlink creation logic
- `sources/agentsmgr/renderers/claude.py` - `mode_default = 'per-project'`
- `sources/agentsmgr/renderers/opencode.py` - `mode_default = 'per-project'`
- `sources/agentsmgr/renderers/qwen.py` - `mode_default = 'per-project'`
- `sources/agentsmgr/generator.py:98-99` - Existing mode resolution pattern

### Next Steps
1. Add debug logging to symlink creation to understand flow
2. Verify if symlinks already exist and are being correctly skipped
3. Test with fresh target directory to see full creation flow
4. Consider if additional logic changes needed beyond the fix applied
