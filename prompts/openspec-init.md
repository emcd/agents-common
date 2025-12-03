# Openspec Initialization Prompt

Use this prompt when initializing Openspec for a new project:

---

Please read openspec/project.md and help me fill it out with details about my project, tech stack, and conventions.

When documenting project conventions, please reference relevant architectural documentation:
- If this project has documentation/architecture/filesystem.rst, reference it in the "Project Conventions" section under an appropriate subsection (e.g., "Filesystem Organization")
- Include references to any other key architectural documentation files

After completing project.md, validate it meets Openspec conventions.

---

## Background

This prompt helps populate openspec/project.md with project-specific context that AI assistants will use when creating specifications and change proposals. The project.md file documents:

- Project purpose and goals
- Tech stack and dependencies
- Code style and conventions
- Architecture patterns
- Testing strategies
- Development practices

By referencing existing architectural documentation (like filesystem.rst), we maintain a single source of truth while making that information discoverable to AI assistants working within the Openspec workflow.
