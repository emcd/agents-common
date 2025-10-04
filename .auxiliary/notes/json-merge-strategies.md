# JSON Merge Strategies for Settings Management

## Use Case

**Scenario**: You have a recommended/template settings file and want to merge it with user's existing settings.

**Requirements**:
1. Add keys from template that don't exist in user settings
2. Preserve user's existing values (don't overwrite)
3. Optional: Interactive diff for conflicts
4. Optional: Detect divergence from recommended settings

**Example**:

```json
// template-settings.json (recommended)
{
  "statusLine": {
    "type": "command",
    "command": "/home/me/.config/claude/statusline.py"
  },
  "alwaysThinkingEnabled": true,
  "feedbackSurveyState": {}
}

// ~/.config/claude/settings.json (user's current)
{
  "alwaysThinkingEnabled": false,  // User customized this
  "customUserSetting": "foo"       // User added this
}

// Desired result after merge
{
  "statusLine": {                  // Added from template (was missing)
    "type": "command",
    "command": "/home/me/.config/claude/statusline.py"
  },
  "alwaysThinkingEnabled": false,  // Preserved user value
  "feedbackSurveyState": {},       // Added from template (was missing)
  "customUserSetting": "foo"       // Preserved user value
}
```

## Approach Comparison

### Option 1: Custom Recursive Merge (Recommended)

**Implementation**:
```python
from typing import Any
from collections.abc import Mapping, MutableMapping

def deep_merge(
    target: MutableMapping[str, Any],
    source: Mapping[str, Any],
    *,
    overwrite: bool = False,
    path: str = "",
) -> dict[str, Any]:
    ''' Recursively merge source into target.

    Args:
        target: Existing user settings (modified in place)
        source: Template/recommended settings
        overwrite: If True, source overwrites target; if False, target wins
        path: Current path (for conflict reporting)

    Returns:
        Dictionary of conflicts: {path: (target_value, source_value)}
    '''
    conflicts = {}

    for key, source_value in source.items():
        current_path = f"{path}.{key}" if path else key

        if key not in target:
            # Key missing in target - add from source
            target[key] = source_value

        elif isinstance(target[key], dict) and isinstance(source_value, dict):
            # Both are dicts - recurse
            nested_conflicts = deep_merge(
                target[key], source_value,
                overwrite=overwrite,
                path=current_path
            )
            conflicts.update(nested_conflicts)

        elif target[key] != source_value:
            # Conflict: both exist but differ
            conflicts[current_path] = (target[key], source_value)
            if overwrite:
                target[key] = source_value

    return conflicts
```

**Usage**:
```python
import json
from pathlib import Path

def merge_settings(
    target_path: Path,
    template_path: Path,
    interactive: bool = False,
) -> None:
    ''' Merge template settings into target, preserving user values. '''

    # Load both files
    with target_path.open() as f:
        target = json.load(f)
    with template_path.open() as f:
        template = json.load(f)

    # Backup original
    backup_path = target_path.with_suffix('.json.backup')
    with backup_path.open('w') as f:
        json.dump(target, f, indent=2)

    # Merge (target wins by default)
    conflicts = deep_merge(target, template, overwrite=False)

    # Handle conflicts
    if conflicts and interactive:
        conflicts = resolve_conflicts_interactively(conflicts, target, template)

    # Write merged result
    with target_path.open('w') as f:
        json.dump(target, f, indent=2)

    # Report
    print(f"Merged {len(template)} template keys into {target_path}")
    if conflicts:
        print(f"Preserved {len(conflicts)} user customizations:")
        for path, (user_val, template_val) in conflicts.items():
            print(f"  {path}: kept '{user_val}' (template has '{template_val}')")
```

**Pros**:
- Simple, no dependencies
- Full control over merge logic
- Easy to understand and debug
- Can customize for specific data types

**Cons**:
- Must handle edge cases yourself (lists, nulls, etc.)
- No standard patch format

---

### Option 2: JSON Merge Patch (RFC 7386)

