import unittest
from collections import Counter
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
            "archetypes": 48,
            "facility_references": 47,
            "entries": 105,
        })
        self.assertEqual(report["connector_profiles"], 41)

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
        self.assertNotEqual(self.library.compile_reference(northstar_id)["blocks"], self.library.compile_reference(frontier_id)["blocks"])

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

    def test_phase_one_through_five_support_inventory(self):
        archetypes = self.library.entries(kind="archetype", category="aerospace_support")
        references = self.library.entries(kind="facility_reference", category="aerospace_support")
        self.assertEqual(len(archetypes), 30)
        self.assertEqual(len(references), 30)
        scale_counts = Counter()
        for entry in archetypes:
            data = self.library.load(entry["id"])
            self.assertIn("support_network", data)
            self.assertTrue(data["support_network"]["required_socket_groups"])
            self.assertIn("vessel_state_support", data)
            for scale in data["scale_tiers"]:
                scale_counts[scale] += 1
        self.assertGreaterEqual(scale_counts["micro"], 2)
        self.assertGreaterEqual(scale_counts["light"], 4)
        self.assertGreaterEqual(scale_counts["standard"], 7)
        self.assertGreaterEqual(scale_counts["heavy"], 7)
        self.assertEqual(scale_counts["superheavy"], 6)
        self.assertEqual(scale_counts["megastructure"], 4)
        for entry in references:
            support = self.library.load(entry["id"])["aerospace_support_reference"]
            self.assertTrue(support["actual_structure_commitment"])
            self.assertTrue(support["network_sockets"])
            self.assertIn("vessel_state", support)
            for socket in support["network_sockets"]:
                self.assertIn(socket["profile"], self.library.structures.connector_profiles())

    def test_heavy_support_references_expose_heavy_transport(self):
        heavy_ids = [
            "continuityworks:archetype/hull_section_fabrication_plant",
            "continuityworks:archetype/booster_refurbishment_hangar",
            "continuityworks:archetype/vertical_integration_support_tower",
            "continuityworks:archetype/launch_queue_preparation_yard",
            "continuityworks:archetype/heavy_component_marshalling_yard",
            "continuityworks:archetype/engine_module_works",
            "continuityworks:archetype/heavy_vehicle_retrofit_works",
        ]
        for archetype_id in heavy_ids:
            data = self.library.load(archetype_id)
            profiles = {socket["profile"] for socket in data["support_network"]["sockets"]}
            self.assertTrue(profiles.intersection({"heavy_logistics_10w", "crawler_lane_9x5", "launch_mount_service_axis"}), archetype_id)

    def test_superheavy_and_mega_support_do_not_fall_back_to_small_roads(self):
        for entry in self.library.entries(kind="archetype", category="aerospace_support"):
            data = self.library.load(entry["id"])
            scales = set(data["scale_tiers"])
            if not scales.intersection({"superheavy", "megastructure"}):
                continue
            profiles = {socket["profile"] for socket in data["support_network"]["sockets"]}
            if "heavy_transport" in set(data["support_network"]["required_socket_groups"]):
                self.assertTrue(profiles.intersection({"superheavy_crawler_lane_15x8", "transport_spine_interface"}), entry["id"])
            self.assertNotEqual(profiles, {"local_road_6w"}, entry["id"])

    def test_subterranean_support_archetypes_are_functionally_distinct(self):
        factory = self.library.load("continuityworks:archetype/subterranean_support_factory")
        staging = self.library.load("continuityworks:archetype/underground_vehicle_staging_integration_complex")
        self.assertEqual(factory["support_design_mode"], "subterranean_support")
        self.assertEqual(staging["support_design_mode"], "subterranean_support")
        self.assertIn("subterranean_factory_volume", factory["recognition"]["required_signatures"])
        self.assertIn("near_complete_superheavy_vehicle", staging["recognition"]["required_signatures"])
        self.assertNotEqual(set(factory["recognition"]["required_signatures"]), set(staging["recognition"]["required_signatures"]))

    def test_refinery_requires_process_specific_visual_signatures(self):
        archetype = self.library.load("continuityworks:archetype/compact_diesel_refinery")
        required = set(archetype["recognition"]["required_signatures"])
        self.assertEqual(required, {"process_columns", "dense_pipe_network", "product_tanks", "flare_stack", "loading_gantry"})
        self.assertIn("continuityworks:archetype/bulk_tank_farm", archetype["distinction"]["not_confusable_with"])

    def test_allowed_corporate_override_reuses_archetype_geometry_contract(self):
        frontier = self.library.compile_reference("continuityworks:reference/northstar_rural_gas_station", "continuityworks:corporate/frontier_cooperative")
        self.assertEqual(frontier["metadata"]["corporate_language_id"], "continuityworks:corporate/frontier_cooperative")
        self.assertTrue(all(block["block"].startswith("minecraft:") for block in frontier["blocks"]))


if __name__ == "__main__":
    unittest.main()
