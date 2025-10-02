# Commands Module Refactoring Plan

## Current State

The `sources/agentsmgr/commands.py` file (~500 lines) has grown to handle multiple responsibilities:

- Error handling infrastructure (`intercept_errors` decorator)
- Four command implementations (Detect, Populate, Survey, Validate)
- Content generation logic (`ContentGenerator` class)
- Supporting utilities (population, content update, variant management)
- Duplicated configuration detection/validation between commands
- Inconsistent naming that doesn't follow project nomenclature standards

## Problems Identified

1. **Size and complexity**: Single file with too many responsibilities
2. **Code duplication**: `_detect_configuration` and `_validate_configuration` duplicated in DetectCommand and PopulateCommand
3. **Survey command**: Limited utility, can be replaced with shell commands
4. **Naming inconsistency**: Mix of `_get_*`, `_provide_*`, `_retrieve_*`, `_select_*` that doesn't align with `.auxiliary/instructions/nomenclature-latin.rst`
5. **Poor discoverability**: Hard to find specific functionality in large file

## Proposed Module Structure

```
sources/agentsmgr/commands/
├── __init__.py           # Re-exports command classes for CLI
├── base.py              # Shared infrastructure and utilities
├── generator.py         # Content generation logic
├── operations.py        # Core operations (populate, update)
├── detection.py         # DetectCommand
├── population.py        # PopulateCommand
└── validation.py        # ValidateCommand
```

### Module Responsibilities

#### `commands/__init__.py`
- Re-export command classes for CLI availability: `DetectCommand`, `PopulateCommand`, `ValidateCommand`
- Note: Backward compatibility is not a concern (prerelease project)

#### `commands/base.py` - Shared Infrastructure
- `intercept_errors` decorator (with improvements - see Error Handling section)
- `retrieve_configuration()` - unified configuration loading (replaces duplicated `_detect_configuration`)
- `validate_configuration()` - unified validation (replaces duplicated `_validate_configuration`)
- `retrieve_data_location()` - move from module level
- `retrieve_variant_answers_file()` - move from module level
- `CoderConfiguration` type alias

#### `commands/generator.py` - Content Generation
- `ContentGenerator` class
- `RenderedItem` dataclass
- All template-related logic and helpers

#### `commands/operations.py` - Core Operations
- `populate_directory()` - orchestrates content generation
- `update_content()` - file writing with simulation support
- `produce_coder_item_type()` - renamed from `_generate_coder_item_type` (see Nomenclature section)

#### `commands/detection.py` - Detection Command
- `DetectCommand` class only
- Uses shared `retrieve_configuration` from base

#### `commands/population.py` - Population Command
- `PopulateCommand` class only
- Uses shared `retrieve_configuration` from base
- Uses operations for directory population

#### `commands/validation.py` - Validation Command
- `ValidateCommand` class only
- Uses shared utilities from base
- Uses operations for directory population

#### Removed: `survey` command and `survey_variants()` function
**Rationale**:
- Limited utility (just lists filenames)
- Trivial to replicate with shell: `ls .../profiles/answers-*.yaml`
- Not integrated with any other functionality
- Maintenance burden with minimal value

## Error Handling Enhancement

### Current Approach
The `intercept_errors` decorator works well for separation of concerns, but could benefit from improved documentation.

### Proposed Improvement

