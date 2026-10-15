<a id="maintenance"></a>
# Maintenance

<!-- TODO: Add GitHub workflow guidance for updating dependency locks. -->

<a id="copier"></a>
## Copier

The project was created from a [Copier template](https://github.com/emcd/python-project-common/tree/master/template). In addition to seeding the initial project structure and code, updates from the template can be incorporated into the project, ensuring adherence to evolving practices and technologies.

<a id="updates"></a>
### Updates

1.  Ensure the working directory is clean (commit or stash changes).

2. Run the update command:

   ```shell
   copier update --answers-file .auxiliary/configuration/copier-answers.yaml
   ```

> **Note:** The update process preserves your answers from the previous
> template generation. You can override specific answers using the
> `--data` option with the update command.
