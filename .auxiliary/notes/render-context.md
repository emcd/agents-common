# Render Context Goal State

## Overview

This document specifies the goal state for template rendering context in `agentsmgr`. The context passed to Jinja2 templates must provide normalized, coder-specific variables that enable clean template logic.

## Current State vs Goal State

### Current Implementation

**File**: `sources/agentsmgr/commands.py:167-171`

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

## Implementation Approach

### Phase 1: Variable Normalization (Immediate)

**Location**: `sources/agentsmgr/commands.py:_load_item_metadata()` or new `_normalize_render_context()` method

**Tasks**:
1. Transform hyphenated keys to underscored keys
2. Create `SimpleNamespace` for coder configuration
3. Create `SimpleNamespace` for context (normalized frontmatter)
4. Return variables dictionary with `content`, `coder`, `context`

**Example Implementation Pattern**:
```python
def _normalize_context(
    frontmatter: dict[ str, __.typx.Any ], coder: str
) -> __.types.SimpleNamespace:
    ''' Normalizes frontmatter into context namespace. '''
    normalized = {
        key.replace( '-', '_' ): value
        for key, value in frontmatter.items( )
    }
    # Map allowed_tools if present
    if 'allowed_tools' in normalized:
        normalized[ 'allowed_tools' ] = _map_allowed_tools(
            normalized[ 'allowed_tools' ], coder )
    return __.types.SimpleNamespace( **normalized )
```

### Phase 2: Tool Specification Mapping (Subsequent)

**Location**: New module `sources/agentsmgr/tools.py`

**Tasks**:
1. Implement `map_allowed_tools(specs: list, coder: str) -> list[str]`
2. Handle `{ tool = 'shell', arguments, allow-extra-arguments }` format
3. Handle `{ server, tool }` format for MCP servers
4. Handle semantic tool names (lowercase strings)
5. Integrate into normalization pipeline

**Example**:
```python
def map_allowed_tools(
    specs: __.cabc.Sequence[ str | dict[ str, __.typx.Any ] ], coder: str
) -> list[ str ]:
    ''' Maps tool specifications to coder-specific syntax. '''
    result = [ ]
    for spec in specs:
        if isinstance( spec, str ):
            # Semantic name: 'read' → 'Read', 'list-directory' → 'LS'
            result.append( _map_semantic_tool( spec, coder ) )
        elif isinstance( spec, dict ):
            if 'server' in spec:
                # MCP server tool
                result.append( _map_mcp_tool( spec, coder ) )
            elif spec.get( 'tool' ) == 'shell':
                # Shell command
                result.append( _map_shell_command( spec, coder ) )
    return result
```

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

### Unit Tests

**Test normalization**:
```python
def test_normalize_hyphenated_keys():
    frontmatter = {
        'argument-hint': 'major.minor',
        'allowed-tools': [
            { 'tool': 'shell', 'arguments': 'git status' },
            { 'tool': 'shell', 'arguments': 'git pull', 'allow-extra-arguments': True },
            'read',
            'list-directory',
            { 'server': 'librovore', 'tool': 'query-inventory' },
        ],
    }
    context = _normalize_context( frontmatter, 'claude' )
    assert context.argument_hint == 'major.minor'
    assert context.allowed_tools == [
        'Bash(git status)',
        'Bash(git pull:*)',
        'Read',
        'LS',
        'mcp__librovore__query_inventory',
    ]
```

### Integration Tests

**Test rendering**:
```python
def test_render_with_normalized_context():
    # Given: TOML with hyphenated keys and explicit tool specifications
    # When: Render template
    # Then: Output has proper frontmatter with coder-specific tools
```

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
