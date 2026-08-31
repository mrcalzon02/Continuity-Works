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
        self.assertEqual(report["entry_count"], 34)
        self.assertEqual(report["counts"]["modules"], 22)
        self.assertEqual(report["connector_profiles"], 11)

    def test_baseline_inventory(self):
        self.assertEqual(len(self.library.ids("layout")), 6)
        self.assertEqual(len(self.library.ids("module")), 22)
        self.assertEqual(len(self.library.ids("test_structure")), 6)
        self.assertIn("continuityworks:layout/modular_grid_3x3", self.library.ids("layout"))
        self.assertIn("continuityworks:module/gatehouse_13x7x7", self.library.ids("module"))
        self.assertIn("continuityworks:module/process_column_5x16x5", self.library.ids("module"))
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
        self.assertFalse(self.library.profiles_compatible("service_2x2", "passage_3x3"))

    def test_module_category_filter(self):
        matches = self.library.entries(kind="module", category="roof")
        self.assertEqual([entry["id"] for entry in matches], ["continuityworks:module/flat_roof_13x2x13", "continuityworks:module/gable_roof_13x5x13"])

    def test_fuel_petroleum_module_filter(self):
        matches = self.library.entries(kind="module", tags={"vanilla_first"})
        self.assertIn("continuityworks:module/fuel_canopy_13x5x9", [entry["id"] for entry in matches])
        self.assertIn("continuityworks:module/pumpjack_9x8x9", [entry["id"] for entry in matches])

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
