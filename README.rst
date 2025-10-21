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
                                  emcd-agents
*******************************************************************************

.. image:: https://img.shields.io/pypi/v/emcd-agents
   :alt: Package Version
   :target: https://pypi.org/project/emcd-agents/

.. image:: https://img.shields.io/pypi/status/emcd-agents
   :alt: PyPI - Status
   :target: https://pypi.org/project/emcd-agents/

.. image:: https://github.com/emcd/agents-common/actions/workflows/tester.yaml/badge.svg?branch=master&event=push
   :alt: Tests Status
   :target: https://github.com/emcd/agents-common/actions/workflows/tester.yaml

.. image:: https://emcd.github.io/agents-common/coverage.svg
   :alt: Code Coverage Percentage
   :target: https://github.com/emcd/agents-common/actions/workflows/tester.yaml

.. image:: https://img.shields.io/github/license/emcd/agents-common
   :alt: Project License
   :target: https://github.com/emcd/agents-common/blob/master/LICENSE.txt

.. image:: https://img.shields.io/pypi/pyversions/emcd-agents
   :alt: Python Versions
   :target: https://pypi.org/project/emcd-agents/


🤖 **AI Agent Configuration Management** - Centralized, version-controlled
configurations for AI development tools with hybrid distribution architecture.
Enables rapid iteration on agent configurations while maintaining consistency
across multiple projects through tag-based releases and dynamic content generation.

Key Features ⭐
===============================================================================

🏗️ **Hybrid Distribution Architecture**
  Combines Copier templates for base configuration with agentsmgr CLI for
  dynamic content generation from structured data sources.

⚡ **Lightning-Fast Iteration**
  Tag-based releases enable rapid configuration updates without heavyweight
  project releases.

🔧 **Simple CLI Interface**
  Primary populate command generates agent configurations from any compatible
  data source with simulation mode support.

📦 **Extensible Data Sources**
  Works with any properly structured agent configuration library, enabling
  community-driven configuration sharing and reuse.

🔌 **Plugin Architecture**
  Extensible source handlers (git, local) and renderers (Claude, Opencode,
  Codex, Qwen) with decorator-based registration system.

🎯 **Multi-Target Support**
  Per-user and per-project targeting modes with intelligent symlink management
  for seamless AI tool integration.


Installation 📦
===============================================================================

Method: Download Standalone Executable
-------------------------------------------------------------------------------

Download the latest standalone executable for your platform from `GitHub
Releases <https://github.com/emcd/agents-common/releases>`_. These
executables have no dependencies and work out of the box.

Method: Install Executable Script
-------------------------------------------------------------------------------

Install via the `uv <https://github.com/astral-sh/uv/blob/main/README.md>`_
``tool`` command:

::

    uv tool install emcd-agents

or, run directly with `uvx
<https://github.com/astral-sh/uv/blob/main/README.md>`_:

::

    uvx --from emcd-agents agentsmgr

Or, install via `pipx <https://pipx.pypa.io/stable/installation/>`_:

::

    pipx install emcd-agents

Method: Install Python Package
-------------------------------------------------------------------------------

Install via `uv <https://github.com/astral-sh/uv/blob/main/README.md>`_ ``pip``
command:

::

    uv pip install emcd-agents

Or, install via ``pip``:

::

    pip install emcd-agents


Examples 💡
===============================================================================

CLI Usage
-------------------------------------------------------------------------------

**Populate Agent Content**:

Generate configurations from a git source:

::

    agentsmgr populate --source=github:emcd/agents-common@agents-2

Generate content for per-project mode:

::

    agentsmgr populate --mode=per-project --source=git:path/to/local/repo

**Test Configuration Changes**:

Preview what would be generated without making changes:

::

    agentsmgr populate --simulate --source=github:emcd/agents-common@agents-2

Copier Template Integration
-------------------------------------------------------------------------------

**Apply Base Template**:

Use as a Copier template for new projects:

::

    copier copy gh:emcd/agents-common path/to/new-project

**Update Existing Projects**:

Update base configuration templates:

::

    copier update --answers-file .auxiliary/configuration/copier-answers--agents.yaml

Use Cases
===============================================================================

