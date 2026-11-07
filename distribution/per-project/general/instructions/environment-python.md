<a id="environment-python"></a>
# Environment (Python)

This guide provides Python-specific environment setup guidance for
projects using the Python template toolchain. For shared baseline setup, see
the [environment guide](environment.md).

<a id="tooling"></a>
## Tooling

1. Ensure that you have installed either [pipx](https://pipx.pypa.io/stable/)
   or [uv](https://github.com/astral-sh/uv/blob/main/README.md) for managing
   Python tools.

   > **Note:** If installing Pipx via `pip`, use your system Python rather
   > than a mutable global version managed by Asdf, Mise, or Pyenv. This
   > reduces the risk that subsequent global version changes break `pipx`.

2. Ensure that you have installed [Copier](https://copier.readthedocs.io/en/stable/)
   and [Hatch](https://github.com/pypa/hatch/blob/master/README.md).

   If using Pipx:

   ```shell
   pipx install copier hatch
   ```

   If using `uv`:

   ```shell
   uv tool install copier
   uv tool install hatch
   ```

<a id="git-hooks"></a>
## Git Hooks

Install Git pre-commit and pre-push hooks with a per-user `pre-commit`
installation outside any Hatch development environment, so hooks keep
working even when Hatch environments are pruned or rebuilt:

```shell
uv tool install pre-commit
```

`pipx install pre-commit` remains functionally compatible, but `uv` is the
single documented path to match the tooling section above.

Then install the hooks in the repository:

```shell
pre-commit install --config .auxiliary/configuration/pre-commit.yaml
```

<a id="refreshing-environments"></a>
## Refreshing Environments

Remove and rebuild Hatch virtual environments after dependency or
interpreter changes:

```shell
hatch env prune
```

<a id="interpreter"></a>
## Interpreter

Run Python inside the development environment:

```shell
hatch --env develop run python
```

<a id="shell"></a>
## Shell

Open a shell inside the development environment:

```shell
hatch --env develop shell
```
