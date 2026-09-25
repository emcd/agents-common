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
Configuration and Copier Template Release Notes
*******************************************************************************

These notes cover **Copier template** and **configuration content** changes
(``template/``, ``components/`` / ``distribution/``, and related harness base
settings). They are versioned with ``agents-*`` git tags for populate pins and
Copier template refs.

They are **not** the emcd-agents / agentsmgr **Python package** changelog.
Package release notes live in :doc:`changelog` and are managed with Towncrier.

Workflow (manual; no Towncrier for this file):

* Authors add bullets under **Unreleased** with template or content changes
  (``template/``, ``components/`` / ``distribution/``, harness base settings).
* Cutting an ``agents-*`` tag renames **Unreleased** to that tag and date.
* Do not file package Towncrier fragments for template-only work.
* Pattern follows python-project-common ``template-changelog.rst`` (manual
  sections), but versions here are ``agents-*`` tags, not package ``v*``.


Unreleased
==========

Curated consumer-facing summary of material configuration and template
changes since ``agents-1.0``. Not a full commit history.

Removals
--------

- Drop Gemini CLI and Qwen Code as supported template/distribution coders.
- Stop shipping shared ``architecture.rst`` instruction and retire
  ADR-centric ``cs-architect``-style commands from distribution content.
- Remove default blocking agent hooks from generated coder configuration.
- Stop hiding managed coder resource directories behind ignore rules that
  blocked normal inspection of agentsmgr-managed trees.
- Remove Claude ``miscellany/bash-tool-bypass`` and
  ``miscellany/command-template.md`` from the Copier template.
- Retire distribution commands ``cs-create-command`` and
  ``cs-update-command``.
- Remove obsolete Claude Code Web session setup notes
  (``documentation/miscellany/ccw-setup.md``).
- Drop Copier answer ``project_bundle_name`` and stop passing
  Agentmux ``--bundle`` in generated MCP configs; Agentmux ≥0.9
  injects ``AGENTMUX_BUNDLE`` into MCP children (lazy upgrade).

Enhancements
------------

- Hybrid layout: ``components/`` sources render to ``distribution/`` via
  ``agentsmgr generate`` (render and optional ``--check`` staleness).
  Copier template validation is separate and uses copiertv profiles.
- Populate installs Agent Skills packages (full directories with
  ``SKILL.md`` / scripts / references / assets, plus legacy flat
  ``*.md``) under canonical ``.auxiliary/agents/skills/``, links root
  ``.agents`` → ``.auxiliary/agents``, and links each coder ``skills/``
  directory to that tree (destructive cutover of legacy dual-copy skill
  dirs only; pre-existing real root ``.agents`` is preserved).
- Rehome LM-facing operational guidance under ``.auxiliary/agents/``
  (entrypoint ``agents.md``, procedures, standards target). Root
  ``AGENTS.md`` / ``CLAUDE.md`` remain thin memory symlinks into that tree.
- Split project-owned guidance into ``.auxiliary/agents/project.md``
  (Purpose / Tech Stack / Notes) with Copier ``_skip_if_exists`` so
  ``copier update`` does not clobber local project knowledge. Generated
  entrypoint stays pointer-only.
- Codify two-tier technical review in the template review procedure.
  Tier-1 Reviewer is the gate. Tier-2 Reviewer, usually an Advisor,
  is engaged only after Tier-1 approval. Authors must not dictate
  review scope or shotgun both tiers.
- Default OpenCode ``build`` and ``plan`` agents to
  ``meta/muse-spark-1.3-contributor`` (Meta metered API, not a
  subscription or OpenCode Zen free tier).
- Stage ``tests.md`` and ``practices-rust.md`` from
  ``python-project-common`` ``docs-1.9``
  (``82082295a30c9ef2aa4c633bc609df70c4a0e127``) into
  ``distribution/per-project/general/instructions/`` for populate.
  No header strip. This is an ingest slice, not retirement of the
  Copier instruction fetch.
- Default instructions target is ``.auxiliary/agents/standards`` (replacing
  older instruction homes); instruction sync copies from distribution
  general instructions into that target.
- OpenSpec 1.5 / OPSX skills and template guidance (``opsx-*`` skill names
  without custom prefix); OpenSpec scaffolding remains under
  ``documentation/architecture/openspec/`` with managed root ``openspec``
  symlink for tooling that expects ``./openspec``.
- nb MCP and OpenSpec workflow guidance live in template procedures under
  ``.auxiliary/agents/procedures/`` rather than only inlined in the
  entrypoint.
- Delegated review / handoff / collaboration guidance in shared AGENTS
  operation text (reviewer vs integrator, fixup hold until approve,
  base-advance re-review, harness-safe autosquash inspect).
- agentmux MCP support and project bundle-name templating in Copier
  answers / MCP sets.
- Claude project MCP server allowlisting for standard project MCP set.
- OpenCode generated resource directories use plural names aligned with other
  coders.
- Cross-harness shell allowlists expanded for common read-oriented and
  development commands; Claude, OpenCode, and Codex harness-level
  allowlists permit ``readlink`` and ``test`` (argument forms only).
- Codex Starlark rules allowlist (including selected git write prefixes
  such as commit/tag) and approval routing defaults suitable for trusted
  local development.
- Rolling handoff hygiene lives in
  ``.auxiliary/agents/procedures/notebook.md`` only (no AGENTS section).
  Coordinators/sole owners and tech leads (for their lanes) own handoffs;
  implementers do not. No routine post-commit handoff refreshes.
- Delegated review: post-approval rebase onto an advanced base may use a
  merge handoff when the stack is byte-identical and the author re-runs
  lints/tests; non-identical stacks still require technical re-review.
  Integrator retains merge-safety checks across lanes.
- Language-aware instruction defaults (e.g. Rust) in Copier answers maps.
- Template validation migrated to copiertv profiles under
  ``.auxiliary/configuration/copiertv/``.

Notices
-------

- Configuration pins (``@agents-*``, Copier ``_commit``) are independent of
  emcd-agents package versions; package CLI changes are documented only in
  :doc:`changelog`.
- Self-dogfood of template changes uses ``copier update`` against a
  reachable template ref, then ``agentsmgr generate`` / ``populate`` as
  needed — do not hand-mirror ``template/`` into live project paths.
- Intermediate OpenSpec home relocation is not a supported migration step;
  future Nbspec cutover is tracked separately from this changelog track.


agents-1.0 (2025-10-22)
=======================

Enhancements
------------

- Initial agent configuration data release with relative path support for
  populate sources.
