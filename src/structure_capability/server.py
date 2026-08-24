from __future__ import annotations
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from .api import StructureCapability

class Handler(BaseHTTPRequestHandler):
    capability = None

    def _send(self, status, payload):
        body = json.dumps(payload, indent=2, default=str).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self):
        length = int(self.headers.get("Content-Length", "0"))
        return json.loads(self.rfile.read(length) or b"{}")

    def do_GET(self):
        if self.path == "/v1/health":
            return self._send(200, {"ok": True, "api": "v1"})
        if self.path == "/v1/capabilities":
            return self._send(200, self.capability.capabilities())
        if self.path == "/v1/tools":
            return self._send(200, self.capability.tools())
        return self._send(404, {"error":"not_found"})

    def do_POST(self):
        try:
            body = self._json()
            if self.path == "/v1/inventory":
                return self._send(200, self.capability.inventory_project())
            if self.path == "/v1/dungeon/layout":
                return self._send(200, self.capability.dungeon_layout(body))
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
            return self._send(404, {"error":"not_found"})
        except Exception as e:
            return self._send(400, {"error": type(e).__name__, "message": str(e)})

def serve(project_root=".", host="127.0.0.1", port=8787):
    Handler.capability = StructureCapability(project_root)
    server = ThreadingHTTPServer((host, int(port)), Handler)
    print(f"Structure Capability API listening on http://{host}:{port}")
    server.serve_forever()
