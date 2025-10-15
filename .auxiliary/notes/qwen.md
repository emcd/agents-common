# Qwen Code Support Implementation Plan

## Overview

Qwen Code is a fork of Gemini CLI with similar architecture to Claude Code. Adding support requires implementing a new renderer and creating Qwen-specific content/template structure. The existing plugin architecture is well-suited for this extension.

## Reference Documentation

- Extension system: https://qwenlm.github.io/qwen-code-docs/en/extension/
- Tool configuration: https://qwenlm.github.io/qwen-code-docs/en/tools/
- Subagents: https://qwenlm.github.io/qwen-code-docs/en/subagents/
- CLI configuration: https://qwenlm.github.io/qwen-code-docs/en/cli/configuration/

## Key Differences from Claude Code

### Configuration Structure

**Path Locations:**
- **User settings:** `~/.qwen/settings.json`
- **Project settings:** `.qwen/settings.json`
- **System settings:** OS-specific locations (overridable via `QWEN_CODE_SYSTEM_SETTINGS_PATH`)
- **No per-user path override variable** (unlike Claude's `CLAUDE_CONFIG_DIR`)

**Directory Structure:**
- Extensions: `.qwen/extensions/`
- Extension config: `qwen-extension.json` per extension
- Commands: Can be nested in subdirectories (e.g., `commands/gcs/sync.toml`)
- Agents: `.qwen/agents/` directory

### Agent Format

Qwen agents use Markdown with YAML frontmatter:

```yaml
---
name: agent-name
description: Brief task-specific description
tools: tool1, tool2, tool3  # Optional explicit tool list
---
System prompt content
```

This differs from Claude's pure markdown format.

### Extension System

Qwen supports extensions with:
- Isolated command namespaces
- MCP server configurations per extension
- Conflict resolution via automatic prefixing (e.g., `/gcp.deploy`)
- Command precedence rules

### Context File

Qwen uses `QWEN.md` as the context file (vs Claude's `CLAUDE.md`), configurable via `contextFileName` in extension config.

## Required Implementation Components

### 1. Qwen Renderer

**File:** `sources/agentsmgr/renderers/qwen.py`

**Key Attributes:**
- `name = 'qwen'`
- `modes_available = frozenset(('per-user', 'per-project'))`
- `mode_default = 'per-project'`
- `memory_filename = 'QWEN.md'`

**Path Resolution:**

**Per-project mode:**
- Target: `.auxiliary/configuration/coders/qwen/`
- Maintains consistency with existing coder pattern
- Users can symlink to `.qwen/` if desired

**Per-user mode:**
- Fallback: `~/.qwen/` (no environment variable override available)
- Configuration file override support via `directory` field in coder config
- Note: Qwen does not provide a standard environment variable for user config path override

**Implementation Pattern:**
Follow the same structure as `ClaudeRenderer` and `OpencodeRenderer`, adapting path logic for Qwen's conventions.

### 2. Content Body Structure

**Directory:** `defaults/contents/`

**New Subdirectories:**
```
defaults/contents/
├── commands/
│   └── qwen/          # Qwen-specific command content
│       ├── cs-conform-python.md
│       ├── cs-release-final.md
│       ├── cs-architect.md
│       └── [25+ other commands]
└── agents/
    └── qwen/          # Qwen-specific agent content
        └── python-conformer.md  # With YAML frontmatter
```

**Content Adaptation Strategy:**
- **DEFERRED:** Port commands and agents to Qwen after research phase
- Need to investigate command argument interpolation in Qwen
- Need to establish mapping between coder-agnostic tool types and Qwen tools
- Key differences to address when porting:
  - Agent frontmatter with explicit tool specifications
  - Command argument handling and interpolation
  - Tool name translations

**Agent Content Requirements:**
- Must include YAML frontmatter with `name`, `description`, and optional `tools`
- System prompt follows the frontmatter separator
- Tool specifications must map to Qwen's tool names (mapping TBD)

### 3. Template Structure

**Current State:**
- `defaults/templates/command.md.jinja` - Used by all Markdown-based coders
- `defaults/templates/agent.md.jinja` - Used by all Markdown-based coders
- Assumes format homogeneity within file type categories

**Challenge:**
- Claude, Opencode, and Codex share the same Markdown structure
- Gemini and Qwen share TOML structure
- Qwen agents use Markdown with YAML frontmatter (differs from Claude)
- Future coders may introduce new format variations

**Decision: Pioneer-Named Template Flavors**

Templates organized by item type and pioneering coder:

```
defaults/templates/
├── commands/
│   ├── claude.md.jinja      # Markdown format (Claude, Opencode, Codex)
│   └── gemini.toml.jinja    # TOML format (Gemini, Qwen)
└── agents/
    ├── claude.md.jinja      # Claude agent format (name, description, model, color)
    ├── opencode.md.jinja    # Opencode agent format (description, mode, model, color)
    └── qwen.md.jinja        # Qwen agent format (name, description, tools)
```

**Rationale:**
- Names honor the pioneering coder for each format
- Avoids encoding "override" hierarchy in directory structure
- Each template is simple and focused without conditional logic
- Eliminates "conditional spaghetti" in shared templates
- Templates are few and updated infrequently, so duplication is acceptable
- Self-documenting: template name indicates which coder's format
- Flexible: coders specify which template they use per item type

**Renderer Template Selection:**

Renderers implement method to specify template flavor per item type:

```python
class ClaudeRenderer(RendererBase):
    def get_template_flavor(self, item_type: str) -> str:
        return 'claude'  # Uses claude template for both commands and agents

class OpencodeRenderer(RendererBase):
    def get_template_flavor(self, item_type: str) -> str:
        if item_type == 'commands':
            return 'claude'    # Shares markdown command format
        return 'opencode'      # Uses own agent format

class QwenRenderer(RendererBase):
    def get_template_flavor(self, item_type: str) -> str:
        if item_type == 'commands':
            return 'gemini'  # Shares TOML format with Gemini
        return 'qwen'        # Uses own agent format
```

**Current Template Mappings:**
- **Commands:**
  - Claude, Opencode, Codex → `claude.md.jinja` (Markdown format)
  - Gemini, Qwen → `gemini.toml.jinja` (TOML format)
- **Agents:**
  - Claude → `claude.md.jinja` (name, description, model, color)
  - Opencode → `opencode.md.jinja` (description, mode, model, color)
  - Qwen → `qwen.md.jinja` (name, description, tools)
  - Codex → `claude.md.jinja` (likely same as Claude)
  - Gemini (future) → `gemini.md.jinja` or `gemini.toml.jinja` (TBD)

**Benefits:**
- Each template is clean and straightforward
- No conditional logic within templates
- Easy to understand what each coder expects
- Simple to customize per-coder frontmatter fields
- Clear ownership of format specifications
- Scales cleanly as new coders are added

### 4. Copier Template Base Files

**Directory:** `template/.auxiliary/configuration/coders/qwen/`

**Required Files:**
```
template/.auxiliary/configuration/coders/qwen/
├── settings.json.jinja           # Base Qwen settings
├── .gitignore                    # Ignore generated content
├── agents/.gitignore             # Generated agents ignored
└── commands/.gitignore           # Generated commands ignored (if supported)
```

**settings.json.jinja Structure:**

Based on Qwen Code configuration options and comparison with Claude/Opencode templates:

```json
{
  "contextFileName": "QWEN.md",

  "mcpServers": {
    {%- if "rust" in languages %}
    "rust-analyzer": {
      "command": "mcp-language-server",
      "args": ["--lsp", "rust-analyzer", "--workspace", "."]
    },
    {%- endif %}
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    },
    "librovore": {
      "command": "uvx",
      "args": ["librovore", "serve"]
    }{%- if "python" in languages %},
    "pyright": {
      "command": "mcp-language-server",
      "args": ["--lsp", "pyright-langserver", "--workspace", ".", "--", "--stdio"]
    }
    {%- endif %}
  },

  "coreTools": [
    "run_shell_command",
    "run_shell_command(git add)",
    "run_shell_command(git branch)",
    "run_shell_command(git diff)",
    "run_shell_command(git log)",
    "run_shell_command(git show)",
    "run_shell_command(git status)",
    "run_shell_command(gh)",
    {%- if "python" in languages %}
    "run_shell_command(hatch)",
    {%- endif %}
    {%- if "rust" in languages %}
    "run_shell_command(cargo)",
    {%- endif %}
    "run_shell_command(ls)",
    "run_shell_command(pwd)",
    "run_shell_command(rg)"
  ],

  "excludeTools": [],

  "fileFiltering": {
    "respectGitIgnore": true,
    "enableRecursiveFileSearch": true
  },

  "autoAccept": false,
  "checkpointing": true,
  "showLineNumbers": true
}
```

**Note:** The `coreTools` whitelist above mirrors Claude's `auto_allow` bash patterns, adapted to Qwen's prefix-matching format.

**Configuration Comparison:**

| Feature | Claude | Opencode | Qwen | Notes |
|---------|--------|----------|------|-------|
| **MCP Servers** | ✓ | ✓ | ✓ | Same structure, different key names |
| **Hooks** | ✓ (pre/post tool use) | ❌ | ❌ | Qwen does not have hook system |
| **Permissions** | ✓ (auto_allow list) | ✓ (allow patterns) | ✓ (coreTools/excludeTools) | Both whitelist and blacklist |
| **Environment Variables** | ✓ (env object) | ❌ | ? | Need to verify Qwen support |
| **Tool Restrictions** | ✓ (Bash patterns) | ✓ (bash patterns) | ✓ (run_shell_command patterns) | Similar granularity |
| **Scripts Directory** | ✓ (.claude/scripts/) | ❌ | ❌ | No hook scripts in Qwen |

**Key Differences:**
- **Permissions Model:** Qwen supports BOTH `coreTools` (whitelist) AND `excludeTools` (blacklist)
  - Can use whitelist-only, blacklist-only, or combined
  - `excludeTools` always takes precedence
- **Hooks:** Qwen does not have pre/post tool use hooks
- **Shell Commands:** Qwen has similar granularity to Claude!
  - Claude: `Bash(git add:*)` - explicit wildcard for subcommands
  - Qwen: `run_shell_command(git add)` - prefix matching automatically includes subcommands
  - Both support restricting to specific commands

**Open Questions:**
1. Does Qwen support environment variables in settings.json? (Like Claude's `env` object)
2. Should settings.json use `coreTools` (whitelist), or rely primarily on agent-level tool specifications?
   - Recommendation: Use `coreTools` whitelist for consistency with Claude's approach
   - Agent-level specs provide additional fine-grained control

### 5. Renderer Registry Update

**File:** `sources/agentsmgr/renderers/__init__.py`

**Change:**
```python
# Add qwen import to module import list
from . import claude, codex, opencode, qwen
```

Self-registration happens via `RENDERERS['qwen'] = QwenRenderer()` in qwen.py module.

### 6. Documentation Updates

**Files to Update:**
- `README.rst` - Add Qwen Code to supported coders list
- `documentation/architecture/summary.rst` - Update coder enumeration
- `documentation/architecture/filesystem.rst` - Add Qwen directory structures and template override pattern

## Design Considerations

### Commands vs Extensions

**Research Findings:**

**Agents:** Can be placed directly in standard locations without extension system:
- Project-level: `.qwen/agents/`
- User-level: `~/.qwen/agents/`
- No extension system required ✓

**Commands:** ✓ RESOLVED - Use same approach as Gemini/TOML format:
- Commands use TOML format (shared with Gemini)
- Argument interpolation: `{{args}}` placeholder in prompt (Gemini-style)
- Two interpolation modes: raw injection or shell-escaped injection
- If no `{{args}}`, arguments appended to end of prompt
- Extension system: **DEFERRED** - can use for organization but not required for basic commands

**Argument Interpolation Example:**
```toml
[metadata]
name = "cs-release-final"
argument-hint = "major.minor"

[context]
description = "Execute final release with version {{args}}"
prompt = "Please execute the final release process for version {{args}}."
```

When invoked: `/cs-release-final 2.0` → prompt includes "version 2.0"

**Implementation Approach:**
- **Agents:** Generate directly in `.qwen/agents/` ✓ (straightforward)
- **Commands:** Use TOML format with `{{args}}` interpolation ✓
  - Qwen and Gemini can share same command content ✓
  - Template: `defaults/templates/commands/gemini.toml.jinja`
  - Content: Can use same body for both Qwen and Gemini
- **Extension system:** Not required for basic commands, can add later for organization

**Key Insight:**
Qwen uses Gemini-style command format, so we can generate commands for both with the same content and template!

### Agent Tool Specification

**Challenge:** Qwen agents explicitly list available tools in YAML frontmatter

**Opportunities:**
- More explicit than Claude's implicit tool availability
- Better tool governance and security
- Clear documentation of agent capabilities

**Implementation:**
- Extend TOML configuration schema with optional `tools` array
- Render tools list in Qwen-specific agent template
- **RESEARCH NEEDED:** Establish mapping between coder-agnostic tool types and Qwen tool names
- Consider wildcard support (e.g., `tools: ["*"]`) or tool groups for convenience

**Tool Mapping Requirements:**

Based on Qwen Code documentation and existing semantic tool names, the mapping is:

| Semantic Name | Claude Tool | Qwen Tool | Status |
|---------------|-------------|-----------|--------|
| `read` | `Read` | `read_file` | ✓ Direct mapping |
| `write` | `Write` | `write_file` | ✓ Direct mapping |
| `edit` | `Edit` | `edit` | ✓ Direct mapping |
| `multi-edit` | `MultiEdit` | `edit` | ⚠️ Qwen uses single edit tool |
| `list-directory` | `LS` | `list_directory` | ✓ Direct mapping |
| `glob` | `Glob` | `glob` | ✓ Direct mapping |
| `grep` | `Grep` | `search_file_content` | ✓ Semantic equivalent |
| `todo-write` | `TodoWrite` | `todo_write` | ✓ Direct mapping |
| `web-fetch` | `WebFetch` | `web_fetch` | ✓ Direct mapping |
| `web-search` | `WebSearch` | `web_search` | ✓ Direct mapping |
| `shell` (compound) | `Bash(...)` | `run_shell_command` | ⚠️ Different structure - see below |

**Shell Tool Mapping - Granular Permissions Supported:**

Both Claude and Qwen support granular shell command permissions!

**Claude format**: `Bash(git status)`, `Bash(git add:*)` (with `:*` wildcard for extra arguments)
**Qwen format**: `run_shell_command(git)` (prefix matching automatically allows subcommands)

**Key Qwen Features:**
- **Whitelist**: `coreTools: ["run_shell_command(git)", "run_shell_command(npm)"]` - only allow these prefixes
- **Blacklist**: `excludeTools: ["run_shell_command(rm)"]` - block these prefixes
- **Wildcard**: Include `run_shell_command` (without prefix) in `coreTools` to allow all except blocked
- **Prefix Matching**: `run_shell_command(git)` allows `git status`, `git log`, etc.
- **Chain Blocking**: Automatically splits `&&`, `||`, `;` and validates each part
- **Blocklist Precedence**: `excludeTools` checked first (overrides `coreTools`)

**Mapping Strategy:**
1. **Whitelist mode** (most commands):
   - `{ tool = 'shell', arguments = 'git status' }` → `run_shell_command(git status)` in `coreTools`
   - `{ tool = 'shell', arguments = 'git add', allow-extra-arguments = true }` → `run_shell_command(git add)` in `coreTools`
   - Claude's `:*` wildcard not needed - Qwen uses prefix matching automatically
2. **Blocklist mode** (when `allowed-tools` is broad):
   - Convert excluded commands to `excludeTools` list
3. **Agent-level**: List `run_shell_command` if any shell access needed

**Qwen-Specific Tools (No Semantic Equivalent Yet):**
- `read_many_files` - Batch file reading (could add as `read-many`)
- `save_memory` - Memory persistence (already have `todo-write`)

**Implementation Strategy:**
- Add `_map_tools_qwen()` function to `context.py` alongside `_map_tools_claude()`
- All semantic tools have direct or equivalent mappings ✓
- Shell commands mapping:
  - `{ tool = 'shell', arguments = 'git status' }` → `run_shell_command(git status)`
  - `{ tool = 'shell', arguments = 'git add', allow-extra-arguments = true }` → `run_shell_command(git add)` (prefix matching handles subcommands)
  - Remove Claude's `:*` suffix - Qwen uses prefix matching automatically
  - Both Claude and Qwen support granular per-command restrictions ✓
- MCP tools: Similar mapping as Claude (`mcp__server__tool` format - need to verify Qwen format)
- For agent tools lists: return sorted list of Qwen tool names

### Command Organization

**Qwen Capability:** Supports nested command directories (`commands/gcs/sync.toml`)

**Approach:**
- **DEFERRED:** Command organization pending research on command system
- If commands require extension system, may need different organizational approach
- If direct command placement supported, flat structure is simplest starting point
- Configuration could support `category` field for future hierarchical organization

### Configuration Path Override

**Limitation:** Qwen provides no environment variable for user config path override (unlike `CLAUDE_CONFIG_DIR`)

**Workaround:**
- Support configuration file `directory` override
- Document that path override is configuration-only for Qwen
- Accept `~/.qwen/` as the standard per-user location

## Implementation Phases

### Phase 0: Template System Restructuring

**Foundation Work:**

Restructure template system to support pioneer-named flavors:

1. **Migrate and split existing templates**
   - Move `defaults/templates/command.md.jinja` → `defaults/templates/commands/claude.md.jinja`
   - Split `defaults/templates/agent.md.jinja` into separate coder-specific templates:
     - `defaults/templates/agents/claude.md.jinja` (name, description, model, color fields)
     - `defaults/templates/agents/opencode.md.jinja` (description, mode, model, color fields)
   - Remove conditional logic from templates - each template is clean and focused
   - Update existing TOML templates (if any) to new structure

2. **Update RendererBase protocol**
   - Add `get_template_flavor(item_type: str) -> str` method to base class
   - Default implementation returns 'claude' for backward compatibility
   - Document template flavor selection contract

3. **Update generator template resolution**
   - Modify template lookup to check `defaults/templates/{item_type}/{flavor}.{ext}.jinja`
   - Call renderer's `get_template_flavor()` to determine which template to use
   - Remove any hardcoded template path assumptions

4. **Update existing renderers**
   - Implement `get_template_flavor()` in ClaudeRenderer (returns 'claude' for all item types)
   - Implement `get_template_flavor()` in OpencodeRenderer (returns 'claude' for commands, 'opencode' for agents)
   - Implement `get_template_flavor()` in CodexRenderer (returns 'claude' for all item types)

5. **Implement tool mapping infrastructure**
   - Add `_map_tools_qwen()` function to `sources/agentsmgr/commands/context.py`
   - Update `_map_tools_for_coder()` to dispatch to Qwen mapper
   - Implement semantic → Qwen tool name translation (see mapping table)
   - Shell command mapping:
     - Map `{ tool = 'shell', arguments = 'git add', allow-extra-arguments = true }` → `run_shell_command(git add)`
     - Strip Claude's `:*` suffix since Qwen uses prefix matching
     - Preserve command prefix for granular permissions
   - MCP tool mapping (verify format matches Claude's pattern)
   - Add tests for Qwen tool mapping including shell commands

6. **Test template migration and tool mapping**
   - Verify existing content generation still works
   - Ensure no regressions in Claude/Opencode/Codex output
   - Validate template path resolution logic
   - Test Qwen tool name mapping with sample configurations

**Deliverables:**
- Restructured template system ready for new flavors
- All existing coders working with new structure
- Qwen tool name mapping implemented and tested
- Foundation for Qwen-specific templates

### Phase 1: Minimal Viable Support

**Core Implementation:**
1. Implement `QwenRenderer` class
   - Basic path resolution (per-user: `~/.qwen/`, per-project: `.auxiliary/configuration/coders/qwen/`)
   - Configuration file directory override support
   - Memory filename: `QWEN.md`
   - Template flavor selection: 'gemini' for commands, 'qwen' for agents

2. Template creation
   - Create `defaults/templates/commands/gemini.toml.jinja` for Qwen/Gemini commands
   - Create `defaults/templates/agents/qwen.md.jinja` with YAML frontmatter rendering
   - Verify template variable access and normalization

3. Content creation
   - **Commands:** Can reuse Gemini command content (TOML format with `{{args}}`)
     - No new content needed - Qwen uses same format as Gemini
     - If Gemini content exists, Qwen can use it directly
     - If not, can defer command content until Gemini support added
   - Create `defaults/contents/agents/qwen/` directory
   - Adapt agent definitions (content only, YAML frontmatter comes from template)
   - Apply tool name mapping in agent TOML configurations

4. Copier template files
   - Create base directory structure in `template/.auxiliary/configuration/coders/qwen/`
   - Add `settings.json.jinja` for base Qwen settings
   - Add `.gitignore` files for generated content
   - Consider whether to include `qwen-extension.json.jinja`

5. Registry integration
   - Add qwen import to `renderers/__init__.py`
   - Register renderer via module import

6. Documentation
   - Update README.rst with Qwen Code support
   - Update architecture documentation
   - Document pioneer-named template flavor system

**Deliverables:**
- Functional Qwen Code agent support
- Qwen commands use Gemini TOML format (shared content)
- Content generation via `agentsmgr populate --coder=qwen`
- Generated agent files compatible with Qwen Code CLI
- Base Copier template integration
- Tool name mapping implemented in `context.py`

**Scope:**
- ✓ Commands supported via Gemini TOML format
- ✓ Agents with YAML frontmatter
- ✓ Tool name mapping for all semantic tools
- ⚠️ Command content can reuse Gemini content when available
- ⚠️ Extension system not implemented (not required for basic functionality)

### Phase 2: Enhanced Features

**Advanced Capabilities:**
1. Hierarchical command organization
   - Support for `category` field in TOML configs
   - Nested directory generation in `commands/`
   - Documentation for command organization patterns

2. Tool specification management
   - Define standard tool groups in configuration
   - Template helpers for common tool sets
   - Validation of tool names against known Qwen tools

3. Extension-based organization
   - Support generating commands as Qwen extensions
   - Extension namespace configuration
   - Extension conflict detection and resolution

4. Hook scripts
   - Qwen-specific pre/post tool use hooks (if needed)
   - Script distribution via Copier template
   - Integration with Qwen's tool execution lifecycle

**Deliverables:**
- Advanced organizational patterns
- Rich tool management capabilities
- Extension system integration
- Complete hook script infrastructure

### Phase 3: Cross-Coder Harmonization

**System-Wide Improvements:**
1. Content harmonization
   - Review differences between Claude, Opencode, Qwen content
   - Identify opportunities for cross-coder content reuse
   - Document coder-specific customization needs

2. Multi-coder project support
   - Improved tooling for projects using multiple coders
   - Conflict detection for shared resources
   - Documentation for multi-coder workflows

3. Template system evolution
   - Evaluate pioneer-named flavor pattern effectiveness
   - Consider template composition/inheritance patterns
   - Expand template customization capabilities

4. User experience polish
   - Improved error messages for Qwen-specific issues
   - Better detection of Qwen Code installation
   - Enhanced simulation mode for Qwen content preview

**Deliverables:**
- Consistent experience across all supported coders
- Robust multi-coder workflows
- Refined template architecture
- Production-ready tooling

## Testing Strategy

**Required Test Coverage:**

1. **Renderer Tests**
   - Path resolution for per-user and per-project modes
   - Configuration file directory override handling
   - Memory filename validation
   - Mode validation (ensure only supported modes accepted)

2. **Template Tests**
   - YAML frontmatter rendering for Qwen agents
   - Template flavor resolution logic
   - Template path construction for different item types
   - Variable normalization in templates

3. **Content Validation Tests**
   - Generated files match Qwen's expected formats
   - YAML frontmatter is valid YAML
   - Required fields present in agent frontmatter
   - Commands follow expected markdown structure

4. **Integration Tests**
   - Full populate workflow with Qwen coder selection
   - Multiple coders in same project
   - Copier template application
   - End-to-end generation from source to output

5. **Configuration Tests**
   - Coder configuration parsing
   - Directory override precedence
   - Environment variable handling (system settings path)
   - Configuration validation

## Migration Path

**User Workflow:**
1. Update to agents-common version with Qwen support
2. Run `agentsmgr populate --coder=qwen --source=github:emcd/agents-common@agents-N`
3. Generated content appears in `.auxiliary/configuration/coders/qwen/`
4. Optionally symlink to `.qwen/` directory or copy content as needed

**Considerations:**
- Should agentsmgr support direct population to `.qwen/` directory?
  - **Pro:** More direct integration with Qwen expectations
  - **Con:** Breaks consistency with `.auxiliary/configuration/coders/*` pattern
  - **Recommendation:** Keep `.auxiliary/configuration/coders/qwen/` for consistency; document symlinking approach

## Risks and Mitigations

### Risk 1: Format Evolution
**Issue:** Qwen Code may evolve format requirements as it diverges from Gemini CLI
**Mitigation:** Template override system provides flexibility; versioning can handle breaking changes

### Risk 2: Tool List Maintenance
**Issue:** Maintaining explicit tool lists in agent frontmatter could become tedious
**Mitigation:** Tool groups, wildcards, and template helpers reduce manual specification burden

### Risk 3: Extension System Complexity
**Issue:** Full extension system support adds significant implementation complexity
**Mitigation:** Phased approach starts simple; add extension support only if users request it

### Risk 4: Template Proliferation
**Issue:** Pioneer-named flavors could lead to many template files as more coders are added
**Mitigation:** Only create new flavors when formats genuinely differ; coders reuse existing flavors when formats align

### Risk 5: Configuration Path Limitations
**Issue:** No environment variable for user config path override limits flexibility
**Mitigation:** Configuration file override support; document limitation clearly

## Open Questions & Research Needs

### High Priority (Blocking Phase 1)

1. **Tool name mapping:** ✓ RESOLVED
   - Complete mapping table created (all semantic tools map to Qwen tools)
   - Implementation needed in `context.py` (`_map_tools_qwen()` function)
   - Shell tool requires special handling (all-or-nothing vs granular)

2. **Command system architecture:** ✓ RESOLVED
   - Commands use TOML format with `{{args}}` interpolation (Gemini-style)
   - Can reuse Gemini command content for Qwen
   - Extension system not required for basic functionality
   - Template: `gemini.toml.jinja` (shared with Gemini)

### Medium Priority (Phase 2+)

3. **Tool specification defaults:** What should default tool list be for agents? Empty (all tools), specific subset, or wildcard?

4. **Command format:** If commands supported, is format TOML or markdown? What's the structure?

5. **MCP server configuration:** How should MCP server config be integrated with Qwen's approach?

6. **Globals directory:** Does Qwen support equivalent of Claude's per-user global files (statusline, etc.)? If so, where?

7. **Settings template content:** What should be in the base `settings.json.jinja` for Qwen? Minimal config or opinionated defaults?

### Research Tasks

**Completed:**
- ✓ Document Qwen's available tools and their canonical names
- ✓ Create tool name mapping specification (all tools mapped)
- ✓ Draft Qwen settings.json template
- ✓ Investigate command argument passing (uses `{{args}}` Gemini-style)
- ✓ Determine command format (TOML, shared with Gemini)

**Remaining:**
- Investigate Qwen hook system (if any) - appears not to exist, needs confirmation
- Test MCP tool format in Qwen (verify naming convention)
- Verify Qwen accepts same MCP server configuration as Claude/Opencode
- Test agent with tool specifications to verify YAML frontmatter format

## Design Discussion: Whitelist vs Blacklist Tool Specification

**Current State:**
- Our normalized configuration uses `allowed-tools` (whitelist approach)
- Claude uses `auto_allow` (whitelist) in settings.json
- Opencode uses `allow` (whitelist) in settings.jsonc
- Qwen uses `excludeTools` (blacklist) in settings.json

**The Question:**
Should we add `excluded-tools` or `denied-tools` to our normalized configuration to model Qwen's blacklist approach?

**Analysis:**

**Option A: Add Blacklist Support to Normalized Config**
```toml
[context]
allowed-tools = ['read', 'write', 'edit']  # Whitelist
excluded-tools = ['run_shell_command']     # Blacklist
```

**Pros:**
- Can model both whitelist and blacklist approaches
- Flexibility for users who think in "allow all except X" terms
- Direct mapping to Qwen's `excludeTools`

**Cons:**
- Semantic ambiguity: What if both specified? Which takes precedence?
- More complexity in validation and tool resolution
- Most coders use whitelist approach (Claude, Opencode)
- Adds cognitive load for configuration authors

**Option B: Keep Whitelist Only (Current Approach)**
```toml
[context]
allowed-tools = ['read', 'write', 'edit']  # Whitelist only
```

**Pros:**
- Simple, unambiguous semantics
- Consistent with majority of coders (Claude, Opencode)
- Explicit about what tools are available
- Easier to reason about security (default deny)

**Cons:**
- Doesn't directly model Qwen's blacklist approach
- Requires renderer to handle conversion (whitelist → derive blacklist)

**Recommendation: Option B (Keep Whitelist Only)**

**Rationale:**
1. **Semantic Clarity**: Whitelist is more explicit and secure (default deny)
2. **Majority Pattern**: Claude and Opencode use whitelist approach
3. **Qwen Supports Both**: Qwen has BOTH `coreTools` (whitelist) AND `excludeTools` (blacklist)
   - We can map our whitelist to Qwen's `coreTools` directly ✓
   - No conversion needed - 1:1 mapping
4. **Agent-Level Control**: Qwen agents explicitly list tools in frontmatter, providing additional fine-grained control

**Implementation Strategy:**
- Keep `allowed-tools` as the normalized configuration
- QwenRenderer maps to `coreTools` in settings.json generation (whitelist → whitelist)
- Shell commands: `Bash(git add:*)` → `run_shell_command(git add)` in `coreTools`
- Agent YAML frontmatter provides explicit tool list (Qwen's agent-level control)
- Leave `excludeTools` empty by default (can be added later if needed)

**Key Insight:**
Qwen's support for BOTH `coreTools` and `excludeTools` means our whitelist approach maps directly to Qwen's `coreTools`. No complex conversion logic needed - both systems use whitelist as the primary model!

**Edge Case - Allow All:**
If needed in the future, could use `coreTools: ["run_shell_command"]` (wildcard) + specific `excludeTools` entries for blocklist mode. But whitelist-first approach is recommended for security.

## Decision: Template Organization

**Chosen Approach: Pioneer-Named Template Flavors**

Implement template flavor system organized by item type and pioneering coder:

**Structure:**
```
defaults/templates/
├── commands/
│   ├── claude.md.jinja      # Markdown format (Claude, Opencode, Codex)
│   └── gemini.toml.jinja    # TOML format (Gemini, Qwen)
└── agents/
    ├── claude.md.jinja      # Claude agent format (name, description, model, color)
    ├── opencode.md.jinja    # Opencode agent format (description, mode, model, color)
    └── qwen.md.jinja        # Qwen agent format (name, description, tools)
```

**Template Selection:**
- Renderers implement `get_template_flavor(item_type)` method
- Returns pioneer name for the format used by that coder for that item type
- Commands: Claude/Opencode/Codex share markdown; Gemini/Qwen share TOML
- Agents: Each coder uses its own template for specific frontmatter fields

**Rationale:**
- Names honor the pioneering coder for each format
- No special "override" or "shared" directory hierarchy
- Each template is clean and focused without conditional logic
- Eliminates "conditional spaghetti" in shared templates
- Templates are few and updated infrequently, so duplication is acceptable
- Easy to understand what each coder expects
- Scales cleanly as new coders/formats are added

**Implementation Note:**
- Add `get_template_flavor()` method to `RendererBase`
- Update `commands/generator.py` to use `{item_type}/{flavor}.{ext}.jinja` path pattern
- Split existing `agent.md.jinja` into separate `claude.md.jinja` and `opencode.md.jinja`
- Remove conditional logic - each template handles one coder's format
- Migrate existing templates to new structure (Phase 0)

## References

- Current source handlers: `sources/agentsmgr/sources/`
- Current renderers: `sources/agentsmgr/renderers/`
- Architecture documentation: `documentation/architecture/`
- Filesystem organization: `documentation/architecture/filesystem.rst`
