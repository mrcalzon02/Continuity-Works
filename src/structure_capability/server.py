from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, unquote, urlsplit
from urllib.request import Request, urlopen

from .api import StructureCapability
from .publication import (
    CANONICAL_API_URL,
    PUBLIC_CAPABILITIES,
    canonical_frontend_url,
    deployment_identity,
    installed_version,
    published_tool_catalog,
    static_serviceability,
)
from .tooling import tool_catalog


DEFAULT_CORS_ORIGINS = "https://mrcalzon02.github.io"
CANONICAL_DISCOVERY_PATH = "/.well-known/continuity-works.json"
LEGACY_DISCOVERY_PATH = "/.well-known/structuresmith.json"
DECISION_BRIDGE_PREFIX = "/v1/blueprints/decision"
DECISION_BRIDGE_ENV = "CONTINUITY_WORKS_DECISION_AUTHORITY_URL"
DECISION_BRIDGE_TIMEOUT_ENV = "CONTINUITY_WORKS_DECISION_AUTHORITY_TIMEOUT_SECONDS"
DECISION_BRIDGE_DEFAULT_TIMEOUT = 10.0
DECISION_BRIDGE_ROUTES = {
    f"{DECISION_BRIDGE_PREFIX}/profile": "GET",
    f"{DECISION_BRIDGE_PREFIX}/begin": "POST",
    f"{DECISION_BRIDGE_PREFIX}/next": "POST",
    f"{DECISION_BRIDGE_PREFIX}/apply": "POST",
    f"{DECISION_BRIDGE_PREFIX}/validate": "POST",
    f"{DECISION_BRIDGE_PREFIX}/finalize": "POST",
}


def _tool_index() -> dict:
    return {tool["name"]: tool for tool in tool_catalog()["tools"]}


def _json_response(description: str = "Successful Continuity Works JSON response") -> dict:
    return {"description": description, "content": {"application/json": {"schema": {"type": "object"}}}}


def _error_response() -> dict:
    return {"description": "Request rejected by the Continuity Works public validation boundary.", "content": {"application/json": {"schema": {"type": "object", "required": ["error"], "properties": {"error": {"type": "string"}, "message": {"type": "string"}}}}}}


def _unavailable_response() -> dict:
    return {"description": "The authoritative Java decision service is not attached to this HTTP process.", "content": {"application/json": {"schema": {"type": "object", "required": ["error", "message"], "properties": {"error": {"type": "string"}, "message": {"type": "string"}}}}}}


def _post_operation(operation_id: str, summary: str, schema: dict | None = None, tool_name: str | None = None) -> dict:
    operation = {"operationId": operation_id, "summary": summary, "responses": {"200": _json_response(), "400": _error_response()}}
    if schema is not None:
        operation["requestBody"] = {"required": True, "content": {"application/json": {"schema": schema}}}
    if tool_name:
        operation["x-continuity-works-tool"] = tool_name
    return operation


def _get_operation(operation_id: str, summary: str, tool_name: str | None = None) -> dict:
    operation = {"operationId": operation_id, "summary": summary, "responses": {"200": _json_response(), "400": _error_response()}}
    if tool_name:
        operation["x-continuity-works-tool"] = tool_name
    return operation


def _decision_authority_url() -> str | None:
    configured = (os.environ.get(DECISION_BRIDGE_ENV) or "").strip()
    if not configured:
        return None
    parsed = urlsplit(configured)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.query or parsed.fragment:
        raise ValueError(f"{DECISION_BRIDGE_ENV} must be an absolute http(s) origin/base URL without query or fragment")
    return configured.rstrip("/")


def _decision_authority_timeout() -> float:
    raw = (os.environ.get(DECISION_BRIDGE_TIMEOUT_ENV) or "").strip()
    if not raw:
        return DECISION_BRIDGE_DEFAULT_TIMEOUT
    try:
        value = float(raw)
    except ValueError as exc:
        raise ValueError(f"{DECISION_BRIDGE_TIMEOUT_ENV} must be a number") from exc
    if value <= 0 or value > 60:
        raise ValueError(f"{DECISION_BRIDGE_TIMEOUT_ENV} must be greater than 0 and no more than 60")
    return value


