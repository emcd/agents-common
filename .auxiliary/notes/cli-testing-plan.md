# AgentsMgr Populate Command Live Testing Plan

## Overview

This document provides a step-by-step plan for safely testing the `agentsmgr populate` command against:
1. The `agents-common` project itself (this repository)
2. Your personal global user configuration directories

**Primary Goal**: Ensure complete backup and restore capability before any live testing.

## Pre-Testing Risk Assessment

### Target Analysis
- **Project**: `/home/me/src/agents-common`
- **Config**: Claude + OpenCode coders configured
- **User Globals**:
  - `~/.claude/` (Claude Code settings)
  - `~/.vscode/` or similar (VS Code/OpenCode settings)

### Risk Levels
- **LOW**: Project per-project mode (can use git for rollback)
- **HIGH**: User global settings modification (personal configs at risk)

## Phase 1: Environment Preparation

### 1.1 Project State Backup
```bash
# Ensure clean git state
cd /home/me/src/agents-common
git status --porcelain  # Must show no changes

# Create git stash as safety net
git stash push -m "Pre-agentsmgr-populate-test backup - $(date +%Y%m%d-%H%M%S)"

# Verify stash created
git stash list | head -1
```

### 1.2 User Global Settings Backup
```bash
# Create timestamped backup directory
BACKUP_DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="$HOME/agentsmgr-test-backups-$BACKUP_DATE"
mkdir -p "$BACKUP_DIR"

# Backup Claude Code settings
if [ -d "$HOME/.claude" ]; then
    cp -r "$HOME/.claude" "$BACKUP_DIR/claude-original"
    echo "Claude settings backed up to: $BACKUP_DIR/claude-original"
fi

# Backup VS Code/OpenCode settings (check common locations)
for vscode_dir in "$HOME/.vscode" "$HOME/.config/Code/User" "$HOME/Library/Application Support/Code/User"; do
    if [ -d "$vscode_dir" ]; then
        dirname=$(basename "$vscode_dir")
        cp -r "$vscode_dir" "$BACKUP_DIR/vscode-$dirname-original"
        echo "VS Code settings backed up to: $BACKUP_DIR/vscode-$dirname-original"
    fi
done

# Create backup manifest
cat > "$BACKUP_DIR/backup-manifest.txt" << EOF
AgentsMgr Testing Backup Created: $(date)
Project: /home/me/src/agents-common
Git HEAD: $(git rev-parse HEAD)
Git Status: $(git status --porcelain | wc -l) changed files

Contents:
$(ls -la "$BACKUP_DIR")
EOF

echo "Backup directory: $BACKUP_DIR"
```

### 1.3 Environment Variable Documentation
```bash
# Document current environment for restoration
cat > "$BACKUP_DIR/environment-state.txt" << EOF
Current Environment Variables:
CLAUDE_CONFIG_DIR=${CLAUDE_CONFIG_DIR:-"<not set>"}
VSCODE_EXTENSIONS=${VSCODE_EXTENSIONS:-"<not set>"}
HOME=$HOME

Current Claude Directory Resolution:
$(test -d "$HOME/.claude" && echo "~/.claude exists" || echo "~/.claude does not exist")
EOF
```

## Phase 2: Simulation Testing

### 2.1 Project Simulation
```bash
cd /home/me/src/agents-common

# Test project-local mode (safest)
echo "=== Testing per-project mode ==="
agentsmgr populate . . --simulate --mode per-project

# Test default mode
echo "=== Testing default mode ==="
agentsmgr populate . . --simulate --mode default

# Verify no files created during simulation
git status --porcelain  # Should show no changes
```

### 2.2 User Global Simulation
```bash
# Test user global mode
echo "=== Testing per-user mode with global updates ==="
agentsmgr populate . . --simulate --mode per-user --update-globals

# Document what WOULD be affected
echo "Expected user directory targets:"
echo "Claude: $(echo ${CLAUDE_CONFIG_DIR:-$HOME/.claude})"
```

