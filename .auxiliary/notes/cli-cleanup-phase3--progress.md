# CLI Cleanup Phase 3: Error Handling - Progress Tracking

## Context and References

- **Implementation Title**: Remove fallback defaults and improve explicit error handling
- **Start Date**: 2025-09-30
- **Reference Files**:
  - `.auxiliary/notes/cli-cleanup.md` - Overall cleanup plan and architectural guidance
  - `.auxiliary/instructions/practices-python.rst` - Python development patterns
  - `sources/agentsmgr/commands.py` - ContentGenerator with fallback default
  - `sources/agentsmgr/exceptions.py` - Exception hierarchy
- **Design Documents**:
  - `.auxiliary/notes/cli-cleanup.md` Phase 3 specification
- **Session Notes**: TodoWrite tracking for current implementation session

## Design and Style Conformance Checklist

- [x] Module organization follows practices guidelines
- [x] Function signatures use wide parameter, narrow return patterns
- [x] Type annotations comprehensive with TypeAlias patterns
- [x] Exception handling follows Omniexception → Omnierror hierarchy
- [x] Naming follows nomenclature conventions
- [x] Immutability preferences applied
- [x] Code style follows formatting guidelines
- [x] No silent fallbacks - explicit error handling

## Implementation Progress Checklist

### Error Handling Improvements
- [x] Remove deep exception handler from ContentGenerator.generate() (completed in Phase 2)
- [x] Add TemplateExtensionError exception class
- [x] Remove 'txt' fallback from _get_output_extension()
- [x] Raise TemplateExtensionError when extension cannot be determined
- [x] ValidateCommand exception scope (already improved in Phase 2)

## Quality Gates Checklist

- [x] Linters pass (`hatch --env develop run linters`)
- [x] Type checker passes
- [x] Tests pass (`hatch --env develop run testers`)
- [x] Code review ready

## Decision Log

- 2025-09-30: Per user requirement "no fallbacks/defaults" - errors should fail explicitly
- 2025-09-30: TemplateExtensionError follows nomenclature: <Noun><Property>Error pattern
- 2025-09-30: Shortened error message to fit 79-character line limit

## Handoff Notes

### Current State
✅ Phase 3 COMPLETE - All error handling improvements implemented and tested.

### Changes Made
1. **TemplateExtensionError exception** (exceptions.py:91-96):
   - Added new exception class following Omnierror hierarchy
   - Inherits from Omnierror and ValueError
   - Clear error message for template extension determination failures
2. **_get_output_extension() improvement** (commands.py:207-212):
   - Removed silent 'txt' fallback
   - Now raises TemplateExtensionError when extension cannot be determined
   - Maintains same logic for valid templates (name.ext.jinja → ext)

### Next Steps
Phase 4 (Package Data Paths) items:
- Propagate auxdata to survey_variants()
- Use auxdata.distribution.provide_data_location()
- Update _retrieve_data_location() and _retrieve_variant_answers_file()

Phase 5 (Result Rendering):
- Keep render_as_markdown() methods on result objects
- Add switch logic for Presentations enum
- Future: Add render_as_json(), render_as_toml()

### Known Issues
None - all tests passing, all linters passing.

### Context Dependencies
- Phases 1 and 2 provide display options and logging infrastructure
- Exception properly integrated into Omnierror hierarchy
- Error will be caught by @intercept_errors() decorator for proper display
