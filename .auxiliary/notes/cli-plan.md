# agentsmgr CLI Architecture Plan

## Executive Summary

This document outlines the implementation plan for the `agentsmgr` CLI in Phase 3 of the template-based settings distribution project. The CLI will generate dynamic agent content from structured data sources, completing the hybrid Copier + agentsmgr approach.

## Phase Completion Status

**Phase 1: Base Template Structure** ✅ **COMPLETED**
- Template structure with proper `.gitignore` files for generated content
- Base settings templates for all coders (Claude, OpenCode, Gemini)
- Hook executables distributed via Copier template

**Phase 2: Source Data and Templates** ✅ **COMPLETED**
- Structured data directory with configurations, contents, and templates
- TOML configuration files for commands and agents
- Coder-specific content files organized properly
- Generic Jinja2 templates ready for rendering

**Phase 3: agentsmgr Command Implementation** ⚠️ **READY TO BEGIN**

## CLI Architecture Design

### Reference Implementation Analysis

**Primary Pattern**: Follow **../python-appcore/sources/appcore/introspection.py** structure rather than **../python-librovore/sources/librovore/cli.py**'s complex architecture because:
- **Simpler scope**: agentsmgr has fewer, more focused commands than librovore's multi-processor system
- **Better architectural fit**: appcore's command inheritance pattern suits agentsmgr's needs
- **Ecosystem consistency**: Both use appcore[cli] foundation with tyro
- **Maintainability**: Cleaner separation of concerns for a focused tool

**Key Patterns from References**:
- **../python-appcore/sources/appcore/introspection.py**: Simple command inheritance, tyro integration, clean auxdata handling
- **../python-librovore/sources/librovore/cli.py**: Robust data validation, graceful error handling, structured result rendering

### Proposed CLI Structure

```python
# agentsmgr/cli.py - Main CLI application
class Application(appcore.cli.Application):
    """Agent configuration management CLI."""

    command: Union[
        PopulateCommand,
        ValidateCommand,
        DetectConfigurationCommand,  # Optional: troubleshooting
    ]

# agentsmgr/commands.py - Command implementations
class PopulateCommand(appcore.cli.Command):
    """Generate dynamic agent content from data sources.

    Reads configuration from Copier answers and generates
    coder-specific commands and agents in target directory.
    """

    source: Annotated[str, tyro.conf.arg(
        help="Data source (local path or git URL)"
    )] = "."

    target: Annotated[Path, tyro.conf.arg(
        help="Target directory for content generation"
    )] = Path.cwd()

    simulate: Annotated[bool, tyro.conf.arg(
        help="Dry run mode - show what would be generated"
    )] = False

class ValidateCommand(appcore.cli.Command):
    """Validate template generation in temporary directory.

    Generates content using specified configuration variant
    and validates structure without modifying target project.
    """

    variant: Annotated[str, tyro.conf.arg(
        help="Configuration variant to test (default, maximum)"
    )] = "default"

    preserve: Annotated[bool, tyro.conf.arg(
        help="Keep temporary files for inspection"
    )] = False

class DetectConfigurationCommand(appcore.cli.Command):
    """Detect and display current Copier configuration.

    Useful for troubleshooting configuration issues.
    """
```

### Core Implementation Components

#### 1. Configuration Detection

```python
def _detect_configuration(self, target: Path) -> Dict[str, Any]:
    """Load configuration from Copier answers file.

    Args:
        target: Target directory to search for configuration

    Returns:
        Configuration dictionary with coders and languages

    Raises:
        ConfigurationError: If no valid configuration found
    """
    answers_file = target / ".auxiliary/configuration/copier-answers--agents.yaml"

    if not answers_file.exists():
        # Fail fast - require explicit Copier integration
        raise ConfigurationError(
            "No agents configuration found. "
            "Run 'copier copy gh:emcd/agents-common' first."
        )

    config = yaml.safe_load(answers_file.read_text())

    # Validate required fields
    if not config.get("coders") or not config.get("languages"):
        raise ConfigurationError(
            "Invalid configuration: missing coders or languages"
        )

    return config
```

#### 2. Data Source Management

**MVP Scope**: Local data directory support
**Release 1.0**: Git URL support

