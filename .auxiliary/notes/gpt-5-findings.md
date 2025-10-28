# GPT-5 Findings

## Renderer-specific symlink orchestration
- **Context**: `sources/agentsmgr/population.py:192`
- ` _create_coder_directory_symlinks` contains coder-specific behavior (special handling for Claude, knowledge of individual directories) even though renderers already encapsulate per-coder filesystem rules.
- **Opportunity**: move symlink definitions into each renderer (e.g., expose `project_symlinks(target)`), so the population logic just iterates coders and asks their renderer which links to create. This removes the need for special cases and keeps knowledge about MCP files and directory aliases next to the renderer that owns them.

## Centralized coder configuration extraction
- **Context**: `sources/agentsmgr/renderers/claude.py:96`, `renderers/codex.py:99`, `renderers/opencode.py:113`, `renderers/gemini.py:98`, `renderers/qwen.py:97`
- Every renderer reimplements `_extract_coder_configuration` plus nearly identical precedence logic (ENV → config override → default path) for resolving per-user directories.
- **Opportunity**: share this logic in `RendererBase` (or a mixin/data descriptor), letting each renderer provide its env-var name and default path. That reduces duplication, makes new renderers cheaper to add, and ensures precedence bugs get fixed centrally.

## Polymorphic tool mapping for render context
- **Context**: `sources/agentsmgr/context.py:63-146`
- `normalize_render_context` hard-codes coder names when mapping semantic tools to concrete tool identifiers, forcing the shared context module to evolve whenever a new coder arrives.
- **Opportunity**: teach renderers (or a registry) how to map tools, e.g., `renderer.map_tools(tool_specs)`. `normalize_render_context` would simply look up the renderer for the current coder and delegate, keeping coder-specific logic encapsulated and easing future extensions.

## Broken-symlink detection branch (needs human review)
- **Context**: `sources/agentsmgr/memorylinks.py:60-78`
- The `elif not link_path.exists() and link_path.is_symlink()` branch is unreachable because `is_symlink()` is checked first. Broken symlinks therefore never take the intended code path, which might hide edge cases.
- **Flag**: Verify with a human before changing; deleting the redundant branch and explicitly handling broken links in the first clause would make the intent clearer.
