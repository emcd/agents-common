*******************************************************************************
003. Tag-Based Release Workflow
*******************************************************************************

Status
===============================================================================

Accepted  

Context
===============================================================================

The agents-common repository needs a release and distribution mechanism that 
enables rapid iteration on AI agent configurations while maintaining version 
control and stability for downstream consumers.

Current problems with heavyweight release processes include:

* Full project template releases required for minor agent configuration changes
* Complex coordination between multiple repositories for configuration updates  
* Difficulty pinning to stable configuration versions
* Slow deployment of critical agent configuration fixes

Key requirements include:

* Rapid deployment of configuration updates (hours not weeks)
* Atomic, consistent distribution of related configuration changes
* Ability for downstream projects to pin to known-good configurations
* Rollback capability when configuration changes cause issues
* Integration with existing git-based workflows and CI/CD systems

Several distribution approaches were considered:

**Branch-Based Distribution**: Use git branches for different configuration versions.

**Heavyweight Releases**: Continue using full semantic versioning with release 
artifacts.

**Tag-Based Lightweight Releases**: Use git tags with automated publishing workflow.

**Continuous Distribution**: Automatically distribute from main branch without 
versioning.

Decision
===============================================================================

Implement tag-based lightweight release workflow using ``agents-N`` versioning 
scheme (agents-1, agents-2, etc.) with automated GitHub Actions publishing.

The workflow includes:

**Versioning Scheme**:
- Sequential numbering: ``agents-1``, ``agents-2``, ``agents-3``, etc.
- Tags represent atomic collections of configuration changes
- Simple incrementing scheme avoids semantic versioning complexity for configuration content

**Publishing Process**:
- GitHub Actions workflow triggers on tag creation
- Automated publishing of tagged configuration content 
- Distribution completes within 5 minutes of tag creation
- No manual release artifact preparation required

**Consumption Model**:
- ``agentsmgr`` CLI can pull from specific tagged versions 
- Project templates reference tagged releases for stable generation
- Downstream projects can pin to known-good configuration versions
- Default behavior uses latest stable tag

**Rollback Strategy**:
- Previous configuration versions remain accessible through git tags
- CLI tooling supports switching between tagged versions
- Git-native rollback through tag references

Alternatives
===============================================================================

**Branch-Based Distribution** was rejected because:
- Branches are mutable and don't provide version stability
- Difficult to maintain multiple stable configuration versions simultaneously
- Complex branching strategy required for parallel maintenance
- No clear atomic release boundaries

**Heavyweight Releases** was rejected because:
- Creates unnecessary friction for rapid configuration iteration
- Semantic versioning inappropriate for configuration content evolution
- Release artifact preparation overhead slows deployment
- Complex release process discourages frequent improvements

**Continuous Distribution** was rejected because:
- No version pinning capability for downstream stability
- Atomic change boundaries unclear for related configuration updates
- Difficult rollback when configuration changes cause issues
- No stable reference points for project template generation

Consequences
===============================================================================

**Positive Consequences:**

* **Rapid Deployment**: Configuration updates deploy within hours of tag creation
* **Atomic Distribution**: Related configuration changes distributed as single unit
* **Version Stability**: Downstream projects can pin to tested configuration versions
* **Simple Workflow**: Lightweight tagging process encourages frequent updates
* **Git Integration**: Leverages familiar git workflow patterns and tooling
* **Rollback Capability**: Previous versions remain accessible for easy rollback
* **CI/CD Compatibility**: Works with existing GitHub Actions and CI/CD systems

**Negative Consequences:**

* **Tag Proliferation**: Repository accumulates many tags over time 
* **Sequential Numbering**: Non-semantic versioning provides less information about change scope
* **Automation Dependency**: Requires GitHub Actions for full workflow automation

**Neutral Consequences:**

* **Version Coordination**: CLI tooling must coordinate with tag versions but 
  this aligns with version management requirements
* **Publishing Latency**: 5-minute publishing window may delay urgent fixes but 
  represents significant improvement over current process