from __future__ import annotations

import argparse
import json
from urllib.request import Request, urlopen


def request(base_url: str, method: str, path: str, body: dict | None = None) -> dict:
    data = None if body is None else json.dumps(body).encode("utf-8"); headers = {"Accept": "application/json"}
    if data is not None: headers["Content-Type"] = "application/json"
    req = Request(f"{base_url.rstrip('/')}{path}", data=data, headers=headers, method=method)
    with urlopen(req, timeout=30) as response:
        payload = json.loads(response.read() or b"{}")
        if response.status != 200: raise RuntimeError(f"{method} {path} returned HTTP {response.status}")
        return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke-test a running Continuity Works HTTP API."); parser.add_argument("base_url"); args = parser.parse_args(); base = args.base_url.rstrip("/")
    health = request(base, "GET", "/v1/health")
    if not health.get("ok") or health.get("service") != "Continuity Works": raise RuntimeError("/v1/health did not report an identified healthy Continuity Works service")
    for field in ("api_version", "tool_schema_version", "commit", "deployment"):
        if field not in health: raise RuntimeError(f"/v1/health is missing build identity field {field!r}")
    catalog = request(base, "GET", "/v1/tools")
    if len(catalog.get("tools", [])) < 12: raise RuntimeError("/v1/tools returned an unexpectedly small catalog")
    for tool in catalog["tools"]:
        if "x-structuresmith" in tool: raise RuntimeError(f"{tool.get('name')} still exposes a retired StructureSmith vendor extension")
        publication = tool.get("x-continuity-works", {}).get("publication", {})
        if publication.get("http_route") != "ready" or not publication.get("canonical_endpoint"): raise RuntimeError(f"{tool.get('name')} lacks Continuity Works public route metadata")
    spec = request(base, "GET", "/openapi.json")
    if spec.get("openapi") != "3.1.0" or "/v1/generate" not in spec.get("paths", {}): raise RuntimeError("/openapi.json does not describe the expected API")
    if "x-continuity-works" not in spec or "x-structuresmith" in spec: raise RuntimeError("/openapi.json does not expose the Continuity Works vendor extension")
    if not spec.get("servers") or spec["servers"][0].get("url", "").rstrip("/") != base: raise RuntimeError("/openapi.json does not identify the running API base")
    discovery = request(base, "GET", "/.well-known/continuity-works.json")
    if discovery.get("name") != "Continuity Works" or discovery.get("api", "").rstrip("/") != base: raise RuntimeError("discovery metadata does not identify the running Continuity Works API base")
    if not str(discovery.get("endpoints", {}).get("tools", "")).startswith(base + "/"): raise RuntimeError("discovery metadata does not advertise an absolute /v1/tools endpoint")
    serviceability = request(base, "GET", "/v1/serviceability")
    if serviceability.get("gate") != "PUBLIC_SERVICEABILITY" or serviceability.get("status") == "FAIL": raise RuntimeError("server-side PUBLIC_SERVICEABILITY gate failed")
    layout = request(base, "POST", "/v1/infrastructure/layout", {"module_type": "inner_city_road", "seed": 20260824, "world_seed": 20260824, "road": {"width": 6, "terrain_padding": 5}, "purpose": {"depth": 3}})
    if layout.get("engine") != "native_infrastructure_v1": raise RuntimeError("real infrastructure capability call returned the wrong engine")
    print(json.dumps({"ok": True, "service": "Continuity Works", "base_url": base, "commit": health.get("commit"), "tool_count": len(catalog["tools"]), "openapi": spec["openapi"], "public_serviceability": serviceability.get("status"), "capability_call": {"route": "/v1/infrastructure/layout", "engine": layout["engine"], "fitness": layout.get("fitness", {}).get("status")}}, indent=2)); return 0


if __name__ == "__main__": raise SystemExit(main())
