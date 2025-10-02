# TODO

## Code Quality

- [ ] **Replace plural-to-singular string heuristic with explicit mapping**: In `ContentGenerator._get_available_templates()` and `._select_template_for_coder()`, replace `.rstrip('s')` with a mapping dict like `{'commands': 'command', 'agents': 'agent'}` for robustness (sources/agentsmgr/commands.py:321-322, 337)
- [ ] **Design and implement configuration-based coder fallbacks**: Replace hardcoded `fallback_map = {"claude": "opencode", "opencode": "claude"}` in `ContentGenerator._get_content_with_fallback()` with configuration-driven system that supports Gemini and future coders (sources/agentsmgr/commands.py:195)

## Features

- [ ] **Support subdirectory specification in remote repository URLs**: When implementing remote git source support (e.g., `gh:emcd/agents-common`), need mechanism to specify data directory within repository. Current `--command.source=defaults` works for local paths but won't translate to remote URLs. Consider URL fragment syntax (e.g., `gh:emcd/agents-common#defaults`) or query parameter approach (e.g., `gh:emcd/agents-common?path=defaults`)

## Documentation

## Testing
