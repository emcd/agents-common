## 1. OPSX Skill Defaults

- [x] 1.1 Create curated `cs-opsx-propose.md` under `defaults/contents/skills/cs-opsx-propose.md` (portable across coders, stores guidance removed)
- [x] 1.2 Create curated `cs-opsx-apply.md` under `defaults/contents/skills/cs-opsx-apply.md` (stores guidance removed)
- [x] 1.3 Create curated `cs-opsx-archive.md` under `defaults/contents/skills/cs-opsx-archive.md` (stores guidance removed)
- [x] 1.4 Create curated `cs-opsx-explore.md` under `defaults/contents/skills/cs-opsx-explore.md` (stores guidance removed)
- [x] 1.5 Create curated `cs-opsx-sync.md` under `defaults/contents/skills/cs-opsx-sync.md` (stores guidance removed)

## 2. Delete Old Commands

- [x] 2.1 Delete `defaults/per-project/resources/opencode/command/openspec-proposal.md`
- [x] 2.2 Delete `defaults/per-project/resources/opencode/command/openspec-apply.md`
- [x] 2.3 Delete `defaults/per-project/resources/opencode/command/openspec-archive.md`
- [x] 2.4 Delete `defaults/per-project/resources/claude/commands/openspec/proposal.md`
- [x] 2.5 Delete `defaults/per-project/resources/claude/commands/openspec/apply.md`
- [x] 2.6 Delete `defaults/per-project/resources/claude/commands/openspec/archive.md`

## 3. Template OpenSpec Configuration

- [x] 3.1 Create `template/documentation/architecture/openspec/config.yaml.jinja` with `schema: spec-driven` and project context placeholder
- [x] 3.2 Delete `template/documentation/architecture/openspec/AGENTS.md`

## 4. Template Guidance

- [x] 4.1 Rewrite `template/documentation/agents/openspec.md` to reference OPSX skills (`cs-opsx-propose`, `cs-opsx-apply`, etc.) and CLI state queries (`openspec list`, `openspec status`, `openspec instructions`, `openspec validate --all --strict`)
- [x] 4.2 Update OpenSpec section in `template/.auxiliary/configuration/AGENTS.md.jinja` to match new guidance

## 5. Validation

- [x] 5.1 Run `openspec validate migrate-openspec-15-opsx --strict` and resolve issues
- [x] 5.2 Run `hatch --env develop run pytest` (all tests pass)
- [x] 5.3 Run `hatch --env develop run linters` (clean)
- [x] 5.4 Run `hatch --env develop run agentsmgr populate project ./defaults . --simulate` (verify new skills discovered)
