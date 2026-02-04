# Python Implementation

Implement Python code following established patterns including functions,
classes, modules, tests, and refactoring while adhering to project practices
and style guidelines.

Request from user: {{args}}

## Context

- Architecture overview: @{documentation/architecture/summary.rst}
- Filesystem patterns: @{documentation/architecture/filesystem.rst}
- Design documents: @{documentation/architecture/designs/}

## Prerequisites

Before implementing Python code, ensure:
- Understanding of implementation requirements and expected behavior.
- Knowledge of existing codebase structure and patterns.
- Clear design specifications or existing design documents if referenced.

### Guide Consultation Requirements

Before implementing Python code, you MUST:
1. Read @{.auxiliary/instructions/practices.rst} for general development principles.
2. Read @{.auxiliary/instructions/practices-python.rst} for Python-specific patterns.
3. Read @{.auxiliary/instructions/style.rst} for code style requirements.
4. Read @{.auxiliary/instructions/nomenclature.rst} for naming conventions.
5. In a step on your todo list, please attest that you have read the practices, style, and nomenclature guides and demonstrate your knowledge by writing one-sentence summaries on any three of the following topics:

- the comprehensive examples showing multiple principles cohesively
- proper module organization content order
- wide parameter, narrow return type patterns for robust interfaces
- immutability preferences for data structures and containers
- exception handling with narrow try blocks and proper chaining
- documentation formatting requirements including narrative mood
- quality assurance principles including linter compliance

## Process Summary

Key functional areas:
1. **Issue Analysis**: Understand issue/requirements and establish or update issue tracking.
2. **Session Continuity**: Check for existing work and preserve context across sessions.
3. **Implementation**: Write Python code following style guidelines and best practices.
4. **Progress Tracking**: Maintain session and cross-session implementation progress.
5. **Quality Assurance**: Run linters, type checkers, and tests to validate code.
6. **Documentation**: Update issue tracking and provide implementation summary.

## Safety Requirements

Stop and consult the user if:
- Design specifications are needed instead of implementation.
- Architectural decisions are required before implementation.
- Requirements are unclear or insufficient for implementation.
- Implementation conflicts with established architectural patterns.
- Code changes would break existing API contracts or interfaces.
- Quality checks reveal significant issues that require design decisions.
- Type checker errors are encountered that cannot be resolved through standard remediation.
- Multiple implementation approaches have significant trade-offs requiring user input.

## Execution

Execute the following steps:

### 1. Issue Analysis and Tracking Setup

Determine if working with existing issue or creating new one:

**If the request from the user contains the path to an existing issue file** (under `.auxiliary/notes/issues/`):
- Read the existing issue file.
- Proceed to add/update progress tracking sections.

**If the request from the user references a GitHub issue** (e.g., "Fix GitHub issue #123"):
- Create or update `.auxiliary/notes/issues/gh-123.md`.
- Include GitHub issue URL in the file.

**If the request from the user provides an issue description** (e.g., "Fix metrics export crash"):
- Create new issue file: `.auxiliary/notes/issues/<short-descriptive-slug>.md`.
- Example: `.auxiliary/notes/issues/fix-metrics-export-crash.md`.

Once issue file is established, ensure it contains these sections (add if missing):

