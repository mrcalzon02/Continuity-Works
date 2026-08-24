import json
import tempfile
import unittest
from pathlib import Path

from structure_capability import StructureCapability
from structure_capability.generators import InfrastructureGenerator
from structure_capability.tooling import tool_catalog


class InfrastructureTests(unittest.TestCase):
    def setUp(self):
        self.generator = InfrastructureGenerator()

    def test_inner_city_cross_section_is_strict(self):
        layout = self.generator.generate({
            "module_type": "inner_city_road",
            "seed": 12,
            "world_seed": 99,
            "lost_cities": {"enabled": True},
        })
        self.assertEqual(layout["layout"]["roadbed_width"], 6)
        self.assertEqual(layout["layout"]["terrain_padding"], {"left": 5, "right": 5})
        self.assertEqual(layout["layout"]["footprint_blocks"][0], 16)
        self.assertEqual(layout["fitness"]["status"], "PASS")

        with self.assertRaisesRegex(ValueError, "road width is strict"):
            self.generator.generate({"module_type": "inner_city_road", "road": {"width": 7, "terrain_padding": 5}})
        with self.assertRaisesRegex(ValueError, "terrain padding is strict"):
            self.generator.generate({"module_type": "inner_city_road", "road": {"width": 6, "terrain_padding": 4}})

    def test_world_seed_and_spawn_anchor_are_deterministic(self):
        request = {
            "module_type": "industrial_facility",
            "variant": "rural",
            "seed": 44,
            "world_seed": 8675309,
            "lost_cities": {"enabled": True, "spawn_modes": ["randomized_coordinate", "sequential_jigsaw"]},
        }
        first = self.generator.generate(request)
        second = self.generator.generate(request)
        self.assertEqual(first["spawn"], second["spawn"])
        self.assertEqual(first["determinism"]["fingerprint"], second["determinism"]["fingerprint"])
        changed = self.generator.generate({**request, "world_seed": 8675310})
        self.assertNotEqual(first["spawn"]["candidate_anchor"], changed["spawn"]["candidate_anchor"])

    def test_highway_reference_profile_builds_elevated_support_contract(self):
        result = self.generator.generate({
            "module_type": "highway",
            "segment_length": 96,
            "highway": {
                "profile": "elevated_urban_water_crossing",
                "lane_count": 4,
                "lane_width": 3,
                "shoulder_width": 1,
                "median_width": 2,
                "elevated": True,
                "support_spacing": 12,
                "deck_thickness": 2,
                "min_clearance": 7,
            },
        })
        self.assertTrue(result["layout"]["profile"]["water_span_ready"])
        self.assertEqual(result["layout"]["deck_width"], 16)
        self.assertGreaterEqual(len(result["layout"]["supports"]), 7)
        self.assertEqual(result["fitness"]["status"], "PASS")

    def test_lost_cities_modes_and_jigsaw_are_explicit(self):
        result = self.generator.generate({
            "module_type": "civic_facility",
            "variant": "urban",
            "lost_cities": {
                "enabled": True,
                "spawn_modes": ["tileable_grid", "randomized_coordinate", "sequential_jigsaw"],
                "tile_span_chunks": 2,
            },
            "jigsaw": {"enabled": True, "pool": "demo:roads", "connector_width": 3, "max_depth": 6},
        })
        self.assertEqual(result["lost_cities"]["adapter_status"], "CONTRACT_READY_RUNTIME_TEST_REQUIRED")
        self.assertTrue(result["lost_cities"]["tileable_grid"]["enabled"])
        self.assertTrue(result["lost_cities"]["randomized_coordinate"]["enabled"])
        self.assertTrue(result["lost_cities"]["sequential_jigsaw"]["enabled"])
        self.assertEqual(result["jigsaw"]["pool"], "demo:roads")
        self.assertEqual(len(result["jigsaw"]["connectors"]), 2)

    def test_purpose_depth_gate(self):
        result = self.generator.generate({"module_type": "civic_facility", "purpose": {"depth": 1}})
        self.assertEqual(result["fitness"]["status"], "FAIL")
        self.assertIn("PURPOSE_DEPTH_TOO_SHALLOW", {item["code"] for item in result["fitness"]["findings"]})

    def test_api_provider_and_dedicated_layout_endpoint(self):
        with tempfile.TemporaryDirectory() as td:
            cap = StructureCapability(td)
            direct = cap.infrastructure_layout({
                "module_type": "inner_city_road", "seed": 7, "world_seed": 321,
                "lost_cities": {"enabled": True},
            })
            self.assertEqual(direct["engine"], "native_infrastructure_v1")
            generated = cap.generate({
                "structure_id": "test:urban_road",
                "structure_type": "infrastructure",
                "purpose": {"kind": "transport"},
                "context": {"terrain": "urban"},
                "generation": {
                    "kind": "infrastructure",
                    "layout": {
                        "module_type": "inner_city_road", "seed": 7, "world_seed": 321,
                        "lost_cities": {"enabled": True},
                    },
                },
            })
            self.assertEqual(generated["generation"]["provider_id"], "native_infrastructure_v1")
            self.assertEqual(generated["generated_layout"]["fitness"]["status"], "PASS")

    def test_tool_catalog_exposes_full_infrastructure_surface(self):
        tools = {tool["name"]: tool for tool in tool_catalog()["tools"]}
        schema = tools["infrastructure_layout"]["parameters"]
        self.assertEqual(schema["properties"]["road"]["properties"]["width"]["const"], 6)
        self.assertEqual(schema["properties"]["road"]["properties"]["terrain_padding"]["const"], 5)
        self.assertIn("lost_cities", schema["properties"])
        self.assertIn("jigsaw", schema["properties"])
        self.assertIn("world_seed", schema["properties"])

    def test_archived_four_facility_examples_match_generator(self):
        archive_root = Path(__file__).parents[1] / "examples" / "infrastructure" / "archives"
        manifest = json.loads((archive_root / "manifest.json").read_text())
        self.assertEqual(len(manifest["examples"]), 4)
        for entry in manifest["examples"]:
            payload = json.loads((archive_root / entry["file"]).read_text())
            regenerated = self.generator.generate(payload["request"])
            self.assertEqual(payload["result"]["determinism"]["fingerprint"], regenerated["determinism"]["fingerprint"])
            self.assertEqual(payload["result"]["fitness"]["status"], "PASS")
            self.assertTrue(payload["result"]["spawn"]["world_seed_authorized"])


if __name__ == "__main__":
    unittest.main()