**Keep the decorator as-is** (it's already correctly designed), but enhance its docstring to better explain:

1. **Purpose**: Clean separation between business logic and error handling/presentation
2. **Responsibilities**:
   - Intercepts `Omnierror` exceptions from command execution
   - Renders errors in appropriate format (markdown for CLI)
   - Ensures proper exit code handling (SystemExit with code 1)
3. **Pattern explanation**: Commands focus on business logic only; decorator handles all error presentation concerns
4. **Type narrowing note**: The `isinstance(auxdata, _core.Globals)` checks in individual command `execute` methods serve type narrowing purposes and should be retained

The existing implementation is correct. Only the docstring needs enrichment to clarify the separation of concerns pattern for future maintainers.

## Nomenclature Fixes

Following `.auxiliary/instructions/nomenclature-latin.rst`:

### In `ContentGenerator`:

| Current Name | Correct Name | Rationale |
|-------------|--------------|-----------|
| `_get_available_templates()` | `_survey_available_templates()` | "survey_&lt;resource&gt;: Lists or enumerates members of external resource collection" |
| `_get_content_with_fallback()` | `_retrieve_content_with_fallback()` | "retrieve_&lt;resource&gt;: Obtains copy of data from external resource" |
| `_get_output_extension()` | `_parse_template_extension()` | "parse_&lt;format&gt;: Extracts structured data from formatted input" (note: "output" is Germanic-derived) |
| `_provide_jinja_environment()` | `_produce_jinja_environment()` | "produce_&lt;object&gt;: Creates new instance in process memory" |

### In module-level functions:

| Current Name | Correct Name | Rationale |
|-------------|--------------|-----------|
| `_generate_coder_item_type()` | `produce_coder_item_type()` | "produce_&lt;object&gt;: Creates new instance in process memory" (generates content objects) |

### Keep as-is:
- `_select_template_for_coder()` - "select" is reasonable for filtering/choosing logic
- `_retrieve_data_location()` - already correct
- `_retrieve_variant_answers_file()` - already correct
- `_load_item_metadata()` - Germanic "load" is acceptable alternative to Latin "retrieve"
- `render_single_item()` - "render_&lt;template&gt;: Produces output by combining template with data" (correct)

## Implementation Steps

### Phase 1: Create Module Structure
1. Create `sources/agentsmgr/commands/` directory
2. Create `__init__.py` with imports for CLI availability
3. Create empty module files: `base.py`, `generator.py`, `operations.py`, `detection.py`, `population.py`, `validation.py`

### Phase 2: Extract Shared Infrastructure (`base.py`)
1. Move `intercept_errors` decorator and enhance its docstring (see Error Handling section)
2. Extract unified `retrieve_configuration()` from DetectCommand/PopulateCommand
3. Extract unified `validate_configuration()` from DetectCommand/PopulateCommand
4. Move `CoderConfiguration` type alias
5. Move `retrieve_data_location()` and `retrieve_variant_answers_file()`
6. Add appropriate imports and module docstring

### Phase 3: Extract Content Generation (`generator.py`)
1. Move `RenderedItem` dataclass
2. Move `ContentGenerator` class
3. Apply nomenclature fixes to ContentGenerator methods
4. Update imports to reference `base` module
5. Add module docstring

### Phase 4: Extract Operations (`operations.py`)
1. Move `populate_directory()`
2. Move `update_content()`
3. Move and rename `_generate_coder_item_type()` → `produce_coder_item_type()`
4. Update imports
5. Add module docstring

### Phase 5: Split Command Classes
1. Move `DetectCommand` to `detection.py`, update to use `base.retrieve_configuration()`
2. Move `PopulateCommand` to `population.py`, update to use `base.retrieve_configuration()`
3. Move `ValidateCommand` to `validation.py`
4. Remove `SurveyCommand` entirely (drop the feature)
5. Update each command to import from appropriate modules
6. Retain `isinstance(auxdata, _core.Globals)` checks in execute methods (type narrowing)

### Phase 6: Update `__init__.py`
1. Import and re-export: `DetectCommand`, `PopulateCommand`, `ValidateCommand`
2. Add `__all__` for explicit public API

### Phase 7: Update Tests
1. Update import paths in tests to use `commands.DetectCommand` etc.
2. Remove tests for `SurveyCommand`
3. Add tests for new shared utilities in `base.py`
4. Verify all tests pass

### Phase 8: Update Documentation
1. Update any references to `survey` command in docs
2. Update module documentation to reflect new structure

## Testing Strategy

- Ensure command classes remain importable: `from agentsmgr.commands import DetectCommand` works
- All existing tests should pass with minimal changes (only import paths)
- Add new tests for extracted shared utilities in `base.py`
- Verify each command works independently

## Type Aliases Strategy

Current state: Only `CoderConfiguration` type alias exists.

Decision: **Move to `base.py` for now**. Create `nomina.py` only if:
- We accumulate 5+ type aliases, or
- Type aliases become complex (unions, generics, protocols), or
- Other modules need to import these types

This follows the pattern used in other packages and avoids premature abstraction.

## Migration Notes

### Changes
- **Removal**: `SurveyCommand` and `survey_variants()` function dropped entirely
  - Check internal usage before removal (unlikely to be widely used)
- **Module structure**: Commands split into separate modules (`detection.py`, `population.py`, `validation.py`)
  - Command classes remain importable from `agentsmgr.commands`
- **Nomenclature**: Internal method names updated to follow project standards
  - External API unchanged

### Note on Backward Compatibility
This is a prerelease project, so backward compatibility is not a primary concern. Focus on correct design and clean architecture.

## Success Criteria

- [ ] No file exceeds 300 lines
- [ ] No duplicated configuration loading logic
- [ ] All nomenclature follows `.auxiliary/instructions/nomenclature-latin.rst`
- [ ] All tests pass
- [ ] Survey command removed entirely
- [ ] Command classes remain importable: `from agentsmgr.commands import DetectCommand` works
- [ ] Each module has clear, focused responsibility
- [ ] Error handling decorator has enhanced docstring explaining separation of concerns
- [ ] Type narrowing `isinstance` checks retained in command execute methods
