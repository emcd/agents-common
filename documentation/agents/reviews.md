# Delegated Review Flow

Use this flow when multiple team members can access the same repository through branches or linked worktrees.

## Engineer Flow

1. Implement the scoped change and run validation.
2. Create a local/private review commit so the diff is hash-stable and hook-checked.
3. Rebase the review branch onto the agreed `<local-integration-base>`.
4. Send the commit hash, changed-file summary, validation results, and any blockers/design questions.
5. The reviewer approves the commit or requests changes.
6. Amend or add a follow-up review commit when requested.

The agreed `<local-integration-base>` is a Git ref in the current repository, such as local `master` or a local lane integration branch. It is not a filesystem path and is not a remote-tracking ref. Do not use `origin/master`, another `origin/*` ref, a path like `/path/to/repo/master`, or a raw commit hash as the rebase base unless the coordinator explicitly names that exact ref or hash. When in doubt, ask for the local branch/ref name before rebasing. Confirm it with `git branch --list <local-integration-base>` or `git rev-parse --verify <local-integration-base>` before running `git rebase`.

## Coordinator/Tech-Lead Flow

1. Review the submitted commit and any included validation evidence.
2. Merge approved review branches with `--no-ff` when preserving a delegated-work or lane boundary; this creates a clear integration point and avoids mutually rebasing branches into increasingly long histories.
3. Merge/push only after explicit human approval.

Prefer reviewing commits by hash. Use an explicit worktree path only for uncommitted diffs or commits in a different repository. Use patch artifacts only as a fallback when the reviewer cannot access the repository, branch, or worktree directly.

# Review Request Packet

For non-trivial delegated work, review requests should include:

- Base ref for rebase: the `<local-integration-base>` to use for `git rebase` or `git rebase -i --autosquash`.
- Intended merge target: the branch/ref where the work should eventually land. This may differ from the rebase base, and may be a shared branch.
- Complete commit list with hashes and one-line descriptions.
- Validation commands run and results, including skipped checks or known gaps.
- Intended contract: what must be true after the change lands.
- Review concerns, if any: genuine uncertainty or risky areas only.
- Known risks, accepted tradeoffs, deferred items, or intentional branch staleness.

Author-provided review concerns are supplemental context, not a limit on review scope. Independent inspection remains the reviewer responsibility.

# Reviewing Stacked Commits

When feedback targets a specific commit inside a **stack** of multiple unmerged, unpushed commits, use `git commit --fixup <target-hash>` instead of manually editing history to reach a non-HEAD commit. A fixup is valid only when the entire fix belongs to code introduced by one target commit in the current stack. Use a first-class follow-up commit when the fix touches code that is already merged to the base branch, or when the fix spans or refactors code introduced by two or more in-stack commits. Name the review finding addressed in the first-class commit message or review reply so reviewers know why it is not a fixup.

Fold the stack with `--autosquash`, which requires `-i` explicitly — `--autosquash` alone is a silent no-op. Use `<local-integration-base>` as the rebase base.

Preview the fold before applying:

```sh
GIT_SEQUENCE_EDITOR="sh -c 'cat \"$1\" >&2; exit 1' --" git rebase -i --autosquash <local-integration-base>
```

This prints the rebase plan to stderr and aborts cleanly (no rebase state left behind). Read the plan before running for real.

To apply the fold: `git rebase -i --autosquash <local-integration-base>`. If the result is wrong, recover with `git reset --hard ORIG_HEAD` — git sets `ORIG_HEAD` to the exact pre-rebase position regardless of how far back `<local-integration-base>` was.

For example, run `git rebase master` from the worktree branch when the coordinator says to rebase onto local `master`. Do not write `git rebase /path/to/repo/master`; that is a filesystem path, not a Git ref.
