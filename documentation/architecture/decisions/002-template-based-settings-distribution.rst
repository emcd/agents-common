*******************************************************************************
002. Template-Based Settings Distribution
*******************************************************************************

Status
===============================================================================

Accepted

Context
===============================================================================

AI agent settings files (like Claude Code's ``settings.json``) contain both
static configuration and dynamic hook configurations that reference script paths.
This creates a coordination problem between distributed configurations and actual
script locations across different deployment environments.

Key challenges include:

* Hook configurations must reference script paths that exist in target environments
* Settings files are inherently project-specific (file paths, project-specific hooks)
* Base settings need to be consistent while allowing project customization
* Must avoid duplicating Copier's templating functionality
* Need to maintain compatibility with existing AI tool expectations

Several approaches were considered:

**Direct Distribution**: Distribute complete ``settings.json`` files with hardcoded paths.

**Configuration Merging**: Use git diff-based algorithms similar to Copier for
merging base and project-specific settings.

**Custom CLI Renderer**: Use Jinja2 templates with custom CLI tooling for
settings generation and local override support.

**Copier Template Integration**: Transform agents-common into a Copier template
that generates tool configurations from structured data sources.

Decision
===============================================================================

Implement a hybrid approach combining Copier template distribution for base
configuration templates with ``agentsmgr`` tool for dynamic content generation
directly in downstream projects from structured data sources.

The approach includes:

**Data-Driven Source Structure**:

- ``data/`` directory contains structured sources (TOML command definitions,
  agent configurations, hook scripts, tool-specific Jinja2 templates)
- ``agentsmgr populate`` generates content directly in downstream projects
- Single source of truth maintained in structured, tool-agnostic format

**Minimal Copier Template** (``template/.auxiliary/configuration/``):

- Contains base configuration templates (settings.json.jinja, mcp-servers.json.jinja)
- Provides directory structure with .gitignore files for generated content
- README files indicating dynamic generation via agentsmgr
- Standard Copier template structure for base distribution

**Dynamic Content Generation**:

- ``agentsmgr populate --source=agents-common@tag`` generates commands, agents, scripts
- Content generated directly in downstream projects, not committed to version control
- Tool-specific formats handled at generation time from common data sources
- Configuration detected from Copier answers files or defaults

Alternatives
===============================================================================

**Direct Distribution** was rejected because:
- Cannot handle path coordination between different deployment environments
- Requires hardcoded paths that break across different project structures
- No mechanism for project-specific customization
- Creates maintenance burden for path updates

**Configuration Merging** was rejected because:
- Adds significant complexity with git diff algorithms
- Difficult to handle conflicts between base and project settings
- More complex than the coordination problem warrants
- Increases maintenance overhead for merge conflict resolution

**Pure Copier Template** was rejected because:
- Generated artifacts committed to version control create repository noise
- Command changes require template generation, commit, tag, and update cycle
- Slower iteration velocity for dynamic content like commands and agents
- Template repository grows with generated content rather than source data

**Custom CLI Renderer Only** was rejected because:
- Base configuration templates benefit from Copier's proven distribution mechanisms
- Projects lose standard multi-template workflow patterns
- Does not leverage existing Copier infrastructure for settings and structure

Consequences
===============================================================================

**Positive Consequences:**

* **Faster Iteration Cycle**: Command changes don't require template commits, tags, or releases
* **Repository Efficiency**: No generated artifacts committed, cleaner git history
* **Proven Base Distribution**: Settings templates use Copier's mature mechanisms
* **True Tool Portability**: ``agentsmgr`` works with any data source, not repository-specific
* **Minimal Commit Noise**: Generated content ignored via .gitignore in downstream projects
* **Clean Separation**: Static base templates vs. dynamic generated content
* **Multi-Tool Scaling**: Single data source generates configurations for multiple AI tools

**Negative Consequences:**

* **Tool Installation Requirement**: Projects need ``agentsmgr`` available for setup
* **Network Dependency**: Requires access to agents-common repository for content generation
* **Configuration Detection**: Additional logic needed to detect project configuration from Copier answers

**Neutral Consequences:**

* **Hybrid Workflow**: Projects use both Copier updates and agentsmgr commands for different content types
* **Repository Structure Change**: Requires migration from ``products/`` to ``data/`` + minimal ``template/``
* **Generated Content Management**: Downstream projects manage generated vs. custom content boundaries
