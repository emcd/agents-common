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
Filesystem Organization
*******************************************************************************

This document describes the specific filesystem organization for the project,
showing how the standard organizational patterns are implemented for this
project's configuration. For the underlying principles and rationale behind
these patterns, see the `common architecture documentation
<https://raw.githubusercontent.com/emcd/python-project-common/refs/tags/docs-1/documentation/common/architecture.rst>`_.

Project Structure
===============================================================================

Root Directory Organization
-------------------------------------------------------------------------------

The project implements the standard filesystem organization:

.. code-block::

    agents-common/
    ├── LICENSE.txt              # Project license
    ├── README.rst               # Project overview and quick start
    ├── pyproject.toml           # Python packaging and tool configuration
    ├── documentation/           # Sphinx documentation source
    ├── sources/                 # All source code
    ├── tests/                   # Test suites
    ├── pyinstaller.spec         # Executable packaging configuration
    └── .auxiliary/              # Development workspace

Source Code Organization
===============================================================================

Package Structure
-------------------------------------------------------------------------------

The main Python package follows the standard ``sources/`` directory pattern:

.. code-block::

    sources/
    ├── agentsmgr/          # Main Python package
    │   ├── __/                      # Centralized import hub
    │   │   ├── __init__.py          # Re-exports core utilities
    │   │   ├── imports.py           # External library imports
    │   │   └── nomina.py            # agents-common-specific naming constants
    │   ├── __init__.py              # Package entry point
    │   ├── py.typed                 # Type checking marker
    │   ├── __main__.py              # CLI entry point for `python -m agentsmgr`
    │   ├── cli.py                   # Command-line interface implementation
    │   ├── exceptions.py            # Package exception hierarchy
    │   └── [modules].py             # Feature-specific modules


All package modules use the standard ``__`` import pattern as documented
in the common architecture guide.

AI Agent Configuration Structure
===============================================================================

Data-Driven Organization
-------------------------------------------------------------------------------

The primary content of this repository is organized under the ``data/``
directory, implementing a 3-tier separation for structured agent configurations:

.. code-block::

    data/
    ├── configurations/            # Tool-agnostic TOML configurations
    │   ├── commands/              # Command metadata
    │   │   ├── cs-conform-python.toml
    │   │   └── cs-release-final.toml
    │   └── agents/                # Agent metadata
    │       └── python-conformer.toml
    ├── contents/                  # Coder-specific content bodies
    │   ├── commands/
    │   │   ├── claude/            # Claude-specific content
    │   │   │   ├── cs-conform-python.md
    │   │   │   └── cs-release-final.md
    │   │   ├── opencode/          # Falls back to/from claude/
    │   │   └── gemini/            # No fallback - different syntax
    │   └── agents/
    │       ├── claude/
    │       │   └── python-conformer.md
    │       ├── opencode/          # Falls back to/from claude/
    │       └── gemini/            # No fallback - different syntax
    └── templates/                 # Generic, reusable templates
        ├── command.md.jinja       # For Claude/Opencode commands
        ├── command.toml.jinja     # For Gemini commands
        ├── agent.md.jinja         # For Claude/Opencode agents
        └── agent.toml.jinja       # For Gemini agents

    template/                      # Minimal Copier template for base configuration
    └── .auxiliary/configuration/
        ├── claude/
        │   ├── commands/.gitignore    # Ignore generated content
        │   ├── agents/.gitignore
        │   ├── scripts/              # Hook executables
        │   └── settings.json.jinja   # Base template
        ├── opencode/
        │   ├── commands/.gitignore
        │   └── agents/.gitignore
        ├── gemini/
        │   ├── commands/.gitignore
        │   └── agents/.gitignore
        └── mcp-servers.json.jinja     # Base MCP configuration

**Design Principles:**

* **Data-Driven Generation**: Structured TOML configurations drive content generation
* **Clean Separation**: Source data, content bodies, and templates are distinctly organized
* **Tool-Agnostic Sources**: Configurations work across multiple AI coding tools
* **Content Fallback Strategy**: Claude ↔ Opencode compatibility, Gemini isolation
* **Semantic Tool Mapping**: allowed-tools specifications map to tool-specific syntax
* **Minimal Base Distribution**: Copier provides only essential templates and structure

