<!-- nbspec: change=add-clone-topology notebook=agents-common note=proposals/add-clone-topology/specifications/clone-topology.md hash=sha256:7e0eb480d4ed8d659af841c3ebe814377f45789a25893c3189cb4840a50bea57 -->
# clone-topology

## ADDED Requirements

### Requirement: Lane isolation by construction

Each lane seat SHALL operate in a full, independent local clone of its
project's primary repository. A lane clone SHALL share no mutable git state
with the primary or with any other lane: refs, branches, index, stash,
worktree metadata, hooks, local configuration, and reflogs are all
clone-private. The topology SHALL NOT rely on git worktrees for seat
isolation.

#### Scenario: Stash is lane-private

- **WHEN** two lanes each run `git stash push` concurrently
- **THEN** each entry lands on its own clone's `refs/stash`
- **AND THEN** neither lane can observe, clobber, or reorder the other's
  entries

#### Scenario: Hooks and config are lane-private

- **WHEN** a lane modifies its clone's hooks or local git configuration
- **THEN** no other lane's git behavior changes

### Requirement: Object storage via plain local clones

Lane clones SHALL be created as plain local-path clones of the primary
(`git clone <primary-path> <lane-path>`), yielding object-complete
repositories whose initial packs are hardlinked by git's local-clone
optimization where the filesystem supports it. Alternates, `--shared`, and
`--reference` SHALL NOT be used. Each clone SHALL be safe to
garbage-collect, repack, or delete independently of every other clone.
(Hardlinked packs are immutable files: repack in either repository writes
new files and unlinks old ones rather than mutating shared content, so a
hardlink can never propagate changes; deleting either repository only
decrements link counts.)

Local-path cloning can race with concurrent mutation of the source, so
provisioning SHALL obtain a consistent snapshot: a local-path clone SHALL
be created only while the primary is quiescent, under a provisioning lock
that excludes commits, ref updates, garbage collection, and repack for the
clone's duration. Alternatively, provisioning MAY use a transport mode
with snapshot semantics (the git transport via a `file://` URL) at the
cost of hardlink savings. Multiple lanes MAY be provisioned concurrently
against the same quiescent primary: the lock excludes primary mutation,
not sibling clone operations. After cloning, provisioning SHALL validate
branch tips by hash against the primary before the lane begins work.

#### Scenario: Independent garbage collection is safe

- **WHEN** `git gc` or a repack runs in any clone after stable creation
- **THEN** it considers only that clone's refs and reflogs
- **AND THEN** no object reachable in any other clone is affected

#### Scenario: Clone deletion is safe

- **WHEN** a lane clone is deleted at seat retirement
- **THEN** the primary and all other lane clones are unaffected

#### Scenario: Provisioning excludes source mutation

- **WHEN** a lane clone is provisioned over a local path
- **THEN** the provisioning lock holds the primary quiescent for the
  duration
- **AND THEN** a primary mutation attempted during provisioning waits or
  fails; it can never yield a torn clone

#### Scenario: Concurrent provisioning from one quiescent primary

- **WHEN** two lanes are provisioned concurrently from the same
  quiescent primary
- **THEN** both obtain consistent clones
- **AND THEN** both validate their branch tips by hash before their
  lanes begin work

### Requirement: Lineage and remote naming

The canonical lineage SHALL be: durable origin (bare repository in synced
storage, or a hosted remote) → primary clone (`~/src/<project>`) → lane
clones (`~/src/CLONES/<project>/<lane>`). In every clone, the remote named
`origin` SHALL point at that clone's immediate parent. Routine fetches flow
strictly downward (child fetches parent); parents read children only
through the review and integration flow.

If the primary is lost, recovery SHALL prefer recreating the primary from
the durable origin and then restoring each lane's parent URL. Primary
state the durable origin never received is recoverable only to the extent
surviving lanes fetched it: recovery SHALL treat surviving lanes'
remote-tracking refs as best-effort sources, inventory their union, and
verify candidate tips by hash and ancestry before adopting them into the
recreated primary. When no surviving lane fetched the newest primary
commits, recovery SHALL explicitly declare and accept the loss window
rather than assume completeness. A lane MAY re-point `origin` at the
grandparent temporarily, and that is an explicitly DEGRADED state: the
disabled push configuration SHALL be preserved, and the lane SHALL return
to normal lineage once the primary is restored.

#### Scenario: Primary loss and best-effort recovery

- **WHEN** the primary clone is lost
- **THEN** a replacement primary is recreated from the durable origin
- **AND THEN** the union of surviving lanes' remote-tracking refs is
  inventoried and candidate tips are verified by hash and ancestry
  before adoption, and lanes resume normal lineage

