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
    ├── data/                    # Redistributable data resources
    ├── pyinstaller.spec         # Executable packaging configuration
    └── .auxiliary/              # Development workspace

Source Code Organization
===============================================================================

Package Structure
-------------------------------------------------------------------------------

The main Python package follows the standard ``sources/`` directory pattern:

.. code-block::

    sources/
    ├── agentsmgr/                   # Main Python package
    │   ├── __/                      # Centralized import hub
    │   │   ├── __init__.py          # Re-exports core utilities
    │   │   ├── imports.py           # External library imports
    │   │   └── nomina.py            # agents-common-specific naming constants
    │   ├── _typedecls/              # Type declarations for third-party libraries
    │   ├── commands/                # CLI command implementations subpackage
    │   │   ├── __/                  # Subpackage import hub
    │   │   ├── __.py                # Cascading imports from parent
    │   │   ├── __init__.py          # Command exports
    │   │   ├── base.py              # Base command abstractions
    │   │   ├── detection.py         # Configuration detection logic
    │   │   ├── population.py        # Content population from sources
    │   │   ├── validation.py        # Configuration validation
    │   │   ├── context.py           # Context management
    │   │   ├── generator.py         # Template generation engine
    │   │   ├── operations.py        # File operations
    │   │   └── userdata.py          # User data management
    │   ├── sources/                 # Pluggable source handler subpackage
    │   │   ├── __/                  # Subpackage import hub
    │   │   ├── __.py                # Cascading imports from parent
    │   │   ├── __init__.py          # Source handler exports
    │   │   ├── base.py              # Source handler protocol and registry
    │   │   ├── local.py             # Local filesystem source handler
    │   │   └── git.py               # Git repository source handler with dulwich
    │   ├── renderers/               # Coder-specific renderer subpackage
    │   │   ├── __/                  # Subpackage import hub
    │   │   ├── __.py                # Cascading imports from parent
    │   │   ├── __init__.py          # Renderer registry and exports
    │   │   ├── base.py              # Renderer base class and target modes
    │   │   ├── claude.py            # Claude-specific rendering logic
    │   │   ├── opencode.py          # Opencode-specific rendering logic
    │   │   ├── codex.py             # Codex rendering logic
    │   │   └── qwen.py              # Qwen rendering logic
    │   ├── __init__.py              # Package entry point
    │   ├── py.typed                 # Type checking marker
    │   ├── __main__.py              # CLI entry point for `python -m agentsmgr`
    │   ├── cli.py                   # Command-line interface implementation
    │   ├── exceptions.py            # Package exception hierarchy
    │   ├── core.py                  # Core data structures and globals
    │   └── results.py               # Result handling and data structures


**Architectural Patterns Implemented:**

* **Cascading Subpackage Pattern**: Each subpackage (``commands/``, ``sources/``, ``renderers/``) implements the standard ``__`` import pattern with ``from ..__ import *`` inheritance
* **Plugin Architecture**: Source handlers and renderers use decorator-based registration systems
* **Protocol-Based Design**: AbstractSourceHandler and RendererBase define clear contracts
* **Type Safety**: Comprehensive type annotations with third-party library type stubs

AI Agent Configuration Structure
===============================================================================

Data-Driven Organization
-------------------------------------------------------------------------------

The primary content of this repository is organized under the ``defaults/``
directory, implementing a 3-tier separation for structured agent configurations:

.. code-block::

    defaults/
    ├── configurations/            # Tool-agnostic TOML configurations
    │   ├── commands/              # Command metadata (25+ slash commands)
    │   │   ├── cs-conform-python.toml     # Python code conformance
    │   │   ├── cs-release-final.toml      # Final release management
    │   │   ├── cs-architect.toml          # Architecture documentation
    │   │   ├── cs-code-python.toml        # Python implementation
    │   │   ├── cs-design-python.toml      # Python API design
    │   │   ├── cs-plan-pytests.toml       # Test planning
    │   │   ├── cs-develop-pytests.toml    # Test implementation
    │   │   ├── cs-manage-prd.toml         # Product requirements
    │   │   ├── cs-copier-update.toml      # Template updates
    │   │   ├── validate-custom-slash.toml # Slash command validation
    │   │   └── [20+ additional commands]
    │   └── agents/                # Agent metadata
    │       └── python-conformer.toml      # Python code review agent
    ├── contents/                  # Coder-specific content bodies
    │   ├── commands/
    │   │   ├── claude/            # Claude-specific content (25+ files)
    │   │   │   ├── cs-conform-python.md
    │   │   │   ├── cs-release-final.md
    │   │   │   ├── cs-architect.md
    │   │   │   └── [22+ additional command contents]
    │   │   ├── gemini/            # Gemini-specific content (minimal)
    │   │   └── qwen/              # Qwen-specific content (shares Gemini format)
    │   └── agents/
    │       ├── claude/
    │       │   └── python-conformer.md
    │       ├── opencode/          # Opencode-specific agent content
    │       ├── qwen/              # Qwen-specific agent content
    │       │   └── python-conformer.md
    │       └── gemini/            # Gemini-specific agent content
    ├── user/                      # Per-user files and executables
    │   ├── configurations/        # Per-user global settings
    │   │   └── claude/
    │   │       ├── statusline.py      # Python-based statusline configuration
    │   │       └── settings.json      # Base Claude settings
    │   └── executables/           # Wrapper scripts for user bin directory
    └── templates/                 # Pioneer-named template flavors by coder
        ├── commands/
        │   ├── claude.md.jinja    # Markdown commands (Claude, Opencode, Codex)
        │   └── gemini.toml.jinja  # TOML commands (Gemini, Qwen)
        └── agents/
            ├── claude.md.jinja    # Claude agent format
            ├── opencode.md.jinja  # Opencode agent format
            └── qwen.md.jinja      # Qwen agent format with YAML frontmatter

    data/                          # Additional configuration data
    └── configuration/
        └── general.toml           # General configuration defaults

    template/                      # Copier template for base configuration
    └── .auxiliary/configuration/
        ├── coders/                # Coder-specific base templates
        │   ├── claude/
        │   │   ├── settings.json.jinja   # Claude base settings template
        │   │   ├── .gitignore            # Ignore generated content
        │   │   ├── scripts/              # Hook executables
        │   │   │   ├── pre-bash-python-check
        │   │   │   ├── post-edit-linter
        │   │   │   └── pre-bash-git-commit-check
        │   │   ├── commands/.gitignore   # Generated commands ignored
        │   │   └── agents/.gitignore     # Generated agents ignored
        │   ├── opencode/
        │   │   ├── settings.jsonc.jinja  # Opencode base settings template
        │   │   ├── .gitignore
        │   │   ├── command/.gitignore   # Singular directory name
        │   │   └── agent/.gitignore     # Singular directory name
        │   ├── gemini/
        │   │   ├── settings.json.jinja   # Gemini base settings template
        │   │   ├── .gitignore
        │   │   ├── commands/.gitignore
        │   │   └── agents/.gitignore
        │   └── qwen/
        │       ├── settings.json.jinja   # Qwen base settings template
        │       ├── .gitignore            # Ignore generated content
        │       ├── commands/.gitignore   # Generated commands ignored
        │       └── agents/.gitignore     # Generated agents ignored
        ├── mcp-servers.json.jinja        # Base MCP configuration
        └── {{ _copier_conf.answers_file }}.jinja  # Copier answers template

