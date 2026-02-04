## 1. Implementation

- [x] 1.1 Update `CodexRenderer` to support `per-project` base directories.
- [x] 1.2 Change Codex default targeting mode to `per-project`.
- [x] 1.3 Add Codex per-project Copier template files under
      `template/.auxiliary/configuration/coders/codex/`.
- [x] 1.4 Add `.codex` symlink creation in per-project mode so Codex discovers
      `.codex/config.toml`.
- [x] 1.5 Keep `populate user` support for Codex global `~/.codex/config.toml`
      as an opt-in legacy path.

## 2. Validation

- [x] 2.1 Add unit tests covering:
      - Codex renderer base directory resolution for both modes.
      - `.codex` per-project symlink provisioning.
- [x] 2.2 Run `hatch --env develop run linters` and `hatch --env develop run testers`.

## 3. Docs & Coordination

- [x] 3.1 Update docs/notes describing how Codex per-project config is
      generated (and how it relates to the `.codex/` symlink), and note that
      skills are handled in `add-agent-skills-support`.
- [ ] 3.2 Record migration guidance for projects currently relying on global
      `~/.codex/config.toml`.
