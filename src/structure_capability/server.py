from __future__ import annotations
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from .api import StructureCapability


class Handler(BaseHTTPRequestHandler):
    capability = None

    def _cors_origin(self):
        configured = os.environ.get("STRUCTURESMITH_CORS_ORIGIN", "*").strip()
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
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
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
        if self.path == "/v1/health":
            return self._send(200, {"ok": True, "api": "v1"})
        if self.path == "/v1/capabilities":
            return self._send(200, self.capability.capabilities())
        if self.path == "/v1/tools":
            return self._send(200, self.capability.tools())
        return self._send(404, {"error": "not_found"})

    def do_POST(self):
        try:
            body = self._json()
            if self.path == "/v1/inventory":
                return self._send(200, self.capability.inventory_project())
            if self.path == "/v1/dungeon/layout":
                return self._send(200, self.capability.dungeon_layout(body))
            if self.path == "/v1/infrastructure/layout":
                return self._send(200, self.capability.infrastructure_layout(body))
            if self.path == "/v1/minecraft/version":
                return self._send(200, self.capability.minecraft_version(body.get("version")))
            if self.path == "/v1/audit":
                return self._send(200, self.capability.audit(body))
            if self.path == "/v1/plan":
                return self._send(200, self.capability.plan(body))
            if self.path == "/v1/generate":
                return self._send(200, self.capability.generate(body))
            if self.path == "/v1/resume":
                return self._send(200, self.capability.resume(body["snapshot_id"]))
            return self._send(404, {"error": "not_found"})
        except Exception as e:
            return self._send(400, {"error": type(e).__name__, "message": str(e)})


def serve(project_root=".", host="127.0.0.1", port=8787):
    Handler.capability = StructureCapability(project_root)
    server = ThreadingHTTPServer((host, int(port)), Handler)
    print(f"Structure Capability API listening on http://{host}:{port}")
    server.serve_forever()
