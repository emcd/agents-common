Remove ``agentsmgr generate --variant`` and ``--preserve``. Use
``agentsmgr generate --answers-file PATH --output PATH`` for explicit
answers-file rendering; callers now provide the output location and lifecycle.