def decision_bridge_document() -> dict:
    authority = _decision_authority_url()
    return {
        "enabled": authority is not None,
        "mode": "delegated_authoritative_java",
        "protocol": "cw-decision-1",
        "authority_configured": authority is not None,
        "routes": dict(DECISION_BRIDGE_ROUTES) if authority else {},
        "invariant": "Inference selects. State accumulates. Catalog defines. Generator builds. Validator decides legality.",
        "python_reimplementation": False,
    }


def _decision_openapi_paths() -> dict:
    if _decision_authority_url() is None:
        return {}
    state_schema = {
        "type": "object",
        "required": ["state"],
        "properties": {"state": {"type": "object"}},
        "additionalProperties": False,
    }
    apply_schema = {
        "type": "object",
        "required": ["state", "encoded_mutations"],
        "properties": {
            "state": {"type": "object"},
            "encoded_mutations": {"type": "string", "maxLength": 256},
        },
        "additionalProperties": False,
    }
    begin_schema = {
        "type": "object",
        "required": ["request"],
        "properties": {"request": {"type": "object"}},
        "additionalProperties": False,
    }
    return {
        f"{DECISION_BRIDGE_PREFIX}/profile": {
            "get": {
                **_get_operation("blueprintDecisionProfile", "Retrieve the authoritative compact decision-chain profile."),
                "x-continuity-works-authority": "delegated_java",
            }
        },
        f"{DECISION_BRIDGE_PREFIX}/begin": {
            "post": {
                **_post_operation("blueprintDecisionBegin", "Begin authoritative compact blueprint decision state.", begin_schema),
                "x-continuity-works-authority": "delegated_java",
            }
        },
        f"{DECISION_BRIDGE_PREFIX}/next": {
            "post": {
                **_post_operation("blueprintDecisionNext", "Retrieve only dependency-valid next mutators.", state_schema),
                "x-continuity-works-authority": "delegated_java",
            }
        },
        f"{DECISION_BRIDGE_PREFIX}/apply": {
            "post": {
                **_post_operation("blueprintDecisionApply", "Apply bounded semantic mutations through the authoritative decision chain.", apply_schema),
                "x-continuity-works-authority": "delegated_java",
            }
        },
        f"{DECISION_BRIDGE_PREFIX}/validate": {
            "post": {
                **_post_operation("blueprintDecisionValidate", "Validate accumulated decision state deterministically.", state_schema),
                "x-continuity-works-authority": "delegated_java",
            }
        },
        f"{DECISION_BRIDGE_PREFIX}/finalize": {
            "post": {
                **_post_operation("blueprintDecisionFinalize", "Finalize valid semantic decision state into blueprint specifications.", state_schema),
                "x-continuity-works-authority": "delegated_java",
            }
        },
    }


