from __future__ import annotations

import os

from structure_capability.server import serve


serve(
    project_root=os.environ.get("STRUCTURESMITH_PROJECT_ROOT", "."),
    host=os.environ.get("HOST", "0.0.0.0"),
    port=int(os.environ.get("PORT", "8787")),
)
