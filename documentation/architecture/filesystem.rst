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
    │   └── [modules].py             # Feature-specific modules
    

All package modules use the standard ``__`` import pattern as documented
in the common architecture guide.

AI Agent Configuration Structure
===============================================================================

Product-Focused Organization
-------------------------------------------------------------------------------

The primary content of this repository is organized under the ``products/`` 
directory, implementing a product-focused structure for AI agent configurations:

.. code-block::

    products/
    ├── claude/                     # Claude Code configurations
    │   ├── agents/                 # Subagent definitions
    │   │   └── python-conformer.md
    │   ├── commands/               # Slash commands
    │   │   ├── cs-annotate-release.md
    │   │   ├── cs-architect.md
    │   │   ├── cs-code-python.md
    │   │   └── [15+ additional commands]
    │   ├── configuration/          # Settings templates  
    │   │   └── settings.json.jinja
    │   ├── miscellany/             # Templates and snippets
    │   │   └── command-template.md
    │   └── scripts/                # Hook executables
    │       ├── post-edit-linter
    │       └── pre-bash-python-check
    └── gemini/                     # Gemini CLI configurations
        ├── commands/               # Command definitions
        │   └── settings.json
        └── configuration/          # Settings templates
            └── settings.json.jinja

**Design Principles:**

* **Product Organization**: Each AI tool maintains dedicated directory structure
* **Resource Consolidation**: All tool-specific resources centralized per product  
* **Consistent Taxonomy**: Latin-derived directory naming maintains linguistic consistency
* **Extensible Structure**: New AI tools integrate without restructuring existing content

Distribution and Integration Patterns
-------------------------------------------------------------------------------

**Template-Based Settings Distribution:**

The system uses Jinja2 templates for flexible configuration generation:

.. code-block::

    products/[tool]/configuration/settings.json.jinja
    ↓ (CLI rendering with local overrides)
    target-project/.auxiliary/configuration/[tool]/settings.json

**Path Coordination Strategy:**

Commands and templates reference downstream deployment paths:

.. code-block::

    # In distributed commands
    @.auxiliary/configuration/claude/miscellany/command-template.md
    
    # In settings templates  
    "command": "{{ script_path_prefix }}/claude/post-edit-linter"

**Tag-Based Release Distribution:**

.. code-block::

    agents-common (products/) 
    ↓ (tag: agents-N)
    python-project-common (template references)
    ↓ (copier instantiation) 
    target-project (.auxiliary/configuration/)

Component Integration
===============================================================================

CLI Integration Patterns
-------------------------------------------------------------------------------

The ``agentsmgr`` package provides CLI tooling for configuration management:

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

* ``prepare-llm-agents``: Environment setup from tagged releases
* Template rendering: Base templates + local overrides → final settings
* Path resolution: Parameterized paths → environment-specific references

Development Workspace Integration
-------------------------------------------------------------------------------

Development-specific organization follows standard ``.auxiliary/`` patterns:

.. code-block::

    .auxiliary/
    ├── configuration/              # Legacy structure (will be deprecated) 
    ├── instructions/               # Development practices and architecture guides
    ├── notes/                      # Development notes and planning documents
    └── scribbles/                  # Temporary development files

The legacy ``.auxiliary/configuration/`` structure is maintained during transition 
but will be deprecated as the ``products/`` structure becomes the authoritative 
source.

Architecture Evolution
===============================================================================

This filesystem organization provides a foundation that architect agents can
evolve as the project grows. For questions about organizational principles,
subpackage patterns, or testing strategies, refer to the comprehensive common
documentation:

* `Architecture Patterns <https://raw.githubusercontent.com/emcd/python-project-common/refs/tags/docs-1/documentation/common/architecture.rst>`_
* `Development Practices <https://raw.githubusercontent.com/emcd/python-project-common/refs/tags/docs-1/documentation/common/practices.rst>`_
* `Test Development Guidelines <https://raw.githubusercontent.com/emcd/python-project-common/refs/tags/docs-1/documentation/common/tests.rst>`_
