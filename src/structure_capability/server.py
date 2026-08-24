from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from urllib.parse import urlsplit

from .api import StructureCapability
from .tooling import tool_catalog


DEFAULT_CORS_ORIGINS = "https://mrcalzon02.github.io"

TOOL_ROUTE_MAP = {
    "structure_audit": ("post", "/v1/audit"),
    "structure_plan": ("post", "/v1/plan"),
    "structure_generate": ("post", "/v1/generate"),
    "dungeon_layout": ("post", "/v1/dungeon/layout"),
    "infrastructure_layout": ("post", "/v1/infrastructure/layout"),
    "minecraft_version": ("post", "/v1/minecraft/version"),
    "minecraft_registry_probe": ("post", "/v1/minecraft/registry/probe"),
    "minecraft_book_generate": ("post", "/v1/minecraft/book"),
    "minecraft_loot_table_generate": ("post", "/v1/minecraft/loot-table"),
    "minecraft_recipe_generate": ("post", "/v1/minecraft/recipe"),
    "minecraft_icon_assign": ("post", "/v1/minecraft/icon"),
}


def _tool_index() -> dict:
    return {tool["name"]: tool for tool in tool_catalog()["tools"]}


def _json_response(description: str = "Successful StructureSmith JSON response") -> dict:
    return {
        "description": description,
        "content": {"application/json": {"schema": {"type": "object"}}},
    }


def _error_response() -> dict:
    return {
        "description": "Request rejected by the existing StructureSmith validation boundary.",
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "required": ["error"],
                    "properties": {
                        "error": {"type": "string"},
                        "message": {"type": "string"},
                    },
                }
            }
        },
    }


def _post_operation(operation_id: str, summary: str, schema: dict | None = None, tool_name: str | None = None) -> dict:
    operation = {
        "operationId": operation_id,
        "summary": summary,
        "responses": {"200": _json_response(), "400": _error_response()},
    }
    if schema is not None:
        operation["requestBody"] = {
            "required": True,
            "content": {"application/json": {"schema": schema}},
        }
    if tool_name:
        operation["x-structuresmith-tool"] = tool_name
    return operation


def openapi_document(base_url: str | None = None) -> dict:
    """Return an OpenAPI 3.1 description of the real dependency-free HTTP handler."""
    tools = _tool_index()
    paths = {
        "/v1/health": {
            "get": {
                "operationId": "health",
                "summary": "Check StructureSmith API health.",
                "responses": {"200": _json_response()},
            }
        },
        "/v1/capabilities": {
            "get": {
                "operationId": "capabilities",
                "summary": "Inspect the authoritative StructureCapability surface.",
                "x-structuresmith-tool": "structure_capabilities",
                "responses": {"200": _json_response()},
            }
        },
        "/v1/tools": {
            "get": {
                "operationId": "tools",
                "summary": "Retrieve the portable JSON-Schema tool catalog for AI clients.",
                "responses": {"200": _json_response()},
            }
        },
        "/v1/inventory": {
            "post": _post_operation(
                "inventory",
                "Inventory the configured StructureSmith project.",
                schema={"type": "object", "properties": {}, "additionalProperties": False},
                tool_name="structure_inventory",
            )
        },
        "/v1/resume": {
            "post": _post_operation(
                "resume",
                "Resume a previously created StructureSmith snapshot.",
                schema={
                    "type": "object",
                    "required": ["snapshot_id"],
                    "properties": {"snapshot_id": {"type": "string"}},
                    "additionalProperties": False,
                },
            )
        },
        "/openapi.json": {
            "get": {
                "operationId": "openapi",
                "summary": "Retrieve this OpenAPI 3.1 document.",
                "responses": {"200": _json_response("OpenAPI 3.1 document.")},
            }
        },
        "/.well-known/structuresmith.json": {
            "get": {
                "operationId": "structuresmithDiscovery",
                "summary": "Retrieve StructureSmith machine-discovery metadata.",
                "responses": {"200": _json_response("StructureSmith discovery metadata.")},
            }
        },
    }

    for tool_name, (method, path) in TOOL_ROUTE_MAP.items():
        tool = tools[tool_name]
        paths[path] = {
            method: _post_operation(
                tool_name,
                tool["description"],
                schema=tool["parameters"],
                tool_name=tool_name,
            )
        }

    document = {
        "openapi": "3.1.0",
        "info": {
            "title": "StructureSmith Capability API",
            "version": "0.2.0",
            "description": (
                "Public HTTP boundary for the existing StructureCapability, generator providers, "
                "Minecraft content tools, schemas, and validation gates."
            ),
        },
        "paths": paths,
        "x-structuresmith": {
            "api_version": "v1",
            "tool_catalog": "/v1/tools",
            "discovery": "/.well-known/structuresmith.json",
        },
    }
    if base_url:
        document["servers"] = [{"url": base_url.rstrip("/")}]
    return document


