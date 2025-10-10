# Minimal type stubs for dulwich.porcelain

from typing import Any

def clone(
    source: str,
    target: str,
    bare: bool = False,
    depth: int | None = None,
    **kwargs: Any
) -> Any: ...