```python
class DataSource:
    """Manages access to agent configuration data."""

    def __init__(self, source_spec: str, cache_dir: Optional[Path] = None):
        self.source_spec = source_spec
        self.cache_dir = cache_dir or Path(tempfile.gettempdir())

    def fetch_data(self) -> Path:
        """Fetch data source and return local path."""
        if self._is_local_path():
            return Path(self.source_spec).resolve()
        elif self._is_git_url():
            return self._clone_git_repo()
        else:
            raise ValueError(f"Unsupported source format: {self.source_spec}")

    def _is_local_path(self) -> bool:
        """Check if source is local filesystem path."""
        return not self.source_spec.startswith(('http', 'git@', 'gh:'))

    def _clone_git_repo(self) -> Path:
        """Clone Git repository to temporary directory."""
        # Implementation using GitPython
        # tempfile.TemporaryDirectory for command lifetime
        pass
```

#### 3. Template Rendering Pipeline

```python
class ContentGenerator:
    """Generates coder-specific content from data sources."""

    def __init__(self, data_path: Path, config: Dict[str, Any]):
        self.data_path = data_path
        self.config = config
        self.jinja_env = self._setup_jinja_environment()

    def generate_all_content(self, target: Path, simulate: bool = False) -> None:
        """Generate content for all configured coders."""
        for coder in self.config["coders"]:
            try:
                self._generate_coder_content(coder, target, simulate)
            except Exception as exc:
                # Continue past individual failures with logging
                logger.error(f"Failed to generate {coder} content: {exc}")

    def _generate_coder_content(self, coder: str, target: Path, simulate: bool) -> None:
        """Generate commands and agents for specific coder."""
        # Variable normalization: hyphen→underscore for Jinja2
        coder_config = self._normalize_coder_config(coder)

        # Generate commands
        self._render_commands(coder, coder_config, target, simulate)

        # Generate agents
        self._render_agents(coder, coder_config, target, simulate)

    def _get_content_with_fallback(self, item_type: str, item_name: str, coder: str) -> str:
        """Get content with Claude↔OpenCode fallback logic."""
        primary_path = self.data_path / f"contents/{item_type}/{coder}/{item_name}.md"

        if primary_path.exists():
            return primary_path.read_text()

        # Fallback logic (Claude ↔ OpenCode only)
        fallback_coder = {"claude": "opencode", "opencode": "claude"}.get(coder)
        if fallback_coder:
            fallback_path = self.data_path / f"contents/{item_type}/{fallback_coder}/{item_name}.md"
            if fallback_path.exists():
                logger.debug(f"Using {fallback_coder} content for {coder} {item_type} {item_name}")
                return fallback_path.read_text()

        raise ContentNotFoundError(f"No content found for {coder} {item_type} {item_name}")
```

#### 4. Template Selection and Output Handling

```python
def _get_available_templates(self, item_type: str) -> List[str]:
    """Get available templates for item type."""
    template_dir = self.data_path / "templates"
    pattern = f"{item_type}.*.jinja"
    return [p.name for p in template_dir.glob(pattern)]

def _select_template_for_coder(self, item_type: str, coder: str) -> str:
    """Select appropriate template based on coder capabilities."""
    available = self._get_available_templates(item_type)

    # Template preference by coder
    preferences = {
        "claude": [f"{item_type}.md.jinja"],      # Markdown with frontmatter
        "opencode": [f"{item_type}.md.jinja"],    # Markdown with YAML frontmatter
        "gemini": [f"{item_type}.toml.jinja"],    # TOML configuration
    }

    # Try preferred templates first
    for preferred in preferences.get(coder, []):
        if preferred in available:
            return preferred

    # No fallbacks - fail fast if we can't find the right template
    if coder not in preferences:
        raise UnsupportedCoderError(f"No template preferences defined for coder: {coder}")

    expected = preferences[coder]
    raise TemplateNotFoundError(
        f"Required template(s) for {coder} not found. "
        f"Expected: {expected}, Available: {available}"
    )

def _determine_output_extension(self, template_name: str) -> str:
    """Extract output extension from template name."""
    # Extract format from template name: "command.md.jinja" -> "md"
    parts = template_name.split('.')
    if len(parts) >= 3 and parts[-1] == 'jinja':
        return parts[-2]

    raise InvalidTemplateNameError(
        f"Template name '{template_name}' does not follow expected pattern: "
        f"'<type>.<format>.jinja' (e.g., 'command.md.jinja')"
    )
```

## Implementation Roadmap

### Implementation Order (Revised)

