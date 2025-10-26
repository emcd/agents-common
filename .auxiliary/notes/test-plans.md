# Test Plans

## Per-User Coder Population and Symlink Filtering

### Unit Tests

#### 1. Coder Filtering by Default Mode

**Test: `test_filter_coders_by_default_mode_per_project`**
- Setup: Mock renderers with various `mode_default` values
- Input: List of coders ['claude', 'codex', 'gemini']
- Expected: Only coders with `mode_default == 'per-project'` returned
- Verify: Codex (per-user default) excluded

**Test: `test_filter_coders_by_default_mode_per_user`**
- Setup: Mock renderers with various `mode_default` values
- Input: List of coders ['claude', 'codex', 'gemini']
- Expected: Only coders with `mode_default == 'per-user'` returned
- Verify: Codex (per-user default) included

**Test: `test_filter_coders_logs_skipped`**
- Setup: Mock renderers, capture log output
- Input: Mixed coders
- Verify: Debug messages logged for skipped coders with reason

#### 2. Directory Symlink Creation Filtering

**Test: `test_coder_directory_symlinks_skip_per_user_default`**
- Setup: Mock renderer with `mode_default = 'per-user'`
- Input: Coder list containing per-user default coder
- Expected: No directory symlink created for per-user default coder
- Verify: `attempted` count excludes skipped coder

**Test: `test_coder_directory_symlinks_create_for_per_project_default`**
- Setup: Mock renderer with `mode_default = 'per-project'`
- Input: Coder list with per-project default coder
- Expected: Directory symlink created
- Verify: Symlink points to correct target under `.auxiliary/configuration/coders/`

**Test: `test_coder_directory_symlinks_mixed_defaults`**
- Setup: Mix of per-user and per-project default renderers
- Input: Coder list ['claude', 'codex', 'opencode']
- Expected: Symlinks only for per-project defaults
- Verify: Codex skipped, others processed

#### 3. Memory Symlink Behavior

**Test: `test_memory_symlinks_created_for_all_coders`**
- Setup: Mix of per-user and per-project default renderers
- Input: All configured coders
- Expected: Memory symlinks created regardless of `mode_default`
- Verify: AGENTS.md, CLAUDE.md, CODEX.md all created
- Rationale: All coders support per-project memory files

**Test: `test_memory_symlinks_point_to_conventions`**
- Setup: Any coder configuration
- Expected: All memory symlinks point to `.auxiliary/configuration/conventions.md`
- Verify: Symlink targets are correct

#### 4. Populate Command Filtering

**Test: `test_populate_project_filters_by_default_mode`**
- Setup: Configuration with mixed default modes
- Input: `populate project` command
- Expected: Only per-project default coders processed
- Verify: Content generator created with filtered coder list

**Test: `test_populate_user_filters_by_default_mode`**
- Setup: Configuration with mixed default modes
- Input: `populate user` command
- Expected: Only per-user default coders processed
- Verify: Content generated to user directories (e.g., `~/.codex/`)

**Test: `test_populate_project_warns_if_no_per_project_coders`**
- Setup: Configuration with only per-user default coders
- Input: `populate project` command
- Expected: Warning logged, early return
- Verify: No content generated

**Test: `test_populate_user_warns_if_no_per_user_coders`**
- Setup: Configuration with only per-project default coders
- Input: `populate user` command
- Expected: Warning logged
- Verify: Still processes globals/wrappers

### Integration Tests

#### 1. Full Populate Project Workflow

**Test: `test_populate_project_with_mixed_coders`**
- Setup: Fresh project with configuration listing both per-user and per-project default coders
- Command: `agentsmgr populate project defaults/`
- Verify:
  - Content generated only in `.auxiliary/configuration/coders/` for per-project defaults
  - No `.codex` directory symlink created
  - `.claude`, `.opencode` directory symlinks created (if per-project defaults)
  - All memory symlinks created (AGENTS.md, CLAUDE.md, CODEX.md, etc.)
  - Git exclude updated with appropriate entries

