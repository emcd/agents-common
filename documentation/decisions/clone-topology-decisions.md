<!-- nbspec: change=add-clone-topology notebook=agents-common note=proposals/add-clone-topology/decisions/clone-topology-decisions.md hash=sha256:64e8a4a53d81a41f6c0aafd8660cb7f26a45504d1aafee340d59b4a7a3558da0 -->
# clone-topology-decisions

Resolved decisions constraining this change, each with provenance.
Reviewers should treat these as settled inputs; the genuinely open choices
live in the "Open decisions" section of topology-design, and
review-resolved contract choices live in its "Review resolutions" section.

## Decision: Clones of clones replaces worktrees as the seat isolation primitive

- Status: RESOLVED — Eric, 2026-07-11; discussion recorded in
  agents-common:issues/git/1 (Advisor assessment, Eric-discussed).
- The shared common-`.git` defect class (stash, branch namespace, hooks,
  config, GC, ambient environment) is addressed by changing the topology,
  not by patching symptoms individually. Candidate direction 3 of
  issues/git/1 ("reconsider worktrees as the isolation primitive") was
  endorsed as the real fix.

## Decision: Plain local clones; alternates, --shared, and --reference rejected

- Status: RESOLVED — Eric-ratified 2026-07-11; issues/git/1
  ("Disk/--reference" paragraph).
- Same-filesystem clones hardlink existing packs at clone time, so most
  disk savings arrive free. Alternates would add ongoing dedup but import
  the classic corruption mode (source repository pruning objects a
  borrower still needs) and path-identity constraints inside containers.
  Revisit only if a repository's history grows large enough to matter.
- Scope note (review round, 2026-07-12): this decision covers post-clone
  object independence; the provisioning-time source-mutation race is a
  separate concern, addressed normatively in the object-storage
  requirement (quiescent-primary lock or `file://` snapshot transport).

## Decision: git stash is banned in lane workflows; WIP commits replace it

- Status: RESOLVED — adopted as immediate interim guidance 2026-07-11;
  issues/git/1 candidate direction 1, Eric-discussed.
- A stash is just a commit; a WIP commit plus later `reset --soft` or
  squash gives the same ergonomics per-branch with no shared stack.
  Untracked content is covered by explicit staging into WIP commits, with
  ephemeral/debug files kept in ignored scratch locations (review round,
  2026-07-12). Applies under both topologies, effective before migration;
  later becomes a mechanical refusal in the planned version-control MCP
  server. The per-lane stash-namespace alternative (candidate 2) was
  rejected: bare `git stash` would remain reachable by reflex.

## Decision: Propagation cost accepted as roughly unchanged

- Status: RESOLVED — Eric's correction, 2026-07-11; issues/git/1.
- "One fetch updates all lanes" was only partially true for worktrees:
  engineer worktrees already require individual rebases onto their
  integration branches. Explicit per-lane fetch+rebase under clone
  topology is comparable work, not new cost. Freshness observability
  (ahead/behind against the integration base) is the mitigation either
  way.

## Decision: Repository policy is declared in the repository; formalization deferred

- Status: RESOLVED in direction — Eric ratified policy-in-repo
  2026-07-11 (home:ideas/projects/2, open question 2); schema and format
  deferred to the vcs-mcp proposal so the policy file has exactly one
  normative home.
- The repository declares its own branch policy (topology, integration
  branches, protected refs) as checked-in configuration riding the same
  review and merge gates as code; lane-to-seat assignment remains an
  agentmux bundle concern.
- Schedule-risk acknowledgment (XO review, 2026-07-12): nothing in this
  change depends on that file existing. Doctor checks validate lineage
  against the agentmux bundle mapping until the policy file lands, and
  the lifecycle requirement states explicitly that doctor SHALL NOT
  require the file before its owning proposal lands. If vcs-mcp is
  delayed indefinitely, this change remains fully operable.

## Decision: Container compatibility is a hard design constraint

- Status: RESOLVED — Eric, 2026-07-11 (recorded in issues/git/1):
  containers are worth the mount pain because they improve both the Git
  experience and safety/friction independently of the MCP server.
- The isolation model must map onto the merged agentmux
  container-sandboxing shape: primary as read-only bind mount, lane
  writable. Full clones satisfy this; worktrees structurally cannot
  (their state lives inside the shared `.git`). The container layer is
  also what upgrades the no-push and single-writer rules from policy to
  capability boundaries (write-authority and concurrency requirements).
