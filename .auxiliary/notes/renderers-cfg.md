# Coder Renderers and Configuration Architecture

## Implementation Status

### ✅ Phases 1-3 Complete (commits dffc4b2, 0555ebd, ebaed49)

**Phase 1**: Renderer architecture with base class, registry, self-registration pattern, and three renderers (Claude, OpenCode, Codex).

**Phase 2**: Configuration support via appcore, `--mode` CLI flag, environment variable resolution, direct per-project paths (`.claude/`, `.opencode/`).

**Phase 3**: Globals population with `--update-globals` flag, JSON merge strategies for settings files, TypeGuard pattern for type safety.

### 🔲 Phase 4 Remaining Work

See **Remaining Work** section below for details on:
- Extended targeting mode enum (`default`, `nowhere`)
- Coder default modes
- Memory file symlinking documentation
- Interactive mode selection (optional)
- Migration tools (optional)

---

## Problem Statement

Need to support multiple AI coding assistants with different requirements:

- **Claude Code**: Supports both per-project (`.claude/`) and per-user (`~/.config/claude/`) configuration
- **Codex CLI**: Only supports per-user configuration (`~/.codex/` or `$CODEX_HOME`)
- **OpenCode**: Supports both per-project (`.opencode/`) and per-user (`~/.config/opencode/`) modes
- **Gemini CLI**: (Future) likely per-user only

Additionally, different users have different preferences for config locations (XDG-compliant vs. defaults).

## Architecture Overview

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
│   - Default targeting mode (default | per-user |        │
│     per-project | nowhere)                              │
│   - Coder-specific path overrides                       │
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
│   - Declare default targeting mode                      │
│   - Resolve config paths (env vars, defaults)           │
│   - Validate targeting mode compatibility               │
│   - Format-specific output structure                    │
└─────────────────────────────────────────────────────────┘
```

### Layer 1: agentsmgr Configuration

**File**: `~/.config/emcd-agents/general.toml` (provided by appcore configuration system)

**Note**: Only this location is supported - no simple dotfiles polluting user home directory.

**Example**:
```toml
# Default targeting mode for all operations
# Can be overridden per-invocation via CLI flag
# Options: "default" | "per-user" | "per-project" | "nowhere"
mode = "default"

# Coder-specific configuration using table arrays
# Environment variables take precedence over these settings
[[coders]]
name = "codex"
directory = "~/.codex"

[[coders]]
name = "claude"
directory = "~/.config/claude"

[[coders]]
name = "opencode"
directory = "~/.config/opencode"
```

**Precedence Order** (highest to lowest):
1. Environment variables (e.g., `CODEX_HOME`, `CLAUDE_CONFIG_DIR`, `OPENCODE_CONFIG`)
2. File configuration (`~/.config/emcd-agents/general.toml`)
3. Coder-specific defaults (declared in renderer)

**Behavior**:
- If file doesn't exist, use `mode = "default"` with coder-specific defaults
- CLI flag `--mode` overrides config file setting
- Environment variables override file configuration for path resolution
- Invalid explicit mode for coder raises helpful error

### Layer 2: Copier Answers

**File**: `.auxiliary/configuration/copier-answers--agents.yaml`

**Example**:
```yaml
_commit: '8814646'
_src_path: .
coders:
- claude
- opencode
- codex
languages:
- python
project_name: agents-common
```

This layer only declares *what* to generate, not *where*. With `mode = "default"`, Claude and OpenCode would use per-project (`.claude/`, `.opencode/`), while Codex would use per-user (`~/.codex/`) automatically.

### Layer 3: Coder Renderer Architecture

**Module Structure** (✅ implemented):
```
sources/agentsmgr/
├── renderers/
│   ├── __init__.py          # Renderer registry
│   ├── base.py              # Base class and type definitions
│   ├── claude.py            # Claude Code renderer
│   ├── codex.py             # Codex CLI renderer
│   ├── opencode.py          # OpenCode renderer
│   └── gemini.py            # Gemini CLI renderer (future)
└── commands/
    ├── generator.py         # Uses renderers for path resolution
    ├── population.py        # Main populate command
    └── globalization.py     # Globals population logic
