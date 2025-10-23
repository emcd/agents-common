# Technical Analysis: Integrating Instruction Download into agentsmgr

**Date**: 2025-10-23
**Status**: Proposal for Review

## Current State Assessment

### prepare-agents Script Functionality

The bash script at `.auxiliary/scripts/prepare-agents:68-112` provides instruction downloading functionality that:

1. **Downloads documentation guides** from a GitHub raw content URL
2. **Strips boilerplate** (first 20 lines) from each file using `tail -n +20`
3. **Saves to `.auxiliary/instructions/`** directory
4. **Provides progress feedback** with success/failure counts
5. **Handles errors gracefully** with file cleanup on empty results

The downloaded files include:
- `architecture.rst`, `nomenclature.rst`, `practices.rst`, `style.rst`, `tests.rst`, etc.
- Source: `https://raw.githubusercontent.com/emcd/python-project-common/refs/tags/docs-1/documentation/common`

### agentsmgr Architecture

The Python codebase demonstrates:

1. **Plugin-based source handling** via decorator registration (`@source_handler`)
2. **Git source resolution** with Dulwich (supports GitHub/GitLab API optimization)
3. **Tag-based version selection** with semantic versioning support
4. **Hybrid distribution model** combining Copier templates with dynamic content generation
5. **Separation of concerns** between data sources, content generation, and rendering

## Integration Proposal

### Option A: Native Git Source Handler (Recommended)

**Approach**: Leverage the existing `GitSourceHandler` to clone/fetch instruction repositories and extract specific subdirectories.

**Implementation Points**:

1. **Extend PopulateCommand** with an `--instructions` or `--update-instructions` flag
2. **Add instruction configuration** to Copier answers or a dedicated config section:
   ```toml
   [instructions]
   source = "github:emcd/python-project-common@docs-1#documentation/common"
   target = ".auxiliary/instructions"
   strip_header_lines = 20  # Optional preprocessing
   ```

3. **Create InstructionPopulator** class parallel to existing population logic:
   ```python
   # sources/agentsmgr/instructions.py
   class InstructionPopulator:
       def populate_instructions(
           self, source_spec, target, strip_lines=0, simulate=False
       ):
           # Use existing GitSourceHandler.resolve()
           # Copy files with optional header stripping
           # Return count of files processed
   ```

4. **Integration point** in `population.py` PopulateCommand.execute():
   ```python
   if self.update_instructions:  # or check config
       instructions_attempted, instructions_updated = (
           populate_instructions(location, configuration, simulate))
       _scribe.info(f"Updated {instructions_updated}/{instructions_attempted} instruction files")
   ```

**Advantages**:
- Reuses proven Git infrastructure with tag selection, API optimization, shallow clones
- Maintains version control via source@ref syntax: `github:emcd/python-project-common@docs-2`
- Consistent with existing agentsmgr architecture and patterns
- Supports multiple instruction sources (not limited to single hardcoded URL)
- Plugin-extensible for future non-Git sources

**Disadvantages**:
- Requires handling subdirectory extraction (already supported via `#fragment` syntax)
- Header stripping adds preprocessing complexity (though minimal)

### Option B: HTTP Download Handler

**Approach**: Create a new `HTTPSourceHandler` for direct file downloads via URL lists.

**Implementation Points**:

1. **Register new source handler**:
   ```python
   @source_handler(['http', 'https'])
   class HTTPSourceHandler:
       def resolve(self, source_spec, tag_prefix=...):
           # Download individual files
           # Return temp directory with downloaded content
   ```

2. **Configuration** specifies file list:
   ```toml
   [instructions]
   source = "https://raw.githubusercontent.com/.../docs-1/documentation/common"
   files = ["architecture.rst", "practices.rst", ...]
   strip_header_lines = 20
   ```

**Advantages**:
- More direct translation of current bash approach
- Potentially faster for small file lists (no full clone)

