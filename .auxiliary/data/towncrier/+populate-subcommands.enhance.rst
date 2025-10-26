CLI: Split populate command into nested project and user subcommands.
The populate command now uses a nested subcommand structure: ``populate project`` for project-scoped operations (content generation, symlinks, git exclude) and ``populate user`` for user-scoped operations (global settings, wrapper installation).
The ``--mode`` flag has been removed, as ``populate project`` always uses per-project mode.
The ``--update-globals`` flag has been replaced by the separate ``populate user`` subcommand.