**Design Principles:**

* **Data-Driven Generation**: Structured TOML configurations drive content generation
* **Clean Separation**: Source data, content bodies, and templates are distinctly organized
* **Plugin Architecture**: Extensible source handlers and renderers via registration patterns
* **Protocol-Based Design**: Clear contracts via AbstractSourceHandler and RendererBase
* **Type Safety**: Comprehensive type annotations with third-party library type stubs
* **Content Specialization**: Currently Claude-focused with extensibility for additional coders
* **Source Flexibility**: Support for local, Git (with @ref), and future source types
* **Global Per-User Files**: Actual implementation includes Python-based statusline configuration

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
    agents-common/defaults/
    ↓ (agentsmgr populate project --source=agents-common@agents-N)
    target-project/.auxiliary/configuration/coders/[tool]/commands/
    target-project/.auxiliary/configuration/coders/[tool]/agents/

    ↓ (agentsmgr populate user --source=agents-common@agents-N)
    ~/.config/[tool]/            # Per-user configuration files
    ~/.local/bin/                # Wrapper executables

**Template-of-Templates Generation:**

Content generation combines structured sources with generic templates:

.. code-block::

    # Source Data Structure
    defaults/configurations/commands/cs-release-final.toml  (metadata)
    + defaults/contents/commands/claude/cs-release-final.md  (content body)
    + defaults/templates/command.md.jinja                    (format template)
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

    agents-common (defaults/ + template/)
    ↓ (tag: agents-N)
    agentsmgr populate --source=agents-common@agents-N
    ↓ (git fetch + template rendering)
    target-project (.auxiliary/configuration/)

Component Integration
===============================================================================

CLI Integration Patterns
-------------------------------------------------------------------------------

The ``agentsmgr`` package provides comprehensive CLI tooling with pluggable architecture:

**Core Commands:**

* ``agentsmgr detect``: Configuration detection and analysis
* ``agentsmgr populate``: Dynamic content generation from sources
* ``agentsmgr validate``: Configuration validation and diagnostics

**Architecture Patterns:**

.. code-block::

    CLI Architecture:
    ├── cli.py                     # Tyro-based CLI with async support
    ├── core.py                    # Global state and display options
    ├── commands/                  # Command implementation subpackage
    │   ├── base.py               # Abstract command protocols
    │   ├── detection.py          # Configuration auto-detection
    │   ├── population.py         # Source-to-target content generation
    │   ├── validation.py         # Configuration validation
    │   ├── context.py            # Context management and resolution
    │   ├── generator.py          # Template generation engine
    │   ├── operations.py         # File system operations
    │   └── userdata.py           # User data management
    ├── sources/                   # Pluggable source handlers
    │   ├── base.py               # Source handler protocol and registry
    │   ├── local.py              # Local filesystem sources
    │   └── git.py                # Git repository sources (with @ref support)
    └── renderers/                 # Coder-specific output formatting
        ├── base.py               # Target mode management and path resolution
        ├── claude.py             # Claude-specific rendering
        ├── opencode.py           # Opencode-specific rendering
        ├── codex.py              # Codex rendering
        └── qwen.py               # Qwen rendering

**Key Integration Features:**

* **Git Source Resolution**: Full ``source@ref#subdir`` syntax with latest tag fallback
* **Plugin Registration**: Decorator-based handler registration for extensibility
* **Configuration Detection**: Automatic discovery of Copier answers and project settings
* **Template System**: Jinja2-based rendering with metadata normalization
* **Target Mode Support**: per-user, per-project targeting with environment overrides
* **Type Safety**: Comprehensive type annotations with protocol-based design

**Integration Workflows:**

* **Source Resolution**: ``github:org/repo@v1.0#subdir`` → local filesystem path
* **Content Generation**: TOML metadata + markdown content + Jinja2 template → coder-specific files
* **Configuration Management**: Auto-detection → validation → population → output
* **Plugin Extension**: Custom sources and renderers via registration decorators

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
