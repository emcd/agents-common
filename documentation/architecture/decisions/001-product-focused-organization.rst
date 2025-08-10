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

Adopt a product-focused organizational structure using ``products/`` as the 
top-level directory, with each AI tool maintaining its own dedicated subdirectory 
structure containing tool-specific resource types.

The implemented structure:

.. code-block::

    products/
    ├── claude/
    │   ├── agents/          # Subagent definitions
    │   ├── commands/        # Slash commands  
    │   ├── miscellany/      # Templates, snippets
    │   ├── scripts/         # Hook executables
    │   └── configuration/   # Settings templates
    └── gemini/
        ├── commands/        # Command definitions
        └── configuration/   # Settings templates

Directory naming follows consistent Latin-derived terminology to maintain 
linguistic consistency across the project (``configuration/`` instead of 
``settings/`` to match ``agents``, ``commands``, ``miscellany``, ``scripts``).

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

* **Clear Resource Ownership**: Each AI tool owns its complete set of configurations 
  in one location
* **Natural Scalability**: New AI tools can be added without restructuring existing 
  content
* **User-Friendly Navigation**: Users working with specific AI tools find all 
  relevant resources in one place
* **Tool Independence**: Each tool can evolve its resource structure independently
* **Naming Clarity**: Avoids confusing directory names like ``agents/claude/agents``
* **Consistent Taxonomy**: Latin-derived naming provides linguistic consistency

**Negative Consequences:**

* **Cross-Tool Comparison**: Comparing similar resources across tools requires 
  navigating multiple directories
* **Resource Duplication**: Shared resources may be duplicated across tool 
  directories (mitigated by future shared resources strategy)

**Neutral Consequences:**

* **Directory Depth**: Creates additional directory level but maintains reasonable 
  navigation depth
* **Template Complexity**: Template generation must handle product-specific paths 
  but this aligns with the tool-specific nature of configurations