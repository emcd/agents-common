# agentsmgr CLI Cleanup Plan

## Executive Summary

The current implementation violates appcore CLI architectural patterns by:
- Scattering error handling throughout the codebase instead of centralizing at command level
- Using direct `print()` calls instead of proper logging and display routing
- Missing integration with appcore's display/inscription system
- Creating fallback defaults instead of explicit error handling

**Resolution Strategy**: Adopt **Option B** - Keep `ContentGenerator` as a pure rendering engine, move all I/O, logging, and display concerns to the command layer.

## Architectural Reference

### appcore Pattern (from python-appcore/sources/appcore/introspection.py)

Commands receive `auxdata` with configured display/inscription:
```python
class ApplicationGlobals(state.Globals):
    display: DisplayOptions  # Extended with custom display options

class Command:
    async def execute(self, auxdata: state.Globals) -> None:
        # Use display for structured output
        await auxdata.display.render(data)

# Logging uses standard Python logging
scribe = __.produce_scribe(__package__)  # getLogger alias
scribe.debug("message")
scribe.info("message")
scribe.warning("message")
```

## Issues Requiring Resolution

### 1. Deep Exception Interception (L145)

**Current Code**:
```python
def generate(self, target: Path, simulate: bool = True) -> None:
    try:
        for coder in self.configuration["coders"]:
            self._generate_coder_content(coder, target, simulate)
    except Exception as exception:
        print(f"⚠️  Failed to generate {coder} content: {exception}")
```

**Problems**:
- Bypasses `@intercept_errors()` decorator at command level
- Direct `print()` bypasses display routing
- Overly broad exception handler swallows errors silently
- Can't honor display format choices

**Resolution**: Remove this try-except entirely. Let exceptions propagate to command's `execute()` where `@intercept_errors()` handles them uniformly.

### 2. Direct Print Instead of Logging (L175, L202, L248, L260)

**Current Code**:
```python
print(f"📁 Generating content for {coder}:")
print(f"   🔄 Using {fallback_coder} content for {coder}")
print(f"   ⚠️  No {item_type} configurations found")
print(f"   ✅ {result.location}")
```

**Problems**:
- These are logging messages, not display output
- Can't be controlled by inscription (logging) options
- Mixed responsibilities: output generation vs. progress reporting

**Resolution**: Replace with proper logging:
```python
scribe = __.produce_scribe(__package__)
scribe.info(f"Generating content for {coder}")
scribe.debug(f"Using {fallback_coder} content for {coder}")
scribe.warning(f"No {item_type} configurations found")
scribe.debug(f"Generated {result.location}")
```

### 3. Missing Display Options Integration (L260)

**Current Code**: Commands print result objects directly:
```python
for line in result.render_as_markdown():
    print(line)
```

**Problems**:
- Hardcoded to Markdown format only
- No stream routing (always stdout)
- No file output support
- Doesn't integrate with appcore display system

**Resolution**:
1. Extend `DisplayOptions` with `Presentations` enum (Markdown initially, JSON/TOML later)
2. Keep `render_as_markdown()` methods on result/exception objects
3. Add switch logic in commands based on presentation format
4. Pattern follows librovore: `_render_and_print_result()` helper function

**Implementation Pattern** (from python-librovore/sources/librovore/cli.py):
```python
# interfaces.py
class Presentations(enum.Enum):
    Markdown = 'markdown'
    # Future: Json, Toml, etc.

# state.py
class DisplayOptions(appcore_cli.DisplayOptions):
    presentation: Presentations = Presentations.Markdown

class ApplicationGlobals(appcore.state.Globals):
    display: DisplayOptions

# commands.py
async def _render_and_print_result(
    result: ResultBase,
    display: DisplayOptions,
    exits: ctxl.AsyncExitStack,
    **nomargs: Any
) -> None:
    stream = await display.provide_stream(exits)
    match display.presentation:
        case Presentations.Markdown:
            lines = result.render_as_markdown(**nomargs)
            if display.determine_colorization(stream):
                # Optional: Rich formatting
                console = Console(file=stream, force_terminal=True)
                markdown_obj = Markdown('\n'.join(lines))
                console.print(markdown_obj)
            else:
                print('\n'.join(lines), file=stream)
        # Future: case Presentations.Json: ...

class Command:
    async def execute(self, auxdata: ApplicationGlobals) -> None:
        result = detect_configuration()
        await _render_and_print_result(result, auxdata.display, auxdata.exits)
```

### 4. Silent Fallback Extension (L211)

**Current Code**:
```python
def _get_output_extension(self, template_name: str) -> str:
    parts = template_name.split('.')
    if len(parts) >= 3 and parts[-1] == 'jinja':
        return parts[-2]
    return 'txt'  # Silent fallback
```

**Problem**: User has repeatedly requested "no fallbacks/defaults" - errors should fail explicitly.