def openapi_document(base_url: str | None = None) -> dict:
    """Return OpenAPI for the executable service, derived from the publication matrix."""
    tools = _tool_index()
    base = (base_url or CANONICAL_API_URL).rstrip("/")
    paths = {
        "/v1/health": {"get": _get_operation("health", "Check Continuity Works API health and build identity.")},
        "/v1/serviceability": {"get": _get_operation("publicServiceability", "Evaluate the local PUBLIC_SERVICEABILITY publication contract.")},
        "/v1/tools": {"get": _get_operation("tools", "Retrieve the public JSON-Schema tool catalog with publication metadata.")},
        "/v1/tools/index": {"get": _get_operation("toolIndex", "Retrieve a compact token-efficient tool index without loading full schemas.")},
        "/v1/tools/{tool_name}": {"get": {**_get_operation("toolContract", "Retrieve exactly one Continuity Works tool contract/schema."), "parameters": [{"name": "tool_name", "in": "path", "required": True, "schema": {"type": "string"}}]}},
        "/v1/presets": {"get": _get_operation("toolPresets", "Retrieve compact reusable request presets.")},
        "/v1/presets/{preset_id}": {"get": {**_get_operation("toolPreset", "Retrieve one reusable request preset."), "parameters": [{"name": "preset_id", "in": "path", "required": True, "schema": {"type": "string"}}]}},
        "/v1/resolve": {"post": _post_operation("resolveToolRequest", "Merge one preset with caller overrides and return only missing/accepted variables for that selected tool.", schema={"type": "object", "required": ["tool"], "properties": {"tool": {"type": "string"}, "preset_id": {"type": "string"}, "request": {"type": "object"}, "overrides": {"type": "object"}}, "additionalProperties": False})},
        "/v1/resume": {"post": _post_operation("resume", "Resume a previously created Continuity Works snapshot.", schema={"type": "object", "required": ["snapshot_id"], "properties": {"snapshot_id": {"type": "string"}}, "additionalProperties": False})},
        "/openapi.json": {"get": _get_operation("openapi", "Retrieve this OpenAPI 3.1 document.")},
        CANONICAL_DISCOVERY_PATH: {"get": _get_operation("continuityWorksDiscovery", "Retrieve absolute Continuity Works machine-discovery metadata.")},
    }
    paths.update(_decision_openapi_paths())
    for name, spec in PUBLIC_CAPABILITIES.items():
        tool = tools.get(name)
        if tool is None:
            continue
        operation = _get_operation(name, tool["description"], tool_name=name) if spec.http_method == "GET" else _post_operation(name, tool["description"], schema=tool["parameters"], tool_name=name)
        paths.setdefault(spec.path, {})[spec.http_method.lower()] = operation
    schema_version = str(tool_catalog().get("schema_version", "unknown"))
    return {"openapi": "3.1.0", "info": {"title": "Continuity Works Capability API", "version": installed_version(), "description": "Executable HTTP boundary for Continuity Works capabilities. GitHub Pages is a separate static frontend."}, "servers": [{"url": base, "description": "Canonical Continuity Works executable API for this service instance."}], "paths": paths, "x-continuity-works": {"api_version": "v1", "tool_schema_version": schema_version, "frontend": canonical_frontend_url(), "api": base, "tool_catalog": f"{base}/v1/tools", "compact_tool_index": f"{base}/v1/tools/index", "tool_contract": f"{base}/v1/tools/{{tool_name}}", "presets": f"{base}/v1/presets", "resolver": f"{base}/v1/resolve", "health": f"{base}/v1/health", "serviceability": f"{base}/v1/serviceability", "discovery": f"{base}{CANONICAL_DISCOVERY_PATH}", "decision_bridge": decision_bridge_document(), "progressive_disclosure": True, "public_gate": "PUBLIC_SERVICEABILITY"}}


def discovery_document(capability: StructureCapability, base_url: str | None = None) -> dict:
    base = (base_url or CANONICAL_API_URL).rstrip("/")
    catalog = published_tool_catalog(tool_catalog(), capability, base)
    identity = deployment_identity(base, str(catalog.get("schema_version", "unknown")))
    endpoints = {"health": f"{base}/v1/health", "serviceability": f"{base}/v1/serviceability", "tools": f"{base}/v1/tools", "compact_tools": f"{base}/v1/tools/index", "presets": f"{base}/v1/presets", "resolver": f"{base}/v1/resolve", "openapi": f"{base}/openapi.json", "discovery": f"{base}{CANONICAL_DISCOVERY_PATH}"}
    if _decision_authority_url() is not None:
        endpoints["blueprint_decision_profile"] = f"{base}{DECISION_BRIDGE_PREFIX}/profile"
        endpoints["blueprint_decision_begin"] = f"{base}{DECISION_BRIDGE_PREFIX}/begin"
        endpoints["blueprint_decision_next"] = f"{base}{DECISION_BRIDGE_PREFIX}/next"
        endpoints["blueprint_decision_apply"] = f"{base}{DECISION_BRIDGE_PREFIX}/apply"
        endpoints["blueprint_decision_validate"] = f"{base}{DECISION_BRIDGE_PREFIX}/validate"
        endpoints["blueprint_decision_finalize"] = f"{base}{DECISION_BRIDGE_PREFIX}/finalize"
    return {"schema_version": "1.3", "name": "Continuity Works", "slug": "continuity-works", "description": "Machine discovery for the executable Continuity Works API. The GitHub Pages origin is a static frontend only.", "frontend": canonical_frontend_url(), "api": base, "build": identity, "endpoints": endpoints, "decision_bridge": decision_bridge_document(), "capabilities": [{"name": tool["name"], **tool.get("x-continuity-works", {}).get("publication", {})} for tool in catalog.get("tools", [])]}


def health_document(base_url: str | None = None) -> dict:
    schema_version = str(tool_catalog().get("schema_version", "unknown"))
    return {"ok": True, **deployment_identity(base_url or CANONICAL_API_URL, schema_version), "decision_bridge": decision_bridge_document()}


