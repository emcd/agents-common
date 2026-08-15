<!-- nbspec: change=add-clone-topology notebook=agents-common note=proposals/add-clone-topology/designs/topology-design.md hash=sha256:15e268f183ad2cd8e9f70c79044c3c94e88712c451cdbbf9653f6986420b897f -->
# topology-design

## Current topology: shared-repository worktrees

```
                 +---------------------------+
                 |  durable origin           |
                 |  (Dropbox bare / GitHub)  |
                 +------------+--------------+
                              | push/fetch (human only)
                 +------------+--------------+
                 |  ~/src/<project>          |  primary clone
                 |  ONE shared .git:         |
                 |  objects, refs, stash,    |
                 |  hooks, config, reflogs   |
                 +--+---------+---------+----+
          worktree |          |         | worktree
                   |          |         |
     ~/src/WORKTREES/  ~/src/WORKTREES/  ...
     <project>/laneA   <project>/laneB
     (private: HEAD, index, merge state — everything else shared)
```

Shared mutable surfaces: branch namespace, `refs/stash` (a single stack),
hooks, local config, packed-refs, reflogs, object store + GC, and the
`GIT_DIR`-shaped ambient environment that produced the nbspec:issues/4
incident class. A lane worktree cannot run with the primary mounted
read-only, because all of its operations write into the shared `.git`.

## Proposed topology: clones of clones

```
                 +---------------------------+
                 |  durable origin           |
                 |  (Dropbox bare / GitHub)  |
                 +------------+--------------+
                       push ^ | fetch          (human only)
                 +------------+--------------+
                 |  ~/src/<project>          |  primary / integration clone
                 |  owner: integrator        |  origin -> durable origin
                 +--+---------------------+--+
        fetch ^    | clone/fetch          | clone/fetch
     (review only) v                      v
     ~/src/CLONES/<project>/laneA   ~/src/CLONES/<project>/laneB
     full clone                      full clone
     origin -> primary               origin -> primary
     push URL disabled               push URL disabled
```

Every arrow that moves work upward is a FETCH performed by the parent
(kernel-style dictator-and-lieutenants). Write authority flows downward
and matches the org chart.

## Rationale

- **Isolation by construction, not by discipline.** Every surface in the
  shared-state list above becomes clone-private. The stash race, the hook
  sabotage surface, and the cross-lane GC hazard cease to exist rather
  than being mitigated.
- **The no-push constraint gains layered enforcement.** Today it is
  prose in AGENTS.md. Under this topology it gains an immediate
  fail-fast guardrail (disabled push URL intercepting default-remote
  pushes) and a defined path to a true capability boundary (read-only
  mounts/permissions plus credential and network scoping under the
  container layer). Until that layer deploys, the rule remains
  behavioral and is stated as such — same-user filesystem access means
  a lane *could* write peer paths; policy forbids it and the spec names
  the enforcement layer that will remove the capability.
- **One-tier extension of the existing convention.** Durable bare origin
  → primary clone is already how repos bootstrap; lane clones add one
  tier with the same mechanics.
- **Container compatibility is decisive.** A lane clone maps directly
  onto the merged agentmux container-sandboxing model: primary as
  read-only bind mount, lane clone inside the writable overlay slice.
  Adopting this topology now makes the container migration a mount-table
  change, not a topology change — and it is also what turns the
  policy rules above into capability boundaries.
- **Per-lane hooks/config duplication is a feature.** Today any lane can
  sabotage every lane's hooks; isolated clones end that. The duplication
  cost lands on bootstrap tooling, where it belongs. (This generalizes
  beyond hooks: debug builds of agentmux and litrpg discover
  configuration via the git common dir, which becomes clone-private
  under this topology — per-lane tool configuration to mutate during
  testing instead of racing on a shared one.)

## Alternatives considered

1. **Keep worktrees, ban stash (guidance only).** Treats the loudest
   symptom; leaves branch-namespace races, shared hooks/config, GC
   collisions, and container incompatibility in place. Adopted only as
   interim guidance until migration completes.
