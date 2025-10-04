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
│ Location: ~/.config/agentsmgr/config.yaml               │
│ Scope: Per-user, persistent across all projects         │
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

**File**: `~/.config/agentsmgr/config.yaml` (or `$XDG_CONFIG_HOME/agentsmgr/config.yaml`)

**Example**:
```yaml
# Default targeting mode for all operations
# Can be overridden per-invocation via CLI flag
targeting_mode: per-project  # or: per-user

# Coder-specific path overrides
# Supports environment variable substitution
coder_overrides:
  codex:
    home: ${CODEX_HOME:-~/.codex}

  claude:
    config_dir: ${CLAUDE_CONFIG_DIR:-~/.config/claude}

  gemini:
    config_dir: ${GEMINI_CONFIG_DIR:-~/.gemini}

  opencode:
    config_dir: ~/.config/opencode

# Optional: Global vs project preferences per coder
coder_targeting:
  codex: per-user      # Force per-user for codex
  claude: inherit      # Use default targeting_mode
  opencode: per-project
```

**Behavior**:
- If file doesn't exist, use sensible defaults
- CLI flag `--targeting-mode` overrides config
- Environment variables expanded at runtime
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

        Args:
            targeting_mode: 'per-user' or 'per-project'
            project_target: Project root path (for per-project mode)
            agentsmgr_config: User's agentsmgr configuration
            env: Environment variables (os.environ)

        Returns:
            Base path where coder config should be written.
            Examples:
              - per-user: /home/user/.config/claude
              - per-project: /path/to/project/.auxiliary/configuration/claude
        '''
        ...

    def get_output_structure(self, item_type: str) -> str:
        ''' Returns subdirectory structure for item type.

        Args:
            item_type: 'commands' or 'agents'

        Returns:
            Subdirectory path relative to output_base.
            Examples:
              - Claude: 'commands' → 'commands/'
              - Codex: 'commands' → 'slash-commands/' (hypothetical)
        '''
        ...
```

#### Example Implementations

**Codex Renderer** (`renderers/codex.py`):
```python
class CodexRenderer:
    ''' Renderer for Codex CLI (per-user only). '''

    coder_name = 'codex'
    supported_targeting_modes = frozenset(['per-user'])

    def validate_targeting_mode(self, mode: TargetingMode) -> None:
        if mode != 'per-user':
            raise UnsupportedTargetingMode(
                coder='codex',
                mode=mode,
                reason='Codex CLI does not support per-project configuration. '
                       'Only per-user configuration in ~/.codex or $CODEX_HOME '
                       'is supported as of version 0.44.0.'
            )

    def resolve_output_base(
        self,
        targeting_mode: TargetingMode,
        project_target: Path,
        agentsmgr_config: Mapping[str, Any],
        env: Mapping[str, str],
    ) -> Path:
        self.validate_targeting_mode(targeting_mode)

        # Precedence: agentsmgr config > env > default

        # 1. Check agentsmgr config override
        override = (
            agentsmgr_config
            .get('coder_overrides', {})
            .get('codex', {})
            .get('home')
        )
        if override:
            return Path(override).expanduser()

        # 2. Check CODEX_HOME environment variable
        if codex_home := env.get('CODEX_HOME'):
            return Path(codex_home).expanduser()

        # 3. Default location
        return Path.home() / '.codex'

    def get_output_structure(self, item_type: str) -> str:
        # Codex uses same structure as our convention
        return item_type  # 'commands' → 'commands/', 'agents' → 'agents/'
```

**Claude Renderer** (`renderers/claude.py`):
```python
class ClaudeRenderer:
    ''' Renderer for Claude Code (supports both modes). '''

    coder_name = 'claude'
    supported_targeting_modes = frozenset(['per-user', 'per-project'])

    def validate_targeting_mode(self, mode: TargetingMode) -> None:
        # Claude supports both modes
        pass

    def resolve_output_base(
        self,
        targeting_mode: TargetingMode,
        project_target: Path,
        agentsmgr_config: Mapping[str, Any],
        env: Mapping[str, str],
    ) -> Path:
        if targeting_mode == 'per-project':
            # Project-local configuration
            return project_target / '.auxiliary' / 'configuration' / 'claude'

        # Per-user configuration
        # Precedence: agentsmgr config > env > default

        override = (
            agentsmgr_config
            .get('coder_overrides', {})
            .get('claude', {})
            .get('config_dir')
        )
        if override:
            return Path(override).expanduser()

        if config_dir := env.get('CLAUDE_CONFIG_DIR'):
            return Path(config_dir).expanduser()

        return Path.home() / '.claude'

    def get_output_structure(self, item_type: str) -> str:
        return item_type
```

**OpenCode Renderer** (`renderers/opencode.py`):
```python
class OpencodeRenderer:
    ''' Renderer for OpenCode (supports both modes). '''

    coder_name = 'opencode'
    supported_targeting_modes = frozenset(['per-user', 'per-project'])

    def validate_targeting_mode(self, mode: TargetingMode) -> None:
        pass

    def resolve_output_base(
        self,
        targeting_mode: TargetingMode,
        project_target: Path,
        agentsmgr_config: Mapping[str, Any],
        env: Mapping[str, str],
    ) -> Path:
        if targeting_mode == 'per-project':
            return project_target / '.auxiliary' / 'configuration' / 'opencode'

        override = (
            agentsmgr_config
            .get('coder_overrides', {})
            .get('opencode', {})
            .get('config_dir')
        )
        if override:
            return Path(override).expanduser()

        if config_dir := env.get('OPENCODE_CONFIG_DIR'):
            return Path(config_dir).expanduser()

        # Default to XDG-compliant location
        return Path.home() / '.config' / 'opencode'

    def get_output_structure(self, item_type: str) -> str:
        return item_type
```

#### Renderer Registry

```python
# sources/agentsmgr/renderers/__init__.py

from .base import CoderRenderer, TargetingMode
from .claude import ClaudeRenderer
from .codex import CodexRenderer
from .opencode import OpencodeRenderer

# Registry mapping coder names to renderer instances
RENDERERS: dict[str, CoderRenderer] = {
    'claude': ClaudeRenderer(),
    'codex': CodexRenderer(),
    'opencode': OpencodeRenderer(),
}

def get_renderer(coder_name: str) -> CoderRenderer:
    ''' Retrieves renderer for specified coder. '''
    if coder_name not in RENDERERS:
        raise UnknownCoderError(coder_name)
    return RENDERERS[coder_name]
```

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

    # NEW: Targeting mode override
    targeting_mode: Optional[TargetingMode] = None  # None = use config default
```

**Usage**:
```bash
# Use default from agentsmgr config
agentsmgr populate

# Override to per-user mode
agentsmgr populate --targeting-mode=per-user

# Override to per-project mode
agentsmgr populate --targeting-mode=per-project

# Simulation mode to preview
agentsmgr populate --targeting-mode=per-user --simulate
```

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
