# Openspec Integration Notes

This file tracks additional ideas and tasks related to Openspec integration.

## AGENTS.md Consolidation (Future Consideration)

### Current State

Multiple AGENTS.md files exist:
- `.auxiliary/configuration/AGENTS.md` - Project-specific AI instructions
- `documentation/architecture/openspec/AGENTS.md` - Openspec workflow instructions
- `template/documentation/architecture/openspec/AGENTS.md` - Template for new projects

### Proposed Consolidation

**Option 1: Symlink + Merge Content**
```bash
# Merge project-specific content into openspec/AGENTS.md
# Symlink for backward compatibility
ln -s ../../documentation/architecture/openspec/AGENTS.md .auxiliary/configuration/AGENTS.md
```

**Merged structure:**
```markdown
# Project Context
[Current .auxiliary/configuration/AGENTS.md content]
- Project overview, MCP servers, operation guidelines

# OpenSpec Instructions
[Current openspec/AGENTS.md content]
- Openspec workflow, validation, conventions

# Project Standards (ADDED)
Before any design or implementation:
- Read @.auxiliary/instructions/practices.rst
- Read @.auxiliary/instructions/practices-python.rst
- Read @.auxiliary/instructions/nomenclature.rst

Quality gates:
```bash
hatch --env develop run linters  # Includes vibelinter
hatch --env develop run testers
```

# Commits
[Git workflow from .auxiliary/configuration/AGENTS.md]

# Project Notes
[Project-specific notes]
```

**Benefits:**
- ✅ Single source of AI instructions
- ✅ Openspec instructions include project standards
- ✅ `openspec update` updates both project and Openspec instructions
- ✅ Template includes project standards by default

**Challenges:**
- ⚠️ `openspec update` might overwrite project-specific customizations
- ⚠️ Need to ensure project standards section is preserved during updates
- ⚠️ Template needs to be customizable per project

### Template Enhancement Strategy

**Current Openspec template:**
- Generic Openspec workflow instructions
- No project-specific standards

**Enhanced template for agents-common projects:**
```markdown
# [Project Name] OpenSpec Guide

## Project Context
- Project overview: @README.rst
- Architecture: @documentation/architecture/
- Practices: @.auxiliary/instructions/
- Current work: @.auxiliary/notes/

## OpenSpec Instructions
[Standard Openspec workflow from upstream]

## Project Standards (CUSTOMIZABLE SECTION)

### Before Creating Proposals
Prerequisites:
1. Read @.auxiliary/instructions/practices.rst
2. Read @.auxiliary/instructions/practices-python.rst (for Python)
3. Read @.auxiliary/instructions/practices-rust.rst (for Rust)
4. Read @.auxiliary/instructions/nomenclature.rst

### Quality Gates
All implementations MUST pass:
```bash
hatch --env develop run linters  # Project-specific linters
hatch --env develop run testers
```

See @.auxiliary/instructions/validation.rst for details.

### Implementation Standards
[Project-specific requirements from practices guides]
- Wide parameter, narrow return patterns
- Exception hierarchy (Omnierror)
- Immutability preferences
- Documentation (narrative mood)

## Commits
[Project git workflow]

## Project Notes
[Project-specific context]
```

**Implementation approach:**
1. Create enhanced template with project standards section
2. Use Copier to distribute to projects
3. Ensure `openspec update` preserves custom sections
4. Test that managed blocks (`<!-- OPENSPEC:START -->`) work correctly

### Tasks (Future)

- [ ] Test if `openspec update` preserves custom content outside managed blocks
- [ ] Create enhanced AGENTS.md template with project standards
- [ ] Add project standards section to current openspec/AGENTS.md
- [ ] Test symlink approach (.auxiliary/configuration → openspec/)
- [ ] Update Copier template to include enhanced AGENTS.md
- [ ] Document which sections are managed vs custom
- [ ] Validate workflow with both files merged

### Decision Points

**When to consolidate:**
- After validating Openspec workflow with current structure
- After confirming `openspec update` behavior with custom content
- When template enhancement is ready for distribution

**Alternatives:**
1. Keep separate files but cross-reference (current approach)
2. Merge into single file with clear section boundaries
3. Use symlink but maintain separate concerns

### Open Questions

1. **Update behavior:** Does `openspec update` preserve content outside managed blocks?
2. **Customization:** Can we mark sections as "project-specific, do not overwrite"?
3. **Template distribution:** How to maintain enhanced template across projects via Copier?
4. **Backward compatibility:** How to handle existing projects during migration?

---

## Related Notes

- Implementation plan: `openspec-designs.md`
- Architecture ideas: `openspec-adrs.md`
- Migration prompts: `openspec-migration.md`
