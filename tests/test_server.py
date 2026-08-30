import json
import os
import tempfile
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from structure_capability import StructureCapability
from structure_capability.server import Handler, ThreadingHTTPServer


class PublicHttpApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tempdir = tempfile.TemporaryDirectory()
        cls.previous_cors = os.environ.get("CONTINUITY_WORKS_CORS_ORIGIN")
        os.environ["CONTINUITY_WORKS_CORS_ORIGIN"] = "https://mrcalzon02.github.io"
        Handler.capability = StructureCapability(cls.tempdir.name)
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)
        cls.tempdir.cleanup()
        if cls.previous_cors is None:
            os.environ.pop("CONTINUITY_WORKS_CORS_ORIGIN", None)
        else:
            os.environ["CONTINUITY_WORKS_CORS_ORIGIN"] = cls.previous_cors

    def request(self, method, path, body=None, headers=None):
        data = None if body is None else json.dumps(body).encode("utf-8")
        request_headers = dict(headers or {})
        if data is not None:
            request_headers["Content-Type"] = "application/json"
        req = Request(
            f"{self.base_url}{path}",
            data=data,
            method=method,
            headers=request_headers,
        )
        try:
            with urlopen(req, timeout=10) as response:
                raw = response.read()
                payload = json.loads(raw) if raw else None
                return response.status, dict(response.headers.items()), payload
        except HTTPError as error:
            raw = error.read()
            payload = json.loads(raw) if raw else None
            return error.code, dict(error.headers.items()), payload

    def test_openapi_and_discovery_advertise_real_routes(self):
        status, _, spec = self.request("GET", "/openapi.json")
        self.assertEqual(status, 200)
        self.assertEqual(spec["openapi"], "3.1.0")
        self.assertEqual(spec["info"]["title"], "Continuity Works Capability API")
        self.assertIn("x-continuity-works", spec)
        self.assertNotIn("x-structuresmith", spec)
        expected = {
            "/v1/health": "get",
            "/v1/capabilities": "get",
            "/v1/tools": "get",
            "/v1/inventory": "post",
            "/v1/audit": "post",
            "/v1/plan": "post",
            "/v1/generate": "post",
            "/v1/dungeon/layout": "post",
            "/v1/infrastructure/layout": "post",
            "/v1/minecraft/version": "post",
            "/v1/minecraft/registry/probe": "post",
            "/v1/minecraft/book": "post",
            "/v1/minecraft/loot-table": "post",
            "/v1/minecraft/recipe": "post",
            "/v1/minecraft/icon": "post",
            "/v1/resume": "post",
            "/openapi.json": "get",
            "/.well-known/continuity-works.json": "get",
        }
        for path, method in expected.items():
            self.assertIn(path, spec["paths"])
            self.assertIn(method, spec["paths"][path])
        self.assertNotIn("/.well-known/structuresmith.json", spec["paths"])

        status, _, discovery = self.request("GET", "/.well-known/continuity-works.json")
        self.assertEqual(status, 200)
        self.assertEqual(discovery["name"], "Continuity Works")
        self.assertEqual(discovery["slug"], "continuity-works")
        self.assertTrue(discovery["endpoints"]["tools"].endswith("/v1/tools"))
        self.assertTrue(discovery["endpoints"]["openapi"].endswith("/openapi.json"))
        self.assertTrue(discovery["endpoints"]["health"].endswith("/v1/health"))
        self.assertTrue(discovery["endpoints"]["discovery"].endswith("/.well-known/continuity-works.json"))

    def test_legacy_discovery_alias_is_unadvertised_but_compatible(self):
        status, _, legacy = self.request("GET", "/.well-known/structuresmith.json")
        self.assertEqual(status, 200)
        self.assertEqual(legacy["name"], "Continuity Works")
        self.assertTrue(legacy["endpoints"]["discovery"].endswith("/.well-known/continuity-works.json"))

    def test_public_tool_catalog_uses_continuity_works_vendor_extension(self):
        status, _, catalog = self.request("GET", "/v1/tools")
        self.assertEqual(status, 200)
        self.assertGreater(len(catalog.get("tools", [])), 0)
        for tool in catalog["tools"]:
            self.assertIn("x-continuity-works", tool)
            self.assertNotIn("x-structuresmith", tool)

    def test_cors_allows_github_pages_and_rejects_other_origins(self):
        status, headers, _ = self.request(
            "GET",
            "/v1/health",
            headers={"Origin": "https://mrcalzon02.github.io"},
        )
        self.assertEqual(status, 200)
        self.assertEqual(headers.get("Access-Control-Allow-Origin"), "https://mrcalzon02.github.io")
        self.assertEqual(headers.get("Vary"), "Origin")

        status, headers, _ = self.request(
            "GET",
            "/v1/health",
            headers={"Origin": "https://example.invalid"},
        )
        self.assertEqual(status, 200)
        self.assertNotIn("Access-Control-Allow-Origin", headers)

    def test_options_preflight(self):
        status, headers, payload = self.request(
            "OPTIONS",
            "/v1/generate",
            headers={
                "Origin": "https://mrcalzon02.github.io",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
        )
        self.assertEqual(status, 204)
        self.assertIsNone(payload)
        self.assertEqual(headers.get("Access-Control-Allow-Origin"), "https://mrcalzon02.github.io")
        self.assertIn("POST", headers.get("Access-Control-Allow-Methods", ""))
        self.assertIn("Content-Type", headers.get("Access-Control-Allow-Headers", ""))

    def test_all_advertised_get_routes_execute(self):
        for path in (
            "/v1/health",
            "/v1/capabilities",
            "/v1/tools",
            "/openapi.json",
            "/.well-known/continuity-works.json",
        ):
            with self.subTest(path=path):
                status, _, payload = self.request("GET", path)
                self.assertEqual(status, 200)
                self.assertIsInstance(payload, dict)

    def test_all_advertised_post_routes_execute(self):
        structure_request = {
            "structure_id": "test:http_smoke",
            "purpose": {"kind": "warehouse", "required_zones": ["storage"]},
        }
        requests = [
            ("/v1/inventory", {}),
            ("/v1/audit", structure_request),
            ("/v1/plan", structure_request),
            ("/v1/generate", structure_request),
            ("/v1/dungeon/layout", {"seed": 42}),
            ("/v1/infrastructure/layout", {"module_type": "inner_city_road"}),
            ("/v1/minecraft/version", {"version": "1.20.1"}),
            ("/v1/minecraft/registry/probe", {"id": "minecraft:stone", "kind": "item"}),
            (
                "/v1/minecraft/book",
                {"target_version": "1.20.1", "title": "Smoke", "author": "CI", "pages": ["ok"]},
            ),
            (
                "/v1/minecraft/loot-table",
                {
                    "target_version": "1.20.1",
                    "table_id": "test:smoke",
                    "items": [{"id": "minecraft:stone", "weight": 1}],
                },
            ),
            (
                "/v1/minecraft/recipe",
                {
                    "target_version": "1.20.1",
                    "recipe_id": "test:smoke",
                    "type": "crafting_shapeless",
                    "ingredients": ["minecraft:stone"],
                    "result": "minecraft:cobblestone",
                },
            ),
            ("/v1/minecraft/icon", {"subject": "structure", "mode": "badge", "label": "CW"}),
        ]
        for path, body in requests:
            with self.subTest(path=path):
                status, _, payload = self.request("POST", path, body)
                self.assertEqual(status, 200, payload)
                self.assertIsInstance(payload, dict)

        status, _, planned = self.request("POST", "/v1/plan", structure_request)
        self.assertEqual(status, 200)
        snapshot_id = planned["snapshot"]["snapshot_id"]
        status, _, resumed = self.request("POST", "/v1/resume", {"snapshot_id": snapshot_id})
        self.assertEqual(status, 200, resumed)
        self.assertEqual(resumed["snapshot_id"], snapshot_id)


if __name__ == "__main__":
    unittest.main()