#### Scenario: Unfetched primary state is declared lost

- **WHEN** the lost primary held commits that no surviving lane and no
  durable origin ever received
- **THEN** recovery explicitly declares the loss window covering those
  commits
- **AND THEN** the recreated primary proceeds without silently claiming
  completeness

#### Scenario: Degraded grandparent operation is temporary

- **WHEN** a lane must continue work before the primary is restored
- **THEN** it re-points `origin` at the durable origin as a named
  degraded state, preserving its disabled push configuration
- **AND THEN** it returns to normal lineage once the primary exists
  again

### Requirement: Pull-based write authority

Lane agents SHALL NOT push to any repository. Integration SHALL be
pull-based: the integrator fetches lane refs from lane clones. Until a
capability-enforcement layer is deployed, the no-push rule is a
BEHAVIORAL rule backed by a fail-fast guardrail, not a capability
boundary, and SHALL be stated as such.

The guardrail: at provisioning, each lane clone's `origin` push URL SHALL
be set to a target that fails locally — before any name resolution,
credential lookup, or other network activity. The recommended shape is an
unregistered URL scheme (e.g. `disabled://push-refused`), which git
rejects at URL parsing on every platform. This guardrail intercepts only
default-remote pushes: explicit-URL pushes, newly added remotes, and URL
reconfiguration remain possible to a same-OS-user agent and are forbidden
by policy.

The capability layer that later makes the rule structural is: read-only
mounts or filesystem permissions for parent and peer clones, plus removal
of publication credentials and network authority from lane environments
(the container-sandboxing model). Acceptance tests for that layer SHALL
cover explicit-URL, force, delete, and multi-ref push attempts.
Publication (pushing the primary to durable origins) SHALL remain a
human-gated operation in every phase.

#### Scenario: Accidental push fails fast and locally

- **WHEN** a lane agent runs `git push` in its clone
- **THEN** the push fails at URL parsing against the disabled scheme
- **AND THEN** no name resolution, credential lookup, or ref
  negotiation occurs

#### Scenario: Capability layer covers non-default push paths

- **WHEN** the capability-enforcement layer is deployed
- **THEN** explicit-URL, force, delete, and multi-ref push attempts
  against parent or peer repositories fail by capability
- **AND THEN** acceptance tests exercise each of those attempt shapes

#### Scenario: Integration reads, never writes, the lane

- **WHEN** the integrator reviews a lane's work
- **THEN** they fetch from the lane clone through its named remote
- **AND THEN** the lane repository is never written to by the integrator

### Requirement: Branch ownership and naming

Within a lane clone, working branches SHALL be named for the change they
carry (existing convention, e.g. `add-clone-topology`); no seat prefix is
required because the integrator's remote-tracking namespace
(`refs/remotes/<lane>/...`) already disambiguates seats. New branches
SHALL base on `origin/<integration-branch>` as seen from the lane.

History rewriting SHALL follow review state. A lane MAY rewrite branches
freely while they are private and unreviewed. During review, findings are
addressed with targeted fixup commits that extend the stack; consolidating
them (autosquash) rewrites hashes and therefore stales any prior
hash-based review, requiring an updated review packet for the new hashes.
After final approval, the approved stack SHALL NOT be rewritten or
rebased; base advances are handled by the integration requirement below.

WIP commits (the stash replacement) SHALL carry intentional untracked
work by explicit staging; ephemeral and debug files SHALL live in ignored
scratch locations and are never carried by WIP commits. The owning lane
SHALL delete a working branch after observing, via fetch, that the
integrator has merged it. Force pushes require no separate policy: a
force push is a push, governed by the write-authority requirement's
behavioral rule, fail-fast guardrail, and eventual capability boundary
like any other push.

#### Scenario: Cross-seat name collision is impossible

- **WHEN** two lanes independently use the branch name `add-foo`
- **THEN** the integrator sees them as distinct remote-tracking refs
  under each lane's named remote

#### Scenario: Consolidation during review stales the packet

- **WHEN** a lane autosquashes review fixups into their targets before
  final approval
- **THEN** the rewritten hashes invalidate the prior review packet
- **AND THEN** the lane sends an updated packet for the new hashes

#### Scenario: Branch deleted after integration is observed

- **WHEN** the owning lane fetches and observes its branch merged into
  the integration branch
- **THEN** the lane deletes its local working branch

### Requirement: Review and integration flow

The integrator SHALL fetch lane refs through a named per-lane remote,
created at lane registration and removed — with its remote-tracking refs
pruned — at lane retirement. Review packets SHALL be hash-stable: they
identify the repository, the base branch and commit, the reviewed ref, and
the complete commit list by hash; nbspec-managed changes additionally bind
verdicts to the rendered-content aggregate hash. Integration merges SHALL
be performed `--no-ff` by the integrator into the integration branch.

