*******************************************************************************
001. Product-Focused Repository Organization
*******************************************************************************

Status
===============================================================================

Accepted

Context
===============================================================================

The agents-common repository needs to organize AI agent configurations for 
multiple tools including Claude Code, Gemini CLI, and future AI development 
environments. Several organizational approaches were considered:

**Function-First Organization**: Commands, agents, templates, and scripts grouped 
by type across all AI tools (``commands/claude/``, ``commands/gemini/``, etc.).

**Tool-First Organization**: Each AI tool maintains dedicated directory structure 
(``claude/``, ``gemini/``, etc.) with tool-specific subdirectories.

**Flat Organization**: All configurations in top-level directories without 
hierarchical structure.

Key forces driving this decision include:

* Different AI tools have significantly different capabilities (Claude has 
  subagents, Gemini does not)
* Users typically focus on one AI tool at a time during development
* AI tools evolve independently with different release cycles  
* Need to avoid naming conflicts like ``agents/claude/agents``
* Must support clean extensibility for future AI tools

Decision
===============================================================================

Adopt a product-focused organizational structure with tool-specific resource 
organization in both source data and generated template output.

The implemented structure:

.. code-block::

    data/                    # Source data organized by resource type
    ├── commands/           # TOML command definitions 
    ├── agents/             # Agent definitions
    ├── scripts/            # Hook executables
    └── miscellany/         # Templates, snippets
    
    template/               # Generated Copier template output
    └── .auxiliary/
        └── configuration/
            ├── claude/     # Generated Claude configurations
            │   ├── agents/
            │   ├── commands/
            │   ├── scripts/
            │   └── settings.json.jinja
            ├── opencode/   # Generated Opencode configurations  
            │   └── commands/
            └── gemini/     # Generated Gemini configurations
                ├── commands/
                └── settings.json.jinja

**Data Organization**: Source data in ``data/`` is organized by resource type 
to enable generation of multiple tool configurations from common sources, 
eliminating format-specific maintenance overhead.

**Template Organization**: Generated output in ``template/`` maintains product-focused 
structure with each AI tool receiving dedicated directories containing tool-specific 
configurations generated from the common data sources.

Directory naming follows consistent Latin-derived terminology (``configuration/`` 
instead of ``settings/`` to match ``agents``, ``commands``, ``miscellany``, ``scripts``).

Alternatives
===============================================================================

**Function-First Organization** was rejected because:
- Creates artificial separation between related tool-specific resources
- Makes it difficult to understand what resources are available for a specific tool
- Requires restructuring when tools have unique resource types
- Complicates maintenance when tools evolve different capabilities

**Flat Organization** was rejected because:
- Does not scale as the number of tools and resource types grows
- Creates naming conflicts and confusion about resource relationships
- Provides no logical grouping for related configurations
- Makes it difficult to locate tool-specific resources

**Mixed Approach** (some resources grouped by function, others by tool) was 
rejected because:
- Creates inconsistent organizational patterns
- Increases cognitive load for users navigating the repository
- Makes it unclear where new resources should be placed

Consequences
===============================================================================

**Positive Consequences:**

* **Single Source Maintenance**: Common data sources eliminate duplication while 
  maintaining tool-specific output organization
* **Clear Tool Boundaries**: Generated template output provides clear ownership 
  and organization for each AI tool's configurations
* **Natural Scalability**: New AI tools can be added by extending generation 
  logic without restructuring existing content
* **User-Friendly Navigation**: Projects applying the template find all relevant 
  resources for specific AI tools in dedicated directories
* **Elimination of Format Duplication**: Tool format variations (like Opencode 
  command filtering) handled at generation time rather than maintained separately

**Negative Consequences:**

* **Build Step Dependency**: Requires generation step to transform data into 
  tool-specific formats
* **Two-Level Organization**: Repository contains both source data organization 
  and output template organization patterns

**Neutral Consequences:**

* **Directory Depth**: Template output creates additional directory levels but 
  maintains reasonable navigation depth for downstream projects
* **Generation Complexity**: Build process must handle data-to-template transformation 
  but this aligns with the goal of eliminating format-specific maintenance