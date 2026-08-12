<!-- nbspec: change=retire-architecture-docs notebook=agents-common note=proposals/retire-architecture-docs/designs/architecture-retirement-design.md hash=sha256:c043f7e1badbf96fd403f9cbc0f5cf694fed5baafbe5a66378968bd63fc760d2 -->
# architecture-retirement-design

## Intent

Narrowed design for retiring **non-OpenSpec** `documentation/architecture/`
content under the human-authorized cleanup contract. OpenSpec stays at
`documentation/architecture/openspec/`. OpenSpec home move (D6) and
OpenSpec→Nbspec cutover are **out of scope** (follow-up todo
`todos/template/27`).

Tip implementation reference: local `xo` @ `265709c` (Owner-approved under
narrowed contract).

## Disposition matrix (non-OpenSpec)

| Former path | Disposition |
|-------------|-------------|
| `summary.rst`, `filesystem.rst`, `index.rst` | Delete |
| `decisions/*` ADRs | Delete (superseded/generic); durable package facts → subsystem README if still needed |
| `designs/` empty shells | Delete |
| `testplans/*` | Delete; pytest planning → `tests/**/README.md` + `tests.rst` |
| `openspec/**` | **Keep** (OPSX home; unchanged location) |
| Capability six specs | Currency audit/edits only; stay under openspec/specs |
| Root README | Never constraints/rationale home |
| This-repo Nbspec clone-topology trees | Unrelated prior work; Sphinx index only; not fleet cutover |

## Mechanisms in scope

### D9 instruction stop-ship

Explicit docs-1 file maps in `copier.yaml` and test profiles omitting
`architecture.rst`. Delete tracked distribution instruction copy.
Self-dogfood answers Copier-owned (may lag). Downstream residual →
agentsmgr/10.

### Commands

Source-first retarget in `components/contents/`; `agentsmgr generate`.
Remove `cs-architect` formally. Retain OpenSpec path citations where
needed. No Towncrier for distribution command content.

### Sphinx (this repo)

Stop specifications index OpenSpec glob. Exclude openspec tree from HTML
set as needed. Index existing local Nbspec docs. Label as project-local.

### Notes / prompts

Delete openspec-init; keep migrate-to-openspec. Clear `.auxiliary/notes`
after nb preserve.

## Out of scope mechanisms (do not implement under this id)

- Guarded populate migration to `documentation/openspec/`
- Template relocate of OpenSpec scaffolding
- Stopping population.py architecture/openspec create
- Migrating six specs to `documentation/specifications/`
- Deleting entire `documentation/architecture/` including openspec
- Marking template/16 complete

## Validation plan

- `agentsmgr generate --check` (artifact counts match command set)
- Focused agentsmgr tests
- Sphinx HTML (+ linkcheck when practical); legacy filesystem 404 gone
- No fleet Nbspec-home leakage in template/distribution/components
- issues/5 diff empty
- population.py OpenSpec block unchanged
- Residual list: copier-answers lag; agentsmgr/10; live openspec path hits

## WIP commit map (candidate / landed material)

| Commit | Role |
|--------|------|
| `27212b1` | Non-OpenSpec RST retirement + agentsmgr README |
| `411ca16` | multi-tool design pointer |
| `5da56dd` | D9 + cs-architect removal + command retargets |
| `9849054` | openspec-init + obsolete notes |
| `9c3bb20` | six-spec currency edits |
| `d712aad` | this-repo Sphinx |
| `265709c` | `.auxiliary/notes` removal + command retarget |

## Follow-up

New proposal via `todos/template/27` for D6 + Nbspec capability cutover.
Do not reuse this change id or older aggregate `72ea25ed...` as
authorization for that work.
