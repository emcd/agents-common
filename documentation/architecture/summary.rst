.. vim: set fileencoding=utf-8:
.. -*- coding: utf-8 -*-
.. +--------------------------------------------------------------------------+
   |                                                                          |
   | Licensed under the Apache License, Version 2.0 (the "License");          |
   | you may not use this file except in compliance with the License.         |
   | You may obtain a copy of the License at                                  |
   |                                                                          |
   |     http://www.apache.org/licenses/LICENSE-2.0                           |
   |                                                                          |
   | Unless required by applicable law or agreed to in writing, software      |
   | distributed under the License is distributed on an "AS IS" BASIS,        |
   | WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. |
   | See the License for the specific language governing permissions and      |
   | limitations under the License.                                           |
   |                                                                          |
   +--------------------------------------------------------------------------+


*******************************************************************************
System Overview
*******************************************************************************

The emcd-agents-common repository implements a centralized AI agent configuration 
management system that provides version-controlled, template-based distribution 
of configurations for multiple AI development tools. The architecture enables 
rapid iteration on agent configurations while maintaining consistency across 
multiple project templates and ensuring clean separation between project 
structure and evolving agent content.

System Purpose
===============================================================================

The system addresses critical problems in AI agent configuration management:

* **Heavyweight Configuration Updates**: Eliminates the need for full project 
  template releases when updating AI agent configurations
* **Configuration Drift**: Provides single source of truth preventing 
  inconsistency between template and production configurations  
* **Distribution Coordination**: Solves path coordination problems between 
  distributed configurations and hook scripts
* **Multi-Tool Scaling**: Supports extensible architecture for multiple AI 
  development environments

Major Components
===============================================================================

Configuration Repository Structure
-------------------------------------------------------------------------------

The system uses a product-focused organizational structure:

.. code-block::

    products/
    ├── claude/                 # Claude Code configurations
    │   ├── agents/            # Subagent definitions  
    │   ├── commands/          # Slash commands
    │   ├── miscellany/        # Templates and snippets
    │   ├── scripts/           # Hook executables
    │   └── configuration/     # Settings templates
    └── gemini/                # Gemini CLI configurations
        ├── commands/          # Command definitions
        └── configuration/     # Settings templates

**Key Design Principles:**

* **Product Organization**: Each AI tool has dedicated directory structure
* **Resource Consolidation**: All tool-specific resources centralized per product
* **Consistent Taxonomy**: Latin-derived directory naming maintains linguistic consistency
* **Extensible Structure**: New AI tools integrate without restructuring existing content

Template-Based Configuration System
-------------------------------------------------------------------------------

The system implements a Jinja2-based template architecture for settings distribution:

**Configuration Templates** (``*.json.jinja``):
- Base templates handle tool-specific hook configurations
- Reference hook script paths that coordinate with distributed executables
- Support parameterized customization through template variables

**Local Override Mechanism**:
- Projects can provide ``local.toml`` files for project-specific extensions
- CLI tooling merges base templates with local overrides
- Avoids duplicating Copier's templating functionality

**Path Coordination Strategy**:
- Commands reference ``.auxiliary/configuration/`` paths for downstream compatibility
- Hook scripts function correctly when deployed to target project structure
- Template references remain valid after distribution

Distribution and Release Management
-------------------------------------------------------------------------------

The system uses a tag-based release workflow for lightweight configuration updates:

**Tag-Based Versioning**:
- Repository uses ``agents-N`` tag versioning scheme (agents-1, agents-2, etc.)
- Enables atomic, consistent configuration deployment
- Provides rollback capability through tag references

**CLI Integration**:  
- ``agentsmgr prepare-llm-agents`` command handles environment setup
- CLI tooling can pull from specific tagged versions
- Downstream projects can pin to known-good configuration versions

**GitHub Actions Workflow**:
- Publishing workflow automatically deploys tagged releases
- Configuration distribution completes within minutes of tag creation
- Supports standard git workflow practices and CI/CD pipelines

Component Relationships
===============================================================================

Configuration Flow Architecture
-------------------------------------------------------------------------------

The system implements a hub-and-spoke distribution model:

1. **Central Repository** (agents-common): 
   - Maintains authoritative configurations for all AI tools
   - Consolidates hook scripts, commands, templates, and settings
   - Tags releases for atomic distribution

