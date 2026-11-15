# Applying Template Updates

This guide covers updating a project built from the agents-common
Copier template, and the `agentsmgr populate` step that goes with it.
It is template-owned: corrections land here, not in per-project files.

## Standard update

Run the update non-interactively with the data file, then populate
from an agents-common checkout at the resolved ref:

Copier requires the data file as a local file, not a URL.
Resolve the master head once to an immutable commit so the data
file, the template, and the populate step all see the same
snapshot, then update, then populate:

```sh
# Exact-run override: set REF_WANT to a tag name (e.g. v1.0a20) or a
# full commit SHA to reproduce that run. Leave empty to track master.
REF_WANT=${REF_WANT:-refs/heads/master}
REF_SRC="https://github.com/emcd/agents-common.git"
case "$REF_WANT" in
  ????????????????????????????????????????)
    case "$REF_WANT" in *[!0-9a-f]*) echo "bad template ref: $REF_WANT" >&2; exit 1;; esac
    REF="$REF_WANT" ;;
  *)
    REF_LINES=$(git ls-remote "$REF_SRC" "$REF_WANT" "$REF_WANT^{}") || { echo "could not resolve template ref $REF_WANT; aborting" >&2; exit 1; }
    UNPEELED=$(printf '%s\n' "$REF_LINES" | awk '$2 !~ /\^\{\}$/ {print $1}')
    [ -n "$UNPEELED" ] || { echo "no such template ref: $REF_WANT" >&2; exit 1; }
    [ "$(printf '%s\n' "$UNPEELED" | wc -l)" -eq 1 ] || { echo "ambiguous template ref: $REF_WANT" >&2; exit 1; }
    REF=$(printf '%s\n' "$REF_LINES" | awk '$2 ~ /\^\{\}$/ {print $1; exit}')
    REF=${REF:-$(printf '%s\n' "$UNPEELED")}
    case "$REF" in ''|*[!0-9a-f]*) echo "bad template ref: $REF" >&2; exit 1;; esac
    [ "${#REF}" -eq 40 ] || { echo "bad template ref: $REF" >&2; exit 1; } ;;
esac
SRC="/path/to/agents-common"
TARGET="/path/to/project"
cd "$TARGET" || { echo "cannot enter target $TARGET; aborting" >&2; exit 1; }
[ -f .auxiliary/configuration/copier-answers--agents.yaml ] || { echo "not a project root (no agents answers file); aborting" >&2; exit 1; }
unset DATA_FILE
WORKDIR="$(mktemp -d)" || exit 1
DATA_FILE="$WORKDIR/single-source-instructions.yaml"
trap 'rm -rf "$WORKDIR"' EXIT INT TERM
git -C "$SRC" archive "$REF" distribution > "$WORKDIR/distribution.tar" || { echo "cannot archive distribution at $REF (fetch it into $SRC first); aborting" >&2; exit 1; }
[ -s "$WORKDIR/distribution.tar" ] || { echo "archive is empty; aborting" >&2; exit 1; }
tar -x -C "$WORKDIR" -f "$WORKDIR/distribution.tar" || { echo "extraction failed; aborting" >&2; exit 1; }
[ -d "$WORKDIR/distribution" ] || { echo "extraction produced no distribution tree; aborting" >&2; exit 1; }
python3 -c "import sys, urllib.request; urllib.request.urlretrieve('https://raw.githubusercontent.com/emcd/agents-common/' + sys.argv[1] + '/.auxiliary/data/copier/single-source-instructions.yaml', sys.argv[2])" "$REF" "$DATA_FILE" || { echo "data-file download failed; aborting" >&2; exit 1; }
[ -s "$DATA_FILE" ] || { echo "downloaded data file is empty; aborting" >&2; exit 1; }
copier update \
    --vcs-ref="$REF" \
    --data-file "$DATA_FILE" \
    --answers-file .auxiliary/configuration/copier-answers--agents.yaml \
    --skip-answered || { echo "copier update failed; aborting before populate" >&2; exit 1; }
agentsmgr populate project "$WORKDIR/distribution" "$TARGET"
```