**Resolution**: Raise exception if extension cannot be determined:
```python
def _get_output_extension(self, template_name: str) -> str:
    parts = template_name.split('.')
    if len(parts) >= 3 and parts[-1] == 'jinja':
        return parts[-2]
    raise TemplateExtensionError(template_name)
```

### 5. Hardcoded Fallback Map (L195)

**Current Code**:
```python
fallback_map = {"claude": "opencode", "opencode": "claude"}
```

**Problem**: Not extensible for Gemini and future coders.

**Resolution**: Add TODO to make configuration-based (user already aware of this need).

### 6. Overly-Broad Try Block (L381)

**Current Code**:
```python
try:
    temporary_directory = Path(tempfile.mkdtemp(...))
except (OSError, IOError) as exception:
    raise DirectoryCreateFailure(...) from exception
try:
    configuration = self._create_test_configuration()
    location = _retrieve_data_location("defaults")
    generator = ContentGenerator(...)
    items_attempted, items_generated = populate_directory(...)
finally:
    if not self.preserve:
        with suppress(OSError, IOError):
            shutil.rmtree(temporary_directory)
```

**Problem**: Second try block covers multiple operations but only has finally clause. If operations fail, exception propagates without cleanup context.

**Resolution**: Use narrower try-except blocks or contextmanager for temporary directory.

### 7. Fragile __file__ Relative Path (L436)

**Current Code**:
```python
data_directory = Path(__file__).parent.parent.parent / 'data'
```

**Problem**: Breaks if module structure changes, doesn't use package data system.

**Resolution**: Propagate `auxdata` to functions that need package data paths:
```python
def survey_variants(auxdata: state.Globals) -> tuple[str, ...]:
    data_directory = auxdata.distribution.provide_data_location()
    profiles_directory = data_directory / 'agentsmgr' / 'profiles'
    ...
```

## Recommended Architecture: Option B

**Principle**: `ContentGenerator` should be a pure rendering engine. Commands handle all I/O, logging, and display through `auxdata`.

### Separation of Concerns

**ContentGenerator Responsibilities** (Pure):
- Template loading and Jinja2 environment setup
- Content lookup with fallback logic
- Template rendering with variable substitution
- Return structured data (RenderedItem)

**Command Responsibilities** (I/O):
- Progress logging via `scribe`
- File writing with error handling
- Display output via `auxdata.display.render()`
- Error handling via `@intercept_errors()`

### Propagation Pattern

Do NOT propagate `auxdata` into `ContentGenerator`. Instead:

1. Commands receive `auxdata` with display/inscription configured
2. Commands use `scribe` for progress logging
3. Commands call generator methods (pure functions)
4. Commands handle file I/O using generator results
5. Commands render final output via `auxdata.display`

### Example Refactored Flow

```python
# Command layer (I/O concerns)
class PopulateCommand(Command):
    @intercept_errors()
    async def execute(self, auxdata: ApplicationGlobals) -> None:
        scribe = __.produce_scribe(__package__)

        configuration = await self._detect_configuration(self.target)
        location = auxdata.distribution.provide_data_location() / 'defaults'
        generator = ContentGenerator(location=location, configuration=configuration)

        scribe.info(f"Generating content for {len(configuration['coders'])} coders")

        items_attempted, items_written = self._populate_directory(
            generator, self.target, self.simulate, scribe
        )

        result = ContentGenerationResult(
            source_location=location,
            target_location=self.target,
            coders=tuple(configuration['coders']),
            simulated=self.simulate,
            items_generated=items_written,
        )

        await auxdata.display.render(result)

# Generator layer (pure rendering)
class ContentGenerator:
    def render_single_item(self, item_type: str, item_name: str, coder: str, target: Path) -> RenderedItem:
        # Pure function - no I/O, no logging, no display
        # Just template loading and rendering
        ...
        return RenderedItem(content=content, location=location)
```

## Implementation Checklist

### Phase 1: Display Options Extension ✅ COMPLETE
- [x] Create `Presentations` enum in cli module with `Markdown` variant only (future: Json, Toml)
- [x] Create `DisplayOptions(appcore_cli.DisplayOptions)` subclass in cli module
- [x] Create `Globals(appcore.state.Globals)` with display options in cli module
- [x] Implement `_render_and_print_result()` helper with match statement on presentation
- [x] Implement `Application.prepare()` method to construct custom Globals
- [x] Add Jinja2 and PyYAML to main dependencies (were only in dev)
- [x] Add Vulture suppressions for new infrastructure classes/functions
- [x] Verify CLI functionality in both default and develop environments

**Implementation Notes:**
- Consolidated all state classes in cli.py per user feedback (no separate interfaces/state modules needed)
- Followed librovore pattern exactly for consistency
- Added pyright ignore for method override compatibility (standard pattern in librovore)
- All tests passing, all linters passing (0 errors, 0 warnings)
- See `.auxiliary/notes/cli-cleanup-phase1--progress.md` for detailed tracking