### 2.3 Isolated Testing Environment
```bash
# Create isolated test environment
TEST_CLAUDE_DIR="/tmp/agentsmgr-test-claude-$BACKUP_DATE"
mkdir -p "$TEST_CLAUDE_DIR"

# Test with isolated environment
export CLAUDE_CONFIG_DIR="$TEST_CLAUDE_DIR"
echo "=== Testing with isolated Claude directory ==="
agentsmgr populate . . --mode per-user --update-globals

# Examine results
echo "Isolated test results:"
find "$TEST_CLAUDE_DIR" -type f | head -10

# Clean up test
unset CLAUDE_CONFIG_DIR
rm -rf "$TEST_CLAUDE_DIR"
```

## Phase 3: Live Testing (Project Only)

### 3.1 Safe Project Testing
```bash
cd /home/me/src/agents-common

# Execute per-project mode (git can rollback)
echo "=== LIVE TEST: Project per-project mode ==="
agentsmgr populate . . --mode per-project

# Verify results
echo "Generated files:"
find .claude -type f 2>/dev/null | head -10

# Test functionality (if possible)
# Check that generated files are valid/readable

# Document changes
git status --porcelain > "$BACKUP_DIR/project-changes.txt"
echo "Project changes logged to: $BACKUP_DIR/project-changes.txt"
```

### 3.2 Project Rollback Test
```bash
# Test rollback capability
echo "=== Testing project rollback ==="
git stash  # Save current state
git status --porcelain  # Should show no changes

# Test restore from stash
git stash pop
echo "Rollback successful"
```

## Phase 4: Live Testing (User Globals - HIGH RISK)

### 4.1 Final Pre-flight Checks
```bash
# Verify backups are complete and accessible
echo "=== Pre-flight verification ==="
ls -la "$BACKUP_DIR/"
echo "Backup integrity check:"
test -d "$BACKUP_DIR/claude-original" && echo "✓ Claude backup present" || echo "✗ Claude backup missing"

# Test backup restore procedure (dry run)
echo "Testing restore procedure..."
if [ -d "$HOME/.claude" ]; then
    RESTORE_TEST_DIR="/tmp/restore-test-$BACKUP_DATE"
    mkdir -p "$RESTORE_TEST_DIR"
    cp -r "$BACKUP_DIR/claude-original" "$RESTORE_TEST_DIR/claude"
    echo "✓ Restore procedure verified"
    rm -rf "$RESTORE_TEST_DIR"
fi
```

### 4.2 Live User Global Testing
```bash
# POINT OF NO RETURN - User global modification
echo "=== LIVE TEST: User global settings ==="
echo "WARNING: About to modify user global settings"
echo "Backup location: $BACKUP_DIR"
read -p "Proceed? (yes/no): " confirm

if [ "$confirm" = "yes" ]; then
    cd /home/me/src/agents-common
    agentsmgr populate . . --mode per-user --update-globals

    echo "User global update completed"
    echo "Generated backups:"
    find ~/.claude -name "*.backup" 2>/dev/null | head -5
else
    echo "User global testing skipped"
fi
```

## Phase 5: Validation and Rollback Procedures

### 5.1 Validation Checks
```bash
# Test that modified settings are valid
echo "=== Validating modified settings ==="

# Check JSON validity of settings files
for settings_file in ~/.claude/settings.json ~/.vscode/settings.json; do
    if [ -f "$settings_file" ]; then
        if python3 -m json.tool "$settings_file" > /dev/null 2>&1; then
            echo "✓ $settings_file is valid JSON"
        else
            echo "✗ $settings_file has JSON errors"
        fi
    fi
done

# Test functionality (manual verification required)
echo "Manual verification required:"
echo "1. Test Claude Code functionality"
echo "2. Test VS Code/OpenCode functionality"
echo "3. Verify settings are preserved"
```

### 5.2 Emergency Rollback Procedures

