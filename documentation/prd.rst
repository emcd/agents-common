.. vim: set fileencoding=utf-8:
.. -*- coding: utf-8 -*-
.. +--------------------------------------------------------------------------+
   |                                                                          |
   | Licensed under the Apache License, Version 2.0 (the "License");          |
   | you may not use this file except in compliance with the License.         |
   | You may obtain a copy of the License at                                  |
   |                                                                          |
   |     http://www.apache.org/licenses/LICENSE-2.0                           |
   |                                                                          |
   | Unless required by applicable law or agreed to in writing, software      |
   | distributed under the License is distributed on an "AS IS" BASIS,        |
   | WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. |
   | See the License for the specific language governing permissions and      |
   | limitations under the License.                                           |
   |                                                                          |
   +--------------------------------------------------------------------------+


*******************************************************************************
Product Requirements Document
*******************************************************************************

Executive Summary
===============================================================================

The emcd-agents-common repository provides centralized, version-controlled 
configurations for AI agent tools including Claude Code, Gemini CLI, and future 
AI development environments. This repository enables rapid iteration on AI agent 
configurations without heavyweight release processes, while maintaining 
consistency across multiple project templates and ensuring clean separation 
between project structure and evolving agent content.

Problem Statement
===============================================================================

Current AI agent configuration management faces several critical issues:

**Heavyweight Configuration Updates**
Users and maintainers must create full stable releases of project templates 
for minor AI agent configuration changes, creating friction for rapid iteration 
on slash commands, subagent definitions, and hook scripts.

**Configuration Drift and Inconsistency** 
Template and production versions of AI agent configurations drift apart, 
requiring manual synchronization that is error-prone and leads to inconsistent 
behavior across projects.

**Distribution Coordination Problems**
Hook configurations reference script paths that must be coordinated between 
distributed configurations and actual script locations, creating complex 
dependencies between repositories.

**Multi-Tool Scaling Challenges**
As additional AI tools (Gemini CLI, Opencode) require similar configuration 
management, the current approach does not scale cleanly across multiple 
AI development environments.

Goals and Objectives
===============================================================================

**Primary Objectives**

* Enable rapid iteration on AI agent configurations without heavyweight release processes
* Eliminate configuration drift between templates and production environments
* Provide single source of truth for all AI agent tooling across multiple projects
* Support clean extensibility for future AI development tools

**Secondary Objectives**

* Simplify distribution workflow through tag-based releases
* Maintain backward compatibility with existing project structures
* Reduce maintenance overhead for configuration synchronization

**Success Metrics**

* Configuration updates deploy within hours rather than requiring full releases
* Zero manual synchronization steps between template and production configurations
* New AI tools integrate without restructuring existing content
* Projects reference consistent, versioned configurations across all environments

Target Users
===============================================================================

**Primary Users: Project Maintainers**
Developers who maintain multiple projects using AI development tools and need 
consistent, up-to-date agent configurations across all projects without manual 
synchronization overhead.

**Secondary Users: AI Tool Contributors**
Contributors who develop slash commands, subagents, and related tooling 
configurations and need rapid feedback cycles for testing and deployment.

**Technical Requirements**
* Familiarity with git tag-based workflows
* Understanding of template-based configuration management
* Experience with AI development tool configuration (Claude Code settings, etc.)

Functional Requirements
===============================================================================

**REQ-001: Product-Organized Repository Structure** (Priority: Critical)
As a project maintainer, I want AI tool configurations organized by product 
so that I can easily locate and manage tool-specific resources.

Acceptance Criteria:
- Repository uses ``products/`` top-level directory structure
- Each AI tool has dedicated subdirectory (claude/, gemini/, etc.)
- Tool subdirectories contain agents/, commands/, scripts/, configuration/ as appropriate
- Directory naming follows consistent terminology conventions

**REQ-002: Consolidated Resource Management** (Priority: Critical)
As a project maintainer, I want all tool-specific resources consolidated 
so that I have a single source of truth for each AI development environment.

Acceptance Criteria:
- Claude hook scripts consolidated from python-project-common template
- All slash commands centralized in products/claude/commands/
- Subagent definitions centralized in products/claude/agents/
- No duplication of configuration resources across repositories

**REQ-003: Template-Based Settings Distribution** (Priority: High)
As a project maintainer, I want base configuration templates that can be 
customized so that I can maintain consistent hook configurations while 
allowing project-specific extensions.

Acceptance Criteria:
- settings.json.jinja templates provided for each AI tool
- Templates handle hook path references correctly
- Support for local.toml override mechanism
- Generated configurations work with existing AI tool expectations

**REQ-004: Tag-Based Release Distribution** (Priority: High)
As a project maintainer, I want lightweight tag-based releases so that 
I can get configuration updates quickly without waiting for heavyweight 
project releases.

Acceptance Criteria:
- Repository supports agents-N tag versioning scheme
- CLI tooling can pull from specific tagged versions
- Downstream projects can pin to known-good configuration versions
- Publishing workflow automatically deploys tagged releases

**REQ-005: Backward Compatible Path References** (Priority: Critical)
As a project maintainer, I want existing command references preserved 
so that distributed configurations work correctly in downstream projects.

Acceptance Criteria:
- Commands reference .auxiliary/configuration/ paths for downstream compatibility
- Hook scripts function correctly when deployed to target project structure
- No breaking changes to existing project deployment workflows
- Template references remain valid after distribution

**REQ-006: Multi-Tool Extensibility** (Priority: Medium)
As a project maintainer, I want clean extensibility for future AI tools 
so that new tools can be added without restructuring existing content.

Acceptance Criteria:
- New AI tools can be added with products/[tool]/ directory structure
- Existing tool configurations unaffected by new tool additions
- Shared resources (MCP servers, etc.) available across tools
- Consistent patterns for tool-specific vs shared resources

Non-Functional Requirements
===============================================================================

**Performance Requirements**
* Configuration distribution completes within 5 minutes of tag creation
* CLI setup commands execute within 30 seconds for typical project sizes
* Repository size remains manageable (< 100MB) for rapid cloning

**Reliability Requirements**
* Tag-based distribution provides atomic, consistent configuration deployment
* Rollback capability to previous configuration versions through tag references
* Graceful handling of missing or malformed configuration files

**Compatibility Requirements**
* Support existing Claude Code settings.json format and expectations
* Maintain compatibility with Copier template generation workflows
* Work with standard git workflow practices and CI/CD pipelines

**Usability Requirements**
* Clear, intuitive directory structure for locating configurations
* Self-documenting configuration templates with appropriate comments
* Minimal learning curve for maintainers familiar with existing workflows

Constraints and Assumptions
===============================================================================

**Technical Constraints**
* Must work within git-based workflow and standard GitHub Actions
* Configuration templates must be compatible with Jinja2 templating engine
* Hook scripts must execute in standard shell environments

**Dependencies**
* Relies on continued availability of target AI tools (Claude Code, Gemini CLI)
* Depends on stable MCP server interfaces for cross-tool functionality
* Requires coordination with python-project-common template updates

**Assumptions**
* Users have git and standard development tools available
* Projects using these configurations follow consistent .auxiliary/ structure
* AI tool configuration formats remain stable across versions

Out of Scope
===============================================================================

* Complex configuration management beyond template-based approach
* Direct integration with AI tool installation or version management
* Runtime configuration validation or error checking
* Project-specific configuration customization beyond template override mechanism
* Support for AI tools that don't follow standard configuration patterns