def discovery_document(base_url: str | None = None) -> dict:
    def endpoint(path: str) -> str:
        return f"{base_url.rstrip('/')}{path}" if base_url else path

    return {
        "schema_version": "1.0",
        "name": "StructureSmith",
        "api_version": "v1",
        "description": "AI-callable Minecraft structure and content capability API.",
        "endpoints": {
            "health": endpoint("/v1/health"),
            "tools": endpoint("/v1/tools"),
            "openapi": endpoint("/openapi.json"),
        },
    }


class Handler(BaseHTTPRequestHandler):
    capability = None

    def _path(self) -> str:
        return urlsplit(self.path).path

    def _public_base_url(self) -> str | None:
        configured = os.environ.get("STRUCTURESMITH_PUBLIC_BASE_URL", "").strip()
        if configured:
            return configured.rstrip("/")
        render_hostname = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "").strip()
        if render_hostname:
            return f"https://{render_hostname}".rstrip("/")
        host = (self.headers.get("X-Forwarded-Host") or self.headers.get("Host") or "").split(",")[0].strip()
        if not host:
            return None
        proto = (self.headers.get("X-Forwarded-Proto") or "http").split(",")[0].strip()
        return f"{proto}://{host}"

    def _cors_origin(self):
        configured = os.environ.get("STRUCTURESMITH_CORS_ORIGIN", DEFAULT_CORS_ORIGINS).strip()
        if configured == "*":
            return "*"
        origin = self.headers.get("Origin")
        allowed = {item.strip() for item in configured.split(",") if item.strip()}
        return origin if origin in allowed else None

    def _cors_headers(self):
        origin = self._cors_origin()
        if origin:
            self.send_header("Access-Control-Allow-Origin", origin)
            if origin != "*":
                self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Accept")
        self.send_header("Access-Control-Max-Age", "600")

    def _send(self, status, payload):
        body = json.dumps(payload, indent=2, default=str).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self._cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def _json(self):
        length = int(self.headers.get("Content-Length", "0"))
        return json.loads(self.rfile.read(length) or b"{}")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors_headers()
        self.end_headers()

    def do_GET(self):
        path = self._path()
        if path == "/v1/health":
            return self._send(200, {"ok": True, "api": "v1"})
        if path == "/v1/capabilities":
            return self._send(200, self.capability.capabilities())
        if path == "/v1/tools":
            return self._send(200, self.capability.tools())
        if path == "/openapi.json":
            return self._send(200, openapi_document(self._public_base_url()))
        if path == "/.well-known/structuresmith.json":
            return self._send(200, discovery_document(self._public_base_url()))
        return self._send(404, {"error": "not_found"})

    def do_POST(self):
        try:
            body = self._json()
            path = self._path()
            if path == "/v1/inventory":
                return self._send(200, self.capability.inventory_project())
            if path == "/v1/dungeon/layout":
                return self._send(200, self.capability.dungeon_layout(body))
            if path == "/v1/infrastructure/layout":
                return self._send(200, self.capability.infrastructure_layout(body))
            if path == "/v1/minecraft/version":
                return self._send(200, self.capability.minecraft_version(body.get("version")))
            if path == "/v1/minecraft/registry/probe":
                return self._send(200, self.capability.minecraft_registry_probe(body))
            if path == "/v1/minecraft/book":
                return self._send(200, self.capability.minecraft_book_generate(body))
            if path == "/v1/minecraft/loot-table":
                return self._send(200, self.capability.minecraft_loot_table_generate(body))
            if path == "/v1/minecraft/recipe":
                return self._send(200, self.capability.minecraft_recipe_generate(body))
            if path == "/v1/minecraft/icon":
                return self._send(200, self.capability.minecraft_icon_assign(body))
            if path == "/v1/audit":
                return self._send(200, self.capability.audit(body))
            if path == "/v1/plan":
                return self._send(200, self.capability.plan(body))
            if path == "/v1/generate":
                return self._send(200, self.capability.generate(body))
            if path == "/v1/resume":
                return self._send(200, self.capability.resume(body["snapshot_id"]))
            return self._send(404, {"error": "not_found"})
        except Exception as e:
            return self._send(400, {"error": type(e).__name__, "message": str(e)})


def serve(project_root=".", host="127.0.0.1", port=8787):
    Handler.capability = StructureCapability(project_root)
    server = ThreadingHTTPServer((host, int(port)), Handler)
    print(f"Structure Capability API listening on http://{host}:{port}")
    server.serve_forever()