**Disadvantages**:
- **Doesn't leverage existing Git infrastructure** (defeats purpose of agentsmgr's design)
- Creates new code path for essentially the same problem Git sources solve
- Harder to version control (URLs don't naturally encode versions like git refs)
- Fragments the codebase philosophy (hybrid distribution relies on Git-based sources)

### Option C: Copier Template Distribution

**Approach**: Distribute instructions via the minimal Copier template rather than agentsmgr.

**Rationale**: Based on PRD, instructions are static documentation that fits the "base configuration template" model rather than "dynamic content generation."

**Advantages**:
- Aligns with hybrid architecture: templates for static, agentsmgr for dynamic
- Instructions rarely change compared to slash commands/agents
- Copier already handles version-controlled file distribution

**Disadvantages**:
- **Not suitable for this use case** - instructions reference external shared documentation that updates independently
- Breaks separation of project-specific templates from shared documentation sources

## Recommendation

**Implement Option A (Native Git Source Handler)** with these specific design decisions:

### 1. Configuration Schema

Configuration is managed through `copier.yaml` with three related fields:

```yaml
provide_instructions:
    type: bool
    help: Download documentation instructions for AI agents
    default: true

instructions_target:
    type: str
    help: Target directory for instruction files
    default: ".auxiliary/instructions"
    when: "{{ provide_instructions }}"

instructions_sources:
    type: yaml
    help: Git sources for documentation instructions
    default:
      - source: "github:emcd/python-project-common@docs-1#documentation/common"
        files:
          "*.rst": {strip_header_lines: 20}
    when: "{{ provide_instructions }}"
```

This generates a `.copier-answers.yaml` with structure:

```yaml
provide_instructions: true
instructions_target: ".auxiliary/instructions"
instructions_sources:
  - source: "github:emcd/python-project-common@docs-1#documentation/common"
    files:
      "*.rst": {strip_header_lines: 20}
  # Optional: additional sources
  # - source: "github:myorg/my-docs@latest#guides"
  #   files:
  #     "*.md": {strip_header_lines: 5}
```

**Design rationale**:
- `provide_instructions` boolean controls feature activation (no CLI flag needed)
- `instructions_target` is global since target is same regardless of source
- `instructions_sources` supports multiple sources with per-file preprocessing
- Conditional display (`when`) keeps UI clean when feature is disabled

### 2. Module Structure

Create `sources/agentsmgr/instructions.py` with:

```python
def populate_instructions(
    source_location: Path,
    configuration: Mapping,
    simulate: bool = False,
) -> tuple[int, int]:
    """Populates instruction files from configured source.

    Returns (files_attempted, files_written).
    """
```

### 3. Integration with PopulateCommand

No CLI flag needed - behavior driven by configuration. In `population.py` PopulateCommand.execute():

```python
# After main population, check configuration for instructions
if configuration.get('provide_instructions', False):
    instructions_sources = configuration.get('instructions_sources', [])
    instructions_target = configuration.get('instructions_target', '.auxiliary/instructions')
    if instructions_sources:
        instructions_attempted, instructions_updated = (
            populate_instructions(
                instructions_sources,
                self.target / instructions_target,
                self.simulate,
            ))
        _scribe.info(
            f"Updated {instructions_updated}/{instructions_attempted} "
            "instruction files")
```

Execute after main population, before final reporting.

### 4. Preprocessing Support

Handle header stripping generically:

```python
def preprocess_content(
    content: str,
    config: Mapping
) -> str:
    """Applies configured preprocessing transforms."""
    if strip_lines := config.get('strip_header_lines'):
        lines = content.splitlines()
        return '\n'.join(lines[strip_lines:])
    return content
```

### 5. File Filtering

Support glob patterns or explicit lists:

```python
files_config = config.get('files', ['*.rst'])  # Default to all .rst
# Use pathlib.Path.match() for filtering
```

## Architectural Considerations

### Consistency with Project Philosophy

The PRD emphasizes:
- **Tag-based releases for rapid iteration** → Git sources with refs solve this
- **Plugin architecture for extensibility** → Decorator-based handlers fit perfectly
- **Hybrid distribution** → Instructions are "configuration data" that agentsmgr distributes
- **Single source of truth** → Git repositories as versioned sources

### Tradeoffs Analysis

| Aspect | Option A (Git) | Option B (HTTP) | Current Bash |
|--------|---------------|-----------------|--------------|
| Version control | Excellent (git refs) | Poor (URL-based) | Poor (hardcoded URL) |
| Infrastructure reuse | High | Low | N/A |
| Complexity | Medium | Low | Very Low |
| Extensibility | High | Medium | None |
| Consistency | High (matches architecture) | Low | N/A |

### Migration Path

1. **Phase 1**: Implement `instructions.py` module with basic functionality
2. **Phase 2**: Add configuration detection (answers file or defaults)
3. **Phase 3**: Integrate into `PopulateCommand` with `--update-instructions` flag
4. **Phase 4**: Deprecate bash script (keep for backward compatibility)
5. **Phase 5**: Document in user guides and update Copier template

### Edge Cases to Address

1. **No instructions configured** → Skip silently (current behavior for optional features)
2. **Source unavailable** → Graceful degradation with warning (don't fail entire populate)
3. **Preprocessing errors** → Log warning, save unprocessed file
4. **File filtering produces no matches** → Warning with suggestion to check config

## Design Decisions

1. **Instruction updates are automatic** (always run with `populate`)
   - **Decision**: No CLI flag - behavior controlled by `provide_instructions` in `copier.yaml`
   - When `provide_instructions: true`, instructions are updated on every populate
   - Rationale: Declarative configuration ensures instructions stay synchronized with agent configurations

2. **Support multiple instruction sources**
   - **Decision**: Configuration accepts list of sources
   - Rationale: Enables combining project-specific and shared documentation

3. **Preprocessing per file/glob pattern**
   - **Decision**: Map globs and filenames to different boilerplate stripping amounts
   - Example configuration:
     ```yaml
     instructions_sources:
       - source: "github:emcd/python-project-common@docs-1#documentation/common"
         files:
           "*.rst": {strip_header_lines: 20}
           "specific-file.md": {strip_header_lines: 10}
     ```
   - Rationale: Flexible preprocessing without format-specific handler complexity

4. **Instructions are always per-project**
   - **Decision**: No per-user targeting mode for instructions
   - Rationale: Custom slash commands and subagents reference instructions relative to project root

## Conclusion

This design maintains architectural consistency, leverages existing infrastructure, and provides natural extensibility for future requirements. The Git-based approach aligns with agentsmgr's plugin architecture and the project's emphasis on version-controlled, tag-based distribution.
