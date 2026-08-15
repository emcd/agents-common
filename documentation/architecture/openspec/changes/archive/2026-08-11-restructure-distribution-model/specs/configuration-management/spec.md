## MODIFIED Requirements

### Requirement: Data-Driven Repository Structure

The repository SHALL organize AI tool configurations as structured data sources
with clear separation between source material, distribution artifacts, and
maintainer tooling.

#### Scenario: Skills as a first-class item type
- **WHEN** reusable expertise is added to the repository
- **THEN** it can be represented as "skills" with:
  - tool-agnostic metadata
  - a tool-agnostic body by default (with optional tool-specific overrides)
  - templates that emit tool-compatible frontmatter and discovery paths

#### Scenario: Tool-specific permissions mapping
- **WHEN** a skill specifies "allowed tools" in tool-agnostic semantic form
- **THEN** the system maps/format those tool specifications per coder where
  supported
- **AND** the system omits or warns for fields that are unsupported by a given
  target tool (without failing generation)

#### Scenario: Distribution tree structure
- **WHEN** content is organized for distribution
- **THEN** it is stored under `distribution/` with `per-project/` and `per-user/` subtrees
- **AND** `per-project/general/` contains coder-agnostic content (skills, instructions)
- **AND** `per-project/coders/<coder>/` contains coder-specific content

#### Scenario: Components tree structure
- **WHEN** source material for generating artifacts is maintained
- **THEN** it is stored under `components/` with `configurations/`, `templates/`, and `contents/` subtrees
- **AND** only command and agent types are generated from components
- **AND** skills and instructions are distributed directly from `distribution/`
