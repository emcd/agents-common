<!-- nbspec: change=retire-architecture-docs notebook=agents-common note=proposals/retire-architecture-docs/specifications/documentation-ownership.md hash=sha256:b212a40ae0df569ad7ac16ab3c0611113a776bb182acd511f1359adc949ba158 -->
# documentation-ownership

## Purpose

Define what this narrowed change requires when retiring **non-OpenSpec**
content under `documentation/architecture/`, while OpenSpec/OPSX remains
at its current buried home, and while OpenSpec→Nbspec cutover and OpenSpec
home relocation remain separate future work.

## ADDED Requirements

### Requirement: Non-OpenSpec architecture RST is retired

Implementation SHALL delete non-OpenSpec documentation under
`documentation/architecture/` that is not part of the OpenSpec/OPSX
scaffolding tree, including summary, filesystem, ADR/decisions shells,
empty designs/testplans shells, and the architecture index, after each
item has an explicit delete or migrate-to-subsystem-README disposition.

#### Scenario: Non-OpenSpec shells absent

- **WHEN** the change is implemented at tip
- **THEN** `documentation/architecture/summary.rst`,
  `filesystem.rst`, legacy ADR/designs/testplans trees, and
  `architecture/index.rst` are absent
- **AND THEN** Sphinx builds without depending on those paths

#### Scenario: OpenSpec tree retained

- **WHEN** the change is implemented at tip
- **THEN** `documentation/architecture/openspec/` remains the buried
  OpenSpec/OPSX home for this change
- **AND THEN** this change does not require deleting that tree

### Requirement: Subsystem README for code-local rationale

Code-local constraints and design rationale SHALL live in the nearest
subsystem README under the repository's actual source layout. Root
README files SHALL NOT hold architectural constraints or design
rationale.

#### Scenario: Package rationale

- **WHEN** package-local layout or hybrid-distribution rationale is
  documented for agentsmgr in this repository
- **THEN** it is written primarily to that package's README
  (apply-time: `sources/agentsmgr/README.md`)
- **AND THEN** it is not placed only under deleted architecture RST paths

#### Scenario: No root README constraints

- **WHEN** subsystem constraints or rationale are migrated
- **THEN** they are not written into root `README.md` / `README.rst` as
  the durable home

### Requirement: OpenSpec home and populate behavior unchanged

This change SHALL NOT alter the OpenSpec buried-home location, root
`openspec` managed-symlink behavior, or `agentsmgr populate` logic that
ensures `documentation/architecture/openspec` and the root symlink.
Template OpenSpec scaffolding under
`template/documentation/architecture/openspec/` SHALL remain unless a
separate change relocates it.

#### Scenario: Populate still provides current OpenSpec shape

- **WHEN** `agentsmgr populate project` runs after this change
- **THEN** it may still ensure `documentation/architecture/openspec`
  and a root `openspec` symlink to that path as before
- **AND THEN** this change does not introduce migration to
  `documentation/openspec/` or equivalent

### Requirement: OpenSpec capability specs stay under OpenSpec

The six capability specifications under
`documentation/architecture/openspec/specs/` SHALL remain the living
homes for still-current agentsmgr capability requirements in this
change. Implementation MAY edit obsolete scenarios in place. This change
SHALL NOT migrate those requirements into
`documentation/specifications/` as an OpenSpec→Nbspec cutover.

#### Scenario: Currency audit without cutover

- **WHEN** the six specs are audited
- **THEN** each still-current requirement remains under the OpenSpec
  specs tree
- **AND THEN** obsolete material may be removed or corrected with reason
- **AND THEN** no requirement is moved to Nbspec solely by this change

### Requirement: This-repo Nbspec Sphinx publication is not fleet cutover

If this repository already has Nbspec-managed documents under
`documentation/specifications/`, `documentation/designs/`, or
`documentation/decisions/`, Sphinx MAY publish them. The specifications
index SHALL NOT glob OpenSpec capability specs from
`documentation/architecture/openspec/`. Template and distribution SHALL
NOT gain those three directories as fleet architecture homes solely because
of this change.

#### Scenario: Specifications index does not glob OpenSpec specs

