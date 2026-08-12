## 1. Distribution Tree

- [x] 1.1 Create `distribution/` directory structure with `per-project/general/{instructions,skills}/` and `per-project/coders/{claude,codex,opencode}/`
- [x] 1.2 Create `distribution/per-user/general/` and `distribution/per-user/coders/{claude,codex,opencode}/`
- [x] 1.3 Add `.gitkeep` files to empty coder directories
- [x] 1.4 Move skills from `defaults/contents/skills/` to `distribution/per-project/general/skills/`
- [x] 1.5 Move per-project resources from `defaults/per-project/resources/` to `distribution/per-project/coders/`
- [x] 1.6 Move per-user resources from `defaults/user/` to `distribution/per-user/`

## 2. Components Tree

- [x] 2.1 Create `components/` directory structure with `configurations/{agents,commands}/`, `templates/{agents,commands}/`, `contents/{agents,commands}/`
- [x] 2.2 Move command/agent configurations from `defaults/configurations/` to `components/configurations/`
- [x] 2.3 Move command/agent templates from `defaults/templates/` to `components/templates/`
- [x] 2.4 Move command/agent contents from `defaults/contents/` to `components/contents/` (excluding skills)

## 3. Instructions Sync

- [x] 3.1 Sync `python-project-common` instruction content into `distribution/per-project/general/instructions/` (direct distribution artifact, not component)
- [x] 3.2 Add `distribution/per-project/general/instructions/` with synced content
- [x] 3.3 Remove network fetch logic from `agentsmgr populate` for instructions (or gate behind `--latest` flag)

## 4. Generation Command

- [x] 4.1 Add `agentsmgr generate` command that produces `components/` -> `distribution/`
- [x] 4.2 Add `agentsmgr generate --check` for staleness validation (regenerate and diff)
- [x] 4.3 Pre-generate command/agent artifacts into `distribution/per-project/coders/`

## 5. Exclude Management

- [x] 5.1 Rewrite `_create_all_symlinks` and exclude logic to manage individual files in `.git/info/exclude`
- [x] 5.2 Add reconciliation: remove exclude entries for files no longer in distribution tree
- [x] 5.3 Remove blanket directory ignores from template `.gitignore`

## 6. Migration

- [x] 6.1 Update docs, scripts, and self-dogfooding commands to reference `distribution/` instead of `defaults/`
- [x] 6.2 Optionally add compatibility shim if existing implicit `defaults/` references require it
- [x] 6.3 Update Copier answers file template for `distribution/` path
- [x] 6.4 Add migration guidance to template documentation

## 7. Validation

- [x] 7.1 Run `openspec validate restructure-distribution-model --strict` and resolve issues
- [x] 7.2 Run `hatch --env develop run pytest` (all tests pass)
- [x] 7.3 Run `hatch --env develop run linters` (clean)
- [x] 7.4 Run `agentsmgr generate --check` (no staleness)
- [x] 7.5 Run `agentsmgr populate project ./distribution . --simulate` (verify new structure)
