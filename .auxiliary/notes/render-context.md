# Render Context Goal State

## Overview

This document specifies the goal state for template rendering context in `agentsmgr`. The context passed to Jinja2 templates must provide normalized, coder-specific variables that enable clean template logic.

## Current State vs Goal State

### Current Implementation

**File**: `sources/agentsmgr/commands/generator.py:76-81`

```python
variables: dict[ str, __.typx.Any ] = {
    'content': body,
    'coder': metadata[ 'coder' ],
    **metadata[ 'frontmatter' ],  # Raw spread - no normalization
}
```

**Problems**:
1. No hyphen-to-underscore normalization
2. `allowed-tools` stays as string or array, not mapped to coder syntax
3. Frontmatter fields with hyphens inaccessible in templates

**Example**: Template tries `{{ allowed_tools }}` but TOML has `allowed-tools` → undefined variable

### Goal State

**Normalized context with namespace access:**

```python
variables: dict[ str, __.typx.Any ] = {
    'content': body,
    'coder': coder_namespace,  # SimpleNamespace with dot-notation
    'context': context_namespace,  # SimpleNamespace with normalized fields
}

# Where context_namespace contains:
context_namespace = SimpleNamespace(
    name=normalized_name,
    description=normalized_description,
    argument_hint=normalized_argument_hint,  # Hyphen → underscore
    allowed_tools=mapped_tools_list,  # Explicit specs → coder-specific
    color=normalized_color,
    # ... all other frontmatter fields normalized
)
```

## Normalization Requirements

### 1. Hyphen-to-Underscore Transformation

**Source** (`data/configurations/commands/cs-release-final.toml`):
```toml
[frontmatter]
name = 'cs-release-final'
description = 'Execute automated final release...'
argument-hint = 'major.minor'
allowed-tools = [
    { tool = 'shell', arguments = 'git status' },
    { tool = 'shell', arguments = 'git pull', allow-extra-arguments = true },
    { tool = 'shell', arguments = 'git checkout', allow-extra-arguments = true },
    # ... explicit tool specifications
]
```

**Template Variables** (after normalization):
```python
{
    'content': body_content,
    'coder': coder_namespace,
    'context': {
        'name': 'cs-release-final',
        'description': 'Execute automated final release...',
        'argument_hint': 'major.minor',  # Hyphen → underscore
        'allowed_tools': [...],  # Mapped to coder-specific syntax
    }
}
```

**Template Usage**:
```jinja
{%- if context.argument_hint is defined %}
argument-hint: "{{ context.argument_hint }}"
{%- endif %}
```

### 2. Coder Namespace Object

**Source** (from `[[coders]]` table array):
```toml
[[coders]]
name = 'claude'
model = 'sonnet-4.5'
mode = 'interactive'
```

**Template Variable** (SimpleNamespace for dot-notation):
```python
coder = SimpleNamespace(
    name='claude',
    model='sonnet-4.5',
    mode='interactive'
)
```

**Template Usage**:
```jinja
{%- if coder.name == 'claude' and context.allowed_tools is defined %}
allowed-tools: {{ context.allowed_tools | join(', ') }}
{%- endif %}
```

### 3. Tool Specification Mapping

**Source** (explicit tool specifications in TOML):
```toml
[frontmatter]
allowed-tools = [
    # Shell commands - exact match
    { tool = 'shell', arguments = 'git status' },

    # Shell commands - with extra arguments allowed
    { tool = 'shell', arguments = 'git pull', allow-extra-arguments = true },
    { tool = 'shell', arguments = 'git checkout', allow-extra-arguments = true },
    { tool = 'shell', arguments = 'hatch version', allow-extra-arguments = true },

    # Built-in tools (semantic names)
    'read',
    'edit',
    'write',
    'list-directory',

    # MCP server tools
    { server = 'librovore', tool = 'query-inventory' },
    { server = 'librovore', tool = 'query-content' },
]
```

