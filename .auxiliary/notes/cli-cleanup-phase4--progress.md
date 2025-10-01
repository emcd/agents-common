# CLI Cleanup Phase 4: Package Data Paths - Progress Tracking

## Context and References

- **Implementation Title**: Replace __file__-relative paths with auxdata distribution paths
- **Start Date**: 2025-09-30
- **Reference Files**:
  - `.auxiliary/notes/cli-cleanup.md` - Overall cleanup plan and architecture
  - `sources/agentsmgr/commands.py` - Commands using package data paths
  - `sources/agentsmgr/generators.py` - ContentGenerator using __file__ relative paths
- **Design Documents**:
  - `documentation/architecture/summary.rst` - System architecture
  - `.auxiliary/instructions/practices-python.rst` - Python development practices
- **Session Notes**: TodoWrite tracking in current session

## Design and Style Conformance Checklist

- [x] Module organization follows practices guidelines
- [x] Function signatures use wide parameter, narrow return patterns
- [x] Type annotations comprehensive with TypeAlias patterns
- [x] Exception handling follows Omniexception → Omnierror hierarchy
- [x] Naming follows nomenclature conventions
- [x] Immutability preferences applied
- [x] Code style follows formatting guidelines

## Implementation Progress Checklist

- [x] Examine current __file__-relative path usage (L447, L509 in commands.py)
- [x] Propagate auxdata to survey_variants() function
- [x] Update _retrieve_variant_answers_file() to accept and use auxdata
- [x] Update ValidateCommand._create_test_configuration() to accept auxdata
- [x] Update all call sites to pass auxdata parameter
- [x] Verify ValidateCommand integration with new signature

## Quality Gates Checklist

- [x] Linters pass (`hatch --env develop run linters`)
- [x] Type checker passes
- [x] Tests pass (`hatch --env develop run testers`)
- [x] Code review ready

## Decision Log

- [2025-09-30] Use auxdata.provide_data_location() instead of __file__ - Follows appcore pattern for package data access, makes code resilient to module structure changes
- [2025-09-30] Propagate auxdata parameter through function chain - survey_variants(), _retrieve_variant_answers_file(), and ValidateCommand._create_test_configuration() now all accept auxdata parameter
- [2025-09-30] Did NOT update _retrieve_data_location() - Function currently only handles local file paths, no need for auxdata until remote git sources are implemented
- [2025-09-30] Created core.py module - Factor out DisplayOptions, Presentations, and Globals to avoid circular import between cli.py and commands.py
- [2025-09-30] Use _core.Globals type for internal functions - Only execute() methods use base appcore.state.Globals for signature compatibility, all internal functions use our specific _core.Globals type
- [2025-09-30] Add ContextInvalidity exception - Following librovore pattern for type guard validation with # pragma: no cover

## Handoff Notes

### Current State
- Phase 4 implementation COMPLETE
- All __file__-relative paths replaced with auxdata.provide_data_location()
- Created core.py module to avoid circular imports
- All quality gates passing (linters, type checker, tests)
- Changes:
  - **New module**: `core.py` - Contains `Presentations`, `DisplayOptions`, and `Globals`
  - **New exception**: `ContextInvalidity` - For type guard validation
  - `survey_variants()`: Now accepts `_core.Globals` parameter, uses `auxdata.provide_data_location()`
  - `_retrieve_variant_answers_file()`: Now accepts `_core.Globals` parameter, uses `auxdata.provide_data_location()`
  - `ValidateCommand._create_test_configuration()`: Now accepts `_core.Globals` parameter, passes to `_retrieve_variant_answers_file()`
  - `SurveyCommand.execute()`: Type guard + passes `auxdata` to `survey_variants()`
  - `ValidateCommand.execute()`: Type guard + passes `auxdata` to `_create_test_configuration()`
  - `cli.py`: Imports from `_core` instead of defining types locally
  - `commands.py`: Imports from `_core` for type annotations

### Next Steps
1. Phase 5: Result Rendering (add switch logic based on Presentations enum)
2. Phase 6: Configuration-Based Fallbacks

### Known Issues
- None

### Context Dependencies
- Functions require auxdata with distribution configured
- Test infrastructure provides proper auxdata through appcore CLI framework
