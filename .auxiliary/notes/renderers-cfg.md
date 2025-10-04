# Coder Renderers and Configuration Architecture

## Problem Statement

Need to support multiple AI coding assistants with different requirements:

- **Claude Code**: Supports both per-project (`.auxiliary/configuration/claude/`) and per-user (`~/.config/claude/`) configuration
- **Codex CLI**: Only supports per-user configuration (`~/.codex/` or `$CODEX_HOME`)
- **OpenCode**: Supports both per-project and per-user modes
- **Gemini CLI**: (Future) likely per-user only

Additionally, different users have different preferences for config locations (XDG-compliant vs. defaults).

## Proposed Architecture

### Three-Layer Configuration Model

```
┌─────────────────────────────────────────────────────────┐
│ Layer 1: agentsmgr Configuration                        │
│ Purpose: How agentsmgr operates (user preferences)      │
│ Location: ~/.config/emcd-agents/general.toml            │
│ Scope: Per-user, persistent across all projects         │
│ Note: Provided by appcore configuration system          │
│                                                          │
│ Contents:                                                │
│   - Default targeting mode (per-user vs per-project)    │
│   - Coder-specific path overrides                       │
│   - Environment variable substitution                   │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│ Layer 2: Copier Answers                                 │
│ Purpose: What to generate for this project              │
│ Location: .auxiliary/configuration/copier-answers--.yaml│
│ Scope: Per-project, version controlled                  │
│                                                          │
│ Contents:                                                │
│   - Which coders to generate for                        │
│   - Which languages/features enabled                    │
│   - Project metadata                                     │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│ Layer 3: Coder Renderers                                │
│ Purpose: Coder-specific behavior and validation         │
│ Location: agentsmgr/renderers/*.py                      │
│ Scope: Code, shipped with agentsmgr                     │
│                                                          │
│ Responsibilities:                                        │
│   - Declare supported targeting modes                   │
│   - Resolve config paths (env vars, defaults)           │
│   - Validate targeting mode compatibility               │
│   - Format-specific output structure                    │
└─────────────────────────────────────────────────────────┘
```

### Layer 1: agentsmgr Configuration

**File**: `~/.config/emcd-agents/general.toml` (provided by appcore configuration system)

**Example**:
```toml
# Default targeting mode for all operations
# Can be overridden per-invocation via CLI flag
target-mode = "per-project"  # or: "per-user"

# Coder-specific configuration using table arrays
# Environment variables take precedence over these settings
[[coders]]
name = "codex"
home = "~/.codex"
target-mode = "per-user"  # Force per-user for codex

[[coders]]
name = "claude"
config-dir = "~/.config/claude"
target-mode = "default"  # Use global target-mode

[[coders]]
name = "gemini"
config-dir = "~/.gemini"

[[coders]]
name = "opencode"
config-dir = "~/.config/opencode"
target-mode = "per-project"
```

**Precedence Order** (highest to lowest):
1. Environment variables (e.g., `CODEX_HOME`, `CLAUDE_CONFIG_DIR`)
2. File configuration (`~/.config/emcd-agents/general.toml`)
3. Coder defaults

**Behavior**:
- If file doesn't exist, use sensible defaults
- CLI flag `--target-mode` overrides config (can specify per-coder)
- Environment variables override file configuration
- Invalid mode for coder raises helpful error

### Layer 2: Copier Answers (Unchanged)

**File**: `.auxiliary/configuration/copier-answers--agents.yaml`

**Example**:
```yaml
_commit: '8814646'
_src_path: .
coders:
- claude
- opencode
languages:
- python
project_name: agents-common
```

**No changes needed** - this layer only declares *what* to generate, not *where*.

### Layer 3: Coder Renderer Architecture

**New Module Structure**:
```
sources/agentsmgr/
├── renderers/
│   ├── __init__.py          # Renderer registry
│   ├── base.py              # Protocol/ABC definitions
│   ├── claude.py            # Claude Code renderer
│   ├── codex.py             # Codex CLI renderer
│   ├── opencode.py          # OpenCode renderer
│   └── gemini.py            # Gemini CLI renderer (future)
└── commands/
    └── generator.py         # Updated to use renderers
```

#### Renderer Protocol

