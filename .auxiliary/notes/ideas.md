# Ideas and Future Considerations

## Openspec Template Enhancement

**Idea:** Add conditional filesystem.rst reference to `template/documentation/architecture/openspec/project.md.jinja`

**Implementation:**
```jinja
## Project Conventions

### Code Style
...

{%- if "python" in languages %}
### Filesystem Organization
See `documentation/architecture/filesystem.rst` for module layout, import patterns, and project structure conventions.
{%- endif %}
```

**Pros:**
- Automatic for Python projects generated from template
- Minimal divergence (just a reference, not content duplication)
- Single source of truth maintained (filesystem.rst)
- Language-specific (only appears for Python projects)

**Cons:**
- Creates divergence from stock Openspec project.md
- May conflict with `openspec update` (though it shouldn't if outside managed blocks)
- Requires maintenance as template evolves

**Decision:** Deferred - using prompts/openspec-init.md approach first to document the manual process. May automate later if the pattern proves valuable.