### Issue Description
- **Title**: [Brief description of the issue/feature]
- **Issue Reference**: [GitHub issue #123 URL or "Ad-hoc bug fix"]
- **Start Date**: [YYYY-MM-DD]
- **Context**: [What is the problem or what needs to be implemented?]

### References
- **Design Documents**: [Any architecture or design docs referenced]
- **Related Files**: [Key files involved in the implementation]
  - `path/to/file1.py` - [Brief description of relevance]
  - `path/to/file2.rst` - [Brief description of relevance]

### Implementation Approach
[Brief description of the approach being taken]

### Design and Style Conformance Checklist
- [ ] Module organization follows practices guidelines.
- [ ] Function signatures use wide parameter, narrow return patterns.
- [ ] Type annotations comprehensive with TypeAlias patterns.
- [ ] Exception handling follows Omniexception → Omnierror hierarchy.
- [ ] Naming follows nomenclature conventions.
- [ ] Immutability preferences applied.
- [ ] Code style follows formatting guidelines.

### Implementation Progress
- [ ] [Specific function/class/module 1]
- [ ] [Specific function/class/module 2]
- [ ] [Integration point 1] tested
- [ ] [Integration point 2] tested

### Quality Gates
- [ ] Linters pass (`hatch --env develop run linters`).
- [ ] Tests pass (`hatch --env develop run testers`).
- [ ] Code review ready.

### Decision Log
Document significant decisions made during implementation:
- [Date] [Decision made] - [Rationale]
- [Date] [Trade-off chosen] - [Why this approach over alternatives]

### Current State
- **Status**: [In Progress / Blocked / Ready for Review / Completed]
- **What's Done**: [Summary of completed work]
- **What's Left**: [Remaining tasks]
- **Known Issues**: [Any problems or concerns to address]

### Next Steps
[Immediate next actions needed for continuation]

### 2. Session Continuity and Context Preservation

If working with existing issue file:
- Read the entire issue file to understand context.
- Review reference files and design documents listed.
- Check decision log for previous design choices.
- Note current state and what's already done.

#### Context Preservation Requirements
Before beginning implementation:
- [ ] Establish issue file (create new or update existing).
- [ ] Document issue description and context.
- [ ] Record all reference files and design documents.
- [ ] Document implementation approach.

During implementation:
- [ ] Update decision log when making design choices.
- [ ] Record integration points and dependencies discovered.
- [ ] Document deviations from original plan with rationale.
- [ ] Update implementation progress checklist as items complete.

Before session end:
- [ ] Update Current State section with what's done and what's left.
- [ ] Ensure todo list completions are reflected in issue file where granularity aligns.
- [ ] Record next steps for continuation.

### 3. Implementation

**Write Python code following established patterns**:
- Apply comprehensive guide patterns for module organization, imports, annotations, immutability, exception handling, and documentation.
- Consult the comprehensive guides when you need specific implementation details.
- For complex annotation work or systematic annotation issues, consider using the `python-annotator` agent.

### 4. Progress Tracking Requirements
Maintain dual tracking systems:
- **Session Level**: Use todo list for immediate task management within current session.
- **Cross-Session**: Update issue file in `.auxiliary/notes/issues/` for persistent tracking.
- **Synchronization**: When todo list items align with issue checklist granularity, update corresponding issue checklist items (todo list may be more fine-grained).
- **Context Preservation**: Record all reference files and design decisions in issue file for future session continuity.

### 5. Quality Assurance

Before proceeding, add this quality verification checklist to your todo list:
- [ ] Code follows proper module organization patterns.
- [ ] Type annotations use wide parameter, narrow return patterns.
- [ ] Functions ≤30 lines, modules ≤600 lines.
- [ ] Immutability preferences applied to data structures.
- [ ] Exception handling uses narrow try blocks with proper chaining.
- [ ] Documentation follows narrative mood requirements.
- [ ] Quality assurance principles applied.

#### Validation Commands
**Linting Validation** (zero-tolerance policy):
```bash
hatch --env develop run linters
```
All issues must be addressed per comprehensive guide principles. Do not use `noqa` without explicit approval.

**Type Checking** (systematic resolution):

**Type Error Resolution Process**:
1. **Code Issues**: Fix immediately using comprehensive guide type annotation patterns.
2. **Third-party Stubs**: Follow guidance in Python-specific practices guide (ensure dependency in `pyproject.toml`, prune Hatch environment, Pyright `createstub`, manage stubs).
3. **Complex Issues**: Use `python-annotator` agent for systematic resolution.

Stop and consult user if type errors cannot be categorized or require architectural decisions.

**Test Validation**:
```bash
hatch --env develop run testers
```
All tests must pass, including new implementations.

### 6. Documentation and Summary

**Provide implementation documentation**:
- Update issue file with implementation state.
- Document design decisions and trade-offs in decision log.
- Update Current State and Next Steps sections.
- Note remaining items for future work.

### 7. Summarize Implementation
Provide concise summary of what was implemented, including:
- Functions, classes, or modules created or modified.
- Key design decisions and rationale.
- Integration points and dependencies.
- Quality assurance status: Confirm all linters, type checkers, and tests pass.
- Checklist of principles and patterns applied during implementation.
- Any remaining tasks or follow-up items.
