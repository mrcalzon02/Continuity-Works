import unittest
from pathlib import Path

from structure_capability.facility_library import FacilityLibrary
from structure_capability.aerospace_support_network import AerospaceSupportNetworkValidator
from structure_capability.seeded_aerospace_support_campus import (
    SeededAerospaceSupportCampusError,
    SeededAerospaceSupportCampusGenerator,
)


class SeededAerospaceSupportCampusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        repo = Path(__file__).resolve().parents[1]
        facilities = FacilityLibrary(repo / "facility_library", repo / "library")
        network = AerospaceSupportNetworkValidator(
            repo,
            structure_library=facilities.structures,
        )
        cls.facilities = facilities
        cls.generator = SeededAerospaceSupportCampusGenerator(facilities, network)

    def test_same_seed_replays_exact_graph_and_fingerprint(self):
        first = self.generator.generate("superheavy", "integration-alpha")
        second = self.generator.generate("superheavy", "integration-alpha")
        self.assertEqual(first["graph"], second["graph"])
        self.assertEqual(
            first["report"]["campus_fingerprint"],
            second["report"]["campus_fingerprint"],
        )

    def test_different_seeds_change_canonical_fingerprint(self):
        first = self.generator.generate("standard", "campus-a")
        second = self.generator.generate("standard", "campus-b")
        self.assertNotEqual(first["report"]["seed_digest"], second["report"]["seed_digest"])
        self.assertNotEqual(
            first["report"]["campus_fingerprint"],
            second["report"]["campus_fingerprint"],
        )

    def test_all_six_scales_produce_valid_launch_connected_graphs(self):
        for scale in self.generator.SCALES:
            with self.subTest(scale=scale):
                result = self.generator.generate(scale, f"scale-regression-{scale}")
                self.assertEqual(result["report"]["status"], "PASS", result["report"])
                self.assertEqual(result["report"]["network_findings"], [])
                self.assertEqual(result["report"]["launch_anchor_count"], 1)
                self.assertGreaterEqual(result["report"]["node_count"], 5)
                self.assertGreaterEqual(result["report"]["edge_count"], 4)

    def test_every_facility_uses_one_compatible_campus_operator(self):
        for scale in self.generator.SCALES:
            result = self.generator.generate(scale, f"operator-{scale}")
            operator = result["report"]["corporate_language_id"]
            for node in result["graph"]["nodes"]:
                if node["kind"] != "facility":
                    continue
                self.assertEqual(node["corporate_language_id"], operator)
                archetype = self.facilities.load(node["archetype_id"])
                self.assertIn(operator, archetype["allowed_corporate_languages"])

    def test_every_facility_resolves_an_actual_reference(self):
        for scale in self.generator.SCALES:
            result = self.generator.generate(scale, f"reference-{scale}")
            for node in result["graph"]["nodes"]:
                if node["kind"] != "facility":
                    continue
                self.assertIsNotNone(node["reference_id"], node)
                self.assertEqual(
                    self.facilities.entry(node["reference_id"])["kind"],
                    "facility_reference",
                )

    def test_explicit_incompatible_operator_is_rejected(self):
        with self.assertRaises(SeededAerospaceSupportCampusError):
            self.generator.generate(
                "superheavy",
                12345,
                "continuityworks:corporate/pel_roma_astronautics",
            )

    def test_invalid_seed_and_scale_are_rejected(self):
        with self.assertRaises(SeededAerospaceSupportCampusError):
            self.generator.generate("light", "")
        with self.assertRaises(SeededAerospaceSupportCampusError):
            self.generator.generate("unknown", 123)

    def test_superheavy_and_megastructure_graphs_use_megascale_transport(self):
        for scale in ("superheavy", "megastructure"):
            result = self.generator.generate(scale, f"transport-{scale}")
            connected_profiles = set()
            nodes = {node["id"]: node for node in result["graph"]["nodes"]}
            for edge in result["graph"]["edges"]:
                for endpoint in (edge["a"], edge["b"]):
                    node = nodes[endpoint["node"]]
                    socket = next(
                        socket
                        for socket in node["sockets"]
                        if socket["id"] == endpoint["socket"]
                    )
                    connected_profiles.add(socket["profile"])
            self.assertTrue(
                connected_profiles.intersection(
                    {"superheavy_crawler_lane_15x8", "transport_spine_interface"}
                ),
                connected_profiles,
            )

    def test_megastructure_template_includes_underground_final_staging(self):
        result = self.generator.generate("megastructure", "deep-campus")
        archetypes = {
            node.get("archetype_id")
            for node in result["graph"]["nodes"]
            if node["kind"] == "facility"
        }
        self.assertIn(
            "continuityworks:archetype/underground_vehicle_staging_integration_complex",
            archetypes,
        )

    def test_micro_template_preserves_six_block_local_road_contract(self):
        result = self.generator.generate("micro", "micro-road")
        profiles = {
            socket["profile"]
            for node in result["graph"]["nodes"]
            for socket in node["sockets"]
        }
        self.assertIn("local_road_6w", profiles)
        self.assertEqual(
            self.generator.network.network_modules["road_baseline"]["local_road_width_blocks"],
            6,
        )
        self.assertEqual(
            self.generator.network.network_modules["road_baseline"]["terrain_padding_each_side_blocks"],
            5,
        )

    def test_site_context_is_seeded_and_normalized(self):
        result = self.generator.generate("heavy", "terrain-layout")
        context = result["report"]["site_context"]
        self.assertIn(context["orientation"], self.generator.ORIENTATIONS)
        self.assertIn(context["spacing"], self.generator.SPACING)
        self.assertIn(context["terrain"], self.generator.TERRAIN["heavy"])
        for node in result["graph"]["nodes"]:
            self.assertEqual(len(node["site_pos"]), 2)
            self.assertGreaterEqual(node["site_pos"][0], 0)
            self.assertGreaterEqual(node["site_pos"][1], 0)


if __name__ == "__main__":
    unittest.main()
