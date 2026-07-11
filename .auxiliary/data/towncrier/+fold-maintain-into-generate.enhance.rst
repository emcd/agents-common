Eliminate the separate ``agentsmgr-maintain`` console script by
folding its remaining contract into ``agentsmgr generate``:

  ``agentsmgr generate`` (default mode)
      Renders distribution to ``distribution/`` (or ``--output PATH``).
      Supports ``--simulate`` and ``--check``.

  ``agentsmgr generate --answers-file PATH --output PATH`` (answers-file)
      Uses the given Copier answers file as the configuration source and
      writes to the explicit ``--output`` target. Caller owns output
      allocation and cleanup; production CLI does not manage a temp
      directory.

``--answers-file`` requires ``--output``. ``--check`` and ``--simulate``
are valid only in default mode (not with ``--answers-file``).