When the integration base advances after final approval, the integrator
SHALL merge the approved tip into the current base when it merges
cleanly; the approved stack is NOT rebased merely because the base
advanced. A textually clean merge is not sufficient by itself: the
combined result SHALL pass the project's validation suite against the
advanced base before integration completes or publishes. Failed combined
validation BLOCKS integration; corrective commits carry new hashes and
follow normal review. If conflict resolution or policy requires rewriting
the approved stack, the approval becomes STALE and the rewritten range
requires renewed review through an updated packet. Continuous-integration
gates run where they run today — on hosted remotes after human
publication — and intra-fleet gating remains commit hooks in each clone
plus validation evidence carried in review packets.

#### Scenario: Fetch-based review

- **WHEN** the integrator fetches a lane's refs
- **THEN** review proceeds against immutable commit hashes
- **AND THEN** the lane pushed nothing to make that possible

#### Scenario: Base advance with clean merge preserves approved hashes

- **WHEN** the integration base advances after final approval and the
  approved tip merges cleanly
- **THEN** the integrator merges the approved tip as-is and every
  approved commit hash remains exactly as reviewed
- **AND THEN** the combined result passes validation against the
  advanced base before integration completes

#### Scenario: Combined-validation failure blocks integration

- **WHEN** the approved tip merges cleanly but the combined result
  fails validation against the advanced base
- **THEN** integration is blocked before completion or publication
- **AND THEN** corrective commits carry new hashes and follow normal
  review

#### Scenario: Required rewrite stales approval

- **WHEN** merging the approved tip requires rewriting or rebasing the
  approved stack
- **THEN** the prior approval is stale
- **AND THEN** the rewritten range is re-reviewed via an updated packet
  before integration

#### Scenario: Named remote lifecycle

- **WHEN** a lane is registered and later retired
- **THEN** the integrator's named remote for that lane is created at
  registration and removed at retirement
- **AND THEN** its remote-tracking refs are pruned at removal

### Requirement: Single-writer concurrency

Every repository in the topology SHALL have exactly one writing owner:
the seat that owns the clone, or the integrator for the primary. Until
the capability-enforcement layer exists, single-writer is a POLICY rule —
same-OS-user seats retain filesystem capability to write peer paths —
and the capability invariant to enforce when that layer lands is: each
seat holds write permission only on its own clone, and read permission on
its parent and peers. Peer-to-peer lane reads (fetch for cross-review)
are PERMITTED, read-only, under the same review-without-execution rules
as integrator review. Cross-seat reads are safe against concurrent
writes because git ref updates are atomic: a fetch observes pre-update or
post-update state, never partial state.

#### Scenario: Fetch during a lane commit

- **WHEN** the integrator fetches while the lane is mid-commit
- **THEN** the fetch returns a consistent snapshot of the lane's refs
- **AND THEN** neither repository is corrupted or left in partial state

#### Scenario: Crossed review requests

- **WHEN** two review requests race in the message queue
- **THEN** each is evaluated against the explicit commit hashes it names
- **AND THEN** message ordering cannot change what was reviewed

#### Scenario: Peer lane read for cross-review

- **WHEN** lane A fetches lane B's refs for a peer review
- **THEN** the fetch is read-only and lane B is never written
- **AND THEN** review-without-execution rules apply to the fetched refs

### Requirement: Lane lifecycle

Lane clones SHALL be created at seat provisioning by bootstrap tooling:
clone per the object-storage requirement (quiescent primary or snapshot
transport), disable the push URL per the write-authority requirement,
install hooks and project-local tool configuration from the project
template rather than inheriting any shared state, and create the lane's
local working branches at verified tips (a fresh clone carries source
branches primarily as remote-tracking refs). The canonical lane
identifier SHALL be the agentmux bundle lane name, normalized to
lowercase at provisioning; provisioning SHALL reject names that collide
after normalization. The agentmux bundle SHALL record the
session-to-clone mapping (lane name and clone path).

Template hook updates do not propagate to existing clones automatically;
refresh mechanics are DEFERRED to provisioning tooling, but doctor checks
SHALL report installed-versus-template hook drift so staleness is
visible, and nothing outside the lane mutates a lane's hooks mid-session.

Retirement SHALL verify both that no unmerged work exists — the
integrator fetches the lane with `--prune` and confirms every lane branch
is merged or explicitly abandoned — AND that the lane working tree holds
no undispositioned dirty or untracked content, before the clone directory
is deleted.

