from __future__ import annotations

import argparse
import json
from pathlib import Path

DEFAULT_API = "https://continuity-works-mrcalzon02-api.onrender.com"
DEFAULT_FRONTEND = "https://mrcalzon02.github.io/Continuity-Works/"


def document(api: str, frontend: str, commit: str, deployment: str) -> dict:
    base = api.rstrip("/")
    front = frontend.rstrip("/") + "/"
    return {
        "schema_version": "1.2",
        "name": "Continuity Works",
        "slug": "continuity-works",
        "description": "Zero-JavaScript discovery for the executable Continuity Works API. GitHub Pages is the static frontend only.",
        "frontend": front,
        "api": base,
        "health": f"{base}/v1/health",
        "tools": f"{base}/v1/tools",
        "openapi": f"{base}/openapi.json",
        "discovery": f"{base}/.well-known/continuity-works.json",
        "serviceability": f"{base}/v1/serviceability",
        "frontend_commit": commit,
        "api_verification_at_build": deployment,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--api", default=DEFAULT_API)
    parser.add_argument("--frontend", default=DEFAULT_FRONTEND)
    parser.add_argument("--commit", default="source")
    parser.add_argument("--deployment", default="candidate")
    args = parser.parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(document(args.api, args.frontend, args.commit, args.deployment), indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
