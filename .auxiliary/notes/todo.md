# TODO

## Code Quality

## Features

- [ ] **Implement source precedence hierarchy**: Extend source resolution to follow CLI → environment → configuration precedence. Currently CLI only supports explicit `--source` parameter. Add environment variable support (e.g., `AGENTSMGR_SOURCE`) and configuration file fallback using `sources.default` from `data/configuration/general.toml`. Update `retrieve_data_location()` in `sources/agentsmgr/commands/base.py` to implement this precedence chain.

- [ ] **Support subdirectory specification in remote repository URLs**: When implementing remote git source support (e.g., `gh:emcd/agents-common`), need mechanism to specify data directory within repository. Current `--command.source=defaults` works for local paths but won't translate to remote URLs. Consider URL fragment syntax (e.g., `gh:emcd/agents-common#defaults`) or query parameter approach (e.g., `gh:emcd/agents-common?path=defaults`)

## Documentation

## Testing
