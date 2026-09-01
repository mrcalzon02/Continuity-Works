import unittest

from structure_capability.early_human_deep_cave import (
    DeepCaveRefugeGenerationError,
    DeepCaveRefugeGenerator,
)
from structure_capability.minecraft.worldgen import MINIMUM_STRUCTURE_EXCLUSION_RADIUS


class DeepCaveRefugeTests(unittest.TestCase):
    def setUp(self):
        self.generator = DeepCaveRefugeGenerator()

    def test_same_seed_is_deterministic(self):
        first = self.generator.generate(seed=3003, scale="medium")
        second = self.generator.generate(seed=3003, scale="medium")
        self.assertEqual(first, second)
        self.assertEqual(first["metadata"]["fingerprint"], second["metadata"]["fingerprint"])

    def test_different_seed_changes_structure(self):
        first = self.generator.generate(seed=3003, scale="medium")
        second = self.generator.generate(seed=3004, scale="medium")
        self.assertNotEqual(first["metadata"]["fingerprint"], second["metadata"]["fingerprint"])

    def test_scales_are_nonempty_and_in_bounds(self):
        for scale in ("small", "medium", "large"):
            with self.subTest(scale=scale):
                result = self.generator.generate(seed=303, scale=scale)
                size = result["size"]
                self.assertGreater(len(result["blocks"]), 0)
                for entry in result["blocks"]:
                    self.assertTrue(entry["block"].startswith("minecraft:"))
                    self.assertTrue(all(0 <= entry["pos"][i] < size[i] for i in range(3)))

    def test_deep_refuge_qualification_passes(self):
        result = self.generator.generate(seed=20260903, scale="medium")
        meta = result["metadata"]
        self.assertTrue(meta["qualification_pass"])
        self.assertTrue(meta["qualification"]["daylight_lost"])
        self.assertTrue(meta["qualification"]["minimum_route_length"])
        self.assertTrue(meta["qualification"]["route_complexity"])
        self.assertGreater(meta["refuge_anchor"][2], meta["daylight_loss_z"])
        self.assertGreater(len(meta["wayfinding_markers"]), 0)

    def test_refuge_is_not_threshold_occupation(self):
        result = self.generator.generate(seed=444, scale="large")
        meta = result["metadata"]
        self.assertGreater(meta["route_length"], 30)
        self.assertGreater(meta["refuge_start_z"], meta["daylight_loss_z"] + 12)
        self.assertGreaterEqual(meta["route_complexity"], 8)

    def test_restricted_ventilation_suppresses_hearth_when_selected(self):
        found = False
        for seed in range(1, 100):
            result = self.generator.generate(seed=seed, scale="small")
            if result["metadata"]["ventilation_class"] == "restricted":
                found = True
                self.assertFalse(result["metadata"]["hearth_allowed"])
                self.assertIsNone(result["metadata"]["hearth"])
                self.assertNotIn("minecraft:campfire", {entry["block"] for entry in result["blocks"]})
                break
        self.assertTrue(found)

    def test_invalid_scale_is_rejected(self):
        with self.assertRaises(DeepCaveRefugeGenerationError):
            self.generator.generate(seed=1, scale="gigantic")

    def test_worldgen_is_underground_and_protected(self):
        bundle = self.generator.worldgen_bundle()
        self.assertEqual(bundle["validation_findings"], [])
        structure = bundle["structure"]
        protection = bundle["protection_profile"]
        self.assertEqual(structure["step"], "underground_structures")
        self.assertNotIn("project_start_to_heightmap", structure)
        self.assertEqual(structure["start_height"]["absolute"], -24)
        self.assertFalse(bundle["placement_contract"]["surface_projection"])
        self.assertTrue(bundle["placement_contract"]["requires_deep_cave_topology"])
        self.assertGreaterEqual(protection["exclusion_radius"], MINIMUM_STRUCTURE_EXCLUSION_RADIUS)
        self.assertGreaterEqual(
            protection["jigsaw_piece_exclusion_radius"],
            MINIMUM_STRUCTURE_EXCLUSION_RADIUS,
        )
        self.assertTrue(protection["protect_jigsaw_pieces"])
        self.assertEqual(protection["family"], "continuityworks:early_human_cave_complex")

    def test_worldgen_spacing_is_valid(self):
        placement = self.generator.worldgen_bundle()["structure_set"]["placement"]
        self.assertLess(placement["separation"], placement["spacing"])


if __name__ == "__main__":
    unittest.main()
