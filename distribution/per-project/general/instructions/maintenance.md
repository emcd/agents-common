<a id="maintenance"></a>
# Maintenance

<!-- TODO: Add GitHub workflow guidance for updating dependency locks. -->

<a id="copier"></a>
## Copier

If the project infrastructure is built upon one or more Copier templates, updates from a template can be incorporated into the project, ensuring adherence to evolving practices and technologies. Follow that template's own guide to applying updates:

- [Applying template updates (Python projects)](https://github.com/emcd/python-project-common/blob/master/documentation/applying-template-updates.md)
- [Applying template updates (Rust projects)](https://github.com/emcd/rust-project-common/blob/master/documentation/applying-template-updates.md)
- [Applying template updates (agent configurations)](https://github.com/emcd/agents-common/blob/master/documentation/applying-template-updates.md)

<a id="updates"></a>
### Updates

Projects may consume one or more templates. To select the right guide, check the `_src_path` recorded in each answers file under `.auxiliary/configuration/` together with the project's own maintenance guidance: `.auxiliary/configuration/copier-answers.yaml`, if present, references the Python or Rust template, and `.auxiliary/configuration/copier-answers--agents.yaml`, if present, references the Agents template. If no file carries provenance matching the intended template, check the project maintenance guidance instead of guessing or running an update — and do not run updates for every template merely because their files are present.
