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
Release Notes
*******************************************************************************

.. towncrier release notes start

agentsmgr 1.0a0 (2025-10-12)
============================

Enhancements
------------

- CLI: Add Git ref specification support with @ref syntax for targeting specific branches, tags, or commits, with automatic latest tag fallback.
- CLI: Add Git source support with github:, gitlab:, and git+https: URL schemes for pulling agent configurations from remote repositories.
- CLI: Add agentsmgr command-line tool with detect, populate, and validate subcommands for managing AI agent configurations.
- CLI: Add automatic memory file symlink creation for coder-specific filenames (CLAUDE.md, AGENTS.md) pointing to shared project conventions.
- CLI: Add multi-target support with per-user and per-project targeting modes, including intelligent symlink management for seamless AI tool integration.
- Comprehensive slash command and agent configuration library for Python development, releases, architecture documentation, and project management.
- Hybrid distribution architecture combines Copier templates for base configuration with agentsmgr CLI for dynamic content generation from structured data sources.
- Multi-AI tool support for Claude Code, Opencode, and future AI development environments with extensible configuration management.
- Plugin architecture with extensible source handlers (git, local) and renderers (Claude, Opencode, Codex) using decorator-based registration system.
- Tag-based release system enables rapid configuration distribution using agents-N versioning scheme for atomic, consistent deployment.
