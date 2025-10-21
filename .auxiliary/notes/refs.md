# Git Reference Resolution Enhancements

## Context

Three proposed enhancements to Git source handler (`sources/agentsmgr/sources/git.py`):

1. **Tag pattern filtering** - Select tags by glob pattern (e.g., `v1.*`, `stable-*`)
2. **Improved observability** - Log which ref was selected
3. **Performance optimization** - Use GitHub/GitLab API + shallow clones

### Current State

- Full clone with `depth = None` (slow for large repos)
- Selects latest tag by semantic version when no ref specified
- Optional `--tag-prefix` parameter for filtering tags by prefix
- Implicit fallback to HEAD if no version tags exist
- Works with any Git server
- Dulwich progress output suppressed for cleaner logs

### Requirements

System must support flexible tag naming:
- Standard semantic versioning (v1.0.0, v2.1.3)
- Sequential numbering (agents-1, agents-2) if adopted
- Custom conventions (stable-*, beta-*, etc.)

## Decisions

### 1. Tag Prefix Filtering

**Priority: HIGH**

Enables flexible tag selection for:
- Semantic versioning with prefixes (`v`, `version-`, `release-`)
- Release channels (`stable-`, `beta-`, `rc-`)
- Monorepo patterns (`python-`, `rust-`)

**Decision: Use `--tag-prefix` CLI flag**

```bash
agentsmgr populate --source github:emcd/agents-common --tag-prefix='v'
agentsmgr populate --source github:emcd/agents-common --tag-prefix='stable-'
```

**Rationale**: Simpler than glob pattern matching. Most use cases involve filtering by prefix and stripping it before version parsing. Glob patterns add complexity without covering additional meaningful scenarios.

**Implementation:**
- Add `--tag-prefix` flag to `PopulateCommand`
- Pass prefix to `_get_latest_tag()` method
- Filter tags by prefix and strip before parsing with `packaging.version.Version`
- Use semantic version comparison (not commit date)
- Fall back to default branch if no tags can be parsed as versions

### 2. Improved Observability

**Priority: MEDIUM**

**Current behavior is correct** - implicit fallback to default branch when no tags exist supports both production and development workflows.

**Decision: Add logging only**

- Log which ref was selected and why
- No behavioral changes
- Keep implicit fallback as-is

**Implementation:**
- Add info logging when latest tag is selected
- Add info logging when falling back to default branch
- Add info logging when using explicit ref

### 3. GitHub/GitLab API Optimization

**Priority: CRITICAL**

**Performance Impact:** 3-50x speedup for large repos by avoiding full clone.

**Decision: Use hybrid approach with Dulwich shallow clones**

**Key Finding:** Dulwich supports both `depth` and `branch` parameters, enabling shallow clone of specific refs without shelling out to git CLI.

**Implementation Strategy:**

1. **Fast path** (GitHub/GitLab):
   - Use API to resolve latest tag (with optional pattern filtering)
   - Perform shallow clone: `dulwich.porcelain.clone(url, target, depth=1, branch=ref)`
   - Gracefully fall back on API failure

2. **Standard path** (other Git servers):
   - Use existing full clone approach
   - Works with any Git server

**Components:**

- GitHub API integration for tag resolution
- GitLab API integration (similar structure)
- Shallow clone using Dulwich `depth` + `branch` parameters
- Fallback logic for API failures or rate limiting

**Authentication:**

- Check `GITHUB_TOKEN` env var first
- Fall back to `gh auth token` if available
- Graceful degradation when unauthenticated (60 requests/hour)
- No subprocess usage needed for cloning (pure Dulwich)

## Implementation Plan

### Phase 1: Logging ✅ COMPLETE

Add info-level logging to show which ref was selected.

1. Log when latest tag is selected ✅
2. Log when falling back to default branch ✅
3. Log when using explicit ref ✅

### Phase 2: Tag Prefix Filtering ✅ COMPLETE

1. Add `--tag-prefix` CLI flag to `PopulateCommand` ✅
2. Pass prefix to `_get_latest_tag()` method ✅
3. Filter tags by prefix and strip before version parsing ✅
4. Use semantic version comparison with `packaging.version.Version` ✅
5. Remove commit timestamp fallback for non-version tags ✅
6. Comprehensive testing with multiple prefixes ✅

### Phase 3: GitHub/GitLab API Optimization

1. Add GitHub API tag resolution with pattern support
2. Implement shallow clone using Dulwich `depth=1, branch=ref`
3. Add GitLab API support (similar to GitHub)
4. Add fallback to full clone on API failure
5. Document `GITHUB_TOKEN` usage for rate limits
6. Add integration tests with real repos

## Open Questions

1. **Pattern with no matches**: Fall back to default branch, or fail?
   - Recommendation: Fall back (current behavior for no tags)

2. **API token sources**: Check `GITHUB_TOKEN` env var, then `gh auth token`
   - Decision: Support both sources

3. **Flag naming**: Use `--ref-filter-glob` and reserve `--ref-filter-regex` for future
   - Decision: Approved

4. **API response caching**: Cache tag lists to reduce API calls?
   - Recommendation: No caching initially, add if rate limiting becomes issue

## References

- Current implementation: `sources/agentsmgr/sources/git.py:157-250`
- Dulwich clone signature: Supports `depth` and `branch` parameters
- GitHub API: https://docs.github.com/en/rest/repos/repos
- GitLab API: https://docs.gitlab.com/ee/api/repositories.html