```

#### Renderer Base Class (✅ implemented)

```python
# sources/agentsmgr/renderers/base.py

TargetingMode: TypeAlias = Literal['per-user', 'per-project']

class RendererBase(immut.Object):
    ''' Base class for coder-specific rendering and path resolution. '''

    name: str
    modes_available: frozenset[TargetingMode]

    def validate_mode(self, mode: TargetingMode) -> None:
        ''' Validates targeting mode is supported by this coder. '''
        if mode not in self.modes_available:
            raise TargetModeNoSupport(self.name, mode)

    def resolve_base_directory(
        self,
        mode: TargetingMode,
        target: Path,
        configuration: Mapping[str, Any],
        environment: Mapping[str, str],
    ) -> Path:
        ''' Resolves base output directory for this coder. '''
        raise NotImplementedError

    def produce_output_structure(self, item_type: str) -> str:
        ''' Produces subdirectory structure for item type. '''
        return item_type
```

#### Renderer Implementation Status

**✅ Codex Renderer** (`renderers/codex.py`):
- Supports only `per-user` targeting mode
- Path precedence: `CODEX_HOME` env var > config file `directory` > `~/.codex` default
- **Needs**: Default mode property (`mode_default = 'per-user'`)

**✅ Claude Renderer** (`renderers/claude.py`):
- Supports both `per-user` and `per-project` modes
- Per-user: `CLAUDE_CONFIG_DIR` env var > config `directory` > `~/.claude` default
- Per-project: `.claude/` in project root
- **Needs**: Default mode property (`mode_default = 'per-project'`)

**✅ OpenCode Renderer** (`renderers/opencode.py`):
- Supports both targeting modes
- Per-user: `OPENCODE_CONFIG` env var > config `directory` > `~/.config/opencode` default
- Per-project: `.opencode/` in project root
- **Needs**: Default mode property (`mode_default = 'per-project'`)

#### Renderer Registry (✅ implemented)

Uses accretive dictionary with self-registration pattern:

```python
# sources/agentsmgr/renderers/base.py
RENDERERS: Dictionary[str, RendererBase] = Dictionary()

# Each renderer self-registers on import
# sources/agentsmgr/renderers/claude.py
RENDERERS['claude'] = ClaudeRenderer(...)
```

### CLI Implementation (✅ completed)

**Current `populate` command** (`population.py`):

```python
class PopulateCommand:
    source: str = '.'
    target: Path = field(default_factory=Path.cwd)
    simulate: bool = True
    mode: TargetingMode = 'per-project'  # Currently: 'per-user' | 'per-project'
    update_globals: bool = False         # Orthogonal to mode
```

**Current semantics**:
- `--mode` controls where commands/agents are generated
- `--update-globals` controls whether per-user global files are updated (independent of mode)
- Globals always go to per-user locations (e.g., `~/.claude/statusline.py`)
- Default: `--mode=per-project` with globals disabled for safety

**🔲 Needs extension** to support new mode enum:
```python
mode: Literal['default', 'per-user', 'per-project', 'nowhere'] = 'default'
```

### Exception Handling (✅ implemented)

**Exceptions** (`exceptions.py`):
- `TargetModeNoSupport`: Raised when coder doesn't support requested explicit mode
- `GlobalsPopulationFailure`: Raised when global file population fails
- `CoderAbsence`: Raised when requesting unknown coder from registry

All exceptions include `render_as_markdown()` for user-friendly error messages.

### Data Source Organization (✅ implemented)

```
defaults/
├── configurations/
│   ├── commands/              # Command metadata
│   │   └── cs-conform-python.toml
│   └── agents/                # Agent metadata
│       └── python-conformer.toml
├── contents/
│   ├── commands/              # Command bodies
│   │   ├── claude/
│   │   ├── opencode/
│   │   └── codex/
│   └── agents/                # Agent bodies
│       ├── claude/
│       ├── opencode/
│       └── codex/
└── globals/                   # Per-user global files
    ├── claude/
    │   └── statusline.md
    ├── opencode/
    └── codex/
