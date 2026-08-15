# Project Guidance

Project-owned knowledge the generated `AGENTS.md` entrypoint must not own.
Structured tracking stays in `nb`.

## Purpose

**emcd-agents** is a centralized, version-controlled system for managing AI
agent configurations. It employs a hybrid distribution architecture that
combines Copier templates for base configurations with a CLI tool (`agentsmgr`)
for dynamic content generation. Its goal is to enable rapid iteration on agent
configurations (slash commands, prompts, tool definitions) while ensuring
consistency across multiple projects and users.

## Tech Stack

- **Language:** Python (>= 3.10)
- **Build System:** Hatch (hatchling)
- **Core Dependencies:**
    - `emcd-appcore[cli]` (Application framework)
    - `Jinja2` (Templating)
    - `PyYAML` (Configuration parsing)
    - `dulwich` (Git operations)
    - `frigid`, `accretive`, `absence` (Immutable/specialized data structures)
    - `dynadoc` (Documentation utilities)
- **Development Tools:**
    - `ruff` (Linting and formatting)
    - `pyright` (Static type checking)
    - `isort` (Import sorting)
    - `pre-commit` (Git hooks)
    - `pytest` (Testing)
    - `coverage` (Test coverage)
    - `sphinx` (Documentation)
    - `towncrier` (Changelog management)
    - `copier` (Project templating)
    - `copiertv` (Template rendering validation)
    - `pyinstaller` (Standalone executable builds)

## Notes

- Self-dogfooding procedure for template/default changes: `procedures/1`.

<!-- Accumulate project-specific knowledge, constraints, deviations, and durable
     links here. For structured items, use `nb`.

     TODO: If this project uses multiple agent/worktree roles, create a stable
     team-organization note in `nb`, modeled after one of the examples at:
     https://raw.githubusercontent.com/emcd/agents-common/master/examples/nb-notes/team-organization/README.md
     Then link the note here, for example:
     - Team org, role ownership, signoff policy, and merge workflow: `coordination/general/<n>` -->
