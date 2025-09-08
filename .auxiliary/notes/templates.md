# Template-Based Settings Distribution Analysis

## Executive Summary

This document analyzes implementation options for template-based settings distribution in agents-common and recommends a hybrid approach: agents-common provides base configuration templates via Copier, while `agentsmgr` generates dynamic content (commands, agents) directly in downstream projects from structured data sources.

## Current State Assessment

**What's Already Implemented:**
- ✅ Jinja2 template system with parameterized paths (`settings.json.jinja`)
- ✅ Python package structure with `agentsmgr` CLI tooling foundation
- ✅ Tag-based versioning strategy (agents-N) in documentation
- ✅ Copier template configuration with language and coder selection

**Current Goal:** Implement data-driven agent configuration generation with hybrid Copier + agentsmgr approach.

## Implementation Options Analysis

### Option 1: Hybrid Copier + agentsmgr Approach (Recommended)

**Architecture:**
```
agents-common/data/ → agentsmgr populate (in downstream) → dynamic content generation
agents-common/template/ → Copier distribution → base configuration templates
```

**Strengths:**
- **Faster iteration cycle**: Command changes don't require template generation and tagging
- **Repository efficiency**: No generated artifacts committed to agents-common
- **True portability**: `agentsmgr` becomes universal tool, not repository-specific
- **Proven distribution**: Base templates still use Copier's mature mechanisms
- **Minimal commit noise**: Generated content ignored via .gitignore in downstream projects
- **Clean separation**: Static base templates vs. dynamic generated content

**Implementation Pattern:**
```python
# agentsmgr populate --source=agents-common@agents-3
def populate(source: str, target: Path):
    # Detect configuration from Copier answers
    config = load_yaml(target / ".auxiliary/configuration/copier-answers--agents.yaml")

    # Generate dynamic content directly in target
    for coder in config["coders"]:
        generate_commands(source, target, coder, config["languages"])
        generate_agents(source, target, coder, config["languages"])
```

**Repository Structure:**
```
agents-common/
├── data/                           # Source data
│   ├── configurations/            # Tool-agnostic TOML configurations
│   ├── contents/                  # Coder-specific content bodies
│   └── templates/                 # Generic, reusable Jinja2 templates
├── template/                      # Base Copier template (minimal)
│   └── .auxiliary/configuration/
│       ├── claude/
│       │   ├── commands/.gitignore    # Ignore generated content
│       │   ├── agents/.gitignore
│       │   ├── scripts/              # Hook executables
│       │   └── settings.json.jinja   # Base template (kept)
│       └── mcp-servers.json.jinja     # Base template (kept)
└── copier.yaml                    # Template configuration
```

### Option 2: Custom CLI-Based Template Renderer

**Architecture:**
```
agents-common → agentsmgr CLI → rendered settings.json + local.toml overrides
```

**Strengths:**
- **Direct control**: Full control over rendering and path resolution logic
- **Local overrides**: TOML-based local customization without template modification
- **Existing foundation**: Leverages existing `agentsmgr` package scaffolding

**Weaknesses:**
- **Requires custom tooling**: Builds custom solution when proven options (Copier) exist
- **Custom conflict resolution**: Must implement update and conflict handling from scratch
- **CLI installation dependency**: Requires additional tooling installation for basic project setup
- **Limited workflow integration**: Doesn't leverage existing Copier multi-template capabilities

### Option 3: Git Submodule + Direct Integration

**Architecture:**
```
python-project-common (submodule: agents-common) → direct file inclusion
```

**Weaknesses:**
- **Submodule maintenance overhead**: Git submodules are notoriously problematic
- **Version coordination complexity**: Difficult to pin to specific agent configurations
- **No local customization**: Limited override capabilities
- **Path resolution issues**: Still doesn't solve the core coordination problem

## Recommended Implementation Strategy

**Option 1** (Hybrid Copier + agentsmgr) provides the optimal balance of proven distribution for base templates and fast iteration for dynamic content, with clean separation of concerns.

### Phase 1: Base Template Structure

**Minimal Template Creation:**
```
template/
└── .auxiliary/configuration/
    ├── claude/
    │   ├── commands/.gitignore        # "*\n!.gitignore"
    │   ├── agents/.gitignore
    │   ├── scripts/                   # Hook executables
    │   └── settings.json.jinja        # Base settings template
    ├── opencode/
    │   └── commands/.gitignore
    ├── gemini/
    │   └── commands/.gitignore
    └── mcp-servers.json.jinja          # Base MCP configuration
```


### Phase 2: Source Data and Templates

**Data Structure Creation:**
```
data/
├── configurations/     # Tool-agnostic TOML configurations
│   ├── commands/      # Command metadata
│   └── agents/        # Agent metadata
├── contents/          # Coder-specific content bodies
│   ├── commands/
│   │   ├── claude/    # Falls back to/from opencode/
│   │   ├── opencode/  # Falls back to/from claude/
│   │   └── gemini/    # No fallback - different syntax
│   └── agents/
│       ├── claude/    # Falls back to/from opencode/
│       ├── opencode/  # Falls back to/from claude/
│       └── gemini/    # No fallback - different syntax
└── templates/         # Generic, reusable templates
    ├── command.md.jinja    # For Claude/Opencode
    ├── command.toml.jinja  # For Gemini
    ├── agent.md.jinja      # For Claude/Opencode
    └── agent.toml.jinja    # For Gemini
```

