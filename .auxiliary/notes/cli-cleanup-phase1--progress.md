# CLI Cleanup Phase 1: Display Options Extension - Implementation Progress

## Context and References

- **Implementation Title**: Display Options Extension for appcore CLI Pattern Compliance
- **Start Date**: 2025-09-30
- **Reference Files**:
  - `.auxiliary/notes/cli-cleanup.md` - Overall cleanup plan and architectural guidance
  - `../python-appcore/sources/appcore/introspection.py` - appcore pattern reference
  - `../python-appcore/sources/appcore/cli.py` - Display options reference
  - `../python-appcore/sources/appcore/state.py` - State/Globals reference
  - `../python-librovore/sources/librovore/cli.py` - Display pattern implementation example
  - `.auxiliary/instructions/practices.rst` - General practices
  - `.auxiliary/instructions/practices-python.rst` - Python-specific practices
- **Design Documents**: None (following existing appcore patterns)
- **Session Notes**: TodoWrite tracking in current session

## Design and Style Conformance Checklist

- [x] Module organization follows practices guidelines (imports, type aliases, private constants, public classes/functions)
- [x] Function signatures use wide parameter, narrow return patterns
- [x] Type annotations comprehensive with TypeAlias patterns for reused types
- [x] Exception handling follows Omniexception → Omnierror hierarchy (N/A - no exceptions added)
- [x] Naming follows nomenclature conventions (enum PascalCase members, etc.)
- [x] Immutability preferences applied (using `__.immut` where appropriate - used __.immut.DataclassObject)
- [x] Code style follows formatting guidelines (spacing, line length, etc.)

## Implementation Progress Checklist

Phase 1 specific tasks:
- [x] Create `Presentations` enum in cli module with `Markdown` variant
- [x] Create `DisplayOptions(appcore_cli.DisplayOptions)` subclass in cli module
- [x] Create `Globals(appcore.state.Globals)` with display options
- [x] Implement `_render_and_print_result()` helper with match statement on presentation
- [x] Implement `Application.prepare()` to construct Globals with display options
- [x] Integration tested with existing commands (all tests pass)

## Quality Gates Checklist

- [x] Linters pass (`hatch --env develop run linters`) - Only expected vulture warning for unused _render_and_print_result (will be used in Phase 2)
- [x] Type checker passes (Pyright via linters)
- [x] Tests pass (`hatch --env develop run testers`) - 8 passed
- [x] Code review ready

## Decision Log

- [2025-09-30] Following Option B architecture: ContentGenerator remains pure, commands handle all I/O through auxdata - Aligns with appcore architectural patterns and maintains clean separation of concerns
- [2025-09-30] Using librovore pattern for `_render_and_print_result()` helper - Proven pattern with proper stream routing, colorization detection, and extensibility
- [2025-09-30] Consolidated state classes into cli.py module - User feedback: separate interfaces/state modules not needed for this scale, keep everything in cli.py
- [2025-09-30] Application.prepare() pattern from librovore - Extends base Globals with display options by extracting fields from base and reconstructing with custom display
- [2025-09-30] Added Jinja2 and PyYAML to main dependencies - Previously only in dev dependencies, needed for runtime functionality in commands.py

## Handoff Notes

### Current State
**Phase 1: COMPLETE** ✅

All infrastructure is in place:
- `Presentations` enum with `Markdown` variant in cli.py
- `DisplayOptions` extending appcore_cli.DisplayOptions with presentation field
- `Globals` extending appcore.state.Globals with display field
- `_render_and_print_result()` helper function with Rich integration
- `Application.prepare()` method to construct custom Globals
- All tests passing (8 passed)
- All linters passing (Vulture suppressions added to vulturefood.py)
- CLI functionality verified (`agentsmgr --help`, `agentsmgr detect --help`, `agentsmgr survey`)
- Display options visible in CLI help: `--display.presentation {Markdown}`

### Next Steps
**Phase 2: Logging Integration** - Replace all `print()` calls with proper logging

1. Import `produce_scribe` or equivalent logging utility in commands module
2. Replace progress `print()` statements in ContentGenerator with scribe calls
3. Move logging to command execute() methods
4. Use appropriate log levels: debug (detailed progress), info (major milestones), warning (fallback usage)
5. Remove print() calls from ContentGenerator entirely

Reference: `.auxiliary/notes/cli-cleanup.md` Phase 2 section

### Known Issues
- None - Phase 1 complete and working

### Context Dependencies
- appcore available as dependency ✅
- Rich library available for markdown rendering ✅
- Pattern proven in librovore reference implementation ✅
- Commands will need to use _render_and_print_result() in Phase 5
