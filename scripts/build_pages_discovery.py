from __future__ import annotations

import argparse
import json
from pathlib import Path

DEFAULT_API = "https://continuity-works-mrcalzon02-api.onrender.com"
DEFAULT_FRONTEND = "https://mrcalzon02.github.io/Continuity-Works/"


def _base_urls(api: str, frontend: str) -> tuple[str, str]:
    return api.rstrip("/"), frontend.rstrip("/") + "/"


def document(api: str, frontend: str, commit: str, deployment: str) -> dict:
    base, front = _base_urls(api, frontend)
    return {
        "schema_version": "1.3",
        "name": "Continuity Works",
        "slug": "continuity-works",
        "description": "Zero-JavaScript discovery for the executable Continuity Works API. GitHub Pages is the static frontend only.",
        "frontend": front,
        "api": base,
        "health": f"{base}/v1/health",
        "capabilities": f"{base}/v1/capabilities",
        "tools": f"{base}/v1/tools",
        "openapi": f"{base}/openapi.json",
        "discovery": f"{base}/.well-known/continuity-works.json",
        "serviceability": f"{base}/v1/serviceability",
        "llms": f"{front}llms.txt",
        "agent": f"{front}ai.json",
        "pages_discovery": f"{front}.well-known/continuity-works.json",
        "frontend_commit": commit,
        "api_verification_at_build": deployment,
    }


def agent_document(api: str, frontend: str) -> dict:
    base, front = _base_urls(api, frontend)
    return {
        "schema_version": "1.0",
        "name": "Continuity Works",
        "kind": "agent-discovery",
        "frontend": front,
        "frontend_is_executable": False,
        "canonical_api": base,
        "instructions": f"{front}llms.txt",
        "endpoints": {
            "health": f"{base}/v1/health",
            "capabilities": f"{base}/v1/capabilities",
            "tools": f"{base}/v1/tools",
            "openapi": f"{base}/openapi.json",
            "discovery": f"{base}/.well-known/continuity-works.json",
            "serviceability": f"{base}/v1/serviceability",
        },
        "startup_sequence": [
            {"method": "GET", "url": f"{base}/v1/health"},
            {"method": "GET", "url": f"{base}/v1/capabilities"},
            {"method": "GET", "url": f"{base}/v1/tools"},
            {
                "action": "Select a tool and invoke the exact published HTTP method and canonical endpoint using its schema."
            },
        ],
        "hostname_policy": "Preserve the full canonical_api hostname exactly as published. Never shorten or reconstruct it from the hosting provider domain.",
    }


def pages_discovery_document(api: str, frontend: str) -> dict:
    base, front = _base_urls(api, frontend)
    return {
        "schema_version": "1.0",
        "name": "Continuity Works",
        "kind": "pages-agent-discovery",
        "surface": "static",
        "executable": False,
        "frontend": front,
        "api": base,
        "instructions": f"{front}llms.txt",
        "agent": f"{front}ai.json",
        "static_api": f"{front}api.json",
        "endpoints": {
            "health": f"{base}/v1/health",
            "capabilities": f"{base}/v1/capabilities",
            "tools": f"{base}/v1/tools",
            "openapi": f"{base}/openapi.json",
            "discovery": f"{base}/.well-known/continuity-works.json",
            "serviceability": f"{base}/v1/serviceability",
        },
        "startup_sequence": [
            f"GET {base}/v1/health",
            f"GET {base}/v1/capabilities",
            f"GET {base}/v1/tools",
            "Invoke the exact canonical endpoint and HTTP method published for the selected tool.",
        ],
    }


def llms_text(api: str, frontend: str) -> str:
    base, front = _base_urls(api, frontend)
    return f"""# Continuity Works

## AI and LLM client instructions

Continuity Works provides an executable HTTP API for AI agents, LLMs, automation systems, and human clients.

The GitHub Pages site at {front} is a STATIC FRONTEND. Do not send Continuity Works API actions to the GitHub Pages origin.

Canonical executable API:
{base}

Health:
{base}/v1/health

Capabilities:
{base}/v1/capabilities

AI tool catalog:
{base}/v1/tools

OpenAPI 3.1 specification:
{base}/openapi.json

Canonical API machine discovery:
{base}/.well-known/continuity-works.json

Pages-local machine discovery:
{front}.well-known/continuity-works.json

Agent JSON:
{front}ai.json

Static API pointer:
{front}api.json

## Core invocation sequence

1. GET the health endpoint and confirm the service identifies itself as Continuity Works.
2. GET the capabilities endpoint.
3. GET the AI tool catalog.
4. Select the required tool and read its published HTTP method, canonical endpoint, and schema.
5. Invoke the exact advertised executable API endpoint with the required schema.
6. Use the OpenAPI document when route or schema details are needed.

Always preserve the full canonical API hostname exactly as published. Do not shorten, infer, or reconstruct the hostname from the hosting provider domain.
"""


def write_bundle(output: Path, api: str, frontend: str, commit: str, deployment: str) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(document(api, frontend, commit, deployment), indent=2) + "\n",
        encoding="utf-8",
    )
    root = output.parent
    (root / "ai.json").write_text(
        json.dumps(agent_document(api, frontend), indent=2) + "\n",
        encoding="utf-8",
    )
    (root / "llms.txt").write_text(llms_text(api, frontend), encoding="utf-8")
    well_known = root / ".well-known" / "continuity-works.json"
    well_known.parent.mkdir(parents=True, exist_ok=True)
    well_known.write_text(
        json.dumps(pages_discovery_document(api, frontend), indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--api", default=DEFAULT_API)
    parser.add_argument("--frontend", default=DEFAULT_FRONTEND)
    parser.add_argument("--commit", default="source")
    parser.add_argument("--deployment", default="candidate")
    args = parser.parse_args()
    write_bundle(
        Path(args.output),
        args.api,
        args.frontend,
        args.commit,
        args.deployment,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
