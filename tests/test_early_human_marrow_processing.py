import unittest

from structure_capability.early_human_marrow_processing import (
    MarrowProcessingGroundGenerationError,
    MarrowProcessingGroundGenerator,
)
from structure_capability.minecraft.worldgen import MINIMUM_STRUCTURE_EXCLUSION_RADIUS


class MarrowProcessingGroundTests(unittest.TestCase):
    def setUp(self):
        self.generator = MarrowProcessingGroundGenerator()

    def test_same_seed_replays_identically(self):
        first = self.generator.generate(seed=15015, scale="medium")
        second = self.generator.generate(seed=15015, scale="medium")
        self.assertEqual(first, second)
        self.assertEqual(first["metadata"]["fingerprint"], second["metadata"]["fingerprint"])

    def test_different_seed_changes_structure(self):
        first = self.generator.generate(seed=15015, scale="medium")
        second = self.generator.generate(seed=15016, scale="medium")
        self.assertNotEqual(first["metadata"]["fingerprint"], second["metadata"]["fingerprint"])

    def test_scales_are_nonempty_and_in_bounds(self):
        for scale in ("small", "medium", "large"):
            with self.subTest(scale=scale):
                result = self.generator.generate(seed=75, scale=scale)
                size = result["size"]
                self.assertGreater(len(result["blocks"]), 0)
                for entry in result["blocks"]:
                    self.assertTrue(entry["block"].startswith("minecraft:"))
                    self.assertTrue(all(0 <= entry["pos"][i] < size[i] for i in range(3)))

    def test_qualification_requires_marrow_processing_topology(self):
        result = self.generator.generate(seed=151515, scale="large")
        q = result["metadata"]["qualification"]
        self.assertTrue(q["passes"])
        self.assertGreaterEqual(q["handling_pocket_count"], 1)
        self.assertGreaterEqual(q["activity_stance_count"], q["handling_pocket_count"])
        self.assertGreaterEqual(q["opened_bone_count"], 5)
        self.assertGreaterEqual(q["stain_count"], 4)
        self.assertGreaterEqual(q["spent_fragment_count"], 6)
        self.assertLessEqual(q["light_percussion_count"], 1)
        self.assertFalse(q["has_dominant_carcass_axis"])

    def test_distributed_extraction_scales_pocket_count(self):
        small = self.generator.generate(seed=4, scale="small", culture_profile="distributed_extraction")
        large = self.generator.generate(seed=4, scale="large", culture_profile="distributed_extraction")
        self.assertGreater(
            large["metadata"]["qualification"]["handling_pocket_count"],
            small["metadata"]["qualification"]["handling_pocket_count"],
        )

    def test_immediate_consumption_suppresses_light_percussion(self):
        result = self.generator.generate(seed=88, scale="large", culture_profile="immediate_consumption")
        self.assertIsNone(result["metadata"]["light_percussion"])
        self.assertEqual(result["metadata"]["qualification"]["light_percussion_count"], 0)

    def test_repeated_use_preserves_processing_qualification(self):
        result = self.generator.generate(seed=99, scale="large", condition="repeated", culture_profile="repeated_use")
        self.assertTrue(result["metadata"]["qualification"]["passes"])
        self.assertGreaterEqual(len(result["metadata"]["stain_points"]), 4)

    def test_arid_weathered_variant_has_no_moss(self):
        result = self.generator.generate(seed=8, biome_family="arid", condition="weathered")
        self.assertNotIn("minecraft:moss_block", {b["block"] for b in result["blocks"]})

    def test_invalid_inputs_are_rejected(self):
        with self.assertRaises(MarrowProcessingGroundGenerationError):
            self.generator.generate(seed=1, scale="gigantic")
        with self.assertRaises(MarrowProcessingGroundGenerationError):
            self.generator.generate(seed=1, condition="industrial")
        with self.assertRaises(MarrowProcessingGroundGenerationError):
            self.generator.generate(seed=1, culture_profile="pot_boiling")

    def test_worldgen_bundle_is_additive_and_protected(self):
        bundle = self.generator.worldgen_bundle()
        self.assertEqual(bundle["validation_findings"], [])
        self.assertEqual(bundle["family_id"], "continuityworks:early_human_carcass_processing")
        self.assertEqual(bundle["compatibility"]["mode"], "additive_non_destructive")
        self.assertTrue(bundle["compatibility"]["family_tight_composition_requires_same_parent_reservation"])
        protection = bundle["protection_profile"]
        self.assertGreaterEqual(protection["exclusion_radius"], MINIMUM_STRUCTURE_EXCLUSION_RADIUS)
        self.assertGreaterEqual(protection["jigsaw_piece_exclusion_radius"], MINIMUM_STRUCTURE_EXCLUSION_RADIUS)
        self.assertTrue(protection["protect_jigsaw_pieces"])

    def test_worldgen_spacing_is_valid(self):
        placement = self.generator.worldgen_bundle()["structure_set"]["placement"]
        self.assertLess(placement["separation"], placement["spacing"])


if __name__ == "__main__":
    unittest.main()
