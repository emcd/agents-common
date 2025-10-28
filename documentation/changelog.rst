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

agentsmgr 1.0a5 (2025-10-28)
============================

Enhancements
------------

- CLI: Add claude-zai wrapper for GLM Coding Plan API integration, providing convenient access to glm-4.6 and glm-4.5-air models.
- OpenCode: Create opencode.jsonc symlink in per-project mode for proper configuration management and git exclusion.


Notices
-------

- OpenCode: Disable built-in Pyright LSP server to prevent diagnostic errors and ensure proper type checking with project configuration.


agentsmgr 1.0a4 (2025-10-25)
============================

Enhancements
------------

- CLI: Add source data structure validation to populate commands.
  The populate project and populate user commands now validate that the source location contains the required directory structure before attempting population.
  Invalid source structures produce clear error messages listing all missing required directories, allowing graceful failure instead of silently generating no items.
- CLI: Implement managed block for Git exclude entries.
  Git exclude entries are now managed within a clearly-marked, lexicographically sorted managed block with BEGIN/END markers.
  This ensures complete block replacement on each update, naturally handling entry removals and preventing accumulation of unnecessary blank lines.
- CLI: Implement mode-based filtering in populate commands.
  The populate project and populate user commands now filter coders by their default mode to ensure each command handles only appropriate coders: populate project processes per-project default coders, while populate user processes per-user default coders.
  Coder directory symlinks are now only created for coders whose default mode is per-project, preventing dangling symlinks for per-user coders.
- CLI: Split populate command into nested project and user subcommands.
  The populate command now uses a nested subcommand structure: ``populate project`` for project-scoped operations (content generation, symlinks, git exclude) and ``populate user`` for user-scoped operations (global settings, wrapper installation).
  The ``--mode`` flag has been removed, as ``populate project`` always uses per-project mode.
  The ``--update-globals`` flag has been replaced by the separate ``populate user`` subcommand.


agentsmgr 1.0a3 (2025-10-23)
============================

Enhancements
------------

- Agent: Add python-annotator agent for Python type annotation tasks including adding type hints, resolving Pyright issues, creating type stubs, and analyzing type: ignore pragmas.
- CLI: Add instruction file downloading support to populate command with automatic retrieval from Git sources, flexible glob pattern filtering, and per-file preprocessing with header stripping support.
- CLI: Automatically manage git exclusion of instruction files through .git/info/exclude when populate command runs, respecting dynamic configuration changes.
- CLI: Populate command now skips items with missing content and logs warnings instead of failing the entire operation, enabling iterative development without complete content sets.


Repairs
-------

- CLI: Fix template path resolution for OpenCode coder which was causing silent failures during content population due to singular/plural directory name mismatch.


agentsmgr 1.0a2 (2025-10-22)
============================

Enhancements
------------

- Add support for Git worktrees and ``GIT_DIR`` environment variable in populate command, improving compatibility with non-standard Git configurations.
- Support relative paths in populate command source argument without requiring explicit ``./`` prefix. The source resolution now uses standard URL scheme extraction for simplified path handling.


Repairs
-------

- Fix Git source handler URL scheme registration for correct path resolution in populate command source argument.
- Fix populate command to respect per-coder mode defaults when creating coder directory symlinks and properly handle interrupted operations for idempotent behavior.


agentsmgr 1.0a1 (2025-10-21)
============================

Enhancements
------------

- CLI: Add --profile parameter to populate command for specifying alternative Copier answers file paths, enabling testing with different configurations.
- CLI: Add --tag-prefix parameter to populate command for filtering Git version tags by prefix, with semantic version comparison for accurate tag selection.
- CLI: Add support for Gemini CLI as a target coder for command generation (agent generation not supported by Gemini CLI).
- CLI: Add support for Qwen Code as a target coder, including agent and command generation with YAML frontmatter templates and MCP server configuration.
- Git: Automatically add generated symlink names to .git/info/exclude during populate command to prevent accidental commits of generated content.
- Performance: Optimize GitHub and GitLab repository processing with API-based tag resolution and shallow cloning, providing 3-50x speedup for population operations.


Notices
-------

- CLI: Change populate command to use positional arguments for source and target instead of --source and --target flags. This is a breaking change for existing scripts.
- CLI: Split command-line interface into user-facing (agentsmgr) and maintainer-facing (agentsmgr-maintain) tools. The validate command is now available via agentsmgr-maintain.


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
