<!-- nbspec: change=retire-architecture-docs notebook=agents-common note=proposals/retire-architecture-docs/decisions/architecture-doc-decisions.md hash=sha256:c7c9ba18fe2fea48feb645f3831eecb4416b051370e629f87316aad74c45f18a -->
# architecture-doc-decisions

## D1 — Homes after non-OpenSpec architecture RST retirement

**Status:** Ratified for this narrowed change.

**Decision:** After deleting non-OpenSpec architecture RST:

1. **Capability contracts** that still use OpenSpec/OPSX remain under the
   existing buried home `documentation/architecture/openspec/` (unchanged
   location in this change).
2. **Code-local constraints/rationale** live in the nearest subsystem
   README under the project's actual source layout (layout-agnostic for
   the fleet; this-repo apply note may name `sources/agentsmgr/README.md`).
3. **Root README** is never the home for constraints/rationale.
4. **This repository** may already publish separate Nbspec-managed docs
   under `documentation/{specifications,designs,decisions}/` for unrelated
   changes (e.g. clone topology). That is project-local Sphinx content,
   not authorization of a fleet Nbspec cutover in this change.

## D2 — Delete superseded and generic material rather than migrate

**Status:** Ratified.

**Decision:** Superseded ADR-001-class content, empty design/testplan
shells, broken external link sections, stale file inventories, and
generic test-process prose are deleted without new homes. Git history
retains them. Still-current capability requirements stay in OpenSpec
specs (currency edits only).

## D3 — Capability spec currency audit only (no Nbspec migrate)

**Status:** Ratified (narrowed; supersedes earlier “migrate all six to
documentation/specifications/” for this change id).

**Decision:** Audit all six OpenSpec capability specs for currency.
Still-current requirements remain under
`documentation/architecture/openspec/specs/`. Obsolete scenarios may be
edited or deleted with reason. **No** migration of those specs into
Nbspec `documentation/specifications/` in this change. Full cutover is a
separate proposal.

## D4 — Agent command references via components + generate; remove cs-architect

**Status:** Ratified.

**Decision:**

1. Fix citations to deleted architecture paths in `components/contents/`,
   then regenerate `distribution/`. Do not hand-edit distribution as
   source of truth.
2. **Formally remove** `cs-architect` (component configuration, contents,
   and generated artifacts). No specification required its existence.
   Architecture work continues via OpenSpec/OPSX, subsystem READMEs, and
   remaining design/implementation commands. No Towncrier fragment
   (distribution command content is not on the agentsmgr Towncrier
   stream under current practice).

## D5 — No coupling to issues/5 autosquash guidance

**Status:** Ratified.

**Decision:** Do not rewrite `template/.auxiliary/agents/procedures/reviews.md`
autosquash inspect/apply guidance.

## D6 — OpenSpec home location unchanged (deferred)

**Status:** **Out of scope for this change** (explicit deferral).

**Decision:** Do **not** implement guarded populate migration, symlink
retarget to `documentation/openspec/`, template relocate, or stop
creating `documentation/architecture/openspec` in this change.
`population.py` and template OpenSpec scaffolding remain as today.
Later work requires a **new** proposal (see follow-up todo). This change
must not be cited as authorization for D6.

## D7 — Sphinx: this-repo publication; stop OpenSpec capability glob

**Status:** Ratified (narrowed).

**Decision:**

1. Stop `documentation/specifications/index.rst` from globbing
   `../architecture/openspec/specs/*/spec`.
2. Exclude the buried OpenSpec tree from the Sphinx HTML set as needed.
3. Index this repository's existing Nbspec-managed docs under
   `documentation/{specifications,designs,decisions}/` for Sphinx only.
4. Do not ship those paths as fleet architecture homes via template or
   distribution in this change.

## D8 — Single package README first (layout-agnostic)

**Status:** Ratified.

**Decision:** Prefer one package-level README per subsystem package in
the first pass. Nested READMEs only if unwieldy. This-repo apply-time
destination for agentsmgr rationale: `sources/agentsmgr/README.md`.

## D9 — Stop-ship architecture.rst via explicit docs-1 file map

**Status:** Ratified.

**Decision:**

1. Explicit docs-1 file map omitting `architecture.rst` in Copier
   defaults and default/maximum test profiles.
2. No new instruction-exclusion API.
3. Intentionally remove tracked
   `distribution/.../instructions/architecture.rst`; validate non-reselect.
4. Self-dogfood `.auxiliary/configuration/copier-answers--agents.yaml`
   remains Copier-owned; may still use `*.rst` until the next
   `copier update` picks up defaults (accepted residual).
5. No provenance-safe downstream stale auto-removal claim
   (`todos/agentsmgr/10` still open).
6. Do not silently delete downstream copies.

## D10 — Prompts and notes

**Status:** Ratified (narrowed).

**Decision:**

1. Delete `prompts/openspec-init.md`.
2. **Keep** `prompts/migrate-to-openspec.md` for unfinished fleet
   migrations.
3. Clear project-local `.auxiliary/notes` after preserving useful open
   items in nb; retarget commands so they do not teach that path.
