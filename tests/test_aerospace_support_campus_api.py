import tempfile
import unittest

from structure_capability import StructureCapability
from structure_capability.publication import CANONICAL_API_URL, PUBLIC_CAPABILITIES
from structure_capability.request_resolution import CapabilityResolver
from structure_capability.server import openapi_document
from structure_capability.tooling import tool_catalog


class AerospaceSupportCampusApiTests(unittest.TestCase):
    TOOL = "aerospace_support_campus_generate"

    def test_tool_catalog_exposes_seed_and_scale_contract(self):
        tools = {tool["name"]: tool for tool in tool_catalog()["tools"]}
        self.assertIn(self.TOOL, tools)
        schema = tools[self.TOOL]["parameters"]
        self.assertEqual(set(schema["required"]), {"scale", "seed"})
        self.assertEqual(
            schema["properties"]["scale"]["enum"],
            ["micro", "light", "standard", "heavy", "superheavy", "megastructure"],
        )
        self.assertFalse(schema["additionalProperties"])

    def test_progressive_disclosure_preset_requires_only_seed(self):
        resolver = CapabilityResolver()
        contract = resolver.contract(self.TOOL)
        self.assertEqual(contract["group"], "layout")
        self.assertIn("layout.aerospace_support_campus", contract["preset_ids"])
        missing = resolver.resolve(
            self.TOOL,
            {},
            preset_id="layout.aerospace_support_campus",
        )
        self.assertFalse(missing["ready"])
        self.assertEqual(missing["missing"], ["seed"])
        resolved = resolver.resolve(
            self.TOOL,
            {"seed": "public-tool-regression"},
            preset_id="layout.aerospace_support_campus",
        )
        self.assertTrue(resolved["ready"])
        self.assertEqual(resolved["request"]["scale"], "standard")

    def test_publication_matrix_and_openapi_expose_canonical_route(self):
        spec = PUBLIC_CAPABILITIES[self.TOOL]
        self.assertEqual(spec.http_method, "POST")
        self.assertEqual(spec.path, "/v1/aerospace/support-campus")
        self.assertEqual(spec.capability_method, self.TOOL)
        openapi = openapi_document(CANONICAL_API_URL)
        operation = openapi["paths"][spec.path]["post"]
        self.assertEqual(operation["x-continuity-works-tool"], self.TOOL)
        request_schema = operation["requestBody"]["content"]["application/json"]["schema"]
        self.assertEqual(set(request_schema["required"]), {"scale", "seed"})

    def test_structure_capability_invokes_authoritative_seeded_generator(self):
        with tempfile.TemporaryDirectory() as td:
            capability = StructureCapability(td)
            result = capability.aerospace_support_campus_generate({
                "scale": "heavy",
                "seed": "api-heavy-campus",
            })
        self.assertEqual(result["report"]["status"], "PASS", result["report"])
        self.assertEqual(result["report"]["scale"], "heavy")
        self.assertEqual(result["report"]["launch_anchor_count"], 1)
        self.assertEqual(
            result["report"]["generation_contract"],
            "continuityworks:seeded_aerospace_support_campus/v1",
        )
        self.assertEqual(len(result["report"]["campus_fingerprint"]), 64)

    def test_capabilities_advertise_seeded_aerospace_campus(self):
        with tempfile.TemporaryDirectory() as td:
            capability = StructureCapability(td)
            capabilities = capability.capabilities()
        self.assertIn(self.TOOL, capabilities["operations"])
        campus = capabilities["aerospace_support_campus"]
        self.assertTrue(campus["deterministic_seeded_generation"])
        self.assertTrue(campus["launch_anchor_reachability_gate"])
        self.assertEqual(campus["road_baseline"]["local_road_width"], 6)
        self.assertEqual(campus["road_baseline"]["terrain_padding_each_side"], 5)


if __name__ == "__main__":
    unittest.main()
