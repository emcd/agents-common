# CLI Improvements for Populate Command

## Overview

This document outlines planned improvements to the `agentsmgr populate` command interface to enhance usability and flexibility.

## Proposed Changes

### 2. Add `profile` Argument for Alternative Configuration Files

**Purpose:**
Enable users to specify an alternative Copier answers file instead of always using the auto-detected `.auxiliary/configuration/copier-answers--agents.yaml`.

**Use Cases:**
- Testing with different configurations without modifying main answers file
- Supporting multiple configuration profiles per project
- Development and testing workflows

**Proposed Behavior:**
```bash
agentsmgr populate --profile=/path/to/alt-answers.yaml
agentsmgr populate --profile=../other-config.yaml --simulate
```

**Design Decisions:**
- Accept full file path for maximum flexibility
- Optional argument (defaults to auto-detected answers file)
- Path resolution: relative paths resolved from current working directory
- Independent from `target` argument (specifies *what* to generate, not *where*)

**Error Handling:**
- Non-existent profile file should raise appropriate configuration error
- Invalid YAML in profile file should raise configuration validation error
