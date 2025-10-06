# Coder Renderers Architecture Implementation

## Context and References

- **Implementation Title**: Coder Renderer Architecture Phase 1
- **Start Date**: 2025-10-04
- **Reference Files**:
  - `.auxiliary/notes/renderers-cfg.md` - Design document for three-layer configuration model
  - `sources/agentsmgr/commands/generator.py` - Existing content generation logic
  - `sources/agentsmgr/exceptions.py` - Exception hierarchy patterns
  - `.auxiliary/instructions/practices-python.rst` - Python development guide
  - `.auxiliary/instructions/nomenclature.rst` - Naming conventions
- **Design Documents**: `.auxiliary/notes/renderers-cfg.md`
- **Session Notes**: TodoWrite tracking for current session tasks

## Design and Style Conformance Checklist

- [x] Module organization follows practices guidelines
- [x] Function signatures use wide parameter, narrow return patterns
- [x] Type annotations comprehensive with TypeAlias patterns
- [x] Exception handling follows Omniexception → Omnierror hierarchy
- [x] Naming follows nomenclature conventions
- [x] Immutability preferences applied (renderers are stateless singletons)
- [x] Code style follows formatting guidelines

## Practices Guide Knowledge Attestation

I have read the practices guides and understand the following principles:

1. **Comprehensive examples** demonstrate cohesive application of multiple patterns (DataProcessor example shows module organization, type annotations, immutability, narrow try blocks, and exception chaining working together).

2. **Import organization** follows centralized `__` subpackage pattern to avoid namespace pollution with external library imports consolidated and accessed via dot notation.

3. **Exception handling** requires narrow try blocks containing only statements that raise exceptions, with proper chaining using `from` clause to preserve debugging context.

## Implementation Progress Checklist

### Phase 1: Refactor without behavior change
- [x] Create `sources/agentsmgr/renderers/` directory structure
- [x] Implement `base.py` with `CoderRenderer` protocol and type aliases
- [x] Implement `__init__.py` with registry pattern
- [x] Implement `claude.py` renderer (per-project mode only for Phase 1)
- [x] Implement `opencode.py` renderer (per-project mode only)
- [x] Implement `codex.py` renderer (per-project mode only)
- [x] Add `UnsupportedTargetingModeError` exception
- [x] Update generator.py to use renderers for path resolution
- [x] All renderers default to existing per-project behavior

## Quality Gates Checklist

- [x] Linters pass (`hatch --env develop run linters`)
- [x] Type checker passes
- [x] Tests pass (`hatch --env develop run testers`) - All 8 tests passing
- [x] Code review ready

## Decision Log

- **2025-10-04** Phase 1 scope: Implement renderer architecture without changing behavior - All renderers support only per-project mode initially, maintaining backward compatibility while establishing foundation for future per-user mode support.

- **2025-10-04** Registry pattern: Use accretive.Dictionary per project standards - Renderers register themselves directly by assigning to RENDERERS dictionary in module body.

- **2025-10-04** Circular import resolution: Import renderer modules at bottom of __init__.py after function definitions. Required noqa: E402 suppression.

- **2025-10-04** Unused parameters: environment parameter in renderer methods intentionally unused in Phase 1 but required for Phase 2 implementation. Vulture warnings acceptable.

- **2025-10-04** Architecture revision based on feedback (round 1):
  - Changed from Protocol to base class (RendererBase inherits from immut.Object)
  - Renamed exception: UnsupportedTargetingModeError → TargetModeNoSupport
  - Simplified parameter names: coder_name → name, agentsmgr_config → configuration, etc.
  - Removed "Phase" mentions from docstrings and error messages
  - Added renderers/__ module for proper import structure
  - Updated commands/__ to wildcard import from renderers

- **2025-10-04** Architecture revision based on feedback (round 2):
  - Renamed exception: UnsupportedCoderError → CoderAbsence
  - Moved RENDERERS registry from __init__.py to base.py
  - Removed produce_renderer() function - use RENDERERS directly
  - Fixed out-of-place imports - removed noqa: E402 suppression
  - Simplified import structure in __init__.py

## Handoff Notes

### Current State
✅ Phase 1 COMPLETE - All implementation tasks finished and tests passing.

**Files Created:**
- `sources/agentsmgr/renderers/base.py` - CoderRenderer protocol and TargetingMode type
- `sources/agentsmgr/renderers/__init__.py` - Registry with self-registration pattern
- `sources/agentsmgr/renderers/claude.py` - Claude Code renderer
- `sources/agentsmgr/renderers/opencode.py` - OpenCode renderer
- `sources/agentsmgr/renderers/codex.py` - Codex CLI renderer

**Files Modified:**
- `sources/agentsmgr/exceptions.py` - Added UnsupportedTargetingModeError
- `sources/agentsmgr/commands/generator.py` - Updated render_single_item to use renderers

**Test Results:**
- All 8 tests passing
- Coverage: 75% for renderers/__init__.py, 48% for individual renderers
- Linters pass with acceptable vulture warnings for unused protocol parameters

### Phase 2 Implementation (Complete)
**Start Date**: 2025-10-05
**End Date**: 2025-10-05