### Phase 3: agentsmgr Command Implementation

**Dynamic Content Generation:**
```python
# agentsmgr populate --source=agents-common@agents-3
class PopulateCommand:
    def populate(self, source: str, target: Path = Path.cwd()):
        # Load configuration from Copier answers
        config = self._detect_configuration(target)

        # Fetch data from source
        data = self._fetch_data_source(source)

        # Generate content for each selected coder
        for coder in config["coders"]:
            self._generate_coder_content(
                data, target, coder, config["languages"]
            )

    def _detect_configuration(self, target: Path) -> Dict[str, Any]:
        answers_file = target / ".auxiliary/configuration/copier-answers--agents.yaml"
        if answers_file.exists():
            return load_yaml(answers_file)
        # Fallback to defaults
        return {"languages": ["python"], "coders": ["claude"]}
```

### Phase 4: Copier Integration

**Integration with Copier Workflows:**
- **New projects**: python-project-common hooks call `agentsmgr populate` if agents enabled
- **Agent updates**: `copier update` on agents-common triggers repopulation via hooks
- **Manual updates**: Direct `agentsmgr populate --source=agents-common@agents-N` calls

### Phase 5: Implementation and Testing


**Eliminate prepare-agents Complexity:**
- Replace `prepare-agents` script with `agentsmgr populate` calls
- Move command format generation from runtime to agentsmgr
- Projects use standard Copier workflows for configuration updates

**Validation and Testing:**
```python
# agentsmgr validate --variant=maximum --preserve
# Similar to emcdproj template validate pattern
# Generates content in temp directory and validates structure
```

## Addressing Near-Duplicate Problems

**Current Issue:** The `prepare-agents` script contains tool-specific hardcoded logic that creates maintenance overhead and doesn't scale cleanly to new AI tools.

**Solution with Copier Template Approach:**

**Data-Driven Command Generation:**
```python
# agentsmgr populate-template handles format generation at generation time
def generate_tool_commands(tool_name: str, commands_data: List[Dict]):
    if tool_name == "opencode":
        # Generate Opencode-specific YAML frontmatter format
        return [generate_opencode_format(cmd) for cmd in commands_data]
    elif tool_name == "claude":
        # Generate Claude Code format with full frontmatter
        return [generate_claude_format(cmd) for cmd in commands_data]
    # ... other tools
```

**Eliminates Runtime Format Processing:**
- Tool-specific command generation handled at agentsmgr populate time
- No more `copy_claude_commands()` logic in prepare-agents
- Projects use agentsmgr for dynamic content generation

## Technical Advantages

1. **Single Source of Truth**: agents-common/data/ becomes canonical source for all agent configurations
2. **Faster Iteration**: Command changes don't require template commits, tags, or Copier updates
3. **Repository Efficiency**: No generated artifacts committed to agents-common, cleaner git history
4. **True Portability**: `agentsmgr` works with any data source, not just agents-common
5. **Proven Base Distribution**: Settings templates still use Copier's mature mechanisms
6. **Minimal Commit Noise**: Generated content ignored in downstream projects via .gitignore
7. **Clean Separation**: Static base templates vs. dynamic generated content
8. **Standard Workflows**: Leverages both Copier and standalone CLI patterns appropriately

## Implementation Phases

### Phase 1: Base Template Structure ✅ COMPLETED
- ✅ Create minimal template structure with .gitignore files for generated content
- ✅ Base settings templates (settings.json.jinja, mcp-servers.json.jinja)
- ✅ Hook executables distributed via Copier template
- ✅ Template output validation and testing

### Phase 2: Source Data and Templates
- Design TOML structure for commands and agents based on existing YAML frontmatter
- Create structured data files in data/configurations/commands/ and data/configurations/agents/
- Create coder-specific content files in data/contents/
- Build generic, reusable Jinja2 templates for markdown and TOML formats
- Template validation and format compatibility testing

### Phase 3: agentsmgr Command Implementation  
- Core `agentsmgr populate` command for dynamic content generation
- Configuration detection from Copier answers
- Git source fetching with local cache management
- Template rendering pipeline with language filtering
- Multi-coder content generation with format-specific handling

### Phase 4: Copier Integration
- Create Copier hook integration for automatic `agentsmgr populate` calls
- Integration with python-project-common hooks for new projects
- Multi-template workflow testing with dummy projects
- Documentation for multi-template usage patterns

### Phase 5: Implementation and Testing
- Replace `prepare-agents` script with `agentsmgr populate` calls
- End-to-end testing across data → agentsmgr → project pipeline
- Validation and testing similar to emcdproj template validate pattern
- Documentation and adoption guides

This approach implements a hybrid system where static base templates use proven Copier distribution while dynamic content generation provides fast iteration cycles.
