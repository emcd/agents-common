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

### Phase 1: Display Options Extension
- [ ] Create `Presentations` enum in interfaces module with `Markdown` variant only (future: Json, Toml)
- [ ] Create `DisplayOptions(appcore_cli.DisplayOptions)` subclass in state module
- [ ] Create `ApplicationGlobals(appcore.state.Globals)` with display options
- [ ] Implement `_render_and_print_result()` helper with match statement on presentation

### Phase 2: Logging Integration
- [ ] Replace all `print()` with `produce_scribe()` calls
- [ ] Use appropriate log levels (debug, info, warning)
- [ ] Remove progress messages from ContentGenerator
- [ ] Add logging to command execute() methods

### Phase 3: Error Handling
- [ ] Remove deep exception handler from ContentGenerator.generate() (L145)
- [ ] Remove 'txt' fallback from _get_output_extension() (L211)
- [ ] Add TemplateExtensionError exception
- [ ] Narrow exception scope in ValidateCommand (L381)

### Phase 4: Package Data Paths
- [ ] Propagate auxdata to survey_variants() (L436)
- [ ] Use auxdata.distribution.provide_data_location()
- [ ] Update _retrieve_data_location() to use auxdata
- [ ] Update _retrieve_variant_answers_file() to use auxdata

### Phase 5: Result Rendering
- [ ] Keep `render_as_markdown()` methods on result/exception objects
- [ ] Add switch logic based on `Presentations` enum to call appropriate render method
- [ ] Pattern: `match auxdata.display.presentation: case Presentations.Markdown: result.render_as_markdown()`
- [ ] Future: Add `render_as_json()`, `render_as_toml()` methods when formats added

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
