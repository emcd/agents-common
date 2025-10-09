# Memory File Symlink Implementation Plan

## Context

Memory files provide project-specific conventions and context to AI coding assistants. Each coder expects a different filename for their memory file:
- Claude Code: `CLAUDE.md`
- OpenCode: `AGENTS.md`
- Codex CLI: `AGENTS.md`
- Gemini CLI: `GEMINI.md`

All symlinks point to shared source: `.auxiliary/configuration/conventions.md`

**Scope**: Project-specific only (per-project mode). Memory file symlinks are always created in project root (`.claude/`, `.opencode/`, etc.), never in per-user directories.

## Requirements

Based on existing `.auxiliary/scripts/prepare-agents` patterns and project needs:

1. **Automatic creation**: Symlinks created automatically during `agentsmgr populate` (no flag required)
2. **Symlink replacement**: Always update symlinks if they point to wrong target
3. **File preservation**: Never overwrite regular files (warn and skip)
4. **Source validation**: Error if `.auxiliary/configuration/conventions.md` doesn't exist
5. **Broken symlink handling**: Remove and recreate broken symlinks
6. **Project-specific only**: No per-user symlink support needed

## Implementation Plan

### 1. Renderer Configuration

**File**: `sources/agentsmgr/renderers/base.py`

Add `memory_filename` property to base class:

```python
class RendererBase( __.immut.Object ):
    ''' Base class for coder-specific rendering and path resolution. '''

    name: str
    modes_available: frozenset[ ExplicitTargetMode ]
    mode_default: ExplicitTargetMode
    memory_filename: str  # NEW: Expected memory filename for this coder
```

**Update each renderer**:

```python
# sources/agentsmgr/renderers/claude.py
class ClaudeRenderer( RendererBase ):
    name = 'claude'
    modes_available = frozenset( ( 'per-user', 'per-project' ) )
    mode_default = 'per-project'
    memory_filename = 'CLAUDE.md'  # NEW

# sources/agentsmgr/renderers/opencode.py
class OpencodeRenderer( RendererBase ):
    name = 'opencode'
    modes_available = frozenset( ( 'per-user', 'per-project' ) )
    mode_default = 'per-project'
    memory_filename = 'AGENTS.md'  # NEW

# sources/agentsmgr/renderers/codex.py
class CodexRenderer( RendererBase ):
    name = 'codex'
    modes_available = frozenset( ( 'per-user', ) )
    mode_default = 'per-user'
    memory_filename = 'AGENTS.md'  # NEW
```

**Effort**: 15 minutes

### 2. Symlink Creation Logic

**File**: `sources/agentsmgr/commands/memorylinks.py` (new module)

Implement symlink creation following `.auxiliary/scripts/prepare-agents` patterns:

```python
''' Memory file symlink management for coder configurations. '''

from . import __

def create_memory_symlink(
    source: __.Path,           # .auxiliary/configuration/conventions.md
    link_path: __.Path,        # CLAUDE.md, AGENTS.md, etc. (at project root)
    simulate: bool = False,
) -> bool:
    ''' Creates symlink from coder memory file to project conventions.

        Follows patterns from .auxiliary/scripts/prepare-agents:
        - If source doesn't exist: Raise error
        - If link is symlink to correct target: Skip silently
        - If link is symlink to wrong target: Update it
        - If link is regular file/directory: Warn and skip
        - If link is broken symlink: Remove and recreate

        Returns True if symlink created/updated, False if skipped.
    '''
    # Relative path from link location to source
    # CLAUDE.md → .auxiliary/configuration/conventions.md
    try:
        relative_source = __.os.path.relpath(
            source, start = link_path.parent )
    except ValueError:
        # Different drives on Windows
        relative_source = str( source.resolve( ) )

    # Implementation details match prepare-agents behavior


def create_memory_symlinks_for_coders(
    coders: __.cabc.Sequence[ str ],
    target: __.Path,                    # Project root
    renderers: __.cabc.Mapping[ str, __.RendererBase ],
    simulate: bool = False,
) -> tuple[ int, int ]:
    ''' Creates memory symlinks for all configured coders.

        Memory symlinks are always created at project root, regardless
        of targeting mode. They point to project-specific conventions.

        Returns tuple of (attempted, created) counts.
    '''
    # Validate source exists
    source = target / '.auxiliary' / 'configuration' / 'conventions.md'
    if not source.exists( ):
        raise __.MemoryFileAbsence( source )

    attempted = 0
    created = 0

    for coder_name in coders:
        renderer = renderers[ coder_name ]

        # Memory symlink at project root
        link_path = target / renderer.memory_filename

        attempted += 1
        if create_memory_symlink( source, link_path, simulate ):
            created += 1

    return ( attempted, created )
```

**Effort**: 1.5 hours (core logic + edge cases)

### 3. Exception Handling

**File**: `sources/agentsmgr/exceptions.py`

Add new exception for missing memory file:

```python
class MemoryFileAbsence( Omnierror, FileNotFoundError ):
    ''' Memory file absence.

        Raised when .auxiliary/configuration/conventions.md does not exist
        but memory symlinks need to be created.
    '''

    def __init__( self, location: __.Path ) -> None:
        super( ).__init__(
            f"Memory file not found: {location}",
            location = location )

    def render_as_markdown( self ) -> str:
        return f'''# Memory File Not Found

The project memory file does not exist at the expected location:

    {self.exceptions[ 'location' ]}

Memory files provide project-specific conventions and context to AI coding
assistants. Create this file before running `agentsmgr populate`.

**Suggested action**: Create `.auxiliary/configuration/conventions.md` with
project-specific conventions, or copy from a template project.
'''
```