**Standard**: [RFC 7386](https://tools.ietf.org/html/rfc7386)

**Implementation**:
```python
import json_merge_patch  # pip install json-merge-patch

def merge_with_json_merge_patch(target_path: Path, template_path: Path) -> None:
    with target_path.open() as f:
        target = json.load(f)
    with template_path.open() as f:
        template = json.load(f)

    # Create patch: only missing keys from template
    patch = create_additive_patch(target, template)

    # Apply patch
    result = json_merge_patch.merge(target, patch)

    with target_path.open('w') as f:
        json.dump(result, f, indent=2)

def create_additive_patch(
    target: dict, template: dict
) -> dict:
    ''' Create patch that only adds missing keys. '''
    patch = {}
    for key, value in template.items():
        if key not in target:
            patch[key] = value
        elif isinstance(value, dict) and isinstance(target[key], dict):
            nested_patch = create_additive_patch(target[key], value)
            if nested_patch:
                patch[key] = nested_patch
    return patch
```

**Pros**:
- Standard format (RFC 7386)
- Simple semantics
- Can represent patches as data

**Cons**:
- Cannot represent "delete this key" well (uses `null`)
- Still need custom logic for additive-only merge
- Less intuitive for complex operations

---

### Option 3: JSON Patch (RFC 6902)

**Standard**: [RFC 6902](https://tools.ietf.org/html/rfc6902)

**Implementation**:
```python
import jsonpatch  # pip install jsonpatch

def create_additive_patch_operations(
    target: dict, template: dict, path: str = ""
) -> list[dict]:
    ''' Create JSON Patch operations to add missing keys. '''
    operations = []

    for key, value in template.items():
        current_path = f"{path}/{key}"

        if key not in target:
            # Add missing key
            operations.append({
                'op': 'add',
                'path': current_path,
                'value': value
            })
        elif isinstance(value, dict) and isinstance(target.get(key), dict):
            # Recurse into nested objects
            operations.extend(
                create_additive_patch_operations(
                    target[key], value, current_path
                )
            )

    return operations

def merge_with_json_patch(target_path: Path, template_path: Path) -> None:
    with target_path.open() as f:
        target = json.load(f)
    with template_path.open() as f:
        template = json.load(f)

    # Create operations for missing keys
    operations = create_additive_patch_operations(target, template)

    # Apply patch
    patch = jsonpatch.JsonPatch(operations)
    result = patch.apply(target)

    with target_path.open('w') as f:
        json.dump(result, f, indent=2)

    print(f"Applied {len(operations)} operations:")
    for op in operations:
        print(f"  {op['op']} {op['path']}")
```

**Pros**:
- Precise operation semantics
- Serializable patches
- Can save/version patches
- Good for auditing changes

**Cons**:
- More complex than needed
- Overkill for simple merge
- Still need custom logic to generate patches

---

### Option 4: Interactive Diff with Merge Tool

**Use existing diff/merge tools**:

```python
import subprocess
import tempfile
from pathlib import Path

def interactive_merge_with_difftool(
    target_path: Path,
    template_path: Path,
    tool: str = 'vimdiff'  # or 'meld', 'kdiff3', etc.
) -> None:
    ''' Launch interactive merge tool for user to resolve. '''

    # Create merged baseline (additive merge)
    with target_path.open() as f:
        target = json.load(f)
    with template_path.open() as f:
        template = json.load(f)

    conflicts = deep_merge(target, template, overwrite=False)
    merged = target.copy()

    # Write to temp files
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(target, f, indent=2)
        target_temp = Path(f.name)

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(merged, f, indent=2)
        merged_temp = Path(f.name)

    try:
        # Launch diff tool
        subprocess.run([tool, str(target_temp), str(merged_temp)], check=True)

        # Ask user which to keep
        print("\nWhich version would you like to keep?")
        print(f"1. Original ({target_path})")
        print(f"2. Merged ({len(template) - len(conflicts)} new keys)")
        choice = input("Choice [1/2]: ")

        if choice == '2':
            with merged_temp.open() as f:
                result = json.load(f)
            with target_path.open('w') as f:
                json.dump(result, f, indent=2)
            print(f"✓ Merged settings written to {target_path}")

    finally:
        target_temp.unlink()
        merged_temp.unlink()
```

**Pros**:
- Familiar UI for developers
- Visual comparison
- User has full control

**Cons**:
- Requires external tool
- Not scriptable
- May be intimidating for non-developers

---

### Option 5: Structured Conflict Resolution (Recommended for Interactive)

**Implementation**:
```python
def resolve_conflicts_interactively(
    conflicts: dict[str, tuple[Any, Any]],
    target: dict,
    template: dict,
) -> dict[str, tuple[Any, Any]]:
    ''' Present conflicts to user for resolution. '''
    resolved = {}

    print(f"\nFound {len(conflicts)} differences between your settings and template:\n")

    for path, (user_value, template_value) in conflicts.items():
        print(f"Setting: {path}")
        print(f"  Your value:     {json.dumps(user_value)}")
        print(f"  Template value: {json.dumps(template_value)}")

        while True:
            choice = input("Keep [u]ser value, use [t]emplate, or [s]kip? [u/t/s]: ").lower()

            if choice == 'u':
                resolved[path] = (user_value, template_value)
                break
            elif choice == 't':
                # Update target with template value
                _set_nested_value(target, path, template_value)
                break
            elif choice == 's':
                # Keep user value (default)
                resolved[path] = (user_value, template_value)
                break
            else:
                print("Invalid choice. Please enter 'u', 't', or 's'.")

        print()

    return resolved

def _set_nested_value(d: dict, path: str, value: Any) -> None:
    ''' Set value at nested path (e.g., 'foo.bar.baz'). '''
    keys = path.split('.')
    for key in keys[:-1]:
        d = d[key]
    d[keys[-1]] = value
```

**Enhanced Usage**:
```python
def smart_merge_settings(
    target_path: Path,
    template_path: Path,
    *,
    interactive: bool = True,
    show_diff: bool = True,
) -> None:
    ''' Smart merge with optional interactivity. '''

    with target_path.open() as f:
        target = json.load(f)
    with template_path.open() as f:
        template = json.load(f)

    # Backup
    backup_path = target_path.with_suffix('.json.backup')
    target_path.rename(backup_path)

    # Merge
    conflicts = deep_merge(target, template, overwrite=False)

    # Report additions
    added_keys = _find_added_keys(target, template)
    if added_keys:
        print(f"✓ Added {len(added_keys)} missing settings from template:")
        for key in added_keys:
            print(f"  + {key}")

    # Handle conflicts
    if conflicts:
        print(f"\n⚠ Found {len(conflicts)} settings that differ from template:")
        if interactive:
            resolve_conflicts_interactively(conflicts, target, template)
        else:
            for path, (user_val, _) in conflicts.items():
                print(f"  ≠ {path}: keeping your value '{user_val}'")

    # Show diff if requested
    if show_diff and (added_keys or conflicts):
        _show_json_diff(backup_path, target)

    # Write result
    with target_path.open('w') as f:
        json.dump(target, f, indent=2)

    print(f"\n✓ Settings updated. Backup saved to {backup_path}")

def _find_added_keys(target: dict, template: dict, path: str = "") -> list[str]:
    ''' Recursively find keys added from template. '''
    added = []
    for key, value in template.items():
        current_path = f"{path}.{key}" if path else key
        if key not in target:
            added.append(current_path)
        elif isinstance(value, dict) and isinstance(target.get(key), dict):
            added.extend(_find_added_keys(target[key], value, current_path))
    return added

def _show_json_diff(old_path: Path, new: dict) -> None:
    ''' Show colored diff between old file and new dict. '''
    import difflib

    with old_path.open() as f:
        old_lines = f.readlines()

    new_lines = json.dumps(new, indent=2).splitlines(keepends=True)

    diff = difflib.unified_diff(
        old_lines, new_lines,
        fromfile=str(old_path),
        tofile='merged',
        lineterm=''
    )

    for line in diff:
        if line.startswith('+'):
            print(f'\033[32m{line}\033[0m', end='')  # Green
        elif line.startswith('-'):
            print(f'\033[31m{line}\033[0m', end='')  # Red
        else:
            print(line, end='')
```

---

## Recommendation

**For your use case**, I recommend **Option 5 (Structured Conflict Resolution)** because:

1. **Additive-only merge is trivial**: Just recursive dict merge with user values winning
2. **Interactive resolution is valuable**: Users want to see what changed
3. **No heavy dependencies**: Pure Python + stdlib
4. **Excellent UX**: Clear output, user control, safety (backups)
5. **Auditable**: Shows exactly what was added/changed

**CLI Integration**:
```bash
# Non-interactive (safe default): add missing keys, keep user values
agentsmgr settings merge --template=recommended-claude.json --target=~/.config/claude/settings.json

# Interactive: prompt for conflicts
agentsmgr settings merge --template=recommended-claude.json --target=~/.config/claude/settings.json --interactive

# Show diff
agentsmgr settings merge --template=recommended-claude.json --target=~/.config/claude/settings.json --show-diff

# Force overwrite (use template values)
agentsmgr settings merge --template=recommended-claude.json --target=~/.config/claude/settings.json --overwrite
```

**Output Example**:
```
✓ Added 2 missing settings from template:
  + statusLine.type
  + statusLine.command

⚠ Found 1 setting that differs from template:
  ≠ alwaysThinkingEnabled: keeping your value 'false'

✓ Settings updated. Backup saved to settings.json.backup
```

---

## When to Use jsonpatch

Use `jsonpatch` (RFC 6902) specifically when:

1. **Storing patches as configuration**: You want to save the "diff" itself
   ```json
   [
     {"op": "add", "path": "/statusLine", "value": {...}},
     {"op": "replace", "path": "/alwaysThinkingEnabled", "value": true}
   ]
   ```

2. **API-driven updates**: REST APIs that accept PATCH requests
   ```bash
   curl -X PATCH /api/settings -d '[{"op": "add", "path": "/theme", "value": "dark"}]'
   ```

3. **Version control for settings**: Track changes over time
   ```bash
   git log settings-patches/  # History of setting changes as patch files
   ```

4. **Distributed updates**: Multiple sources modifying same config
   - Need conflict resolution
   - Want to replay patches in order

For simple "merge template into user settings", custom recursive merge is cleaner and more maintainable.