* **Project Templates**: Distribute consistent AI agent configurations across multiple project templates
* **Development Teams**: Maintain synchronized agent configurations across team members
* **Configuration Evolution**: Rapidly iterate on slash commands and agent definitions
* **Multi-Tool Support**: Support Claude Code, Opencode, Codex, Qwen Code, and future AI development environments


Contribution 🤝
===============================================================================

Contribution to this project is welcome! However, it must follow the `code of
conduct
<https://emcd.github.io/python-project-common/stable/sphinx-html/common/conduct.html>`_
for the project.

Please file bug reports and feature requests in the `issue tracker
<https://github.com/emcd/agents-common/issues>`_ or submit `pull
requests <https://github.com/emcd/agents-common/pulls>`_ to
improve the source code or documentation.

For development guidance and standards, please see the `development guide
<https://emcd.github.io/agents-common/stable/sphinx-html/contribution.html#development>`_.


Additional Indicia
===============================================================================

.. image:: https://img.shields.io/github/last-commit/emcd/agents-common
   :alt: GitHub last commit
   :target: https://github.com/emcd/agents-common

.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/copier-org/copier/master/img/badge/badge-grayscale-inverted-border-orange.json
   :alt: Copier
   :target: https://github.com/copier-org/copier

.. image:: https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg
   :alt: Hatch
   :target: https://github.com/pypa/hatch

.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit
   :alt: pre-commit
   :target: https://github.com/pre-commit/pre-commit

.. image:: https://microsoft.github.io/pyright/img/pyright_badge.svg
   :alt: Pyright
   :target: https://microsoft.github.io/pyright

.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
   :alt: Ruff
   :target: https://github.com/astral-sh/ruff

.. image:: https://img.shields.io/pypi/implementation/emcd-agents
   :alt: PyPI - Implementation
   :target: https://pypi.org/project/emcd-agents/

.. image:: https://img.shields.io/pypi/wheel/emcd-agents
   :alt: PyPI - Wheel
   :target: https://pypi.org/project/emcd-agents/


Other Projects by This Author 🌟
===============================================================================


* `python-absence <https://github.com/emcd/python-absence>`_ (`absence <https://pypi.org/project/absence/>`_ on PyPI)

  🕳️ A Python library package which provides a **sentinel for absent values** - a falsey, immutable singleton that represents the absence of a value in contexts where ``None`` or ``False`` may be valid values.
* `python-accretive <https://github.com/emcd/python-accretive>`_ (`accretive <https://pypi.org/project/accretive/>`_ on PyPI)

  🌌 A Python library package which provides **accretive data structures** - collections which can grow but never shrink.
* `python-classcore <https://github.com/emcd/python-classcore>`_ (`classcore <https://pypi.org/project/classcore/>`_ on PyPI)

  🏭 A Python library package which provides **foundational class factories and decorators** for providing classes with attributes immutability and concealment and other custom behaviors.
* `python-dynadoc <https://github.com/emcd/python-dynadoc>`_ (`dynadoc <https://pypi.org/project/dynadoc/>`_ on PyPI)

  📝 A Python library package which bridges the gap between **rich annotations** and **automatic documentation generation** with configurable renderers and support for reusable fragments.
* `python-falsifier <https://github.com/emcd/python-falsifier>`_ (`falsifier <https://pypi.org/project/falsifier/>`_ on PyPI)

  🎭 A very simple Python library package which provides a **base class for falsey objects** - objects that evaluate to ``False`` in boolean contexts.
* `python-frigid <https://github.com/emcd/python-frigid>`_ (`frigid <https://pypi.org/project/frigid/>`_ on PyPI)

  🔒 A Python library package which provides **immutable data structures** - collections which cannot be modified after creation.
* `python-icecream-truck <https://github.com/emcd/python-icecream-truck>`_ (`icecream-truck <https://pypi.org/project/icecream-truck/>`_ on PyPI)

  🍦 **Flavorful Debugging** - A Python library which enhances the powerful and well-known ``icecream`` package with flavored traces, configuration hierarchies, customized outputs, ready-made recipes, and more.
* `python-mimeogram <https://github.com/emcd/python-mimeogram>`_ (`mimeogram <https://pypi.org/project/mimeogram/>`_ on PyPI)

  📨 A command-line tool for **exchanging collections of files with Large Language Models** - bundle multiple files into a single clipboard-ready document while preserving directory structure and metadata... good for code reviews, project sharing, and LLM interactions.
