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

### Next Steps for Phase 2
1. Add agentsmgr_config loading from ~/.config/emcd-agents/general.toml
2. Implement per-user mode support in renderers
3. Add environment variable resolution (CLAUDE_CONFIG_DIR, CODEX_HOME, etc.)
4. Update PopulateCommand to accept --target-mode CLI flag
5. Add targeting mode validation and helpful error messages

### Known Issues
None - implementation complete and stable.

### Context Dependencies
- Renderer protocol parameters (agentsmgr_config, env) are intentionally unused in Phase 1
- All renderers currently only support per-project mode
- Self-registration pattern requires imports at bottom of __init__.py (E402 suppression necessary)
