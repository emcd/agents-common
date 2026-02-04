# multi-tool-support Design

## Overview

This design implements extensible content generation for multiple AI development tools through a plugin-based renderer architecture. The system enables adding new AI tools (coders) without restructuring existing data sources by separating tool-agnostic data from tool-specific rendering logic.

## Architecture

### Component Organization

See `documentation/architecture/filesystem.rst` for the complete filesystem layout. Key modules for multi-tool support:

- `sources/agentsmgr/renderers/base.py`: RendererBase abstract class, type definitions
- `sources/agentsmgr/renderers/{claude,codex,opencode}.py`: Coder-specific renderer implementations
- `sources/agentsmgr/renderers/__init__.py`: Re-exports and imports for renderer registration
- `sources/agentsmgr/generator.py`: ContentGenerator with template rendering and fallback logic
- `sources/agentsmgr/sources/base.py`: Plugin registration system for source handlers
- `sources/agentsmgr/population.py`: Orchestrates content generation across multiple coders

### Core Abstractions

#### RendererBase Protocol

Abstract base class defining the interface all coder renderers must implement:

```python
class RendererBase(immut.Object):
    # Required class attributes
    name: str                                    # Coder identifier (e.g., 'claude')
    modes_available: frozenset[ExplicitTargetMode]  # Supported targeting modes
    mode_default: ExplicitTargetMode             # Default targeting mode
    memory_filename: str                         # Memory file name (e.g., 'CLAUDE.md')

    # Required methods
    def resolve_base_directory(
        self, mode: ExplicitTargetMode, target: Path,
        configuration: Mapping[str, Any], environment: Mapping[str, str]
    ) -> Path:
        """Resolves base output directory for this coder."""
        raise NotImplementedError

    # Optional overrides
    def calculate_directory_location(self, item_type: str) -> str:
        """Returns directory name for item type (default: item_type)."""
        return item_type

    def get_template_flavor(self, item_type: str) -> str:
        """Determines template format to use (default: 'claude')."""
        return 'claude'

    def provide_project_symlinks(self, target: Path) -> Sequence[tuple[Path, Path]]:
        """Provides (source, link_path) symlink tuples for per-project mode."""
        # Default: .auxiliary/configuration/coders/{name} -> .{name}
```

#### Plugin Registration Pattern

Renderers self-register by importing and adding themselves to the global `RENDERERS` registry defined in `renderers/base.py`. Each renderer module:

1. Imports `RENDERERS` and `RendererBase` as private names (following VBL201)
2. Defines its renderer class inheriting from `RendererBase`
3. Registers an instance in the `RENDERERS` dictionary
4. Gets imported by `renderers/__init__.py` to trigger registration

**Design rationale**: Self-registration pattern enables automatic discovery without maintaining central registry code. New renderers are added by creating the module and importing it in `__init__.py`.

### Path Resolution Hierarchy

Each renderer implements a three-tier precedence system for resolving output directories:

1. **Environment variables** (highest precedence)
   - Claude: `CLAUDE_CONFIG_DIR`
   - Codex: `CODEX_HOME`
   - OpenCode: `OPENCODE_CONFIG`

2. **Configuration file overrides** (middle precedence)
   - Read from `coders` array in application configuration
   - Each coder entry may specify `directory` (or `home` for Codex)

3. **Coder defaults** (fallback)
   - Claude: `~/.claude`
   - Codex: `~/.codex`
   - OpenCode: `~/.config/opencode`

**Per-project mode** bypasses precedence and uses standardized paths:
- `.auxiliary/configuration/coders/{coder_name}/`

### Template Flavor System

The template flavor system enables content format sharing across compatible coders:

```python
def get_template_flavor(self, item_type: str) -> str:
    """Returns pioneering coder name whose template format to use."""
```

**Flavor mappings**:
- `'claude'`: Markdown format pioneered by Claude Code (used by Claude, Codex, OpenCode commands)
- `'opencode'`: OpenCode-specific agent format (used by OpenCode agents only)
- `'gemini'`: TOML format pioneered by Gemini (future use)

ContentGenerator uses the flavor system when resolving template paths, looking up the renderer's preferred flavor and constructing the template path accordingly. This enables Claude and OpenCode to share command templates while using different agent formats.

### Content Fallback Mechanism