Distribution and Integration Patterns
-------------------------------------------------------------------------------

**Hybrid Distribution Architecture:**

The system uses dual-channel distribution combining Copier templates and dynamic generation:

.. code-block::

    # Base Template Distribution (Copier)
    agents-common/template/
    ↓ (copier copy)
    target-project/.auxiliary/configuration/

    # Dynamic Content Generation (agentsmgr)
    agents-common/data/
    ↓ (agentsmgr populate --source=agents-common@agents-N)
    target-project/.auxiliary/configuration/[tool]/commands/
    target-project/.auxiliary/configuration/[tool]/agents/

**Template-of-Templates Generation:**

Content generation combines structured sources with generic templates:

.. code-block::

    # Source Data Structure
    data/configurations/commands/cs-release-final.toml  (metadata)
    + data/contents/commands/claude/cs-release-final.md  (content body)
    + data/templates/command.md.jinja                    (format template)
    ↓ (agentsmgr populate)
    target/.auxiliary/configuration/claude/commands/cs-release-final.md

**Configuration Normalization:**

Variable transformation for template access:

.. code-block::

    # TOML Source (hyphenated keys)
    argument-hint = 'major.minor'
    allowed-tools = 'git-release-standard'

    # Template Variables (underscore keys)
    {{ argument_hint }}  # 'major.minor'
    {{ allowed_tools }}  # ['Edit', 'Bash(git:*)', ...]
    {{ coder.name }}     # 'claude'

**Tag-Based Source Distribution:**

.. code-block::

    agents-common (data/ + template/)
    ↓ (tag: agents-N)
    agentsmgr populate --source=agents-common@agents-N
    ↓ (git fetch + template rendering)
    target-project (.auxiliary/configuration/)

Component Integration
===============================================================================

CLI Integration Patterns
-------------------------------------------------------------------------------

The ``agentsmgr`` package provides CLI tooling for dynamic content generation:

.. code-block::

    sources/agentsmgr/
    ├── __/                         # Import hub following standard pattern
    │   ├── __init__.py            # Re-exports core utilities
    │   ├── imports.py             # External library imports
    │   └── nomina.py              # Project-specific naming constants
    ├── __init__.py                # Package entry point
    ├── py.typed                   # Type checking marker
    └── [modules].py               # CLI command implementations

**Primary Integration Points:**

* ``agentsmgr populate``: Dynamic content generation from git sources
* Configuration detection: Copier answers file or default fallback
* Template rendering: TOML metadata + content bodies + Jinja2 templates → tool-specific files
* Content fallback: Claude ↔ Opencode compatibility, Gemini isolation
* Semantic tool mapping: allowed-tools specifications → coder-specific syntax

**Integration Workflows:**

* **New Projects**: Copier template + automatic agentsmgr populate via hooks
* **Agent Updates**: ``copier update`` + ``agentsmgr populate --source=agents-N``
* **Manual Population**: ``agentsmgr populate`` (works in any project structure)

Development Workspace Integration
-------------------------------------------------------------------------------

Development-specific organization follows standard ``.auxiliary/`` patterns:

.. code-block::

    .auxiliary/
    ├── configuration/              # Current structure for downstream projects
    ├── instructions/               # Development practices and architecture guides
    ├── notes/                      # Development notes and planning documents
    └── scribbles/                  # Temporary development files

The ``.auxiliary/configuration/`` structure remains the standard deployment target
for downstream projects. The change is that agentic coder configurations will now
be generated by agentsmgr rather than distributed from python-project-common.

Architecture Evolution
===============================================================================

This filesystem organization provides a foundation that architect agents can
evolve as the project grows. For questions about organizational principles,
subpackage patterns, or testing strategies, refer to the comprehensive common
documentation:

* `Architecture Patterns <https://raw.githubusercontent.com/emcd/python-project-common/refs/tags/docs-1/documentation/common/architecture.rst>`_
* `Development Practices <https://raw.githubusercontent.com/emcd/python-project-common/refs/tags/docs-1/documentation/common/practices.rst>`_
* `Test Development Guidelines <https://raw.githubusercontent.com/emcd/python-project-common/refs/tags/docs-1/documentation/common/tests.rst>`_