**Phase 3.1: Configuration Detection (Immediate)**
1. `DetectCommand` - Display current Copier configuration
   - Establishes basic CLI framework with appcore integration
   - Tests configuration detection logic in isolation
   - Provides debugging utility for troubleshooting
   - Foundation for all other commands

**Phase 3.2: Template Pipeline Foundation**
2. `PopulateCommand` (simulation mode only) - Test template discovery and rendering
   - Template discovery and selection logic
   - Content generation pipeline without actual file writing
   - Error handling for missing templates/content

**Phase 3.3: Full Population Implementation**
3. `PopulateCommand` (complete) - Full content generation
   - Local data source support (`source="."`)
   - Claude coder support (most complex due to semantic tool mappings)
   - Actual file writing with proper error handling

**Phase 3.4: Output Formatting Enhancement**
4. Result objects with Markdown rendering - Professional output formatting
   - Implement `ResultBase` protocol and result objects for structured output
   - Add `intercept_errors` decorator for consistent error handling
   - Enhance exception classes with `render_as_markdown()` methods
   - **Reference**: See `.auxiliary/notes/cli-rendering.md` for complete strategy

**Phase 3.5: Validation Infrastructure**
5. `ValidateCommand` - Template testing in temporary directories
   - Configuration variant testing
   - Temporary directory generation for safe testing

### MVP Implementation (Immediate - Phase 3.1)

**Core Features**:
1. `DetectCommand` with basic configuration display
2. CLI framework establishment with appcore/tyro integration
3. Configuration file discovery and parsing
4. Basic error handling for missing/invalid configuration

**Key Files to Implement (Phase 3.1)**:
- `agentsmgr/cli.py` - Main application structure with DetectCommand
- `agentsmgr/commands.py` - DetectCommand implementation
- `agentsmgr/exceptions.py` - Custom exception classes for configuration errors

**Phase 3.1 Command Interface**:
```bash
# Display current Copier configuration for agents
agentsmgr detect

# Detect configuration in specific directory
agentsmgr detect --target=/path/to/project
```

**Future Phases Command Interface**:
```bash
# Generate content from local data directory (Phase 3.2+)
agentsmgr populate

# Dry run to see what would be generated (Phase 3.2)
agentsmgr populate --simulate

# Generate in specific directory (Phase 3.3)
agentsmgr populate --target=/path/to/project
```

### Release 1.0 Features

**Enhanced Capabilities**:
1. Git URL support for data sources (`gh:owner/repo@tag`, HTTPS, SSH)
2. OpenCode and Gemini coder support
3. `ValidateCommand` for template testing
4. Comprehensive error handling and user feedback

**Extended Command Interface**:
```bash
# Use remote data source
agentsmgr populate --source=gh:emcd/agents-common@agents-3

# Validate configuration variant
agentsmgr validate --variant=maximum --preserve

# Troubleshoot configuration
agentsmgr detect-configuration
```

### Future Enhancements

**Advanced Features**:
1. Configuration schema validation with detailed error messages
2. Advanced template debugging capabilities
3. Content preview and diff modes
4. Integration with Copier hooks for automatic updates

## Error Handling Strategy

**Configuration Errors**:
- Missing Copier answers file → Clear instructions to run Copier first
- Invalid configuration → Specific validation errors with suggestions

**Content Errors**:
- Missing content files → Continue with other items, log detailed warnings
- Template rendering failures → Skip item with error details, don't abort

**Data Source Errors**:
- Invalid Git URLs → Clear error messages with format examples
- Network failures → Retry logic with fallback to cached versions

## Integration Points

**Copier Integration**:
- Read configuration from `copier-answers--agents.yaml`
- Respect target directory structure from Copier template
- Work with existing `.gitignore` patterns for generated content

**Ecosystem Consistency**:
- Use appcore's exception system for error handling
- Follow tyro argument parsing patterns from ecosystem
- Maintain consistency with python-project-common validation patterns

## Testing Strategy

**Template Validation**:
- Follow python-project-common's `ValidateCommand` pattern
- Test matrix with configuration variants (default, maximum)
- Temporary directory generation for safe testing

**Content Generation Testing**:
- Unit tests for individual template rendering
- Integration tests for complete generation pipeline
- Regression tests for content fallback logic

This architecture provides a solid foundation for Phase 3 implementation while maintaining ecosystem consistency and enabling future enhancements.