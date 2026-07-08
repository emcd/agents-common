# <Bundle> cross-repository maintainer coordination

#coordination #org-chart #policy #status-active

Use this shape when one Agentmux bundle coordinates multiple mostly independent
repositories or packages rather than multiple branches of one repository.

## Maintainers

| Repository | Maintainer Role | Agentmux ID | Owns |
|------------|-----------------|-------------|------|
| `<repo-a>` | <Repo A Maintainer> | `<repo-a>@<bundle>` | Package roadmap, releases, local validation |
| `<repo-b>` | <Repo B Maintainer> | `<repo-b>@<bundle>` | Package roadmap, releases, local validation |
| `<repo-c>` | <Repo C Maintainer> | `<repo-c>@<bundle>` | Package roadmap, releases, local validation |
| `<shared-template>` | <Template Owner> | `<template>@<bundle>` | Shared template/configuration changes |

## Coordinator Responsibilities

- Track cross-repository dependency order and release sequencing.
- Route shared template or policy changes to the owning repository.
- Avoid broad broadcast updates unless multiple maintainers need action.
- Preserve each repository's local commit, release, and validation policy.

## Maintainer Responsibilities

- Keep repository-specific handoffs current in each repository's own notebook
  when active work is in progress.
- Report blockers that affect other repositories or shared release sequencing.
- Coordinate before changing shared templates, generated configuration, or cross-repository policy.

## Coordination Rules

- Use direct Agentmux messages to affected maintainers rather than bundle-wide updates by default.
- Prefer Agentmux for cross-repository coordination because notebook state is
  repository-local and each repository has its own corresponding notebook.
- For shared template changes, include downstream impact and validation expectations.
- For release coordination, include current tag/version, dependency constraints, and publication status.

## Related Notes

- If there is a bundle coordinator, their repository notebook:
  `coordination/general/<n>` for cross-repository coordination state.
- Each repository notebook: `coordination/general/<n>` or
  `coordination/<component>/<n>` for repository-local handoff or release state.
- Each repository notebook: `todos/<component>/<n>` for repository-local
  actionable work.
