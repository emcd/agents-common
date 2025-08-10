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

**Template-Based Generation**: Use Jinja2 templates for base settings with local 
override mechanism.

**Copier Integration**: Handle all settings generation through Copier templates 
in project templates.

Decision
===============================================================================

Implement template-based settings distribution using Jinja2 templates 
(``settings.json.jinja``) for base configurations with local TOML override 
support for project-specific extensions.

The approach includes:

**Base Templates** (``products/[tool]/configuration/settings.json.jinja``):
- Handle tool-specific hook configurations with parameterized script paths
- Use template variables for path resolution (``{{ script_path_prefix }}``)
- Provide extension points for local additions (``{{ env_additions }}``, 
  ``{{ permissions_additions }}``)

**Local Override Mechanism**:
- Projects can provide ``local.toml`` files for additional environment variables, 
  hooks, and permissions
- CLI tooling merges base template with local overrides during rendering
- Supports incremental customization without full template replacement

**CLI Integration**:
- ``agentsmgr`` CLI tool renders final ``settings.json`` from base template + 
  local overrides
- Path resolution occurs at render time based on target environment
- Generated configurations work with existing AI tool expectations

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

**Copier Integration** was rejected because:
- Would duplicate template logic between agents-common and project templates
- Makes it difficult to update base settings independently of project templates
- Does not solve the core coordination problem between hook paths and script distribution
- Couples agent configuration updates to project template releases

Consequences
===============================================================================

**Positive Consequences:**

* **Path Coordination**: Solves script path coordination through parameterized 
  template variables
* **Project Customization**: Local override mechanism enables project-specific 
  extensions without template modification
* **Tool Compatibility**: Generated settings work with existing AI tool expectations
* **Update Velocity**: Base settings can be updated independently of project-specific 
  customizations
* **Familiar Patterns**: Uses established Jinja2 templating familiar to developers
* **Incremental Adoption**: Projects can adopt template-based settings gradually

**Negative Consequences:**

* **CLI Dependency**: Requires CLI tooling for settings generation rather than 
  simple file distribution
* **Template Complexity**: Adds template syntax learning curve for settings 
  customization
* **Rendering Step**: Introduces additional step in project setup workflow

**Neutral Consequences:**

* **Two-File Pattern**: Projects manage both template and local override files 
  rather than single settings file
* **Version Coordination**: Template updates must coordinate with CLI tooling 
  but this aligns with existing version coordination requirements