- **WHEN** Sphinx builds the specifications toctree after implementation
- **THEN** it does not include `../architecture/openspec/specs/*/spec`

#### Scenario: No fleet Nbspec-home leakage

- **WHEN** `template/`, `distribution/`, and `components/` are inspected
- **THEN** they do not teach `documentation/specifications|designs|decisions`
  as the fleet replacement for OpenSpec capability homes in this change

### Requirement: Instruction source selection omits architecture.rst

Stop-shipping of the upstream `architecture.rst` instruction SHALL use an
explicit file map for `github:emcd/python-project-common@docs-1` (and
equivalent) that omits `architecture.rst`, applied in Copier template
defaults and default/maximum test profiles. This change SHALL NOT add a
new instruction-exclusion API.

Tracked `distribution/per-project/general/instructions/architecture.rst`
SHALL be removed intentionally in this repository. Self-dogfood Copier
answers MAY remain Copier-owned and lag until the next `copier update`.
Downstream copies SHALL NOT be silently deleted; residual cleanup remains
under `agents-common:todos/agentsmgr/10`.

#### Scenario: Defaults and profiles omit architecture.rst

- **WHEN** Copier template defaults and test profiles are inspected
- **THEN** `architecture.rst` is absent from the explicit docs-1 map

#### Scenario: Distribution artifact removed intentionally

- **WHEN** this change is implemented in agents-common
- **THEN** `distribution/per-project/general/instructions/architecture.rst`
  is absent as an intentional deletion
- **AND THEN** generation does not re-select it under the updated maps

#### Scenario: Downstream residual accepted

- **WHEN** a downstream project still has a previously populated
  `architecture.rst`
- **THEN** this change does not silently delete it
- **AND THEN** `todos/agentsmgr/10` remains the cleanup home

### Requirement: Command and prompt guidance consistency

Live command and prompt guidance SHALL not cite deleted non-OpenSpec
architecture paths as current procedure. Citations to the retained
OpenSpec home MAY remain. The `cs-architect` command SHALL be removed.
`prompts/openspec-init.md` SHALL be deleted. `prompts/migrate-to-openspec.md`
SHALL be retained for unfinished fleet migrations unless a later change
removes it.

#### Scenario: No citations to deleted RST shells

- **WHEN** component sources and generated distribution commands are
  inspected
- **THEN** they do not reference deleted summary/filesystem/ADR/testplan
  architecture paths as live homes
- **AND THEN** they may still reference
  `documentation/architecture/openspec/` where OPSX requires it

#### Scenario: cs-architect removed

- **WHEN** components and distribution are inspected after implementation
- **THEN** `cs-architect` configuration and generated command files are
  absent

#### Scenario: migrate prompt kept; init prompt removed

- **WHEN** `prompts/` is inspected
- **THEN** `migrate-to-openspec.md` is present
- **AND THEN** `openspec-init.md` is absent

### Requirement: Project-local notes path retired

Project-local `.auxiliary/notes` durable content used by this repository
SHALL be cleared after useful open items are preserved in the project
notebook. Agent commands SHALL NOT teach creating new durable trackers
under `.auxiliary/notes/`.

#### Scenario: notes directory absent; commands do not teach it

- **WHEN** the change is implemented
- **THEN** `.auxiliary/notes` is absent from the tip tree (aside from
  git history)
- **AND THEN** distributed commands do not instruct agents to create
  new issue files under `.auxiliary/notes/`

### Requirement: Separation from unrelated work and deferred cutover

Implementation SHALL NOT modify issues/5 autosquash guidance. This change
SHALL NOT claim to implement `todos/agentsmgr/10`. This change SHALL NOT
authorize later OpenSpec home relocation or OpenSpec→Nbspec cutover;
those require a separate proposal.

#### Scenario: reviews.md autosquash guidance untouched

- **WHEN** the change diff is inspected
- **THEN** `template/.auxiliary/agents/procedures/reviews.md` autosquash
  inspect/apply guidance is unchanged

#### Scenario: Deferred cutover not authorized

- **WHEN** this change is merged
- **THEN** it is not cited as completing D6 or Nbspec capability cutover
- **AND THEN** `todos/template/16` is not marked complete solely because
  of this change