2. **Per-lane stash ref namespace** (`refs/agentmux-stash/<lane>` via
   plumbing). Rejected: requires wrapper tooling anyway, at which point
   WIP commits are simpler — and bare `git stash` still exists for agents
   to reach for by reflex. A remedy the old habit can bypass is not a
   remedy.
3. **Alternates / `--reference` / `--shared` clones.** Rejected
   (Eric-ratified): imports the classic corruption mode — the source
   repository pruning objects a borrower still needs — plus path-identity
   constraints inside containers. Plain local clones already get most of
   the disk savings free via git's hardlink optimization, which shares
   only immutable pack files and degrades safely (repack-and-unlink, never
   in-place mutation).
4. **Lanes clone the durable origin directly (skip the primary).**
   Rejected: the integration branch and review state live in the primary;
   parenting lanes to the durable origin would put a sync boundary
   (Dropbox or network) inside the review loop and detach lanes from the
   integrator's state by default.

## Cost accepted

Propagation is per-lane under either topology (Eric's correction,
2026-07-11): worktree lanes already rebase individually onto their
integration branches, so explicit per-lane fetch+rebase is comparable
work, not new work. Freshness observability (ahead/behind against
`origin/<integration>`) is the mitigation either way and is a core reason
the vcs-mcp `status` operation exists.

## Review resolutions (2026-07-12, Owner + XO revise round)

- **Approved-history contract** (Owner correction to XO Severity 1):
  rebasing cannot reparent approved commits while preserving their
  hashes — there is no "rebase only the WIP boundary" that keeps
  approved hashes on a new base. Resolved contract: during review,
  fixups extend the stack and consolidation stales the packet; after
  final approval, the integrator merges the approved tip into the
  advanced base when clean; any required rewrite stales approval and
  triggers re-review of the new hashes. No "delta verdict" is promised
  for ordinary git commits — that term stays nbspec-specific.
- **Named integrator remotes** (Owner finding 4): decision CLOSED in
  favor of named per-lane remotes, created at lane registration and
  removed with pruning at retirement — stable audit and review
  namespaces. Ephemeral path fetches are no longer a sanctioned
  alternative.
- **Disabled-push shape** (XO Severity 2): pinned to fail-locally
  semantics with a recommended unregistered-scheme URL
  (`disabled://push-refused`), which fails at URL parsing on every
  platform with no name resolution or credential lookup.
- **Provisioning race** (Owner finding 3): local-path cloning of a
  mutating source is the documented race; resolved via
  quiescent-primary provisioning lock, with `file://` transport as the
  snapshot-semantics alternative.

## Open decisions

- **Path root for lane clones.** `~/src/CLONES/<project>/<lane>` is the
  working convention (parallel to `~/src/WORKTREES`); the name and
  location are convention defaults, not load-bearing.
- **Policy file formalization.** The repo policy declaration (topology,
  integration branch, protected refs) is deferred to the vcs-mcp
  proposal so it has exactly one normative home; this spec is written to
  be readable as its input, and doctor checks in this change explicitly
  do not require that file until the owning proposal lands.



## Review resolutions addendum (round 3, Owner verdict 2026-07-12)

- **Recovery is best-effort, never assumed complete**: a surviving lane
  holds only what it fetched, so "recoverable from any lane" was an
  overclaim. Recovery inventories the UNION of surviving lanes'
  remote-tracking refs, verifies candidate tips by hash and ancestry,
  and explicitly declares the loss window when no lane fetched the
  newest primary commits.
- **Textual merge cleanliness is not semantic validity**: a clean merge
  of an approved tip into an advanced base must pass combined-result
  validation before integration completes or publishes; failure blocks
  integration and corrective hashes follow normal review.
- **"No push path exists" claim removed**: force pushes are pushes,
  governed by the write-authority requirement's layered enforcement —
  the vacuous-policy phrasing contradicted the behavioral-vs-capability
  correction from round 2.
