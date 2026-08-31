import unittest
from pathlib import Path

from structure_capability.structure_library import StructureLibrary


class StructureLibraryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[1] / "library"
        cls.library = StructureLibrary(root)

    def test_baseline_library_passes_static_validation(self):
        report = self.library.validate()
        self.assertEqual(report["status"], "PASS", report["findings"])
        self.assertEqual(report["entry_count"], 55)
        self.assertEqual(report["counts"]["modules"], 43)
        self.assertEqual(report["connector_profiles"], 41)

    def test_baseline_inventory(self):
        self.assertEqual(len(self.library.ids("layout")), 6)
        self.assertEqual(len(self.library.ids("module")), 43)
        self.assertEqual(len(self.library.ids("test_structure")), 6)
        self.assertIn("continuityworks:layout/modular_grid_3x3", self.library.ids("layout"))
        self.assertIn("continuityworks:module/gatehouse_13x7x7", self.library.ids("module"))
        self.assertIn("continuityworks:module/process_column_5x16x5", self.library.ids("module"))
        self.assertIn("continuityworks:module/superheavy_launch_tower_15x48x15", self.library.ids("module"))
        self.assertIn("continuityworks:module/mega_silo_shaft_31x48x31", self.library.ids("module"))
        self.assertIn("continuityworks:test/orientation_marker_5x4x5", self.library.ids("test_structure"))

    def test_layout_module_and_physical_fixture_are_separate(self):
        layout = self.library.load("continuityworks:layout/compact_room_7x7")
        module = self.library.load("continuityworks:module/standard_room_9x5x9")
        fixture = self.library.load("continuityworks:test/room_shell_7x5x7")
        self.assertIn("connectors", layout)
        self.assertNotIn("blocks", layout)
        self.assertIn("connectors", module)
        self.assertNotIn("blocks", module)
        self.assertEqual(module["base_layout"], "continuityworks:layout/compact_room_7x7")
        self.assertIn("blocks", fixture)
        self.assertEqual(fixture["metadata"]["layout_id"], "continuityworks:layout/compact_room_7x7")

    def test_connector_profiles_are_symmetric_and_queryable(self):
        self.assertTrue(self.library.profiles_compatible("passage_3x3", "gate_3x3"))
        self.assertTrue(self.library.profiles_compatible("vertical_3x3", "vertical_3x3"))
        self.assertTrue(self.library.profiles_compatible("vehicle_lane_5x4", "vehicle_gate_5x4"))
        self.assertTrue(self.library.profiles_compatible("process_pipe_1x1", "process_pipe_1x1"))
        self.assertTrue(self.library.profiles_compatible("crawler_lane_9x5", "crawler_lane_9x5"))
        self.assertTrue(self.library.profiles_compatible("superheavy_crawler_lane_15x8", "superheavy_crawler_lane_15x8"))
        self.assertTrue(self.library.profiles_compatible("silo_vertical_7x7", "silo_vertical_7x7"))
        self.assertTrue(self.library.profiles_compatible("mega_silo_vertical_15x15", "mega_silo_vertical_15x15"))
        self.assertTrue(self.library.profiles_compatible("industrial_road_8w", "checkpoint_road_interface"))
        self.assertTrue(self.library.profiles_compatible("launch_support_road_8w", "industrial_road_8w"))
        self.assertTrue(self.library.profiles_compatible("crew_access_3x3", "passage_3x3"))
        self.assertTrue(self.library.profiles_compatible("pedestrian_causeway_5x3", "bridge_5x3"))
        self.assertTrue(self.library.profiles_compatible("utility_spine_3x3", "power_service_corridor_3x3"))
        self.assertTrue(self.library.profiles_compatible("pad_queue_interface", "crawler_lane_9x5"))
        self.assertTrue(self.library.profiles_compatible("subterranean_support_interface", "silo_vertical_7x7"))
        self.assertFalse(self.library.profiles_compatible("service_2x2", "passage_3x3"))
        self.assertFalse(self.library.profiles_compatible("local_road_6w", "heavy_logistics_10w"))

    def test_module_category_filter(self):
        matches = self.library.entries(kind="module", category="roof")
        self.assertEqual([entry["id"] for entry in matches], ["continuityworks:module/flat_roof_13x2x13", "continuityworks:module/gable_roof_13x5x13"])

    def test_aerospace_module_filter(self):
        matches = self.library.entries(kind="module", tags={"aerospace"})
        self.assertEqual(len(matches), 21)
        ids = {entry["id"] for entry in matches}
        self.assertIn("continuityworks:module/landing_pad_17x2x17", ids)
        self.assertIn("continuityworks:module/mega_integration_bay_31x40x39", ids)

    def test_orientation_fixture_has_cardinal_markers(self):
        fixture = self.library.load("continuityworks:test/orientation_marker_5x4x5")
        self.assertEqual(set(fixture["metadata"]["direction_legend"]), {"north", "east", "south", "west"})

    def test_tag_filter(self):
        matches = self.library.entries(kind="test_structure", tags={"verticality"})
        self.assertEqual([entry["id"] for entry in matches], ["continuityworks:test/tower_core_9x12x9"])

    def test_module_connectors_use_known_profiles(self):
        profiles = set(self.library.connector_profiles())
        for module_id in self.library.ids("module"):
            module = self.library.load(module_id)
            for connector in module["connectors"]:
                self.assertIn(connector["profile"], profiles)


if __name__ == "__main__":
    unittest.main()
