import unittest

from structure_capability.early_human_bone_breaking import (
    BoneBreakingStationGenerationError,
    BoneBreakingStationGenerator,
)
from structure_capability.minecraft.worldgen import MINIMUM_STRUCTURE_EXCLUSION_RADIUS


class BoneBreakingStationTests(unittest.TestCase):
    def setUp(self):
        self.generator = BoneBreakingStationGenerator()

    def test_same_seed_replays_identically(self):
        first = self.generator.generate(seed=14014, scale="medium")
        second = self.generator.generate(seed=14014, scale="medium")
        self.assertEqual(first, second)
        self.assertEqual(first["metadata"]["fingerprint"], second["metadata"]["fingerprint"])

    def test_different_seed_changes_structure(self):
        first = self.generator.generate(seed=14014, scale="medium")
        second = self.generator.generate(seed=14015, scale="medium")
        self.assertNotEqual(first["metadata"]["fingerprint"], second["metadata"]["fingerprint"])

    def test_scales_are_nonempty_and_in_bounds(self):
        for scale in ("small", "medium", "large"):
            with self.subTest(scale=scale):
                result = self.generator.generate(seed=77, scale=scale)
                size = result["size"]
                self.assertGreater(len(result["blocks"]), 0)
                for entry in result["blocks"]:
                    self.assertTrue(entry["block"].startswith("minecraft:"))
                    self.assertTrue(all(0 <= entry["pos"][i] < size[i] for i in range(3)))

    def test_qualification_requires_bone_breaking_topology(self):
        result = self.generator.generate(seed=140140, scale="large")
        q = result["metadata"]["qualification"]
        self.assertTrue(q["passes"])
        self.assertGreaterEqual(q["impact_station_count"], 1)
        self.assertGreaterEqual(q["fracture_cell_count"], 8)
        self.assertGreaterEqual(q["staging_count"], 3)
        self.assertFalse(q["has_dominant_carcass_axis"])

    def test_scale_increases_station_capacity(self):
        small = self.generator.generate(seed=4, scale="small", culture_profile="distributed_percussion")
        large = self.generator.generate(seed=4, scale="large", culture_profile="distributed_percussion")
        self.assertGreater(
            large["metadata"]["qualification"]["impact_station_count"],
            small["metadata"]["qualification"]["impact_station_count"],
        )

    def test_single_station_reuse_forces_one_station(self):
        result = self.generator.generate(seed=5, scale="large", culture_profile="single_station_reuse")
        self.assertEqual(result["metadata"]["qualification"]["impact_station_count"], 1)
        self.assertTrue(result["metadata"]["qualification"]["passes"])

    def test_arid_weathered_variant_has_no_moss(self):
        result = self.generator.generate(seed=8, biome_family="arid", condition="weathered")
        self.assertNotIn("minecraft:moss_block", {b["block"] for b in result["blocks"]})

    def test_invalid_inputs_are_rejected(self):
        with self.assertRaises(BoneBreakingStationGenerationError):
            self.generator.generate(seed=1, scale="gigantic")
        with self.assertRaises(BoneBreakingStationGenerationError):
            self.generator.generate(seed=1, condition="industrial")
        with self.assertRaises(BoneBreakingStationGenerationError):
            self.generator.generate(seed=1, culture_profile="metal_sawing")

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