**Mapped Result** (coder-specific syntax):
```python
# For Claude:
context.allowed_tools = [
    'Bash(git status)',
    'Bash(git pull:*)',
    'Bash(git checkout:*)',
    'Bash(hatch version:*)',
    'Read',
    'Edit',
    'Write',
    'LS',
    'mcp__librovore__query_inventory',
    'mcp__librovore__query_content',
]
```

**Mapping Rules**:
- `{ tool = 'shell', arguments = 'git status' }` → `Bash(git status)` (exact match)
- `{ tool = 'shell', arguments = 'git pull', allow-extra-arguments = true }` → `Bash(git pull:*)` (wildcard)
- `'read'` → `Read` (semantic name to coder-specific tool)
- `'list-directory'` → `LS` (semantic name to coder-specific tool)
- `{ server = 'librovore', tool = 'query-inventory' }` → `mcp__librovore__query_inventory` (MCP tool)

**Template Usage**:
```jinja
{%- if coder.name == 'claude' and context.allowed_tools is defined %}
allowed-tools: {{ context.allowed_tools | join(', ') }}
{%- endif %}
```

## Tool Mapping Specifications

### Tool Specification Format

**TOML Source Format** (explicit, no meta-aliases):

```toml
[frontmatter]
allowed-tools = [
    # Shell commands - exact match
    { tool = 'shell', arguments = 'git status' },

    # Shell commands - with extra arguments
    { tool = 'shell', arguments = 'git pull', allow-extra-arguments = true },
    { tool = 'shell', arguments = 'hatch --env develop run', allow-extra-arguments = true },

    # Built-in tools (semantic names, lowercase)
    'read',
    'edit',
    'write',
    'list-directory',
    'glob',

    # MCP server tools
    { server = 'librovore', tool = 'query-inventory' },
    { server = 'context7', tool = 'get-library-docs' },
]
```

### Claude-Specific Mapping

**Mapping Rules**:

| TOML Specification | Claude Syntax | Notes |
|-------------------|---------------|-------|
| `{ tool = 'shell', arguments = 'git status' }` | `Bash(git status)` | Exact match only |
| `{ tool = 'shell', arguments = 'git pull', allow-extra-arguments = true }` | `Bash(git pull:*)` | Wildcard arguments |
| `'read'` | `Read` | Semantic name → Claude tool |
| `'edit'` | `Edit` | Semantic name → Claude tool |
| `'list-directory'` | `LS` | Semantic name → Claude tool |
| `{ server = 'librovore', tool = 'query-inventory' }` | `mcp__librovore__query_inventory` | MCP server tool |

**Future**: Other coders (Opencode, Gemini) with their own mapping rules

## Architecture Notes

### Commands Module Refactor Impact

The commands module was recently refactored (commit `5fe291b`) from a monolithic 500-line `commands.py` into a focused subpackage structure:

- **`base.py`**: Shared infrastructure (error handling, config loading, validation)
- **`generator.py`**: Template rendering and content generation (`ContentGenerator` class)
- **`operations.py`**: Directory population orchestration
- **`detection.py`, `population.py`, `validation.py`**: Individual command implementations
- **`__.py`**: Centralized imports following project patterns

This refactor improves the natural placement of render context logic:

1. **Clear ownership**: Template variable construction now lives in `ContentGenerator.render_single_item()` at `generator.py:76-81`
2. **Focused scope**: Generator module handles all template rendering concerns
3. **Room for growth**: Module currently ~194 lines, can accommodate Phase 1 normalization
4. **Extension path**: Phase 2 complexity warrants new `context.py` module in commands subpackage

### Module Placement Strategy

**Phase 1** (Basic normalization):
- Add `_normalize_context()` method to `ContentGenerator` class
- Rationale: Simple transformation tightly coupled to rendering flow
- Keeps template variable construction cohesive

