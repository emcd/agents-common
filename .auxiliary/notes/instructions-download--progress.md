# Instructions Download Implementation Progress

## Context and References

- **Implementation Title**: Instruction downloading support for agentsmgr
- **Start Date**: 2025-10-23
- **Reference Files**:
  - `.auxiliary/notes/instructions-retrieval.md` - Technical analysis and design proposal
  - `documentation/architecture/summary.rst` - System architecture overview
  - `documentation/architecture/filesystem.rst` - Filesystem organization patterns
  - `.auxiliary/instructions/practices-python.rst` - Python development guide
- **Design Documents**: `.auxiliary/notes/instructions-retrieval.md` (Option A: Native Git Source Handler)
- **Session Notes**: Using TodoWrite tool for session-level tracking

## Design and Style Conformance Checklist

- [x] Module organization follows practices guidelines
- [x] Function signatures use wide parameter, narrow return patterns
- [x] Type annotations comprehensive with TypeAlias patterns
- [x] Exception handling follows Omniexception → Omnierror hierarchy
- [x] Naming follows nomenclature conventions
- [x] Immutability preferences applied
- [x] Code style follows formatting guidelines

## Implementation Progress Checklist

- [x] Create `sources/agentsmgr/instructions.py` module
- [x] Implement `populate_instructions` function
- [x] Implement `preprocess_content` helper function
- [x] Add configuration schema to `copier.yaml` (already present)
- [x] Integrate into `PopulateCommand.execute()` in `sources/agentsmgr/population.py`
- [ ] Test integration with existing git source handlers (manual testing needed)
- [ ] Test file filtering with glob patterns (manual testing needed)
- [ ] Test header stripping preprocessing (manual testing needed)

## Quality Gates Checklist

- [x] Linters pass (`hatch --env develop run linters`)
- [x] Type checker passes
- [x] Tests pass (`hatch --env develop run testers`)
- [x] Code review ready

## Decision Log

- [2025-10-23] Chose Option A (Native Git Source Handler) - Leverages existing infrastructure, maintains architectural consistency, supports version-controlled distribution
- [2025-10-23] Configuration-driven behavior (no CLI flag) - Uses `provide_instructions` boolean in copier.yaml for declarative control
- [2025-10-23] Per-file preprocessing configuration - Supports flexible glob pattern mapping to different strip_header_lines values
- [2025-10-23] Exception hierarchy design - Created InstructionSourceInvalidity base with specific subclasses (InstructionSourceFieldAbsence, InstructionFilesConfigurationInvalidity) to avoid TRY003 linter violations
- [2025-10-23] Type casting strategy - Used explicit type annotations and cast for configuration mappings to satisfy Pyright strict type checking
- [2025-10-23] Path handling - Used try/except for relative_to() instead of walk_up parameter for Python 3.9+ compatibility
- [2025-10-23] Exception module organization - Moved instruction-related exception classes to exceptions.py module per code review feedback for consistency with project architecture

## Handoff Notes

### Current State
- **COMPLETED**: Full implementation of instruction downloading support
- Created `sources/agentsmgr/instructions.py` with 200 lines implementing:
  - `populate_instructions()` - Main entry point for instruction population
  - `_populate_instructions_from_location()` - Processes files from resolved source
  - `_process_and_write_instruction_file()` - Handles individual file processing
  - `_preprocess_content()` - Applies header stripping and other transforms
- Integrated into `PopulateCommand.execute()` in `sources/agentsmgr/population.py`
- Configuration schema already present in `copier.yaml`
- All quality gates passed: linters, type checker, test suite

### Next Steps
1. Manual testing with real Git sources to verify end-to-end functionality
2. Consider adding unit tests for instructions module (currently 14% coverage)
3. Test with various glob patterns and preprocessing configurations
4. Verify integration with downstream projects using Copier

### Known Issues
- No automated tests yet for instructions module (manual testing recommended)
- Module coverage at 14% (expected for new untested code)

### Context Dependencies
- Successfully leveraged existing GitSourceHandler via sources.resolve_source_location()
- Uses standard Copier configuration patterns from copier.yaml
- Follows established logging patterns with _scribe
- Integrates seamlessly with existing PopulateCommand flow
