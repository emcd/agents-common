# TODO

## Code Quality

- [ ] **Replace plural-to-singular string heuristic with explicit mapping**: In `ContentGenerator._get_available_templates()` and `._select_template_for_coder()`, replace `.rstrip('s')` with a mapping dict like `{'commands': 'command', 'agents': 'agent'}` for robustness (sources/agentsmgr/commands.py:321-322, 337)

## Features

## Documentation

## Testing