ContentGenerator implements intelligent fallback for coder-specific content bodies. Configuration specifies fallback mappings (e.g., Claude ↔ OpenCode bidirectional fallback, Gemini isolated).

**Resolution logic**:
1. Try `contents/{coder}/{item_type}/{item_name}.md`
2. If missing and fallback configured, try `contents/{fallback_coder}/{item_type}/{item_name}.md`
3. If still missing, raise ContentAbsence exception

**Design rationale**: Reduces duplication for coders with compatible markdown formats (Claude ↔ OpenCode) while maintaining isolation for incompatible formats (Gemini).

### Targeting Mode Support

Each renderer declares supported targeting modes via its `modes_available`
attribute (e.g., Claude, OpenCode, and Codex support both per-user and
per-project).

The population module filters coders by matching their `mode_default` against the requested target mode. This ensures `populate project` only processes per-project coders and `populate user` only processes per-user coders, respecting each tool's design constraints.

### Symlink Management

Renderers provide coder-specific symlinks for per-project mode via the `provide_project_symlinks` method. The base implementation creates a symlink from `.auxiliary/configuration/coders/{name}` to `.{name}` at the project root.

**Additional symlinks** (coder-specific overrides):
- **Claude**: `.mcp.json` → `.auxiliary/configuration/mcp-servers.json`
- **OpenCode**: `opencode.jsonc` → `.auxiliary/configuration/coders/opencode/settings.jsonc`
- **Codex**: None (uses the base `.{name}` symlink behavior)

## Module Contracts

### RendererBase

**Responsibilities**:
- Define interface for coder-specific path resolution and configuration
- Provide default implementations for common behavior
- Validate targeting mode support

**Collaborators**:
- `ContentGenerator`: Uses renderers to determine output locations and template flavors
- `population.py`: Uses renderers for symlink creation and mode filtering

**Invariants**:
- `mode_default` must be in `modes_available`
- `name` must be unique across all registered renderers
- `resolve_base_directory` must return absolute paths

### ContentGenerator

**Responsibilities**:
- Orchestrate template rendering with metadata and content bodies
- Implement content fallback logic for compatible coders
- Manage Jinja2 template environment

**Collaborators**:
- `RENDERERS`: Looks up renderer instances by coder name
- Source handlers: Resolves data source locations
- Template system: Loads and renders Jinja2 templates

**Invariants**:
- Template paths follow pattern: `templates/{flavor}/{item_type}/{item_name}.j2`
- Content bodies follow pattern: `contents/{coder}/{item_type}/{item_name}.md`
- Metadata follows pattern: `configurations/{item_type}/{item_name}.toml`

### RENDERERS Registry

**Responsibilities**:
- Provide global singleton registry of all available renderers
- Enable lookup by coder name

**Collaborators**:
- Renderer modules: Self-register on import
- `ContentGenerator`: Retrieves renderers for content generation
- CLI commands: Validates coder names, iterates available coders

**Invariants**:
- Registry is accretive (write-once, append-only)
- Keys match renderer.name values
- All values are RendererBase instances

## Implementation Patterns

### Adding a New Coder

To add support for a new AI tool:

1. **Create renderer module** `sources/agentsmgr/renderers/{coder}.py` implementing the `RendererBase` interface with:
   - Class attributes: `name`, `modes_available`, `mode_default`, `memory_filename`
   - Required method: `resolve_base_directory`
   - Optional overrides: `get_template_flavor`, `calculate_directory_location`, `provide_project_symlinks`
   - Self-registration in the `RENDERERS` dictionary

2. **Import the new module** in `renderers/__init__.py` to trigger registration

3. **Add content directory** `defaults/contents/{coder}/` with coder-specific content bodies

4. **Add or reuse templates** in `defaults/templates/{flavor}/` as appropriate

5. **Configure fallback** (optional) in application configuration if compatible with existing coder formats

**No changes required** to existing data sources (configurations/, other contents/ directories).

### Coder-Specific Directory Naming

Some coders use non-standard directory names (e.g., OpenCode uses singular forms like `agent/` instead of `agents/`). Override `calculate_directory_location` to provide a mapping from generic item types to coder-specific directory names.

### Environment-Specific Configuration

Path resolution for per-user installations follows the three-tier precedence hierarchy documented earlier: environment variables take precedence over configuration file overrides, which take precedence over coder defaults. Each coder implements this logic in its `resolve_base_directory` method.

