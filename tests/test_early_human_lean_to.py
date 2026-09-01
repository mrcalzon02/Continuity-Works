import unittest

from structure_capability.early_human_lean_to import (
    LeanToWindbreakGenerationError,
    LeanToWindbreakGenerator,
)
from structure_capability.minecraft.worldgen import MINIMUM_STRUCTURE_EXCLUSION_RADIUS


class LeanToWindbreakTests(unittest.TestCase):
    def setUp(self):
        self.generator = LeanToWindbreakGenerator()

    def test_same_seed_is_deterministic(self):
        a = self.generator.generate(seed=505, scale="medium")
        b = self.generator.generate(seed=505, scale="medium")
        self.assertEqual(a, b)

    def test_different_seed_changes_structure(self):
        a = self.generator.generate(seed=505, scale="medium")
        b = self.generator.generate(seed=506, scale="medium")
        self.assertNotEqual(a["metadata"]["fingerprint"], b["metadata"]["fingerprint"])

    def test_scales_are_nonempty_and_in_bounds(self):
        for scale in ("small", "medium", "large"):
            with self.subTest(scale=scale):
                result = self.generator.generate(seed=55, scale=scale)
                size = result["size"]
                self.assertGreater(len(result["blocks"]), 0)
                for entry in result["blocks"]:
                    self.assertTrue(entry["block"].startswith("minecraft:"))
                    self.assertTrue(all(0 <= entry["pos"][i] < size[i] for i in range(3)))

    def test_archetype_qualification_is_directional_not_enclosed(self):
        result = self.generator.generate(seed=55005, scale="medium")
        q = result["metadata"]["qualification"]
        self.assertTrue(result["metadata"]["qualification_pass"])
        self.assertTrue(q["directional_windward_leeward_logic"])
        self.assertTrue(q["dominant_planar_windbreak"])
        self.assertTrue(q["perimeter_open"])
        self.assertTrue(q["overhead_cover_minimal"])
        self.assertTrue(q["hide_dominance_absent"])
        self.assertLess(result["metadata"]["screen_coverage_ratio"], 0.85)

    def test_arid_variant_has_no_moss_bedding(self):
        result = self.generator.generate(seed=14, biome_family="arid")
        self.assertNotIn("minecraft:moss_carpet", {b["block"] for b in result["blocks"]})

    def test_weathering_changes_structure_without_changing_identity_metadata(self):
        active = self.generator.generate(seed=9, condition="active")
        weathered = self.generator.generate(seed=9, condition="weathered")
        self.assertNotEqual(active["metadata"]["fingerprint"], weathered["metadata"]["fingerprint"])
        self.assertEqual(weathered["metadata"]["name"], "Lean-To Windbreak")

    def test_invalid_scale_rejected(self):
        with self.assertRaises(LeanToWindbreakGenerationError):
            self.generator.generate(seed=1, scale="gigantic")

    def test_worldgen_bundle_is_surface_anchored_and_protected(self):
        bundle = self.generator.worldgen_bundle()
        self.assertEqual(bundle["validation_findings"], [])
        self.assertEqual(bundle["structure"]["project_start_to_heightmap"], "WORLD_SURFACE_WG")
        protection = bundle["protection_profile"]
        self.assertGreaterEqual(protection["exclusion_radius"], MINIMUM_STRUCTURE_EXCLUSION_RADIUS)
        self.assertGreaterEqual(protection["jigsaw_piece_exclusion_radius"], MINIMUM_STRUCTURE_EXCLUSION_RADIUS)
        self.assertTrue(protection["protect_jigsaw_pieces"])
        self.assertEqual(protection["family"], "continuityworks:early_human_ephemeral_shelter")

    def test_worldgen_spacing_is_valid(self):
        placement = self.generator.worldgen_bundle()["structure_set"]["placement"]
        self.assertLess(placement["separation"], placement["spacing"])


if __name__ == "__main__":
    unittest.main()
