from __future__ import annotations

import os

from structure_capability.server import serve


def _port_from_environment() -> int:
    raw_port = os.environ.get("CONTINUITY_WORKS_PORT", os.environ.get("PORT", "8787"))
    try:
        port = int(raw_port)
    except (TypeError, ValueError) as exc:
        raise ValueError("API port must be an integer from 1 through 65535") from exc
    if not 1 <= port <= 65535:
        raise ValueError("API port must be an integer from 1 through 65535")
    return port


serve(
    project_root=os.environ.get(
        "CONTINUITY_WORKS_PROJECT_ROOT",
        os.environ.get("STRUCTURESMITH_PROJECT_ROOT", "."),
    ),
    host=os.environ.get("CONTINUITY_WORKS_HOST", os.environ.get("HOST", "0.0.0.0")),
    port=_port_from_environment(),
)
