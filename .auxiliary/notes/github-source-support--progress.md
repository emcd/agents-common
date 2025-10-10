# GitHub Source Support Implementation

### Context and References
- **Implementation Title**: GitHub source location scheme support for agentsmgr
- **Start Date**: 2025-10-09
- **Reference Files**:
  - `.auxiliary/notes/github.md` - Complete technical analysis and implementation plan
  - `sources/agentsmgr/commands/base.py` - Current source resolution logic
  - `sources/agentsmgr/exceptions.py` - Exception hierarchy for error handling
  - `data/configuration/general.toml` - Configuration structure with sources.default
- **Design Documents**: `.auxiliary/notes/github.md` provides comprehensive architecture
- **Session Notes**: Tracked via TodoWrite tool for immediate task management

### Design and Style Conformance Checklist
- [x] Module organization follows practices guidelines
- [x] Function signatures use wide parameter, narrow return patterns
- [x] Type annotations comprehensive with TypeAlias patterns
- [x] Exception handling follows Omniexception → Omnierror hierarchy
- [x] Naming follows nomenclature conventions
- [x] Immutability preferences applied
- [x] Code style follows formatting guidelines

### Implementation Progress Checklist
- [x] Source handler abstraction (AbstractSourceHandler protocol)
- [x] Local source handler (move existing logic)
- [x] Git source handler with Dulwich integration
- [x] URL parsing and scheme mapping logic
- [x] Fragment syntax support for subdirectories
- [x] Update retrieve_data_location() integration
- [x] Add Dulwich dependency to pyproject.toml
- [ ] Integration testing with real repositories

### Quality Gates Checklist
- [x] Linters pass (`hatch --env develop run linters`)
- [x] Type checker passes
- [x] Tests pass (`hatch --env develop run testers`)
- [x] Code review ready

### Decision Log
- [2025-10-09] Use "sources" package name instead of "resolvers" - aligns with existing configuration naming
- [2025-10-09] Choose Dulwich over GitHub API - provides universal Git support and better authentication
- [2025-10-09] Fragment syntax (#) for subdirectory specification - familiar from web URLs and git references
- [2025-10-09] Create minimal type stubs for Dulwich instead of auto-generated ones - avoids complex typing issues
- [2025-10-09] Use pluggable handler architecture with registration - enables extensibility and clean separation

### Handoff Notes
For future sessions or other developers:
- **Current State**: Core implementation complete, all quality gates passed
- **Next Steps**: Integration testing with real GitHub repositories (github:emcd/agents-common#defaults)
- **Known Issues**: New source handlers have 0% test coverage (expected for new implementation)
- **Context Dependencies**:
  - Created `sources/agentsmgr/sources/` subpackage with AbstractSourceHandler protocol
  - Modified `retrieve_data_location()` to delegate to pluggable handlers
  - Added Dulwich dependency and minimal type stubs