## Extension Points

### Source Handler Plugin System

A similar plugin architecture exists for data source handlers in `sources/base.py`. Source handlers register themselves for specific URL schemes (e.g., `git:`, `github:`, `gitlab:`) and implement the `AbstractSourceHandler` protocol to resolve source specifications to local filesystem paths.

This enables extensibility for new source types (S3, HTTP archives, etc.) without modifying core logic.

### Template Engine Abstraction

While currently Jinja2-specific, the template flavor system provides an abstraction layer that could support alternative template engines per flavor if needed.

## Testing Considerations

### Renderer Testing

Each renderer should verify:
- Mode validation (raises TargetModeNoSupport for unsupported modes)
- Path resolution precedence (environment > config > default)
- Symlink generation (correct source/link pairs)
- Template flavor selection (returns expected flavor for each item type)

### Integration Testing

End-to-end tests should verify:
- Content generation with fallback (missing content falls back correctly)
- Multi-coder population (each coder gets appropriate content)
- Mode filtering (per-project vs per-user coder segregation)
- Template flavor resolution (correct templates loaded for each coder)

### Mock Strategy

Tests should mock:
- `RENDERERS` registry for isolated renderer testing
- File system operations for symlink and path resolution testing
- Environment variables for precedence testing

## Performance Characteristics

- **Renderer lookup**: O(1) dictionary access in RENDERERS registry
- **Content fallback**: O(1) or O(2) filesystem checks (primary + fallback)
- **Template loading**: Cached by Jinja2 environment, O(1) after first load
- **Mode filtering**: O(n) where n = number of configured coders (typically < 5)

**Scaling considerations**: Plugin architecture keeps memory overhead low—renderers are lightweight objects with no state beyond configuration. Registry size grows linearly with number of supported coders.

## Trade-offs and Alternatives

### Plugin Registration vs Explicit Registry

**Chosen approach**: Self-registration via module imports
- ✅ Automatic discovery of new renderers
- ✅ No central registry maintenance
- ❌ Import side effects (registration happens at import time)
- ❌ No lazy loading (all renderers loaded even if unused)

**Alternative**: Explicit registry with manual registration
- ❌ Requires updating central list when adding renderers
- ✅ More explicit, easier to trace
- ✅ Could support lazy loading

**Decision rationale**: Simplicity of adding new coders outweighs concerns about import side effects. All renderers are lightweight and lazy loading provides minimal benefit.

### Template Flavor vs Per-Coder Templates

**Chosen approach**: Template flavor system with sharing
- ✅ Reduces duplication for compatible formats
- ✅ Makes format compatibility explicit
- ❌ Additional indirection in template resolution
- ❌ Requires coordination on flavor naming

**Alternative**: Per-coder template directories
- ❌ Massive duplication (Claude/Codex/OpenCode use identical command format)
- ✅ Simpler lookup (direct mapping coder → templates)
- ❌ No explicit representation of format compatibility

**Decision rationale**: Duplication reduction and explicit compatibility modeling justify the indirection cost.

### Content Fallback vs Duplication

**Chosen approach**: Configurable fallback mappings
- ✅ Single source for compatible coders
- ✅ Maintainability (one content file for Claude/OpenCode)
- ❌ Configuration complexity (fallback mappings)
- ❌ Debugging complexity (which content was actually used?)

**Alternative**: Duplicate content for each coder
- ❌ Duplication burden (2x content for Claude/OpenCode)
- ❌ Synchronization issues (content divergence)
- ✅ Explicit, simple lookup
- ✅ Easy debugging

**Decision rationale**: Maintenance burden of duplication outweighs configuration complexity. Claude and OpenCode share markdown format, so fallback is semantically correct.

## Future Considerations

### Dynamic Renderer Discovery

Future enhancement: Load renderers from entry points or plugin directories for third-party renderer packages.

### Renderer Composition

Consider supporting renderer mixins or composition for shared behavior across renderer families (e.g., per-user-only renderers, cloud-based renderers).

### Template Format Versioning

As AI tools evolve their formats, consider versioning within template flavors (e.g., `claude-v1`, `claude-v2`) to maintain compatibility across tool versions.

### Configuration Schema Validation

Add formal schema validation for renderer configuration to catch errors early and provide better diagnostics.
