# <Lane> living roster and notebook taxonomy

#coordination #component-<lane> #status-active

This note tracks current staffing and lane-specific notebook conventions. Update
it in place when roles or lane taxonomy change.

## Roster

| Role | Agentmux ID | Worktree / Branch | Owns | Current Focus |
|------|-------------|-------------------|------|---------------|
| <Lane Owner> | `<lane>@<bundle>` | `<branch>` | Lane integration, review, dispatch | <focus> |
| <Engineer A> | `<engineer-a>@<bundle>` | `<branch>` | <subcomponent> | <focus> |
| <Engineer B> | `<engineer-b>@<bundle>` | `<branch>` | <subcomponent> | <focus> |
| <Reviewer> | `<reviewer>@<bundle>` | `<branch>` | Review risk surface | <focus> |

## Lane Notebook Taxonomy

- `coordination/<lane>` - lane handoff and roster notes.
- `todos/<lane>` - actionable implementation work.
- `issues/<lane>` - bugs and known issues.
- `reviews/<lane>` - review context and findings.
- `procedures/<lane>` - lane-specific smoke tests and checklists.

## Escalation

- <Escalation rule for public contracts or cross-lane effects.>
- <Escalation rule for release or shared-branch publication.>

## Related

- `coordination/general/<n>` - project org chart and signoff policy.
- `coordination/<lane>/<n>` - rolling handoff.
