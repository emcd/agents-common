# <Project> team coordination

#coordination #org-chart #policy #status-active

## Roles

| Role | Agentmux ID | Owns | Merge Authority |
|------|-------------|------|-----------------|
| <Project Owner> | `<owner>@<bundle>` | Architecture, roadmap, final technical decisions | May prepare merges; shared-branch publication requires human approval unless explicitly delegated |
| <Project XO> | `<xo>@<bundle>` | Operational continuity, delegated implementation, review commits | No shared-branch publication without approval |
| <Human Operator> | n/a | Product direction, role changes, final push/merge authority | Final authority |

## XO Lane

The XO may handle scoped work delegated by the owner or human operator:

- Implement well-bounded changes with stated acceptance criteria.
- Keep generated and source templates synchronized when ownership is clear.
- Prepare local/private review commits with validation evidence.
- Update rolling handoffs and todos when durable coordination state changes.

## Escalation

Escalate before deciding:

- Public contracts, CLI behavior, data layout, or distribution boundaries.
- Supported tool/coder additions or removals.
- Cross-project coordination policy changes.
- Work that requires an OpenSpec proposal.
- Any merge, push, or shared-branch publication not explicitly approved.

## Review Flow

1. XO implements the scoped change and runs validation.
2. XO creates a local/private review commit.
3. XO sends the commit hash, changed-file summary, validation results, and blockers or design questions.
4. Owner reviews and approves or requests changes.
5. Human operator decides whether to merge or push if shared branches are involved.

## Related Notes

- `coordination/general/<n>` - rolling project handoff.
- `coordination/xo/<n>` - XO handoff, if separate from the owner handoff.
- `todos/<component>/<n>` - active delegated work.
