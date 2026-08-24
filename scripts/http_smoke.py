from __future__ import annotations

import argparse
import json
from urllib.request import Request, urlopen


def request(base_url: str, method: str, path: str, body: dict | None = None) -> dict:
    data = None if body is None else json.dumps(body).encode("utf-8")
    headers = {"Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = Request(f"{base_url.rstrip('/')}{path}", data=data, headers=headers, method=method)
    with urlopen(req, timeout=30) as response:
        payload = json.loads(response.read() or b"{}")
        if response.status != 200:
            raise RuntimeError(f"{method} {path} returned HTTP {response.status}")
        return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke-test a running StructureSmith HTTP API.")
    parser.add_argument("base_url", help="Base URL, for example http://127.0.0.1:8787 or https://host.example")
    args = parser.parse_args()
    base = args.base_url.rstrip("/")

    health = request(base, "GET", "/v1/health")
    if not health.get("ok"):
        raise RuntimeError("/v1/health did not report ok=true")

    catalog = request(base, "GET", "/v1/tools")
    if len(catalog.get("tools", [])) < 12:
        raise RuntimeError("/v1/tools returned an unexpectedly small catalog")

    spec = request(base, "GET", "/openapi.json")
    if spec.get("openapi") != "3.1.0" or "/v1/generate" not in spec.get("paths", {}):
        raise RuntimeError("/openapi.json does not describe the expected API")

    discovery = request(base, "GET", "/.well-known/structuresmith.json")
    if "tools" not in discovery.get("endpoints", {}):
        raise RuntimeError("discovery metadata does not advertise /v1/tools")

    layout = request(
        base,
        "POST",
        "/v1/infrastructure/layout",
        {
            "module_type": "inner_city_road",
            "seed": 20260824,
            "world_seed": 20260824,
            "road": {"width": 6, "terrain_padding": 5},
            "purpose": {"depth": 3},
        },
    )
    if layout.get("engine") != "native_infrastructure_v1":
        raise RuntimeError("real infrastructure capability call returned the wrong engine")

    print(
        json.dumps(
            {
                "ok": True,
                "base_url": base,
                "tool_count": len(catalog["tools"]),
                "openapi": spec["openapi"],
                "capability_call": {
                    "route": "/v1/infrastructure/layout",
                    "engine": layout["engine"],
                    "fitness": layout.get("fitness", {}).get("status"),
                },
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
