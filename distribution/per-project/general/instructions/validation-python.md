<a id="validation-python"></a>
# Validation (Python)

This guide provides Python-specific validation commands for projects
using Hatch environments. For shared validation expectations, see the
[validation guide](validation.md).

<a id="commands"></a>
## Commands

Run validation commands with `hatch --env develop run <command>`.

**linters**  
Runs code quality checks including Ruff linting, Pyright type checking, and optional language-specific linting configured by the project.

**pytest**  
Runs quick tests for rapid development feedback.

**testers**  
Runs the full test suite with coverage reporting. Coverage artifacts are typically written under `.auxiliary/artifacts/coverage-pytest/`.

**packagers**  
Builds distribution packages using Hatch. Projects with executable outputs may also run PyInstaller in this stage.

**docsgen**  
Builds project documentation and link checks. Artifacts are typically written under `.auxiliary/artifacts/sphinx-html/`.

**make-all**  
Runs the full quality sequence (linters, testers, packagers, docsgen).

<a id="workflow"></a>
## Workflow

1.  **During Development**: Use `pytest` for quick feedback.
2.  **Before Committing**: Run `linters` to catch quality and type issues.
3.  **Before Pull Requests**: Run `make-all` for comprehensive validation.

All required validation commands must pass before contributions can be accepted. If Git hooks are installed, they will run part of this workflow automatically.
