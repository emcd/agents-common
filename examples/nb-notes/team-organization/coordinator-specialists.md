# <Project> team org and workflow

#coordination #org-chart #policy #status-active

## Roster

| Role | Agentmux ID | Owns | Notes |
|------|-------------|------|-------|
| Coordinator / Strategist | `<coordinator>@<bundle>` | Roadmap, sequencing, integration, notebook hygiene | Final coordinator for cross-specialist work |
| <Specialist A> | `<specialist-a>@<bundle>` | `<component-a>` | Owns implementation and local validation for this component |
| <Specialist B> | `<specialist-b>@<bundle>` | `<component-b>` | Owns implementation and local validation for this component |
| <Specialist C> | `<specialist-c>@<bundle>` | `<component-c>` | Owns implementation and local validation for this component |
| <Editor / Reviewer> | `<editor>@<bundle>` | Cross-cutting prose, nomenclature, mechanical consistency | Optional side-car role |

## Coordinator Responsibilities

- Keep one active integration lane at a time unless parallel work is explicitly safe.
- Dispatch complete, coherent work units with validation expectations.
- Require review commits or clear diff artifacts before integration.
- Merge specialist branches into `master` with `--no-ff` to preserve a clear
  integration boundary and single revert point.
- Resolve cross-specialist conflicts and route ambiguous ownership.
- Maintain stable org notes, rolling handoffs, and tracker todos.

## Specialist Responsibilities

- Own local design and validation for the assigned component.
- Rebase specialist branches onto current `master` before requesting review or
  integration.
- Request review with commit hashes and validation evidence.
- Update the component handoff when a meaningful checkpoint, blocker, or ownership change occurs.

## Coordination Rules

- Use low-noise Agentmux communication.
- Send messages when blocked, requesting review, handing off validated work, or reporting material risk.
- Batch related updates into one message.
- Prefer `coordination/<component>` for component handoffs and `coordination/general` for cross-component state.

## Related Notes

- `coordination/general/<n>` - project-wide rolling handoff.
- `coordination/<component>/<n>` - specialist handoff.
- `procedures/<component>/<n>` - component-specific procedures.
