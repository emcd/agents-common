# Contribution

Contribution to the project is welcome! However, it must follow the
[code of conduct](conduct.md) for the project.

## Ways to Contribute

- File bug reports and feature requests in the issue tracker. (Please try
  to avoid duplicate issues.)
- Fork the repository and submit pull requests to improve the source code
  or documentation. Pull requests should follow the development guidance
  and standards below.

Language-specific templates add their own project links (issue tracker,
repository, installation) on top of this skeleton.

## Development

### Requirements and Design

- Review accepted capability requirements in `openspec/specs/`. Manage new
  capabilities, breaking or cross-cutting changes, architectural shifts, and
  substantial performance or security work through OpenSpec changes in
  `openspec/changes/`. Follow the project's OpenSpec workflow instructions
  and keep accepted specifications synchronized when changes are completed.
- Document stable subsystem architecture, design rationale, and local
  constraints in the nearest source-near README. Update the affected README
  when implementation structure or operational patterns change rather than
  recreating centralized architecture or specification mirrors under
  `documentation/`.

### Guidance and Standards

- Follow the [development environment](environment.md) preparation and
  management instructions to ensure consistency with maintainer development
  environments and CI workflows.
- Configure Git commit signing as required for all contributions. See the
  [environment setup guide](environment.md#git-commit-signatures) for
  configuration details.
- Adhere to the [development practices](practices.md),
  [code style](style.md), and [testing guidelines](tests.md) to improve the
  probability of pull request acceptance.
- Also consider the [nomenclature advice](nomenclature.md) for consistency
  and to improve the probability of pull request acceptance.
- Run validation commands before submitting contributions. See the
  [validation guide](validation.md) for available commands and workflow.
- Prepare changelog fragments according to the [releases guide](releases.md)
  as appropriate.
- Although unnecessary for non-maintainer contributions, additional
  background can be found in the [maintenance guide](maintenance.md).

### Language Overlays

Language-specific guidance lives alongside the common guides. Consult the
overlay for the language you are contributing in, in addition to the
guides above:

- [Python environment](environment-python.md) ·
  [Python practices](practices-python.md) ·
  [Python testing](tests-python.md) ·
  [Python validation](validation-python.md) ·
  [Python releases](releases-python.md) ·
  [Python architecture](architecture-python.md) ·
  [Python automatic formatting](python-autoformat.md)
- [Rust practices](practices-rust.md)
- [TOML practices](practices-toml.md)
- [Latin-derived verb vocabulary](nomenclature-latin.md) ·
  [Germanic vocabulary](nomenclature-germanic.md)

### Artificial Intelligence

- Contributions co-authored by large language models (LLMs) are welcome,
  provided that they adhere to the project guidance and standards above
  and are, otherwise, of good quality.