**Phase 2** (Tool mapping):
- Create new `commands/context.py` module
- Rationale: Significant complexity (3+ functions), clear separation of concerns
- Provides extension point for future context transformations
- Note: Initially considered standalone `tools.py` but rejected as too narrow in scope

## Implementation Approach

### Phase 1: Variable Normalization (Immediate)

**Location**: `sources/agentsmgr/commands/generator.py` (add method to `ContentGenerator` class)

**Implementation Strategy**: Add normalization directly to generator module since:
- Normalization logic is tightly coupled to template rendering
- `generator.py` currently ~194 lines, has room for this functionality
- Keeps all template variable construction in one cohesive location

**Tasks**:
1. Add normalization method to `ContentGenerator` class
2. Transform hyphenated keys to underscored keys
3. Create `SimpleNamespace` for coder configuration
4. Create `SimpleNamespace` for context (normalized frontmatter)
5. Update `render_single_item()` at line 76-81 to use normalized context
6. Return variables dictionary with `content`, `coder`, `context`

**Implementation Considerations**:
- Use `types.SimpleNamespace` for dot-notation access in templates
- Simple key transformation: replace hyphens with underscores
- Preserve all frontmatter values unchanged (except key names)
- Integration point: `ContentGenerator.render_single_item()` after `_load_item_metadata()`
- Variables dict should spread `coder` and `context` namespaces alongside `content`

### Phase 2: Tool Specification Mapping (Subsequent)

**Location**: New module `sources/agentsmgr/commands/context.py`

**Implementation Strategy**: Create dedicated context module for Phase 2 because:
- Tool mapping has significant complexity (3+ helper functions)
- Clear separation of concerns: normalization + tool mapping
- Natural extension point for future context transformations
- Keeps generator module focused on rendering orchestration

**Required Functionality**:
1. Normalization function combining Phase 1 logic with tool mapping
2. Tool specification mapper handling three spec types:
   - String literals (semantic names): `'read'` → coder-specific tool name
   - Shell commands: `{ tool = 'shell', arguments, allow-extra-arguments }` → coder syntax
   - MCP tools: `{ server, tool }` → coder-specific MCP format
3. Helper functions for each tool specification type
4. Coder-specific mapping rules (initially Claude, extensible for Opencode/Gemini)

**Implementation Considerations**:
- **Tool specification types**: Must handle strings, shell dicts, and MCP dicts
- **Shell command wildcards**: `allow-extra-arguments: true` → append wildcard (e.g., `Bash(git pull:*)`)
- **Semantic tool mappings**: Maintain lookup table for semantic names to coder tools
  - Examples: `'read'` → `'Read'`, `'list-directory'` → `'LS'` (Claude)
- **MCP tool format**: `{ server = 'librovore', tool = 'query-inventory' }` → `'mcp__librovore__query_inventory'`
- **Unknown spec handling**: Decide whether to error, warn, or pass through
- **Coder extensibility**: Design mapping rules to accommodate future coders
- **Integration**: Move Phase 1 normalization from `generator.py` into this module
- **Validation**: Consider validating tool specs before mapping (schema compliance)

**Integration Tasks**:
1. Create `sources/agentsmgr/commands/context.py` module
2. Implement tool mapping functions with coder-specific logic
3. Move normalization from `generator.py` to `context.py`
4. Update `ContentGenerator.render_single_item()` to use context module
5. Add validation for tool specifications
6. Update existing TOML files with explicit tool specifications

## Template Contract

### Expected Variables (All Templates)

**Always Present**:
- `content`: str - Raw content body from `data/contents/`
- `coder`: SimpleNamespace - Coder configuration with dot-notation access
  - `coder.name`: str - Coder identifier (e.g., 'claude', 'opencode')
  - `coder.model`: str (optional) - Model identifier
  - `coder.mode`: str (optional) - Interaction mode
