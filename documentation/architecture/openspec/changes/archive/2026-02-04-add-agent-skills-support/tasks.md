## 1. Implementation

- [x] 1.1 Add a `skills` item type to the generator and operations flow.
- [x] 1.2 Add default output layout under each coder:
      `.auxiliary/configuration/coders/<coder>/skills/<name>/SKILL.md`.
- [x] 1.3 Create a shared Agent Skills template under
      `defaults/templates/skills/common.md.jinja` that generates a valid
      `SKILL.md` file (YAML frontmatter + Markdown body).
- [x] 1.4 Create initial `defaults/configurations/skills/` and
      `defaults/contents/skills/common/` entries for a small starter set (or
      mechanically derive from existing items if we decide to “promote” them).
- [x] 1.5 Ensure Agent Skills `allowed-tools` mapping is supported:
      - store semantic tool specs in skill configuration
      - map/format per coder during rendering (omit when unsupported)
- [x] 1.6 Ensure generated directories remain untracked without placeholders:
      - Consolidate coder root `.gitignore` patterns to ignore generated dirs
        (`commands/`, `agents/`, `skills/`) and local settings files.
      - Ensure `agentsmgr` creates output directories when missing (so we do
        not rely on `.gitignore` files as directory placeholders).
- [x] 1.7 Update coder templates/configuration where a tool supports explicit
      skills directories (document and gate behind feature detection).

## 2. Validation

- [x] 2.1 Add unit tests for:
      - skills path mapping and rendering
      - frontmatter constraints (name matching, length) where feasible
      - allowed-tools join/format behavior
- [x] 2.2 Run `hatch --env develop run linters` and `hatch --env develop run testers`.

## 3. Docs

- [x] 3.1 Document where skills live in downstream projects and how tools
      discover them (via `.claude/skills`, `.opencode/skills`, `.gemini/skills`).
- [x] 3.2 Document guidance for keeping `SKILL.md` small and pushing detail
      into `references/` (progressive disclosure).
