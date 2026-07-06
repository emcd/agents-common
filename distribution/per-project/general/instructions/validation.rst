Validation
*******************************************************************************

Code validation ensures quality, consistency, and correctness before submitting
contributions. All projects provide standardized Hatch scripts for validation
tasks.

Commands
===============================================================================

Run validation commands using ``hatch --env develop run <command>``.

**linters**
  Runs code quality checks including Ruff linting, Pyright type checking, and
  Rust linting (if applicable). Must pass with no errors.

**pytest**
  Runs quick tests. Useful for quick validation during development.

**testers**
  Runs the full test suite with coverage reporting. Generates HTML and XML
  coverage reports in ``.auxiliary/artifacts/coverage-pytest/``.

**packagers**
  Builds distribution packages using Hatch. Also builds standalone executables
  via PyInstaller (if enabled).

**docsgen**
  Generates project documentation and runs link validation. Outputs to
  ``.auxiliary/artifacts/sphinx-html/``.

**make-all**
  Runs all validation steps in sequence: linters, testers, packagers, and
  docsgen. Use this for comprehensive validation before submitting pull
  requests.

Workflow
===============================================================================

1. **During Development**: Use ``pytest`` for quick feedback.
2. **Before Committing**: Run ``linters`` to catch some bugs, code smells, and
   type issues.
3. **Before Pull Requests**: Run ``make-all`` to ensure all validation passes.

All validation commands must pass without errors before contributions can be
accepted. If you installed the Git pre-commit and pre-push hooks for the
project, then they will perform most of these validations for you.