**Effort**: 20 minutes

### 4. Integration with Populate Command

**File**: `sources/agentsmgr/commands/population.py`

Update `execute_populate_command` to create memory symlinks after content generation:

```python
from . import memorylinks as _memorylinks

def execute_populate_command( command: PopulateCommand ) -> None:
    ''' Executes populate command to generate coder configurations. '''

    # ... existing content generation logic ...

    # Create memory symlinks at project root
    # (Memory files are always project-specific, created for all modes)
    if command.mode != 'nowhere':
        _scribe.info( "Creating memory file symlinks..." )
        attempted, created = _memorylinks.create_memory_symlinks_for_coders(
            coders = coders,
            target = command.target,
            renderers = __.RENDERERS,
            simulate = command.simulate,
        )
        if created > 0:
            _scribe.info(
                f"Created {created} memory symlink(s) "
                f"out of {attempted} attempted" )
```

**Effort**: 30 minutes

### 5. Testing Strategy

**File**: `tests/test_memorylinks.py` (new test module)

Test cases covering:
- Symlink creation when link doesn't exist
- Symlink update when pointing to wrong target
- Skip when symlink already correct
- Preservation of regular files with warning
- Broken symlink removal and recreation
- Error when source doesn't exist
- Relative path calculation correctness
- Simulate mode behavior
- 'nowhere' mode skipping

**Effort**: 1 hour

## Edge Cases and Behaviors

Following `.auxiliary/scripts/prepare-agents` patterns:

| Condition | Behavior | Message |
|-----------|----------|---------|
| Source doesn't exist | Raise MemoryFileAbsence | Error with helpful context |
| Link doesn't exist | Create symlink | Info: "Created memory symlink" |
| Link is symlink to correct target | Skip silently | (no message) |
| Link is symlink to wrong target | Update symlink | Info: "Updated memory symlink" |
| Link is broken symlink | Remove and recreate | Info: "Fixed broken symlink" |
| Link is regular file | Warn and skip | Warning: "File exists, skipping" |
| Link is directory | Warn and skip | Warning: "Directory exists, skipping" |
| Mode is 'nowhere' | Skip (no content) | (no message) |
| Simulate mode | Log action, don't create | Info: "[SIMULATE] Would create..." |

## Symlink Structure

All symlinks use relative paths from link location to source.

**Memory files are at project root**, not inside coder configuration directories:

```
project-root/
├── .auxiliary/configuration/conventions.md  (source)
├── CLAUDE.md → .auxiliary/configuration/conventions.md
├── AGENTS.md → .auxiliary/configuration/conventions.md
├── GEMINI.md → .auxiliary/configuration/conventions.md
├── .claude/        (coder configuration directory)
│   ├── commands/
│   └── agents/
├── .opencode/      (coder configuration directory)
│   ├── commands/
│   └── agents/
└── .gemini/        (coder configuration directory)
    ├── commands/
    └── agents/
```

**Note**: `AGENTS.md` is shared by both OpenCode and Codex (both coders use the same memory filename).

**Rationale for relative paths**:
- Works correctly when project is moved or cloned
- Works across different systems without absolute path issues
- Consistent with `.auxiliary/scripts/prepare-agents` approach

## Implementation Checklist

### Phase 1: Core Infrastructure
- [ ] Add `memory_filename` property to RendererBase
- [ ] Update all renderers with appropriate memory filenames
- [ ] Add MemoryFileAbsence exception
- [ ] Update renderer type annotations if needed

### Phase 2: Symlink Logic
- [ ] Create memorylinks.py module
- [ ] Implement create_memory_symlink() function
- [ ] Implement create_memory_symlinks_for_coders() function
- [ ] Handle all edge cases from table above

### Phase 3: Integration
- [ ] Import memorylinks in population.py
- [ ] Call symlink creation after content generation
- [ ] Add appropriate logging messages
- [ ] Handle exceptions gracefully

### Phase 4: Testing
- [ ] Create test_memorylinks.py
- [ ] Test all edge cases
- [ ] Test simulate mode
- [ ] Test 'nowhere' mode skipping

### Phase 5: Quality Assurance
- [ ] Run linters (should pass)
- [ ] Run type checker (should pass)
- [ ] Run tests (should pass with new tests)
- [ ] Manual testing with real project

## Estimated Total Effort

**Total**: ~3-4 hours
- Renderer updates: 15 min
- Core symlink logic: 1.5 hours
- Exception handling: 20 min
- Integration: 30 min
- Testing: 1 hour
- QA and manual testing: 30 min

## Success Criteria

- [ ] Memory symlinks created automatically during `agentsmgr populate`
- [ ] Symlinks created at project root (not in coder directories)
- [ ] Symlinks always point to `.auxiliary/configuration/conventions.md`
- [ ] Existing symlinks updated if pointing to wrong target
- [ ] Regular files preserved with warnings
- [ ] Broken symlinks fixed automatically
- [ ] Error raised if source doesn't exist
- [ ] All linters pass
- [ ] All type checks pass
- [ ] All tests pass (including new tests)
- [ ] Simulate mode works correctly

## Future Considerations

- **Gemini renderer**: When added, will automatically get memory symlink support via `memory_filename = 'GEMINI.md'`
- **Additional memory files**: If other shared files need symlinking, can extend `create_memory_symlinks_for_coders()` pattern
- **User documentation**: Update user guide with memory file conventions and symlink behavior
