# GitHub Source Location Support

## Objective

Enable `agentsmgr` to retrieve configuration data from GitHub repositories, allowing the tool to be used on projects other than `agents-common` by pulling agent configurations from remote sources.

## Current State

### Architecture Analysis
- **Source Resolution**: `retrieve_data_location()` in `sources/agentsmgr/commands/base.py:128`
- **Current Limitation**: Only supports local paths, explicitly rejects remote URLs
- **Configuration Support**: CLI `--source` parameter and `sources.default` in configuration file
- **Data Structure**: Works with Copier-style templates and structured agent configurations

### Existing Code Points
```python
# sources/agentsmgr/commands/base.py:134-136
if not source_spec.startswith( ( 'http', 'git@', 'gh:' ) ):
    return __.Path( source_spec ).resolve( )
raise __.DataSourceNoSupport( source_spec )
```

## Technical Proposal

### URL Scheme Support

**Primary Target Formats**:
```
github:emcd/agents-common                # GitHub shorthand (preferred)
https://github.com/emcd/agents-common    # Full GitHub URLs
git+https://host.com/org/repo            # Generic Git URLs
```

**Subdirectory Specification** (Fragment Syntax):
```
github:emcd/agents-common#defaults       # Target specific subdirectory
github:emcd/agents-common#path/to/configs # Nested path support
```

### Implementation Strategy

#### Phase 1: Core GitHub Resolution (Immediate)

**1. Source Handler Architecture**
```python
# sources/agentsmgr/sources/
├── __init__.py
├── __.py            # Re-exports and common utilities
├── base.py          # AbstractSourceHandler protocol
├── local.py         # Current local path logic
└── git.py           # Git-based source handling
```

**2. Git Source Implementation**
- Parse various Git URL formats and extract components
- Use Dulwich for Git operations (clone/checkout)
- Support URL scheme mapping (github: → https://github.com/)
- Handle fragment syntax for subdirectory targeting
- Leverage existing Git authentication (SSH keys, credentials)

**3. Integration Points**
- Modify `retrieve_data_location()` to delegate to appropriate source handler
- Maintain existing local path behavior for backward compatibility
- Preserve current CLI and configuration file support

#### Phase 2: Enhanced Robustness (Future)

**Deferred Features** (marked as nice-to-haves):
- Environment variable precedence (`AGENTSMGR_SOURCE`)
- Caching mechanism for remote content
- Git clone fallback for private repositories
- Progress indicators and enhanced error messaging

### Technical Implementation Details

#### URL Parsing and Mapping Logic
```python
def parse_git_url(source_spec: str) -> GitLocation:
    """Parse various Git URL formats into components."""
    # github:owner/repo#subdir        → https://github.com/owner/repo.git
    # gitlab:owner/repo#subdir        → https://gitlab.com/owner/repo.git
    # git+https://host/repo#subdir    → https://host/repo (direct)
    # https://github.com/owner/repo   → https://github.com/owner/repo.git
```

#### Git Source Resolution
```python
class GitSourceHandler(AbstractSourceHandler):
    def resolve(self, source_spec: str) -> Path:
        """Resolve Git source to local temporary directory."""
        location = self.parse_git_url(source_spec)
        temp_dir = self.create_temp_directory()
        self.clone_repository(location.git_url, temp_dir)
        if location.subdir:
            return temp_dir / location.subdir
        return temp_dir

    def clone_repository(self, git_url: str, target_dir: Path) -> None:
        """Clone repository using Dulwich."""
        # Implement shallow clone for efficiency
```

### Integration Approach

#### Minimal Changes to Existing Code
1. **`retrieve_data_location()`**: Replace current logic with resolver delegation
2. **Exception Handling**: Enhance `DataSourceNoSupport` with GitHub-specific guidance
3. **CLI Interface**: No changes needed - existing `--source` parameter works
4. **Configuration**: No changes needed - existing `sources.default` works

#### Backward Compatibility
- All existing local path usage continues unchanged
- Current error messages preserved with enhancements
- Configuration file format remains stable

## Implementation Plan

### Immediate Priorities
1. **Create source handler abstraction** with local and Git implementations
2. **Implement Dulwich-based Git cloning** with URL scheme mapping
3. **Add fragment syntax parsing** for subdirectory support
4. **Update `retrieve_data_location()`** to use source handler pattern
5. **Test with real GitHub repositories** including `github:emcd/agents-common#defaults`

### Success Criteria
- [ ] `agentsmgr populate --source=github:emcd/agents-common#defaults` works
- [ ] Configuration file `sources.default = "github:org/repo#path"` works
- [ ] Local paths continue working unchanged
- [ ] Clear error messages for unsupported URL formats
- [ ] GitHub repositories accessible via existing Git authentication

### Future Enhancements (Deferred)
- **Environment Variable Support**: `AGENTSMGR_SOURCE` precedence
- **Caching Layer**: Local cache for remote content with TTL
- **Private Repository Support**: GitHub token authentication
- **Performance Optimizations**: ETag validation, conditional requests
- **Git Clone Fallback**: For repositories requiring authentication

## Risk Considerations

### Performance Impact
**Without Caching**: Each invocation will clone fresh content from Git repositories
- **Mitigation**: Document this limitation, plan caching for Phase 2
- **Benefit**: Shallow clones are relatively fast for typical configuration repositories

### Network Dependencies
**Reliability**: Tool becomes dependent on Git repository availability
- **Mitigation**: Clear error messages for network failures
- **Benefit**: Git protocol is robust and widely supported

### Authentication
**Git Credentials**: Leverages existing Git authentication setup
- **Benefit**: Works with SSH keys, credential helpers, and Git configuration
- **Private Repos**: Supported through standard Git authentication mechanisms

## Expected Benefits

1. **Cross-Project Usage**: Enable `agentsmgr` on any project by pulling configs from GitHub
2. **Configuration Sharing**: Teams can share agent configurations via repositories
3. **Version Control**: Agent configurations benefit from git versioning and branching
4. **Centralized Management**: Maintain agent configs in dedicated repositories
5. **Community Sharing**: Public repositories enable community configuration sharing

## Configuration Examples

### CLI Usage
```bash
# Use GitHub shorthand
agentsmgr populate --source=github:emcd/agents-common#defaults

# Use full GitHub URL
agentsmgr populate --source=https://github.com/myorg/my-configs#production

# Generic Git URL
agentsmgr populate --source=git+https://gitlab.com/team/configs#team-standards
```

### Configuration File
```toml
# data/configuration/general.toml
[sources]
default = 'github:emcd/agents-common#defaults'
# or
# default = 'https://github.com/myorg/standard-configs#python-projects'
```

This focused approach prioritizes immediate functionality over comprehensive features, enabling cross-project usage while maintaining a clear path for future enhancements.