### Phase 2: Logging Integration ✅ COMPLETE
- [x] Replace all `print()` with `provide_scribe()` calls
- [x] Use appropriate log levels (debug, info, warning)
- [x] Remove progress messages from ContentGenerator
- [x] Add logging to command execute() methods

**Implementation Notes:**
- Added module-level `_scribe = __.provide_scribe(__package__)` in commands.py
- ContentGenerator uses info/debug/warning levels appropriately
- All commands (Detect, Populate, Validate) now include logging
- Removed deep exception handler from ContentGenerator.generate()
- All tests passing, all linters passing (0 errors, 0 warnings)
- See `.auxiliary/notes/cli-cleanup-phase2--progress.md` for detailed tracking

### Phase 3: Error Handling ✅ COMPLETE
- [x] Remove deep exception handler from ContentGenerator.generate() (completed in Phase 2)
- [x] Remove 'txt' fallback from _get_output_extension()
- [x] Add TemplateExtensionError exception
- [x] Narrow exception scope in ValidateCommand (improved with logging in Phase 2)

**Implementation Notes:**
- Added TemplateExtensionError exception following Omnierror hierarchy
- Removed silent 'txt' fallback from _get_output_extension()
- Method now raises TemplateExtensionError when extension cannot be determined
- All tests passing, all linters passing (0 errors, 0 warnings)
- See `.auxiliary/notes/cli-cleanup-phase3--progress.md` for detailed tracking

### Phase 4: Package Data Paths ✅ COMPLETE
- [x] Propagate auxdata to survey_variants() (L452)
- [x] Use auxdata.provide_data_location()
- [x] Update _retrieve_variant_answers_file() to use auxdata
- [x] Update ValidateCommand._create_test_configuration() to use auxdata
- [x] Create core.py module to avoid circular imports
- [x] Add type guards with ContextInvalidity exception

**Implementation Notes:**
- Created `core.py` module with `Presentations`, `DisplayOptions`, and `Globals` to avoid circular import between `cli.py` and `commands.py`
- Added `ContextInvalidity` exception following librovore pattern for type guard validation
- Replaced all __file__-relative paths with auxdata.provide_data_location()
- Functions now accept `_core.Globals` parameter: survey_variants(), _retrieve_variant_answers_file(), ValidateCommand._create_test_configuration()
- Command execute() methods use type guards: `if not isinstance(auxdata, _core.Globals): raise _exceptions.ContextInvalidity`
- Only execute() methods use base `appcore.state.Globals` for signature compatibility; internal functions use specific `_core.Globals` type
- Did NOT update _retrieve_data_location() - currently only handles local paths, no need for auxdata until remote git sources implemented
- All tests passing (9 tests), all linters passing (0 errors, 0 warnings)
- CLI verified working: `hatch run agentsmgr --help`, `agentsmgr detect`, `agentsmgr survey`

### Phase 5: Result Rendering ✅ COMPLETE
- [x] Keep `render_as_markdown()` methods on result/exception objects
- [x] Add switch logic based on `Presentations` enum to call appropriate render method
- [x] Pattern: `match auxdata.display.presentation: case Presentations.Markdown: result.render_as_markdown()`
- [x] Update all command execute() methods to use centralized render_and_print_result()
- [x] Update intercept_errors() to use centralized rendering for exceptions
- [x] Create Renderable protocol for type safety
- [x] Move render_and_print_result() from cli.py to core.py to avoid circular imports
- [ ] Future: Add `render_as_json()`, `render_as_toml()` methods when formats added

**Implementation Notes:**
- Created Renderable protocol in core.py for type-safe rendering interface
- Moved render_and_print_result() from cli.py to core.py to avoid circular import issues
- All command execute() methods now use centralized rendering
- intercept_errors() decorator now renders exceptions through centralized logic
- Added type guards for Globals in command execute() methods
- All tests passing (9 tests), all linters passing (0 errors, 0 warnings)
- CLI verified working: detect, populate, survey, validate commands

### Phase 6: Configuration-Based Fallbacks
- [ ] See TODO in .auxiliary/notes/todo.md for configuration-based fallback design

## Testing Considerations

After refactoring:
1. Validate all commands work with different display presentations
2. Test logging output at different inscription levels
3. Verify stream routing (stdout/stderr) works correctly
4. Confirm file output works for both display and inscription
5. Ensure package data paths resolve correctly

## References

- appcore pattern: `../python-appcore/sources/appcore/introspection.py`
- Display options: `../python-appcore/sources/appcore/cli.py`
- State/Globals: `../python-appcore/sources/appcore/state.py`
- Logging: `__.produce_scribe()` → `logging.getLogger()`
