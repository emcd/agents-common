# Cleanup and removal protocol

#procedures #cleanup #status-active

## Purpose

Use this procedure for removal or cleanup work where stale references in code,
tests, live specs, or documentation could recreate removed behavior.

## Protocol

### 1. Inventory First

Before dispatching or implementing cleanup, run a repository-wide search over
all relevant surfaces:

```sh
rg '<pattern>' src/ tests/ documentation/ openspec/specs/
```

Adjust directories for the project. Include source, tests, specs, docs,
configuration, and generated-template sources when relevant.

### 2. Dispatch Complete Site Lists

The work assignment should include:

- Every code and test site to update.
- Every live spec clause that mandates the old behavior.
- Every documentation/configuration/template reference.
- The proof-of-absence command required before closure.

### 3. Treat Live Specs as Code Sites

A live spec that still requires removed behavior is a directive to future
implementers. Remove or modify that spec text in the same changeset as the code
removal unless the project explicitly accepts a staged migration.

### 4. Require Proof of Absence

Completion reports should include the proof command and output:

```sh
rg '<pattern>' src/ tests/ documentation/ openspec/specs/
# no output
```

If the command still has output, the cleanup is not complete.

### 5. Verify Before Merge

Do not merge cleanup work until proof of absence is included or the remaining
references are explicitly justified.

## Scope Exceptions

- Rename-only changes may use old-name proof of absence plus new-name spot checks.
- Bug fixes that restore intended behavior are not cleanup tasks.
- Small mechanical sweeps may compress the inventory step when the pattern is unambiguous and output is short enough to review inline.
