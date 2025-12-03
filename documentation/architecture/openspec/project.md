# Project Context

## Purpose
**emcd-agents** is a centralized, version-controlled system for managing AI agent configurations. It employs a hybrid distribution architecture that combines Copier templates for base configurations with a CLI tool (`agentsmgr`) for dynamic content generation. Its goal is to enable rapid iteration on agent configurations (slash commands, prompts, tool definitions) while ensuring consistency across multiple projects and users.

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
    - `pyinstaller` (Standalone executable builds)

## Project Conventions

### Code Style
- **Line Length:** 79 characters.
- **Typing:** Strong static typing enforced by `pyright`.
- **Formatting:** Enforced by `ruff` and `isort`.
- **Imports:** Sorted by `isort` with specific groupings (`agentsmgr` as first-party).
- **Docstrings:** Sphinx-compatible reStructuredText.

### Architecture Patterns
- **Hybrid Distribution:** Combines static templates (Copier) with dynamic generation (`agentsmgr`).
- **Plugin System:** Extensible source handlers (Git, Local) and renderers (Claude, Opencode, Qwen) using decorator-based registration.
- **Immutability:** Preference for immutable data structures (`frigid` packages) to ensure state predictability.
- **Sentinel Values:** Use of `absence` package for distinguishing "undefined" from "None".

### Development Practices
Detailed practices documented in `.auxiliary/instructions/`:
- **practices.rst** - Robustness principle (Postel's Law), immutability first, dependency injection, exception chaining
- **practices-python.rst** - Module organization, type annotations, wide parameter/narrow return patterns, exception hierarchies, documentation (narrative mood)
- **nomenclature.rst** - Naming patterns for variables, functions, classes, exceptions
- **style.rst** - Code formatting (spacing, line length, 79 chars, documentation standards)
- **validation.rst** - Quality gates (linters, type checkers, tests must pass)

### Testing Strategy
- **Framework:** `pytest` for unit and integration tests.
- **Doctests:** Executed via `sphinx` to ensure documentation accuracy.
- **Coverage:** tracked via `coverage.py` with HTML and XML reports.
- **Categorization:** Tests marked (e.g., `@pytest.mark.slow`) to separate fast unit tests from slower integration tests.
- **CI/CD:** GitHub Actions workflows for testing (`tester.yaml`), releasing (`releaser.yaml`), and initialization (`core--initializer.yaml`).

### Git Workflow
- **Versioning:** Tag-based release workflow.
- **Commits:**
    - Present tense, imperative mood verbs (e.g., "Fix bug", not "Fixed bug").
    - Detailed body explaining *why*.
    - `Co-Authored-By:` footer for AI contributions.
- **Changelog:** Managed via `towncrier` news fragments (enhance, notify, remove, repair).

## Domain Context
- **AI Configuration:** Managing prompts, slash commands, and agent personas for various AI coding assistants (Claude, Qwen, Opencode).
- **Templating:** Utilizing Jinja2 for dynamic generation of configuration files based on data sources.
- **Symlink Management:** Intelligent management of symlinks for per-user and per-project configuration targeting.

## Important Constraints
- **Compatibility:** Must support Python 3.10 through 3.14 (and PyPy).
- **Performance:** CLI commands should be responsive; heavy operations (like git clones) should be handled efficiently.
- **Safety:** Operations involving file system modifications (symlinks, file writes) must be safe and usually require user confirmation or simulation mode.

## External Dependencies
- **Source Repositories:** Git repositories (e.g., GitHub) hosting agent configurations.
- **Target Applications:** AI coding assistants (Claude Desktop, etc.) that consume the generated configurations.