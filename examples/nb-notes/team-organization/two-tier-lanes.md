# <Project> two-tier lane org chart

#coordination #org-chart #policy #status-active

Use this topology when a project has a coordinator, multiple lane owners, and
one or more implementation agents under each lane. This note is stable policy.
Update it for real org, branch-topology, or signoff changes. Put staffing churn
in living-roster notes linked below.

## Reporting Lines

### Human / Product Owner

- <Human/Product Owner> - product direction, final authority, optional code/design review.

### Project Coordination

- <Coordinator> (`<coordinator>@<bundle>`) - runs standups, sequences lane work, merges integration branches to `master`, and maintains cross-lane hygiene.

### Lane Owners / Tech Leads

| Lane | Integration Branch | Owner | Agentmux ID | Owns |
|------|--------------------|-------|-------------|------|
| <Lane A> | `<lane-a>` | <Lane A Lead> | `<lane-a>@<bundle>` | <Primary ownership surface> |
| <Lane B> | `<lane-b>` | <Lane B Lead> | `<lane-b>@<bundle>` | <Primary ownership surface> |
| <Lane C> | `<lane-c>` | <Lane C Lead> | `<lane-c>@<bundle>` | <Primary ownership surface> |
| <Lane D> | `<lane-d>` | <Lane D Lead> | `<lane-d>@<bundle>` | <Primary ownership surface> |

Lane owners report to the Coordinator for coordination and to the Product Owner
for product direction.

## Special Roles

### Dedicated Reviewers

| Role | Agentmux ID | Reviews | When Included |
|------|-------------|---------|---------------|
| <Lane A Reviewer> | `<lane-a-reviewer>@<bundle>` | <Lane A risk surface> | High-judgment or release-blocking lane reviews |
| <Lane B Reviewer> | `<lane-b-reviewer>@<bundle>` | <Lane B risk surface> | High-judgment or release-blocking lane reviews |
| <Domain / Security / QA Reviewer> | `<reviewer>@<bundle>` | <Cross-cutting risk surface> | Cross-lane or specialist reviews |

Reviewers may observe standups in lightweight mode. They should reply only when
asked or when they spot a material review-risk issue.

### Editor General

- Scope:
  - Cross-lane mechanical refactors.
  - Nomenclature, documentation, stale README, and practices audits.
  - Proposal writing or review for cross-cutting mechanical changes.
- Out of scope:
  - Lane-owned implementation work unless explicitly delegated.
- Routing:
  - Cross-lane tasks come from the Coordinator.
  - In-lane findings go to the lane owner.

### Advisor

- Scope:
  - High-touch implementation.
  - Proposal and code review.
  - Product/design feedback.
- Reports findings to:
  - <Human/Product Owner>.
  - The relevant Coordinator or lane owner.

## Lane Engineers

| Lane | Engineers |
|------|-----------|
| <Lane A> | `<engineer-a>@<bundle>`, `<engineer-b>@<bundle>` |
| <Lane B> | `<engineer-c>@<bundle>`, `<engineer-d>@<bundle>` |
| <Lane C> | `<engineer-e>@<bundle>` |
| <Lane D> | `<engineer-f>@<bundle>` |

## Integration Branch Topology

Each lane owner owns an integration branch under `master`.

- Merges flow up: leaf branch -> integration branch -> `master`.
- Rebases flow down: leaf branches rebase onto their lane integration branch; lane integration branches rebase onto `master` only when safe.
- Use `--no-ff` between shared branches to preserve lane boundaries and single revert points.
- Do not rebase shared/stable branches once other branches depend on them unless the lane coordinates a freeze or rebase window.

## Responsibilities By Level

### Engineers

- Rebase private leaf branches onto the lane integration branch to stay current.
- Request lane-owner review/merge with commit hashes and validation.
- Only rebase branches that are private and not used by other collaborators.

### Lane Owners

- Size work into coherent, reviewable units.
- Merge approved leaf branches into the lane integration branch with `--no-ff`.
- Rebase the lane integration branch onto `master` before requesting Coordinator merge when safe.
- Request Coordinator merge into `master` with validation and known risks.

### Coordinator

- Merge approved integration branches into `master` with `--no-ff`.
- Resolve cross-lane conflicts before merging.
- Maintain org notes, signoff policy, and cross-lane handoffs.

## Signoff Policy

| Change Category | Required Signoff |
|-----------------|------------------|
| Core runtime or state invariants | <Owning Lane Lead> |
| Public API, tool, or integration contracts | <Relevant Lane Lead> + <Coordinator> |
| Data shape, schema, or migration changes | <Data/Domain Lane Lead> |
| User-visible interaction or presentation changes | <Frontend/UI Lane Lead> + affected lane owner |
| Cross-lane mechanical refactors | <Editor General> + affected lane owners |
| Release/shared-branch publication | <Coordinator> + <Human/Product Owner if required> |

## Living-Roster Notes

- `coordination/<lane-a>/<n>` - <Lane A> roster and notebook taxonomy.
- `coordination/<lane-b>/<n>` - <Lane B> roster and notebook taxonomy.
- `coordination/<lane-c>/<n>` - <Lane C> roster and notebook taxonomy.

## Related Procedures

- `procedures/general/<n>` - work unit sizing and merge acknowledgments.
- `procedures/reviews/<n>` - project-specific review packet additions, if any.
- `procedures/editor/<n>` - Editor General operating procedures, if used.
