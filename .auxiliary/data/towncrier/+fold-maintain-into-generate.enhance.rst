Eliminate the separate ``agentsmgr-maintain`` console script by
folding its remaining contract into ``agentsmgr generate`` via three
modes selected by flag:

  ``agentsmgr generate`` (default mode, unchanged)
      Renders distribution to ``distribution/`` (or ``--output PATH``).
      Supports ``--simulate`` and ``--check``.

  ``agentsmgr generate --variant NAME`` (variant mode)
      Resolves ``tests/data/profiles/answers-NAME.yaml`` and renders
      into an isolated temp directory. Use ``--preserve`` to keep the
      temp directory for inspection. Validates that arbitrary variant
      configurations (e.g., ``maximum`` with rust support) can be
      rendered without errors, which is unique coverage not provided
      by ``--check`` (which tests only the project's own committed
      configuration).

  ``agentsmgr generate --answers-file PATH`` (answers-file mode)
      Uses the given Copier answers file as the configuration source.
      Default target is an isolated temp directory (safe; will not
      pollute the committed distribution tree). Use ``--output PATH``
      to override and render to a specific path. Use ``--preserve`` to
      keep the output directory.

``--variant`` and ``--answers-file`` are mutually exclusive.
``--check`` and ``--simulate`` are valid only in default mode.
``--preserve`` is valid only in variant and answers-file modes.
``--output`` is valid only in default and answers-file modes
(rejected in variant mode, which always uses a temp directory).
