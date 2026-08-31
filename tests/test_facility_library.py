import unittest
from pathlib import Path

from structure_capability.facility_library import FacilityLibrary


class FacilityLibraryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        repo = Path(__file__).resolve().parents[1]
        cls.library = FacilityLibrary(repo / "facility_library", repo / "library")

    def test_semantic_library_passes_validation(self):
        report = self.library.validate()
        self.assertEqual(report["status"], "PASS", report["findings"])
        self.assertEqual(report["counts"], {
            "corporate_languages": 10,
            "archetypes": 18,
            "facility_references": 17,
            "entries": 45,
        })
        self.assertEqual(report["connector_profiles"], 18)

    def test_corporate_palettes_are_vanilla_only(self):
        for corporate_id in self.library.ids("corporate_language"):
            palette = self.library.corporate_palette(corporate_id)
            self.assertTrue(palette)
            self.assertTrue(all(block.startswith("minecraft:") for block in palette.values()))

    def test_same_archetype_can_have_distinct_corporate_references(self):
        northstar_id = "continuityworks:reference/northstar_rural_gas_station"
        frontier_id = "continuityworks:reference/frontier_rural_gas_station"
        northstar = self.library.load(northstar_id)
        frontier = self.library.load(frontier_id)
        self.assertEqual(northstar["archetype_id"], frontier["archetype_id"])
        self.assertNotEqual(northstar["corporate_language_id"], frontier["corporate_language_id"])
        northstar_blocks = self.library.compile_reference(northstar_id)["blocks"]
        frontier_blocks = self.library.compile_reference(frontier_id)["blocks"]
        self.assertNotEqual(northstar_blocks, frontier_blocks)

    def test_every_reference_is_recognizable_and_materializes(self):
        for reference_id in self.library.ids("facility_reference"):
            recognition = self.library.evaluate_reference(reference_id)
            self.assertEqual(recognition["status"], "PASS", recognition)
            self.assertEqual(recognition["missing_signatures"], [])
            self.assertGreater(recognition["compiled_block_count"], 500)
            compiled = self.library.compile_reference(reference_id)
            self.assertTrue(all(block["block"].startswith("minecraft:") for block in compiled["blocks"]))

    def test_aerospace_inventory(self):
        self.assertEqual(len(self.library.entries(kind="corporate_language", category="aerospace_orbital")), 6)
        self.assertEqual(len(self.library.entries(kind="archetype", category="aerospace_orbital")), 12)
        self.assertEqual(len(self.library.entries(kind="facility_reference", category="aerospace_orbital")), 12)

    def test_refinery_requires_process_specific_visual_signatures(self):
        archetype = self.library.load("continuityworks:archetype/compact_diesel_refinery")
        required = set(archetype["recognition"]["required_signatures"])
        self.assertEqual(required, {"process_columns", "dense_pipe_network", "product_tanks", "flare_stack", "loading_gantry"})
        self.assertIn("continuityworks:archetype/bulk_tank_farm", archetype["distinction"]["not_confusable_with"])

    def test_allowed_corporate_override_reuses_archetype_geometry_contract(self):
        reference_id = "continuityworks:reference/northstar_rural_gas_station"
        frontier = self.library.compile_reference(reference_id, "continuityworks:corporate/frontier_cooperative")
        self.assertEqual(frontier["metadata"]["corporate_language_id"], "continuityworks:corporate/frontier_cooperative")
        self.assertTrue(all(block["block"].startswith("minecraft:") for block in frontier["blocks"]))


if __name__ == "__main__":
    unittest.main()
