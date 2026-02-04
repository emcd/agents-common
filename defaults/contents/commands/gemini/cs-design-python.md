# Python Design Analysis

Analyze Python API design patterns, filesystem organization, module structure, class hierarchies, interface definitions, and design patterns to provide guidance on Python-specific structural decisions and project organization. Focus exclusively on interface contracts, signatures, and type specifications—never implementation details or method bodies.

This creates design documentation that complements existing specifications. For creating new capability specifications or modifying existing ones, use the Openspec workflow (`/openspec:proposal`).

Request from user: {{args}}

## Context

- Architecture overview: @{documentation/architecture/summary.rst}
- Filesystem patterns: @{documentation/architecture/filesystem.rst}
- Existing design docs: @{documentation/architecture/openspec/specs/}

## Prerequisites

Before providing design analysis, ensure:
- Understanding of module organization and class hierarchies.
- Familiarity with Python practices and style guidelines.
- Knowledge of nomenclature conventions and naming patterns.

### Project Standards

Before providing design analysis, you MUST:
1. Read @{.auxiliary/instructions/practices.rst} for general development principles.
2. Read @{.auxiliary/instructions/practices-python.rst} for Python-specific patterns.
3. Read @{.auxiliary/instructions/style.rst} for code style requirements.
4. Read @{.auxiliary/instructions/nomenclature.rst} for naming conventions.
5. In a step on your TODO list, please attest that you have read the practices, style, and nomenclature guides and demonstrate your knowledge by writing one-sentence summaries on any three of the following topics:

- interface specification patterns from comprehensive examples
- module organization principles and content ordering
- import organization for design specifications
- wide parameter, narrow return interface patterns
- immutable container design patterns
- exception hierarchy design patterns
- documentation specification requirements
- nomenclature patterns from nomenclature guides

## Output Structure

Create technical design specification at `documentation/architecture/openspec/specs/[capability-name]/design.md`:

- Interface contracts and signatures.
- Module organization.
- Class hierarchies.
- Exception patterns.
- Design rationale.

If `spec.md` exists for this capability, consult it to understand requirements and context. See existing `design.md` files for format examples.

## Process Summary

Key functional areas:
1. **Design Analysis**: Examine current Python structure and design patterns.
2. **Interface Specification**: Define clean API boundaries and contracts.
3. **Module Organization**: Apply filesystem and import patterns effectively.
4. **Class Design**: Create maintainable hierarchies and interface patterns.
5. **Documentation**: Specify design decisions with examples and rationale.

## Safety Requirements

Stop and consult the user if:
- Architectural decisions are needed instead of design specifications.
- Implementation details are requested instead of design specifications.
- Requirements analysis is needed (use `/openspec:proposal` for requirements).
- User requests actual code implementations instead of specifications.
- Design decisions require architectural changes beyond Python structure.
- Interface changes would break existing API contracts significantly.
- Design conflicts with established filesystem organization patterns.
- Requirements are unclear or insufficient for proper design specification.
- Multiple design approaches have significant trade-offs requiring user input.

## Execution

Execute the following steps:

### 1. Design Analysis
Examine Python structure and patterns:
- Review module organization and import patterns.
- Analyze class hierarchies and interface definitions.
- Identify design patterns in use.
- Assess alignment with practices and nomenclature guidelines.
- Document design strengths and improvement opportunities.

### 2. Interface Specification

**CRITICAL: Define interfaces through signatures and type annotations only. Avoid specifying how methods should be implemented internally—focus on contracts, not implementation logic.**

**Define clean API boundaries and contracts**:
- Focus exclusively on signatures and type annotations (never implementation logic or method bodies).
- Apply wide parameter, narrow return patterns for robust interfaces.
- Design exception class hierarchies following established patterns.
- Apply appropriate naming conventions from nomenclature guidelines.
- Define annotations using proper `__.typx.TypeAlias` patterns when appropriate.
- Consider immutability preferences in container design.
- Consult comprehensive guides for detailed patterns when needed.

### 3. Filesystem and Module Organization Design

**Apply Python-specific organizational patterns and filesystem structure**:
- Consult `documentation/architecture/filesystem.rst` for established patterns.
- Design module structure following standard organization order.
- Plan centralized import integration for organized dependencies.
- Specify exception hierarchies and their organization.
- Design interface patterns for different component types.
- Plan type alias organization and dependency management.
- Update `documentation/architecture/filesystem.rst` if new patterns are established.
- Consult comprehensive guides for detailed organizational patterns.

### 4. Class and Function Design

**CRITICAL: Design class structures through their public contracts and type relationships. Specify signatures, inheritance patterns, and interface boundaries—never internal implementation logic or method bodies.**

**Create maintainable Python structures**:
- Design class hierarchies with appropriate immutable base classes and mixins (`__.immut.Object`, `__.immut.Protocol`, etc.).
- Specify function signatures using wide input, narrow output patterns with proper spacing.
- Apply nomenclature guidelines for methods, attributes, and functions.
- Design immutable data structures and container patterns.
- Plan dependency injection and configuration patterns with sensible defaults.
- Focus exclusively on interface specifications, not implementation details.
- Consult comprehensive guides for detailed design patterns.

### 5. Design Documentation

**Create comprehensive design specifications without implementations**:

**CRITICAL:**
- Use atemporal language in all specifications. Avoid temporal terms like 'new', 'current', 'existing', 'future'—designs should read as canonical specifications independent of implementation timeline.
- Provide only signatures, contracts, and interface specifications - no implementations.

**Create `documentation/architecture/openspec/specs/[capability-name]/design.md`**:
- Document interface contracts and expected behaviors (contracts only, not code).
- Provide design examples using signatures and type annotations only.
- Specify exception handling patterns and error propagation (exception classes by name/signature only).
- Document module organization and filesystem structure.
- Document design rationale and trade-off decisions.
- Do not provide exception class implementations, function bodies, or method implementations.
- Consult comprehensive guides for documentation formatting requirements.

### 6. Design Validation

**Ensure design quality and consistency**:
- Verify alignment with practices, style, and nomenclature guidelines.
- Check consistency with filesystem organization patterns in `filesystem.rst`.
- Validate that wide parameter/narrow return patterns are followed.
- Ensure proper separation between public and private interfaces.
- Confirm that design supports expected usage patterns and extensibility.
- Verify that specifications focus on contracts, not implementations.
- Consult comprehensive guides to verify pattern alignment.

### 7. Summarize Updates
Provide concise summary of updates to the user, including:
- Capability name and location.
- Key design decisions.
- Any updates to `filesystem.rst` or other architectural documentation.