def serviceability_document(capability: StructureCapability, base_url: str | None = None) -> dict:
    base = (base_url or CANONICAL_API_URL).rstrip("/")
    raw_catalog = tool_catalog()
    discovery = discovery_document(capability, base)
    gate = static_serviceability(capability, raw_catalog, openapi_document(base), discovery, base)
    gate["build"] = deployment_identity(base, str(raw_catalog.get("schema_version", "unknown")))
    gate["capabilities"] = discovery["capabilities"]
    gate["decision_bridge"] = decision_bridge_document()
    return gate


def _published_contract(capability: StructureCapability, name: str, base_url: str) -> dict:
    contract = capability.tool_contract(name)
    contract.pop("x-structuresmith", None)
    catalog = published_tool_catalog(tool_catalog(), capability, base_url)
    published = next((item for item in catalog.get("tools", []) if item.get("name") == name), None)
    if published is not None:
        contract["x-continuity-works"] = published.get("x-continuity-works", {})
    return contract


def _published_index(capability: StructureCapability, base_url: str, group: str | None = None) -> dict:
    result = capability.tool_index(group=group)
    catalog = published_tool_catalog(tool_catalog(), capability, base_url)
    publication = {item["name"]: item.get("x-continuity-works", {}).get("publication", {}) for item in catalog.get("tools", [])}
    for item in result.get("tools", []):
        item["publication"] = publication.get(item.get("name"), {"publication_state": "internal_unpublished"})
    result["public_service"] = catalog.get("public_service", {})
    return result


def _route(method: str, path: str):
    method = method.upper()
    for spec in PUBLIC_CAPABILITIES.values():
        if spec.http_method == method and spec.path == path:
            return spec
    return None