Track the template at HEAD by default: the block above resolves
master once per run rather than pinning a release tag. Release tags
remain the curation checkpoints (and the package/publication line),
not required sync points. To reproduce an exact run instead, set
`REF_WANT` to a tag name or full commit SHA (`REF_WANT=v1.0a20`);
a pin that merely dodges an environment problem is a
workaround, not a fix — fix the environment instead. Whatever ref the
update uses, the data-file URL must name the same ref: the file
carries renamed answers so the update does not silently keep a
retired layout, and it holds no guidance beyond that.
(If this project also uses the Rust template, it keeps a separate
answers file alongside this one; each template's copy and populate
leaves the other's answers file untouched.)

Do not pass `--quiet`: the post-update banner is suppressed in quiet
mode, and you will miss conflict and follow-up notices.

Copier update is a three-way merge, not an overwrite: it re-renders
the old template at your recorded `_commit` and the new one, then
merges the template's evolution against yours. Conflict markers
surface only where both sides changed the same region. If project
content vanishes without markers in the file, that alone does not
identify the mechanism — possibilities include a stale merge base (a
recorded `_commit` older than the file's true lineage), overwrite
semantics, or a rejection conflict mode (`--conflict rej` writes
markers to `.rej` files and leaves the upstream value in place).
Inspect `git diff`, any `.rej` files, the recorded ref, and the
selected conflict mode before diagnosing. Either way, back up
project augmentations such as MCP server additions before updating
so nothing depends on reconstructing the mechanism afterward.

## Ordering rules

- **Update first, then populate.** Populate aborts when the
  template-rendered `.auxiliary/agents/agents.md` does not exist yet.
- **Review before populating.** Resolve update conflicts first; do
  not populate over a conflicted tree.
- **Commit together.** Land the update and the populate in the same
  changeset. Committing the update first leaves downstream clones
  holding half-migrated trees.
- **Reload sessions after coder-config changes.** Running sessions
  may hold stale runtime configuration, especially where automatic
  reload is disabled or unavailable — on-disk changes do not
  necessarily reach them. After anything under
  `.auxiliary/configuration/coders/` changes, request the affected
  harness's supported reload (restart the seat session if needed)
  before trusting the new behavior; edits made meanwhile may still
  run under the old config. Reload only affected seat sessions —
  this never calls for restarting shared services.

## Retired content

When the template retires something, delete leftover tracked copies
outright. Do not add exclude entries for retired paths: removed means
absent, not excluded. Populate copies but never deletes, so stale
trees (old instruction homes, retired `coders/*/agents` and
`coders/*/commands` directories, legacy `*.rst` standards) must be
removed by hand. Visibility is not provenance — but neither is
absence from current producers: a newly visible file is only
deletable as stale output once established as obsolete generated
content (producer/history evidence, e.g. a retired distribution path
with no local modifications). Inspect before acting, and preserve or
migrate project-owned material first per the custom-skills, legacy
real-path, and rollback rules below; unknown provenance means
investigate, not blindly delete or stage.

Know which of the three classes an established template/distribution
path under `coders/` belongs to before touching it. Tracked =
template-rendered configuration (`settings.json`, `config.toml`,
rules, `.gitignore`): commit these. Populate-managed =
populate-created trees that must never be committed (prompt content,
per-coder `skills/` discovery symlinks, standards): these are
git-excluded by the managed block populate maintains, so leave the
exclusions alone and do not stage the trees. Retired = content
neither the template nor the distribution produces any more
(per-coder `agents/` and `commands/` subtrees above all): after
rescuing any unique local content, delete outright, neither tracked
nor excluded. These classes cover established paths only, not
arbitrary coder-tree contents of unknown provenance.

A moved or reformatted key is not a line-level change: Copier's merge
can keep both the stale local copy and the template's new one (seen
with a duplicated JSON key that the `check-json` hook then rejects).
After updating, treat hook failures about duplicate keys as this
shape until proven otherwise — delete the stale copy by hand so the
file matches a fresh template render.

## Custom skills

Project-owned skills live in `.auxiliary/agents/skills/` (directory
package with `SKILL.md`, or flat `<name>.md`). Populate merges into
that tree and never deletes foreign entries. Only the per-coder
`skills/` discovery symlinks are replaced on populate, so move any
custom skills out of `coders/*/skills/` first — or delete them if
vestigial. `project-triage` in per-coder `skills/` trees is retired
distributed content, not a custom skill: delete it outright, do not
rescue it. The same holds for retired distributed MCP servers —
`pyright` and `librovore` entries lingering in old configurations
are vestigial (both cut from the template in March) and should be
deleted on sight, not restored.

## Legacy real paths

Populate retargets a wrong symlink but only warns and skips a real
path. Before populating, check whether `.claude/`, `.opencode/`, and
root memory files are symlinks or legacy real directories/files: a
legacy real path blocks its managed symlink from materializing.
Remove legacy real paths by hand (after rescuing anything
project-owned).

## Rollback

- Recorded answers persist: re-running the update without the data
  file does NOT restore prior values — Copier keeps the recorded
  answers. To roll back the answers migration, read the prior value
  from version control without touching the worktree (checking it
  out would dirty the tree and trip the clean-tree gate), pass it
  back in as data, then re-run populate so generated output matches:

      PRIOR=$(git show <pre-update-ref>:.auxiliary/configuration/copier-answers--agents.yaml | grep instructions_target | awk '{print $2}')
      copier update --answers-file .auxiliary/configuration/copier-answers--agents.yaml --skip-answered --data instructions_target=$PRIOR
      agentsmgr populate project <source>/distribution <target>

- Populated content: first rescue any project-owned files from the
  managed trees — custom skills in `.auxiliary/agents/skills/`
  coexist with distributed ones and must be preserved — then delete
  the managed trees and re-populate.
