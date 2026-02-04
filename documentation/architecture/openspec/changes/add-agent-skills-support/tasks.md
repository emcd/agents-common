## 1. Implementation

- [ ] 1.1 Add a `skills` item type to the generator and operations flow.
- [ ] 1.2 Add default output layout under each coder:
      `.auxiliary/configuration/coders/<coder>/skills/<name>/SKILL.md`.
- [ ] 1.3 Create Agent Skills templates under `defaults/templates/skills/` that
      generate valid `SKILL.md` files (YAML frontmatter + Markdown body).
- [ ] 1.4 Create initial `defaults/configurations/skills/` and
      `defaults/contents/skills/common/` entries for a small starter set (or
      mechanically derive from existing items if we decide to “promote” them).
- [ ] 1.5 Ensure Agent Skills `allowed-tools` mapping is supported:
      - store semantic tool specs in skill configuration
      - map/format per coder during rendering (omit when unsupported)
- [ ] 1.6 Add per-project coder resources for skills directories (e.g.
      `.auxiliary/configuration/coders/<coder>/skills/.gitignore`) so generated
      skills remain untracked, consistent with `commands/` and `agents/`.
- [ ] 1.7 Update coder templates/configuration where a tool supports explicit
      skills directories (document and gate behind feature detection).

## 2. Validation

- [ ] 2.1 Add unit tests for:
      - skills path mapping and rendering
      - frontmatter constraints (name matching, length) where feasible
      - allowed-tools join/format behavior
- [ ] 2.2 Run `hatch --env develop run linters` and `hatch --env develop run testers`.

## 3. Docs

- [ ] 3.1 Document where skills live in downstream projects and how tools
      discover them (via `.claude/skills`, `.opencode/skills`, `.codex/skills`).
- [ ] 3.2 Document guidance for keeping `SKILL.md` small and pushing detail
      into `references/` (progressive disclosure).
