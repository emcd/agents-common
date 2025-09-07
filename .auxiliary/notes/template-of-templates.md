# Template-of-Templates Architecture

## Overview

The `agentsmgr template populate` command uses a template-of-templates approach to generate tool-specific configurations from structured data sources. This architecture separates source data from format-specific templates, enabling clean generation of configurations for multiple AI coding tools.

## Architecture

### Directory Structure

```
data/
├── commands/
│   ├── cs-release-final.toml          # Source data
│   ├── cs-conform-python.toml
│   └── ...
├── agents/
│   ├── python-conformer.toml
│   └── ...
├── scripts/
│   ├── pre-bash-python-check
│   ├── post-edit-linter
│   └── ...
└── templates/                         # Tool-specific templates  
    ├── claude/
    │   ├── command.md.jinja           # Claude command template
    │   ├── agent.md.jinja             # Claude agent template
    │   └── settings.json.jinja        # Claude settings template
    ├── opencode/
    │   ├── command.md.jinja           # Opencode command template (different frontmatter)
    │   └── settings.json.jinja        # Opencode settings template
    └── gemini/
        ├── command.toml.jinja         # Gemini uses TOML format
        └── settings.json.jinja        # Gemini settings template
```

### Source Data Format

**Command Data Example:**
```toml
# data/commands/cs-release-final.toml
name = "Release Final"
description = "Finalize release process and publish"
category = "release"

[examples]
python = "hatch build && hatch publish"
rust = "cargo publish"

[claude_specific]
argument_hints = ["--dry-run", "--skip-tests"]
allowed_tools = ["Bash", "Read", "Edit"]

[opencode_specific]
# Different frontmatter structure
context_files = ["pyproject.toml", "Cargo.toml"]
```

**Agent Data Example:**
```toml
# data/agents/python-conformer.toml
name = "Python Conformer"
description = "Review and improve Python code for conformance"

[claude_specific]
system_prompt = "You are a Python code reviewer focused on style and standards."
tools = ["Read", "Edit", "MultiEdit", "Bash"]

[gemini_specific]
# Gemini agent format differs from Claude
model = "gemini-pro"
temperature = 0.1
```

### Tool Templates Handle Format Differences

**Claude Command Template:**
```jinja2
<!-- data/templates/claude/command.md.jinja -->
---
argument-hints: {{ claude_specific.argument_hints | join(", ") }}
allowed-tools: {{ claude_specific.allowed_tools | join(", ") }}
---

# {{ name }}

{{ description }}

## Example Usage
{% for lang in languages %}
{% if examples[lang] %}
**{{ lang | title }}:**
```bash
{{ examples[lang] }}
```
{% endif %}
{% endfor %}
```

**Opencode Command Template:**
```jinja2
<!-- data/templates/opencode/command.md.jinja -->  
---
context-files: {{ opencode_specific.context_files | join(", ") }}
---

# {{ name }}

{{ description }}

## Example Usage
{% for lang in languages %}
{% if examples[lang] %}
**{{ lang | title }}:**
```bash
{{ examples[lang] }}
```
{% endif %}
{% endfor %}
```

**Gemini Command Template:**
```jinja2
# data/templates/gemini/command.toml.jinja
name = "{{ name }}"
description = "{{ description }}"

{% for lang in languages %}
{% if examples[lang] %}
[examples.{{ lang }}]
command = "{{ examples[lang] }}"
{% endif %}
{% endfor %}
```

## Command Implementation

```python
# agentsmgr template populate
class TemplatePopulator:
    def populate(self, data_dir: Path, template_dir: Path, target_dir: Path, 
                 selected_coders: List[str], selected_languages: List[str]):
        for coder in selected_coders:  # from copier answers
            self._populate_coder(coder, data_dir, template_dir, target_dir, selected_languages)
    
    def _populate_coder(self, coder: str, data_dir: Path, template_dir: Path, 
                       target_dir: Path, selected_languages: List[str]):
        # Load tool-specific templates
        templates = self._load_coder_templates(template_dir / coder)
        
        # Generate commands
        for command_file in (data_dir / "commands").glob("*.toml"):
            command_data = load_toml(command_file)
            rendered = templates["command"].render(
                **command_data, 
                languages=selected_languages
            )
            output_path = target_dir / coder / "commands" / f"{command_file.stem}.md"
            write_file(output_path, rendered)
        
        # Generate agents (if applicable for this coder)
        if (template_dir / coder / "agent.md.jinja").exists():
            for agent_file in (data_dir / "agents").glob("*.toml"):
                agent_data = load_toml(agent_file)
                rendered = templates["agent"].render(
                    **agent_data,
                    languages=selected_languages
                )
                output_path = target_dir / coder / "agents" / f"{agent_file.stem}.md"
                write_file(output_path, rendered)
        
        # Generate settings template
        settings_data = self._build_settings_context(coder, selected_languages)
        rendered = templates["settings"].render(**settings_data)
        output_path = target_dir / coder / "settings.json.jinja"
        write_file(output_path, rendered)
        
        # Copy scripts (language-specific)
        self._copy_scripts(data_dir / "scripts", target_dir / coder / "scripts", selected_languages)

    def _load_coder_templates(self, template_path: Path) -> Dict[str, Template]:
        """Load all Jinja2 templates for a specific coder."""
        templates = {}
        for template_file in template_path.glob("*.jinja"):
            template_name = template_file.stem.split('.')[0]  # command.md.jinja -> command
            templates[template_name] = Template(template_file.read_text())
        return templates
    
    def _build_settings_context(self, coder: str, languages: List[str]) -> Dict[str, Any]:
        """Build context for settings template rendering."""
        return {
            "script_path_prefix": f".auxiliary/configuration/{coder}/scripts",
            "languages": languages,
            "coder": coder
        }
    
    def _copy_scripts(self, source_dir: Path, target_dir: Path, languages: List[str]):
        """Copy and potentially customize scripts based on selected languages."""
        target_dir.mkdir(parents=True, exist_ok=True)
        
        for script in source_dir.glob("*"):
            # Language-specific script selection logic
            if "python" in script.name and "python" not in languages:
                continue
            if "rust" in script.name and "rust" not in languages:
                continue
                
            shutil.copy2(script, target_dir / script.name)
```

## Benefits

### Clean Separation
- **Source data** contains semantic information in tool-agnostic format
- **Templates** handle tool-specific format requirements  
- **Generated output** optimized for each tool's expectations

### Format Evolution Support
- Claude and Opencode frontmatter can diverge over time
- Gemini's TOML agent specifications vs Claude's Markdown
- New tools can be added with new template sets

### Language-Aware Generation
- Commands show appropriate examples for selected languages
- Scripts are filtered based on language selection
- Settings templates reference correct language-specific tools

### Tool-Specific Customization
- Each tool gets format-appropriate configuration
- Tool-specific metadata sections in source data
- Templates can implement tool-unique features

### Future Extensibility
- New AI tools: add template directory and extend copier choices
- New languages: extend data examples and script logic
- New configuration types: add new template files

This architecture enables agents-common to scale cleanly across multiple AI coding tools while maintaining single-source-of-truth for configuration content.