```

**✅ Global Files Implementation** (`globalization.py`):
- Populated when `--update-globals` flag is set (orthogonal to `--mode`)
- Placed in root of per-user coder config directory (e.g., `~/.claude/statusline.py`)
- Two file types:
  - **Direct copy**: Non-settings files (e.g., `statusline.py`) - just overwrite
  - **Merge**: Settings files (e.g., `settings.json`) - additive merge preserving user values
- Settings file detection: `claude/settings.json`, `opencode/{opencode.json,opencode.jsonc}`, `codex/config.json`
- Merge strategy: See `.auxiliary/notes/json-merge-strategies.md`

---

## Remaining Work

### 1. Extended Targeting Mode Enum

**🔲 Update TargetingMode type alias**:
```python
# sources/agentsmgr/renderers/base.py
TargetingMode: TypeAlias = Literal['default', 'per-user', 'per-project', 'nowhere']
```

**Semantics**:
- `'default'`: Use each coder's default mode (from renderer)
- `'per-user'`: Force all coders to per-user (error if unsupported)
- `'per-project'`: Force all coders to per-project (error if unsupported)
- `'nowhere'`: Skip content generation entirely (only globals if `--update-globals`)

**Validation behavior**:
- Explicit modes (`per-user`, `per-project`): Validate per-coder during generation (current behavior)
- `default` mode: No validation needed, each coder uses its own default
- `nowhere` mode: Skip validation and generation entirely

### 2. Coder Default Modes

**🔲 Add `mode_default` property to RendererBase**:
```python
class RendererBase(immut.Object):
    name: str
    modes_available: frozenset[TargetingMode]
    mode_default: Literal['per-user', 'per-project']  # NEW
```

**Required defaults**:
- Claude: `mode_default = 'per-project'`
- OpenCode: `mode_default = 'per-project'`
- Codex: `mode_default = 'per-user'`

**🔲 Update ContentGenerator** to resolve `'default'` mode:
```python
def render_single_item(...):
    renderer = RENDERERS[coder]

    # Resolve 'default' to actual mode
    actual_mode = (
        renderer.mode_default if self.mode == 'default'
        else self.mode
    )

    # Skip generation if mode is 'nowhere'
    if self.mode == 'nowhere':
        return None

    # Validate only explicit modes
    if actual_mode in ('per-user', 'per-project'):
        renderer.validate_mode(actual_mode)

    output_base = renderer.resolve_base_directory(
        mode=actual_mode, ...)
```

### 3. Documentation

**🔲 Document memory file symlinking strategy**:
- Memory file (`memory.md`) provides shared context across coders
- Should be symlinked from one coder's directory to others
- Example: `~/.claude/memory.md` ← actual file, `~/.opencode/memory.md` ← symlink
- Document recommended approach in user documentation or architecture docs

### 4. Optional Enhancements (Phase 4)

**Interactive mode selection**:
- Prompt user to choose mode if not specified in config
- Show which coders support which modes
- Low priority - CLI flags are sufficient

**Migration tools**:
- Help users transition from old `.auxiliary/configuration/claude/` to `.claude/`
- Automated detection and migration prompts
- Low priority - breaking change already happened in Phase 2

---

## Design Decisions (Resolved)

All design questions have been answered:

1. **Config file location**: Only `~/.config/emcd-agents/general.toml` via appcore (no dotfiles)

2. **Mixed targeting behavior**: Use 4-mode enum with `'default'` allowing each coder to use its preferred mode

3. **Validation timing**: Per-coder during generation for explicit modes; no validation for `'default'` mode

4. **Default targeting mode**: `'default'` (delegates to each coder's default)

5. **Per-coder targeting**: Handled by coder's `mode_default` property, not config file

---

## Benefits

- **Explicit coder capabilities**: Each renderer declares what it supports and its default
- **Flexible targeting**: `'default'` mode allows mixed per-user/per-project in single project
- **Environment-aware**: Respects environment variables and user configuration
- **Extensible**: New coders register themselves with their own defaults
- **Type-safe**: Immutable base classes and type aliases ensure correctness
- **Fail-safe**: `'nowhere'` mode allows globals-only updates
