# agentsmgr CLI Architecture Plan

## Executive Summary

The `agentsmgr` CLI generates dynamic agent content from structured data sources, completing the hybrid Copier + agentsmgr approach for distributing coder-specific settings.

## Implementation Status

**Phases 1-2** ✅ **COMPLETED**
- Template structure with `.gitignore` patterns
- TOML configurations, content files, Jinja2 templates
- Data directory separation: `defaults/` (unpublished) vs `data/agentsmgr/` (published)

**Phase 3: Core CLI** ✅ **COMPLETED**
- DetectCommand, SurveyCommand, ValidateCommand, PopulateCommand (simulation only)
- TOML parsing with frontmatter extraction
- Template rendering pipeline with Claude↔OpenCode fallback
- Standalone file writing functions
- Result objects with Markdown rendering

**Phase 3.3: Live File Writing** ⚠️ **NEXT**
- Enable PopulateCommand to write files to target projects
- Integrate `generate_items_to_directory()` and `update_content()` functions
- Track and report actual item counts

## Architecture Reference

**Pattern**: Follow `python-appcore` simple command inheritance (not `python-librovore`'s complex multi-processor system)

**Implemented Commands**:
- `DetectCommand`: Display Copier configuration from target directory
- `SurveyCommand`: List available configuration variants
- `ValidateCommand`: Test generation in temporary directory with variant profiles
- `PopulateCommand`: Generate content (currently simulation-only)

## Key Implementation Details

**Configuration Detection**: Loads `copier-answers--agents.yaml` from `.auxiliary/configuration/`, validates required fields (coders, languages)

**Content Pipeline**:
1. TOML parsing: Extract `[frontmatter]` and `[[coders]]` metadata
2. Content lookup: Claude↔OpenCode fallback for shared content
3. Template selection: Plural→singular conversion (e.g., "commands" → "command.md.jinja")
4. Jinja2 rendering: Spread frontmatter and coder config into template variables
5. File writing: Standalone `update_content()` and `generate_items_to_directory()` functions

**Data Sources**:
- Current: Local path support only (`_retrieve_data_location()`)
- Future: Git URL support (`gh:`, HTTPS, SSH)

## Next Steps

**Phase 3.3 Tasks**:
1. Update `PopulateCommand.execute()` to use `generate_items_to_directory()`
2. Replace simulation-only with actual file writes (controlled by `--simulate` flag)
3. Return actual item counts in `ContentGenerationResult`
4. Test with real project targets

**Future Enhancements**:
- OpenCode and Gemini coder support
- Git data source support with caching
- Template debugging and content preview modes
- Copier hook integration for automatic updates