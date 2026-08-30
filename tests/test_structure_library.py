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
        self.assertEqual(report["entry_count"], 12)

    def test_baseline_inventory(self):
        self.assertEqual(len(self.library.ids("layout")), 6)
        self.assertEqual(len(self.library.ids("test_structure")), 6)
        self.assertIn("continuityworks:layout/modular_grid_3x3", self.library.ids("layout"))
        self.assertIn("continuityworks:test/orientation_marker_5x4x5", self.library.ids("test_structure"))

    def test_layout_and_physical_fixture_are_separate(self):
        layout = self.library.load("continuityworks:layout/compact_room_7x7")
        fixture = self.library.load("continuityworks:test/room_shell_7x5x7")
        self.assertIn("connectors", layout)
        self.assertNotIn("blocks", layout)
        self.assertIn("blocks", fixture)
        self.assertEqual(fixture["metadata"]["layout_id"], "continuityworks:layout/compact_room_7x7")

    def test_orientation_fixture_has_cardinal_markers(self):
        fixture = self.library.load("continuityworks:test/orientation_marker_5x4x5")
        self.assertEqual(set(fixture["metadata"]["direction_legend"]), {"north", "east", "south", "west"})

    def test_tag_filter(self):
        matches = self.library.entries(kind="test_structure", tags={"verticality"})
        self.assertEqual([entry["id"] for entry in matches], ["continuityworks:test/tower_core_9x12x9"])


if __name__ == "__main__":
    unittest.main()
