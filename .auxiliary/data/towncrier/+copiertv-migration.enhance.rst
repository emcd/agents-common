Migrate Copier template rendering validation to copiertv, configured
via ``.auxiliary/configuration/copiertv/general.toml``. The
``agentsmgr-maintain template`` subcommand is removed; ``agentsmgr-maintain``
now provides a single flat ``validate`` command (``agentsmgr-maintain
<variant>``) which renders the distribution tree from ``components/`` using
a variant answers file from ``tests/data/profiles/`` into an isolated
temp directory.