- `context`: SimpleNamespace - Normalized frontmatter with dot-notation access
  - All fields from TOML `[frontmatter]` section
  - Hyphenated keys normalized to underscores
  - `allowed_tools` mapped to coder-specific syntax if present

### Template Conditionals

**Check for Optional Context Fields**:
```jinja
{%- if context.argument_hint is defined %}
argument-hint: "{{ context.argument_hint }}"
{%- endif %}
```

**Coder-Specific Logic**:
```jinja
{%- if coder.name == 'claude' and context.allowed_tools is defined %}
allowed-tools: {{ context.allowed_tools | join(', ') }}
{%- endif %}
```

## Validation Requirements

### Context Validation (Pre-Render)

**Checks**:
1. All hyphenated keys converted to underscores in `context` namespace
2. `coder` is SimpleNamespace with required fields (`name` at minimum)
3. `context.allowed_tools` (if present) is list of strings in coder-specific syntax
4. All frontmatter fields accessible via `context.field_name`

### Output Validation (Post-Render)

**Checks**:
1. Generated frontmatter matches expected format for target coder
2. No undefined variable references in output
3. Tool specifications match coder's expected syntax

## Testing Strategy

### Test Coverage Requirements

**Phase 1 Tests** (normalization in `generator.py`):
- Hyphen-to-underscore transformation for all frontmatter keys
- `SimpleNamespace` creation for both `coder` and `context`
- Dot-notation access to all normalized fields
- Preservation of non-hyphenated keys
- Handling of empty frontmatter
- Multiple hyphen cases (e.g., `argument-hint`, `allowed-tools`)

**Phase 2 Tests** (tool mapping in `context.py`):
- Each tool specification type (string, shell dict, MCP dict)
- Shell commands with and without `allow-extra-arguments`
- Semantic tool name mappings for each supported coder
- MCP tool format construction
- Mixed specification lists
- Unknown/invalid specification handling
- Coder-specific mapping rules (Claude, Opencode, Gemini)
- Integration of normalization + tool mapping pipeline

**Integration Tests**:
- End-to-end template rendering with normalized context
- TOML configuration → template → output verification
- Generated frontmatter matches expected coder format
- No undefined template variables in rendered output
- Multiple coders with same source configuration

## Migration Path

### Immediate (Phase 1)

1. ✅ Fix HTML escaping (`autoescape=False`)
2. ⚠️ Implement hyphen-to-underscore normalization for context namespace
3. ⚠️ Create SimpleNamespace for coder configuration
4. ⚠️ Create SimpleNamespace for context (frontmatter)
5. ⚠️ Update templates to use `coder.name` and `context.field_name`

### Near-Term (Phase 2)

1. ⚠️ Implement tool specification mapping:
   - `{ tool = 'shell', arguments, allow-extra-arguments }` → coder syntax
   - `{ server, tool }` → MCP tool syntax
   - Semantic tool names → coder-specific tools
2. ⚠️ Add validation for tool specifications
3. ⚠️ Update existing TOML files with explicit tool specifications

### Future

1. Support other coders (Opencode, Gemini) with their own mapping rules
2. Advanced argument patterns beyond boolean allow-extra-arguments
3. Tool permission validation and security constraints

## Success Criteria

**Phase 1 Complete When**:
- Templates can access `{{ context.argument_hint }}` for `argument-hint` in TOML
- Templates can use `{{ coder.name }}` for coder configuration
- All frontmatter fields accessible via `context` namespace
- Generated files have correct frontmatter structure (minus tool expansion)

**Phase 2 Complete When**:
- `{ tool = 'shell', arguments = 'git pull', allow-extra-arguments = true }` → `Bash(git pull:*)`
- `'list-directory'` → `LS` for Claude
- `{ server = 'librovore', tool = 'query-inventory' }` → `mcp__librovore__query_inventory`
- Generated frontmatter matches existing manual configurations exactly
- All TOML configurations updated with explicit tool specifications