```python
# sources/agentsmgr/renderers/base.py

from typing import Literal, Protocol
from pathlib import Path
from collections.abc import Mapping

TargetingMode = Literal['per-user', 'per-project']

class CoderRenderer(Protocol):
    ''' Protocol for coder-specific rendering and path resolution. '''

    @property
    def coder_name(self) -> str:
        ''' Canonical name of the coder (e.g., 'claude', 'codex'). '''
        ...

    @property
    def supported_targeting_modes(self) -> frozenset[TargetingMode]:
        ''' Set of targeting modes this coder supports. '''
        ...

    def validate_targeting_mode(self, mode: TargetingMode) -> None:
        ''' Raises UnsupportedTargetingMode if mode not supported. '''
        ...

    def resolve_output_base(
        self,
        targeting_mode: TargetingMode,
        project_target: Path,
        agentsmgr_config: Mapping[str, Any],
        env: Mapping[str, str],
    ) -> Path:
        ''' Resolves base output directory for this coder.

        Determines the appropriate output location based on targeting mode,
        respecting the precedence of environment variables over file configuration
        over coder defaults. For per-user mode, checks environment first, then
        configuration file overrides, then falls back to coder-specific defaults.
        For per-project mode, constructs path within project structure.
        '''
        ...

    def get_output_structure(self, item_type: str) -> str:
        ''' Returns subdirectory structure for item type.

        Translates generic item type (commands/agents) to coder-specific
        directory structure. Most coders use the same structure, but some
        may have different conventions.
        '''
        ...
```

#### Renderer Implementation Guidelines

Each coder renderer should implement the `CoderRenderer` protocol with these considerations:

**Codex Renderer** (`renderers/codex.py`):
- Only supports `per-user` targeting mode (validation must error on `per-project`)
- Path resolution precedence: `CODEX_HOME` env var > config file > `~/.codex` default
- Error message should reference Codex CLI version 0.44.0 limitation

**Claude Renderer** (`renderers/claude.py`):
- Supports both `per-user` and `per-project` modes
- For per-user: precedence is `CLAUDE_CONFIG_DIR` env var > config file > `~/.claude` default
- For per-project: use standard `.auxiliary/configuration/claude/` structure

**OpenCode Renderer** (`renderers/opencode.py`):
- Supports both targeting modes
- For per-user: precedence is `OPENCODE_CONFIG_DIR` env var > config file > `~/.config/opencode` default (XDG-compliant)
- For per-project: use standard `.auxiliary/configuration/opencode/` structure

**Path Resolution Pattern** (all renderers):
1. Check environment variable (if per-user mode)
2. Check configuration file override (if per-user mode)
3. Use coder-specific default or project structure (based on mode)

Note: Detailed implementations will follow project coding standards and practices.

#### Renderer Registry

The registry will use an accretive dictionary pattern where individual renderer modules
register themselves on import. This allows renderers to be added without modifying
central registry code.

**Registry Structure** (`sources/agentsmgr/renderers/__init__.py`):
```python
from accretive import Dictionary

# Accretive dictionary - can only add, never remove or modify
RENDERERS: Dictionary[str, CoderRenderer] = Dictionary()

def get_renderer(coder_name: str) -> CoderRenderer:
    ''' Retrieves renderer for specified coder. '''
    if coder_name not in RENDERERS:
        raise UnknownCoderError(coder_name)
    return RENDERERS[coder_name]
```

**Self-Registration Pattern** (each renderer module):
```python
# sources/agentsmgr/renderers/claude.py

from . import RENDERERS

class ClaudeRenderer:
    coder_name = 'claude'
    # ... implementation ...

# Register on module import
RENDERERS['claude'] = ClaudeRenderer()
```

This pattern ensures the registry grows naturally as new renderers are added.

### Integration with ContentGenerator

**Updated `generator.py`**:

```python
class ContentGenerator:

    location: Path
    configuration: CoderConfiguration
    agentsmgr_config: Mapping[str, Any]  # NEW
    targeting_mode: TargetingMode         # NEW
    jinja_environment: Environment

    def render_single_item(
        self, item_type: str, item_name: str, coder: str, target: Path
    ) -> RenderedItem:
        # ... existing metadata/template loading ...

        # NEW: Use renderer to resolve output location
        renderer = renderers.get_renderer(coder)
        renderer.validate_targeting_mode(self.targeting_mode)

        output_base = renderer.resolve_output_base(
            targeting_mode=self.targeting_mode,
            project_target=target,
            agentsmgr_config=self.agentsmgr_config,
            env=os.environ,
        )

        output_subdir = renderer.get_output_structure(item_type)

        extension = self._parse_template_extension(template_name)
        location = output_base / output_subdir / f"{item_name}.{extension}"

        return RenderedItem(content=content, location=location)
```

