import json
import os
import tempfile
import unittest
from pathlib import Path

from structure_capability import StructureCapability
from structure_capability.publication import (
    CANONICAL_API_URL,
    CANONICAL_FRONTEND_URL,
    PUBLIC_CAPABILITIES,
    published_tool_catalog,
    static_serviceability,
)
from structure_capability.server import discovery_document, health_document, openapi_document
from structure_capability.tooling import tool_catalog


class PublicServiceabilityContractTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.capability = StructureCapability(self.tempdir.name)

    def tearDown(self):
        self.tempdir.cleanup()

    def test_every_tool_has_one_publication_record_and_python_method(self):
        catalog = tool_catalog()
        names = {tool["name"] for tool in catalog["tools"]}
        self.assertEqual(names, set(PUBLIC_CAPABILITIES))
        for name, spec in PUBLIC_CAPABILITIES.items():
            with self.subTest(name=name):
                self.assertTrue(callable(getattr(self.capability, spec.capability_method, None)))
                self.assertTrue(spec.path.startswith("/"))
                self.assertIn(spec.http_method, {"GET", "POST"})
                self.assertIn(spec.manual_ui, {"available", "not_applicable"})

    def test_openapi_and_discovery_are_derived_from_publication_matrix(self):
        spec = openapi_document(CANONICAL_API_URL)
        self.assertEqual(spec["servers"][0]["url"], CANONICAL_API_URL)
        self.assertEqual(spec["info"]["title"], "Continuity Works Capability API")
        self.assertIn("x-continuity-works", spec)
        self.assertNotIn("x-structuresmith", spec)
        for name, publication in PUBLIC_CAPABILITIES.items():
            operation = spec["paths"][publication.path][publication.http_method.lower()]
            self.assertEqual(operation["x-continuity-works-tool"], name)
            self.assertNotIn("x-structuresmith-tool", operation)
        discovery = discovery_document(self.capability, CANONICAL_API_URL)
        self.assertEqual(discovery["name"], "Continuity Works")
        self.assertEqual(discovery["slug"], "continuity-works")
        self.assertEqual(discovery["frontend"], CANONICAL_FRONTEND_URL)
        self.assertEqual(discovery["api"], CANONICAL_API_URL)
        for endpoint in discovery["endpoints"].values():
            self.assertTrue(endpoint.startswith(CANONICAL_API_URL + "/"))
        self.assertEqual({item["name"] for item in discovery["capabilities"]}, set(PUBLIC_CAPABILITIES))

    def test_local_public_serviceability_gate_never_claims_remote_verification(self):
        raw = tool_catalog()
        gate = static_serviceability(
            self.capability,
            raw,
            openapi_document(CANONICAL_API_URL),
            discovery_document(self.capability, CANONICAL_API_URL),
            CANONICAL_API_URL,
        )
        self.assertEqual(gate["gate"], "PUBLIC_SERVICEABILITY")
        self.assertEqual(gate["status"], "READY_FOR_REMOTE_VERIFICATION")
        self.assertEqual(gate["public_deployment"], "not_verified_by_local_gate")
        self.assertEqual(gate["findings"], [])

    def test_public_catalog_exposes_continuity_works_extension_only(self):
        catalog = published_tool_catalog(tool_catalog(), self.capability, CANONICAL_API_URL)
        self.assertEqual(catalog["public_service"]["service"], "Continuity Works")
        for tool in catalog["tools"]:
            self.assertNotIn("x-structuresmith", tool)
            publication = tool["x-continuity-works"]["publication"]
            self.assertEqual(publication["implementation"], "ready")
            self.assertEqual(publication["http_route"], "ready")
            self.assertNotEqual(publication["publication_state"], "internal_unpublished")
            self.assertTrue(publication["canonical_endpoint"].startswith(CANONICAL_API_URL + "/"))
            self.assertEqual(publication["external_verification"], "required")

    def test_health_contains_build_identity_without_faking_commit(self):
        old = os.environ.get("CONTINUITY_WORKS_COMMIT")
        os.environ["CONTINUITY_WORKS_COMMIT"] = "abc123"
        try:
            health = health_document(CANONICAL_API_URL)
        finally:
            if old is None:
                os.environ.pop("CONTINUITY_WORKS_COMMIT", None)
            else:
                os.environ["CONTINUITY_WORKS_COMMIT"] = old
        self.assertTrue(health["ok"])
        self.assertEqual(health["service"], "Continuity Works")
        self.assertEqual(health["service_slug"], "continuity-works")
        self.assertEqual(health["api_version"], "v1")
        self.assertEqual(health["commit"], "abc123")
        self.assertIn("tool_schema_version", health)
        self.assertIn("deployment", health)

    def test_legacy_environment_names_remain_readable_but_not_canonical(self):
        old_new = os.environ.pop("CONTINUITY_WORKS_COMMIT", None)
        old_legacy = os.environ.get("STRUCTURESMITH_COMMIT")
        os.environ["STRUCTURESMITH_COMMIT"] = "legacy123"
        try:
            health = health_document(CANONICAL_API_URL)
        finally:
            if old_new is not None:
                os.environ["CONTINUITY_WORKS_COMMIT"] = old_new
            if old_legacy is None:
                os.environ.pop("STRUCTURESMITH_COMMIT", None)
            else:
                os.environ["STRUCTURESMITH_COMMIT"] = old_legacy
        self.assertEqual(health["commit"], "legacy123")
        self.assertEqual(health["service"], "Continuity Works")

    def test_zero_javascript_source_discovery_is_absolute(self):
        repo = Path(__file__).resolve().parents[1]
        html = (repo / "index.html").read_text(encoding="utf-8")
        static = json.loads((repo / "public" / "api.json").read_text(encoding="utf-8"))
        self.assertIn(f'name="continuity-works-api" content="{CANONICAL_API_URL}"', html)
        self.assertNotIn('name="structuresmith-api"', html)
        self.assertIn(CANONICAL_API_URL + "/openapi.json", html)
        self.assertIn(CANONICAL_API_URL + "/v1/tools", html)
        self.assertIn(CANONICAL_API_URL + "/v1/health", html)
        self.assertIn(CANONICAL_API_URL + "/.well-known/continuity-works.json", html)
        self.assertEqual(static["name"], "Continuity Works")
        self.assertEqual(static["api"], CANONICAL_API_URL)
        self.assertEqual(static["frontend"], CANONICAL_FRONTEND_URL)
        for key in ("health", "tools", "openapi", "discovery", "serviceability"):
            self.assertTrue(static[key].startswith(CANONICAL_API_URL + "/"))

    def test_manual_workbench_uses_live_catalog_not_handwritten_tool_list(self):
        repo = Path(__file__).resolve().parents[1]
        source = (repo / "frontend" / "src" / "components" / "ManualCapabilityWorkbench.js").read_text(encoding="utf-8")
        self.assertNotIn("const TOOL_DEFINITIONS = [", source)
        self.assertIn("client.tools", source)
        self.assertIn("publication_state", source)


if __name__ == "__main__":
    unittest.main()
