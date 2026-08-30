from __future__ import annotations

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

PUBLIC_GATE = "PUBLIC_SERVICEABILITY"
DEFAULT_API = "https://continuity-works-mrcalzon02-api.onrender.com"
DEFAULT_FRONTEND = "https://mrcalzon02.github.io/Continuity-Works/"
DEFAULT_ORIGIN = "https://mrcalzon02.github.io"
DISCOVERY_PATH = "/.well-known/continuity-works.json"
VENDOR_EXTENSION = "x-continuity-works"
TOOL_EXTENSION = "x-continuity-works-tool"


class ServiceabilityFailure(RuntimeError):
    def __init__(self, code: str, message: str, evidence=None):
        super().__init__(message)
        self.code = code
        self.evidence = evidence


class DiscoveryParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta: dict[str, str] = {}
        self.links: list[dict[str, str]] = []

    def handle_starttag(self, tag, attrs):
        values = {k: v for k, v in attrs if v is not None}
        if tag == "meta" and values.get("name"):
            self.meta[values["name"]] = values.get("content", "")
        if tag == "link":
            self.links.append(values)

    def link(self, rel: str):
        for item in self.links:
            if rel in set((item.get("rel") or "").split()):
                return item.get("href")
        return None


def _is_absolute_http(value: str) -> bool:
    parsed = urlparse(str(value or ""))
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _request_json(url: str, method: str = "GET", body=None, headers=None, timeout=45):
    data = None if body is None else json.dumps(body).encode("utf-8")
    request_headers = {"Accept": "application/json", **(headers or {})}
    if data is not None:
        request_headers["Content-Type"] = "application/json"
    req = Request(url, data=data, headers=request_headers, method=method)
    try:
        with urlopen(req, timeout=timeout) as response:
            raw = response.read()
            return response.status, dict(response.headers.items()), json.loads(raw or b"{}")
    except HTTPError as exc:
        raise ServiceabilityFailure("API_HOST_UNREACHABLE", f"{method} {url} returned HTTP {exc.code}: {exc.read().decode('utf-8','replace')[:500]}") from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise ServiceabilityFailure("API_HOST_UNREACHABLE", f"Could not reach {url}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ServiceabilityFailure("DISCOVERY_MISSING", f"{url} did not return valid JSON") from exc


def _request_text(url: str, timeout=45) -> str:
    try:
        with urlopen(Request(url, headers={"Accept": "text/html,application/xhtml+xml"}, method="GET"), timeout=timeout) as response:
            if response.status != 200:
                raise ServiceabilityFailure("FRONTEND_STALE", f"Frontend returned HTTP {response.status}")
            return response.read().decode("utf-8", "replace")
    except ServiceabilityFailure:
        raise
    except Exception as exc:
        raise ServiceabilityFailure("FRONTEND_STALE", f"Could not fetch frontend {url}: {exc}") from exc


def verify_api(api_base: str, expected_commit: str | None = None, origin: str = DEFAULT_ORIGIN) -> dict:
    api = api_base.rstrip("/")
    _, cors_headers, health = _request_json(f"{api}/v1/health", headers={"Origin": origin})
    if not health.get("ok") or health.get("service") != "Continuity Works":
        raise ServiceabilityFailure("API_HOST_UNREACHABLE", "Health endpoint did not identify a healthy Continuity Works service", health)
    if expected_commit and health.get("commit") != expected_commit:
        raise ServiceabilityFailure("DEPLOYMENT_COMMIT_MISMATCH", f"API commit {health.get('commit')!r} does not match expected {expected_commit!r}", health)
    cors_value = cors_headers.get("Access-Control-Allow-Origin") or cors_headers.get("access-control-allow-origin")
    if cors_value not in {origin, "*"}:
        raise ServiceabilityFailure("CORS_REJECTED", f"API did not accept browser origin {origin!r}", {"header": cors_value})

    _, _, catalog = _request_json(f"{api}/v1/tools")
    tools = catalog.get("tools") or []
    if not tools:
        raise ServiceabilityFailure("DISCOVERY_MISSING", "Tool catalog is empty or missing")
    tool_map = {tool.get("name"): tool for tool in tools}
    if any("x-structuresmith" in tool for tool in tools):
        raise ServiceabilityFailure("OPENAPI_MISMATCH", "Public tool catalog still exposes retired StructureSmith vendor extensions")

    _, _, spec = _request_json(f"{api}/openapi.json")
    if spec.get("openapi") != "3.1.0":
        raise ServiceabilityFailure("OPENAPI_MISMATCH", "OpenAPI document is missing version 3.1.0")
    if VENDOR_EXTENSION not in spec or "x-structuresmith" in spec:
        raise ServiceabilityFailure("OPENAPI_MISMATCH", "OpenAPI does not use the Continuity Works vendor extension")
    servers = spec.get("servers") or []
    if not servers or servers[0].get("url", "").rstrip("/") != api:
        raise ServiceabilityFailure("OPENAPI_MISMATCH", "OpenAPI does not identify the canonical executable API host", servers)

    _, _, discovery = _request_json(f"{api}{DISCOVERY_PATH}")
    if discovery.get("name") != "Continuity Works" or discovery.get("api", "").rstrip("/") != api:
        raise ServiceabilityFailure("DISCOVERY_MISSING", "Discovery document does not expose the canonical Continuity Works identity and API base", discovery)
    for key in ("health", "tools", "openapi", "discovery"):
        if not _is_absolute_http((discovery.get("endpoints") or {}).get(key)):
            raise ServiceabilityFailure("DISCOVERY_MISSING", f"Discovery endpoint {key!r} is missing or relative", discovery)

    _, _, gate = _request_json(f"{api}/v1/serviceability")
    if gate.get("gate") != PUBLIC_GATE or gate.get("status") == "FAIL":
        raise ServiceabilityFailure("TOOL_ROUTE_MISSING", "Server-side PUBLIC_SERVICEABILITY gate failed", gate)

    for name, tool in tool_map.items():
        publication = (tool.get(VENDOR_EXTENSION) or {}).get("publication") or {}
        endpoint = publication.get("canonical_endpoint")
        method = str(publication.get("http_method") or "").lower()
        if not _is_absolute_http(endpoint) or not endpoint.startswith(api + "/"):
            raise ServiceabilityFailure("TOOL_ROUTE_MISSING", f"{name} has no canonical external endpoint", publication)
        path = urlparse(endpoint).path
        operation = (spec.get("paths") or {}).get(path, {}).get(method)
        if not operation or operation.get(TOOL_EXTENSION) != name:
            raise ServiceabilityFailure("OPENAPI_MISMATCH", f"{name} route and OpenAPI operation disagree", {"endpoint": endpoint, "method": method})
        if publication.get("publication_state") == "internal_unpublished":
            raise ServiceabilityFailure("TOOL_ROUTE_MISSING", f"{name} is classified internal/unpublished", publication)

    representative = tool_map.get("minecraft_version")
    if representative is None:
        raise ServiceabilityFailure("TOOL_ROUTE_MISSING", "Representative minecraft_version capability is absent")
    endpoint = representative[VENDOR_EXTENSION]["publication"]["canonical_endpoint"]
    _, _, generated = _request_json(endpoint, method="POST", body={"version": "1.20.1"})
    if not isinstance(generated, dict) or not generated:
        raise ServiceabilityFailure("TOOL_ROUTE_MISSING", "Representative capability did not return a genuine JSON result", generated)
    return {"gate": PUBLIC_GATE, "status": "VERIFIED", "service": "Continuity Works", "api": api, "commit": health.get("commit"), "deployment": health.get("deployment"), "tool_schema_version": health.get("tool_schema_version"), "tool_count": len(tools), "representative_capability": "minecraft_version", "findings": [{"code": "REMOTE_API_VERIFIED", "tool_count": len(tools)}]}


def _parse_frontend(html: str, pages_url: str):
    parser = DiscoveryParser()
    parser.feed(html)
    api = parser.meta.get("continuity-works-api")
    static_href = parser.link("continuity-works-static-discovery") or parser.link("alternate")
    discovery_href = parser.link("continuity-works-discovery")
    openapi_href = parser.link("service-desc")
    tools_href = parser.link("continuity-works-tools")
    if not api or not _is_absolute_http(api):
        raise ServiceabilityFailure("DISCOVERY_MISSING", "Raw frontend HTML does not declare meta[name=continuity-works-api]")
    if not static_href:
        raise ServiceabilityFailure("DISCOVERY_MISSING", "Raw frontend HTML does not link a static api.json discovery document")
    if not discovery_href or not _is_absolute_http(discovery_href):
        raise ServiceabilityFailure("DISCOVERY_MISSING", "Raw frontend HTML does not expose an absolute API discovery URL")
    if not openapi_href or not _is_absolute_http(openapi_href):
        raise ServiceabilityFailure("DISCOVERY_MISSING", "Raw frontend HTML does not expose an absolute OpenAPI URL")
    if not tools_href or not _is_absolute_http(tools_href):
        raise ServiceabilityFailure("DISCOVERY_MISSING", "Raw frontend HTML does not expose an absolute tool-catalog URL")
    return parser, api.rstrip("/"), urljoin(pages_url, static_href), discovery_href, openapi_href, tools_href


def verify_pages(pages_url: str, expected_commit: str | None = None, expected_api: str | None = None, origin: str = DEFAULT_ORIGIN) -> dict:
    pages = pages_url.rstrip("/") + "/"
    html = _request_text(pages)
    _, api, static_url, discovery_url, openapi_url, tools_url = _parse_frontend(html, pages)
    if expected_api and api != expected_api.rstrip("/"):
        raise ServiceabilityFailure("FRONTEND_STALE", f"Frontend advertises {api!r}, expected {expected_api.rstrip('/')!r}")
    for absolute in (api, discovery_url, openapi_url, tools_url):
        if absolute not in html:
            raise ServiceabilityFailure("DISCOVERY_MISSING", f"Raw frontend source does not visibly contain {absolute}")
    _, _, static = _request_json(static_url)
    if static.get("name") != "Continuity Works" or static.get("api", "").rstrip("/") != api:
        raise ServiceabilityFailure("FRONTEND_STALE", "Static api.json disagrees with the Continuity Works raw HTML API metadata", static)
    if expected_commit and static.get("frontend_commit") != expected_commit:
        raise ServiceabilityFailure("FRONTEND_STALE", f"Pages build commit {static.get('frontend_commit')!r} does not match expected {expected_commit!r}", static)
    for key in ("api", "frontend", "health", "tools", "openapi", "discovery"):
        if not _is_absolute_http(static.get(key)):
            raise ServiceabilityFailure("DISCOVERY_MISSING", f"Static discovery field {key!r} is missing or relative", static)
    _, _, discovery = _request_json(discovery_url)
    capabilities = {item.get("name"): item for item in discovery.get("capabilities", [])}
    capability = capabilities.get("minecraft_version")
    if capability is None:
        raise ServiceabilityFailure("TOOL_ROUTE_MISSING", "Pages-discovered API does not advertise minecraft_version")
    endpoint = capability.get("canonical_endpoint")
    if not _is_absolute_http(endpoint):
        raise ServiceabilityFailure("TOOL_ROUTE_MISSING", "Discovered capability endpoint is not absolute", capability)
    _, _, result = _request_json(endpoint, method="POST", body={"version": "1.20.1"})
    if not result:
        raise ServiceabilityFailure("TOOL_ROUTE_MISSING", "Pages-discovered capability invocation returned no result")
    api_result = verify_api(api, expected_commit=expected_commit, origin=origin)
    return {"gate": PUBLIC_GATE, "status": "VERIFIED", "service": "Continuity Works", "frontend": pages, "api": api, "commit": expected_commit or api_result.get("commit"), "discovery_chain": [pages, static_url, discovery_url, endpoint], "representative_capability": "minecraft_version", "tool_count": api_result.get("tool_count")}


def verify_static(directory: str, expected_api: str = DEFAULT_API, expected_frontend: str = DEFAULT_FRONTEND) -> dict:
    root = Path(directory)
    index = root / "index.html"
    api_json = root / "api.json"
    if not index.exists() or not api_json.exists():
        raise ServiceabilityFailure("DISCOVERY_MISSING", f"Static build must contain index.html and api.json under {root}")
    html = index.read_text(encoding="utf-8")
    _, api, _, discovery_url, openapi_url, tools_url = _parse_frontend(html, expected_frontend)
    if api != expected_api.rstrip("/"):
        raise ServiceabilityFailure("FRONTEND_STALE", f"Static build advertises {api!r}, expected {expected_api.rstrip('/')!r}")
    static = json.loads(api_json.read_text(encoding="utf-8"))
    if static.get("name") != "Continuity Works" or static.get("api", "").rstrip("/") != api:
        raise ServiceabilityFailure("FRONTEND_STALE", "Static api.json disagrees with index.html")
    if static.get("frontend") != expected_frontend:
        raise ServiceabilityFailure("FRONTEND_STALE", "Static api.json has the wrong frontend URL")
    if discovery_url != static.get("discovery") or openapi_url != static.get("openapi") or tools_url != static.get("tools"):
        raise ServiceabilityFailure("FRONTEND_STALE", "HTML links and api.json canonical endpoints disagree")
    return {"gate": PUBLIC_GATE, "status": "STATIC_READY", "service": "Continuity Works", "directory": str(root), "api": api}


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Continuity Works PUBLIC_SERVICEABILITY.")
    parser.add_argument("--api")
    parser.add_argument("--pages")
    parser.add_argument("--static-dir")
    parser.add_argument("--expected-api")
    parser.add_argument("--expected-commit")
    parser.add_argument("--origin", default=DEFAULT_ORIGIN)
    args = parser.parse_args()
    try:
        if args.static_dir:
            result = verify_static(args.static_dir, expected_api=args.expected_api or DEFAULT_API)
        elif args.pages:
            result = verify_pages(args.pages, expected_commit=args.expected_commit, expected_api=args.api or args.expected_api, origin=args.origin)
        elif args.api:
            result = verify_api(args.api, expected_commit=args.expected_commit, origin=args.origin)
        else:
            parser.error("one of --api, --pages, or --static-dir is required")
            return 2
    except ServiceabilityFailure as exc:
        print(json.dumps({"gate": PUBLIC_GATE, "status": "FAIL", "code": exc.code, "message": str(exc), "evidence": exc.evidence}, indent=2), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