class Handler(BaseHTTPRequestHandler):
    capability: StructureCapability | None = None
    def _path(self) -> str:
        return urlsplit(self.path).path
    def _query(self) -> dict:
        return parse_qs(urlsplit(self.path).query, keep_blank_values=False)
    def _public_base_url(self) -> str:
        configured = (os.environ.get("CONTINUITY_WORKS_PUBLIC_BASE_URL") or os.environ.get("STRUCTURESMITH_PUBLIC_BASE_URL") or "").strip()
        if configured: return configured.rstrip("/")
        render_url = os.environ.get("RENDER_EXTERNAL_URL", "").strip()
        if render_url: return render_url.rstrip("/")
        render_hostname = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "").strip()
        if render_hostname: return f"https://{render_hostname}".rstrip("/")
        host = (self.headers.get("X-Forwarded-Host") or self.headers.get("Host") or "").split(",")[0].strip()
        if not host: return CANONICAL_API_URL
        proto = (self.headers.get("X-Forwarded-Proto") or "http").split(",")[0].strip()
        return f"{proto}://{host}"
    def _cors_origin(self):
        configured = (os.environ.get("CONTINUITY_WORKS_CORS_ORIGIN") or os.environ.get("STRUCTURESMITH_CORS_ORIGIN") or DEFAULT_CORS_ORIGINS).strip()
        if configured == "*": return "*"
        origin = self.headers.get("Origin")
        allowed = {item.strip() for item in configured.split(",") if item.strip()}
        return origin if origin in allowed else None
    def _cors_headers(self):
        origin = self._cors_origin()
        if origin:
            self.send_header("Access-Control-Allow-Origin", origin)
            if origin != "*": self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Accept")
        self.send_header("Access-Control-Max-Age", "600")
    def _send(self, status: int, payload):
        body = json.dumps(payload, indent=2, default=str).encode()
        self.send_response(status); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(body))); self.send_header("Cache-Control", "no-store"); self._cors_headers(); self.end_headers(); self.wfile.write(body)
    def _json(self):
        length = int(self.headers.get("Content-Length", "0")); return json.loads(self.rfile.read(length) or b"{}")
    def _invoke_public(self, spec, body: dict | None = None):
        if self.capability is None: raise RuntimeError("Continuity Works capability has not been initialized")
        fn = getattr(self.capability, spec.capability_method)
        if spec.argument_mode == "none": return fn()
        if spec.argument_mode == "version": return fn((body or {}).get("version"))
        return fn(body or {})
    def _decision_bridge(self, method: str, path: str, body: dict | None = None):
        authority = _decision_authority_url()
        if authority is None:
            return self._send(503, {
                "error": "decision_authority_unavailable",
                "message": f"{DECISION_BRIDGE_ENV} is not configured; the Python service will not reimplement authoritative Java decision semantics.",
                "decision_bridge": decision_bridge_document(),
            })
        if authority == self._public_base_url().rstrip("/"):
            return self._send(503, {
                "error": "decision_authority_loop",
                "message": f"{DECISION_BRIDGE_ENV} points back to this HTTP service; attach the separate authoritative Java decision service instead.",
            })
        expected = DECISION_BRIDGE_ROUTES.get(path)
        if expected != method.upper():
            return self._send(404, {"error": "not_found"})
        data = None if body is None else json.dumps(body).encode("utf-8")
        headers = {"Accept": "application/json"}
        if data is not None:
            headers["Content-Type"] = "application/json"
        request = Request(f"{authority}{path}", data=data, headers=headers, method=method.upper())
        try:
            with urlopen(request, timeout=_decision_authority_timeout()) as response:
                raw = response.read()
                payload = json.loads(raw) if raw else {}
                return self._send(response.status, payload)
        except HTTPError as error:
            raw = error.read()
            try:
                payload = json.loads(raw) if raw else {"error": "decision_authority_http_error"}
            except json.JSONDecodeError:
                payload = {"error": "decision_authority_http_error", "message": raw.decode("utf-8", "replace")}
            return self._send(error.code, payload)
        except (URLError, TimeoutError, OSError) as error:
            return self._send(502, {"error": "decision_authority_unreachable", "message": str(error)})
    def do_OPTIONS(self):
        self.send_response(204); self._cors_headers(); self.end_headers()
    def do_GET(self):
        try:
            if self.capability is None: raise RuntimeError("Continuity Works capability has not been initialized")
            path = self._path(); base = self._public_base_url()
            if path == "/v1/health": return self._send(200, health_document(base))
            if path == "/v1/serviceability": return self._send(200, serviceability_document(self.capability, base))
            if path == "/v1/tools":
                query = self._query(); name = (query.get("name") or [None])[0]; mode = (query.get("mode") or ["full"])[0]; group = (query.get("group") or [None])[0]
                if name: return self._send(200, _published_contract(self.capability, name, base))
                if mode in {"compact", "index"}: return self._send(200, _published_index(self.capability, base, group=group))
                return self._send(200, published_tool_catalog(tool_catalog(), self.capability, base))
            if path == "/v1/tools/index": return self._send(200, _published_index(self.capability, base, group=(self._query().get("group") or [None])[0]))
            if path.startswith("/v1/tools/"): return self._send(200, _published_contract(self.capability, unquote(path.removeprefix("/v1/tools/")), base))
            if path == "/v1/presets": return self._send(200, self.capability.tool_presets(compact=not ((self._query().get("mode") or ["compact"])[0] == "full")))
            if path.startswith("/v1/presets/"): return self._send(200, self.capability.tool_preset(unquote(path.removeprefix("/v1/presets/"))))
            if path == "/openapi.json": return self._send(200, openapi_document(base))
            if path in {CANONICAL_DISCOVERY_PATH, LEGACY_DISCOVERY_PATH}: return self._send(200, discovery_document(self.capability, base))
            if path in DECISION_BRIDGE_ROUTES: return self._decision_bridge("GET", path)
            spec = _route("GET", path)
            if spec: return self._send(200, self._invoke_public(spec))
            return self._send(404, {"error": "not_found"})
        except Exception as exc: return self._send(400, {"error": type(exc).__name__, "message": str(exc)})
    def do_POST(self):
        try:
            if self.capability is None: raise RuntimeError("Continuity Works capability has not been initialized")
            body = self._json(); path = self._path()
            if path == "/v1/resolve": return self._send(200, self.capability.resolve_tool_request(body))
            if path == "/v1/resume": return self._send(200, self.capability.resume(body["snapshot_id"]))
            if path in DECISION_BRIDGE_ROUTES: return self._decision_bridge("POST", path, body)
            spec = _route("POST", path)
            if spec: return self._send(200, self._invoke_public(spec, body))
            return self._send(404, {"error": "not_found"})
        except Exception as exc: return self._send(400, {"error": type(exc).__name__, "message": str(exc)})


def serve(project_root=".", host="127.0.0.1", port=8787):
    Handler.capability = StructureCapability(project_root)
    server = ThreadingHTTPServer((host, int(port)), Handler)
    print(f"Continuity Works Capability API listening on http://{host}:{port}")
    server.serve_forever()