### CLI Changes

**New flag for `populate` command**:

```python
class PopulateCommand:
    source: str = '.'
    target: Path = field(default_factory=Path.cwd)
    simulate: bool = True

    # NEW: Targeting mode overrides (can specify multiple, one per coder)
    # Tyro will collect multiple uses into a sequence
    target_mode: Sequence[str] = ()  # Format: "coder:mode" or just "mode" for all
```

**Usage**:
```bash
# Use default from agentsmgr config
agentsmgr populate

# Override to per-user mode for all coders
agentsmgr populate --target-mode=per-user

# Per-coder targeting modes
agentsmgr populate --target-mode=codex:per-user --target-mode=claude:per-project

# Mixed specification (default + override)
agentsmgr populate --target-mode=per-project --target-mode=codex:per-user

# Simulation mode to preview
agentsmgr populate --target-mode=per-user --simulate
```

**Parsing logic**: Split `<coder>:<mode>` strings to build dictionary. If no colon, apply mode to all coders.

### Error Handling

**New Exception**:
```python
class UnsupportedTargetingMode(Omnierror):
    ''' Raised when coder doesn't support requested targeting mode. '''

    def __init__(self, coder: str, mode: str, reason: str = ''):
        self.coder = coder
        self.mode = mode
        self.reason = reason

    def render_as_markdown(self) -> tuple[str, ...]:
        lines = [
            f"# Error: Unsupported Targeting Mode",
            f"",
            f"The **{self.coder}** coder does not support **{self.mode}** targeting mode.",
        ]
        if self.reason:
            lines.extend(["", self.reason])
        lines.extend([
            "",
            "## Supported Modes",
            "",
            f"- {', '.join(RENDERERS[self.coder].supported_targeting_modes)}",
        ])
        return tuple(lines)
```

**Example Error Output**:
```
# Error: Unsupported Targeting Mode

The **codex** coder does not support **per-project** targeting mode.

Codex CLI does not support per-project configuration. Only per-user
configuration in ~/.codex or $CODEX_HOME is supported as of version 0.44.0.

## Supported Modes

- per-user
```

### Migration Path

1. **Phase 1: Refactor without behavior change**
   - Introduce renderer architecture
   - All renderers default to existing per-project behavior
   - No config changes, purely internal refactor

2. **Phase 2: Add configuration support**
   - Implement agentsmgr config loading
   - Add `--targeting-mode` CLI flag
   - Enable per-user mode for coders that support it

3. **Phase 3: Environment variable support**
   - Implement env var resolution in renderers
   - Document environment variable usage

4. **Phase 4: Advanced features**
   - Interactive mode selection
   - Validation warnings for mixed modes
   - Migration tools

## Open Questions

1. **Config file location**: Should agentsmgr config be:
   - `~/.config/agentsmgr/config.yaml` (XDG-compliant)
   - `~/.agentsmgr.yaml` (simple dotfile)
   - Support both with precedence?

2. **Mixed targeting**: If project answers specify `coders: [claude, codex]` and targeting mode is `per-project`, should we:
   - Error immediately (codex doesn't support it)
   - Skip codex with warning
   - Auto-switch codex to per-user mode

3. **Validation timing**: When should targeting mode validation occur:
   - At command start (fail fast)
   - Per-coder during generation (partial success)

4. **Default targeting mode**: What should the default be if no config exists:
   - `per-project` (current behavior, safer)
   - `per-user` (more useful for codex)
   - Require explicit configuration

5. **Per-coder targeting override**: Should agentsmgr config support:
   ```yaml
   coder_targeting:
     codex: per-user      # Always use per-user for codex
     claude: per-project  # Always use per-project for claude
   ```
   This would override the global `targeting_mode` on a per-coder basis.

## Benefits

- **Explicit coder capabilities**: Each renderer declares what it supports
- **Fail-fast validation**: Errors before generation starts
- **Environment-aware**: Respects user's XDG preferences
- **Extensible**: New coders are isolated implementations
- **Backward compatible**: Existing per-project workflow unchanged
- **Type-safe**: Protocol ensures all renderers implement required methods

## Testing Strategy

- Unit tests for each renderer (path resolution, validation)
- Integration tests with different config combinations
- Test environment variable expansion
- Test error messages and user experience
- Fixture-based tests using profiles in `tests/data/profiles/`
