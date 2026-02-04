# Claude Statusline Token Calculation Discrepancy

## Problem

The statusline token usage calculation shows significantly lower context usage
than Claude Code's auto-compact warning.

Example observation:
```
🟢 67k/200k (34%) | 📁 ~/src/wt-vibe-py-linter--fixer | 🌿 fixer | 🧠 Opus 4.5
Context left until auto-compact: 6%
```

Statusline shows 34% used, but Claude Code reports only 6% remaining (94% used).

## Current Calculation

The statusline uses `context_window` from the status hook JSON:

```json
"context_window": {
  "total_input_tokens": 15234,
  "total_output_tokens": 4521,
  "context_window_size": 200000
}
```

Calculation: `(total_input_tokens + total_output_tokens) / context_window_size`

## Suspected Cause

The `context_window` fields likely exclude:
- System prompts
- Tool definitions
- MCP server instructions
- Cached content

These can consume substantial context, especially in projects with extensive
CLAUDE.md instructions, multiple MCP servers, and many tool definitions.

## Possible Solutions

1. **Wait for API improvement**: Request that Claude Code include total context
   usage (including system content) in the status hook JSON.

2. **Estimate overhead**: Add a configurable overhead factor to approximate
   system content usage, though this would be imprecise.

3. **Parse transcript**: Return to transcript parsing if it provides more
   accurate token counts, though this was previously replaced due to complexity.

## Status

Documented for future investigation. The current statusline provides useful
relative usage trends but absolute percentages are unreliable.