**Test: `test_populate_project_codex_skipped`**
- Setup: Project configuration including Codex
- Command: `agentsmgr populate project defaults/`
- Verify:
  - No `.auxiliary/configuration/coders/codex/` directory created
  - No `.codex` directory symlink created
  - `AGENTS.md` memory symlink created (shared by all coders)
  - Log messages indicate Codex skipped for per-project

#### 2. Full Populate User Workflow

**Test: `test_populate_user_with_mixed_coders`**
- Setup: Configuration with mixed default modes
- Command: `agentsmgr populate user defaults/`
- Verify:
  - Content generated to `~/.codex/` for Codex (per-user default)
  - Commands and agents populated in user directories
  - Globals and wrappers processed as before
  - No content generated for per-project default coders

**Test: `test_populate_user_codex_content_generated`**
- Setup: Configuration including Codex
- Command: `agentsmgr populate user defaults/`
- Verify:
  - `~/.codex/commands/` directory exists with generated commands
  - `~/.codex/agents/` directory exists if agent templates available
  - Content matches Codex renderer expectations
  - Uses Claude-compatible templates (per Codex renderer flavor)

#### 3. Dangling Symlink Prevention

**Test: `test_no_dangling_symlinks_after_populate_project`**
- Setup: Clean project
- Command: `agentsmgr populate project defaults/`
- Verify: `find . -xtype l` returns no dangling symlinks
- Critical: No `.codex` directory symlink

**Test: `test_existing_dangling_codex_symlink_ignored`**
- Setup: Manually create dangling `.codex` symlink
- Command: `agentsmgr populate project defaults/`
- Verify: Existing dangling symlink left alone (not recreated)
- Note: Future enhancement could remove it

#### 4. Simulation Mode

**Test: `test_populate_project_simulate_filters_correctly`**
- Setup: Configuration with mixed defaults
- Command: `agentsmgr populate project --simulate defaults/`
- Verify:
  - Simulation output shows only per-project default coders
  - No files written
  - Logs indicate what would be created

**Test: `test_populate_user_simulate_shows_user_coders`**
- Setup: Configuration with mixed defaults
- Command: `agentsmgr populate user --simulate defaults/`
- Verify:
  - Simulation shows content would be generated for per-user defaults
  - Target directories shown (e.g., `~/.codex/`)

### Manual Verification Tests

#### 1. End-to-End Project Setup

1. Start with clean project
2. Configure mixed coders in `.auxiliary/configuration/copier-answers--agents.yaml`
3. Run `agentsmgr populate project defaults/`
4. Verify:
   - Directory structure correct
   - Only appropriate symlinks exist
   - `ls -la` shows no dangling links
   - Git exclude updated correctly

#### 2. End-to-End User Setup

1. Back up existing user coder directories
2. Run `agentsmgr populate user defaults/`
3. Verify:
   - `~/.codex/` contains commands and agents
   - `~/.claude/` unchanged (per-project default)
   - User globals updated
   - Wrapper scripts installed

#### 3. Cross-Mode Verification

1. Run both `populate project` and `populate user`
2. Verify:
   - No content duplication
   - Each coder's content in appropriate location
   - No conflicts or overwrites
   - Both commands can run independently

### Regression Tests

**Test: `test_per_project_behavior_unchanged_for_claude`**
- Setup: Claude coder only (per-project default)
- Command: `agentsmgr populate project defaults/`
- Verify: Behavior identical to pre-fix (content in `.auxiliary/configuration/coders/claude/`)

**Test: `test_memory_symlinks_unchanged`**
- Setup: Any coder configuration
- Command: `agentsmgr populate project defaults/`
- Verify: Memory symlink behavior unchanged from pre-fix

**Test: `test_git_exclude_management_unchanged`**
- Setup: Mixed coder configuration
- Command: `agentsmgr populate project defaults/`
- Verify: Git exclude entries added correctly as before
