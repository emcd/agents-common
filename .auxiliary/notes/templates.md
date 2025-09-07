# Template-Based Settings Distribution Analysis

## Executive Summary

This document analyzes implementation options for template-based settings distribution in agents-common and recommends transforming agents-common into a Copier template that generates AI tool configurations from structured data sources, leveraging Copier's proven distribution mechanisms.

## Current State Assessment

**What's Already Implemented:**
- ✅ Product-focused repository structure (`products/claude/`, `products/gemini/`)
- ✅ Jinja2 template system with parameterized paths (`settings.json.jinja`)
- ✅ Python package structure with `agentsmgr` CLI tooling foundation
- ✅ Tag-based versioning strategy (agents-N) in documentation
- ✅ Template variables for extension points (`{{ env_additions }}`, `{{ script_path_prefix }}`)
- ✅ Multi-tool command filtering requirements (Opencode format compatibility)

**Evolution:** Transform from products-based organization to data-driven Copier template generation.

## Implementation Options Analysis

### Option 1: Copier Template Integration (Recommended)

**Architecture:**
```
agents-common/data/ → agentsmgr populate-template → agents-common/template/ → Copier distribution
```

**Strengths:**
- **Proven distribution**: Leverages Copier's mature update and conflict resolution mechanisms
- **Data-driven generation**: Tool configurations generated from structured data sources eliminating format-specific maintenance overhead
- **Multi-tool scaling**: Single data source generates configurations for multiple AI tools with tool-specific formatting
- **Standard workflow**: Projects use familiar `copier update` commands for configuration updates
- **Independent versioning**: Agent configurations version independently from project templates through multi-template support
- **Eliminates duplication**: Tool format variations handled at generation time (e.g., Opencode command filtering)

**Implementation Pattern:**
```python
# agentsmgr populate-template
def populate_template():
    for command_toml in data/commands/:
        command_data = load_toml(command_toml)
        
        # Generate Claude format (full YAML frontmatter)
        write_claude_command(template/claude/commands/, command_data)
        
        # Generate Opencode format (specific YAML frontmatter)
        write_opencode_command(template/opencode/commands/, command_data)
    
    # Generate settings templates with proper paths
    generate_settings_templates()
```

**Repository Structure:**
```
agents-common/
├── data/                           # Source data
│   ├── commands/                  # TOML command definitions
│   ├── agents/                    # Agent definitions  
│   └── scripts/                   # Hook scripts
├── template/                      # Generated Copier template
│   └── .auxiliary/configuration/
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

**Option 1** (Copier Template Integration) provides the optimal balance of proven distribution mechanisms, data-driven generation, and alignment with existing architectural decisions.

### Phase 1: Data Structure and Generation

**Data-to-Template Generation:**
```python
# agentsmgr/commands/populate.py
class PopulateTemplateCommand:
    def populate_template(self, data_path: Path, template_path: Path):
        # Load structured data
        commands = self._load_command_data(data_path / "commands")
        agents = self._load_agent_data(data_path / "agents")
        scripts = self._copy_scripts(data_path / "scripts")
        
        # Generate tool-specific configurations
        self._generate_claude_config(template_path, commands, agents, scripts)
        self._generate_opencode_config(template_path, commands)  # Filtered
        self._generate_gemini_config(template_path, commands)
        
    def _generate_claude_config(self, template_path, commands, agents, scripts):
        # Generate full-format commands with YAML frontmatter
        for cmd in commands:
            write_claude_command(template_path / "claude/commands", cmd)
        
        # Generate settings template with proper paths
        generate_settings_template(template_path / "claude", "claude")
```

**Repository Structure Migration:**
- Transform existing `products/` to `data/` organization
- Generate `template/.auxiliary/configuration/` structure  
- Create `copier.yaml` configuration for template behavior

### Phase 2: Copier Template Configuration

**Create copier.yaml for agents-common:**
```yaml
_min_copier_version: "9.0"
_answers_file: .copier-answers.agents.yml
_subdirectory: template

agent_tools:
    type: str
    help: AI tools to configure
    multiselect: true
    choices:
        - claude
        - opencode  
        - gemini
    default:
        - claude

agents_version:
    type: str
    help: Agent configuration version
    default: "latest"
```

**Project Integration Workflow:**
```bash
# After base project creation
copier copy -a .copier-answers.agents.yml \
  https://github.com/emcd/agents-common.git@agents-3 .

# Updates use standard Copier workflow
copier update -a .copier-answers.agents.yml
```

### Phase 3: Migration and Workflow Integration

**Repository Migration:**
```bash
# In agents-common maintenance workflow
agentsmgr populate-template \
  --source=data \
  --target=template

git add template/ && git commit -m "Generate template from data"
git tag agents-N
```

**Eliminate prepare-agents Complexity:**
- Replace tool-specific hardcoded logic with Copier template application
- Move command filtering logic upstream to template generation
- Projects get standard Copier update workflow

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
- Opencode gets commands with appropriate YAML frontmatter format in template
- Claude gets commands with Claude-specific format in template  
- No more `copy_claude_commands()` logic in prepare-agents
- Projects just apply Copier template with appropriate tool selection

## Technical Advantages

1. **Single Source of Truth**: agents-common becomes the canonical source for all agent configurations
2. **Proven Distribution**: Leverages Copier's mature update and conflict resolution mechanisms  
3. **Data-Driven Generation**: Tool configurations generated from structured data sources eliminating format-specific maintenance overhead
4. **Multi-Tool Scaling**: Single data source generates configurations for multiple AI tools with tool-specific formatting
5. **Standard Workflow**: Projects use familiar `copier update` commands for configuration updates
6. **Independent Versioning**: Agent configurations version independently from project templates through multi-template support
7. **Eliminates Runtime Format Processing**: Tool format variations handled at generation time rather than project setup time
8. **Update Velocity**: Agent configurations can be updated and distributed within hours

## Implementation Phases

### Phase 1: Data Structure Migration
- Transform existing `products/` structure to `data/` organization
- Migrate current configurations to structured TOML data sources
- Core `agentsmgr populate-template` command for data-to-template generation
- Repository structure validation and testing

### Phase 2: Template Generation Logic
- Multi-tool command generation with format-specific handling
- Settings template generation with proper path references
- Tool-specific format generation logic (Opencode-specific YAML frontmatter)
- Template output validation and testing

### Phase 3: Copier Integration
- Create `copier.yaml` configuration for agents-common template
- Multi-template workflow testing with dummy projects
- Integration with existing project structures
- Documentation for multi-template usage patterns

### Phase 4: Workflow Migration
- Tag-based distribution workflow for generated templates
- Migration path for existing projects using prepare-agents
- End-to-end testing across data → template → project pipeline
- Documentation and adoption guides

This approach transforms agents-common into a data-driven Copier template that generates tool configurations from structured sources, eliminating format-specific maintenance overhead while leveraging proven distribution mechanisms.