Doctor checks SHALL verify, per clone: the `origin` URL matches the
recorded lineage (from the bundle mapping; validation against a
repository policy file is DEFERRED and doctor SHALL NOT require that file
until its owning proposal lands), the push URL is disabled, the
integration base resolves, and hook drift per above. Disk-use checks are
DEFERRED until a threshold policy exists.

#### Scenario: Provisioning yields a compliant clone

- **WHEN** bootstrap tooling provisions a lane
- **THEN** the resulting clone has a parent-pointing `origin`, a
  disabled push URL, template-installed hooks and tool configuration, a
  lowercased lane identifier, and local working branches at verified
  tips

#### Scenario: Retirement refuses while work is unmerged

- **WHEN** a seat is retired while its clone holds an unmerged branch
- **THEN** cleanup refuses until the branch is merged or explicitly
  abandoned by the integrator

#### Scenario: Retirement refuses undispositioned content

- **WHEN** a seat is retired while its working tree holds dirty or
  untracked content
- **THEN** cleanup refuses until that content is committed, migrated,
  or explicitly discarded

### Requirement: Review without execution

Fetching refs SHALL execute no fetched code: git transports objects and
refs only — hooks, local configuration, and their execution context are
never transported. The integrator SHALL review fetched refs from the
object store (`git show`, `git diff`, rendered artifacts) and SHALL NOT
check out a fetched review ref into a working tree whose hook path
resolves inside that tree, since checkout would then swap hook content
under control of the reviewed branch. Building or testing a fetched ref
is code execution and SHALL occur only in the authoring lane or in a
sandbox, never implicitly as part of review.

#### Scenario: Fetch is inert

- **WHEN** the integrator fetches a lane ref that modifies hook sources
- **THEN** nothing executes and the integrator's active hooks are
  unchanged

#### Scenario: File-level inspection avoids checkout

- **WHEN** review requires reading files from the fetched ref
- **THEN** inspection uses object-store reads rather than checking the
  ref out in the integration clone

### Requirement: Portability

The topology SHALL rely only on git behaviors portable across Linux,
macOS, and Windows: local-path clones (the hardlink optimization degrades
to plain copy where unsupported), no symlinks, no socket dependencies in
the git layer, and lane names lowercased at provisioning (per the
lifecycle requirement) to avoid case-only collisions on case-insensitive
filesystems. The path roots (`~/src`, `~/src/CLONES`) SHALL be
convention defaults resolved against the platform home directory, not
hardcoded absolute paths.

#### Scenario: Filesystem without hardlink support

- **WHEN** a lane clone is provisioned on a filesystem that does not
  support hardlinks
- **THEN** the clone falls back to copying objects
- **AND THEN** every other property of this specification holds
  unchanged

### Requirement: Migration and rollback

Migration SHALL proceed seat by seat with no loss of work, in this order:

1. Inventory the worktree: tracked modifications, untracked and ignored
   files, detached HEAD, and in-progress operations. Migration SHALL NOT
   proceed while a rebase, merge, bisect, or similar operation is in
   progress.
2. Commit tracked work (WIP commits permitted). Stage intentional
   untracked work into WIP commits explicitly; remaining untracked and
   ignored content SHALL be explicitly dispositioned — carried over,
   relocated to scratch, or intentionally discarded — never silently
   dropped.
3. If the worktree is at a detached HEAD, create a named recovery branch
   at that commit before proceeding.
4. Provision the lane clone. A clone of the primary carries source
   branches primarily as remote-tracking refs: migration SHALL create the
   lane's local working branches at the verified source tips.
5. Compare ALL migrated refs by hash between worktree and clone.
6. Retain both the worktree and the clone until acceptance completes;
   only then remove the worktree and repoint the seat's working
   directory and bundle mapping at the clone.

Rollback SHALL be symmetric: worktrees can be recreated from the primary
at any time, and a lane clone SHALL NOT be deleted until its branches are
merged or migrated. Review context (notebooks, verdicts, review packets)
is topology-independent and unaffected in both directions.

#### Scenario: Migration preserves work by hash

- **WHEN** a seat migrates from worktree to lane clone
- **THEN** every migrated ref in the clone matches the worktree's tip
  hash, with local working branches created from remote-tracking refs
- **AND THEN** the worktree is removed only after acceptance completes

#### Scenario: Dirty, detached, and untracked state migrates explicitly

- **WHEN** a migrating worktree holds uncommitted changes, untracked
  files, and a detached HEAD
- **THEN** migration creates a named recovery branch for the detached
  commit, commits or explicitly dispositions all content, and refuses
  while any operation is in progress

#### Scenario: Rollback to worktrees

- **WHEN** migration must be reversed for a seat
- **THEN** a worktree is recreated from the primary and the lane clone
  is retained until its unmerged branches are recovered
