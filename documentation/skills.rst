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


Skills (SKILL.md)
===============================================================================

This repository supports generating Agent Skills (`SKILL.md`) into downstream
projects.

Where skills live
-------------------------------------------------------------------------------

`agentsmgr populate project ./defaults` writes skills under the project’s
configuration directories:

.. code-block:: text

   .auxiliary/configuration/coders/<coder>/skills/<skill-name>/SKILL.md

These directories are exposed via the existing coder symlinks at project root,
so tools discover skills in their expected locations:

.. code-block:: text

   .claude/skills/<skill-name>/SKILL.md
   .codex/skills/<skill-name>/SKILL.md
   .gemini/skills/<skill-name>/SKILL.md
   .opencode/skills/<skill-name>/SKILL.md

Notes:

* Tools use filesystem discovery; we do not require a separate “skills registry”
  file.
* Generated directories (`agents/`, `commands/`, `skills/`) are ignored by
  consolidated coder-root `.gitignore` files, so they remain untracked.

Skill contents and portability
-------------------------------------------------------------------------------

The base `SKILL.md` format is standardized (YAML frontmatter + Markdown body),
but some fields and behaviors are tool-specific.

* `allowed-tools` is mapped and emitted where supported; for other coders it is
  omitted.
* Argument interpolation is not part of the base standard. If a tool supports
  invocation arguments (e.g., Claude’s `$ARGUMENTS`), treat it as a tool
  extension and avoid relying on it for cross-coder skills.

Guidance
-------------------------------------------------------------------------------

Keep `SKILL.md` small and focused:

* Put “what to do” in the body.
* Push lengthy background, examples, or reference material into adjacent
  `references/` files when needed.
* Prefer explicit “Inputs” sections that tell the agent what it must ask for if
  not already present in conversation context.
