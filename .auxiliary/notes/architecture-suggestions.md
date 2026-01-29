# Architecture Suggestions for agents-common

## Date: 2026-01-28
## Context: Adding Kimi CLI Support

This document captures observations and suggestions for improving the `agents-common`
project structure, gathered while implementing Kimi CLI support.

---

## 1. Settings File Abstraction

**Current State:**
The `userdata.py` settings merge logic handles JSON and TOML with separate code paths
and conditional logic (`if source.suffix == '.toml':`).

**Suggestion:**
Introduce a `SettingsSerializer` protocol to make the merge logic format-agnostic:

```python
class SettingsSerializer(Protocol):
    def load(self, content: str) -> dict: ...
    def dump(self, data: dict) -> str: ...
    def backup_suffix(self) -> str: ...
```

**Benefits:**
- Easier to add new formats (YAML, etc.) without modifying merge logic
- Cleaner separation of serialization from merge semantics
- Each coder can specify its preferred serializer

---

## 2. Coder Capability Declaration

**Current State:**
Filtering coders by mode checks `renderer.mode_default == target_mode`. This conflates
"what the coder supports" with "what the coder defaults to".

**Suggestion:**
Renderers could declare capabilities explicitly:

```python
class Capability(enum.Flag):
    PER_USER_CONFIG = auto()
    PER_PROJECT_CONFIG = auto()
    COMMANDS = auto()      # Slash commands (Claude-style)
    AGENTS = auto()        # Agent definitions
    SKILLS = auto()        # Skill definitions (Kimi-style)
    MCP = auto()           # MCP server config

class RendererBase:
    capabilities: frozenset[Capability]
```

**Benefits:**
- More semantic filtering in population.py
- Clearer intent than checking mode_default
- Extensible for future capabilities

---

## 3. Memory File Standardization

**Current State:**
The `memory_filename` attribute assumes a simple filename. However:
- Claude uses `CLAUDE.md` (dedicated file)
- Kimi uses `AGENTS.md` (via `${KIMI_AGENTS_MD}` template variable)
- Some coders may not have dedicated memory files

**Suggestion:**
Consider a `MemoryFile` dataclass:

```python
@dataclass
class MemoryFile:
    filename: str                    # e.g., "CLAUDE.md" or "AGENTS.md"
    shared: bool                     # True if shared (AGENTS.md), False if dedicated
    template_variable: str | None    # e.g., "${KIMI_AGENTS_MD}"
    required: bool                   # Whether coder requires this file
```

**Benefits:**
- Captures the distinction between dedicated and shared memory files
- Documents template variable integration
- Clearer than string filename alone

---

## 4. Skills vs Commands vs Agents

**Current State:**
The project has concepts of "commands" and "agents" modeled after Claude Code.
However, different coders have different extension mechanisms:

- **Claude Code:** Slash commands (markdown) + AGENTS.md
- **Kimi CLI:** Skills (SKILL.md with YAML frontmatter) + Flow skills + AGENTS.md reference
- **OpenCode:** Commands + Prompts
- **Gemini:** Similar to Claude

**Important Note:** Most coders (Claude Code, Opencode, etc.) now support skills.
The project has not yet recognized or leveraged this convergence.

**Suggestion:**
Consider a unified "Capabilities" or "Extensions" abstraction that maps to
coder-specific implementations:

```python
class ExtensionType(enum.Enum):
    SKILL = auto()      # Maps to SKILL.md for Kimi, /skill for Claude, etc.
    COMMAND = auto()    # Slash commands
    AGENT = auto()      # Agent definitions
    FLOW = auto()       # Workflow definitions (Kimi flow skills)
```

**Benefits:**
- Acknowledges the skills convergence across coders
- Allows unified authoring with coder-specific rendering
- Reduces confusion about which concept applies to which coder

---

## 5. MCP Configuration as Cross-Coder Concept

**Current State:**
MCP configuration is currently embedded in coder-specific formats:
- Claude: `.mcp.json` file
- Kimi: `[mcp.servers]` section in `config.toml`
- Others: Various formats

**Suggestion:**
Treat MCP servers as a first-class, cross-coder concept with format-specific
renderers, similar to how commands work:

```python
# Shared definition
mcp_servers = {
    "pyright": {...},
    "context7": {...},
}

# Rendered to:
# - Claude: JSON in .mcp.json
# - Kimi: TOML in [mcp.servers]
# - Others: Their native format
```

**Benefits:**
- Single source of truth for MCP server configuration
- Consistent server setup across all coders
- Easier to add new MCP servers globally

---

## Summary

The current architecture is clean and the renderer pattern works well for
accommodating different coder behaviors. These suggestions aim to:

1. Make the code more extensible for new formats
2. Clarify the semantic capabilities of each coder
3. Standardize memory file handling
4. Leverage the skills convergence across coders
5. Unify MCP server configuration

Not all suggestions need to be implemented immediately. They represent
evolutionary improvements to consider as the project grows.
