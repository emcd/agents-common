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

Transform agents-common into a Copier template that generates AI tool 
configurations from structured data sources, leveraging Copier's proven 
distribution and update mechanisms.

The approach includes:

**Data-Driven Source Structure**:
- ``data/`` directory contains structured sources (TOML command definitions, 
  agent configurations, hook scripts)
- ``agentsmgr populate-template`` transforms data into Copier template format
- Single source of truth maintained in structured, tool-agnostic format

**Generated Copier Template** (``template/.auxiliary/configuration/``):
- Tool-specific configurations generated from common data sources
- Different output formats for different tools (Claude full format, Opencode filtered)
- Jinja2 templates for settings with parameterized script paths
- Standard Copier template structure for distribution

**Multi-Template Distribution**:
- Projects apply agents-common as secondary Copier template after base project template
- Leverages Copier's native multi-template support with separate answers files
- Independent versioning and update cycles for agent configurations
- Standard ``copier update`` workflow for configuration updates

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

**Custom CLI Renderer** was rejected because:
- Requires custom tooling when proven solutions (Copier) already exist
- Creates additional dependency on CLI installation for basic project setup
- Does not leverage existing multi-template capabilities
- Introduces custom conflict resolution when Copier already handles this

Consequences
===============================================================================

**Positive Consequences:**

* **Proven Distribution**: Leverages Copier's mature update and conflict resolution mechanisms
* **Data-Driven Generation**: Tool configurations generated from structured data sources 
  eliminating format-specific maintenance overhead
* **Multi-Tool Scaling**: Single data source generates configurations for multiple 
  AI tools with tool-specific formatting
* **Standard Workflow**: Projects use familiar ``copier update`` commands for 
  configuration updates
* **Independent Versioning**: Agent configurations version independently from 
  project templates through multi-template support
* **Path Coordination**: Template generation resolves script paths for target deployment structure

**Negative Consequences:**

* **Build Step Dependency**: Requires ``agentsmgr populate-template`` step to 
  transform data into template format
* **Template Generation Complexity**: Additional tooling needed to transform 
  data sources into multiple output formats
* **Multi-Template Coordination**: Projects must manage multiple Copier answers 
  files for different template sources

**Neutral Consequences:**

* **Repository Structure Change**: Requires migration from ``products/`` to 
  ``data/`` + ``template/`` organization
* **Copier Dependency**: Projects must use Copier for agent configuration 
  distribution, though most already do for base project generation