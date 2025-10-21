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

The system uses a hybrid Copier + agentsmgr approach with clean data separation.
For detailed directory organization and file structure, see :doc:`filesystem`.

**Key Design Principles:**

* **Data-Driven Generation**: Structured TOML configurations drive content generation
* **Clean Separation**: Source data, content bodies, and templates are distinctly organized
* **Hybrid Distribution**: Copier provides base templates, agentsmgr provides dynamic content
* **Plugin Architecture**: Extensible source handlers and renderers via registration patterns
* **Protocol-Based Design**: Clear contracts via AbstractSourceHandler and RendererBase
* **Type Safety**: Comprehensive type annotations with third-party library type stubs

Template-Based Content Generation System
-------------------------------------------------------------------------------

The system implements a template-of-templates architecture for dynamic content generation:

**Source Data Structure** (``defaults/configurations/``):
- TOML files contain tool-agnostic metadata following project standards
- 25+ slash commands with comprehensive metadata definitions
- Agent definitions with tool-specific rendering configuration

**Content Bodies** (``defaults/contents/``):
- Coder-specific content without frontmatter for maximum reusability
- Currently Claude-focused with extensive command library
- Extensible structure for additional AI coding assistants

**Generic Templates** (``defaults/templates/``):
- Jinja2 templates combine metadata + content for each tool format
- Variable normalization: hyphen→underscore for template access
- Support for markdown and TOML output formats

**Additional Configuration** (``data/``):
- General configuration defaults and system-wide settings
- Extensible for future configuration needs

**Base Configuration Templates** (``template/``):
- Copier template for settings.json.jinja and directory structure
- Hook scripts for pre/post tool use validation
- .gitignore files prevent committing generated content
- Multi-coder support (Claude, Opencode, Gemini base templates)

Hybrid Distribution Architecture
-------------------------------------------------------------------------------

The system uses a hybrid approach combining Copier templates and dynamic generation:

**Tag-Based Source Versioning**:
- Repository uses ``agents-N`` tag versioning scheme (agents-1, agents-2, etc.)
- Enables atomic, consistent data source distribution
- Source data tagged independently from project templates

**Copier Template Integration**:
- Minimal template provides base configuration and directory structure
- Standard Copier workflows for multi-template projects
- Base settings templates distributed via proven mechanisms
- Hook scripts for pre/post tool use validation

**Dynamic Content Generation**:
- ``agentsmgr populate --source=agents-common@agents-N`` generates tool-specific content
- Content generated directly in downstream projects from git source
- Configuration detection from Copier answers or defaults
- Generated content ignored via .gitignore (not committed)

**Plugin-Based Source Resolution**:
- Git source handler supports full ``source@ref#subdir`` syntax
- Local filesystem source handler for development workflows
- Decorator-based registration system for extensible source types
- Latest tag fallback when no explicit ref specified

Component Relationships
===============================================================================

Hybrid Distribution Flow Architecture
-------------------------------------------------------------------------------

The system implements a dual-channel distribution model:

1. **Source Data Repository** (agents-common):
   - Maintains structured data sources in ``defaults/`` directory
   - Provides minimal Copier template for base configuration
   - Tags releases for atomic data source distribution

2. **Base Template Distribution** (Copier):
   - ``template/`` provides base settings templates and directory structure
   - Standard Copier multi-template workflow integration
   - Handles MCP server configurations and hook script distribution

3. **Dynamic Content Generation** (agentsmgr):
   - Fetches tagged data sources from git repositories
   - Generates tool-specific commands and agents in target projects
   - Plugin-based source resolution with @ref syntax support

4. **Coder-Specific Rendering** (agentsmgr.renderers):
   - Claude renderer with per-user and per-project targeting
   - Opencode, Codex, and Qwen renderers for multi-tool support
   - Base renderer class defining target mode contracts and template flavor selection

5. **Target Projects**:
   - Base configuration from Copier template distribution
   - Dynamic content generated by agentsmgr populate command
   - Generated content ignored via .gitignore patterns
   - Final settings rendered from base templates with parameterized paths

Data Flow Patterns
-------------------------------------------------------------------------------

**Source Data Distribution Flow**:

.. code-block::

    agents-common (defaults/) → Tag Release (agents-N) →
    agentsmgr populate →
    Target Projects (.auxiliary/configuration/)

**Base Template Distribution Flow**:

.. code-block::

    agents-common (template/) → Copier Distribution →
    Target Projects (.auxiliary/configuration/)

**Content Generation Flow**:

.. code-block::

    TOML Configuration (metadata) +
    Coder Content (body) +
    Generic Template (format) →
    agentsmgr populate →
    Tool-Specific Files

**Settings Generation Flow**:

.. code-block::

    Base Template (settings.json.jinja) +
    Copier Variables (project-specific) →
    Copier Rendering →
    Final Settings (settings.json)

**Command Execution Flow**:

.. code-block::

    Slash Command →
    Generated File (.auxiliary/configuration/) →
    Hook Script (from Copier template) →
    Execution

Key Architectural Patterns
===============================================================================

Plugin Architecture Pattern
-------------------------------------------------------------------------------

The architecture implements extensible plugin systems for core functionality:

**Source Handler Plugins** (``agentsmgr.sources``):
- Protocol-based AbstractSourceHandler contract
- Decorator-based registration system (@source_handler)
- Git handler with @ref syntax and latest tag fallback
- Local filesystem handler for development workflows

**Renderer Plugins** (``agentsmgr.renderers``):
- RendererBase class defining target mode contracts
- Coder-specific rendering logic (Claude, Opencode, Codex)
- Target mode validation and path resolution
- Registry-based lookup and instantiation

Template-Based Content Generation
-------------------------------------------------------------------------------

The system employs sophisticated template patterns for dynamic content generation:

**Metadata + Content + Template Pattern**:
- TOML configurations provide tool-agnostic metadata
- Coder-specific content bodies maintain separation of concerns
- Jinja2 templates combine metadata and content for target format

**Variable Normalization Pattern**:
- Hyphenated TOML keys → underscore template variables
- Semantic tool mapping with coder object abstractions
- Type-safe template rendering with comprehensive annotations

Protocol-Based Design
-------------------------------------------------------------------------------

The architecture emphasizes clear contracts and type safety:

**Protocol Interfaces**: AbstractSourceHandler and RendererBase define clear contracts
**Type Annotations**: Comprehensive type hints with third-party library stubs
**Immutable Objects**: Extensive use of immutable dataclasses and protocols
**Async Support**: Native async/await patterns throughout CLI and command implementations

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