#### 5.2.1 Project Rollback
```bash
# Emergency project rollback
cd /home/me/src/agents-common
git reset --hard HEAD  # Nuclear option
git clean -fd           # Remove untracked files
```

#### 5.2.2 User Settings Rollback
```bash
# Emergency user settings rollback
BACKUP_DATE="<INSERT_BACKUP_DATE>"  # From Phase 1
BACKUP_DIR="$HOME/agentsmgr-test-backups-$BACKUP_DATE"

# Restore Claude settings
if [ -d "$BACKUP_DIR/claude-original" ]; then
    rm -rf "$HOME/.claude"
    cp -r "$BACKUP_DIR/claude-original" "$HOME/.claude"
    echo "Claude settings restored from backup"
fi

# Restore VS Code settings (adjust path as needed)
for backup_dir in "$BACKUP_DIR"/vscode-*-original; do
    if [ -d "$backup_dir" ]; then
        dirname=$(basename "$backup_dir" | sed 's/-original$//' | sed 's/vscode-//')
        # Determine original path and restore
        echo "Manual restoration required for: $backup_dir"
        echo "Restore to appropriate VS Code directory"
    fi
done
```

#### 5.2.3 Selective Rollback (Settings Files Only)
```bash
# Use built-in backup files
find ~/.claude -name "*.backup" -exec bash -c '
    for backup in "$@"; do
        original="${backup%.backup}"
        echo "Restoring $original from $backup"
        cp "$backup" "$original"
    done
' _ {} +
```

## Phase 6: Post-Testing Cleanup

### 6.1 Success Path Cleanup
```bash
# If testing successful, clean up
BACKUP_DATE="<INSERT_BACKUP_DATE>"
BACKUP_DIR="$HOME/agentsmgr-test-backups-$BACKUP_DATE"

# Archive successful test
tar -czf "$HOME/agentsmgr-test-archive-$BACKUP_DATE.tar.gz" -C "$HOME" "$(basename "$BACKUP_DIR")"

# Clean up git stash if no longer needed
cd /home/me/src/agents-common
git stash drop  # Remove test stash

echo "Testing completed successfully"
echo "Archived backup: $HOME/agentsmgr-test-archive-$BACKUP_DATE.tar.gz"
```

### 6.2 Documentation of Results
```bash
# Document test results
cat > "$HOME/agentsmgr-test-results-$BACKUP_DATE.txt" << EOF
AgentsMgr Populate Command Test Results
Date: $(date)
Project: /home/me/src/agents-common

Test Phases Completed:
[ ] Phase 1: Environment Preparation
[ ] Phase 2: Simulation Testing
[ ] Phase 3: Live Project Testing
[ ] Phase 4: Live User Global Testing
[ ] Phase 5: Validation
[ ] Phase 6: Cleanup

Issues Encountered:
<document any issues>

Files Modified:
Project: $(cd /home/me/src/agents-common && git status --porcelain | wc -l) files
User Global: <manually document>

Functionality Tests:
Claude Code: <pass/fail>
VS Code/OpenCode: <pass/fail>

Recommendations:
<document any recommendations for future use>
EOF
```

## Emergency Contacts and Resources

- **Backup Location Pattern**: `$HOME/agentsmgr-test-backups-YYYYMMDD-HHMMSS/`
- **Git Project**: `/home/me/src/agents-common`
- **Key Commands**:
  - Project rollback: `git reset --hard HEAD && git clean -fd`
  - Settings rollback: Restore from `$BACKUP_DIR/*-original/`
  - Built-in backups: `~/.claude/*.backup` files

## Testing Schedule Recommendation

1. **Week 1**: Phases 1-3 (Project testing only)
2. **Week 2**: Phase 4 (User global testing) - Plan for potential downtime
3. **Rollback Window**: Keep backups for 30 days minimum

**Critical**: Do not proceed to Phase 4 without successful completion of Phases 1-3.