**Scope**: Add configuration support and per-user mode targeting

**Tasks Completed**:
- [x] Update ClaudeRenderer with per-user mode support and env var resolution
- [x] Update OpenCodeRenderer with per-user mode support and env var resolution
- [x] Update CodexRenderer to support per-user mode (only mode it supports)
- [x] Add agentsmgr_configuration and target_mode parameters to ContentGenerator
- [x] Update PopulateCommand to accept --target-mode CLI flag
- [x] TargetModeNoSupport exception already has markdown rendering

**Environment Variable Precedence Implemented**:
1. CLAUDE_CONFIG_DIR, OPENCODE_CONFIG_DIR, CODEX_HOME (highest)
2. agentsmgr configuration file overrides (infrastructure ready, file loading deferred to Phase 3)
3. Coder-specific defaults (lowest)

**Files Modified in Phase 2**:
- `sources/agentsmgr/renderers/claude.py` - Added per-user mode with env var support, changed per-project to `.claude/`
- `sources/agentsmgr/renderers/opencode.py` - Added per-user mode with env var support, uses `.opencode/`
- `sources/agentsmgr/renderers/codex.py` - Changed to per-user only mode
- `sources/agentsmgr/commands/generator.py` - Added target_mode and application_configuration parameters
- `sources/agentsmgr/commands/population.py` - Added --target-mode CLI flag (will rename to --mode)
- `sources/agentsmgr/__/imports.py` - Added os to centralized imports
- `documentation/architecture/filesystem.rst` - Updated data/ → defaults/, added globals structure

**Test Results**:
- All 8 tests passing
- Linters: 0 errors, 0 warnings
- Coverage: 33% overall (renderers at 23-60% as implementation details expand)

**Decision Log - Phase 2**:
- **2025-10-05** Configuration file loading deferred to Phase 3: Phase 2 establishes infrastructure for application_configuration parameter, but actual file loading from ~/.config/emcd-agents/general.toml will be implemented in Phase 3.

- **2025-10-05** Codex renderer changed to per-user only: Removed per-project mode support since Codex CLI doesn't support it. Now raises TargetModeNoSupport with helpful error message.

- **2025-10-05** Environment variable precedence: Each renderer checks environment variables first (CLAUDE_CONFIG_DIR, OPENCODE_CONFIG_DIR, CODEX_HOME), then configuration file overrides, then falls back to defaults.

- **2025-10-05** Added _extract_coder_configuration helper: All renderers use consistent pattern for extracting coder-specific configuration from application configuration dictionary.

- **2025-10-06** Review feedback incorporated: Added os to package imports, renamed agentsmgr_configuration → application_configuration, simplified default_factory, fixed variable name truncations (env → environment, config → coder_configuration/directory).

- **2025-10-06** OpenCode configuration verified and corrected: Per OpenCode documentation, uses `OPENCODE_CONFIG` (not `OPENCODE_CONFIG_DIR`) to override default `~/.config/opencode` path. Per-project mode uses `.opencode/` directory in project root (not `.auxiliary/configuration/opencode/`). OpenCode supports both per-user (`~/.config/opencode/agent`) and per-project (`.opencode/agent`) configurations.

- **2025-10-06** Global settings support added to design: Added `defaults/globals/` directory to design document. Global settings controlled by `--update-globals` flag (orthogonal to `--mode`). Two types: direct-copy files (like `statusline.py`) and merge files (like `settings.json`). Renderers have built-in knowledge of settings file names.

- **2025-10-06** CLI semantics refined: Renamed `--target-mode` to `--mode` for clarity. Added `--update-globals` flag orthogonal to mode. Globals always populate to per-user locations regardless of mode. Default behavior: `--mode=per-project` with globals disabled for safety.

- **2025-10-06** Per-project path simplification: Changed from `.auxiliary/configuration/claude/` with symlinks to direct `.claude/` generation. Original symlink pattern was for sharing across coders, but only `memory.md` (formerly `conventions.md`) actually needs sharing. Memory file will still be symlinked across all coders.

- **2025-10-06** Review feedback round 2: Simplified default_factory to pass Dictionary class directly, renamed TOML field `config-dir` → `directory`, restructured globals from `defaults/configurations/globals` to `defaults/globals`, updated documentation `data/` → `defaults/`.

### Known Issues
None - Phase 2 implementation complete and all tests passing.

### Next Steps for Phase 3
1. Rename `target_mode` parameter to `mode` throughout codebase
2. Add `update_globals` parameter to PopulateCommand
3. Implement globals population logic
   - Survey `defaults/globals/{coder}/` for files
   - Direct copy for non-settings files
   - Merge logic for settings files (see `.auxiliary/notes/json-merge-strategies.md`)
4. Implement configuration file loading from `~/.config/emcd-agents/general.toml`
5. Implement memory file (`memory.md`) symlinking across coders
6. Add configuration validation and schema

### Context Dependencies
- agentsmgr_configuration parameter now flows through ContentGenerator to renderers
- PopulateCommand currently passes empty Dictionary for agentsmgr_configuration
- Phase 3 will add actual configuration file loading logic
