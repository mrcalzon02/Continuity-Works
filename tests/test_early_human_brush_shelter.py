import unittest

from structure_capability.early_human_brush_shelter import (
    TemporaryBrushShelterGenerationError,
    TemporaryBrushShelterGenerator,
)
from structure_capability.minecraft.worldgen import MINIMUM_STRUCTURE_EXCLUSION_RADIUS


class TemporaryBrushShelterTests(unittest.TestCase):
    def setUp(self):
        self.generator = TemporaryBrushShelterGenerator()

    def test_same_seed_is_deterministic(self):
        first = self.generator.generate(seed=4004, scale="medium")
        second = self.generator.generate(seed=4004, scale="medium")
        self.assertEqual(first, second)
        self.assertEqual(first["metadata"]["fingerprint"], second["metadata"]["fingerprint"])

    def test_different_seed_changes_structure(self):
        first = self.generator.generate(seed=4004, scale="medium")
        second = self.generator.generate(seed=4005, scale="medium")
        self.assertNotEqual(first["metadata"]["fingerprint"], second["metadata"]["fingerprint"])

    def test_scales_are_nonempty_and_in_bounds(self):
        for scale in ("small", "medium", "large"):
            with self.subTest(scale=scale):
                result = self.generator.generate(seed=44, scale=scale)
                size = result["size"]
                self.assertGreater(len(result["blocks"]), 0)
                for entry in result["blocks"]:
                    self.assertTrue(entry["block"].startswith("minecraft:"))
                    self.assertTrue(all(0 <= entry["pos"][i] < size[i] for i in range(3)))

    def test_archetype_remains_partial_and_ephemeral(self):
        result = self.generator.generate(seed=20260902, scale="large")
        meta = result["metadata"]
        self.assertTrue(meta["qualification_pass"])
        self.assertFalse(meta["perimeter_closed"])
        self.assertFalse(meta["complete_roof"])
        self.assertFalse(meta["dominant_planar_wall"])
        self.assertLess(meta["brush_skin_coverage_ratio"], 0.75)
        self.assertGreater(len(meta["frame_points"]), 0)
        self.assertGreater(len(meta["brush_skin_points"]), 0)

    def test_arid_variant_avoids_moss(self):
        result = self.generator.generate(seed=14, biome_family="arid")
        blocks = {entry["block"] for entry in result["blocks"]}
        self.assertNotIn("minecraft:moss_carpet", blocks)

    def test_weathered_and_collapsed_states_remove_frame_material(self):
        active = self.generator.generate(seed=77, condition="active")
        weathered = self.generator.generate(seed=77, condition="weathered")
        collapsed = self.generator.generate(seed=77, condition="collapsed")
        self.assertGreater(len(active["blocks"]), len(weathered["blocks"]))
        self.assertGreater(len(weathered["blocks"]), len(collapsed["blocks"]))

    def test_invalid_scale_rejected(self):
        with self.assertRaises(TemporaryBrushShelterGenerationError):
            self.generator.generate(seed=1, scale="giant")

    def test_worldgen_bundle_is_surface_anchored_and_protected(self):
        bundle = self.generator.worldgen_bundle()
        self.assertEqual(bundle["validation_findings"], [])
        self.assertEqual(bundle["structure"]["step"], "surface_structures")
        self.assertEqual(bundle["structure"]["project_start_to_heightmap"], "WORLD_SURFACE_WG")
        protection = bundle["protection_profile"]
        self.assertEqual(protection["family"], "continuityworks:early_human_ephemeral_shelter")
        self.assertGreaterEqual(protection["exclusion_radius"], MINIMUM_STRUCTURE_EXCLUSION_RADIUS)
        self.assertGreaterEqual(
            protection["jigsaw_piece_exclusion_radius"],
            MINIMUM_STRUCTURE_EXCLUSION_RADIUS,
        )
        self.assertTrue(protection["protect_jigsaw_pieces"])

    def test_worldgen_spacing_is_valid(self):
        placement = self.generator.worldgen_bundle()["structure_set"]["placement"]
        self.assertLess(placement["separation"], placement["spacing"])


if __name__ == "__main__":
    unittest.main()