2. **Template Integration** (python-project-common):
   - References tagged releases from agents-common repository
   - Copier templates generate project-specific MCP configurations
   - Handles conditional logic and project-specific customization

3. **Target Projects**:
   - Receive distributed configurations in ``.auxiliary/configuration/`` structure
   - CLI tooling renders final settings from base templates + local overrides
   - Hook scripts execute with correct path references

Data Flow Patterns
-------------------------------------------------------------------------------

**Configuration Distribution Flow**:

.. code-block::

    agents-common (products/) → Tag Release → 
    python-project-common (references) → 
    Target Projects (.auxiliary/configuration/)

**Settings Generation Flow**:

.. code-block::

    Base Template (settings.json.jinja) + 
    Local Overrides (local.toml) → 
    CLI Rendering → 
    Final Settings (settings.json)

**Command Execution Flow**:

.. code-block::

    Slash Command → 
    Reference (.auxiliary/configuration/) → 
    Template/Hook Script → 
    Execution

Key Architectural Patterns
===============================================================================

Separation of Concerns
-------------------------------------------------------------------------------

The architecture implements clear boundaries between different types of configuration:

**Static Project Structure** (Copier Templates):
- MCP server configurations (``mcp-servers.json.jinja``)
- Project-specific settings variations
- Conditional generation logic

**Dynamic Agent Content** (agents-common):
- Slash commands that evolve rapidly
- Subagent definitions requiring iteration
- Hook scripts with coordinated path references
- Base settings templates

Template-Based Configuration Management
-------------------------------------------------------------------------------

The system employs template-based patterns for flexible configuration generation:

**Base + Override Pattern**:
- Base templates provide consistent foundation
- Local overrides enable project-specific customization  
- Rendering process combines both sources

**Path Abstraction Pattern**:
- Templates use parameterized path references
- CLI tooling resolves paths for target environment
- Enables consistent deployment across different project structures

Extensible Product Architecture
-------------------------------------------------------------------------------

The product-focused organization supports clean extensibility:

**Product Isolation**: Each AI tool maintains independent directory structure
**Shared Resources**: Common elements (MCP servers) available across products
**Consistent Interface**: New tools follow established organizational patterns

Deployment Architecture
===============================================================================

The system supports distributed deployment across multiple project environments:

**Development Environment**:
- Direct integration with agents-common repository
- Live configuration updates through git operations
- Development tooling for testing configuration changes

**Template Generation**:  
- Copier templates reference tagged releases
- Automated pulling of configuration content during template instantiation
- Version pinning for stable project generation

**Production Projects**:
- Configurations deployed to standard ``.auxiliary/configuration/`` structure
- CLI tooling handles rendering and local customization
- Hook scripts execute with environment-appropriate paths

Quality Attributes
===============================================================================

Performance Characteristics
-------------------------------------------------------------------------------

* **Distribution Performance**: Configuration updates deploy within 5 minutes of tag creation
* **CLI Performance**: Setup commands execute within 30 seconds for typical project sizes  
* **Repository Efficiency**: Repository size remains manageable (< 100MB) for rapid cloning

Reliability and Consistency
-------------------------------------------------------------------------------

* **Atomic Distribution**: Tag-based releases provide consistent configuration deployment
* **Version Rollback**: Previous configurations accessible through tag references
* **Path Coordination**: Template system ensures hook scripts resolve correctly

Maintainability and Evolution  
-------------------------------------------------------------------------------

* **Single Source of Truth**: Eliminates configuration drift through centralization
* **Clean Extension**: New AI tools integrate without restructuring existing content
* **Template Flexibility**: Jinja2 templates support customization without complexity

Future Evolution Paths
===============================================================================

The architecture supports anticipated evolution patterns:

**Multi-Language Templates**: Architecture ready for Rust and other language-specific templates sharing same agent configurations

**Additional AI Tools**: Product-focused organization scales cleanly to Opencode, Cursor, and future AI development environments  

**Enhanced Distribution**: Template system can evolve to support more sophisticated customization patterns while maintaining backward compatibility

**CLI Enhancement**: Agent management tooling can expand functionality while preserving core distribution workflow